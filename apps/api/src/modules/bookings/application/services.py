"""
Сервисы для модуля бронирований.
"""
import uuid
from datetime import datetime, timedelta, time, timezone
from decimal import Decimal
from typing import List, Optional, Tuple
from uuid import UUID

from sqlalchemy import and_, desc, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy.exc import IntegrityError

from core.config import settings
from core.exceptions import BusinessLogicError, NotFoundError, PermissionDeniedError
from core.logging import get_logger
from modules.admin.domain.models import AuditLog
from integrations.google_calendar import google_calendar_service
from modules.bookings.domain.models import Booking, BookingStatus
from modules.bookings.domain.schemas import (
    AdminBookingAction,
    BookingAnalytics,
    BookingCancellationRequest,
    BookingCreate,
    BookingDetail,
    BookingFilters,
    BookingList,
    BookingModerationQueue,
    BookingPaymentConfirmation,
    BookingRescheduleRequest,
    BookingResponse,
    BookingStats,
    BookingStatusUpdate,
    BookingUpdate,
    CalendarEvent,
    CalendarEventResponse,
    PaymentInfo,
)
from modules.mentors.domain.models import Mentor
from modules.users.domain.models import User, UserRole, Student
from modules.availability.domain.models import AvailabilityRule, TimeOff
from modules.chat.domain.models import Dialog

logger = get_logger(__name__)


