"""
Subscription status endpoint.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from schemas.response import StandardResponse
from services.student_service import StudentService
from services.subscription_service import SubscriptionService
from config.database import get_db, get_db_sync, ASYNC_MODE
from utils.logger import get_logger


# Use sync database dependency
db_dependency = get_db_sync if ASYNC_MODE else get_db

router = APIRouter(prefix="/api/subscriptions", tags=["subscriptions"])
logger = get_logger("subscriptions_route")


@router.get("/check/{student_id}", response_model=StandardResponse)
async def check_subscription_status(student_id: int, db: Session = Depends(db_dependency)):
    """
    Check subscription status for a student.
    
    Returns active subscription details if exists.
    Returns expired flag if subscription has expired.
    
    URL Parameters:
        student_id: Student ID
    
    Response:
        {
            "status": "success",
            "message": "Active subscription found",
            "data": {
                "has_active_subscription": true,
                "is_expired": false,
                "start_date": "2024-01-01T00:00:00",
                "end_date": "2024-01-31T00:00:00",
                "days_remaining": 15
            }
        }
    
    Or if no subscription:
        {
            "status": "success",
            "message": "No active subscription",
            "data": {
                "has_active_subscription": false
            }
        }
    """
    try:
        # Validate student exists
        student = StudentService.get_student_by_id(db, student_id)
        if not student:
            logger.warning(f"Subscription check for unknown student: {student_id}")
            return StandardResponse(
                status="error",
                message="Student not found",
                error_code="STUDENT_NOT_FOUND",
            )

        # Check subscription status
        subscription_status = SubscriptionService.check_subscription_status(
            db, student_id
        )

        message = (
            "Active subscription found"
            if subscription_status["has_active_subscription"]
            else "No active subscription"
        )

        logger.info(f"Subscription status checked: Student {student_id}")

        return StandardResponse(
            status="success",
            message=message,
            data=subscription_status,
        )

    except Exception as e:
        logger.error(f"Error checking subscription status: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
