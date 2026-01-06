"""
Сервисы для административного модуля.
"""
import uuid
from datetime import datetime, date, timedelta
from decimal import Decimal
from typing import Any, Dict, List, Optional, Tuple
from uuid import UUID

from sqlalchemy import and_, desc, func, or_, select, text, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from core.config import settings
from core.exceptions import BusinessLogicError, NotFoundError
from core.logging import get_logger
from core.security import get_password_hash
from modules.admin.domain.models import AuditLog
from modules.admin.domain.schemas import (
    AdminActionLog,
    AdminDashboardStats,
    AdminNotification,
    AuditLogEntry,
    AuditLogFilters,
    AuditLogList,
    BulkOperationResult,
    BookingModerationAction,
    CreateMentorRequest,
    CreateMentorResponse,
    ExportJob,
    ExportRequest,
    FeatureFlag,
    FeatureFlagUpdate,
    MentorModerationAction,
    ModerationQueue,
    PlatformAnalytics,
    SystemHealth,
    SystemMetrics,
    SystemSettings,
    UserManagementAction,
    UserManagementFilters,
)
from modules.bookings.domain.models import Booking, BookingStatus
from modules.mentors.domain.models import Mentor
from modules.users.domain.models import User, UserRole

logger = get_logger(__name__)


class AdminDashboardService:
    """Сервис для административного дашборда."""
    
    def __init__(self, db_session: AsyncSession):
        self.db = db_session
    
    async def get_dashboard_stats(self) -> AdminDashboardStats:
        """Получение статистики для дашборда."""
        logger.info("Generating admin dashboard stats")
        
        try:
            # Параллельно собираем статистику
            stats = {}
            
            # Пользователи
            total_users_query = select(func.count(User.id))
            total_users_result = await self.db.execute(total_users_query)
            stats['total_users'] = total_users_result.scalar() or 0
            
            students_query = select(func.count(User.id)).where(User.role == UserRole.STUDENT)
            students_result = await self.db.execute(students_query)
            stats['total_students'] = students_result.scalar() or 0
            
            mentors_query = select(func.count(User.id)).where(User.role == UserRole.MENTOR)
            mentors_result = await self.db.execute(mentors_query)
            stats['total_mentors'] = mentors_result.scalar() or 0
            
            active_users_query = select(func.count(User.id)).where(User.is_active == True)
            active_users_result = await self.db.execute(active_users_query)
            stats['active_users'] = active_users_result.scalar() or 0
            
            # Бронирования
            total_bookings_query = select(func.count(Booking.id))
            total_bookings_result = await self.db.execute(total_bookings_query)
            stats['total_bookings'] = total_bookings_result.scalar() or 0
            
            pending_bookings_query = select(func.count(Booking.id)).where(
                Booking.status == BookingStatus.AWAITING_VERIFICATION
            )
            pending_result = await self.db.execute(pending_bookings_query)
            stats['pending_bookings'] = pending_result.scalar() or 0
            
            completed_bookings_query = select(func.count(Booking.id)).where(
                Booking.status == BookingStatus.COMPLETED
            )
            completed_result = await self.db.execute(completed_bookings_query)
            stats['completed_bookings'] = completed_result.scalar() or 0
            
            # Финансы (используем Booking.price, только CONFIRMED и COMPLETED)
            revenue_query = select(func.coalesce(func.sum(Booking.price), 0)).where(
                Booking.status.in_([BookingStatus.CONFIRMED, BookingStatus.COMPLETED])
            )
            revenue_result = await self.db.execute(revenue_query)
            revenue_value = revenue_result.scalar()
            stats['total_revenue'] = Decimal(str(revenue_value)) if revenue_value is not None else Decimal('0')
            
            pending_revenue_query = select(func.coalesce(func.sum(Booking.price), 0)).where(
                Booking.status == BookingStatus.AWAITING_VERIFICATION
            )
            pending_revenue_result = await self.db.execute(pending_revenue_query)
            pending_revenue_value = pending_revenue_result.scalar()
            stats['pending_revenue'] = Decimal(str(pending_revenue_value)) if pending_revenue_value is not None else Decimal('0')
            
            # Месячная выручка
            month_start = datetime.utcnow().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            monthly_revenue_query = select(func.coalesce(func.sum(Booking.price), 0)).where(
                and_(
                    Booking.status.in_([BookingStatus.CONFIRMED, BookingStatus.COMPLETED]),
                    Booking.created_at >= month_start
                )
            )
            monthly_revenue_result = await self.db.execute(monthly_revenue_query)
            monthly_revenue_value = monthly_revenue_result.scalar()
            stats['monthly_revenue'] = Decimal(str(monthly_revenue_value)) if monthly_revenue_value is not None else Decimal('0')
            
            # За сегодня
            today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
            
            new_users_today_query = select(func.count(User.id)).where(User.created_at >= today_start)
            new_users_today_result = await self.db.execute(new_users_today_query)
            stats['new_users_today'] = new_users_today_result.scalar() or 0
            
            new_bookings_today_query = select(func.count(Booking.id)).where(Booking.created_at >= today_start)
            new_bookings_today_result = await self.db.execute(new_bookings_today_query)
            stats['new_bookings_today'] = new_bookings_today_result.scalar() or 0
            
            # Верификация менторов больше не используется
            stats['mentor_verifications_pending'] = 0
            
            # Конверсия
            booking_conversion = (stats['completed_bookings'] / max(stats['total_bookings'], 1)) * 100
            payment_confirmation = (stats['total_bookings'] - stats['pending_bookings']) / max(stats['total_bookings'], 1) * 100
            
            logger.info(
                "Dashboard stats generated",
                total_users=stats['total_users'],
                total_bookings=stats['total_bookings'],
                total_revenue=float(stats['total_revenue']),
                total_mentors=stats['total_mentors']
            )
            
            return AdminDashboardStats(
                total_users=stats['total_users'],
                total_students=stats['total_students'],
                total_mentors=stats['total_mentors'],
                active_users=stats['active_users'],
                total_bookings=stats['total_bookings'],
                pending_bookings=stats['pending_bookings'],
                completed_bookings=stats['completed_bookings'],
                total_revenue=stats['total_revenue'],
                pending_revenue=stats['pending_revenue'],
                monthly_revenue=stats['monthly_revenue'],
                new_users_today=stats['new_users_today'],
                new_bookings_today=stats['new_bookings_today'],
                mentor_verifications_pending=stats['mentor_verifications_pending'],
                booking_conversion_rate=round(booking_conversion, 2),
                payment_confirmation_rate=round(payment_confirmation, 2)
            )
        except Exception as e:
            logger.error("Error generating dashboard stats", error=str(e), exc_info=True)
            # Возвращаем пустую статистику вместо падения
            return AdminDashboardStats(
                total_users=0,
                total_students=0,
                total_mentors=0,
                active_users=0,
                total_bookings=0,
                pending_bookings=0,
                completed_bookings=0,
                total_revenue=Decimal('0'),
                pending_revenue=Decimal('0'),
                monthly_revenue=Decimal('0'),
                new_users_today=0,
                new_bookings_today=0,
                mentor_verifications_pending=0,
                booking_conversion_rate=0.0,
                payment_confirmation_rate=0.0
            )
    
    async def get_platform_analytics(self, period: str = "7d") -> PlatformAnalytics:
        """Получение аналитики платформы."""
        logger.info("Generating platform analytics", period=period)
        
        try:
            # Определяем период
            end_date = datetime.utcnow()
            if period == "7d":
                start_date = end_date - timedelta(days=7)
            elif period == "30d":
                start_date = end_date - timedelta(days=30)
            elif period == "90d":
                start_date = end_date - timedelta(days=90)
            else:
                start_date = end_date - timedelta(days=7)
            
            # Рост пользователей
            user_growth = await self._get_user_growth_data(start_date, end_date)
            
            # Распределение пользователей по ролям
            user_distribution = await self._get_user_distribution()
            
            # Топ страны
            top_countries = await self._get_top_countries()
            
            # Тренды бронирований
            booking_trends = await self._get_booking_trends(start_date, end_date)
            
            # Распределение статусов бронирований
            booking_status_distribution = await self._get_booking_status_distribution()
            
            # Популярные длительности
            popular_duration = await self._get_popular_durations()
            
            # Топ менторы
            top_mentors = await self._get_top_mentors()
            
            # Предметы менторов
            mentor_subjects = await self._get_mentor_subjects()
            
            # Распределение рейтингов
            mentor_rating_distribution = await self._get_mentor_rating_distribution()
            
            # Тренды выручки
            revenue_trends = await self._get_revenue_trends(start_date, end_date)
            
            # Средняя стоимость сессии (только для CONFIRMED и COMPLETED)
            avg_price_query = select(func.coalesce(func.avg(Booking.price), 0)).where(
                Booking.status.in_([BookingStatus.CONFIRMED, BookingStatus.COMPLETED])
            )
            avg_price_result = await self.db.execute(avg_price_query)
            avg_price_value = avg_price_result.scalar()
            average_session_price = Decimal(str(avg_price_value)) if avg_price_value is not None else Decimal('0')
            
            logger.info(
                "Platform analytics generated",
                period=period,
                user_growth_count=len(user_growth),
                booking_trends_count=len(booking_trends),
                revenue_trends_count=len(revenue_trends),
                average_session_price=float(average_session_price)
            )
            
            return PlatformAnalytics(
                period=period,
                user_growth=user_growth,
                user_distribution=user_distribution,
                top_countries=top_countries,
                booking_trends=booking_trends,
                booking_status_distribution=booking_status_distribution,
                popular_duration=popular_duration,
                top_mentors=top_mentors,
                mentor_subjects=mentor_subjects,
                mentor_rating_distribution=mentor_rating_distribution,
                revenue_trends=revenue_trends,
                average_session_price=average_session_price
            )
        except Exception as e:
            logger.error("Error in get_platform_analytics", error=str(e), exc_info=True)
            # Возвращаем пустую аналитику вместо падения
            return PlatformAnalytics(
                period=period,
                user_growth=[],
                user_distribution={},
                top_countries=[],
                booking_trends=[],
                booking_status_distribution={},
                popular_duration=[],
                top_mentors=[],
                mentor_subjects=[],
                mentor_rating_distribution=[],
                revenue_trends=[],
                average_session_price=Decimal('0')
            )
    
    async def get_moderation_queue(self) -> ModerationQueue:
        """Получение очереди модерации."""
        # Верификация менторов больше не используется
        pending_mentors = []
        
        # Платежи на подтверждение
        pending_payments_query = select(Booking, User).join(
            User, Booking.student_id == User.id
        ).where(
            Booking.status == BookingStatus.AWAITING_VERIFICATION
        ).order_by(Booking.created_at).limit(50)
        
        pending_payments_result = await self.db.execute(pending_payments_query)
        pending_payments = []
        for booking, user in pending_payments_result:
            pending_payments.append({
                "id": booking.id,
                "student_name": user.name or user.email,
                "student_email": user.email,
                "amount": float(booking.price or 0),
                "created_at": booking.created_at.isoformat()
            })
        
        # TODO: Открытые тикеты поддержки
        open_support_tickets = []
        
        # TODO: Проблемы требующие внимания
        issues_requiring_attention = []
        
        return ModerationQueue(
            pending_mentor_verifications=pending_mentors,
            pending_payments=pending_payments,
            open_support_tickets=open_support_tickets,
            issues_requiring_attention=issues_requiring_attention
        )
    
    async def _get_user_growth_data(self, start_date: datetime, end_date: datetime) -> List[Dict[str, Any]]:
        """Получение данных роста пользователей."""
        try:
            # Группируем по дням
            query = text("""
                SELECT DATE(created_at) as date, COUNT(*) as count
                FROM users 
                WHERE created_at >= :start_date AND created_at <= :end_date
                GROUP BY DATE(created_at)
                ORDER BY DATE(created_at)
            """)
            
            result = await self.db.execute(query, {"start_date": start_date, "end_date": end_date})
            
            growth_data: List[Dict[str, Any]] = []
            for row in result:
                # row.date может быть date/datetime или уже строкой
                raw_date = getattr(row, "date", None)
                if isinstance(raw_date, (date, datetime)):
                    date_str = raw_date.isoformat()
                else:
                    date_str = str(raw_date) if raw_date is not None else ""

                growth_data.append({
                    "date": date_str,
                    "count": getattr(row, "count", 0) or 0,
                })

            return growth_data
        except Exception as e:
            logger.error("Error in _get_user_growth_data", error=str(e), exc_info=True)
            return []
    
    async def _get_user_distribution(self) -> Dict[str, int]:
        """Распределение пользователей по ролям."""
        try:
            query = select(User.role, func.count(User.id)).group_by(User.role)
            result = await self.db.execute(query)

            distribution: Dict[str, int] = {}
            for role, count in result:
                # role может быть Enum (UserRole) или уже строкой из БД
                role_value = role.value if hasattr(role, "value") else role
                distribution[str(role_value)] = count or 0

            return distribution
        except Exception as e:
            logger.error("Error in _get_user_distribution", error=str(e), exc_info=True)
            return {}
    
    async def _get_top_countries(self) -> List[Dict[str, Any]]:
        """Топ стран пользователей."""
        # TODO: Реализовать когда будет поле country в профилях
        return []
    
    async def _get_booking_trends(self, start_date: datetime, end_date: datetime) -> List[Dict[str, Any]]:
        """Тренды бронирований."""
        try:
            query = text("""
                SELECT DATE(created_at) as date, COUNT(*) as count
                FROM bookings 
                WHERE created_at >= :start_date AND created_at <= :end_date
                GROUP BY DATE(created_at)
                ORDER BY DATE(created_at)
            """)
            
            result = await self.db.execute(query, {"start_date": start_date, "end_date": end_date})
            
            trends: List[Dict[str, Any]] = []
            for row in result:
                raw_date = getattr(row, "date", None)
                if isinstance(raw_date, (date, datetime)):
                    date_str = raw_date.isoformat()
                else:
                    date_str = str(raw_date) if raw_date is not None else ""

                trends.append({
                    "date": date_str,
                    "count": getattr(row, "count", 0) or 0,
                })

            return trends
        except Exception as e:
            logger.error("Error in _get_booking_trends", error=str(e), exc_info=True)
            return []
    
    async def _get_booking_status_distribution(self) -> Dict[str, int]:
        """Распределение бронирований по статусам."""
        try:
            query = select(Booking.status, func.count(Booking.id)).group_by(Booking.status)
            result = await self.db.execute(query)

            distribution: Dict[str, int] = {}
            for status, count in result:
                # status может быть Enum (BookingStatus) или строкой
                status_value = status.value if hasattr(status, "value") else status
                distribution[str(status_value)] = count or 0

            return distribution
        except Exception as e:
            logger.error("Error in _get_booking_status_distribution", error=str(e), exc_info=True)
            return {}
    
    async def _get_popular_durations(self) -> List[Dict[str, Any]]:
        """Популярные длительности сессий."""
        try:
            query = select(
                Booking.duration_minutes, 
                func.count(Booking.id).label('count')
            ).group_by(Booking.duration_minutes).order_by(desc('count'))
            
            result = await self.db.execute(query)
            
            durations = []
            for duration, count in result:
                durations.append({
                    "duration": duration or 0,
                    "count": count or 0
                })
            
            return durations
        except Exception as e:
            logger.error("Error in _get_popular_durations", error=str(e), exc_info=True)
            return []
    
    async def _get_top_mentors(self) -> List[Dict[str, Any]]:
        """Топ менторы по количеству бронирований."""
        try:
            query = select(
                Booking.mentor_id,
                func.count(Booking.id).label('bookings_count'),
                User.name,
                User.email
            ).join(User, Booking.mentor_id == User.id).where(
                Booking.status.in_([BookingStatus.CONFIRMED, BookingStatus.COMPLETED])
            ).group_by(
                Booking.mentor_id, User.name, User.email
            ).order_by(desc('bookings_count')).limit(10)
            
            result = await self.db.execute(query)
            
            top_mentors = []
            for mentor_id, count, name, email in result:
                top_mentors.append({
                    "mentor_id": str(mentor_id),
                    "name": name or email or "Unknown",
                    "email": email or "",
                    "bookings_count": count or 0
                })
            
            return top_mentors
        except Exception as e:
            logger.error("Error in _get_top_mentors", error=str(e), exc_info=True)
            return []
    
    async def _get_mentor_subjects(self) -> List[Dict[str, Any]]:
        """Популярные предметы менторов."""
        # TODO: Реализовать когда будут предметы в профиле ментора
        return []
    
    async def _get_mentor_rating_distribution(self) -> List[Dict[str, Any]]:
        """Распределение рейтингов менторов."""
        # TODO: Реализовать когда будет рейтинг
        return []
    
    async def _get_revenue_trends(self, start_date: datetime, end_date: datetime) -> List[Dict[str, Any]]:
        """Тренды выручки."""
        try:
            # Используем правильное имя колонки 'price' вместо 'price_amount'
            # И правильные значения статусов из enum
            confirmed_status = BookingStatus.CONFIRMED.value
            completed_status = BookingStatus.COMPLETED.value
            
            query = text("""
                SELECT DATE(created_at) as date, COALESCE(SUM(price), 0) as revenue
                FROM bookings 
                WHERE created_at >= :start_date 
                    AND created_at <= :end_date
                    AND status IN (:confirmed_status, :completed_status)
                GROUP BY DATE(created_at)
                ORDER BY DATE(created_at)
            """)
            
            result = await self.db.execute(
                query, 
                {
                    "start_date": start_date, 
                    "end_date": end_date,
                    "confirmed_status": confirmed_status,
                    "completed_status": completed_status
                }
            )
            
            trends: List[Dict[str, Any]] = []
            for row in result:
                # Безопасная обработка даты
                raw_date = getattr(row, "date", None)
                if isinstance(raw_date, (date, datetime)):
                    date_str = raw_date.isoformat()
                else:
                    date_str = str(raw_date) if raw_date is not None else ""
                
                # Безопасная обработка revenue
                revenue_value = getattr(row, "revenue", 0)
                if revenue_value is None:
                    revenue_value = 0
                
                trends.append({
                    "date": date_str,
                    "revenue": float(revenue_value)
                })
            
            return trends
        except Exception as e:
            logger.error("Error in _get_revenue_trends", error=str(e), exc_info=True)
            return []


