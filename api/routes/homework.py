"""
Homework submission endpoint.
"""
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
import os
import time
from schemas.homework import HomeworkSubmissionRequest
from schemas.response import HomeworkSubmissionResponse, StandardResponse
from services.homework_service import HomeworkService
from services.student_service import StudentService
from services.payment_service import PaymentService
from services.paystack_service import PaystackService
from services.tutor_service import TutorService
from services.whatsapp_service import WhatsAppService
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


@router.post("/upload-image")
async def upload_homework_image(
    file: UploadFile = File(...),
    student_id: int = Form(...),
    homework_id: int = Form(...),
    token: str = Form(...),
    db: Session = Depends(get_db)
):
    """
    Upload homework image from the mobile upload page.
    
    This endpoint is called when user uploads image from the homework-upload.tsx page.
    
    - Validates token (security check)
    - Saves image to disk with proper directory structure
    - Updates homework record with file path
    - Marks homework as submitted
    - Sends WhatsApp confirmation
    """
    try:
        logger.info(f"📸 Image upload request: homework_id={homework_id}, student_id={student_id}")
        
        # Get the homework record
        from models.homework import Homework
        homework = db.query(Homework).filter(Homework.id == homework_id).first()
        
        if not homework:
            logger.warning(f"❌ Homework {homework_id} not found")
            return {
                "status": "error",
                "error": f"Homework {homework_id} not found"
            }
        
        # Verify student_id matches
        if homework.student_id != student_id:
            logger.warning(f"❌ Student ID mismatch: homework.student_id={homework.student_id}, request.student_id={student_id}")
            return {
                "status": "error",
                "error": "Student ID mismatch"
            }
        
        # Get student details
        student = db.query(StudentService.__self__ if hasattr(StudentService, '__self__') else StudentService).filter(
            StudentService.__dict__.get('id') == student_id
        ).first() if hasattr(StudentService, 'query') else None
        
        # Try a simpler approach to get student
        from models.student import Student
        student = db.query(Student).filter(Student.id == student_id).first()
        
        if not student:
            logger.warning(f"❌ Student {student_id} not found")
            return {
                "status": "error",
                "error": f"Student {student_id} not found"
            }
        
        logger.info(f"   Student: {student.full_name} ({student.phone_number})")
        
        # Validate file
        if not file.filename:
            return {
                "status": "error",
                "error": "No filename provided"
            }
        
        # Check file type
        if not file.content_type or not file.content_type.startswith('image/'):
            return {
                "status": "error",
                "error": "File must be an image"
            }
        
        # Read file content
        content = await file.read()
        logger.info(f"   File size: {len(content)} bytes")
        
        # Determine upload directory
        railway_uploads = "/app/uploads/homework"
        local_uploads = "uploads/homework"
        upload_dir = railway_uploads if os.path.exists("/app/uploads") else local_uploads
        
        # Create student directory
        student_dir = os.path.join(upload_dir, str(student.id))
        os.makedirs(student_dir, exist_ok=True)
        logger.info(f"   Upload dir: {student_dir}")
        
        # Create unique filename
        timestamp = int(time.time() * 1000)
        extension = os.path.splitext(file.filename)[1] or '.jpg'
        filename = f"homework_{timestamp}{extension}"
        file_path = os.path.join(student_dir, filename)
        
        # Ensure absolute path
        file_path = os.path.abspath(file_path)
        
        # Save file
        logger.info(f"   Saving to: {file_path}")
        with open(file_path, "wb") as f:
            f.write(content)
        
        # Verify file was saved
        if not os.path.exists(file_path):
            logger.error(f"❌ Failed to save file")
            return {
                "status": "error",
                "error": "Failed to save image file"
            }
        
        actual_size = os.path.getsize(file_path)
        logger.info(f"✓ Image saved: {actual_size} bytes")
        
        # Store relative path for database
        path_parts = file_path.replace('\\', '/').split('/')
        relative_path = "{}/{}".format(path_parts[-2], path_parts[-1])
        logger.info(f"   Database path: {relative_path}")
        
        # Update homework record
        homework.file_path = relative_path
        homework.submission_type = homework.submission_type  # Keep existing type (should be IMAGE)
        homework.content = f"Image submission uploaded"
        db.commit()
        db.refresh(homework)
        
        logger.info(f"✅ Homework updated: {homework.id}")
        
        # Auto-assign to tutor
        try:
            assignment = TutorService.assign_homework_by_subject(db, homework.id)
            logger.info(f"   Tutor assigned: {assignment.tutor_id if assignment else 'None'}")
        except Exception as e:
            logger.warning(f"   Could not auto-assign tutor: {str(e)}")
        
        # Send WhatsApp confirmation
        try:
            subject = homework.subject
            confirmation_message = (
                f"✅ Homework Submitted!\n\n"
                f"📚 Subject: {subject}\n"
                f"📷 Type: Image\n"
                f"⏱️ Submitted: {homework.created_at.strftime('%b %d, %I:%M %p')}\n\n"
                f"🎓 A tutor will review your work shortly!"
            )
            
            await WhatsAppService.send_message(
                phone_number=student.phone_number,
                message=confirmation_message
            )
            logger.info(f"✓ WhatsApp confirmation sent to {student.phone_number}")
        except Exception as e:
            logger.warning(f"⚠️ Could not send WhatsApp confirmation: {str(e)}")
        
        return {
            "status": "success",
            "message": "Image uploaded successfully",
            "homework_id": homework.id,
            "file_path": relative_path
        }
        
    except Exception as e:
        logger.error(f"❌ Error uploading image: {str(e)}")
        import traceback
        logger.error(f"   Traceback: {traceback.format_exc()}")
        return {
            "status": "error",
            "error": f"Upload failed: {str(e)}"
        }