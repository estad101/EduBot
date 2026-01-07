"""
File handling utilities for homework submissions.
"""
import os
import aiofiles
from pathlib import Path
from config.settings import settings
from utils.logger import get_logger
from utils.validators import sanitize_filename

logger = get_logger("file_handler")


async def save_homework_file(student_id: int, file_content: bytes, filename: str) -> str:
    """
    Save homework file to disk.
    
    Args:
        student_id: Student ID
        file_content: File bytes
        filename: Original filename
    
    Returns:
        File path relative to uploads directory
    
    Raises:
        ValueError: If file is too large or invalid
    """
    # Validate file size
    file_size_mb = len(file_content) / (1024 * 1024)
    if file_size_mb > settings.max_file_size_mb:
        raise ValueError(f"File exceeds maximum size of {settings.max_file_size_mb}MB")
    
    # Create student homework directory
    student_dir = Path(settings.uploads_dir) / "homework" / str(student_id)
    student_dir.mkdir(parents=True, exist_ok=True)
    
    # Sanitize filename
    safe_filename = sanitize_filename(filename)
    
    # Build full path
    file_path = student_dir / safe_filename
    
    # Save file
    try:
        async with aiofiles.open(file_path, "wb") as f:
            await f.write(file_content)
        
        logger.info(f"File saved for student {student_id}: {safe_filename}")
        
        # Return relative path for storage in database
        return str(file_path).replace("\\", "/")
    except Exception as e:
        logger.error(f"Error saving file for student {student_id}: {str(e)}")
        raise ValueError(f"Failed to save file: {str(e)}")


async def delete_homework_file(file_path: str) -> bool:
    """
    Delete a homework file.
    
    Args:
        file_path: File path to delete
    
    Returns:
        True if successful, False otherwise
    """
    try:
        file_full_path = Path(file_path)
        if file_full_path.exists():
            file_full_path.unlink()
            logger.info(f"File deleted: {file_path}")
            return True
        else:
            logger.warning(f"File not found: {file_path}")
            return False
    except Exception as e:
        logger.error(f"Error deleting file {file_path}: {str(e)}")
        return False


def validate_image_file(mime_type: str, file_size_bytes: int) -> tuple[bool, str]:
    """
    Validate image file before saving.
    
    Args:
        mime_type: MIME type of file (e.g., 'image/jpeg')
        file_size_bytes: File size in bytes
    
    Returns:
        Tuple of (is_valid, error_message)
    """
    # Check MIME type
    if mime_type not in settings.allowed_mime_types:
        return False, f"Invalid image type. Allowed types: {', '.join(settings.allowed_mime_types)}"
    
    # Check file size
    max_bytes = settings.max_file_size_mb * 1024 * 1024
    if file_size_bytes > max_bytes:
        return False, f"File exceeds maximum size of {settings.max_file_size_mb}MB"
    
    if file_size_bytes == 0:
        return False, "File is empty"
    
    return True, ""