class UserManagementService:
    """Сервис управления пользователями."""
    
    def __init__(self, db_session: AsyncSession):
        self.db = db_session
    
    async def bulk_user_action(
        self, 
        action_data: UserManagementAction,
        admin_id: UUID
    ) -> BulkOperationResult:
        """Массовое действие над пользователями."""
        logger.info(
            "Executing bulk user action",
            action=action_data.action,
            user_count=len(action_data.user_ids),
            admin_id=admin_id
        )
        
        operation_id = uuid.uuid4()
        started_at = datetime.utcnow()
        successful_items = 0
        errors = []
        affected_ids = []
        
        for user_id in action_data.user_ids:
            try:
                # Получаем пользователя
                user_query = select(User).where(User.id == user_id)
                user_result = await self.db.execute(user_query)
                user = user_result.scalar_one_or_none()
                
                if not user:
                    errors.append(f"Пользователь {user_id} не найден")
                    continue
                
                # Выполняем действие
                old_values = {
                    "is_active": user.is_active,
                    "role": user.role.value if hasattr(user.role, "value") else user.role,
                }
                
                if action_data.action == "activate":
                    user.is_active = True
                elif action_data.action == "deactivate":
                    user.is_active = False
                elif action_data.action == "promote" and action_data.new_role:
                    user.role = action_data.new_role
                elif action_data.action == "demote" and action_data.new_role:
                    user.role = action_data.new_role
                else:
                    errors.append(f"Неизвестное действие: {action_data.action}")
                    continue
                
                new_values = {
                    "is_active": user.is_active,
                    "role": user.role.value if hasattr(user.role, "value") else user.role,
                }
                
                await self.db.commit()
                
                # Логируем действие
                await self._create_admin_action_log(
                    admin_id=admin_id,
                    action_type=action_data.action,
                    target_type="user",
                    target_id=user_id,
                    description=f"{action_data.action} user {user.email}",
                    old_values=old_values,
                    new_values=new_values
                )
                
                successful_items += 1
                affected_ids.append(user_id)
                
                # TODO: Отправить уведомление если нужно
                
            except Exception as e:
                logger.error("Error in bulk user action", user_id=user_id, error=str(e))
                errors.append(f"Ошибка для пользователя {user_id}: {str(e)}")
        
        completed_at = datetime.utcnow()
        
        return BulkOperationResult(
            total_items=len(action_data.user_ids),
            successful_items=successful_items,
            failed_items=len(action_data.user_ids) - successful_items,
            errors=errors,
            affected_ids=affected_ids,
            operation_id=operation_id,
            started_at=started_at,
            completed_at=completed_at
        )
    
    async def create_mentor(
        self,
        mentor_data: CreateMentorRequest,
        admin_id: UUID
    ) -> CreateMentorResponse:
        """Создание ментора администратором."""
        logger.info("Creating mentor by admin", email=mentor_data.email, admin_id=admin_id)
        
        # Проверяем существование пользователя с таким email
        existing_user_query = select(User).where(User.email == mentor_data.email)
        existing_user_result = await self.db.execute(existing_user_query)
        existing_user = existing_user_result.scalar_one_or_none()
        
        if existing_user:
            raise BusinessLogicError(f"Пользователь с email {mentor_data.email} уже существует")
        
        try:
            # Создаем пользователя
            hashed_password = get_password_hash(mentor_data.password)
            user = User(
                email=mentor_data.email,
                password_hash=hashed_password,
                name=mentor_data.name,
                role=UserRole.MENTOR,
                phone=mentor_data.phone,
                is_active=True
            )
            self.db.add(user)
            await self.db.flush()  # Получаем user.id
            
            # Создаем профиль ментора
            mentor_profile = Mentor(
                user_id=user.id,
                headline=mentor_data.headline,
                bio=mentor_data.bio,
                price_30=mentor_data.price_30,
                price_45=mentor_data.price_45,
                price_60=mentor_data.price_60,
                rating_avg=Decimal("0.00"),
                rating_count=0,
                languages=mentor_data.languages or [],
                subjects=[],  # Пустой список subjects
                avatar_url=mentor_data.avatar_url
            )
            self.db.add(mentor_profile)
            await self.db.commit()
            await self.db.refresh(user)
            await self.db.refresh(mentor_profile)
            
            # Логируем действие
            await self._create_admin_action_log(
                admin_id=admin_id,
                action_type="create_mentor",
                target_type="user",
                target_id=user.id,
                description=f"Created mentor {user.email}",
                new_values={
                    "email": user.email,
                    "name": user.name,
                    "role": user.role,  # user.role уже строка, не нужно .value
                    "price_30": float(mentor_data.price_30) if mentor_data.price_30 else None,
                    "price_45": float(mentor_data.price_45) if mentor_data.price_45 else None,
                    "price_60": float(mentor_data.price_60) if mentor_data.price_60 else None
                }
            )
            
            logger.info("Mentor created successfully", user_id=user.id, mentor_id=mentor_profile.id)
            
            # TODO: Отправить приветственное письмо если mentor_data.send_welcome_email
            
            return CreateMentorResponse(
                user_id=user.id,
                mentor_id=mentor_profile.id,
                email=user.email,
                name=user.name,
                message="Ментор успешно создан"
            )
            
        except Exception as e:
            await self.db.rollback()
            logger.error("Error creating mentor", error=str(e), admin_id=admin_id)
            raise BusinessLogicError(f"Ошибка при создании ментора: {str(e)}")
    
    async def _create_admin_action_log(
        self,
        admin_id: UUID,
        action_type: str,
        target_type: str,
        target_id: UUID,
        description: str,
        old_values: Optional[Dict[str, Any]] = None,
        new_values: Optional[Dict[str, Any]] = None
    ) -> None:
        """Создание лога действия администратора."""
        # TODO: Создать таблицу admin_action_log
        logger.info(
            "Admin action logged",
            admin_id=admin_id,
            action_type=action_type,
            target_type=target_type,
            target_id=target_id
        )


