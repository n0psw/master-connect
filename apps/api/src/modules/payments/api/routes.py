"""
API роуты для модуля платежей.
"""
import os
import shutil
from pathlib import Path
from typing import List
from uuid import UUID, uuid4

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, status
from sqlalchemy.ext.asyncio import AsyncSession

from core.dependencies import (
    get_current_active_user,
    get_current_admin,
    get_current_user_info,
    CurrentUserInfo,
)
from core.exceptions import BusinessLogicError, NotFoundError, PermissionDeniedError
from core.logging import get_logger
from db.session import get_db
from modules.payments.application.services import PaymentEvidenceService
from modules.payments.domain.schemas import (
    PaymentEvidenceCreate,
    PaymentEvidenceResponse,
    PaymentEvidenceUpdate,
)

logger = get_logger(__name__)

router = APIRouter(prefix="/payments", tags=["Платежи"])


async def get_payment_service(db: AsyncSession = Depends(get_db)) -> PaymentEvidenceService:
    """Dependency для получения сервиса платежей."""
    return PaymentEvidenceService(db)


@router.post(
    "/evidence",
    response_model=PaymentEvidenceResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Создать доказательство оплаты",
    description="Создание доказательства оплаты с загрузкой файла",
    responses={
        201: {"description": "Доказательство создано"},
        400: {"description": "Некорректные данные или файл"},
        401: {"description": "Требуется авторизация"},
        403: {"description": "Недостаточно прав доступа"},
        404: {"description": "Бронирование не найдено"},
        422: {"description": "Ошибка валидации"},
    }
)
async def create_payment_evidence(
    booking_id: UUID = Form(..., description="ID бронирования"),
    comment_text: str = Form(None, description="Комментарий к оплате"),
    file: UploadFile = File(..., description="Файл квитанции (PDF, JPG, PNG)"),
    current_user_info: CurrentUserInfo = Depends(get_current_user_info),
    payment_service: PaymentEvidenceService = Depends(get_payment_service)
) -> PaymentEvidenceResponse:
    """
    Создание доказательства оплаты с загрузкой файла.
    
    Поддерживаемые форматы файлов: PDF, JPG, JPEG, PNG
    Максимальный размер файла: 10MB
    """
    try:
        # Валидация файла
        if not file.filename:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Файл не выбран"
            )
        
        # Проверка типа файла
        allowed_extensions = {'.pdf', '.jpg', '.jpeg', '.png'}
        file_extension = '.' + file.filename.split('.')[-1].lower()
        
        if file_extension not in allowed_extensions:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Неподдерживаемый формат файла. Разрешены: {', '.join(allowed_extensions)}"
            )
        
        # Проверка размера файла (10MB)
        max_size = 10 * 1024 * 1024  # 10MB
        content = await file.read()
        if len(content) > max_size:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Размер файла превышает 10MB"
            )
        
        # Создаем директорию для загрузок если её нет
        upload_dir = Path("uploads/payment_evidences")
        try:
            upload_dir.mkdir(parents=True, exist_ok=True, mode=0o755)
        except (PermissionError, OSError) as e:
            import os
            import stat
            try:
                os.makedirs(upload_dir, mode=0o755, exist_ok=True)
                if upload_dir.exists():
                    os.chmod(upload_dir, 0o755)
            except (PermissionError, OSError):
                logger.error(f"Cannot create upload directory: {e}")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Ошибка доступа к директории загрузок. Обратитесь к администратору."
                )
        
        # Генерируем уникальное имя файла
        unique_filename = f"{uuid4().hex}{file_extension}"
        file_path = upload_dir / unique_filename
        
        # Сохраняем файл на диск
        with open(file_path, "wb") as f:
            f.write(content)
        
        # URL для доступа к файлу (будет отдаваться через статические файлы)
        file_url = f"/uploads/payment_evidences/{unique_filename}"
        
        # Создаем доказательство
        evidence_data = PaymentEvidenceCreate(
            booking_id=booking_id,
            comment_text=comment_text,
            receipt_file_url=file_url
        )
        
        evidence = await payment_service.create_evidence(
            evidence_data=evidence_data,
            created_by=current_user_info.user_id
        )
        
        logger.info(
            "Payment evidence created",
            evidence_id=evidence.id,
            booking_id=booking_id,
            user_id=current_user_info.user_id,
            filename=file.filename
        )
        
        return evidence
    
    except NotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Бронирование не найдено"
        )
    
    except (BusinessLogicError, PermissionDeniedError) as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    
    except Exception as e:
        logger.error("Error creating payment evidence", booking_id=booking_id, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Внутренняя ошибка сервера"
        )


