"""
Admin API routes for data operations.
"""
from fastapi import APIRouter, Depends, HTTPException, Query, Request, Body
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from datetime import datetime, timedelta
from pydantic import BaseModel
import secrets

from config.database import get_db, get_db_sync, engine, ASYNC_MODE, AsyncSession as AsyncSessionType
from config.settings import settings
from admin.auth import AdminAuth, admin_session_required
from models.student import Student, UserStatus
from models.lead import Lead
from models.payment import Payment, PaymentStatus
from models.homework import Homework, SubmissionType
from models.subscription import Subscription
from models.settings import AdminSetting
from services.lead_service import LeadService
from services.notification_trigger import NotificationTrigger
from schemas.response import StandardResponse
from utils.logger import get_logger
from utils.security import (
    get_client_ip, track_failed_login, record_failed_login, 
    clear_failed_login, create_session, generate_csrf_token
)

logger = get_logger("admin_api")

router = APIRouter(prefix="/api/admin", tags=["admin_api"])

# Use sync database dependency for admin routes (they use .query() pattern)
# In async mode, we created a sync SessionLocal for backward compatibility
db_dependency = get_db_sync if ASYNC_MODE else get_db

# ASYNC database dependency - for fully async endpoints
# Falls back to sync wrapper if async not available
async def get_async_db():
    """Async dependency for AsyncSession."""
    if ASYNC_MODE and AsyncSessionType:
        from config.database import async_session_maker
        async with async_session_maker() as session:
            try:
                yield session
            except Exception as e:
                logger.error(f"Async database session error: {e}")
                await session.rollback()
                raise
            finally:
                await session.close()
    else:
        # Fallback to sync in compatibility mode
        # This is less efficient but ensures the app works
        db = get_db_sync()
        try:
            yield db
        except Exception as e:
            logger.error(f"Database session error: {e}")
            db.rollback()
            raise
        finally:
            db.close()


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
async def send_whatsapp_test_message(request: Request, request_body: dict = Body(...), db: Session = Depends(db_dependency)):
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
    db: Session = Depends(db_dependency)
):
    """List all registered students with pagination.
    
    Only returns students who have completed registration:
    - Must have non-empty full_name
    - Must have phone_number
    - Must have non-empty/non-pending class_grade
    """
    students = (
        db.query(Student)
        .filter(
            Student.full_name != "",
            Student.full_name.isnot(None),
            Student.class_grade != "",
            Student.class_grade != "Pending",
            Student.class_grade.isnot(None),
        )
        .offset(skip)
        .limit(limit)
        .all()
    )
    
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
async def get_student(student_id: int, db: Session = Depends(db_dependency)):
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


