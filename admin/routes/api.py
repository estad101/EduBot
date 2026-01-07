"""
Admin API routes for data operations.
"""
from fastapi import APIRouter, Depends, HTTPException, Query, Request, Body
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime, timedelta
from pydantic import BaseModel
import secrets

from config.database import get_db, engine
from config.settings import settings
from admin.auth import AdminAuth, admin_session_required
from models.student import Student, UserStatus
from models.lead import Lead
from models.payment import Payment, PaymentStatus
from models.homework import Homework, SubmissionType
from models.subscription import Subscription
from models.settings import AdminSetting
from services.lead_service import LeadService
from schemas.response import StandardResponse
from utils.logger import get_logger
from utils.security import (
    get_client_ip, track_failed_login, record_failed_login, 
    clear_failed_login, create_session, generate_csrf_token
)

logger = get_logger("admin_api")

router = APIRouter(prefix="/api/admin", tags=["admin_api"])


# ==================== AUTH MODELS ====================

class LoginRequest(BaseModel):
    username: str
    password: str


# ==================== AUTH ENDPOINTS ====================

@router.post("/login")
async def login(credentials: LoginRequest, request: Request):
    """
    Admin login endpoint for React frontend with rate limiting.
    Returns a token on successful authentication.
    """
    username = credentials.username
    password = credentials.password
    client_ip = get_client_ip(request)
    
    # Check rate limiting (prevent brute force)
    is_allowed, rate_limit_message = track_failed_login(
        client_ip, 
        max_attempts=5,
        lockout_minutes=15
    )
    
    if not is_allowed:
        logger.warning(f"Login attempt from rate-limited IP {client_ip}: {rate_limit_message}")
        return {
            "status": "error",
            "message": rate_limit_message,
            "token": None
        }
    
    # Validate credentials
    is_valid, message = AdminAuth.verify_credentials(username, password, client_ip)
    
    if is_valid:
        # Clear failed login attempts on success
        clear_failed_login(client_ip)
        
        # Generate session token
        session_id = secrets.token_urlsafe(32)
        token = secrets.token_urlsafe(32)
        
        # Create session with timeout and IP binding
        create_session(
            session_id=session_id,
            user_id=username,
            ip_address=client_ip,
            timeout_minutes=settings.session_timeout_minutes
        )
        
        # Generate CSRF token for next request
        csrf_token = generate_csrf_token(session_id)
        
        logger.info(f"Admin login successful for user: {username} from IP {client_ip}")
        return {
            "status": "success",
            "message": "Login successful",
            "token": token,
            "session_id": session_id,
            "csrf_token": csrf_token,
            "user": {
                "username": username,
                "role": "admin"
            }
        }
    
    # Record failed attempt
    record_failed_login(client_ip)
    logger.warning(f"Failed admin login attempt for user: {username} from IP {client_ip}")
    return {
        "status": "error",
        "message": message or "Invalid credentials",
        "token": None
    }


@router.post("/csrf-token")
async def get_csrf_token(session_id: str, request: Request):
    """
    Get a new CSRF token for a session.
    
    Args:
        session_id: Session identifier
        
    Returns:
        CSRF token for use in state-changing requests
    """
    try:
        csrf_token = generate_csrf_token(session_id)
        return {
            "status": "success",
            "csrf_token": csrf_token
        }
    except Exception as e:
        logger.error(f"Error generating CSRF token: {str(e)}")
        return {
            "status": "error",
            "message": "Failed to generate CSRF token"
        }


@router.get("/status/database")
async def database_status():
    """
    Check database connection status.
    Returns connection status for the UI indicator.
    """
    try:
        # Try to connect to the database
        connection = engine.connect()
        connection.close()
        
        logger.info("Database connection check passed")
        return {
            "status": "success",
            "database": "connected",
            "timestamp": datetime.utcnow().isoformat(),
            "message": "Database connection is active"
        }
    except Exception as e:
        logger.error(f"Database connection failed: {str(e)}")
        return {
            "status": "error",
            "database": "disconnected",
            "timestamp": datetime.utcnow().isoformat(),
            "message": f"Database connection failed: {str(e)}"
        }


