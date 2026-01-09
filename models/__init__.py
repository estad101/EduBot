"""Models package - import all models here to register with SQLAlchemy."""
# Note: Import models only during database initialization to avoid circular imports
# Don't import them at module load time

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

