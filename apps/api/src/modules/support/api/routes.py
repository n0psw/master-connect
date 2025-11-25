"""
API роуты для модуля поддержки.
"""
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from core.dependencies import get_current_active_user, get_current_admin
from core.exceptions import BusinessLogicError, NotFoundError
from core.logging import get_logger
from db.session import get_db
from modules.support.application.services import SupportService
from modules.support.domain.models import TicketStatus
from modules.support.domain.schemas import (
    TicketCreate,
    TicketList,
    TicketResponse,
    TicketStats,
    TicketStatusUpdate,
    TicketUpdate,
)
from modules.users.domain.models import User

logger = get_logger(__name__)

router = APIRouter(prefix="/support", tags=["Поддержка"])


async def get_support_service(db: AsyncSession = Depends(get_db)) -> SupportService:
    """Dependency для получения сервиса поддержки."""
    return SupportService(db)


@router.post(
    "/tickets",
    response_model=TicketResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Создать тикет поддержки",
    description="Создание нового тикета в службу поддержки",
    responses={
        201: {"description": "Тикет создан"},
        401: {"description": "Требуется авторизация"},
        422: {"description": "Ошибка валидации"},
    }
)
async def create_ticket(
    ticket_data: TicketCreate,
    current_user: User = Depends(get_current_active_user),
    service: SupportService = Depends(get_support_service)
) -> TicketResponse:
    """
    Создание нового тикета поддержки.
    
    Может включать ссылку на бронирование, если тикет связан с консультацией.
    """
    try:
        ticket = await service.create_ticket(
            ticket_data=ticket_data,
            user_id=current_user.id
        )
        
        logger.info(
            "Ticket created",
            ticket_id=ticket.id,
            user_id=current_user.id
        )
        
        return ticket
    
    except Exception as e:
        logger.error("Error creating ticket", user_id=current_user.id, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Внутренняя ошибка сервера"
        )


@router.get(
    "/tickets",
    response_model=TicketList,
    summary="Получить мои тикеты",
    description="Получение списка тикетов текущего пользователя",
    responses={
        200: {"description": "Список тикетов"},
        401: {"description": "Требуется авторизация"},
    }
)
async def get_my_tickets(
    page: int = Query(1, ge=1, description="Номер страницы"),
    page_size: int = Query(20, ge=1, le=100, description="Размер страницы"),
    status: TicketStatus = Query(None, description="Фильтр по статусу"),
    current_user: User = Depends(get_current_active_user),
    service: SupportService = Depends(get_support_service)
) -> TicketList:
    """
    Получение списка тикетов текущего пользователя.
    """
    try:
        tickets, total = await service.get_user_tickets(
            user_id=current_user.id,
            page=page,
            page_size=page_size,
            status=status
        )
        
        return TicketList(
            tickets=tickets,
            total=total,
            page=page,
            page_size=page_size
        )
    
    except Exception as e:
        logger.error("Error getting tickets", user_id=current_user.id, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Внутренняя ошибка сервера"
        )


@router.get(
    "/tickets/{ticket_id}",
    response_model=TicketResponse,
    summary="Получить тикет",
    description="Получение информации о конкретном тикете",
    responses={
        200: {"description": "Информация о тикете"},
        401: {"description": "Требуется авторизация"},
        404: {"description": "Тикет не найден"},
    }
)
async def get_ticket(
    ticket_id: str,
    current_user: User = Depends(get_current_active_user),
    service: SupportService = Depends(get_support_service)
) -> TicketResponse:
    """
    Получение информации о тикете.
    """
    try:
        ticket = await service.get_ticket(
            ticket_id=ticket_id,
            user_id=current_user.id
        )
        return ticket
    
    except NotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Тикет не найден"
        )
    
    except Exception as e:
        logger.error("Error getting ticket", ticket_id=ticket_id, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Внутренняя ошибка сервера"
        )