@router.get(
    "/evidence/booking/{booking_id}",
    response_model=List[PaymentEvidenceResponse],
    summary="Получить доказательства оплаты",
    description="Получение всех доказательств оплаты для бронирования",
    responses={
        200: {"description": "Список доказательств оплаты"},
        401: {"description": "Требуется авторизация"},
        403: {"description": "Недостаточно прав доступа"},
        404: {"description": "Бронирование не найдено"},
    }
)
async def get_payment_evidence(
    booking_id: UUID,
    current_user_info: CurrentUserInfo = Depends(get_current_user_info),
    payment_service: PaymentEvidenceService = Depends(get_payment_service)
) -> List[PaymentEvidenceResponse]:
    """Получение всех доказательств оплаты для бронирования."""
    try:
        evidences = await payment_service.get_evidence_by_booking(
            booking_id=booking_id,
            user_id=current_user_info.user_id,
            user_role=current_user_info.role
        )
        
        return evidences
    
    except NotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Бронирование не найдено"
        )
    
    except PermissionDeniedError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e)
        )
    
    except Exception as e:
        logger.error("Error getting payment evidence", booking_id=booking_id, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Внутренняя ошибка сервера"
        )


@router.get(
    "/evidence/{evidence_id}",
    response_model=PaymentEvidenceResponse,
    summary="Получить доказательство оплаты",
    description="Получение конкретного доказательства оплаты по ID",
    responses={
        200: {"description": "Доказательство оплаты"},
        401: {"description": "Требуется авторизация"},
        403: {"description": "Недостаточно прав доступа"},
        404: {"description": "Доказательство не найдено"},
    }
)
async def get_payment_evidence_by_id(
    evidence_id: UUID,
    current_user_info: CurrentUserInfo = Depends(get_current_user_info),
    payment_service: PaymentEvidenceService = Depends(get_payment_service)
) -> PaymentEvidenceResponse:
    """Получение конкретного доказательства оплаты по ID."""
    try:
        evidence = await payment_service.get_evidence_by_id(
            evidence_id=evidence_id,
            user_id=current_user_info.user_id,
            user_role=current_user_info.role
        )
        
        return evidence
    
    except NotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Доказательство не найдено"
        )
    
    except PermissionDeniedError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e)
        )
    
    except Exception as e:
        logger.error("Error getting payment evidence", evidence_id=evidence_id, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Внутренняя ошибка сервера"
        )


@router.put(
    "/evidence/{evidence_id}",
    response_model=PaymentEvidenceResponse,
    summary="Обновить доказательство оплаты",
    description="Обновление комментария к доказательству оплаты",
    responses={
        200: {"description": "Доказательство обновлено"},
        400: {"description": "Некорректные данные"},
        401: {"description": "Требуется авторизация"},
        403: {"description": "Недостаточно прав доступа"},
        404: {"description": "Доказательство не найдено"},
        422: {"description": "Ошибка валидации"},
    }
)
async def update_payment_evidence(
    evidence_id: UUID,
    update_data: PaymentEvidenceUpdate,
    current_user_info: CurrentUserInfo = Depends(get_current_user_info),
    payment_service: PaymentEvidenceService = Depends(get_payment_service)
) -> PaymentEvidenceResponse:
    """Обновление доказательства оплаты."""
    try:
        evidence = await payment_service.update_evidence(
            evidence_id=evidence_id,
            update_data=update_data,
            user_id=current_user_info.user_id
        )
        
        logger.info("Payment evidence updated", evidence_id=evidence_id, user_id=current_user_info.user_id)
        
        return evidence
    
    except NotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Доказательство не найдено"
        )
    
    except PermissionDeniedError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e)
        )
    
    except Exception as e:
        logger.error("Error updating payment evidence", evidence_id=evidence_id, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Внутренняя ошибка сервера"
        )


@router.delete(
    "/evidence/{evidence_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Удалить доказательство оплаты",
    description="Удаление доказательства оплаты",
    responses={
        204: {"description": "Доказательство удалено"},
        401: {"description": "Требуется авторизация"},
        403: {"description": "Недостаточно прав доступа"},
        404: {"description": "Доказательство не найдено"},
    }
)
async def delete_payment_evidence(
    evidence_id: UUID,
    current_user_info: CurrentUserInfo = Depends(get_current_user_info),
    payment_service: PaymentEvidenceService = Depends(get_payment_service)
) -> None:
    """Удаление доказательства оплаты."""
    try:
        await payment_service.delete_evidence(
            evidence_id=evidence_id,
            user_id=current_user_info.user_id,
            user_role=current_user_info.role
        )
        
        logger.info("Payment evidence deleted", evidence_id=evidence_id, user_id=current_user_info.user_id)
    
    except NotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Доказательство не найдено"
        )
    
    except PermissionDeniedError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e)
        )
    
    except Exception as e:
        logger.error("Error deleting payment evidence", evidence_id=evidence_id, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Внутренняя ошибка сервера"
        )
