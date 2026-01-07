"""
Response schema - standardized JSON response format for n8n.
"""
from pydantic import BaseModel
from typing import Optional, Any, Dict


class StandardResponse(BaseModel):
    """
    Standard response format for all API endpoints.
    Designed for n8n workflow integration.
    """
    status: str  # "success", "error", "validation_error"
    message: str
    data: Optional[Dict[str, Any]] = None
    error_code: Optional[str] = None

    class Config:
        json_schema_extra = {
            "example": {
                "status": "success",
                "message": "Operation completed successfully",
                "data": {
                    "student_id": 1,
                    "phone_number": "+234901234567",
                    "status": "REGISTERED_FREE"
                }
            }
        }


class UserIdentificationResponse(BaseModel):
    """Response for user identification endpoint."""
    status: str  # "NEW_USER" or "RETURNING_USER"
    student_id: Optional[int] = None
    phone_number: str
    user_status: Optional[str] = None  # NEW_USER, REGISTERED_FREE, ACTIVE_SUBSCRIBER
    name: Optional[str] = None
    email: Optional[str] = None
    has_active_subscription: Optional[bool] = None

    class Config:
        json_schema_extra = {
            "example": {
                "status": "RETURNING_USER",
                "student_id": 1,
                "phone_number": "+234901234567",
                "user_status": "REGISTERED_FREE",
                "name": "John Doe",
                "email": "john@example.com",
                "has_active_subscription": False
            }
        }


class StudentRegistrationResponse(BaseModel):
    """Response for student registration."""
    status: str  # "success"
    student_id: int
    phone_number: str
    full_name: str
    email: str
    class_grade: str
    user_status: str  # REGISTERED_FREE

    class Config:
        json_schema_extra = {
            "example": {
                "status": "success",
                "student_id": 1,
                "phone_number": "+234901234567",
                "full_name": "John Doe",
                "email": "john@example.com",
                "class_grade": "10A",
                "user_status": "REGISTERED_FREE"
            }
        }


class PaymentInitiationResponse(BaseModel):
    """Response for payment initiation."""
    status: str  # "success"
    payment_id: int
    authorization_url: str
    access_code: str
    amount: float
    reference: str
    message: str

    class Config:
        json_schema_extra = {
            "example": {
                "status": "success",
                "payment_id": 1,
                "authorization_url": "https://checkout.paystack.com/xxxxx",
                "access_code": "xxxxx",
                "amount": 5000.0,
                "reference": "ref_xxxxx",
                "message": "Payment initiated. Use authorization_url to complete payment."
            }
        }


class PaymentVerificationResponse(BaseModel):
    """Response for payment verification."""
    status: str  # "success"
    payment_id: int
    payment_status: str  # SUCCESS, FAILED, etc.
    message: str
    student_status: Optional[str] = None  # Updated user status
    subscription_id: Optional[int] = None

    class Config:
        json_schema_extra = {
            "example": {
                "status": "success",
                "payment_id": 1,
                "payment_status": "SUCCESS",
                "message": "Payment verified successfully",
                "student_status": "ACTIVE_SUBSCRIBER",
                "subscription_id": 1
            }
        }


class SubscriptionStatusResponse(BaseModel):
    """Response for subscription status check."""
    status: str  # "success"
    has_active_subscription: bool
    is_expired: Optional[bool] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    days_remaining: Optional[int] = None
    message: str

    class Config:
        json_schema_extra = {
            "example": {
                "status": "success",
                "has_active_subscription": True,
                "is_expired": False,
                "start_date": "2024-01-01T00:00:00",
                "end_date": "2024-01-31T00:00:00",
                "days_remaining": 15,
                "message": "Active subscription found"
            }
        }


class HomeworkSubmissionResponse(BaseModel):
    """Response for homework submission."""
    status: str  # "success"
    homework_id: int
    student_id: int
    subject: str
    submission_type: str  # TEXT, IMAGE
    payment_type: str  # ONE_TIME, SUBSCRIPTION
    payment_required: bool
    message: str
    authorization_url: Optional[str] = None  # If payment required

    class Config:
        json_schema_extra = {
            "example": {
                "status": "success",
                "homework_id": 1,
                "student_id": 1,
                "subject": "Mathematics",
                "submission_type": "TEXT",
                "payment_type": "SUBSCRIPTION",
                "payment_required": False,
                "message": "Homework submitted successfully"
            }
        }
