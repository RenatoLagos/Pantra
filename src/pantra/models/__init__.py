"""SQLAlchemy ORM models.

Importing this package registers every table on `Base.metadata`, which is
what Alembic autogenerate scans.
"""
from pantra.models.ai_run import AIRun
from pantra.models.base import Base, TimestampMixin, UUIDPK
from pantra.models.booking import Booking, BookingStatus
from pantra.models.business import Business, BusinessDomain
from pantra.models.channel import Channel, ChannelStatus, ChannelType
from pantra.models.conversation import Conversation, ConversationStatus, Message, MessageSender
from pantra.models.customer import Customer
from pantra.models.handoff import HandoffStatus, HandoffTask
from pantra.models.idempotency import ToolIdempotency
from pantra.models.knowledge import KnowledgeCategory, KnowledgeEntry
from pantra.models.lead import Lead, LeadStatus
from pantra.models.practitioner import Practitioner
from pantra.models.schedule import PractitionerSchedule
from pantra.models.service import Service

__all__ = [
    "AIRun",
    "Base",
    "Booking",
    "BookingStatus",
    "Business",
    "BusinessDomain",
    "Channel",
    "ChannelStatus",
    "ChannelType",
    "Conversation",
    "ConversationStatus",
    "Customer",
    "HandoffStatus",
    "HandoffTask",
    "KnowledgeCategory",
    "KnowledgeEntry",
    "Lead",
    "LeadStatus",
    "Message",
    "MessageSender",
    "Practitioner",
    "PractitionerSchedule",
    "Service",
    "TimestampMixin",
    "ToolIdempotency",
    "UUIDPK",
]
