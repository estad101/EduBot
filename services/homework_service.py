"""
Homework service - handles homework submissions.
"""
from sqlalchemy.orm import Session
from models.homework import Homework, SubmissionType, PaymentType
from models.student import Student
from utils.logger import get_logger

logger = get_logger("homework_service")


class HomeworkService:
    """Service for homework operations."""

    @staticmethod
    def submit_homework(
        db: Session,
        student_id: int,
        subject: str,
        submission_type: str,
        content: str | None = None,
        file_path: str | None = None,
        payment_type: str = "ONE_TIME",
        payment_id: int | None = None,
    ) -> Homework:
        """
        Submit homework.
        
        Args:
            db: Database session
            student_id: Student ID
            subject: Subject/topic
            submission_type: TEXT or IMAGE
            content: Text content (for TEXT submissions)
            file_path: File path (for IMAGE submissions)
            payment_type: ONE_TIME or SUBSCRIPTION
            payment_id: Payment ID (for one-time payments)
        
        Returns:
            Created Homework object
        
        Raises:
            ValueError: If validation fails
        """
        # Validate student exists
        student = db.query(Student).filter(Student.id == student_id).first()
        if not student:
            raise ValueError(f"Student {student_id} not found")

        # Validate submission type
        if submission_type.upper() not in ["TEXT", "IMAGE"]:
            raise ValueError("Submission type must be TEXT or IMAGE")

        # Validate content based on type
        if submission_type.upper() == "TEXT":
            if not content or len(content.strip()) == 0:
                raise ValueError("Content required for TEXT submissions")
        elif submission_type.upper() == "IMAGE":
            if not file_path:
                raise ValueError("File path required for IMAGE submissions")

        # Create homework record
        homework = Homework(
            student_id=student_id,
            subject=subject,
            submission_type=SubmissionType[submission_type.upper()],
            content=content,
            file_path=file_path,
            payment_type=PaymentType[payment_type.upper()],
            payment_id=payment_id,
        )

        db.add(homework)
        db.commit()
        db.refresh(homework)

        logger.info(
            f"Homework submitted: {homework.id} by student {student_id} "
            f"({submission_type}) - {subject}"
        )

        return homework

    @staticmethod
    def get_homework_by_id(db: Session, homework_id: int) -> Homework | None:
        """Get homework by ID."""
        return db.query(Homework).filter(Homework.id == homework_id).first()

    @staticmethod
    def get_student_homeworks(
        db: Session, student_id: int, limit: int = 50, offset: int = 0
    ) -> list[Homework]:
        """
        Get student's homework submissions.
        
        Args:
            db: Database session
            student_id: Student ID
            limit: Max results
            offset: Pagination offset
        
        Returns:
            List of Homework objects
        """
        return (
            db.query(Homework)
            .filter(Homework.student_id == student_id)
            .order_by(Homework.created_at.desc())
            .limit(limit)
            .offset(offset)
            .all()
        )

    @staticmethod
    def get_student_homework_count(db: Session, student_id: int) -> int:
        """Get count of student's homeworks."""
        return db.query(Homework).filter(Homework.student_id == student_id).count()