class AuditLogService:
    """Сервис для работы с аудит логом."""
    
    def __init__(self, db_session: AsyncSession):
        self.db = db_session
    
    async def get_audit_log(
        self,
        page: int = 1,
        page_size: int = 50,
        filters: Optional[AuditLogFilters] = None
    ) -> AuditLogList:
        """Получение записей аудит лога."""
        query = select(AuditLog, User).join(User, AuditLog.actor_id == User.id)
        count_query = select(func.count(AuditLog.id))
        
        conditions = []
        
        if filters:
            if filters.actor_id:
                conditions.append(AuditLog.actor_id == filters.actor_id)
            
            if filters.action:
                conditions.append(AuditLog.action.ilike(f"%{filters.action}%"))
            
            if filters.entity:
                conditions.append(AuditLog.entity == filters.entity)
            
            if filters.date_from:
                conditions.append(AuditLog.created_at >= filters.date_from)
            
            if filters.date_to:
                conditions.append(AuditLog.created_at <= filters.date_to)
        
        if conditions:
            query = query.where(and_(*conditions))
            count_query = count_query.where(and_(*conditions))
        
        # Подсчет общего количества
        total_result = await self.db.execute(count_query)
        total = total_result.scalar()
        
        # Пагинация и сортировка
        offset = (page - 1) * page_size
        query = query.order_by(desc(AuditLog.created_at)).offset(offset).limit(page_size)
        
        result = await self.db.execute(query)
        
        entries = []
        for audit_log, user in result:
            entries.append(AuditLogEntry(
                id=audit_log.id,
                actor_id=audit_log.actor_id,
                actor_email=user.email,
                action=audit_log.action,
                entity=audit_log.entity,
                entity_id=audit_log.entity_id,
                meta=audit_log.meta,
                ip_address=audit_log.ip_address,
                user_agent=audit_log.user_agent,
                created_at=audit_log.created_at
            ))
        
        return AuditLogList(
            entries=entries,
            total=total,
            page=page,
            page_size=page_size
        )


