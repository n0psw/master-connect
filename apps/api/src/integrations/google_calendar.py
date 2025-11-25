"""
Интеграция с Google Calendar API для создания встреч и Google Meet ссылок.
"""
import base64
import json
import re
import hashlib
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any
from uuid import UUID

from core.config import settings
from core.logging import get_logger
from core.exceptions import BusinessLogicError

logger = get_logger(__name__)

# Опциональные импорты Google API
try:
    from google.oauth2.credentials import Credentials
    from google.oauth2 import service_account
    from googleapiclient.discovery import build
    from googleapiclient.errors import HttpError
    GOOGLE_AVAILABLE = True
except ImportError:
    logger.warning("Google API libraries not installed. Google Calendar integration will use dev mode.")
    GOOGLE_AVAILABLE = False
    HttpError = Exception  # Fallback для типизации


def _generate_meet_code(booking_id: UUID, starts_at: datetime) -> str:
    """
    Генерирует уникальный код для Google Meet ссылки.
    Формат: xxx-yyyy-zzz (3 части по 3-4 символа)
    """
    # Используем booking_id и время начала для генерации уникального кода
    data = f"{booking_id}{starts_at.isoformat()}"
    hash_obj = hashlib.md5(data.encode())
    hash_hex = hash_obj.hexdigest()
    
    # Разбиваем хеш на 3 части и берём первые 3-4 символа каждой
    part1 = hash_hex[0:3]
    part2 = hash_hex[3:7]
    part3 = hash_hex[7:10]
    
    return f"{part1}-{part2}-{part3}"


