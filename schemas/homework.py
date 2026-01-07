"""
Homework request schemas for validation.
"""
from pydantic import BaseModel, field_validator
from typing import Optional


class HomeworkSubmissionRequest(BaseModel):
    """Request for homework submission."""
    student_id: int
    subject: str
    submission_type: str  # TEXT or IMAGE
    content: Optional[str] = None  # For TEXT submissions
    file_path: Optional[str] = None  # For IMAGE submissions (sent by n8n after download)
    file_size_bytes: Optional[int] = None  # File size for validation

    @field_validator("subject")
    @classmethod
    def validate_subject(cls, v: str) -> str:
        """Validate subject."""
        if len(v.strip()) < 1 or len(v.strip()) > 255:
            raise ValueError("Subject must be 1-255 characters")
        return v.strip()

    @field_validator("submission_type")
    @classmethod
    def validate_submission_type(cls, v: str) -> str:
        """Validate submission type."""
        if v.upper() not in ["TEXT", "IMAGE"]:
            raise ValueError("Submission type must be TEXT or IMAGE")
        return v.upper()

    @field_validator("content")
    @classmethod
    def validate_content(cls, v: Optional[str]) -> Optional[str]:
        """Validate text content."""
        if v is not None and len(v.strip()) < 1:
            raise ValueError("Content must not be empty for TEXT submissions")
        return v

    class Config:
        json_schema_extra = {
            "example": {
                "student_id": 1,
                "subject": "Mathematics",
                "submission_type": "TEXT",
                "content": "Here is my homework solution..."
            }
        }