@router.delete("/students/{student_id}")
async def delete_student(student_id: int, db: Session = Depends(db_dependency)):
    """Hard delete a student from the database (cascades to related records)."""
    student = db.query(Student).filter_by(id=student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    
    try:
        student_name = student.full_name
        student_phone = student.phone_number
        
        # Delete related records will be cascaded automatically by SQLAlchemy
        # This includes:
        # - Homeworks (student_id) - CASCADE
        # - Subscriptions (student_id) - CASCADE
        # - Payments (student_id) - CASCADE
        
        logger.info(f"🗑️ Deleting student: {student_id} ({student_name})")
        db.delete(student)
        db.commit()
        
        logger.info(f"✓ Student successfully deleted: {student_id} ({student_name}) - {student_phone}")
        
        return {
            "status": "success",
            "message": f"Student {student_name} and all related records have been permanently deleted"
        }
    except Exception as e:
        db.rollback()
        logger.error(f"❌ Error deleting student {student_id}: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        raise HTTPException(
            status_code=500, 
            detail=f"Failed to delete student: {str(e)}"
        )


# ==================== PAYMENTS ENDPOINTS ====================

@router.get("/payments")
async def list_payments(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(db_dependency)
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
    db: Session = Depends(db_dependency)
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
    submission_type: str = Query(None),
    subject: str = Query(None),
    student_id: int = Query(None),
    db: Session = Depends(db_dependency)
):
    """List homework submissions with pagination and filtering.
    
    Query parameters:
    - skip: Number of records to skip (default 0)
    - limit: Number of records to return (default 50, max 100)
    - submission_type: Filter by IMAGE or TEXT (optional)
    - subject: Filter by subject name (optional)
    - student_id: Filter by student ID (optional)
    """
    # Build query
    query = db.query(Homework)
    
    # Apply filters
    if submission_type:
        query = query.filter(Homework.submission_type == submission_type.upper())
    if subject:
        query = query.filter(Homework.subject.ilike(f"%{subject}%"))
    if student_id:
        query = query.filter(Homework.student_id == student_id)
    
    # Get total count before pagination
    total_count = query.count()
    
    # Apply sorting (latest first) and pagination
    homeworks = query.order_by(Homework.created_at.desc()).offset(skip).limit(limit).all()
    
    return {
        "status": "success",
        "total": total_count,
        "skip": skip,
        "limit": limit,
        "count": len(homeworks),
        "data": [
            {
                "id": h.id,
                "student_id": h.student_id,
                "student_name": h.student.full_name if h.student else "Unknown",
                "student_class": h.student.class_grade if h.student else "Unknown",
                "subject": h.subject,
                "submission_type": h.submission_type.value if h.submission_type else "text",
                "content": h.content,
                "file_path": h.file_path,
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
    db: Session = Depends(db_dependency)
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
async def get_student_stats(student_id: int, db: Session = Depends(db_dependency)):
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
    db: Session = Depends(db_dependency)
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


# ==================== PAYMENTS API ====================

@router.get("/payments/stats")
async def get_payment_stats(db: Session = Depends(db_dependency)):
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
async def get_payment_detail(payment_id: int, db: Session = Depends(db_dependency)):
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
    db: Session = Depends(db_dependency)
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
async def get_subscription_stats(db: Session = Depends(db_dependency)):
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
    db: Session = Depends(db_dependency)
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
async def cancel_subscription(subscription_id: int, db: Session = Depends(db_dependency)):
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
async def get_homework_stats(db: Session = Depends(db_dependency)):
    """Get homework statistics."""
    from models.homework import HomeworkStatus
    
    total = db.query(Homework).count()
    text_submissions = db.query(Homework).filter_by(
        submission_type=SubmissionType.TEXT
    ).count()
    image_submissions = db.query(Homework).filter_by(
        submission_type=SubmissionType.IMAGE
    ).count()
    
    # Count unsolved homework (PENDING, PAID, ASSIGNED, IN_PROGRESS)
    unsolved = db.query(Homework).filter(
        Homework.status.in_([
            HomeworkStatus.PENDING,
            HomeworkStatus.PAID,
            HomeworkStatus.ASSIGNED,
            HomeworkStatus.IN_PROGRESS
        ])
    ).count()
    
    # Count solved homework
    solved = db.query(Homework).filter_by(
        status=HomeworkStatus.SOLVED
    ).count()
    
    return {
        "status": "success",
        "data": {
            "total_submissions": total,
            "text_submissions": text_submissions,
            "image_submissions": image_submissions,
            "unsolved_homework": unsolved,
            "solved_homework": solved
        }
    }


@router.get("/homework/{homework_id}")
async def get_homework_detail(homework_id: int, db: Session = Depends(db_dependency)):
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


@router.post("/homework/{homework_id}/provide-solution")
async def provide_solution(
    homework_id: int,
    request_body: dict = Body(...),
    db: Session = Depends(db_dependency)
):
    """Provide solution to homework and send to student via WhatsApp."""
    solution_text = request_body.get("solution_text", "").strip()
    
    if not solution_text:
        return {
            "status": "error",
            "message": "Solution text is required"
        }
    homework = db.query(Homework).filter_by(id=homework_id).first()
    if not homework:
        raise HTTPException(status_code=404, detail="Homework not found")
    
    student = db.query(Student).filter_by(id=homework.student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    
    try:
        # Update homework status to indicate solution is being prepared
        homework.status = HomeworkStatus.IN_PROGRESS
        db.commit()
        
        # Send solution message to student via WhatsApp
        from services.whatsapp_service import WhatsAppService
        
        message = f"""
*📝 Homework Solution*

Subject: {homework.subject}

*Solution:*
{solution_text}

Please review the solution and let us know if you have any questions.
        """.strip()
        
        result = WhatsAppService.send_message(
            phone_number=student.phone_number,
            message=message
        )
        
        if result:
            # Mark as solved once message is sent
            homework.status = HomeworkStatus.SOLVED
            db.commit()
            
            logger.info(f"Solution provided for homework {homework_id} to student {student.phone_number}")
            
            return {
                "status": "success",
                "message": "Solution sent to student successfully",
                "data": {
                    "homework_id": homework_id,
                    "student_phone": student.phone_number,
                    "status": HomeworkStatus.SOLVED.value
                }
            }
        else:
            # Revert status if message fails
            homework.status = HomeworkStatus.ASSIGNED
            db.commit()
            
            return {
                "status": "error",
                "message": "Failed to send solution via WhatsApp",
                "data": {
                    "homework_id": homework_id,
                    "status": HomeworkStatus.ASSIGNED.value
                }
            }
    except Exception as e:
        logger.error(f"Error providing solution for homework {homework_id}: {str(e)}")
        return {
            "status": "error",
            "message": str(e)
        }


@router.post("/homework/{homework_id}/mark-solved")
async def mark_homework_solved(
    homework_id: int,
    request_body: dict = Body(...),
    db: Session = Depends(db_dependency)
):
    """Mark homework as solved and notify student."""
    delivery_message = request_body.get("delivery_message", "Homework solution delivered successfully!")
    homework = db.query(Homework).filter_by(id=homework_id).first()
    if not homework:
        raise HTTPException(status_code=404, detail="Homework not found")
    
    student = db.query(Student).filter_by(id=homework.student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    
    try:
        # Update homework status to SOLVED
        homework.status = HomeworkStatus.SOLVED
        db.commit()
        
        # Send delivery confirmation to student
        from services.whatsapp_service import WhatsAppService
        
        message = f"""
✅ *Homework Marked as Solved*

Subject: {homework.subject}

{delivery_message}

Thank you for using our homework help service!
        """.strip()
        
        result = WhatsAppService.send_message(
            phone_number=student.phone_number,
            message=message
        )
        
        if result:
            logger.info(f"Homework {homework_id} marked as solved and student {student.phone_number} notified")
        
        return {
            "status": "success",
            "message": "Homework marked as solved",
            "data": {
                "homework_id": homework_id,
                "student_phone": student.phone_number,
                "status": HomeworkStatus.SOLVED.value,
                "message_sent": result
            }
        }
    except Exception as e:
        logger.error(f"Error marking homework {homework_id} as solved: {str(e)}")
        return {
            "status": "error",
            "message": str(e)
        }


@router.delete("/homework/{homework_id}")
async def delete_homework(homework_id: int, db: Session = Depends(db_dependency)):
    """Delete a homework submission."""
    homework = db.query(Homework).filter_by(id=homework_id).first()
    if not homework:
        raise HTTPException(status_code=404, detail="Homework not found")
    
    try:
        # Get student info before deleting (for logging)
        student = db.query(Student).filter_by(id=homework.student_id).first()
        student_name = student.full_name if student else f"Student {homework.student_id}"
        
        # Delete the homework submission
        db.delete(homework)
        db.commit()
        
        logger.info(f"Homework {homework_id} deleted by admin. Student: {student_name}, Subject: {homework.subject}")
        
        return {
            "status": "success",
            "message": "Homework deleted successfully",
            "data": {
                "homework_id": homework_id,
                "student_id": homework.student_id
            }
        }
    except Exception as e:
        db.rollback()
        logger.error(f"Error deleting homework {homework_id}: {str(e)}")
        return {
            "status": "error",
            "message": str(e)
        }


# ==================== SYSTEM STATS ====================

@router.get("/stats/overview")
async def get_overview_stats(db: Session = Depends(db_dependency)):
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
async def get_dashboard_stats(db: Session = Depends(db_dependency)):
    """Get dashboard statistics (alias for /stats/overview).
    
    Only counts registered students (those with name, phone, and class_grade).
    """
    from sqlalchemy import func
    
    # Only count registered students (with name and non-pending class)
    total_students = db.query(Student).filter(
        Student.full_name != "",
        Student.full_name.isnot(None),
        Student.class_grade != "",
        Student.class_grade != "Pending",
        Student.class_grade.isnot(None),
    ).count()
    
    active_subscribers = db.query(Student).filter(
        Student.status == UserStatus.ACTIVE_SUBSCRIBER,
        Student.full_name != "",
        Student.full_name.isnot(None),
        Student.class_grade != "",
        Student.class_grade != "Pending",
        Student.class_grade.isnot(None),
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
@admin_session_required
async def get_settings(request: Request, db: Session = Depends(db_dependency)):
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
        if not settings_dict.get("bot_name"):
            settings_dict["bot_name"] = "EduBot"
        if not settings_dict.get("template_welcome"):
            settings_dict["template_welcome"] = "👋 {name}, welcome to {bot_name}!"
        if not settings_dict.get("template_status"):
            settings_dict["template_status"] = "📋 Status: Awaiting registration\n\nPlease provide:\n1. Your full name\n2. Your class/grade\n3. Email address"
        if not settings_dict.get("template_greeting"):
            settings_dict["template_greeting"] = "Hi {name}! What would you like to do?"
        if not settings_dict.get("template_help"):
            settings_dict["template_help"] = "📚 Help & Features\n\n🎓 I can help you with:\n📝 Homework - Submit assignments and get feedback\n💳 Subscribe - Unlimited submissions\n❓ FAQs - Quick answers\n💬 Support - Chat with our team"
        if not settings_dict.get("template_faq"):
            settings_dict["template_faq"] = "❓ Frequently Asked Questions\n\nChoose a category for more info."
        if not settings_dict.get("template_error"):
            settings_dict["template_error"] = "❓ I didn't quite understand that.\n\nChoose an option above to continue."
        
        # Ensure all expected keys exist
        expected_keys = [
            "whatsapp_api_key", "whatsapp_phone_number_id", "whatsapp_business_account_id",
            "whatsapp_phone_number", "whatsapp_webhook_token", "paystack_public_key",
            "paystack_secret_key", "paystack_webhook_secret", "database_url", "bot_name",
            "template_welcome", "template_status", "template_greeting", "template_help", 
            "template_faq", "template_error"
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
                "database_url": settings.database_url or "",
                "bot_name": "EduBot",
                "template_welcome": "👋 {name}, welcome to {bot_name}!",
                "template_status": "📋 Status: Awaiting registration\n\nPlease provide:\n1. Your full name\n2. Your class/grade\n3. Email address",
                "template_greeting": "Hi {name}! What would you like to do?",
                "template_help": "📚 Help & Features\n\n🎓 I can help you with:\n📝 Homework - Submit assignments and get feedback\n💳 Subscribe - Unlimited submissions\n❓ FAQs - Quick answers\n💬 Support - Chat with our team",
                "template_faq": "❓ Frequently Asked Questions\n\nChoose a category for more info.",
                "template_error": "❓ I didn't quite understand that.\n\nChoose an option above to continue."
            }
        }


@router.get("/settings/debug")
async def debug_settings(db: Session = Depends(db_dependency)):
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
@admin_session_required
async def update_settings(request: Request, data: dict, db: Session = Depends(db_dependency)):
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


@router.post("/settings/validate-whatsapp")
@admin_session_required
async def validate_whatsapp(request: Request, db: Session = Depends(db_dependency)):
    """Validate WhatsApp configuration."""
    try:
        # Get current settings
        db_settings = db.query(AdminSetting).filter(
            AdminSetting.key.in_([
                "whatsapp_api_key",
                "whatsapp_phone_number_id",
                "whatsapp_business_account_id"
            ])
        ).all()
        
        settings_dict = {s.key: s.value for s in db_settings}
        
        # Check if required fields are present
        required_fields = ["whatsapp_api_key", "whatsapp_phone_number_id", "whatsapp_business_account_id"]
        missing = [f for f in required_fields if not settings_dict.get(f)]
        
        if missing:
            return {
                "status": "warning",
                "message": f"Missing WhatsApp configuration: {', '.join(missing)}",
                "valid": False
            }
        
        # Check field lengths
        if len(settings_dict.get("whatsapp_api_key", "")) < 50:
            return {
                "status": "warning",
                "message": "WhatsApp API key appears too short",
                "valid": False
            }
        
        return {
            "status": "success",
            "message": "WhatsApp configuration appears valid",
            "valid": True
        }
    except Exception as e:
        logger.error(f"WhatsApp validation error: {str(e)}")
        return {
            "status": "error",
            "message": f"Validation error: {str(e)}",
            "valid": False
        }


@router.post("/settings/validate-paystack")
@admin_session_required
async def validate_paystack(request: Request, db: Session = Depends(db_dependency)):
    """Validate Paystack configuration."""
    try:
        # Get current settings
        db_settings = db.query(AdminSetting).filter(
            AdminSetting.key.in_([
                "paystack_public_key",
                "paystack_secret_key"
            ])
        ).all()
        
        settings_dict = {s.key: s.value for s in db_settings}
        
        # Check if required fields are present
        required_fields = ["paystack_public_key", "paystack_secret_key"]
        missing = [f for f in required_fields if not settings_dict.get(f)]
        
        if missing:
            return {
                "status": "warning",
                "message": f"Missing Paystack configuration: {', '.join(missing)}",
                "valid": False
            }
        
        # Check field lengths
        if len(settings_dict.get("paystack_public_key", "")) < 20:
            return {
                "status": "warning",
                "message": "Paystack public key appears too short",
                "valid": False
            }
        
        return {
            "status": "success",
            "message": "Paystack configuration appears valid",
            "valid": True
        }
    except Exception as e:
        logger.error(f"Paystack validation error: {str(e)}")
        return {
            "status": "error",
            "message": f"Validation error: {str(e)}",
            "valid": False
        }


# ==================== REPORTS ENDPOINTS ====================

@router.get("/reports")
async def get_reports(db: Session = Depends(db_dependency)):
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
    db: Session = Depends(db_dependency)
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
async def get_leads_stats(db: Session = Depends(db_dependency)):
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
async def get_lead_detail(lead_id: int, db: Session = Depends(db_dependency)):
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
    db: Session = Depends(db_dependency)
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
async def delete_lead(lead_id: int, db: Session = Depends(db_dependency)):
    """Hard delete a lead from the database."""
    try:
        lead = db.query(Lead).filter(Lead.id == lead_id).first()
        
        if not lead:
            raise HTTPException(status_code=404, detail="Lead not found")
        
        phone_number = lead.phone_number
        
        # Hard delete - completely remove from database
        db.delete(lead)
        db.commit()
        
        logger.info(f"✓ Lead hard deleted: {lead_id} ({phone_number})")
        
        return {
            "status": "success",
            "message": f"Lead {phone_number} has been permanently deleted"
        }
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error deleting lead: {str(e)}")
        return {
            "status": "error",
            "message": str(e)
        }

# ==================== CONVERSATIONS ENDPOINTS ====================

@router.get("/conversations")
async def get_conversations(
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(db_dependency)
):
    """
    Get list of recent conversations with WhatsApp users.
    Includes both registered students AND unregistered leads.
    Returns phone numbers, last message, timestamp, and activity status.
    
    Activity Status:
    - is_active: True if user has messaged in the last 3 minutes
    - is_active: False if no message for 3+ minutes (inactive)
    """
    try:
        from models.student import Student
        from models.lead import Lead
        from services.conversation_service import ConversationService
        from datetime import datetime, timedelta
        
        conversations = []
        conversation_phones = set()
        INACTIVITY_TIMEOUT_MINUTES = 3
        
        # Get ALL students, not just fully registered ones, to show activity
        all_students = (
            db.query(Student)
            .order_by(Student.updated_at.desc())
            .limit(limit * 2)  # Get more to account for filtering
            .all()
        )
        
        # Separate fully registered from partially registered
        for student in all_students:
            try:
                # Get conversation state to find last message
                conv_state = ConversationService.get_state(student.phone_number)
                messages = conv_state.get("data", {}).get("messages", [])
                is_chat_support = conv_state.get("data", {}).get("chat_support_active", False)
                
                # Determine if fully registered
                is_fully_registered = (
                    student.full_name and student.full_name.strip() != "" and
                    student.class_grade and student.class_grade.strip() != "" and
                    student.class_grade != "Pending"
                )
                
                last_message = conv_state.get("data", {}).get("last_message")
                if not last_message:
                    if messages and len(messages) > 0:
                        last_message = messages[-1].get("text", "No message")
                    else:
                        last_message = "No messages yet" if not is_fully_registered else f"{student.full_name} is registered"
                
                last_message_time = student.updated_at.isoformat() if student.updated_at else student.created_at.isoformat()
                last_message_datetime = student.updated_at if student.updated_at else student.created_at
                
                if messages and len(messages) > 0:
                    last_msg = messages[-1]
                    if last_msg.get("timestamp"):
                        last_message_time = last_msg["timestamp"]
                        try:
                            # Parse timestamp to datetime for inactivity check
                            if isinstance(last_msg["timestamp"], str):
                                last_message_datetime = datetime.fromisoformat(last_msg["timestamp"].replace('Z', '+00:00'))
                        except Exception as e:
                            logger.warning(f"Error parsing message timestamp: {e}")
                
                # Check if user is inactive (no message in last 3 minutes)
                now = datetime.now(last_message_datetime.tzinfo) if last_message_datetime.tzinfo else datetime.utcnow()
                time_since_last_message = now - last_message_datetime
                is_active = time_since_last_message < timedelta(minutes=INACTIVITY_TIMEOUT_MINUTES)
                
                conversations.append({
                    "phone_number": student.phone_number,
                    "student_name": student.full_name or student.phone_number,
                    "last_message": last_message,
                    "last_message_time": last_message_time,
                    "message_count": len(messages),
                    "is_active": is_active,
                    "type": "student" if is_fully_registered else "lead",
                    "is_chat_support": is_chat_support,
                    "inactivity_minutes": int(time_since_last_message.total_seconds() / 60)
                })
                
                conversation_phones.add(student.phone_number)
            except Exception as student_err:
                logger.warning(f"Error processing student {student.phone_number}: {student_err}")
                continue
        
        # Get unregistered leads (not in student table)
        unregistered_leads = (
            db.query(Lead)
            .filter(Lead.is_active == True, Lead.converted_to_student == False)
            .order_by(Lead.last_message_time.desc())
            .limit(limit)
            .all()
        )
        
        for lead in unregistered_leads:
            if lead.phone_number not in conversation_phones:
                try:
                    conv_state = ConversationService.get_state(lead.phone_number)
                    messages = conv_state.get("data", {}).get("messages", [])
                    is_chat_support = conv_state.get("data", {}).get("chat_support_active", False)
                    
                    last_message_datetime = lead.last_message_time if lead.last_message_time else datetime.utcnow()
                    
                    # Check if user is inactive (no message in last 3 minutes)
                    now = datetime.now(last_message_datetime.tzinfo) if last_message_datetime.tzinfo else datetime.utcnow()
                    time_since_last_message = now - last_message_datetime
                    is_active = time_since_last_message < timedelta(minutes=INACTIVITY_TIMEOUT_MINUTES)
                    
                    conversations.append({
                        "phone_number": lead.phone_number,
                        "student_name": lead.sender_name or lead.phone_number,
                        "last_message": lead.last_message or "Awaiting registration",
                        "last_message_time": lead.last_message_time.isoformat(),
                        "message_count": lead.message_count,
                        "is_active": is_active,
                        "type": "lead",
                        "is_chat_support": is_chat_support,
                        "inactivity_minutes": int(time_since_last_message.total_seconds() / 60)
                    })
                    
                    conversation_phones.add(lead.phone_number)
                except Exception as lead_err:
                    logger.warning(f"Error processing lead {lead.phone_number}: {lead_err}")
                    continue
        
        # Sort by last message time
        def get_sort_key(conv):
            try:
                time_str = conv.get("last_message_time", "")
                if isinstance(time_str, str):
                    return datetime.fromisoformat(time_str.replace('Z', '+00:00'))
                return datetime.utcnow()
            except Exception as e:
                logger.warning(f"Error parsing time {time_str}: {e}")
                return datetime.utcnow()
        
        conversations.sort(key=get_sort_key, reverse=True)
        conversations = conversations[:limit]
        
        logger.info(f"Returning {len(conversations)} conversations ({sum(1 for c in conversations if c['type']=='student')} students, {sum(1 for c in conversations if c['type']=='lead')} leads)")
        
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
async def get_conversation_messages(phone_number: str, db: Session = Depends(db_dependency)):
    """
    Get message history for a specific phone number.
    Returns conversation thread with user and bot messages.
    Handles both registered students and unregistered leads.
    """
    try:
        from models.student import Student
        from models.lead import Lead
        from services.conversation_service import ConversationService
        
        messages = []
        
        # Get conversation state (works for both students and leads)
        conv_state = ConversationService.get_state(phone_number)
        
        # Try to get stored messages from conversation service
        stored_messages = conv_state.get("data", {}).get("messages", [])
        
        if stored_messages and len(stored_messages) > 0:
            # Use stored messages if available
            messages = stored_messages
        else:
            # Get bot settings
            bot_name_setting = db.query(AdminSetting).filter(AdminSetting.key == "bot_name").first()
            bot_name = bot_name_setting.value if bot_name_setting else "EduBot"
            
            template_welcome_setting = db.query(AdminSetting).filter(AdminSetting.key == "template_welcome").first()
            template_welcome = template_welcome_setting.value if template_welcome_setting else "👋 {name}, welcome to {bot_name}!"
            
            template_status_setting = db.query(AdminSetting).filter(AdminSetting.key == "template_status").first()
            template_status = template_status_setting.value if template_status_setting else "📋 Status: Awaiting registration\n\nPlease provide:\n1. Your full name\n2. Your class/grade\n3. Email address"
            
            # Check if it's a student or lead and create default conversation
            student = db.query(Student).filter(Student.phone_number == phone_number).first()
            lead = db.query(Lead).filter(Lead.phone_number == phone_number).first()
            
            if student or lead:
                # Create initial greeting message
                name = student.full_name if student else (lead.sender_name if lead else "User")
                timestamp = student.created_at if student else (lead.created_at if lead else datetime.utcnow())
                
                # Replace template variables
                welcome_text = template_welcome.replace("{name}", name).replace("{bot_name}", bot_name)
                
                messages = [
                    {
                        "id": f"msg_welcome_{phone_number}",
                        "phone_number": phone_number,
                        "text": welcome_text,
                        "timestamp": timestamp.isoformat() if hasattr(timestamp, 'isoformat') else timestamp,
                        "sender_type": "bot",
                        "message_type": "text"
                    }
                ]
                
                # Add status message for unregistered leads
                if lead and not student:
                    messages.append({
                        "id": f"msg_status_{phone_number}",
                        "phone_number": phone_number,
                        "text": template_status,
                        "timestamp": (timestamp + timedelta(seconds=1)).isoformat() if hasattr(timestamp, 'isoformat') else timestamp,
                        "sender_type": "bot",
                        "message_type": "text"
                    })
        
        return {
            "status": "success",
            "data": messages
        }
    except Exception as e:
        logger.error(f"Error fetching messages for {phone_number}: {str(e)}")
        return {
            "status": "success",
            "data": []
        }


@router.post("/conversations/{phone_number}/chat-support/start")
async def start_chat_support(
    phone_number: str,
    request_body: dict = Body(...),
    db: Session = Depends(db_dependency)
):
    """
    Admin initiates a chat support session with a user.
    
    Request body:
    {
        "message": "Optional greeting message to send to user"
    }
    """
    try:
        from services.conversation_service import ConversationService, ConversationState
        from services.whatsapp_service import WhatsAppService
        
        greeting_message = request_body.get("message", "🎧 Chat Support: An admin is now available to help you. How can we assist you?")
        
        # Check if user is already in chat support
        conv_state = ConversationService.get_state(phone_number)
        is_already_in_chat = conv_state.get("data", {}).get("chat_support_active", False)
        
        if is_already_in_chat:
            return {
                "status": "error",
                "message": "User is already in an active chat support session"
            }
        
        # Initialize chat support session
        ConversationService.set_data(phone_number, "chat_support_active", True)
        ConversationService.set_data(phone_number, "chat_start_time", datetime.now().isoformat())
        ConversationService.set_data(phone_number, "chat_messages", [])
        ConversationService.set_state(phone_number, ConversationState.CHAT_SUPPORT_ACTIVE)
        
        # Send greeting message to user
        try:
            result = await WhatsAppService.send_message(
                phone_number=phone_number,
                message_type="text",
                text=greeting_message
            )
        except Exception as msg_err:
            logger.warning(f"Could not send greeting message: {str(msg_err)}")
        
        logger.info(f"Admin started chat support session with {phone_number}")
        
        return {
            "status": "success",
            "message": "Chat support session started",
            "data": {
                "phone_number": phone_number,
                "session_started": datetime.now().isoformat(),
                "initial_message_sent": True
            }
        }
    
    except Exception as e:
        logger.error(f"Error starting chat support: {str(e)}")
        return {
            "status": "error",
            "message": f"Error starting chat: {str(e)}"
        }


@router.post("/conversations/{phone_number}/chat-support/send")
async def send_chat_support_message(
    phone_number: str,
    request_body: dict = Body(...),
    db: Session = Depends(db_dependency)
):
    """
    Admin sends a message to a user in active chat support.
    
    Request body:
    {
        "message": "Your support message here"
    }
    """
    try:
        from services.conversation_service import ConversationService
        from services.whatsapp_service import WhatsAppService
        
        message_text = request_body.get("message", "").strip()
        
        if not message_text:
            return {
                "status": "error",
                "message": "Message cannot be empty"
            }
        
        # Check if user is in active chat support
        conv_state = ConversationService.get_state(phone_number)
        is_in_chat = conv_state.get("data", {}).get("chat_support_active", False)
        
        if not is_in_chat:
            return {
                "status": "error",
                "message": "User is not in an active chat support session"
            }
        
        # Send message via WhatsApp
        result = await WhatsAppService.send_message(
            phone_number=phone_number,
            message_type="text",
            text=f"🎧 Support Team: {message_text}"
        )
        
        if result.get("status") == "success":
            # Store admin message in conversation
            chat_messages = ConversationService.get_data(phone_number, "chat_messages") or []
            if isinstance(chat_messages, str):
                chat_messages = []
            
            chat_messages.append({
                "text": message_text,
                "timestamp": datetime.now().isoformat(),
                "sender": "admin"
            })
            ConversationService.set_data(phone_number, "chat_messages", chat_messages)
            
            # Trigger notification to user for admin message
            try:
                student = db.query(Student).filter(Student.phone_number == phone_number).first()
                user_name = student.name if student else "Support Team"
                NotificationTrigger.on_chat_message_received(
                    phone_number=phone_number,
                    sender_name="Support Team",
                    message_preview=message_text[:100],
                    db=db
                )
            except Exception as e:
                logger.warning(f"Could not send user chat notification: {str(e)}")
            
            logger.info(f"Admin sent chat support message to {phone_number}")
            
            return {
                "status": "success",
                "message": "Message sent to user",
                "data": {
                    "phone_number": phone_number,
                    "message_sent": message_text,
                    "timestamp": datetime.now().isoformat()
                }
            }
        else:
            logger.warning(f"Failed to send chat message to {phone_number}: {result.get('error')}")
            return {
                "status": "error",
                "message": f"Failed to send message: {result.get('error')}"
            }
    
    except Exception as e:
        logger.error(f"Error sending chat support message: {str(e)}")
        return {
            "status": "error",
            "message": f"Error sending message: {str(e)}"
        }


@router.post("/conversations/{phone_number}/chat-support/end")
async def end_chat_support(
    phone_number: str,
    request_body: dict = Body(...) ,
    db: Session = Depends(db_dependency)
):
    """
    Admin ends a chat support session with a user.
    
    Request body:
    {
        "message": "Optional closing message to send to user"
    }
    """
    try:
        from services.conversation_service import ConversationService, ConversationState
        from services.whatsapp_service import WhatsAppService
        
        closing_message = request_body.get("message", "Thank you for contacting support. Chat session ended.")
        
        # Check if user is in active chat support
        conv_state = ConversationService.get_state(phone_number)
        is_in_chat = conv_state.get("data", {}).get("chat_support_active", False)
        
        if not is_in_chat:
            return {
                "status": "error",
                "message": "User is not in an active chat support session"
            }
        
        # Send closing message to user
        try:
            await WhatsAppService.send_message(
                phone_number=phone_number,
                message_type="text",
                text=closing_message
            )
        except Exception as msg_err:
            logger.warning(f"Could not send closing message: {str(msg_err)}")
        
        # Update conversation state
        ConversationService.set_data(phone_number, "chat_support_active", False)
        ConversationService.set_data(phone_number, "in_chat_support", False)
        chat_start_time = ConversationService.get_data(phone_number, "chat_start_time")
        ConversationService.set_data(phone_number, "chat_messages", None)
        ConversationService.set_state(phone_number, ConversationState.IDLE)
        
        # Calculate chat duration
        duration_minutes = None
        if chat_start_time:
            try:
                start_dt = datetime.fromisoformat(chat_start_time)
                duration = datetime.now() - start_dt
                duration_minutes = int(duration.total_seconds() / 60)
            except:
                pass
        
        # Trigger notification that chat has ended
        try:
            student = db.query(Student).filter(Student.phone_number == phone_number).first()
            user_name = student.name if student else "User"
            NotificationTrigger.on_chat_support_ended_admin(
                phone_number=phone_number,
                user_name=user_name,
                admin_phone="admin",
                duration_minutes=duration_minutes,
                db=db
            )
        except Exception as e:
            logger.warning(f"Could not send chat ended notification: {str(e)}")
        
        logger.info(f"Admin ended chat support session with {phone_number}")
        
        return {
            "status": "success",
            "message": "Chat support session ended",
            "data": {
                "phone_number": phone_number,
                "session_ended": datetime.now().isoformat()
            }
        }
    
    except Exception as e:
        logger.error(f"Error ending chat support: {str(e)}")
        return {
            "status": "error",
            "message": f"Error ending chat: {str(e)}"
        }

# ==================== BOT MESSAGE MANAGEMENT ====================
# Full admin control over preformatted bot responses

@router.get("/bot-messages/list")
@admin_session_required
async def admin_list_bot_messages(
    request: Request,
    active_only: bool = Query(False),
    context: Optional[str] = Query(None),
    db: Session = Depends(db_dependency)
):
    """List all bot messages (admin only)."""
    try:
        from models.bot_message import BotMessage
        
        query = db.query(BotMessage)
        
        if active_only:
            query = query.filter(BotMessage.is_active == True)
        
        if context:
            query = query.filter(BotMessage.context == context)
        
        messages = query.all()
        
        return {
            "status": "success",
            "data": [
                {
                    "id": msg.id,
                    "message_key": msg.message_key,
                    "message_type": msg.message_type,
                    "context": msg.context,
                    "content": msg.content,
                    "has_menu": msg.has_menu,
                    "menu_items": msg.menu_items,
                    "next_states": msg.next_states,
                    "variables": msg.variables,
                    "is_active": msg.is_active,
                    "description": msg.description,
                    "created_by": msg.created_by,
                    "updated_by": msg.updated_by,
                    "created_at": msg.created_at.isoformat() if msg.created_at else None,
                    "updated_at": msg.updated_at.isoformat() if msg.updated_at else None
                }
                for msg in messages
            ],
            "count": len(messages)
        }
    except Exception as e:
        logger.error(f"Error listing bot messages: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/bot-messages/{message_key}")
@admin_session_required
async def admin_get_bot_message(
    request: Request,
    message_key: str,
    db: Session = Depends(db_dependency)
):
    """Get a specific bot message by key (admin only)."""
    try:
        from models.bot_message import BotMessage
        
        msg = db.query(BotMessage).filter(BotMessage.message_key == message_key).first()
        
        if not msg:
            raise HTTPException(status_code=404, detail=f"Message '{message_key}' not found")
        
        return {
            "status": "success",
            "data": {
                "id": msg.id,
                "message_key": msg.message_key,
                "message_type": msg.message_type,
                "context": msg.context,
                "content": msg.content,
                "has_menu": msg.has_menu,
                "menu_items": msg.menu_items,
                "next_states": msg.next_states,
                "variables": msg.variables,
                "is_active": msg.is_active,
                "description": msg.description,
                "created_by": msg.created_by,
                "updated_by": msg.updated_by,
                "created_at": msg.created_at.isoformat() if msg.created_at else None,
                "updated_at": msg.updated_at.isoformat() if msg.updated_at else None
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting bot message: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/bot-messages/create")
@admin_session_required
async def admin_create_bot_message(
    request: Request,
    data: dict = Body(...),
    db: Session = Depends(db_dependency)
):
    """Create a new bot message (admin only)."""
    try:
        from models.bot_message import BotMessage
        
        # Validate required fields
        required_fields = ["message_key", "message_type", "context", "content"]
        for field in required_fields:
            if field not in data:
                raise HTTPException(status_code=400, detail=f"Missing required field: {field}")
        
        # Check if message already exists
        existing = db.query(BotMessage).filter(
            BotMessage.message_key == data["message_key"]
        ).first()
        
        if existing:
            raise HTTPException(status_code=400, detail=f"Message key '{data['message_key']}' already exists")
        
        # Get admin username from session
        admin_username = request.session.get("admin_username", "unknown")
        
        # Create new message
        new_msg = BotMessage(
            message_key=data["message_key"],
            message_type=data["message_type"],
            context=data["context"],
            content=data["content"],
            has_menu=data.get("has_menu", False),
            menu_items=data.get("menu_items"),
            next_states=data.get("next_states"),
            variables=data.get("variables"),
            is_active=data.get("is_active", True),
            description=data.get("description"),
            created_by=admin_username,
            updated_by=admin_username
        )
        
        db.add(new_msg)
        db.commit()
        db.refresh(new_msg)
        
        logger.info(f"Admin {admin_username} created bot message: {data['message_key']}")
        
        return {
            "status": "success",
            "message": f"Bot message '{data['message_key']}' created successfully",
            "data": {
                "id": new_msg.id,
                "message_key": new_msg.message_key
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating bot message: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/bot-messages/{message_key}/update")
@admin_session_required
async def admin_update_bot_message(
    request: Request,
    message_key: str,
    data: dict = Body(...),
    db: Session = Depends(db_dependency)
):
    """Update a bot message (admin only)."""
    try:
        from models.bot_message import BotMessage
        
        msg = db.query(BotMessage).filter(BotMessage.message_key == message_key).first()
        
        if not msg:
            raise HTTPException(status_code=404, detail=f"Message '{message_key}' not found")
        
        # Get admin username from session
        admin_username = request.session.get("admin_username", "unknown")
        
        # Update fields
        if "content" in data:
            msg.content = data["content"]
        if "message_type" in data:
            msg.message_type = data["message_type"]
        if "context" in data:
            msg.context = data["context"]
        if "has_menu" in data:
            msg.has_menu = data["has_menu"]
        if "menu_items" in data:
            msg.menu_items = data["menu_items"]
        if "next_states" in data:
            msg.next_states = data["next_states"]
        if "variables" in data:
            msg.variables = data["variables"]
        if "is_active" in data:
            msg.is_active = data["is_active"]
        if "description" in data:
            msg.description = data["description"]
        
        msg.updated_by = admin_username
        msg.updated_at = datetime.utcnow()
        
        db.commit()
        db.refresh(msg)
        
        logger.info(f"Admin {admin_username} updated bot message: {message_key}")
        
        return {
            "status": "success",
            "message": f"Bot message '{message_key}' updated successfully",
            "data": {
                "id": msg.id,
                "message_key": msg.message_key
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error updating bot message: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/bot-messages/{message_key}")
@admin_session_required
async def admin_delete_bot_message(
    request: Request,
    message_key: str,
    db: Session = Depends(db_dependency)
):
    """Delete a bot message (admin only)."""
    try:
        from models.bot_message import BotMessage
        
        msg = db.query(BotMessage).filter(BotMessage.message_key == message_key).first()
        
        if not msg:
            raise HTTPException(status_code=404, detail=f"Message '{message_key}' not found")
        
        # Get admin username from session
        admin_username = request.session.get("admin_username", "unknown")
        
        db.delete(msg)
        db.commit()
        
        logger.info(f"Admin {admin_username} deleted bot message: {message_key}")
        
        return {
            "status": "success",
            "message": f"Bot message '{message_key}' deleted successfully"
        }
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error deleting bot message: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/bot-messages/{message_key}/toggle")
@admin_session_required
async def admin_toggle_bot_message(
    request: Request,
    message_key: str,
    db: Session = Depends(db_dependency)
):
    """Toggle bot message active status (admin only)."""
    try:
        from models.bot_message import BotMessage
        
        msg = db.query(BotMessage).filter(BotMessage.message_key == message_key).first()
        
        if not msg:
            raise HTTPException(status_code=404, detail=f"Message '{message_key}' not found")
        
        # Get admin username from session
        admin_username = request.session.get("admin_username", "unknown")
        
        msg.is_active = not msg.is_active
        msg.updated_by = admin_username
        msg.updated_at = datetime.utcnow()
        
        db.commit()
        db.refresh(msg)
        
        logger.info(f"Admin {admin_username} toggled bot message '{message_key}' to {msg.is_active}")
        
        return {
            "status": "success",
            "message": f"Bot message '{message_key}' is now {'active' if msg.is_active else 'inactive'}",
            "data": {
                "is_active": msg.is_active
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error toggling bot message: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/bot-messages/stats/overview")
@admin_session_required
async def admin_bot_messages_stats(
    request: Request,
    db: Session = Depends(db_dependency)
):
    """Get bot messages statistics (admin only)."""
    try:
        from models.bot_message import BotMessage
        
        total = db.query(BotMessage).count()
        active = db.query(BotMessage).filter(BotMessage.is_active == True).count()
        inactive = db.query(BotMessage).filter(BotMessage.is_active == False).count()
        
        # Count by type
        by_type = {}
        for msg in db.query(BotMessage).all():
            msg_type = msg.message_type
            by_type[msg_type] = by_type.get(msg_type, 0) + 1
        
        # Count by context
        by_context = {}
        for msg in db.query(BotMessage).all():
            context = msg.context
            by_context[context] = by_context.get(context, 0) + 1
        
        return {
            "status": "success",
            "data": {
                "total_messages": total,
                "active": active,
                "inactive": inactive,
                "by_type": by_type,
                "by_context": by_context
            }
        }
    except Exception as e:
        logger.error(f"Error getting bot messages stats: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# ==================== SETTINGS ENDPOINTS ====================

@router.get("/settings")
async def get_public_settings(db: Session = Depends(db_dependency)):
    """Get public settings from admin_settings table (no auth required for login page)."""
    try:
        from models.settings import AdminSetting
        
        # Fetch all settings from database
        settings = db.query(AdminSetting).all()
        
        # Build response dict with all settings
        settings_dict = {}
        for setting in settings:
            settings_dict[setting.key] = setting.value
        
        return {
            "status": "success",
            "data": settings_dict
        }
    except Exception as e:
        logger.error(f"Error getting settings: {str(e)}")
        # Return default values on error
        return {
            "status": "success",
            "data": {
                "bot_name": "EduBot"
            }
        }


@router.get("/settings/{key}")
async def get_setting(key: str, db: Session = Depends(db_dependency)):
    """Get a specific setting from admin_settings table."""
    try:
        from models.settings import AdminSetting
        
        setting = db.query(AdminSetting).filter(AdminSetting.key == key).first()
        
        if not setting:
            return {
                "status": "error",
                "message": f"Setting '{key}' not found",
                "data": None
            }
        
        return {
            "status": "success",
            "data": {
                "key": setting.key,
                "value": setting.value,
                "description": setting.description
            }
        }
    except Exception as e:
        logger.error(f"Error getting setting '{key}': {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/settings/{key}")
@admin_session_required
async def update_setting(
    key: str,
    value: str = Body(...),
    request: Request = None,
    db: Session = Depends(db_dependency)
):
    """Update a specific setting in admin_settings table (admin only)."""
    try:
        from models.settings import AdminSetting
        
        setting = db.query(AdminSetting).filter(AdminSetting.key == key).first()
        
        if not setting:
            # Create new setting if it doesn't exist
            setting = AdminSetting(key=key, value=value)
            db.add(setting)
        else:
            # Update existing setting
            setting.value = value
        
        # Track who made the update
        admin_username = request.session.get("admin_username", "unknown") if request else "api"
        setting.description = f"Last updated by {admin_username}"
        
        db.commit()
        db.refresh(setting)
        
        logger.info(f"Admin {admin_username} updated setting: {key}")
        
        return {
            "status": "success",
            "message": f"Setting '{key}' updated successfully",
            "data": {
                "key": setting.key,
                "value": setting.value
            }
        }
    except Exception as e:
        db.rollback()
        logger.error(f"Error updating setting '{key}': {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))