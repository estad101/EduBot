"""Models package - import all models here to register with SQLAlchemy."""
from .student import Student, UserStatus
from .lead import Lead
from .payment import Payment, PaymentStatus
from .homework import Homework, SubmissionType, PaymentType, HomeworkStatus
from .subscription import Subscription
from .tutor import Tutor
from .tutor_assignment import TutorAssignment, TutorSolution, AssignmentStatus
from .settings import AdminSetting
from .support_ticket import SupportTicket, TicketStatus, TicketPriority

__all__ = [
    "Student",
    "UserStatus",
    "Lead",
    "Payment",
    "PaymentStatus",
    "Homework",
    "SubmissionType",
    "PaymentType",
    "HomeworkStatus",
    "Subscription",
    "Tutor",
    "TutorAssignment",
    "TutorSolution",
    "AssignmentStatus",
    "AdminSetting",
    "SupportTicket",
    "TicketStatus",
    "TicketPriority",
]
