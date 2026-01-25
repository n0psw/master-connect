"""
Агрегирующий импорт всех моделей, чтобы SQLAlchemy успел зарегистрировать их
до configure_mappers()/create_all(). Импорты здесь важны как побочный эффект.
"""

# Базовые/пользователи/аутентификация
from modules.users.domain.models import User, Student  # noqa: F401
from modules.auth.domain.models import RefreshToken  # noqa: F401

# Менторы и сопутствующие
from modules.mentors.domain.models import Mentor, MentorUniversity  # noqa: F401

# Доступность
from modules.availability.domain.models import AvailabilityRule, TimeOff, MentorSettings  # noqa: F401

# Бронирования и сопряженные сущности
from modules.bookings.domain.models import Booking  # noqa: F401
from modules.bookings.domain.models import BookingRequest  # noqa: F401
from modules.reviews.domain.models import Review  # noqa: F401
from modules.chat.domain.models import Dialog, Message  # noqa: F401
from modules.payments.domain.models import PaymentEvidence  # noqa: F401

# Поддержка/админ
from modules.support.domain.models import SupportTicket  # noqa: F401
from modules.admin.domain.models import AuditLog  # noqa: F401

# Уведомления
from modules.notifications.domain.models import Notification  # noqa: F401



