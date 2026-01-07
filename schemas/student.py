"""
Student request schemas for validation.
"""
from pydantic import BaseModel, EmailStr, field_validator
from typing import Optional
import re


class UserIdentificationRequest(BaseModel):
    """Request for identifying a user by phone number."""
    phone_number: str

    @field_validator("phone_number")
    @classmethod
    def validate_phone(cls, v: str) -> str:
        """Validate phone number format."""
        # Remove spaces, dashes, parentheses
        v = re.sub(r"[\s\-\(\)]", "", v)
        
        # Must start with + and contain only digits after that
        if not re.match(r"^\+\d{10,15}$", v):
            raise ValueError("Phone number must be in format: +234901234567 (with country code, 10-15 digits)")
        return v

    class Config:
        json_schema_extra = {
            "example": {"phone_number": "+234901234567"}
        }


class StudentRegistrationRequest(BaseModel):
    """Request for student registration."""
    phone_number: str
    full_name: str
    email: EmailStr
    class_grade: str

    @field_validator("phone_number")
    @classmethod
    def validate_phone(cls, v: str) -> str:
        """Validate phone number format."""
        v = re.sub(r"[\s\-\(\)]", "", v)
        if not re.match(r"^\+\d{10,15}$", v):
            raise ValueError("Phone number must be in format: +234901234567")
        return v

    @field_validator("full_name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        """Validate full name."""
        if len(v.strip()) < 3:
            raise ValueError("Full name must be at least 3 characters")
        if len(v.strip()) > 255:
            raise ValueError("Full name must not exceed 255 characters")
        return v.strip()

    @field_validator("class_grade")
    @classmethod
    def validate_grade(cls, v: str) -> str:
        """Validate class/grade."""
        if len(v.strip()) < 1 or len(v.strip()) > 100:
            raise ValueError("Class/grade must be 1-100 characters")
        return v.strip()

    class Config:
        json_schema_extra = {
            "example": {
                "phone_number": "+234901234567",
                "full_name": "John Doe",
                "email": "john@example.com",
                "class_grade": "10A"
            }
        }
