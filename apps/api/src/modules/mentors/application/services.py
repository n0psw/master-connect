"""
Сервисы для модуля менторов.
"""
from datetime import datetime
from decimal import Decimal
from typing import List, Optional, Tuple
from uuid import UUID

from sqlalchemy import and_, desc, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from core.exceptions import BusinessLogicError, NotFoundError, PermissionDeniedError
from core.logging import get_logger
from modules.admin.domain.models import AuditLog
from modules.mentors.domain.models import Mentor, MentorUniversity
from modules.mentors.domain.schemas import (
    AdminMentorDetail,
    AdminMentorUpdate,
    MentorCard,
    MentorCreate,
    MentorDetail,
    MentorFilters,
    MentorResponse,
    MentorSortOptions,
    MentorStats,
    MentorUniversityCreate,
    MentorUniversityResponse,
    MentorUniversityUpdate,
    MentorUpdate,
    PopularLanguages,
    PopularSubjects,
    UniversitySuggestion,
)
from modules.users.domain.models import User, UserRole

logger = get_logger(__name__)


class MentorService:
    """Сервис для управления менторами."""
    
    def __init__(self, db_session: AsyncSession):
        self.db = db_session
    
    async def get_mentors_catalog(
        self,
        page: int = 1,
        page_size: int = 20,
        filters: Optional[MentorFilters] = None,
        sort: MentorSortOptions = MentorSortOptions.RATING_DESC,
        search_query: Optional[str] = None
    ) -> Tuple[List[MentorCard], int]:
        """Получение каталога менторов с фильтрацией и сортировкой."""
        query = select(Mentor).join(User).where(User.is_active == True)
        count_query = select(func.count(Mentor.user_id)).join(User).where(User.is_active == True)
        
        # Загружаем связанные данные
        query = query.options(
            selectinload(Mentor.user),
            selectinload(Mentor.universities)
        )
        
        # Применяем фильтры
        conditions = []
        
        if filters:
            if filters.languages:
                conditions.append(Mentor.languages.op("&&")(filters.languages))
            
            if filters.subjects:
                conditions.append(Mentor.subjects.op("&&")(filters.subjects))
            
            if filters.countries:
                # Фильтр по странам через университеты
                country_condition = select(MentorUniversity.mentor_id).where(
                    MentorUniversity.country.in_(filters.countries)
                ).scalar_subquery()
                conditions.append(Mentor.user_id.in_(country_condition))
            
            if filters.price_min is not None:
                # Проверяем любую из цен
                price_conditions = []
                if filters.price_min > 0:
                    price_conditions.extend([
                        Mentor.price_30 >= filters.price_min,
                        Mentor.price_45 >= filters.price_min,
                        Mentor.price_60 >= filters.price_min
                    ])
                if price_conditions:
                    conditions.append(or_(*price_conditions))
            
            if filters.price_max is not None:
                # Проверяем любую из цен
                price_conditions = []
                if filters.price_max > 0:
                    price_conditions.extend([
                        Mentor.price_30 <= filters.price_max,
                        Mentor.price_45 <= filters.price_max,
                        Mentor.price_60 <= filters.price_max
                    ])
                if price_conditions:
                    conditions.append(or_(*price_conditions))
            
            if filters.rating_min is not None:
                conditions.append(Mentor.rating_avg >= filters.rating_min)
            
        
        # Поиск по тексту
        if search_query:
            search_pattern = f"%{search_query.lower()}%"
            text_conditions = [
                func.lower(User.name).like(search_pattern),
                func.lower(Mentor.headline).like(search_pattern),
                func.lower(Mentor.bio).like(search_pattern)
            ]
            conditions.append(or_(*text_conditions))
        
        if conditions:
            query = query.where(and_(*conditions))
            count_query = count_query.where(and_(*conditions))
        
        # Подсчет общего количества
        total_result = await self.db.execute(count_query)
        total = total_result.scalar()
        
        # Сортировка
        if sort == MentorSortOptions.RATING_DESC:
            query = query.order_by(desc(Mentor.rating_avg), desc(Mentor.rating_count))
        elif sort == MentorSortOptions.RATING_ASC:
            query = query.order_by(Mentor.rating_avg, Mentor.rating_count)
        elif sort == MentorSortOptions.PRICE_ASC:
            query = query.order_by(Mentor.price_60.nulls_last(), Mentor.price_30.nulls_last())
        elif sort == MentorSortOptions.PRICE_DESC:
            query = query.order_by(desc(Mentor.price_60), desc(Mentor.price_30))
        elif sort == MentorSortOptions.REVIEWS_COUNT_DESC:
            query = query.order_by(desc(Mentor.rating_count))
        elif sort == MentorSortOptions.CREATED_ASC:
            query = query.order_by(Mentor.created_at)
        elif sort == MentorSortOptions.CREATED_DESC:
            query = query.order_by(desc(Mentor.created_at))
        
        # Пагинация
        offset = (page - 1) * page_size
        query = query.offset(offset).limit(page_size)
        
        # Выполнение запроса
        result = await self.db.execute(query)
        mentors = result.scalars().all()
        
        # Формирование карточек менторов
        mentor_cards = []
        for mentor in mentors:
            universities = [uni.university for uni in mentor.universities]
            country = mentor.universities[0].country if mentor.universities else None
            city = mentor.universities[0].city if mentor.universities else None
            
            mentor_cards.append(MentorCard(
                id=mentor.user_id,
                user_id=mentor.user_id,
                name=mentor.user.name or mentor.user.email,
                headline=mentor.headline,
                avatar_url=mentor.avatar_url,
                languages=mentor.languages,
                subjects=mentor.subjects,
                universities=universities,
                price_30=mentor.price_30,
                price_60=mentor.price_60,
                rating_avg=mentor.rating_avg,
                rating_count=mentor.rating_count,
                country=country,
                city=city
            ))
        
        logger.info(
            "Mentors catalog retrieved",
            total=total,
            page=page,
            page_size=page_size,
            sort=sort,
            has_filters=filters is not None,
            search_query=search_query
        )
        
        return mentor_cards, total
    
    async def get_mentor_detail(self, mentor_id: UUID) -> Optional[MentorDetail]:
        """Получение детальной информации о менторе."""
        query = (
            select(Mentor)
            .options(
                selectinload(Mentor.user),
                selectinload(Mentor.universities)
            )
            .where(Mentor.user_id == mentor_id)
        )
        
        result = await self.db.execute(query)
        mentor = result.scalar_one_or_none()
        
        if not mentor or not mentor.user.is_active:
            return None
        
        # Статистика консультаций (пока заглушка)
        total_consultations = 0
        completed_consultations = 0
        
        from modules.users.domain.schemas import UserResponse
        
        return MentorDetail(
            mentor=MentorResponse.model_validate(mentor),
            user=UserResponse.model_validate(mentor.user),
            universities=[MentorUniversityResponse.model_validate(uni) for uni in mentor.universities],
            reviews_count=mentor.rating_count,
            total_consultations=total_consultations,
            completed_consultations=completed_consultations
        )
    
    async def create_mentor_profile(
        self,
        user_id: UUID,
        mentor_data: MentorCreate,
        created_by: Optional[UUID] = None
    ) -> MentorResponse:
        """Создание профиля ментора."""
        # Проверяем, что пользователь существует и имеет роль mentor
        user_query = select(User).where(User.id == user_id)
        user_result = await self.db.execute(user_query)
        user = user_result.scalar_one_or_none()
        
        if not user:
            raise NotFoundError("User", str(user_id))
        
        if user.role != UserRole.MENTOR:
            raise BusinessLogicError("Пользователь должен иметь роль 'mentor'")
        
        # Проверяем, не существует ли уже профиль
        existing_query = select(Mentor).where(Mentor.user_id == user_id)
        existing_result = await self.db.execute(existing_query)
        existing_mentor = existing_result.scalar_one_or_none()
        
        if existing_mentor:
            raise BusinessLogicError("Профиль ментора уже существует")
        
        # Создаем профиль ментора
        mentor = Mentor(
            user_id=user_id,
            headline=mentor_data.headline,
            bio=mentor_data.bio,
            price_30=mentor_data.price_30,
            price_45=mentor_data.price_45,
            price_60=mentor_data.price_60,
            languages=mentor_data.languages,
            subjects=mentor_data.subjects,
            avatar_url=mentor_data.avatar_url,
        )
        
        self.db.add(mentor)
        await self.db.commit()
        
        # Логируем аудит
        if created_by:
            await self._create_audit_log(
                actor_id=created_by,
                action="CREATE_MENTOR_PROFILE",
                entity="mentor",
                entity_id=user_id
            )
        
        logger.info(
            "Mentor profile created",
            mentor_id=user_id,
            created_by=created_by
        )
        
        return MentorResponse.model_validate(mentor)
    
    async def update_mentor_profile(
        self,
        mentor_id: UUID,
        mentor_data: MentorUpdate,
        updated_by: Optional[UUID] = None
    ) -> MentorResponse:
        """Обновление профиля ментора."""
        mentor = await self._get_mentor_or_404(mentor_id)
        
        # Обновляем поля
        update_data = mentor_data.dict(exclude_unset=True)
        
        for field, value in update_data.items():
            setattr(mentor, field, value)
        
        mentor.updated_at = datetime.utcnow()
        
        await self.db.commit()
        
        # Логируем аудит
        if updated_by:
            await self._create_audit_log(
                actor_id=updated_by,
                action="UPDATE_MENTOR_PROFILE",
                entity="mentor",
                entity_id=mentor_id,
                meta=update_data
            )
        
        logger.info(
            "Mentor profile updated",
            mentor_id=mentor_id,
            updated_fields=list(update_data.keys()),
            updated_by=updated_by
        )
        
        return MentorResponse.model_validate(mentor)
    
    
    async def get_mentor_stats(self) -> MentorStats:
        """Получение статистики менторов."""
        # Общая статистика
        total_mentors_query = select(func.count(Mentor.user_id))
        active_mentors_query = (
            select(func.count(Mentor.user_id))
            .join(User)
            .where(User.is_active == True)
        )
        
        # Средний рейтинг
        avg_rating_query = select(func.avg(Mentor.rating_avg)).where(
            Mentor.rating_count > 0
        )
        
        # Выполняем запросы
        total_mentors_result = await self.db.execute(total_mentors_query)
        active_mentors_result = await self.db.execute(active_mentors_query)
        avg_rating_result = await self.db.execute(avg_rating_query)
        
        return MentorStats(
            total_mentors=total_mentors_result.scalar() or 0,
            active_mentors=active_mentors_result.scalar() or 0,
            average_rating=avg_rating_result.scalar(),
            total_consultations=0  # TODO: Подсчитать из bookings
        )
    
    # === АДМИНСКИЕ МЕТОДЫ ===
    
    async def create_mentor_as_admin(
        self,
        mentor_data: "AdminMentorCreate",
        created_by: UUID
    ) -> "AdminMentorDetail":
        """Создание ментора администратором."""
        from modules.users.application.services import UserService
        from modules.users.domain.schemas import UserCreate
        
        # Создаем пользователя
        user_service = UserService(self.db)
        user_create_data = UserCreate(
            email=mentor_data.email,
            name=mentor_data.name,
            password=mentor_data.password,
            phone=mentor_data.phone,
            timezone=mentor_data.timezone,
            locale=mentor_data.locale,
            role=UserRole.MENTOR
        )
        
        user = await user_service.create_user(user_create_data)
        
        # Создаем профиль ментора
        mentor_create_data = MentorCreate(
            headline=mentor_data.headline,
            bio=mentor_data.bio,
            price_30=mentor_data.price_30,
            price_45=mentor_data.price_45,
            price_60=mentor_data.price_60,
            languages=mentor_data.languages,
            subjects=mentor_data.subjects,
            avatar_url=mentor_data.avatar_url
        )
        
        mentor = await self.create_mentor_profile(
            user_id=user.id,
            mentor_data=mentor_create_data,
            created_by=created_by
        )
        
        # Получаем детальную информацию
        return await self.get_admin_mentor_detail(user.id)
    
    async def update_mentor_as_admin(
        self,
        mentor_id: UUID,
        mentor_data: "AdminMentorUpdate",
        updated_by: UUID
    ) -> "AdminMentorDetail":
        """Обновление ментора администратором."""
        from modules.users.application.services import UserService
        
        # Обновляем пользователя
        user_service = UserService(self.db)
        user_update_data = {}
        if mentor_data.name is not None:
            user_update_data["name"] = mentor_data.name
        if mentor_data.phone is not None:
            user_update_data["phone"] = mentor_data.phone
        if mentor_data.timezone is not None:
            user_update_data["timezone"] = mentor_data.timezone
        if mentor_data.locale is not None:
            user_update_data["locale"] = mentor_data.locale
        if mentor_data.is_active is not None:
            user_update_data["is_active"] = mentor_data.is_active
        
        if user_update_data:
            from modules.users.domain.schemas import UserUpdate
            user_update_obj = UserUpdate(**user_update_data)
            await user_service.update_user(mentor_id, user_update_obj, updated_by)
        
        # Обновляем профиль ментора
        mentor_update_data = MentorUpdate(
            headline=mentor_data.headline,
            bio=mentor_data.bio,
            price_30=mentor_data.price_30,
            price_45=mentor_data.price_45,
            price_60=mentor_data.price_60,
            languages=mentor_data.languages,
            subjects=mentor_data.subjects,
            avatar_url=mentor_data.avatar_url
        )
        
        await self.update_mentor_profile(
            mentor_id=mentor_id,
            mentor_data=mentor_update_data,
            updated_by=updated_by
        )
        
        # Получаем обновленную информацию
        return await self.get_admin_mentor_detail(mentor_id)
    
    async def delete_mentor_as_admin(
        self,
        mentor_id: UUID,
        deleted_by: UUID
    ) -> bool:
        """Удаление ментора администратором."""
        from modules.users.application.services import UserService
        from modules.bookings.domain.models import Booking, BookingStatus
        
        # Проверяем, что ментор существует
        mentor = await self._get_mentor_or_404(mentor_id)
        
        # Проверяем наличие активных бронирований
        active_bookings_query = (
            select(Booking)
            .where(
                Booking.mentor_id == mentor_id,
                Booking.status.in_([
                    BookingStatus.CONFIRMED,
                    BookingStatus.AWAITING_VERIFICATION,
                    BookingStatus.HOLD
                ])
            )
        )
        result = await self.db.execute(active_bookings_query)
        active_bookings = result.scalars().all()
        
        if active_bookings:
            # Если есть активные бронирования, отменяем их
            for booking in active_bookings:
                booking.status = BookingStatus.CANCELLED
                booking.notes = "Ментор удален администратором"
                booking.updated_at = datetime.utcnow()
        
        # Удаляем профиль ментора
        await self.db.delete(mentor)
        
        # Деактивируем пользователя вместо удаления
        user_service = UserService(self.db)
        await user_service.activate_deactivate_user(mentor_id, is_active=False, admin_id=deleted_by)
        
        await self.db.commit()
        
        # Логируем аудит
        await self._create_audit_log(
            actor_id=deleted_by,
            action="DELETE_MENTOR",
            entity="mentor",
            entity_id=mentor_id,
            meta={"deleted_by_admin": True}
        )
        
        logger.info(
            "Mentor deleted by admin",
            mentor_id=mentor_id,
            deleted_by=deleted_by
        )
        
        return True
    
    async def get_admin_mentor_detail(self, mentor_id: UUID) -> "AdminMentorDetail":
        """Получение детальной информации о менторе для администратора."""
        # Оптимизированный запрос с eager loading
        query = (
            select(Mentor)
            .options(
                selectinload(Mentor.user),
                selectinload(Mentor.universities)
            )
            .where(Mentor.user_id == mentor_id)
        )
        
        result = await self.db.execute(query)
        mentor = result.scalar_one_or_none()
        
        if not mentor:
            raise NotFoundError("Mentor", str(mentor_id))
        
        # Статистика консультаций (пока заглушка)
        total_consultations = 0
        completed_consultations = 0
        
        from modules.users.domain.schemas import UserResponse
        
        return AdminMentorDetail(
            mentor=MentorResponse.model_validate(mentor),
            user=UserResponse.model_validate(mentor.user),
            universities=[MentorUniversityResponse.model_validate(uni) for uni in mentor.universities],
            reviews_count=mentor.rating_count,
            total_consultations=total_consultations,
            completed_consultations=completed_consultations
        )
    
    async def get_popular_subjects(self, limit: int = 20) -> PopularSubjects:
        """Получение популярных предметов."""
        # Получаем все предметы менторов
        query = select(Mentor.subjects).where(Mentor.subjects.isnot(None))
        result = await self.db.execute(query)
        
        # Подсчитываем популярность
        subject_count = {}
        for row in result.scalars():
            for subject in row or []:
                if subject.strip():
                    subject_count[subject] = subject_count.get(subject, 0) + 1
        
        # Сортируем по популярности
        popular_subjects = sorted(
            subject_count.keys(),
            key=lambda x: subject_count[x],
            reverse=True
        )[:limit]
        
        return PopularSubjects(subjects=popular_subjects)
    
    async def get_popular_languages(self, limit: int = 10) -> PopularLanguages:
        """Получение популярных языков."""
        # Получаем все языки менторов
        query = select(Mentor.languages).where(Mentor.languages.isnot(None))
        result = await self.db.execute(query)
        
        # Подсчитываем популярность
        language_count = {}
        for row in result.scalars():
            for language in row or []:
                if language.strip():
                    language_count[language] = language_count.get(language, 0) + 1
        
        # Сортируем по популярности
        popular_languages = sorted(
            language_count.keys(),
            key=lambda x: language_count[x],
            reverse=True
        )[:limit]
        
        return PopularLanguages(languages=popular_languages)
    
    async def get_university_suggestions(
        self, 
        query: str, 
        limit: int = 10
    ) -> List[UniversitySuggestion]:
        """Получение предложений университетов для автокомплита."""
        search_pattern = f"%{query.lower()}%"
        
        # Поиск университетов
        suggestions_query = (
            select(
                MentorUniversity.university,
                MentorUniversity.country,
                MentorUniversity.city,
                func.count(MentorUniversity.id).label("count")
            )
            .where(func.lower(MentorUniversity.university).like(search_pattern))
            .group_by(MentorUniversity.university, MentorUniversity.country, MentorUniversity.city)
            .order_by(desc("count"))
            .limit(limit)
        )
        
        result = await self.db.execute(suggestions_query)
        
        suggestions = []
        for row in result:
            suggestions.append(UniversitySuggestion(
                name=row.university,
                country=row.country,
                city=row.city,
                count=row.count
            ))
        
        return suggestions
    
    async def _get_mentor_or_404(self, mentor_id: UUID) -> Mentor:
        """Получение ментора или 404."""
        query = select(Mentor).where(Mentor.user_id == mentor_id)
        result = await self.db.execute(query)
        mentor = result.scalar_one_or_none()
        
        if not mentor:
            raise NotFoundError("Mentor", str(mentor_id))
        
        return mentor
    
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