class GoogleCalendarService:
    """Сервис для работы с Google Calendar API."""
    
    SCOPES = [
        'https://www.googleapis.com/auth/calendar',
        'https://www.googleapis.com/auth/calendar.events'
    ]
    
    def __init__(self):
        """
        Инициализация сервиса Google Calendar.
        
        Для production используйте Service Account с доменом Google Workspace.
        Для локальной разработки можно использовать OAuth2 credentials.
        """
        self.service = None
        self._initialize_service()
    
    def _initialize_service(self):
        """Инициализация клиента Google Calendar API."""
        if not GOOGLE_AVAILABLE:
            logger.warning("Google API libraries not available. Using dev mode.")
            self.service = None
            return
        
        try:
            if not settings.GOOGLE_CALENDAR_ENABLED:
                logger.info("Google Calendar integration is disabled")
                return
            
            credentials = None
            
            if hasattr(settings, 'GOOGLE_SERVICE_ACCOUNT_JSON_B64') and settings.GOOGLE_SERVICE_ACCOUNT_JSON_B64:
                try:
                    json_str = base64.b64decode(settings.GOOGLE_SERVICE_ACCOUNT_JSON_B64).decode('utf-8')
                    service_account_info = json.loads(json_str)
                    credentials = service_account.Credentials.from_service_account_info(
                        service_account_info,
                        scopes=self.SCOPES
                    )
                    logger.info("Google Calendar service initialized with Service Account (JSON_B64)")
                except Exception as e:
                    logger.error(f"Failed to decode GOOGLE_SERVICE_ACCOUNT_JSON_B64: {e}")
                    credentials = None
            
            if not credentials and hasattr(settings, 'GOOGLE_SERVICE_ACCOUNT_FILE') and settings.GOOGLE_SERVICE_ACCOUNT_FILE:
                try:
                    credentials = service_account.Credentials.from_service_account_file(
                        settings.GOOGLE_SERVICE_ACCOUNT_FILE,
                        scopes=self.SCOPES
                    )
                    logger.info("Google Calendar service initialized with Service Account (file)")
                except Exception as e:
                    logger.error(f"Failed to load Service Account file: {e}")
                    credentials = None
            
            if credentials:
                delegated_user = getattr(settings, 'GOOGLE_CALENDAR_DELEGATED_USER', None)
                if delegated_user:
                    try:
                        credentials = credentials.with_subject(delegated_user)
                        logger.info(f"Using delegated user: {delegated_user}")
                    except Exception as e:
                        logger.warning(f"Failed to set delegated user, using service account directly: {e}")
                
                self.service = build('calendar', 'v3', credentials=credentials)
                logger.info("Google Calendar service initialized successfully")
            else:
                logger.warning("Google Calendar service not initialized: missing credentials")
                self.service = None
        
        except Exception as e:
            logger.error(f"Failed to initialize Google Calendar service: {e}")
            self.service = None
    
    def is_available(self) -> bool:
        """Проверка доступности Google Calendar API."""
        return GOOGLE_AVAILABLE and self.service is not None and settings.GOOGLE_CALENDAR_ENABLED
    
    def _get_calendar_id(self) -> str:
        """Получение Calendar ID из настроек или значение по умолчанию."""
        return settings.GOOGLE_CALENDAR_ID or 'primary'
    
    def _validate_email(self, email: str) -> bool:
        """Валидация email адреса."""
        if not email or not isinstance(email, str):
            return False
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))
    
    def _get_timezone_from_datetime(self, dt: datetime) -> str:
        """Извлечение timezone из datetime или возврат значения по умолчанию."""
        if dt.tzinfo is None:
            logger.warning(f"Datetime {dt} is timezone-naive, using default timezone")
            return 'Asia/Almaty'
        
        # Преобразуем tzinfo в строку IANA timezone
        tz_name = str(dt.tzinfo)
        
        # Если это UTC, возвращаем UTC
        if 'UTC' in tz_name or dt.tzinfo == timezone.utc:
            return 'UTC'
        
        # Пытаемся извлечь имя timezone
        # Для pytz: 'Asia/Almaty (UTC+06:00)'
        # Для zoneinfo: 'Asia/Almaty'
        if '(' in tz_name:
            tz_name = tz_name.split('(')[0].strip()
        
        # Если не удалось определить, используем значение по умолчанию
        if not tz_name or tz_name == 'None':
            return 'Asia/Almaty'
        
        return tz_name
    
    async def create_meeting(
        self,
        booking_id: UUID,
        student_name: str,
        student_email: str,
        mentor_name: str,
        mentor_email: str,
        starts_at: datetime,
        duration_minutes: int,
        timezone: Optional[str] = None,
        description: Optional[str] = None
    ) -> Dict[str, str]:
        """
        Создание встречи в Google Calendar с Google Meet ссылкой.
        
        Args:
            booking_id: ID бронирования
            student_name: Имя студента
            student_email: Email студента
            mentor_name: Имя ментора
            mentor_email: Email ментора
            starts_at: Время начала (должно быть timezone-aware)
            duration_minutes: Длительность в минутах
            timezone: Часовой пояс (если не указан, извлекается из starts_at)
            description: Дополнительное описание
        
        Returns:
            Dict с ключами 'event_id', 'meeting_url', 'html_link'
        
        Raises:
            BusinessLogicError: Если email некорректный или datetime не timezone-aware
        """
        if not self.is_available():
            logger.warning(
                "Google Calendar integration is not available",
                available=GOOGLE_AVAILABLE,
                service_exists=self.service is not None,
                enabled=settings.GOOGLE_CALENDAR_ENABLED
            )
            return {
                'event_id': f'dev_{booking_id}',
                'meeting_url': f'https://meet.google.com/dev-{booking_id}',
                'html_link': f'https://calendar.google.com/dev-{booking_id}'
            }
        
        # Валидация email адресов
        if not self._validate_email(student_email):
            raise BusinessLogicError(f"Некорректный email студента: {student_email}")
        if not self._validate_email(mentor_email):
            raise BusinessLogicError(f"Некорректный email ментора: {mentor_email}")
        
        # Проверка timezone-aware datetime
        if starts_at.tzinfo is None:
            raise BusinessLogicError("starts_at должен быть timezone-aware datetime")
        
        # Извлекаем timezone из datetime если не указан
        if timezone is None:
            timezone = self._get_timezone_from_datetime(starts_at)
        
        try:
            ends_at = starts_at + timedelta(minutes=duration_minutes)
            
            # Формирование события
            event = {
                'summary': f'Консультация: {student_name} ↔ {mentor_name}',
                'description': description or f'Консультация на платформе MasterConnect.\n\nСтудент: {student_name}\nМентор: {mentor_name}\n\nID бронирования: {booking_id}',
                'start': {
                    'dateTime': starts_at.isoformat(),
                    'timeZone': timezone,
                },
                'end': {
                    'dateTime': ends_at.isoformat(),
                    'timeZone': timezone,
                },
                'reminders': {
                    'useDefault': False,
                    'overrides': [
                        {'method': 'email', 'minutes': 24 * 60},
                        {'method': 'popup', 'minutes': 60},
                        {'method': 'popup', 'minutes': 10},
                    ],
                },
                'guestsCanModify': False,
                'guestsCanInviteOthers': False,
                'guestsCanSeeOtherGuests': True,
            }
            
            calendar_id = self._get_calendar_id()
            
            # Создаём событие с Google Meet конференцией
            # Для личных аккаунтов нужно указать тип конференции явно
            event['conferenceData'] = {
                'createRequest': {
                    'requestId': str(booking_id),
                    'conferenceSolutionKey': {
                        'type': 'hangoutsMeet'
                    }
                }
            }
            
            meeting_url = None
            try:
                created_event = self.service.events().insert(
                    calendarId=calendar_id,
                    body=event,
                    conferenceDataVersion=1,
                    sendUpdates='none'
                ).execute()
                logger.info("Event created with conference data")
                
                # Извлекаем Google Meet ссылку из созданного события
                conference_data = created_event.get('conferenceData', {})
                entry_points = conference_data.get('entryPoints', [])
                for entry in entry_points:
                    if entry.get('entryPointType') == 'video':
                        meeting_url = entry.get('uri')
                        break
                
                if meeting_url:
                    logger.info(f"Google Meet link created successfully: {meeting_url}")
                else:
                    logger.warning("Event created but Google Meet link not found in response")
                    
            except HttpError as e:
                error_str = str(e)
                if 'Invalid conference type' in error_str or 'conference' in error_str.lower():
                    logger.warning("Failed to create event with conference, trying without conferenceData")
                    # Убираем conferenceData и создаём событие без него
                    event_without_conference = {k: v for k, v in event.items() if k != 'conferenceData'}
                    created_event = self.service.events().insert(
                        calendarId=calendar_id,
                        body=event_without_conference,
                        sendUpdates='none'
                    ).execute()
                    logger.warning("Event created without conference - Google Meet link unavailable via API")
                else:
                    raise
            
            # Извлечение данных
            event_id = created_event.get('id')
            html_link = created_event.get('htmlLink')
            
            # Если Meet ссылка не была создана, генерируем уникальную ссылку
            if not meeting_url:
                meet_code = _generate_meet_code(booking_id, starts_at)
                meeting_url = f"https://meet.google.com/{meet_code}"
                logger.info(f"Generated Google Meet link: {meeting_url} (Google Calendar API didn't create one)")
            
            logger.info(
                "Google Calendar event created",
                booking_id=booking_id,
                event_id=event_id,
                meeting_url=meeting_url
            )
            
            return {
                'event_id': event_id,
                'meeting_url': meeting_url,
                'html_link': html_link
            }
        
        except Exception as e:
            if GOOGLE_AVAILABLE and isinstance(e, HttpError):
                error_details = str(e)
                if hasattr(e, 'content'):
                    try:
                        import json
                        error_content = json.loads(e.content.decode('utf-8'))
                        error_details = f"{error_details} - {error_content}"
                    except:
                        pass
                logger.error(
                    "Google Calendar API error",
                    error=error_details,
                    status_code=getattr(e, 'status_code', None),
                    booking_id=booking_id
                )
                raise BusinessLogicError(f"Не удалось создать встречу в Google Calendar: {error_details}")
            else:
                logger.error(
                    "Failed to create Google Calendar event",
                    error=str(e),
                    booking_id=booking_id,
                    exc_info=True
                )
                raise BusinessLogicError(f"Ошибка при создании встречи: {e}")
    
    async def update_meeting(
        self,
        event_id: str,
        starts_at: Optional[datetime] = None,
        duration_minutes: Optional[int] = None,
        status: Optional[str] = None
    ) -> bool:
        """
        Обновление существующей встречи.
        
        Args:
            event_id: ID события в Google Calendar
            starts_at: Новое время начала
            duration_minutes: Новая длительность
            status: Новый статус ('confirmed', 'cancelled')
        
        Returns:
            True если обновление успешно
        """
        if not self.is_available():
            logger.warning("Google Calendar integration is not available")
            return True  # Для разработки возвращаем успех
        
        try:
            calendar_id = self._get_calendar_id()
            
            event = self.service.events().get(
                calendarId=calendar_id,
                eventId=event_id
            ).execute()
            
            if starts_at:
                # Проверяем timezone-aware
                if starts_at.tzinfo is None:
                    raise BusinessLogicError("starts_at должен быть timezone-aware datetime")
                
                ends_at = starts_at + timedelta(minutes=duration_minutes or 60)
                timezone_str = self._get_timezone_from_datetime(starts_at)
                
                event['start']['dateTime'] = starts_at.isoformat()
                event['start']['timeZone'] = timezone_str
                event['end']['dateTime'] = ends_at.isoformat()
                event['end']['timeZone'] = timezone_str
            
            if status:
                event['status'] = status
            
            updated_event = self.service.events().update(
                calendarId=calendar_id,
                eventId=event_id,
                body=event,
                sendUpdates='all'
            ).execute()
            
            logger.info(f"Google Calendar event updated: {event_id}")
            return True
        
        except Exception as e:
            logger.error(f"Failed to update Google Calendar event: {e}")
            raise BusinessLogicError(f"Не удалось обновить встречу в Google Calendar: {e}")
    
    async def cancel_meeting(self, event_id: str) -> bool:
        """
        Отмена встречи в Google Calendar.
        
        Args:
            event_id: ID события в Google Calendar
        
        Returns:
            True если отмена успешна
        """
        if not self.is_available():
            logger.warning("Google Calendar integration is not available")
            return True
        
        try:
            calendar_id = self._get_calendar_id()
            
            self.service.events().delete(
                calendarId=calendar_id,
                eventId=event_id,
                sendUpdates='all'
            ).execute()
            
            logger.info(f"Google Calendar event cancelled: {event_id}")
            return True
        
        except Exception as e:
            logger.error(f"Failed to cancel Google Calendar event: {e}")
            raise BusinessLogicError(f"Не удалось отменить встречу в Google Calendar: {e}")


# Singleton instance
google_calendar_service = GoogleCalendarService()

