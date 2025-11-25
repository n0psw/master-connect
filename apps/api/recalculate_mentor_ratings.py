"""
Скрипт для пересчета рейтингов всех менторов на основе существующих отзывов.
Используется для исправления рейтингов, которые не были обновлены из-за бага в _update_mentor_rating.
"""
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))

from decimal import Decimal
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from db.session import get_async_session
from modules.mentors.domain.models import Mentor
from modules.reviews.domain.models import Review
from core.logging import get_logger

logger = get_logger(__name__)


async def recalculate_all_mentor_ratings():
    """Пересчитывает рейтинг для всех менторов на основе существующих отзывов."""
    async for db in get_async_session():
        try:
            # Получаем всех менторов
            mentors_query = select(Mentor)
            mentors_result = await db.execute(mentors_query)
            mentors = mentors_result.scalars().all()
            
            logger.info(f"Found {len(mentors)} mentors to process")
            
            updated_count = 0
            for mentor in mentors:
                try:
                    # Получаем все отзывы для этого ментора
                    reviews_query = select(Review.rating).where(Review.mentor_id == mentor.user_id)
                    reviews_result = await db.execute(reviews_query)
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
                    
                    await db.commit()
                    
                    if old_rating != mentor.rating_avg or old_count != mentor.rating_count:
                        updated_count += 1
                        logger.info(
                            f"Mentor {mentor.user_id}: "
                            f"rating {old_rating} -> {mentor.rating_avg}, "
                            f"count {old_count} -> {mentor.rating_count}"
                        )
                    else:
                        logger.debug(
                            f"Mentor {mentor.user_id}: "
                            f"no change (rating={mentor.rating_avg}, count={mentor.rating_count})"
                        )
                        
                except Exception as e:
                    logger.error(
                        f"Error updating mentor {mentor.user_id}: {str(e)}",
                        exc_info=True
                    )
                    await db.rollback()
                    continue
            
            logger.info(f"Successfully updated {updated_count} mentors")
            
        except Exception as e:
            logger.error(f"Error in recalculate_all_mentor_ratings: {str(e)}", exc_info=True)
            await db.rollback()
        finally:
            await db.close()
            break


if __name__ == "__main__":
    asyncio.run(recalculate_all_mentor_ratings())

