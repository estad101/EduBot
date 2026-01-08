"""
Homework submission endpoint.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from schemas.homework import HomeworkSubmissionRequest
from schemas.response import HomeworkSubmissionResponse, StandardResponse
from services.homework_service import HomeworkService
from services.student_service import StudentService
from services.payment_service import PaymentService
from services.paystack_service import PaystackService
from config.database import get_db
from utils.logger import get_logger
from utils.validators import validate_phone_number

router = APIRouter(prefix="/api/homework", tags=["homework"])
logger = get_logger("homework_route")


@router.post("/submit", response_model=StandardResponse)
async def submit_homework(
    request: HomeworkSubmissionRequest, db: Session = Depends(get_db)
):
    """
    Submit homework assignment.
    
    Payment rules:
    - If student has active subscription: accept submission
    - If no subscription: require one-time payment
    
    Request:
        {
            "student_id": 1,
            "subject": "Mathematics",
            "submission_type": "TEXT",
            "content": "Here is my solution..."
        }
    
    Or for images:
        {
            "student_id": 1,
            "subject": "Science",
            "submission_type": "IMAGE",
            "file_path": "uploads/homework/1/diagram.jpg",
            "file_size_bytes": 250000
        }
    
    Response (if subscription active):
        {
            "status": "success",
            "message": "Homework submitted successfully",
            "data": {
                "homework_id": 1,
                "student_id": 1,
                "subject": "Mathematics",
                "submission_type": "TEXT",
                "payment_type": "SUBSCRIPTION",
                "payment_required": false
            }
        }
    
    Response (if payment required):
        {
            "status": "success",
            "message": "Payment required to submit homework",
            "data": {
                "payment_required": true,
                "authorization_url": "https://checkout.paystack.com/...",
                "payment_id": 1
            }
        }
    """
    try:
        # Validate student exists
        student = StudentService.get_student_by_id(db, request.student_id)
        if not student:
            logger.warning(f"Homework submission from unknown student: {request.student_id}")
            return StandardResponse(
                status="error",
                message="Student not found",
                error_code="STUDENT_NOT_FOUND",
            )

        # Check if student has active subscription
        has_subscription = StudentService.has_active_subscription(db, request.student_id)

        if has_subscription:
            # Accept homework with subscription
            homework = HomeworkService.submit_homework(
                db,
                student_id=request.student_id,
                subject=request.subject,
                submission_type=request.submission_type,
                content=request.content,
                file_path=request.file_path,
                payment_type="SUBSCRIPTION",
                payment_id=None,
            )

            logger.info(
                f"Homework submitted with subscription: {homework.id} - Student: {request.student_id}"
            )

            return StandardResponse(
                status="success",
                message="Homework submitted successfully",
                data={
                    "homework_id": homework.id,
                    "student_id": homework.student_id,
                    "subject": homework.subject,
                    "submission_type": homework.submission_type.value,
                    "payment_type": "SUBSCRIPTION",
                    "payment_required": False,
                },
            )

        else:
            # No subscription - require one-time payment
            # Initialize Paystack payment
            try:
                payment_data = PaystackService.initialize_payment(
                    email=student.email,
                    amount_naira=5000.0,  # Standard homework submission fee
                    metadata={
                        "student_id": request.student_id,
                        "student_name": student.full_name,
                        "submission_type": request.submission_type,
                        "subject": request.subject,
                    },
                )

                # Create payment record
                payment = PaymentService.create_payment(
                    db,
                    student_id=request.student_id,
                    amount=payment_data["amount"],
                    reference=payment_data["reference"],
                    authorization_url=payment_data["authorization_url"],
                    access_code=payment_data["access_code"],
                    is_subscription=False,
                )

                logger.info(
                    f"One-time payment initiated for homework: {payment.id} - Student: {request.student_id}"
                )

                return StandardResponse(
                    status="success",
                    message="Payment required. Complete payment to submit homework.",
                    data={
                        "payment_required": True,
                        "payment_id": payment.id,
                        "authorization_url": payment_data["authorization_url"],
                        "access_code": payment_data["access_code"],
                        "amount": payment_data["amount"],
                        "reference": payment_data["reference"],
                    },
                )

            except ValueError as e:
                logger.error(f"Payment initialization failed: {str(e)}")
                return StandardResponse(
                    status="error",
                    message=f"Failed to initiate payment: {str(e)}",
                    error_code="PAYMENT_INIT_ERROR",
                )

    except ValueError as e:
        logger.error(f"Homework submission error: {str(e)}")
        return StandardResponse(
            status="validation_error",
            message=str(e),
            error_code="VALIDATION_ERROR",
        )
    except Exception as e:
        logger.error(f"Unexpected error during homework submission: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{homework_id}/image-status")
async def check_image_status(homework_id: int, db: Session = Depends(get_db)):
    """
    Check if an image homework submission has a valid image file.
    
    Returns status of the image file for verification purposes.
    """
    import os
    
    try:
        homework = HomeworkService.get_homework_by_id(db, homework_id)
        if not homework:
            return StandardResponse(
                status="error",
                message="Homework not found",
                error_code="NOT_FOUND",
            )
        
        # Check if it's an image submission
        if homework.submission_type.value != "IMAGE":
            return StandardResponse(
                status="success",
                message="Not an image submission",
                data={
                    "homework_id": homework_id,
                    "type": homework.submission_type.value,
                    "has_file": False,
                },
            )
        
        # Check if file path exists and file is accessible
        file_path = homework.file_path
        if not file_path:
            logger.warning(f"Image submission {homework_id} has no file_path")
            return StandardResponse(
                status="success",
                message="Image submission has no file path",
                data={
                    "homework_id": homework_id,
                    "type": "IMAGE",
                    "has_file": False,
                    "file_path": None,
                },
            )
        
        # Check if file exists
        if os.path.exists(file_path):
            file_size = os.path.getsize(file_path)
            logger.info(f"✓ Image file verified for homework {homework_id}: {file_path} ({file_size} bytes)")
            return StandardResponse(
                status="success",
                message="Image file found and accessible",
                data={
                    "homework_id": homework_id,
                    "type": "IMAGE",
                    "has_file": True,
                    "file_path": file_path,
                    "file_size": file_size,
                    "file_exists": True,
                },
            )
        else:
            logger.warning(f"Image file missing for homework {homework_id}: {file_path}")
            return StandardResponse(
                status="success",
                message="Image file path recorded but file not found",
                data={
                    "homework_id": homework_id,
                    "type": "IMAGE",
                    "has_file": False,
                    "file_path": file_path,
                    "file_exists": False,
                    "status": "FILE_MISSING",
                },
            )
    
    except Exception as e:
        logger.error(f"Error checking image status: {str(e)}")
        return StandardResponse(
            status="error",
            message=f"Error checking image status: {str(e)}",
            error_code="CHECK_ERROR",
        )