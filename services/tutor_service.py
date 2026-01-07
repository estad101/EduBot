"""
Tutor service - handles tutor operations and homework assignments.
"""
from sqlalchemy.orm import Session
from sqlalchemy import and_, func
from models.tutor import Tutor
from models.tutor_assignment import TutorAssignment, AssignmentStatus, TutorSolution
from models.homework import Homework, HomeworkStatus
from utils.logger import get_logger
from typing import Optional, List

logger = get_logger("tutor_service")


class TutorService:
    """Service for tutor operations."""

    @staticmethod
    def create_tutor(
        db: Session,
        full_name: str,
        email: str,
        phone_number: str,
        subjects: List[str],
        bio: str = None,
    ) -> Tutor:
        """
        Create a new tutor.
        
        Args:
            db: Database session
            full_name: Tutor's full name
            email: Email address
            phone_number: WhatsApp phone number
            subjects: List of subject specializations
            bio: Short biography
        
        Returns:
            Created Tutor object
        
        Raises:
            ValueError: If tutor already exists
        """
        # Check if tutor exists
        existing = db.query(Tutor).filter(
            (Tutor.email == email) | (Tutor.phone_number == phone_number)
        ).first()
        
        if existing:
            raise ValueError(f"Tutor with email {email} or phone {phone_number} already exists")

        tutor = Tutor(
            full_name=full_name,
            email=email,
            phone_number=phone_number,
            subjects=subjects,
            bio=bio,
            is_active=True,
        )

        db.add(tutor)
        db.commit()
        db.refresh(tutor)

        logger.info(f"Tutor created: {tutor.id} - {full_name} ({', '.join(subjects)})")
        return tutor

    @staticmethod
    def get_tutor_by_id(db: Session, tutor_id: int) -> Optional[Tutor]:
        """Get tutor by ID."""
        return db.query(Tutor).filter(Tutor.id == tutor_id).first()

    @staticmethod
    def get_tutor_by_email(db: Session, email: str) -> Optional[Tutor]:
        """Get tutor by email."""
        return db.query(Tutor).filter(Tutor.email == email).first()

    @staticmethod
    def get_tutor_by_phone(db: Session, phone_number: str) -> Optional[Tutor]:
        """Get tutor by phone number."""
        return db.query(Tutor).filter(Tutor.phone_number == phone_number).first()

    @staticmethod
    def get_available_tutors_for_subject(
        db: Session,
        subject: str,
        limit: int = 5,
    ) -> List[Tutor]:
        """
        Get available tutors for a subject.
        
        Looks for active tutors who specialize in the subject and
        have fewer than 5 active assignments.
        
        Args:
            db: Database session
            subject: Subject to find tutors for
            limit: Maximum number of tutors to return
        
        Returns:
            List of available Tutor objects
        """
        from sqlalchemy import func
        
        # Get active tutors with this subject
        tutors = db.query(Tutor).filter(
            Tutor.is_active == True,
            Tutor.subjects.contains([subject])  # JSON contains check
        ).all()

        # Filter by workload - tutors with < 5 active assignments
        available = []
        for tutor in tutors:
            active_count = db.query(TutorAssignment).filter(
                and_(
                    TutorAssignment.tutor_id == tutor.id,
                    TutorAssignment.status.in_([AssignmentStatus.PENDING, AssignmentStatus.IN_PROGRESS])
                )
            ).count()

            if active_count < 5:
                available.append(tutor)

        return available[:limit]

    @staticmethod
    def assign_homework_to_tutor(
        db: Session,
        homework_id: int,
        tutor_id: int,
    ) -> TutorAssignment:
        """
        Assign homework to a tutor.
        
        Args:
            db: Database session
            homework_id: Homework ID to assign
            tutor_id: Tutor ID to assign to
        
        Returns:
            Created TutorAssignment object
        
        Raises:
            ValueError: If homework or tutor not found
        """
        # Check homework exists
        homework = db.query(Homework).filter(Homework.id == homework_id).first()
        if not homework:
            raise ValueError(f"Homework {homework_id} not found")

        # Check tutor exists
        tutor = db.query(Tutor).filter(Tutor.id == tutor_id).first()
        if not tutor:
            raise ValueError(f"Tutor {tutor_id} not found")

        # Create assignment
        assignment = TutorAssignment(
            homework_id=homework_id,
            tutor_id=tutor_id,
            status=AssignmentStatus.ASSIGNED,
        )

        # Update homework status
        homework.status = HomeworkStatus.ASSIGNED
        homework.assigned_tutor_id = tutor_id

        db.add(assignment)
        db.commit()
        db.refresh(assignment)

        logger.info(f"Homework {homework_id} assigned to tutor {tutor_id}")
        return assignment

    @staticmethod
    def assign_homework_by_subject(
        db: Session,
        homework_id: int,
    ) -> Optional[TutorAssignment]:
        """
        Auto-assign homework to best available tutor for subject.
        
        Args:
            db: Database session
            homework_id: Homework ID to assign
        
        Returns:
            TutorAssignment object if successful, None if no tutors available
        
        Raises:
            ValueError: If homework not found
        """
        # Get homework
        homework = db.query(Homework).filter(Homework.id == homework_id).first()
        if not homework:
            raise ValueError(f"Homework {homework_id} not found")

        # Find available tutors for subject
        available_tutors = TutorService.get_available_tutors_for_subject(
            db, homework.subject, limit=1
        )

        if not available_tutors:
            logger.warning(f"No available tutors for subject: {homework.subject}")
            return None

        tutor = available_tutors[0]
        assignment = TutorService.assign_homework_to_tutor(
            db, homework_id, tutor.id
        )

        return assignment

    @staticmethod
    def submit_solution(
        db: Session,
        assignment_id: int,
        solution_text: Optional[str] = None,
        solution_file_path: Optional[str] = None,
        video_url: Optional[str] = None,
    ) -> TutorSolution:
        """
        Submit a solution for assigned homework.
        
        Args:
            db: Database session
            assignment_id: Assignment ID
            solution_text: Text explanation
            solution_file_path: Path to solution document/image
            video_url: URL to video walkthrough
        
        Returns:
            Created TutorSolution object
        
        Raises:
            ValueError: If assignment not found
        """
        # Get assignment
        assignment = db.query(TutorAssignment).filter(
            TutorAssignment.id == assignment_id
        ).first()
        
        if not assignment:
            raise ValueError(f"Assignment {assignment_id} not found")

        # Create solution
        solution = TutorSolution(
            assignment_id=assignment_id,
            tutor_id=assignment.tutor_id,
            solution_text=solution_text,
            solution_file_path=solution_file_path,
            is_walkthrough_video=bool(video_url),
            video_url=video_url,
        )

        # Update assignment status
        assignment.status = AssignmentStatus.COMPLETED

        # Update homework status
        homework = assignment.homework
        homework.status = HomeworkStatus.SOLVED

        db.add(solution)
        db.commit()
        db.refresh(solution)

        logger.info(
            f"Solution submitted for assignment {assignment_id} "
            f"by tutor {assignment.tutor_id}"
        )

        return solution

    @staticmethod
    def get_assignment_by_id(db: Session, assignment_id: int) -> Optional[TutorAssignment]:
        """Get assignment by ID."""
        return db.query(TutorAssignment).filter(
            TutorAssignment.id == assignment_id
        ).first()

    @staticmethod
    def get_assignments_by_tutor(
        db: Session,
        tutor_id: int,
        status: Optional[AssignmentStatus] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> List[TutorAssignment]:
        """
        Get assignments for a tutor.
        
        Args:
            db: Database session
            tutor_id: Tutor ID
            status: Optional status filter
            limit: Max results
            offset: Pagination offset
        
        Returns:
            List of TutorAssignment objects
        """
        query = db.query(TutorAssignment).filter(
            TutorAssignment.tutor_id == tutor_id
        )

        if status:
            query = query.filter(TutorAssignment.status == status)

        return query.offset(offset).limit(limit).all()

    @staticmethod
    def get_assignments_by_homework(
        db: Session,
        homework_id: int,
    ) -> List[TutorAssignment]:
        """Get all assignments for a homework."""
        return db.query(TutorAssignment).filter(
            TutorAssignment.homework_id == homework_id
        ).all()

    @staticmethod
    def deactivate_tutor(db: Session, tutor_id: int) -> Tutor:
        """Deactivate a tutor."""
        tutor = TutorService.get_tutor_by_id(db, tutor_id)
        if not tutor:
            raise ValueError(f"Tutor {tutor_id} not found")

        tutor.is_active = False
        db.commit()
        db.refresh(tutor)

        logger.info(f"Tutor deactivated: {tutor_id}")
        return tutor

    @staticmethod
    def update_tutor_subjects(
        db: Session,
        tutor_id: int,
        subjects: List[str],
    ) -> Tutor:
        """Update tutor's subject specializations."""
        tutor = TutorService.get_tutor_by_id(db, tutor_id)
        if not tutor:
            raise ValueError(f"Tutor {tutor_id} not found")

        tutor.subjects = subjects
        db.commit()
        db.refresh(tutor)

        logger.info(f"Tutor {tutor_id} subjects updated: {', '.join(subjects)}")
        return tutor