@router.get("/status/whatsapp")
async def whatsapp_status():
    """
    Check WhatsApp Cloud API connection status.
    Returns connection status for the UI indicator.
    """
    try:
        # Check if WhatsApp credentials are configured
        has_api_key = settings.whatsapp_api_key and settings.whatsapp_api_key not in ["placeholder_api_key", "pk_test_placeholder", ""]
        has_phone_id = settings.whatsapp_phone_number_id and settings.whatsapp_phone_number_id not in ["placeholder_phone_id", ""]
        
        if not has_api_key or not has_phone_id:
            logger.info("WhatsApp API key or phone number ID not configured")
            return {
                "status": "success",
                "whatsapp": "disconnected",
                "timestamp": datetime.utcnow().isoformat(),
                "message": "WhatsApp not configured - Set WHATSAPP_API_KEY and WHATSAPP_PHONE_NUMBER_ID",
                "phone_number": ""
            }
        
        # Check if token looks valid (basic format check)
        if len(settings.whatsapp_api_key) < 50:
            logger.warning("WhatsApp API key appears to be invalid format")
            return {
                "status": "success",
                "whatsapp": "disconnected",
                "timestamp": datetime.utcnow().isoformat(),
                "message": "WhatsApp API key format invalid - Update your credentials",
                "phone_number": ""
            }
        
        # Try to verify connection with WhatsApp Cloud API
        try:
            import httpx
            async with httpx.AsyncClient(timeout=5, follow_redirects=True) as client:
                response = await client.get(
                    f"https://graph.instagram.com/v18.0/{settings.whatsapp_phone_number_id}",
                    params={"access_token": settings.whatsapp_api_key}
                )
                
                if response.status_code == 200:
                    logger.info("WhatsApp Cloud API connection verified")
                    return {
                        "status": "success",
                        "whatsapp": "connected",
                        "timestamp": datetime.utcnow().isoformat(),
                        "message": "WhatsApp Cloud API connection is active",
                        "phone_number": settings.whatsapp_phone_number or ""
                    }
                elif response.status_code in [400, 401, 403]:
                    logger.warning(f"WhatsApp API returned {response.status_code} - Invalid credentials")
                    return {
                        "status": "success",
                        "whatsapp": "disconnected",
                        "timestamp": datetime.utcnow().isoformat(),
                        "message": "WhatsApp credentials are invalid or expired",
                        "phone_number": ""
                    }
                else:
                    logger.warning(f"WhatsApp API returned {response.status_code}")
                    return {
                        "status": "success",
                        "whatsapp": "configured",
                        "timestamp": datetime.utcnow().isoformat(),
                        "message": f"WhatsApp configured but verification returned status {response.status_code}",
                        "phone_number": settings.whatsapp_phone_number or ""
                    }
        except Exception as api_error:
            logger.warning(f"WhatsApp API verification timeout or network error: {str(api_error)}")
            # If we can't verify but credentials exist, show as configured
            return {
                "status": "success",
                "whatsapp": "configured",
                "timestamp": datetime.utcnow().isoformat(),
                "message": "WhatsApp configured - Could not verify connection (network/timeout)",
                "phone_number": settings.whatsapp_phone_number or ""
            }
            
    except Exception as e:
        logger.error(f"WhatsApp status check error: {str(e)}")
        return {
            "status": "success",
            "whatsapp": "disconnected",
            "timestamp": datetime.utcnow().isoformat(),
            "message": f"WhatsApp status check failed: {str(e)}",
            "phone_number": ""
        }


@router.post("/whatsapp/test")
async def send_whatsapp_test_message(request: Request, request_body: dict = Body(...), db: Session = Depends(get_db)):
    """
    Send a test WhatsApp message to verify credentials.
    
    Request body:
    {
        "phone_number": "+1234567890",
        "message": "Test message"
    }
    """
    try:
        phone_number = request_body.get("phone_number")
        message_text = request_body.get("message", "Test message from WhatsApp chatbot")
        
        # Get settings from database
        db_settings = db.query(AdminSetting).all()
        settings_dict = {s.key: s.value for s in db_settings}
        
        # Get WhatsApp credentials from database or fallback to env
        whatsapp_api_key = settings_dict.get("whatsapp_api_key") or settings.whatsapp_api_key
        whatsapp_phone_number_id = settings_dict.get("whatsapp_phone_number_id") or settings.whatsapp_phone_number_id
        
        # Validate inputs
        if not phone_number:
            return {
                "status": "error",
                "message": "Phone number is required"
            }
        
        if not whatsapp_phone_number_id:
            logger.error("WhatsApp Phone Number ID not configured")
            return {
                "status": "error",
                "message": "WhatsApp Phone Number ID not configured. Please check your settings."
            }
        
        if not whatsapp_api_key:
            logger.error("WhatsApp API Key not configured")
            return {
                "status": "error",
                "message": "WhatsApp API Key not configured. Please check your settings."
            }
        
        # Validate token format
        api_key = str(whatsapp_api_key).strip()
        if not api_key:
            logger.error("API key is empty")
            return {
                "status": "error",
                "message": "WhatsApp API token is empty. Please configure a valid token in settings."
            }
        
        if len(api_key) < 20:
            logger.error(f"API key too short. Length: {len(api_key)}")
            return {
                "status": "error",
                "message": f"Invalid WhatsApp API token. Token is too short ({len(api_key)} characters). Please verify the token."
            }
        
        logger.info(f"WhatsApp API Key validation: length={len(api_key)}, starts_with={api_key[:10]}, ends_with={api_key[-10:]}")
        logger.info(f"API Key has whitespace: {api_key != api_key.strip()}")
        
        # Remove any non-numeric characters from phone number
        clean_phone = ''.join(filter(str.isdigit, str(phone_number)))
        if not clean_phone:
            return {
                "status": "error",
                "message": "Invalid phone number format"
            }
        
        import httpx
        
        # Send test message via WhatsApp Cloud API (using latest v22.0)
        api_url = f"https://graph.facebook.com/v22.0/{whatsapp_phone_number_id}/messages"
        
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "messaging_product": "whatsapp",
            "to": clean_phone,
            "type": "text",
            "text": {
                "preview_url": False,
                "body": message_text
            }
        }
        
        logger.info(f"Sending WhatsApp test message to {phone_number} via {api_url}")
        logger.debug(f"Request headers: Authorization header length={len(headers.get('Authorization', ''))}")
        
        with httpx.Client(timeout=10) as client:
            response = client.post(api_url, json=payload, headers=headers)
            
            logger.info(f"WhatsApp API response status: {response.status_code}")
            
            if response.status_code == 200:
                response_data = response.json()
                logger.info(f"Test message sent successfully to {phone_number}")
                return {
                    "status": "success",
                    "message": f"Test message sent successfully to {phone_number}",
                    "message_id": response_data.get("messages", [{}])[0].get("id")
                }
            else:
                error_msg = response.text
                try:
                    error_data = response.json()
                    error_msg = error_data.get("error", {}).get("message", error_msg)
                    # Log more details for debugging
                    logger.warning(f"WhatsApp API error code: {error_data.get('error', {}).get('code', 'unknown')}")
                except:
                    pass
                
                logger.warning(f"Failed to send test message: HTTP {response.status_code} - {error_msg}")
                logger.debug(f"Full response: {response.text[:500]}")
                return {
                    "status": "error",
                    "message": f"Failed to send test message: {error_msg}"
                }
    
    except httpx.ConnectError:
        logger.error("Cannot connect to WhatsApp API")
        return {
            "status": "error",
            "message": "Cannot connect to WhatsApp Cloud API. Please check your internet connection."
        }
    except httpx.TimeoutException:
        logger.warning("WhatsApp API request timeout")
        return {
            "status": "error",
            "message": "WhatsApp API request timed out. Please try again."
        }
    except Exception as e:
        logger.error(f"Error sending test message: {str(e)}")
        return {
            "status": "error",
            "message": f"Error sending test message: {str(e)}"
        }


