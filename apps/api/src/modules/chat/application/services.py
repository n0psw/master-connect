"""
Сервисы для модуля чата.
"""
from datetime import datetime, timezone
from typing import List, Optional, Tuple
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from core.exceptions import BusinessLogicError, NotFoundError, PermissionDeniedError
from core.logging import get_logger
from modules.bookings.domain.models import Booking, BookingStatus
from modules.chat.domain.models import Dialog, Message
from modules.chat.domain.schemas import (
    DialogListResponse,
    DialogSummary,
    MessageCreate,
    MessageListResponse,
    MessageResponse,
)
from modules.mentors.domain.models import Mentor
from modules.users.domain.models import Student, UserRole

logger = get_logger(__name__)

# Статусы бронирований, для которых чат остается доступным
ACTIVE_STATUSES = [
    BookingStatus.HOLD,
    BookingStatus.AWAITING_VERIFICATION,
    BookingStatus.CONFIRMED,
    BookingStatus.COMPLETED,
]


class ChatService:
    """Высокоуровневый сервис для диалогов и сообщений."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def list_user_dialogs(
        self,
        user_id: UUID,
        user_role: UserRole,
    ) -> DialogListResponse:
        """Получение диалогов, доступных пользователю."""
        bookings = await self._load_user_bookings(user_id, user_role)
        summaries: List[DialogSummary] = []

        for booking in bookings:
            dialog = booking.dialog
            if dialog is None:
                dialog = await self._create_dialog_for_booking(booking)

            summary = await self._build_dialog_summary(dialog, booking, current_user_id=user_id)
            summaries.append(summary)

        summaries.sort(
            key=lambda d: d.last_message_at or datetime.min.replace(tzinfo=timezone.utc),
            reverse=True
        )
        return DialogListResponse(dialogs=summaries)

    async def get_dialog_messages(
        self,
        dialog_id: UUID,
        user_id: UUID,
        user_role: UserRole,
    ) -> MessageListResponse:
        """Получение сообщений конкретного диалога."""
        dialog, booking = await self._get_dialog_with_booking(dialog_id)

        if not self._user_can_access_dialog(dialog, booking, user_id, user_role):
            raise PermissionDeniedError("Недостаточно прав для доступа к диалогу")

        messages_stmt = (
            select(Message)
            .where(Message.dialog_id == dialog_id)
            .order_by(Message.created_at.asc())
        )
        messages_result = await self.db.execute(messages_stmt)
        messages = messages_result.scalars().all()

        message_responses = [
            self._build_message_response(message, current_user_id=user_id)
            for message in messages
        ]

        # Помечаем сообщения как прочитанные
        await self._mark_messages_as_read(dialog.id, user_id)

        dialog_summary = await self._build_dialog_summary(dialog, booking, current_user_id=user_id)
        return MessageListResponse(dialog=dialog_summary, messages=message_responses)

    async def send_message(
        self,
        dialog_id: UUID,
        user_id: UUID,
        user_role: UserRole,
        data: MessageCreate,
    ) -> MessageResponse:
        """Отправка сообщения в диалоге."""
        dialog, booking = await self._get_dialog_with_booking(dialog_id)

        if not self._user_can_access_dialog(dialog, booking, user_id, user_role):
            raise PermissionDeniedError("Недостаточно прав для отправки сообщения")

        text = data.text.strip()
        if not text:
            raise BusinessLogicError("Текст сообщения не может быть пустым")

        message = Message(
            dialog_id=dialog.id,
            sender_id=user_id,
            text=text,
            is_read=False,
        )

        self.db.add(message)
        await self.db.commit()
        await self.db.refresh(message)

        logger.info(
            "Chat message created",
            dialog_id=str(dialog.id),
            booking_id=str(dialog.booking_id),
            sender_id=str(user_id),
        )

        return self._build_message_response(message, current_user_id=user_id)

    async def _load_user_bookings(
        self,
        user_id: UUID,
        role: UserRole,
    ) -> List[Booking]:
        """Загрузка бронирований пользователя вместе с диалогами и участниками."""
        stmt = (
            select(Booking)
            .options(
                selectinload(Booking.dialog).selectinload(Dialog.messages),
                selectinload(Booking.student).selectinload(Student.user),
                selectinload(Booking.mentor).selectinload(Mentor.user),
            )
            .where(Booking.status.in_(ACTIVE_STATUSES))
            .order_by(Booking.created_at.desc())
        )

        if role == UserRole.STUDENT:
            stmt = stmt.where(Booking.student_id == user_id)
        elif role == UserRole.MENTOR:
            stmt = stmt.where(Booking.mentor_id == user_id)
        # Для админа оставляем все актуальные бронирования

        result = await self.db.execute(stmt)
        bookings = result.scalars().unique().all()
        return bookings

    async def _create_dialog_for_booking(self, booking: Booking) -> Dialog:
        """Создание диалога, если он отсутствует для бронирования."""
        dialog = Dialog(booking_id=booking.id)
        self.db.add(dialog)
        await self.db.commit()
        await self.db.refresh(dialog)
        booking.dialog = dialog
        return dialog

    async def _get_dialog_with_booking(self, dialog_id: UUID) -> Tuple[Dialog, Booking]:
        """Получение диалога вместе с бронированием и участниками."""
        stmt = (
            select(Dialog)
            .where(Dialog.id == dialog_id)
            .options(
                selectinload(Dialog.booking)
                .selectinload(Booking.student)
                .selectinload(Student.user),
                selectinload(Dialog.booking)
                .selectinload(Booking.mentor)
                .selectinload(Mentor.user),
            )
        )
        result = await self.db.execute(stmt)
        dialog = result.scalar_one_or_none()

        if dialog is None:
            raise NotFoundError("Dialog", str(dialog_id))

        booking = dialog.booking
        if booking is None:
            raise NotFoundError("Booking", "Не найдено бронирование для диалога")

        return dialog, booking

    async def _mark_messages_as_read(self, dialog_id: UUID, user_id: UUID) -> None:
        """Пометка сообщений в диалоге как прочитанных для пользователя."""
        await self.db.execute(
            Message.__table__
            .update()
            .where(
                (Message.dialog_id == dialog_id)
                & (Message.sender_id != user_id)
                & (Message.is_read.is_(False))
            )
            .values(is_read=True)
        )
        await self.db.commit()

    def _user_can_access_dialog(
        self,
        dialog: Dialog,
        booking: Booking,
        user_id: UUID,
        user_role: UserRole,
    ) -> bool:
        """Проверка, может ли пользователь взаимодействовать с диалогом."""
        if user_role == UserRole.ADMIN:
            return True
        return user_id in (booking.student_id, booking.mentor_id)

    async def _build_dialog_summary(
        self,
        dialog: Dialog,
        booking: Booking,
        current_user_id: UUID,
    ) -> DialogSummary:
        """Сбор сводной информации по диалогу."""
        student_name = (
            booking.student.user.name if booking.student and booking.student.user else None
        )
        mentor_name = (
            booking.mentor.user.name if booking.mentor and booking.mentor.user else None
        )

        last_message_stmt = (
            select(Message)
            .where(Message.dialog_id == dialog.id)
            .order_by(Message.created_at.desc())
            .limit(1)
        )
        last_message = (await self.db.execute(last_message_stmt)).scalar_one_or_none()

        last_message_preview: Optional[str] = None
        last_message_at: Optional[datetime] = None
        if last_message:
            last_message_preview = last_message.text or "[Вложение]"
            last_message_at = last_message.created_at

        unread_count_stmt = (
            select(func.count(Message.id))
            .where(
                Message.dialog_id == dialog.id,
                Message.sender_id != current_user_id,
                Message.is_read.is_(False),
            )
        )
        unread_count = (await self.db.execute(unread_count_stmt)).scalar_one()

        return DialogSummary(
            id=dialog.id,
            booking_id=booking.id,
            student_id=booking.student_id,
            student_name=student_name,
            mentor_id=booking.mentor_id,
            mentor_name=mentor_name,
            last_message_preview=last_message_preview,
            last_message_at=last_message_at,
            unread_count=unread_count or 0,
        )

    def _build_message_response(
        self,
        message: Message,
        current_user_id: UUID,
    ) -> MessageResponse:
        """Преобразование модели сообщения в ответ."""
        return MessageResponse(
            id=message.id,
            dialog_id=message.dialog_id,
            sender_id=message.sender_id,
            text=message.text,
            file_url=message.file_url,
            is_read=message.is_read,
            created_at=message.created_at,
            is_own=message.sender_id == current_user_id,
        )



