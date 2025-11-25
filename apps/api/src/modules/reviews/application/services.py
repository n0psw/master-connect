"""
Сервисы для модуля отзывов.
"""
from typing import Optional
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from core.exceptions import BusinessLogicError, NotFoundError, PermissionDeniedError
from core.logging import get_logger
from modules.bookings.domain.models import Booking, BookingStatus
from modules.reviews.domain.models import Review
from modules.reviews.domain.schemas import (
    ReviewCreate,
    ReviewResponse,
    ReviewStats,
    ReviewUpdate,
)
from modules.users.domain.models import User, Student
from modules.mentors.domain.models import Mentor

logger = get_logger(__name__)


class ReviewService:
    """Сервис для управления отзывами."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create_review(
        self,
        review_data: ReviewCreate,
        student_id: UUID
    ) -> ReviewResponse:
        """Создание отзыва."""
        # Проверяем существование бронирования
        booking_query = (
            select(Booking)
            .where(Booking.id == review_data.booking_id)
            .options(selectinload(Booking.review))
        )
        booking_result = await self.db.execute(booking_query)
        booking = booking_result.scalar_one_or_none()
        
        if not booking:
            raise NotFoundError("Booking", str(review_data.booking_id))
        
        # Проверяем права доступа
        if booking.student_id != student_id:
            raise PermissionDeniedError("Вы можете оставлять отзывы только на свои консультации")
        
        # Проверяем статус бронирования
        if booking.status != BookingStatus.COMPLETED:
            raise BusinessLogicError("Отзыв можно оставить только после завершения консультации")
        
        # Проверяем, что отзыв еще не оставлен
        if booking.review:
            raise BusinessLogicError("Отзыв на эту консультацию уже оставлен")
        
        # Создаем отзыв
        review = Review(
            booking_id=review_data.booking_id,
            student_id=student_id,
            mentor_id=booking.mentor_id,
            rating=review_data.rating,
            text=review_data.text
        )
        
        self.db.add(review)
        await self.db.commit()
        await self.db.refresh(review)
        
        logger.info("Review created", review_id=review.id, booking_id=review_data.booking_id, rating=review_data.rating)
        
        # Обновляем средний рейтинг ментора
        await self._update_mentor_rating(booking.mentor_id)
        
        return await self._build_review_response(review)
    
    async def get_review_by_id(
        self,
        review_id: UUID,
        user_id: UUID,
        user_role: str
    ) -> ReviewResponse:
        """Получение отзыва по ID."""
        review_query = (
            select(Review)
            .where(Review.id == review_id)
            .options(
                selectinload(Review.student).selectinload(Student.user),
                selectinload(Review.mentor).selectinload(Mentor.user)
            )
        )
        
        review_result = await self.db.execute(review_query)
        review = review_result.scalar_one_or_none()
        
        if not review:
            raise NotFoundError("Review", str(review_id))
        
        # Проверяем права доступа (студент, ментор или админ)
        if (user_role != "ADMIN" and 
            review.student_id != user_id and 
            review.mentor_id != user_id):
            raise PermissionDeniedError("Недостаточно прав для просмотра отзыва")
        
        return await self._build_review_response(review)
    
    async def get_reviews_by_mentor(
        self,
        mentor_id: UUID,
        page: int = 1,
        page_size: int = 20
    ) -> dict:
        """Получение отзывов ментора."""
        offset = (page - 1) * page_size
        
        # Получаем отзывы
        reviews_query = (
            select(Review)
            .where(Review.mentor_id == mentor_id)
            .options(
                selectinload(Review.student).selectinload(Student.user),
                selectinload(Review.mentor).selectinload(Mentor.user)
            )
            .order_by(Review.created_at.desc())
            .offset(offset)
            .limit(page_size)
        )
        
        reviews_result = await self.db.execute(reviews_query)
        reviews = reviews_result.scalars().all()
        
        # Получаем общее количество
        count_query = select(func.count()).select_from(Review).where(Review.mentor_id == mentor_id)
        count_result = await self.db.execute(count_query)
        total = count_result.scalar() or 0
        
        # Строим ответы для каждого отзыва с обработкой ошибок
        review_responses = []
        for review in reviews:
            try:
                review_response = await self._build_review_response(review)
                review_responses.append(review_response)
            except Exception as e:
                logger.error(
                    "Error building review response", 
                    review_id=review.id, 
                    mentor_id=mentor_id, 
                    error=str(e),
                    exc_info=True
                )
                # Пропускаем проблемный отзыв, но продолжаем обработку остальных
        
        return {
            "reviews": review_responses,
            "total": total,
            "page": page,
            "page_size": page_size
        }
    
    async def get_reviews_by_student(
        self,
        student_id: UUID,
        page: int = 1,
        page_size: int = 20
    ) -> dict:
        """Получение отзывов студента."""
        offset = (page - 1) * page_size
        
        # Получаем отзывы
        reviews_query = (
            select(Review)
            .where(Review.student_id == student_id)
            .options(
                selectinload(Review.student).selectinload(Student.user),
                selectinload(Review.mentor).selectinload(Mentor.user)
            )
            .order_by(Review.created_at.desc())
            .offset(offset)
            .limit(page_size)
        )
        
        reviews_result = await self.db.execute(reviews_query)
        reviews = reviews_result.scalars().all()
        
        # Получаем общее количество
        count_query = select(func.count()).select_from(Review).where(Review.student_id == student_id)
        count_result = await self.db.execute(count_query)
        total = count_result.scalar() or 0
        
        # Строим ответы с обработкой ошибок
        review_responses = []
        for review in reviews:
            try:
                review_response = await self._build_review_response(review)
                review_responses.append(review_response)
            except Exception as e:
                logger.error(
                    "Error building review response in list",
                    review_id=review.id,
                    error=str(e),
                    exc_info=True
                )
                # Пропускаем проблемный отзыв, но продолжаем обработку остальных
        
        return {
            "reviews": review_responses,
            "total": total,
            "page": page,
            "page_size": page_size
        }
    
    async def update_review(
        self,
        review_id: UUID,
        update_data: ReviewUpdate,
        student_id: UUID
    ) -> ReviewResponse:
        """Обновление отзыва."""
        review_query = select(Review).where(Review.id == review_id)
        review_result = await self.db.execute(review_query)
        review = review_result.scalar_one_or_none()
        
        if not review:
            raise NotFoundError("Review", str(review_id))
        
        # Проверяем права доступа
        if review.student_id != student_id:
            raise PermissionDeniedError("Вы можете редактировать только свои отзывы")
        
        # Обновляем данные
        if update_data.rating is not None:
            review.rating = update_data.rating
        if update_data.text is not None:
            review.text = update_data.text
        
        await self.db.commit()
        await self.db.refresh(review)
        
        logger.info("Review updated", review_id=review_id)
        
        # Обновляем средний рейтинг ментора
        await self._update_mentor_rating(review.mentor_id)
        
        return await self._build_review_response(review)
    
    async def delete_review(
        self,
        review_id: UUID,
        user_id: UUID,
        user_role: str
    ) -> None:
        """Удаление отзыва."""
        review_query = select(Review).where(Review.id == review_id)
        review_result = await self.db.execute(review_query)
        review = review_result.scalar_one_or_none()
        
        if not review:
            raise NotFoundError("Review", str(review_id))
        
        # Проверяем права доступа (студент или админ)
        if user_role != "ADMIN" and review.student_id != user_id:
            raise PermissionDeniedError("Недостаточно прав для удаления отзыва")
        
        mentor_id = review.mentor_id
        
        await self.db.delete(review)
        await self.db.commit()
        
        logger.info("Review deleted", review_id=review_id)
        
        # Обновляем средний рейтинг ментора
        await self._update_mentor_rating(mentor_id)
    
    async def get_mentor_stats(self, mentor_id: UUID) -> ReviewStats:
        """Получение статистики отзывов ментора."""
        # Получаем все отзывы ментора
        reviews_query = select(Review).where(Review.mentor_id == mentor_id)
        reviews_result = await self.db.execute(reviews_query)
        reviews = reviews_result.scalars().all()
        
        total_reviews = len(reviews)
        
        if total_reviews == 0:
            return ReviewStats(
                total_reviews=0,
                average_rating=0.0,
                rating_distribution={1: 0, 2: 0, 3: 0, 4: 0, 5: 0},
                positive_reviews=0,
                negative_reviews=0
            )
        
        # Вычисляем статистику
        ratings = [review.rating for review in reviews]
        average_rating = sum(ratings) / total_reviews
        
        rating_distribution = {i: ratings.count(i) for i in range(1, 6)}
        positive_reviews = sum(1 for r in ratings if r >= 4)
        negative_reviews = sum(1 for r in ratings if r <= 2)
        
        return ReviewStats(
            total_reviews=total_reviews,
            average_rating=round(average_rating, 2),
            rating_distribution=rating_distribution,
            positive_reviews=positive_reviews,
            negative_reviews=negative_reviews
        )
    
    async def recalculate_all_mentor_ratings(self) -> dict:
        """Пересчитывает рейтинг для всех менторов на основе существующих отзывов."""
        from modules.mentors.domain.models import Mentor
        from decimal import Decimal
        
        try:
            # Получаем всех менторов
            mentors_query = select(Mentor)
            mentors_result = await self.db.execute(mentors_query)
            mentors = mentors_result.scalars().all()
            
            updated_count = 0
            for mentor in mentors:
                try:
                    # Получаем все отзывы для этого ментора
                    reviews_query = select(Review.rating).where(Review.mentor_id == mentor.user_id)
                    reviews_result = await self.db.execute(reviews_query)
                    ratings = reviews_result.scalars().all()
                    
                    # Вычисляем средний рейтинг
                    if ratings:
                        average_rating = sum(ratings) / len(ratings)
                        total_reviews = len(ratings)
                    else:
                        average_rating = 0.0
                        total_reviews = 0
                    
                    # Обновляем ментора
                    old_rating = mentor.rating_avg
                    old_count = mentor.rating_count
                    
                    mentor.rating_avg = Decimal(str(round(average_rating, 2)))
                    mentor.rating_count = total_reviews
                    
                    await self.db.commit()
                    
                    if old_rating != mentor.rating_avg or old_count != mentor.rating_count:
                        updated_count += 1
                        logger.info(
                            f"Mentor {mentor.user_id}: "
                            f"rating {old_rating} -> {mentor.rating_avg}, "
                            f"count {old_count} -> {mentor.rating_count}"
                        )
                        
                except Exception as e:
                    logger.error(
                        f"Error updating mentor {mentor.user_id}: {str(e)}",
                        exc_info=True
                    )
                    await self.db.rollback()
                    continue
            
            logger.info(f"Successfully updated {updated_count} mentors")
            return {"updated_count": updated_count, "total_mentors": len(mentors)}
            
        except Exception as e:
            logger.error(f"Error in recalculate_all_mentor_ratings: {str(e)}", exc_info=True)
            await self.db.rollback()
            raise
    
    async def _update_mentor_rating(self, mentor_id: UUID) -> None:
        """Обновление среднего рейтинга ментора."""
        try:
            from modules.mentors.domain.models import Mentor
            from decimal import Decimal
            
            # Получаем все отзывы ментора
            reviews_query = select(Review.rating).where(Review.mentor_id == mentor_id)
            reviews_result = await self.db.execute(reviews_query)
            ratings = reviews_result.scalars().all()
            
            # Вычисляем средний рейтинг
            if ratings:
                average_rating = sum(ratings) / len(ratings)
                total_reviews = len(ratings)
            else:
                average_rating = 0.0
                total_reviews = 0
            
            # Обновляем ментора
            mentor_query = select(Mentor).where(Mentor.user_id == mentor_id)
            mentor_result = await self.db.execute(mentor_query)
            mentor = mentor_result.scalar_one_or_none()
            
            if mentor:
                # Используем правильные имена полей: rating_avg и rating_count
                mentor.rating_avg = Decimal(str(round(average_rating, 2)))
                mentor.rating_count = total_reviews
                await self.db.commit()
                
                logger.info(
                    "Mentor rating updated", 
                    mentor_id=mentor_id, 
                    rating=float(mentor.rating_avg), 
                    total_reviews=mentor.rating_count
                )
        except Exception as e:
            logger.error(
                "Error updating mentor rating", 
                mentor_id=mentor_id, 
                error=str(e), 
                exc_info=True
            )
            # Не поднимаем исключение, чтобы не сломать создание отзыва
    
    async def _build_review_response(self, review: Review) -> ReviewResponse:
        """Построение ответа с информацией об отзыве."""
        try:
            # Используем getattr для безопасного доступа к связанным объектам
            student = getattr(review, 'student', None)
            mentor = getattr(review, 'mentor', None)
            
            student_user = getattr(student, 'user', None) if student else None
            mentor_user = getattr(mentor, 'user', None) if mentor else None
            
            # avatar_url хранится в Mentor и Student моделях
            student_avatar_url = getattr(student, 'avatar_url', None) if student else None
            mentor_avatar_url = getattr(mentor, 'avatar_url', None) if mentor else None
            
            return ReviewResponse(
                id=review.id,
                booking_id=review.booking_id,
                student_id=review.student_id,
                mentor_id=review.mentor_id,
                rating=review.rating,
                text=review.text,
                created_at=review.created_at,
                updated_at=review.updated_at,
                student_name=student_user.name if student_user else None,
                student_avatar_url=student_avatar_url,
                mentor_name=mentor_user.name if mentor_user else None,
                mentor_avatar_url=mentor_avatar_url
            )
        except Exception as e:
            logger.error(
                "Error building review response",
                review_id=review.id,
                error=str(e),
                exc_info=True
            )
            # Возвращаем минимальный ответ без связанных данных
            return ReviewResponse(
                id=review.id,
                booking_id=review.booking_id,
                student_id=review.student_id,
                mentor_id=review.mentor_id,
                rating=review.rating,
                text=review.text,
                created_at=review.created_at,
                updated_at=review.updated_at,
                student_name=None,
                student_avatar_url=None,
                mentor_name=None,
                mentor_avatar_url=None
            )