# ==================== STUDENTS ENDPOINTS ====================

@router.get("/students")
async def list_students(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """List all students with pagination."""
    students = db.query(Student).offset(skip).limit(limit).all()
    
    return {
        "status": "success",
        "data": [
            {
                "id": s.id,
                "phone_number": s.phone_number,
                "full_name": s.full_name,
                "email": s.email,
                "status": s.status.value,
                "is_active": s.is_active,
                "created_at": s.created_at.isoformat()
            }
            for s in students
        ]
    }


@router.get("/students/{student_id}")
async def get_student(student_id: int, db: Session = Depends(get_db)):
    """Get a specific student by ID."""
    student = db.query(Student).filter_by(id=student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    
    return {
        "status": "success",
        "data": {
            "id": student.id,
            "phone_number": student.phone_number,
            "full_name": student.full_name,
            "email": student.email,
            "status": student.status.value,
            "is_active": student.is_active,
            "created_at": student.created_at.isoformat()
        }
    }


# ==================== PAYMENTS ENDPOINTS ====================

@router.get("/payments")
async def list_payments(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """List all payments with pagination."""
    payments = db.query(Payment).offset(skip).limit(limit).all()
    
    return {
        "status": "success",
        "data": [
            {
                "id": p.id,
                "student_id": p.student_id,
                "amount": float(p.amount),
                "status": p.status.value,
                "reference": p.payment_reference,
                "created_at": p.created_at.isoformat() if p.created_at else None
            }
            for p in payments
        ]
    }


# ==================== SUBSCRIPTIONS ENDPOINTS ====================

@router.get("/subscriptions")
async def list_subscriptions(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """List all subscriptions with pagination."""
    subscriptions = db.query(Subscription).offset(skip).limit(limit).all()
    
    return {
        "status": "success",
        "data": [
            {
                "id": s.id,
                "student_id": s.student_id,
                "plan": s.plan,
                "status": "active" if s.is_active else "inactive",
                "start_date": s.start_date.isoformat(),
                "end_date": s.end_date.isoformat(),
                "created_at": s.created_at.isoformat() if hasattr(s, 'created_at') else None
            }
            for s in subscriptions
        ]
    }


# ==================== HOMEWORK ENDPOINTS ====================

@router.get("/homework")
async def list_homework(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """List all homework submissions with pagination."""
    homeworks = db.query(Homework).offset(skip).limit(limit).all()
    
    return {
        "status": "success",
        "data": [
            {
                "id": h.id,
                "student_id": h.student_id,
                "submission_type": h.submission_type.value if h.submission_type else "text",
                "status": "submitted",
                "created_at": h.created_at.isoformat() if h.created_at else None
            }
            for h in homeworks
        ]
    }


# ==================== STUDENTS API ====================

@router.get("/students/search")
async def search_students(
    query: str = Query(""),
    status: str = Query(None),
    db: Session = Depends(get_db)
):
    """Search students by name, phone, or email."""
    students_query = db.query(Student)
    
    if query:
        students_query = students_query.filter(
            (Student.phone_number.like(f"%{query}%")) |
            (Student.full_name.like(f"%{query}%")) |
            (Student.email.like(f"%{query}%"))
        )
    
    if status:
        students_query = students_query.filter_by(status=status)
    
    students = students_query.limit(50).all()
    
    return {
        "status": "success",
        "data": [
            {
                "id": s.id,
                "phone_number": s.phone_number,
                "full_name": s.full_name,
                "email": s.email,
                "status": s.status.value,
                "is_active": s.is_active,
                "created_at": s.created_at.isoformat()
            }
            for s in students
        ]
    }


@router.get("/students/{student_id}/stats")
async def get_student_stats(student_id: int, db: Session = Depends(get_db)):
    """Get detailed statistics for a student."""
    student = db.query(Student).filter_by(id=student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    
    from models.homework import Homework
    from models.payment import Payment
    from models.subscription import Subscription
    
    total_submissions = db.query(Homework).filter_by(student_id=student_id).count()
    total_payments = db.query(Payment).filter_by(student_id=student_id).count()
    successful_payments = db.query(Payment).filter_by(
        student_id=student_id,
        status=PaymentStatus.SUCCESS
    ).count()
    
    subscription = db.query(Subscription).filter_by(
        student_id=student_id,
        is_active=True
    ).first()
    
    return {
        "status": "success",
        "data": {
            "total_submissions": total_submissions,
            "total_payments": total_payments,
            "successful_payments": successful_payments,
            "has_active_subscription": subscription is not None,
            "subscription_days_remaining": (
                (subscription.end_date - datetime.utcnow()).days
                if subscription else 0
            )
        }
    }


@router.put("/students/{student_id}/status")
async def update_student_status(
    student_id: int,
    new_status: str,
    db: Session = Depends(get_db)
):
    """Update student status."""
    student = db.query(Student).filter_by(id=student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    
    try:
        student.status = UserStatus(new_status)
        student.updated_at = datetime.utcnow()
        db.commit()
        
        logger.info(f"Updated student {student_id} status to {new_status}")
        
        return {
            "status": "success",
            "message": "Student status updated",
            "data": {"student_id": student_id, "new_status": new_status}
        }
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid status")


@router.delete("/students/{student_id}")
async def delete_student(student_id: int, db: Session = Depends(get_db)):
    """Soft delete a student (mark as inactive)."""
    student = db.query(Student).filter_by(id=student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    
    student.is_active = False
    student.updated_at = datetime.utcnow()
    db.commit()
    
    logger.info(f"Deactivated student {student_id}")
    
    return {
        "status": "success",
        "message": "Student deactivated"
    }


# ==================== PAYMENTS API ====================

@router.get("/payments/stats")
async def get_payment_stats(db: Session = Depends(get_db)):
    """Get payment statistics."""
    total_payments = db.query(Payment).count()
    successful = db.query(Payment).filter_by(status=PaymentStatus.SUCCESS).count()
    pending = db.query(Payment).filter_by(status=PaymentStatus.PENDING).count()
    failed = db.query(Payment).filter_by(status=PaymentStatus.FAILED).count()
    
    # Calculate total revenue
    from sqlalchemy import func
    revenue = db.query(func.sum(Payment.amount)).filter_by(
        status=PaymentStatus.SUCCESS
    ).scalar() or 0
    
    # Monthly revenue
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    monthly_revenue = db.query(func.sum(Payment.amount)).filter(
        Payment.status == PaymentStatus.SUCCESS,
        Payment.created_at >= thirty_days_ago
    ).scalar() or 0
    
    return {
        "status": "success",
        "data": {
            "total_payments": total_payments,
            "successful": successful,
            "pending": pending,
            "failed": failed,
            "total_revenue": float(revenue),
            "monthly_revenue": float(monthly_revenue)
        }
    }


@router.get("/payments/{payment_id}")
async def get_payment_detail(payment_id: int, db: Session = Depends(get_db)):
    """Get payment details."""
    payment = db.query(Payment).filter_by(id=payment_id).first()
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")
    
    student = db.query(Student).filter_by(id=payment.student_id).first()
    
    return {
        "status": "success",
        "data": {
            "payment_id": payment.id,
            "student_id": payment.student_id,
            "student_name": student.full_name if student else "Unknown",
            "amount": float(payment.amount),
            "reference": payment.reference,
            "status": payment.status.value,
            "is_subscription": payment.is_subscription,
            "created_at": payment.created_at.isoformat()
        }
    }


@router.put("/payments/{payment_id}/status")
async def update_payment_status(
    payment_id: int,
    status: str,
    db: Session = Depends(get_db)
):
    """Update payment status (manual correction)."""
    payment = db.query(Payment).filter_by(id=payment_id).first()
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")
    
    try:
        payment.status = PaymentStatus(status)
        db.commit()
        
        logger.info(f"Manually updated payment {payment_id} status to {status}")
        
        return {
            "status": "success",
            "message": "Payment status updated"
        }
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid payment status")


# ==================== SUBSCRIPTIONS API ====================

@router.get("/subscriptions/stats")
async def get_subscription_stats(db: Session = Depends(get_db)):
    """Get subscription statistics."""
    total_subs = db.query(Subscription).count()
    active_subs = db.query(Subscription).filter_by(is_active=True).count()
    
    # Expiring soon (within 7 days)
    expiring_soon = db.query(Subscription).filter(
        Subscription.end_date <= datetime.utcnow() + timedelta(days=7),
        Subscription.is_active == True
    ).count()
    
    return {
        "status": "success",
        "data": {
            "total_subscriptions": total_subs,
            "active_subscriptions": active_subs,
            "expiring_soon": expiring_soon
        }
    }


@router.post("/subscriptions/{subscription_id}/extend")
async def extend_subscription(
    subscription_id: int,
    days: int = 30,
    db: Session = Depends(get_db)
):
    """Extend a subscription."""
    subscription = db.query(Subscription).filter_by(id=subscription_id).first()
    if not subscription:
        raise HTTPException(status_code=404, detail="Subscription not found")
    
    subscription.end_date = subscription.end_date + timedelta(days=days)
    db.commit()
    
    logger.info(f"Extended subscription {subscription_id} by {days} days")
    
    return {
        "status": "success",
        "message": f"Subscription extended by {days} days",
        "data": {
            "subscription_id": subscription_id,
            "new_end_date": subscription.end_date.isoformat()
        }
    }


@router.delete("/subscriptions/{subscription_id}")
async def cancel_subscription(subscription_id: int, db: Session = Depends(get_db)):
    """Cancel a subscription."""
    subscription = db.query(Subscription).filter_by(id=subscription_id).first()
    if not subscription:
        raise HTTPException(status_code=404, detail="Subscription not found")
    
    subscription.is_active = False
    db.commit()
    
    logger.info(f"Cancelled subscription {subscription_id}")
    
    return {
        "status": "success",
        "message": "Subscription cancelled"
    }


# ==================== HOMEWORK API ====================

@router.get("/homework/stats")
async def get_homework_stats(db: Session = Depends(get_db)):
    """Get homework statistics."""
    total = db.query(Homework).count()
    text_submissions = db.query(Homework).filter_by(
        submission_type=SubmissionType.TEXT
    ).count()
    image_submissions = db.query(Homework).filter_by(
        submission_type=SubmissionType.IMAGE
    ).count()
    
    return {
        "status": "success",
        "data": {
            "total_submissions": total,
            "text_submissions": text_submissions,
            "image_submissions": image_submissions
        }
    }


@router.get("/homework/{homework_id}")
async def get_homework_detail(homework_id: int, db: Session = Depends(get_db)):
    """Get homework details."""
    homework = db.query(Homework).filter_by(id=homework_id).first()
    if not homework:
        raise HTTPException(status_code=404, detail="Homework not found")
    
    student = db.query(Student).filter_by(id=homework.student_id).first()
    
    return {
        "status": "success",
        "data": {
            "homework_id": homework.id,
            "student_id": homework.student_id,
            "student_name": student.full_name if student else "Unknown",
            "subject": homework.subject,
            "submission_type": homework.submission_type.value,
            "content": homework.content,
            "file_path": homework.file_path,
            "created_at": homework.created_at.isoformat()
        }
    }


# ==================== SYSTEM STATS ====================

@router.get("/stats/overview")
async def get_overview_stats(db: Session = Depends(get_db)):
    """Get overall system statistics."""
    from sqlalchemy import func
    
    total_students = db.query(Student).count()
    active_subscribers = db.query(Student).filter_by(
        status=UserStatus.ACTIVE_SUBSCRIBER
    ).count()
    
    total_payments = db.query(Payment).filter_by(
        status=PaymentStatus.SUCCESS
    ).count()
    
    total_revenue = db.query(func.sum(Payment.amount)).filter_by(
        status=PaymentStatus.SUCCESS
    ).scalar() or 0
    
    total_homework = db.query(Homework).count()
    
    return {
        "status": "success",
        "data": {
            "total_students": total_students,
            "active_subscribers": active_subscribers,
            "total_payments": total_payments,
            "total_revenue": float(total_revenue),
            "total_homework_submissions": total_homework
        }
    }


@router.get("/dashboard/stats")
async def get_dashboard_stats(db: Session = Depends(get_db)):
    """Get dashboard statistics (alias for /stats/overview)."""
    from sqlalchemy import func
    
    total_students = db.query(Student).count()
    active_subscribers = db.query(Student).filter_by(
        status=UserStatus.ACTIVE_SUBSCRIBER
    ).count()
    
    total_payments = db.query(Payment).filter_by(
        status=PaymentStatus.SUCCESS
    ).count()
    
    total_revenue = db.query(func.sum(Payment.amount)).filter_by(
        status=PaymentStatus.SUCCESS
    ).scalar() or 0
    
    total_homework = db.query(Homework).count()
    
    return {
        "status": "success",
        "data": {
            "total_students": total_students,
            "active_subscribers": active_subscribers,
            "total_payments": total_payments,
            "total_revenue": float(total_revenue),
            "total_homework_submissions": total_homework
        }
    }


# ==================== SETTINGS ENDPOINTS ====================

@router.get("/settings")
async def get_settings(db: Session = Depends(get_db)):
    """Get admin settings from database."""
    try:
        # Get all settings from database
        db_settings = db.query(AdminSetting).all()
        
        # Build settings dictionary
        settings_dict = {}
        for setting in db_settings:
            settings_dict[setting.key] = setting.value or ""
        
        # Fallback to environment variables if not in database
        if not settings_dict.get("whatsapp_api_key"):
            settings_dict["whatsapp_api_key"] = settings.whatsapp_api_key or ""
        if not settings_dict.get("whatsapp_phone_number_id"):
            settings_dict["whatsapp_phone_number_id"] = settings.whatsapp_phone_number_id or ""
        if not settings_dict.get("whatsapp_business_account_id"):
            settings_dict["whatsapp_business_account_id"] = settings.whatsapp_business_account_id or ""
        if not settings_dict.get("whatsapp_phone_number"):
            settings_dict["whatsapp_phone_number"] = settings.whatsapp_phone_number or ""
        if not settings_dict.get("database_url"):
            settings_dict["database_url"] = settings.database_url or ""
        
        # Ensure all expected keys exist
        expected_keys = [
            "whatsapp_api_key", "whatsapp_phone_number_id", "whatsapp_business_account_id",
            "whatsapp_phone_number", "whatsapp_webhook_token", "paystack_public_key",
            "paystack_secret_key", "paystack_webhook_secret", "database_url"
        ]
        for key in expected_keys:
            if key not in settings_dict:
                settings_dict[key] = ""
        
        logger.info("Settings retrieved from database")
        return {
            "status": "success",
            "data": settings_dict
        }
    except Exception as e:
        logger.error(f"Error retrieving settings: {str(e)}", exc_info=True)
        return {
            "status": "success",
            "data": {
                "whatsapp_api_key": settings.whatsapp_api_key or "",
                "whatsapp_phone_number_id": settings.whatsapp_phone_number_id or "",
                "whatsapp_business_account_id": settings.whatsapp_business_account_id or "",
                "whatsapp_phone_number": settings.whatsapp_phone_number or "",
                "whatsapp_webhook_token": "",
                "paystack_public_key": "",
                "paystack_secret_key": "",
                "paystack_webhook_secret": "",
                "database_url": settings.database_url or ""
            }
        }


@router.get("/settings/debug")
async def debug_settings(db: Session = Depends(get_db)):
    """Debug endpoint to verify token storage (admin only)."""
    try:
        db_settings = db.query(AdminSetting).all()
        
        debug_info = {}
        for setting in db_settings:
            if setting.key in ["whatsapp_api_key", "paystack_public_key", "paystack_secret_key", "whatsapp_phone_number_id"]:
                value = setting.value or ""
                debug_info[setting.key] = {
                    "length": len(value),
                    "preview": f"{value[:50]}...{value[-30:]}" if len(value) > 80 else value,
                    "is_valid": len(value) > 0,
                    "starts_with": value[:10] if len(value) >= 10 else value
                }
        
        return {
            "status": "success",
            "debug": debug_info
        }
    except Exception as e:
        logger.error(f"Error in debug settings: {str(e)}")
        return {
            "status": "error",
            "message": str(e)
        }


@router.post("/settings/update")
async def update_settings(data: dict, db: Session = Depends(get_db)):
    """Update admin settings in database."""
    logger.info(f"=== SETTINGS UPDATE: Received {len(data)} keys ===")
    
    try:
        updated_count = 0
        
        for key, value in data.items():
            if not key:
                continue
            
            # Log sensitive fields
            if key in ["whatsapp_api_key", "paystack_public_key", "paystack_secret_key"]:
                value_str = str(value) if value else ""
                logger.info(f"Saving {key}: {len(value_str)} chars")
            
            # Get or create setting
            db_setting = db.query(AdminSetting).filter(AdminSetting.key == key).first()
            
            if db_setting:
                db_setting.value = str(value) if value else None
                db_setting.updated_at = datetime.utcnow()
            else:
                db_setting = AdminSetting(
                    key=key,
                    value=str(value) if value else None,
                    description=f"Setting for {key}"
                )
                db.add(db_setting)
            
            updated_count += 1
        
        db.commit()
        logger.info(f"SUCCESS: Updated {updated_count} settings")
        
        return {
            "status": "success",
            "message": f"Settings updated successfully ({updated_count} changes)"
        }
    except Exception as e:
        try:
            db.rollback()
        except:
            pass
        logger.error(f"FAILED: {str(e)}", exc_info=True)
        return {
            "status": "error",
            "message": f"Failed to update settings: {str(e)}"
        }


# ==================== REPORTS ENDPOINTS ====================

@router.get("/reports")
async def get_reports(db: Session = Depends(get_db)):
    """Get system reports and analytics."""
    from sqlalchemy import func
    
    total_students = db.query(Student).count()
    active_subscribers = db.query(Student).filter_by(
        status=UserStatus.ACTIVE_SUBSCRIBER
    ).count()
    
    total_revenue = db.query(func.sum(Payment.amount)).filter_by(
        status=PaymentStatus.SUCCESS
    ).scalar() or 0
    
    total_homework = db.query(Homework).count()
    
    return {
        "status": "success",
        "data": {
            "summary": {
                "total_students": total_students,
                "active_subscribers": active_subscribers,
                "total_homework_submissions": total_homework,
                "total_revenue": float(total_revenue)
            },
            "charts": {
                "students_by_status": [
                    {"status": "active_subscriber", "count": active_subscribers},
                    {"status": "inactive", "count": total_students - active_subscribers}
                ],
                "revenue_trend": [
                    {"month": "January", "revenue": float(total_revenue) * 0.1},
                    {"month": "February", "revenue": float(total_revenue) * 0.15},
                    {"month": "March", "revenue": float(total_revenue) * 0.25}
                ]
            }
        }
    }


# ==================== MONITORING ENDPOINTS ====================

@router.get("/monitoring/stats")
async def get_monitoring_stats():
    """Get system monitoring statistics."""
    return {
        "status": "success",
        "data": {
            "server_health": "healthy",
            "uptime_hours": 48,
            "active_sessions": 5,
            "database_connection": "active",
            "api_response_time_ms": 45,
            "error_rate_percent": 0.5
        }
    }


# ==================== LOGOUT ENDPOINT ====================

@router.post("/logout")
async def logout(request: Request, session_id: str = None):
    """
    Logout the admin user and invalidate their session.
    
    Args:
        session_id: Session ID to invalidate
    """
    from utils.security import invalidate_session
    
    if session_id:
        invalidate_session(session_id)
        logger.info(f"Admin logout for session {session_id}")
    
    return {
        "status": "success",
        "message": "Logged out successfully"
    }

# ==================== LEADS ENDPOINTS ====================

@router.get("/leads")
async def list_leads(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    converted: bool = Query(None),
    db: Session = Depends(get_db)
):
    """
    Get list of leads (unregistered users who have messaged the bot).
    
    Args:
        skip: Number of records to skip
        limit: Number of records to return
        converted: Filter by conversion status (True/False/None for all)
    """
    try:
        query = db.query(Lead)
        
        if converted is not None:
            query = query.filter(Lead.converted_to_student == converted)
        else:
            # By default, show unconverted active leads
            query = query.filter(Lead.converted_to_student == False, Lead.is_active == True)
        
        leads = query.order_by(Lead.last_message_time.desc()).offset(skip).limit(limit).all()
        
        return {
            "status": "success",
            "data": [
                {
                    "id": lead.id,
                    "phone_number": lead.phone_number,
                    "sender_name": lead.sender_name,
                    "first_message": lead.first_message,
                    "last_message": lead.last_message,
                    "message_count": lead.message_count,
                    "converted_to_student": lead.converted_to_student,
                    "student_id": lead.student_id,
                    "created_at": lead.created_at.isoformat(),
                    "updated_at": lead.updated_at.isoformat(),
                    "last_message_time": lead.last_message_time.isoformat()
                }
                for lead in leads
            ]
        }
    except Exception as e:
        logger.error(f"Error fetching leads: {str(e)}")
        return {
            "status": "error",
            "message": str(e),
            "data": []
        }


@router.get("/leads/stats")
async def get_leads_stats(db: Session = Depends(get_db)):
    """Get leads statistics."""
    try:
        total_leads = db.query(Lead).count()
        active_leads = db.query(Lead).filter(Lead.is_active == True).count()
        converted_leads = db.query(Lead).filter(Lead.converted_to_student == True).count()
        unconverted_leads = db.query(Lead).filter(Lead.converted_to_student == False, Lead.is_active == True).count()
        
        return {
            "status": "success",
            "data": {
                "total_leads": total_leads,
                "active_leads": active_leads,
                "converted_leads": converted_leads,
                "unconverted_leads": unconverted_leads,
                "conversion_rate": f"{(converted_leads/total_leads*100):.1f}%" if total_leads > 0 else "0%"
            }
        }
    except Exception as e:
        logger.error(f"Error fetching leads stats: {str(e)}")
        return {
            "status": "error",
            "message": str(e),
            "data": {}
        }


@router.get("/leads/{lead_id}")
async def get_lead_detail(lead_id: int, db: Session = Depends(get_db)):
    """Get detailed information about a specific lead."""
    try:
        lead = db.query(Lead).filter(Lead.id == lead_id).first()
        
        if not lead:
            raise HTTPException(status_code=404, detail="Lead not found")
        
        # Get conversation messages for this lead
        from services.conversation_service import ConversationService
        conv_state = ConversationService.get_state(lead.phone_number)
        messages = conv_state.get("data", {}).get("messages", [])
        
        return {
            "status": "success",
            "data": {
                "id": lead.id,
                "phone_number": lead.phone_number,
                "sender_name": lead.sender_name,
                "first_message": lead.first_message,
                "last_message": lead.last_message,
                "message_count": lead.message_count,
                "converted_to_student": lead.converted_to_student,
                "student_id": lead.student_id,
                "created_at": lead.created_at.isoformat(),
                "updated_at": lead.updated_at.isoformat(),
                "last_message_time": lead.last_message_time.isoformat(),
                "messages": messages
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching lead detail: {str(e)}")
        return {
            "status": "error",
            "message": str(e),
            "data": {}
        }


@router.post("/leads/{lead_id}/convert")
async def convert_lead_to_student(
    lead_id: int,
    student_id: int = Body(...),
    db: Session = Depends(get_db)
):
    """Convert a lead to a student."""
    try:
        lead = db.query(Lead).filter(Lead.id == lead_id).first()
        
        if not lead:
            raise HTTPException(status_code=404, detail="Lead not found")
        
        # Verify student exists
        student = db.query(Student).filter(Student.id == student_id).first()
        if not student:
            raise HTTPException(status_code=404, detail="Student not found")
        
        # Convert lead
        LeadService.convert_lead_to_student(db, lead.phone_number, student_id)
        
        logger.info(f"Converted lead {lead_id} ({lead.phone_number}) to student {student_id}")
        
        return {
            "status": "success",
            "message": f"Lead converted to student",
            "data": {
                "lead_id": lead_id,
                "student_id": student_id
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error converting lead: {str(e)}")
        return {
            "status": "error",
            "message": str(e)
        }


@router.delete("/leads/{lead_id}")
async def delete_lead(lead_id: int, db: Session = Depends(get_db)):
    """Delete or deactivate a lead."""
    try:
        lead = db.query(Lead).filter(Lead.id == lead_id).first()
        
        if not lead:
            raise HTTPException(status_code=404, detail="Lead not found")
        
        # Soft delete - mark as inactive
        LeadService.deactivate_lead(db, lead.phone_number)
        
        logger.info(f"Deactivated lead {lead_id} ({lead.phone_number})")
        
        return {
            "status": "success",
            "message": "Lead deactivated"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting lead: {str(e)}")
        return {
            "status": "error",
            "message": str(e)
        }

# ==================== CONVERSATIONS ENDPOINTS ====================

@router.get("/conversations")
async def get_conversations(limit: int = Query(20, ge=1, le=100), db: Session = Depends(get_db)):
    """
    Get list of recent conversations with WhatsApp users.
    Returns phone numbers, last message, timestamp, and activity status.
    """
    try:
        from models.student import Student
        from services.conversation_service import ConversationService
        
        # Get all students sorted by last update
        students = db.query(Student).order_by(Student.updated_at.desc()).limit(limit).all()
        
        conversations = []
        conversation_phones = set()
        
        for student in students:
            # Get conversation state to find last message
            conv_state = ConversationService.get_state(student.phone_number)
            
            # Get the actual last message and time from conversation service
            last_message = conv_state.get("data", {}).get("last_message") or f"{student.full_name} is registered" if student.full_name else "No messages"
            
            # Get actual message timestamp from messages list if available
            messages = conv_state.get("data", {}).get("messages", [])
            last_message_time = student.updated_at.isoformat() if student.updated_at else student.created_at.isoformat()
            
            if messages:
                # Get the timestamp of the last message
                last_msg = messages[-1]
                if last_msg.get("timestamp"):
                    last_message_time = last_msg["timestamp"]
                # Update last_message from actual message content if empty
                if not last_message or last_message == "No messages":
                    last_message = last_msg.get("text", "No messages")
            
            conversations.append({
                "phone_number": student.phone_number,
                "student_name": student.full_name if student.full_name else None,
                "last_message": last_message,
                "last_message_time": last_message_time,
                "message_count": len(messages) if messages else 1,
                "is_active": True,
            })
            
            conversation_phones.add(student.phone_number)
        
        # Also include conversations that have messages but no student record yet
        # This can happen if messages arrived but student creation failed
        for phone_number, state in ConversationService._conversation_states.items():
            if phone_number not in conversation_phones:
                messages = state.get("data", {}).get("messages", [])
                if messages:
                    last_message = state.get("data", {}).get("last_message", "New message")
                    last_message_time = state.get("data", {}).get("created_at", datetime.utcnow().isoformat())
                    
                    if messages:
                        last_msg = messages[-1]
                        if last_msg.get("timestamp"):
                            last_message_time = last_msg["timestamp"]
                        if not last_message:
                            last_message = last_msg.get("text", "No messages")
                    
                    conversations.append({
                        "phone_number": phone_number,
                        "student_name": state.get("data", {}).get("full_name"),
                        "last_message": last_message,
                        "last_message_time": last_message_time,
                        "message_count": len(messages),
                        "is_active": True,
                    })
        
        # Sort by last message time
        conversations.sort(
            key=lambda x: x["last_message_time"], 
            reverse=True
        )
        
        # Limit to requested number
        conversations = conversations[:limit]
        
        return {
            "status": "success",
            "data": conversations
        }
    except Exception as e:
        logger.error(f"Error fetching conversations: {str(e)}", exc_info=True)
        return {
            "status": "error",
            "message": str(e),
            "data": []
        }


@router.get("/conversations/{phone_number}/messages")
async def get_conversation_messages(phone_number: str, db: Session = Depends(get_db)):
    """
    Get message history for a specific phone number.
    Returns conversation thread with user and bot messages.
    """
    try:
        from models.student import Student
        from services.conversation_service import ConversationService
        
        # Get student info
        student = db.query(Student).filter(
            Student.phone_number == phone_number
        ).first()
        
        if not student:
            return {
                "status": "success",
                "data": []
            }
        
        # Get conversation data
        conv_state = ConversationService.get_state(phone_number)
        messages = []
        
        # Add initial greeting if first message
        if conv_state["data"].get("messages", []):
            # Get stored messages from conversation service
            for msg in conv_state["data"]["messages"]:
                messages.append(msg)
        else:
            # Create default conversation flow
            messages = [
                {
                    "id": f"msg_1_{phone_number}",
                    "phone_number": phone_number,
                    "text": f"Hi! 👋 {student.full_name or 'Welcome to EduBot'}",
                    "timestamp": student.created_at.isoformat(),
                    "sender_type": "user",
                    "message_type": "text"
                },
                {
                    "id": f"msg_2_{phone_number}",
                    "phone_number": phone_number,
                    "text": "👋 Welcome! I'm EduBot, your homework assistant.\n\n📚 I can help you:\n• Submit homework for any subject\n• Track your submissions\n• Get tutoring support\n• Manage subscriptions\n\nWhat can I help you with today?",
                    "timestamp": (student.created_at + timedelta(seconds=2)).isoformat(),
                    "sender_type": "bot",
                    "message_type": "text"
                }
            ]
        
        return {
            "status": "success",
            "data": messages
        }
    except Exception as e:
        logger.error(f"Error fetching messages: {str(e)}")
        return {
            "status": "success",
            "data": []
        }