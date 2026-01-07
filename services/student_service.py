"""
Student service - handles student registration and identification.
"""
from typing import Optional
from sqlalchemy.orm import Session
from models.student import Student, UserStatus
from utils.logger import get_logger

logger = get_logger("student_service")


class StudentService:
    """Service for student operations."""

    @staticmethod
    def identify_user(db: Session, phone_number: str) -> dict:
        """
        Identify user by phone number.
        
        Args:
            db: Database session
            phone_number: WhatsApp phone number
        
        Returns:
            Dictionary with user info or None if not found
        """
        student = db.query(Student).filter(
            Student.phone_number == phone_number
        ).first()

        if not student:
            return {
                "status": "NEW_USER",
                "student_id": None,
                "phone_number": phone_number,
                "user_status": None,
                "name": None,
                "email": None,
                "has_active_subscription": False,
            }

        # Check if has active subscription
        has_active = StudentService.has_active_subscription(db, student.id)

        return {
            "status": "RETURNING_USER",
            "student_id": student.id,
            "phone_number": student.phone_number,
            "user_status": student.status.value,
            "name": student.full_name,
            "email": student.email,
            "has_active_subscription": has_active,
        }

    @staticmethod
    def register_student(
        db: Session, phone_number: str, full_name: str, email: str, class_grade: str
    ) -> Student:
        """
        Register a new student.
        
        Args:
            db: Database session
            phone_number: WhatsApp phone number
            full_name: Student's full name
            email: Email address
            class_grade: Class/grade level
        
        Returns:
            Created Student object
        
        Raises:
            ValueError: If student already exists
        """
        # Check if student already exists
        existing = db.query(Student).filter(Student.phone_number == phone_number).first()
        if existing:
            raise ValueError(f"Student with phone number {phone_number} already exists")

        # Create new student
        student = Student(
            phone_number=phone_number,
            full_name=full_name,
            email=email,
            class_grade=class_grade,
            status=UserStatus.REGISTERED_FREE,
            is_active=True,
        )

        db.add(student)
        db.commit()
        db.refresh(student)

        logger.info(f"Student registered: {student.id} - {phone_number}")
        return student

    @staticmethod
    def get_student_by_id(db: Session, student_id: int) -> Optional[Student]:
        """Get student by ID."""
        return db.query(Student).filter(Student.id == student_id).first()

    @staticmethod
    def get_student_by_phone(db: Session, phone_number: str) -> Optional[Student]:
        """Get student by phone number."""
        return db.query(Student).filter(Student.phone_number == phone_number).first()

    @staticmethod
    def has_active_subscription(db: Session, student_id: int) -> bool:
        """
        Check if student has active subscription.
        
        Args:
            db: Database session
            student_id: Student ID
        
        Returns:
            True if has valid subscription, False otherwise
        """
        from models.subscription import Subscription
        from datetime import datetime

        subscription = (
            db.query(Subscription)
            .filter(
                Subscription.student_id == student_id,
                Subscription.is_active == True,
                Subscription.end_date > datetime.utcnow(),
            )
            .first()
        )

        return subscription is not None

    @staticmethod
    def update_student_status(db: Session, student_id: int, new_status: UserStatus) -> Student:
        """Update student status."""
        student = StudentService.get_student_by_id(db, student_id)
        if not student:
            raise ValueError(f"Student {student_id} not found")

        student.status = new_status
        db.commit()
        db.refresh(student)

        logger.info(f"Student status updated: {student_id} -> {new_status.value}")
        return student
