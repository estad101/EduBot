"""
Payment request schemas for validation.
"""
from pydantic import BaseModel, field_validator
from typing import Optional
from decimal import Decimal


class PaymentInitiationRequest(BaseModel):
    """Request to initiate a payment."""
    student_id: int
    amount: float  # In naira (will be converted to kobo)
    is_subscription: bool = False
    email: Optional[str] = None
    metadata: Optional[dict] = None

    @field_validator("amount")
    @classmethod
    def validate_amount(cls, v: float) -> float:
        """Validate payment amount."""
        if v <= 0:
            raise ValueError("Amount must be greater than 0")
        if v > 1000000:  # Sanity check - max 1M naira
            raise ValueError("Amount exceeds maximum limit")
        return v

    class Config:
        json_schema_extra = {
            "example": {
                "student_id": 1,
                "amount": 5000.0,
                "is_subscription": False,
                "email": "john@example.com"
            }
        }


class PaymentVerificationRequest(BaseModel):
    """Request to verify a payment."""
    reference: str
    student_id: int

    @field_validator("reference")
    @classmethod
    def validate_reference(cls, v: str) -> str:
        """Validate payment reference."""
        if len(v.strip()) < 5:
            raise ValueError("Invalid payment reference")
        return v.strip()

    class Config:
        json_schema_extra = {
            "example": {
                "reference": "ref_1234567890",
                "student_id": 1
            }
        }


class PaystackWebhookRequest(BaseModel):
    """Request for Paystack webhook."""
    event: str
    data: dict

    class Config:
        json_schema_extra = {
            "example": {
                "event": "charge.success",
                "data": {
                    "id": 123456,
                    "reference": "ref_xxxxx",
                    "amount": 500000,
                    "status": "success"
                }
            }
        }
