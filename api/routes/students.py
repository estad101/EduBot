"""
Student registration endpoint.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from schemas.student import StudentRegistrationRequest
from schemas.response import StudentRegistrationResponse, StandardResponse
from services.student_service import StudentService
from services.lead_service import LeadService
from config.database import get_db
from utils.logger import get_logger

router = APIRouter(prefix="/api/students", tags=["students"])
logger = get_logger("students_route")


@router.post("/register", response_model=StandardResponse)
async def register_student(
    request: StudentRegistrationRequest, db: Session = Depends(get_db)
):
    """
    Register a new student.
    
    Called during onboarding for new users. Phone number must be unique.
    
    Request:
        {
            "phone_number": "+234901234567",
            "full_name": "John Doe",
            "email": "john@example.com",
            "class_grade": "10A"
        }
    
    Response:
        {
            "status": "success",
            "message": "Student registered successfully",
            "data": {
                "student_id": 1,
                "phone_number": "+234901234567",
                "full_name": "John Doe",
                "email": "john@example.com",
                "class_grade": "10A",
                "user_status": "REGISTERED_FREE"
            }
        }
    """
    try:
        # Check if student already exists
        existing = StudentService.get_student_by_phone(db, request.phone_number)
        if existing:
            logger.warning(f"Duplicate registration attempt: {request.phone_number}")
            return StandardResponse(
                status="validation_error",
                message="Student with this phone number already exists",
                error_code="STUDENT_EXISTS",
            )

        # Register student
        student = StudentService.register_student(
            db,
            phone_number=request.phone_number,
            full_name=request.full_name,
            email=request.email,
            class_grade=request.class_grade,
        )

        logger.info(f"Student registered: {student.id} - {student.phone_number}")

        # Mark the lead as converted to student
        try:
            LeadService.convert_lead_to_student(
                db, 
                phone_number=request.phone_number, 
                student_id=student.id
            )
            logger.info(f"Lead {request.phone_number} marked as converted to student {student.id}")
        except ValueError:
            # Lead might not exist if user registered directly without texting first
            logger.info(f"No lead found for {request.phone_number} - that's okay, direct registration")
        except Exception as e:
            logger.warning(f"Failed to mark lead as converted: {str(e)}")
            # Don't fail registration if lead conversion fails

        return StandardResponse(
            status="success",
            message="Student registered successfully",
            data={
                "student_id": student.id,
                "phone_number": student.phone_number,
                "full_name": student.full_name,
                "email": student.email,
                "class_grade": student.class_grade,
                "user_status": student.status.value,
            },
        )

    except ValueError as e:
        logger.error(f"Registration error: {str(e)}")
        return StandardResponse(
            status="error",
            message=str(e),
            error_code="REGISTRATION_ERROR",
        )
    except Exception as e:
        logger.error(f"Unexpected error during registration: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/list", response_model=StandardResponse)
async def get_all_students(db: Session = Depends(get_db)):
    """
    Get all registered students.
    
    Returns a list of all students registered in the system with their details.
    """
    try:
        from models.student import Student
        
        students = db.query(Student).all()
        
        students_data = []
        for student in students:
            students_data.append({
                "student_id": student.id,
                "phone_number": student.phone_number,
                "full_name": student.full_name,
                "email": student.email,
                "class_grade": student.class_grade,
                "status": student.status.value if student.status else "UNKNOWN",
                "has_active_subscription": student.has_active_subscription,
                "created_at": student.created_at.isoformat() if student.created_at else None,
                "last_message_at": student.last_activity_at.isoformat() if hasattr(student, 'last_activity_at') and student.last_activity_at else None,
            })
        
        logger.info(f"Retrieved {len(students)} students")
        
        return StandardResponse(
            status="success",
            message=f"Found {len(students)} registered students",
            data={"students": students_data, "total": len(students)}
        )
    except Exception as e:
        logger.error(f"Error fetching students: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stats", response_model=StandardResponse)
async def get_students_stats(db: Session = Depends(get_db)):
    """
    Get student statistics for the dashboard.
    
    Returns counts of registered, active, and subscribed students.
    """
    try:
        from models.student import Student
        from models.subscription import Subscription
        
        total_students = db.query(Student).count()
        active_subscriptions = db.query(Subscription).filter(
            Subscription.is_active == True
        ).count()
        
        # Get unique students with active subscriptions
        unique_students_with_subs = db.query(Student).filter(
            Student.has_active_subscription == True
        ).count()
        
        return StandardResponse(
            status="success",
            message="Student statistics retrieved",
            data={
                "total_registered": total_students,
                "with_active_subscription": unique_students_with_subs,
                "total_subscriptions": active_subscriptions,
            }
        )
    except Exception as e:
        logger.error(f"Error fetching stats: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))