@router.put(
    "/tickets/{ticket_id}",
    response_model=TicketResponse,
    summary="Обновить тикет",
    description="Обновление информации о тикете",
    responses={
        200: {"description": "Тикет обновлен"},
        400: {"description": "Некорректные данные"},
        401: {"description": "Требуется авторизация"},
        404: {"description": "Тикет не найден"},
    }
)
async def update_ticket(
    ticket_id: str,
    ticket_data: TicketUpdate,
    current_user: User = Depends(get_current_active_user),
    service: SupportService = Depends(get_support_service)
) -> TicketResponse:
    """
    Обновление тикета.
    
    Пользователи могут обновлять только свои тикеты и только если они не закрыты.
    """
    try:
        ticket = await service.update_ticket(
            ticket_id=ticket_id,
            ticket_data=ticket_data,
            user_id=current_user.id
        )
        return ticket
    
    except NotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Тикет не найден"
        )
    
    except BusinessLogicError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    
    except Exception as e:
        logger.error("Error updating ticket", ticket_id=ticket_id, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Внутренняя ошибка сервера"
        )


# Админские endpoints
@router.get(
    "/admin/tickets",
    response_model=TicketList,
    summary="Получить все тикеты (админ)",
    description="Получение списка всех тикетов для администраторов",
    responses={
        200: {"description": "Список тикетов"},
        401: {"description": "Требуется авторизация"},
        403: {"description": "Недостаточно прав"},
    }
)
async def get_all_tickets(
    page: int = Query(1, ge=1, description="Номер страницы"),
    page_size: int = Query(20, ge=1, le=100, description="Размер страницы"),
    status: TicketStatus = Query(None, description="Фильтр по статусу"),
    current_user: User = Depends(get_current_admin),
    service: SupportService = Depends(get_support_service)
) -> TicketList:
    """
    Получение всех тикетов (только для админов).
    """
    try:
        tickets, total = await service.get_all_tickets(
            page=page,
            page_size=page_size,
            status=status
        )
        
        return TicketList(
            tickets=tickets,
            total=total,
            page=page,
            page_size=page_size
        )
    
    except Exception as e:
        logger.error("Error getting all tickets", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Внутренняя ошибка сервера"
        )


@router.patch(
    "/admin/tickets/{ticket_id}/status",
    response_model=TicketResponse,
    summary="Изменить статус тикета (админ)",
    description="Изменение статуса тикета администратором",
    responses={
        200: {"description": "Статус изменен"},
        400: {"description": "Некорректный переход статуса"},
        401: {"description": "Требуется авторизация"},
        403: {"description": "Недостаточно прав"},
        404: {"description": "Тикет не найден"},
    }
)
async def update_ticket_status(
    ticket_id: str,
    status_data: TicketStatusUpdate,
    current_user: User = Depends(get_current_admin),
    service: SupportService = Depends(get_support_service)
) -> TicketResponse:
    """
    Изменение статуса тикета (только для админов).
    """
    try:
        ticket = await service.update_ticket_status(
            ticket_id=ticket_id,
            new_status=status_data.status
        )
        
        logger.info(
            "Ticket status updated by admin",
            ticket_id=ticket_id,
            admin_id=current_user.id,
            new_status=status_data.status
        )
        
        return ticket
    
    except NotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Тикет не найден"
        )
    
    except BusinessLogicError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    
    except Exception as e:
        logger.error("Error updating ticket status", ticket_id=ticket_id, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Внутренняя ошибка сервера"
        )


@router.get(
    "/admin/stats",
    response_model=TicketStats,
    summary="Статистика по тикетам (админ)",
    description="Получение статистики по тикетам поддержки",
    responses={
        200: {"description": "Статистика"},
        401: {"description": "Требуется авторизация"},
        403: {"description": "Недостаточно прав"},
    }
)
async def get_ticket_stats(
    current_user: User = Depends(get_current_admin),
    service: SupportService = Depends(get_support_service)
) -> TicketStats:
    """
    Получение статистики по тикетам (только для админов).
    """
    try:
        stats = await service.get_ticket_stats()
        return stats
    
    except Exception as e:
        logger.error("Error getting ticket stats", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Внутренняя ошибка сервера"
        )