class MentorUniversityService:
    """Сервис для управления образованием менторов."""
    
    def __init__(self, db_session: AsyncSession):
        self.db = db_session
    
    async def add_university(
        self,
        mentor_id: UUID,
        university_data: MentorUniversityCreate
    ) -> MentorUniversityResponse:
        """Добавление образования ментора."""
        # Проверяем, что ментор существует
        mentor_query = select(Mentor).where(Mentor.user_id == mentor_id)
        mentor_result = await self.db.execute(mentor_query)
        mentor = mentor_result.scalar_one_or_none()
        
        if not mentor:
            raise NotFoundError("Mentor", str(mentor_id))
        
        # Создаем запись об образовании
        university = MentorUniversity(
            mentor_id=mentor_id,
            university=university_data.university,
            degree=university_data.degree,
            major=university_data.major,
            year_from=university_data.year_from,
            year_to=university_data.year_to,
            country=university_data.country,
            city=university_data.city
        )
        
        self.db.add(university)
        await self.db.commit()
        
        logger.info(
            "University added to mentor",
            mentor_id=mentor_id,
            university=university_data.university
        )
        
        return MentorUniversityResponse.model_validate(university)
    
    async def update_university(
        self,
        university_id: UUID,
        university_data: MentorUniversityUpdate
    ) -> MentorUniversityResponse:
        """Обновление образования ментора."""
        query = select(MentorUniversity).where(MentorUniversity.id == university_id)
        result = await self.db.execute(query)
        university = result.scalar_one_or_none()
        
        if not university:
            raise NotFoundError("MentorUniversity", str(university_id))
        
        # Обновляем поля
        update_data = university_data.dict(exclude_unset=True)
        
        for field, value in update_data.items():
            setattr(university, field, value)
        
        university.updated_at = datetime.utcnow()
        
        await self.db.commit()
        
        logger.info(
            "University updated",
            university_id=university_id,
            mentor_id=university.mentor_id,
            updated_fields=list(update_data.keys())
        )
        
        return MentorUniversityResponse.model_validate(university)
    
    async def delete_university(self, university_id: UUID) -> bool:
        """Удаление образования ментора."""
        query = select(MentorUniversity).where(MentorUniversity.id == university_id)
        result = await self.db.execute(query)
        university = result.scalar_one_or_none()
        
        if not university:
            return False
        
        await self.db.delete(university)
        await self.db.commit()
        
        logger.info(
            "University deleted",
            university_id=university_id,
            mentor_id=university.mentor_id
        )
        
        return True

