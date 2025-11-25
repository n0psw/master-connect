"""
API маршруты для чата.
"""
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from core.dependencies import CurrentUserInfo, get_current_user_info
from core.exceptions import MasterConnectException, NotFoundError, PermissionDeniedError
from core.logging import get_logger
from db.session import get_db
from modules.chat.application.services import ChatService
from modules.chat.domain.schemas import (
    DialogListResponse,
    MessageCreate,
    MessageListResponse,
    MessageResponse,
)

logger = get_logger(__name__)

router = APIRouter(prefix="/chat", tags=["Чат"])


async def get_chat_service(db: AsyncSession = Depends(get_db)) -> ChatService:
    """DI для сервиса чата."""
    return ChatService(db)


@router.get(
    "/dialogs",
    response_model=DialogListResponse,
    summary="Список диалогов",
    description="Получение диалогов, доступных текущему пользователю",
)
async def list_dialogs(
    current_user: CurrentUserInfo = Depends(get_current_user_info),
    chat_service: ChatService = Depends(get_chat_service),
) -> DialogListResponse:
    """Получение всех диалогов пользователя."""
    try:
        return await chat_service.list_user_dialogs(
            user_id=current_user.id,
            user_role=current_user.role,
        )
    except Exception as e:
        logger.error("Error listing dialogs", user_id=current_user.id, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Внутренняя ошибка сервера"
        )


@router.get(
    "/dialogs/{dialog_id}/messages",
    response_model=MessageListResponse,
    summary="Сообщения диалога",
    description="Получение сообщений конкретного диалога",
)
async def get_dialog_messages(
    dialog_id: UUID,
    current_user: CurrentUserInfo = Depends(get_current_user_info),
    chat_service: ChatService = Depends(get_chat_service),
) -> MessageListResponse:
    """Получение сообщений диалога."""
    try:
        return await chat_service.get_dialog_messages(
            dialog_id=dialog_id,
            user_id=current_user.id,
            user_role=current_user.role,
        )
    except NotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Диалог не найден"
        )
    except PermissionDeniedError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e)
        )
    except Exception as e:
        logger.error("Error getting dialog messages", dialog_id=dialog_id, user_id=current_user.id, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Внутренняя ошибка сервера"
        )


@router.post(
    "/dialogs/{dialog_id}/messages",
    response_model=MessageResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Отправить сообщение",
    description="Отправка сообщения в диалоге",
)
async def send_message(
    dialog_id: UUID,
    message_data: MessageCreate,
    current_user: CurrentUserInfo = Depends(get_current_user_info),
    chat_service: ChatService = Depends(get_chat_service),
) -> MessageResponse:
    """Отправка сообщения в диалог."""
    try:
        return await chat_service.send_message(
            dialog_id=dialog_id,
            user_id=current_user.id,
            user_role=current_user.role,
            data=message_data,
        )
    except NotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Диалог не найден"
        )
    except PermissionDeniedError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e)
        )
    except Exception as e:
        logger.error("Error sending message", dialog_id=dialog_id, user_id=current_user.id, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Внутренняя ошибка сервера"
        )



