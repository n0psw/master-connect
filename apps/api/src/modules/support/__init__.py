"""
Модуль поддержки.
"""
from modules.support.domain.models import SupportTicket, TicketStatus
from modules.support.api.routes import router

__all__ = ["SupportTicket", "TicketStatus", "router"]

