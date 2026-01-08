"""
Homework service - handles homework submissions.
"""
from typing import Optional
from sqlalchemy.orm import Session
import os
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
        content: Optional[str] = None,
        file_path: Optional[str] = None,
        payment_type: str = "ONE_TIME",
        payment_id: Optional[int] = None,
        payment_required: bool = False,
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
            payment_required: Whether payment is required (default False)
        
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
            
            # Verify file exists - try both relative and with uploads prefix
            file_exists = os.path.exists(file_path)
            if not file_exists and not file_path.startswith('uploads/'):
                # Try with uploads prefix
                alt_path = f"uploads/{file_path}"
                file_exists = os.path.exists(alt_path)
                if file_exists:
                    logger.info(f"✓ IMAGE file found at: {alt_path}")
                    file_size = os.path.getsize(alt_path)
                    logger.info(f"  File size: {file_size} bytes")
            elif file_exists:
                file_size = os.path.getsize(file_path)
                logger.info(f"✓ IMAGE file verified: {file_path} ({file_size} bytes)")
            else:
                logger.warning(f"⚠️ IMAGE submission - file not found at: {file_path}")

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
            f"✅ Homework submitted: ID={homework.id}, Student={student_id}, "
            f"Type={submission_type}, Subject={subject}"
        )
        if file_path:
            logger.info(f"   📎 File: {file_path}")

        return homework

    @staticmethod
    def get_homework_by_id(db: Session, homework_id: int) -> Optional[Homework]:
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