class BookingService:
    """Сервис для управления бронированиями."""
    
    def __init__(self, db_session: AsyncSession):
        self.db = db_session
    
    async def create_booking(
        self,
        student_id: UUID,
        booking_data: BookingCreate
    ) -> BookingResponse:
        """Создание нового бронирования."""
        logger.info("Creating booking", student_id=student_id, mentor_id=booking_data.mentor_id)
        
        try:
            # Проверяем, что ментор существует и активен
            mentor = await self._get_mentor_or_404(booking_data.mentor_id)
            
            # Проверяем максимальную дальность бронирования (advance_booking_days)
            from modules.availability.domain.models import MentorSettings
            settings_query = select(MentorSettings).where(MentorSettings.mentor_id == booking_data.mentor_id)
            settings_result = await self.db.execute(settings_query)
            mentor_settings = settings_result.scalar_one_or_none()
            advance_days = mentor_settings.advance_booking_days if mentor_settings else 30
            
            now = datetime.now(timezone.utc)
            max_booking_date = now + timedelta(days=advance_days)
            if booking_data.starts_at > max_booking_date:
                raise BusinessLogicError(
                    f"Нельзя забронировать более чем на {advance_days} дней вперед. "
                    f"Максимальная дата: {max_booking_date.date()}"
                )
            
            # Проверяем максимальное количество бронирований на день
            # Нормализуем время к UTC для корректного сравнения
            if booking_data.starts_at.tzinfo is None:
                starts_at_utc = booking_data.starts_at.replace(tzinfo=timezone.utc)
            else:
                starts_at_utc = booking_data.starts_at.astimezone(timezone.utc)
            booking_date_start = starts_at_utc.replace(hour=0, minute=0, second=0, microsecond=0)
            booking_date_end = booking_date_start + timedelta(days=1)
            
            max_bookings_per_day = mentor_settings.max_bookings_per_day if mentor_settings else 8
            existing_bookings_query = select(func.count(Booking.id)).where(
                and_(
                    Booking.mentor_id == booking_data.mentor_id,
                    Booking.starts_at >= booking_date_start,
                    Booking.starts_at < booking_date_end,
                    Booking.status.in_([
                        BookingStatus.HOLD,
                        BookingStatus.AWAITING_VERIFICATION,
                        BookingStatus.CONFIRMED
                    ])
                )
            )
            existing_bookings_result = await self.db.execute(existing_bookings_query)
            existing_bookings_count = existing_bookings_result.scalar() or 0
            
            if existing_bookings_count >= max_bookings_per_day:
                raise BusinessLogicError(
                    f"Достигнуто максимальное количество бронирований на день ({max_bookings_per_day}). "
                    f"Выберите другую дату."
                )
            
            # Проверяем на дублирование бронирования (явная проверка перед созданием)
            duplicate_query = select(Booking).where(
                and_(
                    Booking.mentor_id == booking_data.mentor_id,
                    Booking.student_id == student_id,
                    Booking.starts_at == booking_data.starts_at,
                    Booking.status.in_([
                        BookingStatus.HOLD,
                        BookingStatus.AWAITING_VERIFICATION,
                        BookingStatus.CONFIRMED
                    ])
                )
            )
            duplicate_result = await self.db.execute(duplicate_query)
            duplicate_booking = duplicate_result.scalar_one_or_none()
            
            if duplicate_booking:
                raise BusinessLogicError(
                    "Вы уже забронировали этот слот. Пожалуйста, выберите другое время."
                )
            
            # Проверяем доступность слота с блокировкой (SELECT FOR UPDATE)
            # Это предотвращает race condition при одновременных запросах
            await self._check_slot_availability(
                mentor_id=booking_data.mentor_id,
                starts_at=booking_data.starts_at,
                duration_minutes=booking_data.duration_minutes
            )
            
            # Рассчитываем цену
            price_amount = await self._calculate_price(mentor, booking_data.duration_minutes)
            
            # Вычисляем время окончания
            ends_at = booking_data.starts_at + timedelta(minutes=booking_data.duration_minutes)
            
            # Создаем бронирование
            booking = Booking(
                id=uuid.uuid4(),
                student_id=student_id,
                mentor_id=booking_data.mentor_id,
                starts_at=booking_data.starts_at,
                ends_at=ends_at,
                duration_minutes=booking_data.duration_minutes,
                status=BookingStatus.HOLD,
                price=price_amount,
                currency="KZT",
                intake_form=booking_data.intake_form.model_dump(),
                payment_note=booking_data.notes
            )
            
            self.db.add(booking)
            await self.db.flush()  # Flush для получения ID, но не commit
            
            # Создаем диалог для чата
            chat_dialog = Dialog(booking_id=booking.id)
            self.db.add(chat_dialog)
            
            # Коммитим все вместе в одной транзакции
            await self.db.commit()
            await self.db.refresh(booking)
            await self.db.refresh(chat_dialog)
            
            logger.info(
                "Booking created",
                booking_id=booking.id,
                student_id=student_id,
                mentor_id=booking_data.mentor_id,
                starts_at=booking_data.starts_at,
                status=booking.status,
                price=price_amount
            )
            
            # Создаем аудит лог (не критично, если не получится)
            try:
                await self._create_audit_log(
                    actor_id=student_id,
                    action="CREATE_BOOKING",
                    entity="booking",
                    entity_id=booking.id,
                    meta={
                        "mentor_id": str(booking_data.mentor_id),
                        "starts_at": booking_data.starts_at.isoformat(),
                        "duration_minutes": booking_data.duration_minutes,
                        "price": float(price_amount)
                    }
                )
            except Exception as audit_error:
                # Логируем, но не прерываем выполнение
                logger.warning("Failed to create audit log", booking_id=booking.id, error=str(audit_error))
            
            # Планирование истечения холда временно отключено (в модели нет поля)
            
            # Строим ответ
            # Если здесь произойдет ошибка, бронирование уже создано в БД
            # Но мы все равно должны вернуть успешный ответ, поэтому оборачиваем в try-except
            try:
                return await self._build_booking_response(booking)
            except Exception as build_error:
                # Если не удалось построить ответ, логируем, но не падаем
                # Бронирование уже создано, студент должен получить успех
                logger.error(
                    "Failed to build booking response, but booking was created",
                    booking_id=booking.id,
                    error=str(build_error),
                    exc_info=True
                )
                # Возвращаем минимальный ответ с основными данными
                return BookingResponse(
                    id=booking.id,
                    student_id=booking.student_id,
                    mentor_id=booking.mentor_id,
                    starts_at=booking.starts_at,
                    ends_at=booking.ends_at,
                    duration_minutes=booking.duration_minutes,
                    status=booking.status,
                    price_amount=booking.price,
                    price_currency=booking.currency,
                    hold_expires_at=None,
                    google_meet_link=booking.meeting_url,
                    google_calendar_event_id=booking.meeting_event_id,
                    intake_form=booking.intake_form or {},
                    notes=booking.payment_note,
                    created_at=booking.created_at,
                    updated_at=booking.updated_at,
                    mentor_name="Ментор",  # Fallback
                    mentor_avatar_url=None,
                    student_name="Студент",  # Fallback
                    student_avatar_url=None
                )
            
        except IntegrityError as e:
            # Обрабатываем ошибку уникального индекса (fallback защита)
            await self.db.rollback()
            logger.warning(
                "IntegrityError при создании бронирования",
                student_id=student_id,
                mentor_id=booking_data.mentor_id,
                starts_at=booking_data.starts_at,
                error=str(e)
            )
            raise BusinessLogicError(
                "Слот недоступен: кто-то уже забронировал это время. Пожалуйста, выберите другое время."
            )
        except BusinessLogicError:
            # Прокидываем BusinessLogicError дальше (rollback уже сделан или не нужен)
            try:
                await self.db.rollback()
            except Exception:
                pass  # Игнорируем ошибки rollback
            raise
        except Exception as e:
            # Обрабатываем другие ошибки
            # Если commit уже был выполнен, rollback не поможет, но попробуем
            try:
                await self.db.rollback()
            except Exception:
                pass  # Игнорируем ошибки rollback
            
            logger.error(
                "Ошибка при создании бронирования",
                student_id=student_id,
                mentor_id=booking_data.mentor_id,
                error=str(e),
                exc_info=True
            )
            raise
    
    async def get_booking_detail(
        self,
        booking_id: UUID,
        user_id: UUID,
        user_role: UserRole
    ) -> BookingDetail:
        """Получение детальной информации о бронировании."""
        booking = await self._get_booking_or_404(booking_id)
        
        # Проверяем права доступа
        if not self._can_access_booking(booking, user_id, user_role):
            raise PermissionDeniedError("Недостаточно прав для доступа к бронированию")
        
        try:
            booking_response = await self._build_booking_response(booking)
        except Exception as build_error:
            logger.error(
                "Failed to build booking response in get_booking_detail",
                booking_id=booking_id,
                error=str(build_error),
                exc_info=True
            )
            # Возвращаем минимальный ответ с fallback значениями
            starts_at = booking.starts_at
            ends_at = booking.ends_at
            created_at = booking.created_at
            updated_at = booking.updated_at
            
            if starts_at and starts_at.tzinfo is None:
                starts_at = starts_at.replace(tzinfo=timezone.utc)
            if ends_at and ends_at.tzinfo is None:
                ends_at = ends_at.replace(tzinfo=timezone.utc)
            if created_at and created_at.tzinfo is None:
                created_at = created_at.replace(tzinfo=timezone.utc)
            if updated_at and updated_at.tzinfo is None:
                updated_at = updated_at.replace(tzinfo=timezone.utc)
            
            booking_response = BookingResponse(
                id=booking.id,
                student_id=booking.student_id,
                mentor_id=booking.mentor_id,
                starts_at=starts_at,
                ends_at=ends_at,
                duration_minutes=booking.duration_minutes,
                status=booking.status,
                price_amount=booking.price,
                price_currency=booking.currency,
                hold_expires_at=None,
                google_meet_link=booking.meeting_url,
                google_calendar_event_id=booking.meeting_event_id,
                intake_form=booking.intake_form or {},
                notes=booking.payment_note,
                created_at=created_at,
                updated_at=updated_at,
                mentor_name="Ментор",
                mentor_avatar_url=None,
                student_name="Студент",
                student_avatar_url=None,
                has_review=getattr(booking, 'review', None) is not None
            )
        
        # Определяем доступные действия
        now = datetime.now(timezone.utc)
        can_cancel = self._can_cancel_booking(booking, user_role, now)
        can_reschedule = self._can_reschedule_booking(booking, user_role, now)
        can_mark_payment = self._can_mark_payment(booking, user_id, user_role)
        
        # Определяем дедлайны
        cancellation_deadline = self._get_cancellation_deadline(booking)
        reschedule_deadline = self._get_reschedule_deadline(booking)
        
        return BookingDetail(
            booking=booking_response,
            can_cancel=can_cancel,
            can_reschedule=can_reschedule,
            can_mark_payment=can_mark_payment,
            cancellation_deadline=cancellation_deadline,
            reschedule_deadline=reschedule_deadline
        )
    
    async def get_bookings_list(
        self,
        user_id: UUID,
        user_role: UserRole,
        page: int = 1,
        page_size: int = 20,
        filters: Optional[BookingFilters] = None,
        sort_by: Optional[str] = None
    ) -> BookingList:
        """Получение списка бронирований для пользователя."""
        # Базовый запрос - используем selectinload для eager loading
        # Если нужен поиск, добавим JOIN позже
        query = select(Booking)
        count_query = select(func.count(Booking.id))
        
        # Флаг для отслеживания, был ли добавлен JOIN для поиска
        search_join_added = False
        
        # Фильтр по правам доступа
        if user_role == UserRole.STUDENT:
            access_filter = Booking.student_id == user_id
        elif user_role == UserRole.MENTOR:
            access_filter = Booking.mentor_id == user_id
        elif user_role == UserRole.ADMIN:
            access_filter = True  # Админ видит все
        else:
            access_filter = False
        
        conditions = [access_filter] if access_filter is not True else []
        
        # Применяем дополнительные фильтры
        if filters:
            if filters.status:
                conditions.append(Booking.status.in_(filters.status))
            
            # Фильтрация только будущих бронирований
            if filters.upcoming:
                now_utc = datetime.now(timezone.utc)
                conditions.append(Booking.starts_at > now_utc)
            
            if filters.mentor_id:
                conditions.append(Booking.mentor_id == filters.mentor_id)
            
            if filters.student_id and user_role == UserRole.ADMIN:
                conditions.append(Booking.student_id == filters.student_id)
            
            if filters.date_from:
                conditions.append(Booking.starts_at >= filters.date_from)
            
            if filters.date_to:
                conditions.append(Booking.starts_at <= filters.date_to)
            
            if filters.duration_minutes:
                conditions.append(Booking.duration_minutes == filters.duration_minutes)
            
            # Поиск по имени студента/ментора или email
            # Используем JOIN для оптимизации вместо подзапросов EXISTS
            if filters.search:
                search_term = f"%{filters.search.lower()}%"
                from modules.users.domain.models import User as UserModel
                from sqlalchemy.orm import aliased
                
                # Создаем алиасы для JOIN
                student_user = aliased(UserModel)
                mentor_user = aliased(UserModel)
                
                # Используем JOIN для оптимизации поиска (только если еще не добавлен)
                if not search_join_added:
                    query = query.join(
                        Student, Booking.student_id == Student.user_id
                    ).join(
                        student_user, Student.user_id == student_user.id
                    ).join(
                        Mentor, Booking.mentor_id == Mentor.user_id
                    ).join(
                        mentor_user, Mentor.user_id == mentor_user.id
                    ).options(
                        selectinload(Booking.student).selectinload(Student.user),
                        selectinload(Booking.mentor).selectinload(Mentor.user),
                        selectinload(Booking.review)
                    )
                    
                    count_query = count_query.join(
                        Student, Booking.student_id == Student.user_id
                    ).join(
                        student_user, Student.user_id == student_user.id
                    ).join(
                        Mentor, Booking.mentor_id == Mentor.user_id
                    ).join(
                        mentor_user, Mentor.user_id == mentor_user.id
                    )
                    search_join_added = True
                
                search_conditions = or_(
                    func.lower(student_user.name).like(search_term),
                    func.lower(student_user.email).like(search_term),
                    func.lower(mentor_user.name).like(search_term),
                    func.lower(mentor_user.email).like(search_term)
                )
                conditions.append(search_conditions)
        
        if conditions:
            query = query.where(and_(*conditions))
            count_query = count_query.where(and_(*conditions))
        
        # Если JOIN не был добавлен для поиска, добавляем selectinload для eager loading
        if not search_join_added:
            query = query.options(
                selectinload(Booking.student).selectinload(Student.user),
                selectinload(Booking.mentor).selectinload(Mentor.user),
                selectinload(Booking.review)
            )
        else:
            # Если JOIN был добавлен, все равно нужно загрузить review
            query = query.options(selectinload(Booking.review))
        
        # Подсчет общего количества
        total_result = await self.db.execute(count_query)
        total = total_result.scalar()
        
        # Сортировка
        offset = (page - 1) * page_size
        if sort_by == "created_asc":
            query = query.order_by(Booking.created_at).offset(offset).limit(page_size)
        elif sort_by == "scheduled_desc":
            query = query.order_by(desc(Booking.starts_at)).offset(offset).limit(page_size)
        elif sort_by == "scheduled_asc":
            query = query.order_by(Booking.starts_at).offset(offset).limit(page_size)
        elif sort_by == "price_desc":
            query = query.order_by(desc(Booking.price)).offset(offset).limit(page_size)
        elif sort_by == "price_asc":
            query = query.order_by(Booking.price).offset(offset).limit(page_size)
        else:  # created_desc по умолчанию
            query = query.order_by(desc(Booking.created_at)).offset(offset).limit(page_size)
        
        # Выполнение запроса
        result = await self.db.execute(query)
        bookings = result.scalars().all()
        
        # Формируем ответы с обработкой ошибок
        booking_responses = []
        for booking in bookings:
            try:
                response = await self._build_booking_response(booking)
                booking_responses.append(response)
            except Exception as build_error:
                logger.error(
                    "Failed to build booking response in get_bookings_list, skipping booking",
                    booking_id=booking.id,
                    error=str(build_error),
                    exc_info=True
                )
                # Добавляем минимальный ответ с fallback значениями
                booking_responses.append(BookingResponse(
                    id=booking.id,
                    student_id=booking.student_id,
                    mentor_id=booking.mentor_id,
                    starts_at=booking.starts_at,
                    ends_at=booking.ends_at,
                    duration_minutes=booking.duration_minutes,
                    status=booking.status,
                    price_amount=booking.price,
                    price_currency=booking.currency,
                    hold_expires_at=None,
                    google_meet_link=booking.meeting_url,
                    google_calendar_event_id=booking.meeting_event_id,
                    intake_form=booking.intake_form or {},
                    notes=booking.payment_note,
                    created_at=booking.created_at,
                    updated_at=booking.updated_at,
                    mentor_name="Ментор",
                    mentor_avatar_url=None,
                    student_name="Студент",
                    student_avatar_url=None
                ))
        
        total_pages = (total + page_size - 1) // page_size if page_size > 0 else 1
        
        return BookingList(
            bookings=booking_responses,
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages
        )
    
    async def mark_payment_by_student(
        self,
        booking_id: UUID,
        student_id: UUID
    ) -> BookingResponse:
        """Отметка студентом о совершении платежа."""
        booking = await self._get_booking_or_404(booking_id)
        
        # Проверяем права доступа
        if booking.student_id != student_id:
            raise PermissionDeniedError("Недостаточно прав для доступа к бронированию")
        
        # Проверяем статус
        if booking.status != BookingStatus.HOLD:
            raise BusinessLogicError(
                f"Нельзя отметить оплату для бронирования в статусе {booking.status.value}"
            )
        
        # Проверка истечения холда временно отключена (в модели нет поля)
        
        # Меняем статус
        # Проверяем валидность перехода статуса
        if not booking.can_transition_to(BookingStatus.AWAITING_VERIFICATION):
            raise BusinessLogicError(
                f"Нельзя перевести бронирование из статуса {booking.status.value} в AWAITING_VERIFICATION"
            )
        
        old_status = booking.status
        booking.status = BookingStatus.AWAITING_VERIFICATION
        booking.updated_at = datetime.now(timezone.utc)
        
        await self.db.commit()
        
        # Логируем
        logger.info(
            "Payment marked by student",
            booking_id=booking_id,
            student_id=student_id,
            old_status=old_status,
            new_status=booking.status
        )
        
        try:
            await self._create_audit_log(
                actor_id=student_id,
                action="MARK_PAYMENT",
                entity="booking",
                entity_id=booking_id,
                meta={"old_status": old_status.value, "new_status": booking.status.value}
            )
        except Exception as audit_error:
            logger.warning(
                "Failed to create audit log for payment marking",
                booking_id=booking_id,
                error=str(audit_error),
                exc_info=True
            )
        
        # TODO: Отправить уведомление администраторам о необходимости проверки оплаты
        
        try:
            return await self._build_booking_response(booking)
        except Exception as build_error:
            logger.error(
                "Failed to build booking response after marking payment, but payment was marked",
                booking_id=booking_id,
                error=str(build_error),
                exc_info=True
            )
            return BookingResponse(
                id=booking.id,
                student_id=booking.student_id,
                mentor_id=booking.mentor_id,
                starts_at=booking.starts_at,
                ends_at=booking.ends_at,
                duration_minutes=booking.duration_minutes,
                status=booking.status,
                price_amount=booking.price,
                price_currency=booking.currency,
                hold_expires_at=None,
                google_meet_link=booking.meeting_url,
                google_calendar_event_id=booking.meeting_event_id,
                intake_form=booking.intake_form or {},
                notes=booking.payment_note,
                created_at=booking.created_at,
                updated_at=booking.updated_at,
                mentor_name="Ментор",
                mentor_avatar_url=None,
                student_name="Студент",
                student_avatar_url=None
            )
    
    async def confirm_payment_by_admin(
        self,
        booking_id: UUID,
        admin_id: UUID,
        confirmation_data: BookingPaymentConfirmation
    ) -> BookingResponse:
        """Подтверждение или отклонение оплаты администратором."""
        booking = await self._get_booking_or_404(booking_id)
        
        # Проверяем статус
        if booking.status != BookingStatus.AWAITING_VERIFICATION:
            raise BusinessLogicError(
                f"Нельзя подтвердить оплату для бронирования в статусе {booking.status.value}"
            )
        
        old_status = booking.status
        logger.info(
            "Starting payment confirmation",
            booking_id=booking_id,
            old_status=str(old_status),
            payment_confirmed=confirmation_data.payment_confirmed
        )
        
        if confirmation_data.payment_confirmed:
            # Проверяем валидность перехода статуса
            if not booking.can_transition_to(BookingStatus.CONFIRMED):
                raise BusinessLogicError(
                    f"Нельзя перевести бронирование из статуса {booking.status.value} в CONFIRMED"
                )
            
            # Подтверждаем оплату
            booking.status = BookingStatus.CONFIRMED
            booking.payment_status = "PAID"
            booking.payment_verified_at = datetime.now(timezone.utc)
            
            # Сохраняем примечание к платежу (если есть)
            if confirmation_data.payment_notes or confirmation_data.payment_reference:
                ref = f" (ref: {confirmation_data.payment_reference})" if confirmation_data.payment_reference else ""
                booking.payment_note = (confirmation_data.payment_notes or "") + ref
            
            # Создаем событие в календаре
            # Не откатываем подтверждение если календарь недоступен - логируем ошибку
            logger.info("Attempting to create calendar event", booking_id=booking_id)
            try:
                calendar_event = await self._create_calendar_event(booking)
                booking.meeting_event_id = calendar_event.event_id
                booking.meeting_url = calendar_event.meet_link
                logger.info(
                    "Calendar event created successfully",
                    booking_id=booking_id,
                    event_id=calendar_event.event_id
                )
            except Exception as e:
                logger.error(
                    "Failed to create calendar event, but booking will be confirmed",
                    booking_id=booking_id,
                    error=str(e),
                    exc_info=True
                )
                # Не откатываем подтверждение - календарь не критичен
                # Бронирование будет подтверждено, но без ссылки на Google Meet
        else:
            # Проверяем валидность перехода статуса
            if not booking.can_transition_to(BookingStatus.REJECTED):
                raise BusinessLogicError(
                    f"Нельзя перевести бронирование из статуса {booking.status.value} в REJECTED"
                )
            
            # Отклоняем оплату
            booking.status = BookingStatus.REJECTED
            booking.payment_status = "REJECTED"
        
        # Общие заметки администратора сохраняем в notes
        if confirmation_data.payment_notes:
            booking.payment_note = confirmation_data.payment_notes
        booking.updated_at = datetime.now(timezone.utc)
        
        await self.db.commit()
        
        action = "confirmed" if confirmation_data.payment_confirmed else "rejected"
        logger.info(
            f"Payment {action} by admin",
            booking_id=booking_id,
            admin_id=admin_id,
            old_status=old_status,
            new_status=booking.status
        )
        
        try:
            await self._create_audit_log(
                actor_id=admin_id,
                action="CONFIRM_PAYMENT" if confirmation_data.payment_confirmed else "REJECT_PAYMENT",
                entity="booking",
                entity_id=booking_id,
                meta={
                    "old_status": old_status.value if hasattr(old_status, 'value') else str(old_status),
                    "new_status": booking.status.value if hasattr(booking.status, 'value') else str(booking.status),
                    "payment_reference": confirmation_data.payment_reference,
                    "notes": confirmation_data.payment_notes
                }
            )
        except Exception as audit_error:
            logger.warning(
                "Failed to create audit log for payment confirmation",
                booking_id=booking_id,
                error=str(audit_error),
                exc_info=True
            )
        
        # TODO: Отправить уведомления студенту и ментору
        
        try:
            return await self._build_booking_response(booking)
        except Exception as build_error:
            logger.error(
                "Failed to build booking response after payment confirmation, but payment was confirmed",
                booking_id=booking_id,
                error=str(build_error),
                exc_info=True
            )
            return BookingResponse(
                id=booking.id,
                student_id=booking.student_id,
                mentor_id=booking.mentor_id,
                starts_at=booking.starts_at,
                ends_at=booking.ends_at,
                duration_minutes=booking.duration_minutes,
                status=booking.status,
                price_amount=booking.price,
                price_currency=booking.currency,
                hold_expires_at=None,
                google_meet_link=booking.meeting_url,
                google_calendar_event_id=booking.meeting_event_id,
                intake_form=booking.intake_form or {},
                notes=booking.payment_note,
                created_at=booking.created_at,
                updated_at=booking.updated_at,
                mentor_name="Ментор",
                mentor_avatar_url=None,
                student_name="Студент",
                student_avatar_url=None
            )
    
    async def cancel_booking(
        self,
        booking_id: UUID,
        user_id: UUID,
        user_role: UserRole,
        cancellation_data: BookingCancellationRequest
    ) -> BookingResponse:
        """Отмена бронирования."""
        booking = await self._get_booking_or_404(booking_id)
        
        # Проверяем права доступа
        if not self._can_access_booking(booking, user_id, user_role):
            raise PermissionDeniedError("Недостаточно прав для доступа к бронированию")
        
        # Проверяем возможность отмены
        if not self._can_cancel_booking(booking, user_role, datetime.now(timezone.utc)):
            raise BusinessLogicError("Нельзя отменить это бронирование")
        
        # Проверяем валидность перехода статуса
        if not booking.can_transition_to(BookingStatus.CANCELLED):
            raise BusinessLogicError(
                f"Нельзя перевести бронирование из статуса {booking.status.value} в CANCELLED"
            )
        
        old_status = booking.status
        booking.status = BookingStatus.CANCELLED
        # Сохраним причину отмены в общих заметках
        if cancellation_data.reason:
            booking.payment_note = cancellation_data.reason
        booking.updated_at = datetime.now(timezone.utc)
        
        # Удаляем событие из календаря
        # Не блокируем отмену если календарь недоступен
        if booking.meeting_event_id:
            try:
                await self._delete_calendar_event(booking.meeting_event_id)
                logger.info(
                    "Calendar event deleted successfully",
                    booking_id=booking_id,
                    event_id=booking.meeting_event_id
                )
            except Exception as e:
                logger.error(
                    "Failed to delete calendar event, but booking will be cancelled",
                    booking_id=booking_id,
                    event_id=booking.meeting_event_id,
                    error=str(e),
                    exc_info=True
                )
                # Не прерываем отмену - календарь не критичен
        
        await self.db.commit()
        
        logger.info(
            "Booking cancelled",
            booking_id=booking_id,
            user_id=user_id,
            user_role=user_role,
            old_status=old_status,
            reason=cancellation_data.reason
        )
        
        try:
            await self._create_audit_log(
                actor_id=user_id,
                action="CANCEL_BOOKING",
                entity="booking",
                entity_id=booking_id,
                meta={
                    "old_status": old_status.value,
                    "new_status": booking.status.value,
                    "reason": cancellation_data.reason,
                    "request_refund": cancellation_data.request_refund
                }
            )
        except Exception as audit_error:
            logger.warning(
                "Failed to create audit log for booking cancellation",
                booking_id=booking_id,
                error=str(audit_error),
                exc_info=True
            )
        
        # TODO: Обработать возврат средств если requested
        # TODO: Отправить уведомления
        
        try:
            return await self._build_booking_response(booking)
        except Exception as build_error:
            logger.error(
                "Failed to build booking response after cancellation, but booking was cancelled",
                booking_id=booking_id,
                error=str(build_error),
                exc_info=True
            )
            return BookingResponse(
                id=booking.id,
                student_id=booking.student_id,
                mentor_id=booking.mentor_id,
                starts_at=booking.starts_at,
                ends_at=booking.ends_at,
                duration_minutes=booking.duration_minutes,
                status=booking.status,
                price_amount=booking.price,
                price_currency=booking.currency,
                hold_expires_at=None,
                google_meet_link=booking.meeting_url,
                google_calendar_event_id=booking.meeting_event_id,
                intake_form=booking.intake_form or {},
                notes=booking.payment_note,
                created_at=booking.created_at,
                updated_at=booking.updated_at,
                mentor_name="Ментор",
                mentor_avatar_url=None,
                student_name="Студент",
                student_avatar_url=None
            )
    
    async def mark_booking_completed(
        self,
        booking_id: UUID,
        admin_id: UUID,
        user_role: UserRole
    ) -> BookingResponse:
        """Отметить бронирование как завершенное."""
        if user_role != UserRole.ADMIN:
            raise PermissionDeniedError("Только администраторы могут завершать бронирования")
        
        booking = await self._get_booking_or_404(booking_id)
        
        # Безопасно получаем значение статуса для логирования
        current_status_value = booking.status.value if hasattr(booking.status, 'value') else str(booking.status)
        
        logger.info(
            "Marking booking as completed",
            booking_id=booking_id,
            admin_id=admin_id,
            current_status=current_status_value
        )
        
        # Проверяем статус (может быть строкой или enum)
        booking_status = booking.status
        if isinstance(booking_status, str):
            booking_status = BookingStatus(booking_status)
        
        # Проверяем статус и валидность перехода
        if booking_status != BookingStatus.CONFIRMED:
            raise BusinessLogicError(
                f"Нельзя завершить бронирование в статусе {current_status_value}. "
                f"Только подтвержденные бронирования можно завершить."
            )
        
        if not booking.can_transition_to(BookingStatus.COMPLETED):
            raise BusinessLogicError(
                f"Нельзя перевести бронирование из статуса {current_status_value} в COMPLETED"
            )
        
        # Сохраняем старое значение статуса (как enum, не как строка)
        old_status = booking_status  # Используем нормализованный статус
        old_status_value = old_status.value if hasattr(old_status, 'value') else str(old_status)
        
        booking.status = BookingStatus.COMPLETED
        booking.updated_at = datetime.now(timezone.utc)
        
        await self.db.commit()
        
        logger.info(
            "Booking marked as completed",
            booking_id=booking_id,
            admin_id=admin_id,
            old_status=old_status_value,
            new_status=BookingStatus.COMPLETED.value
        )
        
        # Перезагружаем объект с связанными данными после commit
        await self.db.refresh(booking, ["student", "mentor"])
        # Также нужно перезагрузить вложенные связи
        if booking.student:
            await self.db.refresh(booking.student, ["user"])
        if booking.mentor:
            await self.db.refresh(booking.mentor, ["user"])
        
        try:
            # Безопасно получаем значения статусов (могут быть строки после refresh)
            new_status_value = booking.status.value if hasattr(booking.status, 'value') else str(booking.status)
            
            await self._create_audit_log(
                actor_id=admin_id,
                action="MARK_BOOKING_COMPLETED",
                entity="booking",
                entity_id=booking_id,
                meta={
                    "old_status": old_status_value,
                    "new_status": new_status_value
                }
            )
        except Exception as audit_error:
            logger.warning(
                "Failed to create audit log for marking booking as completed",
                booking_id=booking_id,
                error=str(audit_error),
                exc_info=True
            )
        
        try:
            return await self._build_booking_response(booking)
        except Exception as build_error:
            logger.error(
                "Failed to build booking response after marking as completed, but booking was marked",
                booking_id=booking_id,
                error=str(build_error),
                exc_info=True
            )
            return BookingResponse(
                id=booking.id,
                student_id=booking.student_id,
                mentor_id=booking.mentor_id,
                starts_at=booking.starts_at,
                ends_at=booking.ends_at,
                duration_minutes=booking.duration_minutes,
                status=booking.status,
                price_amount=booking.price,
                price_currency=booking.currency,
                hold_expires_at=None,
                google_meet_link=booking.meeting_url,
                google_calendar_event_id=booking.meeting_event_id,
                intake_form=booking.intake_form or {},
                notes=booking.payment_note,
                created_at=booking.created_at,
                updated_at=booking.updated_at,
                mentor_name="Ментор",
                mentor_avatar_url=None,
                student_name="Студент",
                student_avatar_url=None
            )
    
    async def mark_booking_completed_by_mentor(
        self,
        booking_id: UUID,
        mentor_id: UUID
    ) -> BookingResponse:
        """Отметить бронирование как завершенное ментором."""
        booking = await self._get_booking_or_404(booking_id)
        
        if booking.mentor_id != mentor_id:
            raise PermissionDeniedError("Вы можете завершать только свои консультации")
        
        # Безопасно получаем значение статуса для логирования
        current_status_value = booking.status.value if hasattr(booking.status, 'value') else str(booking.status)
        
        logger.info(
            "Marking booking as completed by mentor",
            booking_id=booking_id,
            mentor_id=mentor_id,
            current_status=current_status_value
        )
        
        # Проверяем статус (может быть строкой или enum)
        booking_status = booking.status
        if isinstance(booking_status, str):
            booking_status = BookingStatus(booking_status)
        
        if booking_status != BookingStatus.CONFIRMED:
            raise BusinessLogicError(
                f"Нельзя завершить бронирование в статусе {current_status_value}. "
                f"Только подтвержденные бронирования можно завершить."
            )
        
        if not booking.can_transition_to(BookingStatus.COMPLETED):
            raise BusinessLogicError(
                f"Нельзя перевести бронирование из статуса {current_status_value} в COMPLETED"
            )
        
        # Сохраняем старое значение статуса (как enum, не как строка)
        old_status = booking_status  # Используем нормализованный статус
        old_status_value = old_status.value if hasattr(old_status, 'value') else str(old_status)
        
        booking.status = BookingStatus.COMPLETED
        booking.updated_at = datetime.now(timezone.utc)
        
        await self.db.commit()
        
        logger.info(
            "Booking marked as completed by mentor",
            booking_id=booking_id,
            mentor_id=mentor_id,
            old_status=old_status_value,
            new_status=BookingStatus.COMPLETED.value
        )
        
        # Перезагружаем объект с связанными данными после commit
        await self.db.refresh(booking, ["student", "mentor"])
        # Также нужно перезагрузить вложенные связи
        if booking.student:
            await self.db.refresh(booking.student, ["user"])
        if booking.mentor:
            await self.db.refresh(booking.mentor, ["user"])
        
        try:
            # Безопасно получаем значения статусов (могут быть строки после refresh)
            new_status_value = booking.status.value if hasattr(booking.status, 'value') else str(booking.status)
            
            await self._create_audit_log(
                actor_id=mentor_id,
                action="MARK_BOOKING_COMPLETED_BY_MENTOR",
                entity="booking",
                entity_id=booking_id,
                meta={
                    "old_status": old_status_value,
                    "new_status": new_status_value
                }
            )
        except Exception as audit_error:
            logger.warning(
                "Failed to create audit log for marking booking as completed by mentor",
                booking_id=booking_id,
                error=str(audit_error),
                exc_info=True
            )
        
        try:
            return await self._build_booking_response(booking)
        except Exception as build_error:
            logger.error(
                "Failed to build booking response after marking as completed by mentor, but booking was marked",
                booking_id=booking_id,
                error=str(build_error),
                exc_info=True
            )
            starts_at = booking.starts_at
            ends_at = booking.ends_at
            created_at = booking.created_at
            updated_at = booking.updated_at
            
            if starts_at and starts_at.tzinfo is None:
                starts_at = starts_at.replace(tzinfo=timezone.utc)
            if ends_at and ends_at.tzinfo is None:
                ends_at = ends_at.replace(tzinfo=timezone.utc)
            if created_at and created_at.tzinfo is None:
                created_at = created_at.replace(tzinfo=timezone.utc)
            if updated_at and updated_at.tzinfo is None:
                updated_at = updated_at.replace(tzinfo=timezone.utc)
            
            return BookingResponse(
                id=booking.id,
                student_id=booking.student_id,
                mentor_id=booking.mentor_id,
                starts_at=starts_at,
                ends_at=ends_at,
                duration_minutes=booking.duration_minutes,
                status=booking.status,
                price_amount=booking.price,
                price_currency=booking.currency,
                hold_expires_at=None,
                google_meet_link=booking.meeting_url,
                google_calendar_event_id=booking.meeting_event_id,
                intake_form=booking.intake_form or {},
                notes=booking.payment_note,
                created_at=created_at,
                updated_at=updated_at,
                mentor_name="Ментор",
                mentor_avatar_url=None,
                student_name="Студент",
                student_avatar_url=None
            )
    
    async def mark_booking_no_show(
        self,
        booking_id: UUID,
        admin_id: UUID,
        user_role: UserRole,
        no_show_type: str = "student"
    ) -> BookingResponse:
        """Отметить бронирование как неявку."""
        if user_role != UserRole.ADMIN:
            raise PermissionDeniedError("Только администраторы могут отмечать неявки")
        
        booking = await self._get_booking_or_404(booking_id)
        
        logger.info(
            "Marking booking as no show",
            booking_id=booking_id,
            admin_id=admin_id,
            no_show_type=no_show_type,
            current_status=booking.status.value
        )
        
        # Проверяем статус
        if booking.status != BookingStatus.CONFIRMED:
            raise BusinessLogicError(
                f"Нельзя отметить неявку для бронирования в статусе {booking.status.value}. "
                f"Только подтвержденные бронирования можно отметить как неявку."
            )
        
        old_status = booking.status
        
        # Определяем тип неявки и проверяем валидность перехода
        if no_show_type == "student":
            if not booking.can_transition_to(BookingStatus.NO_SHOW_STUDENT):
                raise BusinessLogicError(
                    f"Нельзя перевести бронирование из статуса {booking.status.value} в NO_SHOW_STUDENT"
                )
            booking.status = BookingStatus.NO_SHOW_STUDENT
        elif no_show_type == "mentor":
            if not booking.can_transition_to(BookingStatus.NO_SHOW_MENTOR):
                raise BusinessLogicError(
                    f"Нельзя перевести бронирование из статуса {booking.status.value} в NO_SHOW_MENTOR"
                )
            booking.status = BookingStatus.NO_SHOW_MENTOR
        else:
            raise BusinessLogicError(f"Неизвестный тип неявки: {no_show_type}")
        
        booking.updated_at = datetime.now(timezone.utc)
        
        await self.db.commit()
        
        logger.info(
            "Booking marked as no show",
            booking_id=booking_id,
            admin_id=admin_id,
            no_show_type=no_show_type,
            old_status=old_status,
            new_status=booking.status
        )
        
        try:
            await self._create_audit_log(
                actor_id=admin_id,
                action="MARK_BOOKING_NO_SHOW",
                entity="booking",
                entity_id=booking_id,
                meta={
                    "old_status": old_status.value,
                    "new_status": booking.status.value,
                    "no_show_type": no_show_type
                }
            )
        except Exception as audit_error:
            logger.warning(
                "Failed to create audit log for marking booking as no show",
                booking_id=booking_id,
                error=str(audit_error),
                exc_info=True
            )
        
        try:
            return await self._build_booking_response(booking)
        except Exception as build_error:
            logger.error(
                "Failed to build booking response after marking as no show, but booking was marked",
                booking_id=booking_id,
                error=str(build_error),
                exc_info=True
            )
            return BookingResponse(
                id=booking.id,
                student_id=booking.student_id,
                mentor_id=booking.mentor_id,
                starts_at=booking.starts_at,
                ends_at=booking.ends_at,
                duration_minutes=booking.duration_minutes,
                status=booking.status,
                price_amount=booking.price,
                price_currency=booking.currency,
                hold_expires_at=None,
                google_meet_link=booking.meeting_url,
                google_calendar_event_id=booking.meeting_event_id,
                intake_form=booking.intake_form or {},
                notes=booking.payment_note,
                created_at=booking.created_at,
                updated_at=booking.updated_at,
                mentor_name="Ментор",
                mentor_avatar_url=None,
                student_name="Студент",
                student_avatar_url=None
            )
    
    async def reschedule_booking(
        self,
        booking_id: UUID,
        user_id: UUID,
        user_role: UserRole,
        reschedule_data: BookingRescheduleRequest
    ) -> BookingResponse:
        """Перенос бронирования."""
        booking = await self._get_booking_or_404(booking_id)
        
        # Проверяем права доступа
        if not self._can_access_booking(booking, user_id, user_role):
            raise PermissionDeniedError("Недостаточно прав для доступа к бронированию")
        
        # Проверяем статус текущего бронирования - можно переносить только активные
        if booking.status not in [BookingStatus.CONFIRMED, BookingStatus.AWAITING_VERIFICATION]:
            raise BusinessLogicError(
                f"Нельзя перенести бронирование в статусе {booking.status.value}. "
                f"Можно переносить только подтвержденные или ожидающие подтверждения бронирования."
            )
        
        # Проверяем возможность переноса (для AWAITING_VERIFICATION разрешаем перенос админу)
        now = datetime.now(timezone.utc)
        if booking.status == BookingStatus.AWAITING_VERIFICATION:
            if user_role != UserRole.ADMIN:
                raise BusinessLogicError("Только администратор может переносить бронирования, ожидающие подтверждения оплаты")
        elif not self._can_reschedule_booking(booking, user_role, now):
            raise BusinessLogicError("Нельзя перенести это бронирование")
        
        # Проверяем доступность нового слота (исключаем текущее бронирование)
        await self._check_slot_availability(
            mentor_id=booking.mentor_id,
            starts_at=reschedule_data.new_starts_at,
            duration_minutes=booking.duration_minutes,
            exclude_booking_id=booking_id
        )
        
        # Сохраняем старые данные
        old_starts_at = booking.starts_at
        old_ends_at = booking.ends_at
        
        # Обновляем время
        booking.starts_at = reschedule_data.new_starts_at
        booking.ends_at = reschedule_data.new_starts_at + timedelta(minutes=booking.duration_minutes)
        # Сохраняем причину переноса в заметках
        if reschedule_data.reason:
            booking.payment_note = reschedule_data.reason
        booking.updated_at = datetime.now(timezone.utc)
        
        # Обновляем событие в календаре
        if booking.meeting_event_id:
            try:
                await self._update_calendar_event(booking)
            except Exception as e:
                logger.error("Failed to update calendar event", booking_id=booking_id, error=str(e))
        
        await self.db.commit()
        
        logger.info(
            "Booking rescheduled",
            booking_id=booking_id,
            user_id=user_id,
            user_role=user_role,
            old_starts_at=old_starts_at,
            new_starts_at=booking.starts_at,
            reason=reschedule_data.reason
        )
        
        try:
            await self._create_audit_log(
                actor_id=user_id,
                action="RESCHEDULE_BOOKING",
                entity="booking",
                entity_id=booking_id,
                meta={
                    "old_starts_at": old_starts_at.isoformat(),
                    "new_starts_at": booking.starts_at.isoformat(),
                    "old_ends_at": old_ends_at.isoformat(),
                    "new_ends_at": booking.ends_at.isoformat(),
                    "reason": reschedule_data.reason
                }
            )
        except Exception as audit_error:
            logger.warning(
                "Failed to create audit log for booking reschedule",
                booking_id=booking_id,
                error=str(audit_error),
                exc_info=True
            )
        
        # TODO: Отправить уведомления
        
        try:
            return await self._build_booking_response(booking)
        except Exception as build_error:
            logger.error(
                "Failed to build booking response after reschedule, but booking was rescheduled",
                booking_id=booking_id,
                error=str(build_error),
                exc_info=True
            )
            return BookingResponse(
                id=booking.id,
                student_id=booking.student_id,
                mentor_id=booking.mentor_id,
                starts_at=booking.starts_at,
                ends_at=booking.ends_at,
                duration_minutes=booking.duration_minutes,
                status=booking.status,
                price_amount=booking.price,
                price_currency=booking.currency,
                hold_expires_at=None,
                google_meet_link=booking.meeting_url,
                google_calendar_event_id=booking.meeting_event_id,
                intake_form=booking.intake_form or {},
                notes=booking.payment_note,
                created_at=booking.created_at,
                updated_at=booking.updated_at,
                mentor_name="Ментор",
                mentor_avatar_url=None,
                student_name="Студент",
                student_avatar_url=None
            )
    
    async def get_booking_stats(
        self,
        user_id: Optional[UUID] = None,
        user_role: Optional[UserRole] = None
    ) -> BookingStats:
        """Получение статистики бронирований."""
        now = datetime.now(timezone.utc)
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        week_start = today_start - timedelta(days=now.weekday())
        month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        
        # Фильтрация по правам доступа
        if user_role == UserRole.MENTOR and user_id:
            filter_condition = Booking.mentor_id == user_id
        elif user_role == UserRole.STUDENT and user_id:
            filter_condition = Booking.student_id == user_id
        else:
            filter_condition = True  # Админ или без фильтра
        
        base_query = select(Booking)
        if filter_condition is not True:
            base_query = base_query.where(filter_condition)
        
        # Общее количество
        total_result = await self.db.execute(
            select(func.count(Booking.id)).where(filter_condition) if filter_condition is not True 
            else select(func.count(Booking.id))
        )
        total_bookings = total_result.scalar() or 0
        
        # По статусам
        pending_payment_result = await self.db.execute(
            select(func.count(Booking.id)).where(
                and_(
                    filter_condition if filter_condition is not True else True,
                    Booking.status == BookingStatus.AWAITING_VERIFICATION
                )
            )
        )
        pending_payment = pending_payment_result.scalar() or 0
        
        confirmed_result = await self.db.execute(
            select(func.count(Booking.id)).where(
                and_(
                    filter_condition if filter_condition is not True else True,
                    Booking.status == BookingStatus.CONFIRMED
                )
            )
        )
        confirmed = confirmed_result.scalar() or 0
        
        completed_result = await self.db.execute(
            select(func.count(Booking.id)).where(
                and_(
                    filter_condition if filter_condition is not True else True,
                    Booking.status == BookingStatus.COMPLETED
                )
            )
        )
        completed = completed_result.scalar() or 0
        
        cancelled_result = await self.db.execute(
            select(func.count(Booking.id)).where(
                and_(
                    filter_condition if filter_condition is not True else True,
                    Booking.status == BookingStatus.CANCELLED
                )
            )
        )
        cancelled = cancelled_result.scalar() or 0
        
        # По времени
        today_result = await self.db.execute(
            select(func.count(Booking.id)).where(
                and_(
                    filter_condition if filter_condition is not True else True,
                    Booking.created_at >= today_start
                )
            )
        )
        today = today_result.scalar() or 0
        
        this_week_result = await self.db.execute(
            select(func.count(Booking.id)).where(
                and_(
                    filter_condition if filter_condition is not True else True,
                    Booking.created_at >= week_start
                )
            )
        )
        this_week = this_week_result.scalar() or 0
        
        this_month_result = await self.db.execute(
            select(func.count(Booking.id)).where(
                and_(
                    filter_condition if filter_condition is not True else True,
                    Booking.created_at >= month_start
                )
            )
        )
        this_month = this_month_result.scalar() or 0
        
        # Финансовые показатели
        revenue_query = select(func.sum(Booking.price)).where(
            and_(
                filter_condition if filter_condition is not True else True,
                Booking.status == BookingStatus.COMPLETED
            )
        )
        revenue_result = await self.db.execute(revenue_query)
        total_revenue = revenue_result.scalar() or Decimal("0")
        
        pending_revenue_query = select(func.sum(Booking.price)).where(
            and_(
                filter_condition if filter_condition is not True else True,
                Booking.status.in_([BookingStatus.CONFIRMED, BookingStatus.AWAITING_VERIFICATION])
            )
        )
        pending_revenue_result = await self.db.execute(pending_revenue_query)
        pending_revenue = pending_revenue_result.scalar() or Decimal("0")
        
        # Средние показатели
        avg_duration_query = select(func.avg(Booking.duration_minutes)).where(
            filter_condition if filter_condition is not True else True
        )
        avg_duration_result = await self.db.execute(avg_duration_query)
        average_session_duration = float(avg_duration_result.scalar() or 60.0)
        
        avg_price_query = select(func.avg(Booking.price)).where(
            filter_condition if filter_condition is not True else True
        )
        avg_price_result = await self.db.execute(avg_price_query)
        average_price = avg_price_result.scalar() or Decimal("30000")
        
        return BookingStats(
            total_bookings=total_bookings,
            pending_payment=pending_payment,
            confirmed=confirmed,
            completed=completed,
            cancelled=cancelled,
            today=today,
            this_week=this_week,
            this_month=this_month,
            total_revenue=total_revenue,
            pending_revenue=pending_revenue,
            average_session_duration=average_session_duration,
            average_price=average_price
        )
    
    async def _get_booking_or_404(self, booking_id: UUID) -> Booking:
        """Получение бронирования или 404."""
        query = select(Booking).options(
            selectinload(Booking.student).selectinload(Student.user),
            selectinload(Booking.mentor).selectinload(Mentor.user),
            selectinload(Booking.review)
        ).where(Booking.id == booking_id)
        
        result = await self.db.execute(query)
        booking = result.scalar_one_or_none()
        
        if not booking:
            raise NotFoundError("Booking", str(booking_id))
        
        return booking
    
    async def _get_mentor_or_404(self, mentor_id: UUID) -> Mentor:
        """Получение ментора или 404."""
        query = select(Mentor).options(selectinload(Mentor.user)).where(Mentor.user_id == mentor_id)
        result = await self.db.execute(query)
        mentor = result.scalar_one_or_none()
        
        if not mentor or not mentor.user.is_active:
            raise NotFoundError("Mentor", str(mentor_id))
        
        return mentor
    
    async def _check_slot_availability(
        self,
        mentor_id: UUID,
        starts_at: datetime,
        duration_minutes: int,
        exclude_booking_id: Optional[UUID] = None
    ) -> None:
        """
        Проверка доступности слота для бронирования.
        
        Использует SELECT FOR UPDATE для предотвращения race conditions.
        """
        ends_at = starts_at + timedelta(minutes=duration_minutes)
        
        # Получаем настройки ментора для буферного времени
        from modules.availability.domain.models import MentorSettings
        settings_query = select(MentorSettings).where(MentorSettings.mentor_id == mentor_id)
        settings_result = await self.db.execute(settings_query)
        mentor_settings = settings_result.scalar_one_or_none()
        buffer_minutes = mentor_settings.buffer_time_minutes if mentor_settings else 15
        
        # Учитываем буферное время при проверке пересечений
        # Новое бронирование должно начинаться не раньше чем через buffer_minutes после окончания предыдущего
        # И заканчиваться не позже чем за buffer_minutes до начала следующего
        check_starts_at = starts_at - timedelta(minutes=buffer_minutes)
        check_ends_at = ends_at + timedelta(minutes=buffer_minutes)
        
        # Проверяем пересечения с другими бронированиями
        # Используем упрощенную и более надежную формулу: два интервала пересекаются,
        # если start1 < end2 AND start2 < end1
        # Исключаем EXPIRED статус - они не должны блокировать слот
        # Также исключаем истекшие HOLD бронирования (старше BOOKING_HOLD_DURATION_MINUTES)
        now = datetime.now(timezone.utc)
        from core.config import settings
        hold_duration = settings.BOOKING_HOLD_DURATION_MINUTES
        hold_expiry_threshold = now - timedelta(minutes=hold_duration)
        
        query = select(Booking).where(
            and_(
                Booking.mentor_id == mentor_id,
                or_(
                    Booking.status.in_([
                        BookingStatus.AWAITING_VERIFICATION,
                        BookingStatus.AWAITING_VERIFICATION.value,
                        BookingStatus.CONFIRMED,
                        BookingStatus.CONFIRMED.value
                    ]),
                    and_(
                        or_(
                            Booking.status == BookingStatus.HOLD,
                            Booking.status == BookingStatus.HOLD.value
                        ),
                        Booking.created_at > hold_expiry_threshold
                    )
                ),
                Booking.starts_at < check_ends_at,
                Booking.ends_at > check_starts_at
            )
        ).with_for_update()
        
        if exclude_booking_id:
            query = query.where(Booking.id != exclude_booking_id)
        
        result = await self.db.execute(query)
        conflicting_booking = result.scalar_one_or_none()
        
        if conflicting_booking:
            raise BusinessLogicError(
                f"Слот недоступен: конфликт с бронированием {conflicting_booking.id}. "
                f"Учитывается буферное время {buffer_minutes} минут между консультациями."
            )
        
        # Проверяем доступность ментора через availability rules
        weekday = starts_at.weekday()  # 0 = Monday, 6 = Sunday
        start_time = starts_at.time()
        end_time = ends_at.time()
        
        # Ищем правило доступности для этого дня недели
        # Проверяем, что весь интервал попадает в доступное время
        availability_query = select(AvailabilityRule).where(
            and_(
                AvailabilityRule.mentor_id == mentor_id,
                AvailabilityRule.weekday == weekday,
                AvailabilityRule.time_start <= start_time,
                AvailabilityRule.time_end >= end_time
            )
        ).limit(1)
        
        availability_result = await self.db.execute(availability_query)
        availability_rule = availability_result.scalar_one_or_none()
        
        if not availability_rule:
            raise BusinessLogicError(
                f"Ментор недоступен в выбранное время. Проверьте расписание ментора."
            )
        
        # Проверяем, не попадает ли слот в перерывы (breaks)
        if availability_rule.breaks_json:
            for break_period in availability_rule.breaks_json:
                try:
                    break_start_str = break_period.get('start', '')
                    break_end_str = break_period.get('end', '')
                    
                    if not break_start_str or not break_end_str:
                        continue
                    
                    break_start = time.fromisoformat(break_start_str)
                    break_end = time.fromisoformat(break_end_str)
                    
                    # Проверяем пересечение с перерывом
                    # Слот пересекается с перерывом, если start_time < break_end AND end_time > break_start
                    if start_time < break_end and end_time > break_start:
                        break_title = break_period.get('title', f'{break_start_str}-{break_end_str}')
                        raise BusinessLogicError(
                            f"Ментор недоступен в выбранное время: попадает в перерыв ({break_title})"
                        )
                except (ValueError, KeyError) as e:
                    # Игнорируем некорректные перерывы, но логируем
                    logger.warning(f"Invalid break period format: {break_period}, error: {e}")
                    continue
        
        # Проверяем, не попадает ли слот в период отсутствия (time off)
        time_off_query = select(TimeOff).where(
            and_(
                TimeOff.mentor_id == mentor_id,
                TimeOff.starts_at < ends_at,
                TimeOff.ends_at > starts_at
            )
        )
        
        time_off_result = await self.db.execute(time_off_query)
        time_off = time_off_result.scalar_one_or_none()
        
        if time_off:
            raise BusinessLogicError(
                f"Ментор недоступен в выбранное время: период отсутствия до {time_off.ends_at.strftime('%Y-%m-%d %H:%M')}"
            )
    
    async def _calculate_price(self, mentor: Mentor, duration_minutes: int) -> Decimal:
        """Расчет цены консультации."""
        if duration_minutes == 30:
            return mentor.price_30 or Decimal("15000")
        elif duration_minutes == 45:
            return mentor.price_45 or Decimal("22500")
        elif duration_minutes == 60:
            return mentor.price_60 or Decimal("30000")
        else:
            # Пропорциональный расчет для нестандартных длительностей
            base_price = mentor.price_60 or Decimal("30000")
            return (base_price / 60) * duration_minutes
    
    async def _build_booking_response(self, booking: Booking) -> BookingResponse:
        """Построение ответа с бронированием."""
        student = getattr(booking, 'student', None)
        mentor = getattr(booking, 'mentor', None)
        
        mentor_name = "Ментор"
        mentor_avatar_url = None
        student_name = "Студент"
        student_avatar_url = None
        
        mentor_email = None
        if mentor:
            mentor_user = getattr(mentor, 'user', None)
            if mentor_user:
                mentor_name = mentor_user.name or mentor_user.email or "Ментор"
                mentor_email = mentor_user.email
                mentor_avatar_url = getattr(mentor, 'avatar_url', None)
        
        student_email = None
        if student:
            student_user = getattr(student, 'user', None)
            if student_user:
                student_name = student_user.name or student_user.email or "Студент"
                student_email = student_user.email
                student_avatar_url = getattr(student, 'avatar_url', None)
        
        # Проверяем наличие отзыва
        has_review = getattr(booking, 'review', None) is not None
        
        starts_at = booking.starts_at
        ends_at = booking.ends_at
        created_at = booking.created_at
        updated_at = booking.updated_at
        
        if starts_at and starts_at.tzinfo is None:
            starts_at = starts_at.replace(tzinfo=timezone.utc)
        if ends_at and ends_at.tzinfo is None:
            ends_at = ends_at.replace(tzinfo=timezone.utc)
        if created_at and created_at.tzinfo is None:
            created_at = created_at.replace(tzinfo=timezone.utc)
        if updated_at and updated_at.tzinfo is None:
            updated_at = updated_at.replace(tzinfo=timezone.utc)
        
        return BookingResponse(
            id=booking.id,
            student_id=booking.student_id,
            mentor_id=booking.mentor_id,
            starts_at=starts_at,
            ends_at=ends_at,
            duration_minutes=booking.duration_minutes,
            status=booking.status,
            price_amount=booking.price,
            price_currency=booking.currency,
            hold_expires_at=None,
            google_meet_link=booking.meeting_url,
            google_calendar_event_id=booking.meeting_event_id,
            intake_form=booking.intake_form or {},
            notes=booking.payment_note,
            created_at=created_at,
            updated_at=updated_at,
            mentor_name=mentor_name,
            mentor_email=mentor_email,
            mentor_avatar_url=mentor_avatar_url,
            student_name=student_name,
            student_email=student_email,
            student_avatar_url=student_avatar_url,
            has_review=has_review
        )
    
    def _can_access_booking(self, booking: Booking, user_id: UUID, user_role: UserRole) -> bool:
        """Проверка прав доступа к бронированию."""
        if user_role == UserRole.ADMIN:
            return True
        elif user_role == UserRole.STUDENT and booking.student_id == user_id:
            return True
        elif user_role == UserRole.MENTOR and booking.mentor_id == user_id:
            return True
        else:
            return False
    
    def _can_cancel_booking(self, booking: Booking, user_role: UserRole, now: datetime) -> bool:
        """Проверка возможности отмены бронирования."""
        # Админ может отменить любое активное бронирование независимо от времени
        if user_role == UserRole.ADMIN:
            return booking.status in [
                BookingStatus.HOLD,
                BookingStatus.AWAITING_VERIFICATION,
                BookingStatus.CONFIRMED
            ]
        
        # Другие пользователи могут отменить только до начала консультации
        starts_at = booking.starts_at
        if starts_at.tzinfo is None:
            starts_at = starts_at.replace(tzinfo=timezone.utc)
        
        if starts_at <= now:
            return False
        
        # Проверяем статус
        return booking.status in [
            BookingStatus.HOLD,
            BookingStatus.AWAITING_VERIFICATION,
            BookingStatus.CONFIRMED
        ]
    
    def _can_reschedule_booking(self, booking: Booking, user_role: UserRole, now: datetime) -> bool:
        """Проверка возможности переноса бронирования."""
        # Админ может перенести подтвержденные бронирования
        if user_role == UserRole.ADMIN:
            return booking.status == BookingStatus.CONFIRMED
        
        # Другие пользователи могут переносить только подтвержденные бронирования
        # и только если до начала больше 24 часов
        if booking.status != BookingStatus.CONFIRMED:
            return False
        
        starts_at = booking.starts_at
        if starts_at.tzinfo is None:
            starts_at = starts_at.replace(tzinfo=timezone.utc)
        
        time_until_start = starts_at - now
        return time_until_start > timedelta(hours=24)
    
    def _can_mark_payment(self, booking: Booking, user_id: UUID, user_role: UserRole) -> bool:
        """Проверка возможности отметки оплаты."""
        return (
            user_role == UserRole.STUDENT and
            booking.student_id == user_id and
            booking.status == BookingStatus.HOLD
        )
    
    def _get_cancellation_deadline(self, booking: Booking) -> Optional[datetime]:
        """Получение крайнего срока для отмены."""
        if booking.status in [BookingStatus.HOLD, BookingStatus.AWAITING_VERIFICATION]:
            starts_at = booking.starts_at
            if starts_at and starts_at.tzinfo is None:
                starts_at = starts_at.replace(tzinfo=timezone.utc)
            return starts_at
        elif booking.status == BookingStatus.CONFIRMED:
            # За 2 часа до начала
            starts_at = booking.starts_at
            if starts_at and starts_at.tzinfo is None:
                starts_at = starts_at.replace(tzinfo=timezone.utc)
            return starts_at - timedelta(hours=2)
        else:
            return None
    
    def _get_reschedule_deadline(self, booking: Booking) -> Optional[datetime]:
        """Получение крайнего срока для переноса."""
        if booking.status == BookingStatus.CONFIRMED:
            # За 24 часа до начала
            starts_at = booking.starts_at
            if starts_at and starts_at.tzinfo is None:
                starts_at = starts_at.replace(tzinfo=timezone.utc)
            return starts_at - timedelta(hours=24)
        else:
            return None
    
    async def _create_calendar_event(self, booking: Booking) -> CalendarEventResponse:
        """Создание события в Google Calendar с Google Meet ссылкой."""
        logger.info("Creating calendar event", booking_id=booking.id)
        
        # Проверяем доступность Google Calendar сервиса
        is_available = google_calendar_service.is_available()
        logger.info(
            "Google Calendar service status",
            booking_id=booking.id,
            is_available=is_available,
            service_exists=google_calendar_service.service is not None
        )
        
        # Загружаем данные пользователей если не загружены
        if not hasattr(booking, 'student') or booking.student is None:
            logger.info("Loading student data", booking_id=booking.id)
            await self.db.refresh(booking, ["student"])
        if not hasattr(booking, 'mentor') or booking.mentor is None:
            logger.info("Loading mentor data", booking_id=booking.id)
            await self.db.refresh(booking, ["mentor"])
        
        # Получаем emails и имена
        if not hasattr(booking.student, 'user') or booking.student.user is None:
            logger.error("Student user data not found", booking_id=booking.id)
            raise BusinessLogicError("Данные студента не найдены")
        if not hasattr(booking.mentor, 'user') or booking.mentor.user is None:
            logger.error("Mentor user data not found", booking_id=booking.id)
            raise BusinessLogicError("Данные ментора не найдены")
        
        student_email = booking.student.user.email
        student_name = booking.student.user.name or "Студент"
        mentor_email = booking.mentor.user.email
        mentor_name = booking.mentor.user.name or "Ментор"
        
        logger.info(
            "Participant emails",
            booking_id=booking.id,
            student_email=student_email,
            mentor_email=mentor_email
        )
        
        if not student_email:
            raise BusinessLogicError("Email студента не указан")
        if not mentor_email:
            raise BusinessLogicError("Email ментора не указан")
        
        try:
            logger.info(
                "Calling google_calendar_service.create_meeting",
                booking_id=booking.id,
                starts_at=booking.starts_at.isoformat() if booking.starts_at else None,
                duration_minutes=booking.duration_minutes
            )
            # Создаем встречу через Google Calendar
            # timezone будет извлечен из booking.starts_at автоматически
            result = await google_calendar_service.create_meeting(
                booking_id=booking.id,
                student_name=student_name,
                student_email=student_email,
                mentor_name=mentor_name,
                mentor_email=mentor_email,
                starts_at=booking.starts_at,
                duration_minutes=booking.duration_minutes
            )
            logger.info(
                "Google Calendar create_meeting result",
                booking_id=booking.id,
                event_id=result.get('event_id'),
                meeting_url=result.get('meeting_url')
            )
            
            return CalendarEventResponse(
                event_id=result['event_id'],
                event_url=result.get('html_link', ''),
                meet_link=result['meeting_url']
            )
        except Exception as e:
            logger.error(
                "Failed to create Google Calendar event",
                booking_id=booking.id,
                error=str(e),
                exc_info=True
            )
            raise BusinessLogicError(
                f"Не удалось создать событие в Google Calendar: {str(e)}"
            )
    
    async def _update_calendar_event(self, booking: Booking) -> None:
        """Обновление события в Google Calendar."""
        logger.info("Updating calendar event", booking_id=booking.id)
        
        if not booking.meeting_event_id:
            logger.warning("No event ID to update", booking_id=booking.id)
            return
        
        try:
            # Определяем статус в Google Calendar
            calendar_status = None
            if booking.status == BookingStatus.CANCELLED:
                calendar_status = 'cancelled'
            elif booking.status == BookingStatus.CONFIRMED:
                calendar_status = 'confirmed'
            
            await google_calendar_service.update_meeting(
                event_id=booking.meeting_event_id,
                starts_at=booking.starts_at,
                duration_minutes=booking.duration_minutes,
                status=calendar_status
            )
            logger.info("Calendar event updated successfully", booking_id=booking.id)
        except Exception as e:
            logger.error(f"Failed to update calendar event: {e}", booking_id=booking.id)
    
    async def _delete_calendar_event(self, event_id: str) -> None:
        """Удаление события из Google Calendar."""
        logger.info("Deleting calendar event", event_id=event_id)
        
        try:
            await google_calendar_service.cancel_meeting(event_id)
            logger.info("Calendar event deleted successfully", event_id=event_id)
        except Exception as e:
            logger.error(
                "Failed to delete calendar event",
                event_id=event_id,
                error=str(e),
                exc_info=True
            )
            # Пробрасываем исключение, но вызывающий код должен обработать его gracefully
            raise
    
    async def expire_hold_bookings(self) -> int:
        """
        Автоматическое истечение HOLD бронирований.
        Переводит истекшие HOLD бронирования в статус EXPIRED.
        Возвращает количество истекших бронирований.
        """
        now = datetime.now(timezone.utc)
        from core.config import settings
        hold_duration = settings.BOOKING_HOLD_DURATION_MINUTES
        expiry_threshold = now - timedelta(minutes=hold_duration)
        
        logger.info(
            "Checking for expired HOLD bookings",
            expiry_threshold=expiry_threshold.isoformat(),
            hold_duration_minutes=hold_duration
        )
        
        # Находим все истекшие HOLD бронирования
        expired_query = select(Booking).where(
            and_(
                or_(
                    Booking.status == BookingStatus.HOLD,
                    Booking.status == BookingStatus.HOLD.value
                ),
                Booking.created_at <= expiry_threshold
            )
        )
        
        result = await self.db.execute(expired_query)
        expired_bookings = result.scalars().all()
        
        expired_count = 0
        for booking in expired_bookings:
            # Проверяем валидность перехода статуса
            if not booking.can_transition_to(BookingStatus.EXPIRED):
                status_str = booking.status.value if hasattr(booking.status, 'value') else str(booking.status)
                logger.warning(
                    "Cannot transition booking to EXPIRED",
                    booking_id=booking.id,
                    current_status=status_str
                )
                continue
            
            old_status = booking.status
            booking.status = BookingStatus.EXPIRED
            booking.updated_at = now
            expired_count += 1
            
            old_status_str = old_status.value if hasattr(old_status, 'value') else str(old_status)
            new_status_str = booking.status.value if hasattr(booking.status, 'value') else str(booking.status)
            
            logger.info(
                "Expired HOLD booking",
                booking_id=booking.id,
                old_status=old_status_str,
                new_status=new_status_str,
                created_at=booking.created_at.isoformat(),
                expired_at=now.isoformat()
            )
        
        if expired_count > 0:
            await self.db.commit()
            logger.info(
                "Expired HOLD bookings processed",
                expired_count=expired_count
            )
        
        return expired_count
    
    async def _schedule_hold_expiry_check(self, booking_id: UUID, expires_at: datetime) -> None:
        """Планирование проверки истечения холда."""
        logger.info("Scheduling hold expiry check", booking_id=booking_id, expires_at=expires_at)
    
    async def _create_audit_log(
        self,
        actor_id: UUID,
        action: str,
        entity: str,
        entity_id: UUID,
        meta: dict = None
    ) -> None:
        """Создание записи аудита."""
        audit_log = AuditLog.create_log(
            actor_id=actor_id,
            action=action,
            entity=entity,
            entity_id=entity_id,
            meta=meta or {}
        )
        
        self.db.add(audit_log)


