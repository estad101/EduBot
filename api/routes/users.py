"""
User identification endpoint.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from schemas.student import UserIdentificationRequest
from schemas.response import UserIdentificationResponse, StandardResponse
from services.student_service import StudentService
from config.database import get_db, get_db_sync, ASYNC_MODE
from utils.validators import validate_phone_number
from utils.logger import get_logger


# Use sync database dependency
db_dependency = get_db_sync if ASYNC_MODE else get_db

router = APIRouter(prefix="/api/users", tags=["users"])
logger = get_logger("users_route")


@router.post("/identify", response_model=StandardResponse)
async def identify_user(
    request: UserIdentificationRequest, db: Session = Depends(db_dependency)
):
    """
    Identify user by WhatsApp phone number.
    
    Checks if user exists in system. If new, returns NEW_USER.
    If existing, returns user details and subscription status.
    
    Request:
        {
            "phone_number": "+234901234567"
        }
    
    Response:
        {
            "status": "success",
            "message": "...",
            "data": {
                "status": "NEW_USER" or "RETURNING_USER",
                "student_id": 1,
                "phone_number": "+234901234567",
                "user_status": "REGISTERED_FREE",
                "name": "John Doe",
                "email": "john@example.com",
                "has_active_subscription": false
            }
        }
    """
    try:
        # Validate phone number
        is_valid, error_msg = validate_phone_number(request.phone_number)
        if not is_valid:
            logger.warning(f"Invalid phone number: {request.phone_number}")
            return StandardResponse(
                status="validation_error",
                message=error_msg,
                error_code="INVALID_PHONE",
            )

        # Identify user
        user_info = StudentService.identify_user(db, request.phone_number)

        logger.info(f"User identified: {user_info['phone_number']} - {user_info['status']}")

        return StandardResponse(
            status="success",
            message=f"User {user_info['status']}",
            data=user_info,
        )

    except Exception as e:
        logger.error(f"Error identifying user: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