class SystemManagementService:
    """Сервис управления системой."""
    
    def __init__(self, db_session: AsyncSession):
        self.db = db_session
    
    async def get_system_health(self) -> SystemHealth:
        """Получение состояния системы."""
        # Проверяем базу данных
        try:
            await self.db.execute(text("SELECT 1"))
            database_status = "healthy"
        except Exception:
            database_status = "down"
        
        # TODO: Проверить email сервис, файловое хранилище
        
        return SystemHealth(
            status="healthy" if database_status == "healthy" else "degraded",
            database_status=database_status,
            email_service_status="healthy",  # TODO: Реальная проверка
            storage_status="healthy",  # TODO: Реальная проверка
            active_connections=0,  # TODO: Получить из pool
            memory_usage_percent=0.0,  # TODO: psutil
            disk_usage_percent=0.0,  # TODO: psutil
            api_version=settings.APP_VERSION,
            database_version="PostgreSQL 15",  # TODO: Получить версию
            last_check=datetime.utcnow()
        )
    
    async def get_system_metrics(self) -> SystemMetrics:
        """Получение системных метрик."""
        # TODO: Реализовать сбор метрик
        return SystemMetrics(
            timestamp=datetime.utcnow(),
            requests_per_minute=0,
            average_response_time=0.0,
            error_rate_percent=0.0,
            db_connections_active=0,
            db_query_avg_time=0.0,
            online_users=0,
            active_sessions=0,
            bookings_per_hour=0,
            revenue_per_hour=Decimal('0')
        )