class BookingModerationService:
    """Сервис для модерации бронирований администраторами."""
    
    def __init__(self, db_session: AsyncSession):
        self.db = db_session
    
    async def get_moderation_queue(self) -> BookingModerationQueue:
        """Получение очереди модерации."""
        # Бронирования, ожидающие подтверждения оплаты
        awaiting_query = select(Booking).options(
            selectinload(Booking.student),
            selectinload(Booking.mentor).selectinload(Mentor.user)
        ).where(
            Booking.status == BookingStatus.AWAITING_VERIFICATION
        ).order_by(Booking.created_at)
        
        awaiting_result = await self.db.execute(awaiting_query)
        awaiting_bookings = awaiting_result.scalars().all()
        
        # Недавние платежи (за последние 24 часа)
        recent_cutoff = datetime.now(timezone.utc) - timedelta(hours=24)
        recent_query = select(Booking).options(
            selectinload(Booking.student),
            selectinload(Booking.mentor).selectinload(Mentor.user)
        ).where(
            and_(
                Booking.status == BookingStatus.CONFIRMED,
                Booking.updated_at >= recent_cutoff
            )
        ).order_by(desc(Booking.updated_at))
        
        recent_result = await self.db.execute(recent_query)
        recent_bookings = recent_result.scalars().all()
        
        # Предстоящие сессии (на ближайшие 3 дня)
        upcoming_cutoff = datetime.now(timezone.utc) + timedelta(days=3)
        upcoming_query = select(Booking).options(
            selectinload(Booking.student),
            selectinload(Booking.mentor).selectinload(Mentor.user)
        ).where(
            and_(
                Booking.status == BookingStatus.CONFIRMED,
                Booking.starts_at <= upcoming_cutoff,
                Booking.starts_at >= datetime.now(timezone.utc)
            )
        ).order_by(Booking.starts_at)
        
        upcoming_result = await self.db.execute(upcoming_query)
        upcoming_bookings = upcoming_result.scalars().all()
        
        # Преобразуем в ответы
        booking_service = BookingService(self.db)
        
        awaiting_responses = []
        for booking in awaiting_bookings:
            response = await booking_service._build_booking_response(booking)
            awaiting_responses.append(response)
        
        recent_responses = []
        for booking in recent_bookings:
            response = await booking_service._build_booking_response(booking)
            recent_responses.append(response)
        
        upcoming_responses = []
        for booking in upcoming_bookings:
            response = await booking_service._build_booking_response(booking)
            upcoming_responses.append(response)
        
        # Определяем бронирования, требующие внимания
        attention_bookings = []
        now = datetime.now(timezone.utc)
        
        # 1. HOLD дольше 20 минут
        hold_threshold = now - timedelta(minutes=20)
        hold_query = select(Booking).where(
            and_(
                Booking.status == BookingStatus.HOLD,
                Booking.created_at < hold_threshold
            )
        ).limit(10)
        
        hold_result = await self.db.execute(hold_query)
        hold_bookings = hold_result.scalars().all()
        attention_bookings.extend(hold_bookings)
        
        # 2. AWAITING_VERIFICATION дольше 24 часов
        verification_threshold = now - timedelta(hours=24)
        verification_query = select(Booking).where(
            and_(
                Booking.status == BookingStatus.AWAITING_VERIFICATION,
                Booking.updated_at < verification_threshold
            )
        ).limit(10)
        
        verification_result = await self.db.execute(verification_query)
        verification_bookings = verification_result.scalars().all()
        attention_bookings.extend(verification_bookings)
        
        # 3. Начало меньше чем через 2 часа, но не CONFIRMED
        soon_threshold = now + timedelta(hours=2)
        soon_query = select(Booking).where(
            and_(
                Booking.starts_at <= soon_threshold,
                Booking.starts_at >= now,
                Booking.status != BookingStatus.CONFIRMED,
                Booking.status != BookingStatus.CANCELLED,
                Booking.status != BookingStatus.COMPLETED
            )
        ).limit(10)
        
        soon_result = await self.db.execute(soon_query)
        soon_bookings = soon_result.scalars().all()
        attention_bookings.extend(soon_bookings)
        
        # Убираем дубликаты и преобразуем в BookingConflict
        unique_attention = {booking.id: booking for booking in attention_bookings}.values()
        attention_conflicts = []
        for booking in unique_attention:
            conflict_type = "hold_expired" if booking.status == BookingStatus.HOLD else \
                          "verification_delayed" if booking.status == BookingStatus.AWAITING_VERIFICATION else \
                          "upcoming_unconfirmed"
            
            description = ""
            if booking.status == BookingStatus.HOLD:
                description = f"Бронирование в статусе HOLD более 20 минут (создано {booking.created_at.strftime('%Y-%m-%d %H:%M')})"
            elif booking.status == BookingStatus.AWAITING_VERIFICATION:
                description = f"Ожидает подтверждения оплаты более 24 часов (обновлено {booking.updated_at.strftime('%Y-%m-%d %H:%M')})"
            else:
                description = f"Консультация начинается менее чем через 2 часа, но не подтверждена (начало: {booking.starts_at.strftime('%Y-%m-%d %H:%M')})"
            
            suggested_action = "Проверить оплату и подтвердить или отклонить" if booking.status == BookingStatus.AWAITING_VERIFICATION else \
                             "Проверить статус и принять меры"
            
            from modules.bookings.domain.schemas import BookingConflict
            attention_conflicts.append(BookingConflict(
                booking_id=booking.id,
                conflict_type=conflict_type,
                description=description,
                suggested_action=suggested_action
            ))
        
        return BookingModerationQueue(
            awaiting_payment=awaiting_responses,
            recent_payments=recent_responses,
            upcoming_sessions=upcoming_responses,
            requires_attention=attention_conflicts
        )

