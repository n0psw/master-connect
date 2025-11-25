"""
Сервисы для модуля платежей.
"""
from datetime import datetime
from typing import List, Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from core.exceptions import BusinessLogicError, NotFoundError, PermissionDeniedError
from core.logging import get_logger
from modules.bookings.domain.models import Booking, BookingStatus
from modules.payments.domain.models import PaymentEvidence
from modules.payments.domain.schemas import (
    PaymentEvidenceCreate,
    PaymentEvidenceResponse,
    PaymentEvidenceUpdate,
)
from modules.users.domain.models import User, UserRole

logger = get_logger(__name__)


class PaymentEvidenceService:
    """Сервис для управления доказательствами оплаты."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create_evidence(
        self,
        evidence_data: PaymentEvidenceCreate,
        created_by: UUID
    ) -> PaymentEvidenceResponse:
        """Создание доказательства оплаты."""
        # Проверяем существование бронирования
        booking_query = select(Booking).where(Booking.id == evidence_data.booking_id)
        booking_result = await self.db.execute(booking_query)
        booking = booking_result.scalar_one_or_none()
        
        if not booking:
            raise NotFoundError("Booking", str(evidence_data.booking_id))
        
        # Проверяем права доступа
        if booking.student_id != created_by:
            raise PermissionDeniedError("Недостаточно прав для добавления доказательства оплаты")
        
        # Проверяем статус бронирования
        if booking.status not in [BookingStatus.HOLD, BookingStatus.AWAITING_VERIFICATION]:
            raise BusinessLogicError("Нельзя добавить доказательство оплаты для данного бронирования")
        
        # Создаем доказательство
        evidence = PaymentEvidence(
            booking_id=evidence_data.booking_id,
            created_by=created_by,
            comment_text=evidence_data.comment_text,
            receipt_file_url=evidence_data.receipt_file_url
        )
        
        self.db.add(evidence)
        await self.db.commit()
        await self.db.refresh(evidence)
        
        logger.info("Payment evidence created", evidence_id=evidence.id, booking_id=evidence_data.booking_id)
        
        return await self._build_evidence_response(evidence)
    
    async def get_evidence_by_booking(
        self,
        booking_id: UUID,
        user_id: UUID,
        user_role: UserRole
    ) -> List[PaymentEvidenceResponse]:
        """Получение доказательств оплаты для бронирования."""
        # Проверяем права доступа
        booking_query = select(Booking).where(Booking.id == booking_id)
        booking_result = await self.db.execute(booking_query)
        booking = booking_result.scalar_one_or_none()
        
        if not booking:
            raise NotFoundError("Booking", str(booking_id))
        
        # Проверяем права доступа
        if user_role != UserRole.ADMIN and booking.student_id != user_id and booking.mentor_id != user_id:
            raise PermissionDeniedError("Недостаточно прав для просмотра доказательств оплаты")
        
        # Получаем доказательства
        evidence_query = (
            select(PaymentEvidence)
            .where(PaymentEvidence.booking_id == booking_id)
            .options(selectinload(PaymentEvidence.creator))
            .order_by(PaymentEvidence.created_at.desc())
        )
        
        evidence_result = await self.db.execute(evidence_query)
        evidences = evidence_result.scalars().all()
        
        return [await self._build_evidence_response(evidence) for evidence in evidences]
    
    async def get_evidence_by_id(
        self,
        evidence_id: UUID,
        user_id: UUID,
        user_role: UserRole
    ) -> PaymentEvidenceResponse:
        """Получение доказательства оплаты по ID."""
        evidence_query = (
            select(PaymentEvidence)
            .where(PaymentEvidence.id == evidence_id)
            .options(selectinload(PaymentEvidence.creator), selectinload(PaymentEvidence.booking))
        )
        
        evidence_result = await self.db.execute(evidence_query)
        evidence = evidence_result.scalar_one_or_none()
        
        if not evidence:
            raise NotFoundError("PaymentEvidence", str(evidence_id))
        
        # Проверяем права доступа
        if (user_role != UserRole.ADMIN and 
            evidence.created_by != user_id and 
            evidence.booking.student_id != user_id and 
            evidence.booking.mentor_id != user_id):
            raise PermissionDeniedError("Недостаточно прав для просмотра доказательства")
        
        return await self._build_evidence_response(evidence)
    
    async def update_evidence(
        self,
        evidence_id: UUID,
        update_data: PaymentEvidenceUpdate,
        user_id: UUID
    ) -> PaymentEvidenceResponse:
        """Обновление доказательства оплаты."""
        evidence_query = (
            select(PaymentEvidence)
            .where(PaymentEvidence.id == evidence_id)
            .options(selectinload(PaymentEvidence.creator))
        )
        
        evidence_result = await self.db.execute(evidence_query)
        evidence = evidence_result.scalar_one_or_none()
        
        if not evidence:
            raise NotFoundError("PaymentEvidence", str(evidence_id))
        
        # Проверяем права доступа
        if evidence.created_by != user_id:
            raise PermissionDeniedError("Недостаточно прав для редактирования доказательства")
        
        # Обновляем данные
        if update_data.comment_text is not None:
            evidence.comment_text = update_data.comment_text
        
        await self.db.commit()
        await self.db.refresh(evidence)
        
        logger.info("Payment evidence updated", evidence_id=evidence_id)
        
        return await self._build_evidence_response(evidence)
    
    async def delete_evidence(
        self,
        evidence_id: UUID,
        user_id: UUID,
        user_role: UserRole
    ) -> None:
        """Удаление доказательства оплаты."""
        evidence_query = (
            select(PaymentEvidence)
            .where(PaymentEvidence.id == evidence_id)
            .options(selectinload(PaymentEvidence.booking))
        )
        
        evidence_result = await self.db.execute(evidence_query)
        evidence = evidence_result.scalar_one_or_none()
        
        if not evidence:
            raise NotFoundError("PaymentEvidence", str(evidence_id))
        
        # Проверяем права доступа
        if (user_role != UserRole.ADMIN and 
            evidence.created_by != user_id):
            raise PermissionDeniedError("Недостаточно прав для удаления доказательства")
        
        await self.db.delete(evidence)
        await self.db.commit()
        
        logger.info("Payment evidence deleted", evidence_id=evidence_id)
    
    async def _build_evidence_response(self, evidence: PaymentEvidence) -> PaymentEvidenceResponse:
        """Построение ответа с информацией о доказательстве."""
        creator_rel = evidence.__dict__.get("creator")
        creator_name = creator_rel.name if creator_rel else None
        
        created_at = evidence.created_at
        if isinstance(created_at, datetime):
            created_at_str = created_at.isoformat()
        else:
            created_at_str = str(created_at)
        
        return PaymentEvidenceResponse(
            id=evidence.id,
            booking_id=evidence.booking_id,
            created_by=evidence.created_by,
            comment_text=evidence.comment_text,
            receipt_file_url=evidence.receipt_file_url,
            created_at=created_at_str,
            creator_name=creator_name
        )

