"""
Input validation utilities.
"""
import re
from typing import Tuple
from utils.logger import get_logger

logger = get_logger("validators")


def validate_phone_number(phone_number: str) -> Tuple[bool, str]:
    """
    Validate phone number format.
    
    Args:
        phone_number: Phone number string
    
    Returns:
        Tuple of (is_valid, error_message)
    """
    # Remove spaces, dashes, parentheses
    cleaned = re.sub(r"[\s\-\(\)]", "", phone_number)
    
    # Must start with + and contain only digits after that, 10-15 digits total
    if not re.match(r"^\+\d{10,15}$", cleaned):
        return False, "Phone number must be in format: +234901234567 (with country code, 10-15 digits)"
    
    return True, ""


def validate_email(email: str) -> Tuple[bool, str]:
    """
    Validate email format.
    
    Args:
        email: Email string
    
    Returns:
        Tuple of (is_valid, error_message)
    """
    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    if not re.match(pattern, email):
        return False, "Invalid email format"
    
    if len(email) > 255:
        return False, "Email too long (max 255 characters)"
    
    return True, ""


def validate_file_extension(filename: str, allowed_extensions: list) -> Tuple[bool, str]:
    """
    Validate file extension.
    
    Args:
        filename: Original filename
        allowed_extensions: List of allowed extensions (e.g., ['jpg', 'png', 'webp'])
    
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not filename:
        return False, "Filename is empty"
    
    ext = filename.split(".")[-1].lower()
    if ext not in allowed_extensions:
        return False, f"File type not allowed. Allowed types: {', '.join(allowed_extensions)}"
    
    return True, ""


def sanitize_filename(filename: str) -> str:
    """
    Sanitize filename to prevent directory traversal attacks.
    
    Args:
        filename: Original filename
    
    Returns:
        Sanitized filename
    """
    # Remove path separators and special characters
    sanitized = re.sub(r"[^a-zA-Z0-9._-]", "_", filename)
    
    # Remove leading dots to prevent hidden files
    sanitized = sanitized.lstrip(".")
    
    # Limit length
    if len(sanitized) > 255:
        name, ext = sanitized.rsplit(".", 1) if "." in sanitized else (sanitized, "")
        sanitized = name[:250] + ("." + ext if ext else "")
    
    return sanitized
