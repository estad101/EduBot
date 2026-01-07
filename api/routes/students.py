"""
Student registration endpoint.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from schemas.student import StudentRegistrationRequest
from schemas.response import StudentRegistrationResponse, StandardResponse
from services.student_service import StudentService
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
