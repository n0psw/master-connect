"""
Сервисы для модуля поддержки.
"""
from typing import List, Optional, Tuple
from uuid import UUID

from sqlalchemy import and_, desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from core.exceptions import BusinessLogicError, NotFoundError
from core.logging import get_logger
from modules.support.domain.models import SupportTicket, TicketStatus
from modules.support.domain.schemas import (
    TicketCreate,
    TicketResponse,
    TicketStats,
    TicketUpdate,
)
from modules.users.domain.models import User

logger = get_logger(__name__)


class SupportService:
    """Сервис для управления тикетами поддержки."""
    
    def __init__(self, db_session: AsyncSession):
        self.db = db_session
    
    async def create_ticket(
        self,
        ticket_data: TicketCreate,
        user_id: UUID
    ) -> TicketResponse:
        """Создание нового тикета."""
        logger.info("Creating support ticket", user_id=user_id, subject=ticket_data.subject)
        
        ticket = SupportTicket(
            user_id=user_id,
            booking_id=ticket_data.booking_id,
            subject=ticket_data.subject,
            body=ticket_data.body,
            status=TicketStatus.OPEN
        )
        
        self.db.add(ticket)
        await self.db.commit()
        await self.db.refresh(ticket)
        
        logger.info("Support ticket created", ticket_id=ticket.id)
        
        return await self._build_ticket_response(ticket)
    
    async def get_user_tickets(
        self,
        user_id: UUID,
        page: int = 1,
        page_size: int = 20,
        status: Optional[TicketStatus] = None
    ) -> Tuple[List[TicketResponse], int]:
        """Получение тикетов пользователя."""
        offset = (page - 1) * page_size
        
        query = select(SupportTicket).where(SupportTicket.user_id == user_id)
        
        if status:
            query = query.where(SupportTicket.status == status)
        
        query = query.order_by(desc(SupportTicket.created_at))
        
        # Подсчет
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await self.db.execute(count_query)
        total = total_result.scalar() or 0
        
        # Пагинация
        query = query.limit(page_size).offset(offset)
        
        result = await self.db.execute(query)
        tickets = result.scalars().all()
        
        responses = []
        for ticket in tickets:
            response = await self._build_ticket_response(ticket)
            responses.append(response)
        
        return responses, total
    
    async def get_all_tickets(
        self,
        page: int = 1,
        page_size: int = 20,
        status: Optional[TicketStatus] = None
    ) -> Tuple[List[TicketResponse], int]:
        """Получение всех тикетов (для админов)."""
        offset = (page - 1) * page_size
        
        query = select(SupportTicket)
        
        if status:
            query = query.where(SupportTicket.status == status)
        
        query = query.order_by(desc(SupportTicket.created_at))
        
        # Подсчет
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await self.db.execute(count_query)
        total = total_result.scalar() or 0
        
        # Пагинация
        query = query.limit(page_size).offset(offset)
        
        result = await self.db.execute(query)
        tickets = result.scalars().all()
        
        responses = []
        for ticket in tickets:
            response = await self._build_ticket_response(ticket)
            responses.append(response)
        
        return responses, total
    
    async def get_ticket(
        self,
        ticket_id: UUID,
        user_id: Optional[UUID] = None
    ) -> TicketResponse:
        """Получение тикета по ID."""
        query = select(SupportTicket).where(SupportTicket.id == ticket_id)
        
        if user_id:
            query = query.where(SupportTicket.user_id == user_id)
        
        result = await self.db.execute(query)
        ticket = result.scalar_one_or_none()
        
        if not ticket:
            raise NotFoundError("SupportTicket", str(ticket_id))
        
        return await self._build_ticket_response(ticket)
    
    async def update_ticket(
        self,
        ticket_id: UUID,
        ticket_data: TicketUpdate,
        user_id: UUID
    ) -> TicketResponse:
        """Обновление тикета пользователем."""
        query = select(SupportTicket).where(
            and_(
                SupportTicket.id == ticket_id,
                SupportTicket.user_id == user_id
            )
        )
        result = await self.db.execute(query)
        ticket = result.scalar_one_or_none()
        
        if not ticket:
            raise NotFoundError("SupportTicket", str(ticket_id))
        
        if ticket.is_closed:
            raise BusinessLogicError("Невозможно изменить закрытый тикет")
        
        if ticket_data.subject:
            ticket.subject = ticket_data.subject
        
        if ticket_data.body:
            ticket.body = ticket_data.body
        
        await self.db.commit()
        await self.db.refresh(ticket)
        
        logger.info("Ticket updated", ticket_id=ticket_id)
        
        return await self._build_ticket_response(ticket)
    
    async def update_ticket_status(
        self,
        ticket_id: UUID,
        new_status: TicketStatus
    ) -> TicketResponse:
        """Обновление статуса тикета (админ)."""
        query = select(SupportTicket).where(SupportTicket.id == ticket_id)
        result = await self.db.execute(query)
        ticket = result.scalar_one_or_none()
        
        if not ticket:
            raise NotFoundError("SupportTicket", str(ticket_id))
        
        if not ticket.can_transition_to(new_status):
            raise BusinessLogicError(
                f"Невозможно изменить статус с {ticket.status} на {new_status}"
            )
        
        ticket.status = new_status
        await self.db.commit()
        await self.db.refresh(ticket)
        
        logger.info("Ticket status updated", ticket_id=ticket_id, new_status=new_status)
        
        return await self._build_ticket_response(ticket)
    
    async def get_ticket_stats(self) -> TicketStats:
        """Получение статистики по тикетам."""
        total_query = select(func.count()).select_from(SupportTicket)
        total_result = await self.db.execute(total_query)
        total = total_result.scalar() or 0
        
        open_query = select(func.count()).where(SupportTicket.status == TicketStatus.OPEN)
        open_result = await self.db.execute(open_query)
        open_count = open_result.scalar() or 0
        
        in_progress_query = select(func.count()).where(
            SupportTicket.status == TicketStatus.IN_PROGRESS
        )
        in_progress_result = await self.db.execute(in_progress_query)
        in_progress_count = in_progress_result.scalar() or 0
        
        resolved_query = select(func.count()).where(
            SupportTicket.status == TicketStatus.RESOLVED
        )
        resolved_result = await self.db.execute(resolved_query)
        resolved_count = resolved_result.scalar() or 0
        
        closed_query = select(func.count()).where(
            SupportTicket.status == TicketStatus.CLOSED
        )
        closed_result = await self.db.execute(closed_query)
        closed_count = closed_result.scalar() or 0
        
        return TicketStats(
            total=total,
            open=open_count,
            in_progress=in_progress_count,
            resolved=resolved_count,
            closed=closed_count
        )
    
    async def _build_ticket_response(self, ticket: SupportTicket) -> TicketResponse:
        """Построение ответа с информацией о тикете."""
        # Загружаем пользователя если не загружен
        if not hasattr(ticket, 'user') or ticket.user is None:
            await self.db.refresh(ticket, ["user"])
        
        return TicketResponse(
            id=ticket.id,
            user_id=ticket.user_id,
            booking_id=ticket.booking_id,
            subject=ticket.subject,
            body=ticket.body,
            status=ticket.status,
            created_at=ticket.created_at,
            updated_at=ticket.updated_at,
            user_name=ticket.user.name if ticket.user else None,
            user_email=ticket.user.email if ticket.user else None
        )

