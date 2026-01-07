"""
Security utilities - webhook signatures, hashing, validation, CSRF tokens, and session management.
"""
import hmac
import hashlib
import json
import secrets
import time
from datetime import datetime, timedelta
from typing import Dict, Tuple
from fastapi import Request
from config.settings import settings
from utils.logger import get_logger

logger = get_logger("security")

# In-memory CSRF token store (in production, use Redis)
csrf_tokens: Dict[str, Dict[str, any]] = {}

# In-memory session store with timeout (in production, use Redis)
session_store: Dict[str, Dict[str, any]] = {}

# Failed login attempts tracking
failed_attempts: Dict[str, Dict[str, any]] = {}


def verify_paystack_webhook_signature(payload_body: str, signature: str) -> bool:
    """
    Verify Paystack webhook signature.
    
    Paystack signs payloads with HMAC-SHA512.
    Signature should match: HMAC-SHA512(secret, payload)
    
    Args:
        payload_body: Raw request body as string
        signature: X-Paystack-Signature header value
    
    Returns:
        True if signature is valid, False otherwise
    """
    try:
        secret = settings.paystack_webhook_secret.encode()
        body = payload_body.encode() if isinstance(payload_body, str) else payload_body
        
        # Compute HMAC-SHA512
        computed_hash = hmac.new(
            secret,
            body,
            hashlib.sha512
        ).hexdigest()
        
        # Use constant-time comparison to prevent timing attacks
        is_valid = hmac.compare_digest(computed_hash, signature)
        
        if not is_valid:
            logger.warning(f"Invalid Paystack webhook signature. Expected: {computed_hash}, Got: {signature}")
        
        return is_valid
    except Exception as e:
        logger.error(f"Error verifying webhook signature: {str(e)}")
        return False


def hash_payment_reference(reference: str) -> str:
    """Generate a hash of payment reference for storage."""
    return hashlib.sha256(reference.encode()).hexdigest()


def generate_idempotency_key(student_id: int, amount: float, timestamp: str) -> str:
    """
    Generate an idempotency key to prevent duplicate payments.
    
    Args:
        student_id: Student ID
        amount: Payment amount
        timestamp: ISO timestamp
    
    Returns:
        Idempotency key
    """
    data = f"{student_id}_{amount}_{timestamp}".encode()
    return hashlib.sha256(data).hexdigest()


# ==================== CSRF TOKEN FUNCTIONS ====================

def generate_csrf_token(session_id: str) -> str:
    """
    Generate a CSRF token for a session.
    
    Args:
        session_id: Unique session identifier
        
    Returns:
        CSRF token string
    """
    token = secrets.token_urlsafe(32)
    csrf_tokens[token] = {
        "session_id": session_id,
        "created_at": datetime.utcnow(),
        "used": False
    }
    
    # Clean up expired tokens (older than 1 hour)
    now = datetime.utcnow()
    expired = [t for t, data in csrf_tokens.items() 
               if (now - data["created_at"]).total_seconds() > 3600]
    for t in expired:
        del csrf_tokens[t]
    
    logger.info(f"CSRF token generated for session {session_id}")
    return token


def validate_csrf_token(token: str, session_id: str) -> bool:
    """
    Validate a CSRF token.
    
    Args:
        token: CSRF token to validate
        session_id: Session ID to verify against
        
    Returns:
        True if token is valid, False otherwise
    """
    if token not in csrf_tokens:
        logger.warning(f"Invalid CSRF token submitted from session {session_id}")
        return False
    
    token_data = csrf_tokens[token]
    
    # Check if token matches session
    if token_data["session_id"] != session_id:
        logger.warning(f"CSRF token session mismatch: {session_id}")
        return False
    
    # Check if token is expired (1 hour)
    if (datetime.utcnow() - token_data["created_at"]).total_seconds() > 3600:
        logger.warning(f"CSRF token expired for session {session_id}")
        del csrf_tokens[token]
        return False
    
    # Token can only be used once
    if token_data["used"]:
        logger.warning(f"CSRF token reuse attempt from session {session_id}")
        return False
    
    # Mark token as used
    token_data["used"] = True
    logger.info(f"CSRF token validated and consumed for session {session_id}")
    return True


# ==================== SESSION MANAGEMENT ====================

def create_session(session_id: str, user_id: str, ip_address: str, 
                   timeout_minutes: int = 60) -> None:
    """
    Create a new session with timeout and IP binding.
    
    Args:
        session_id: Unique session identifier
        user_id: User ID (e.g., 'admin')
        ip_address: Client IP address for validation
        timeout_minutes: Session timeout in minutes
    """
    session_store[session_id] = {
        "user_id": user_id,
        "ip_address": ip_address,
        "created_at": datetime.utcnow(),
        "last_activity": datetime.utcnow(),
        "timeout_minutes": timeout_minutes
    }
    logger.info(f"Session created: {session_id} for user {user_id} from IP {ip_address}")


def validate_session(session_id: str, ip_address: str, 
                    timeout_minutes: int = 60) -> Tuple[bool, str]:
    """
    Validate an existing session.
    
    Args:
        session_id: Session ID to validate
        ip_address: Current client IP address
        timeout_minutes: Session timeout in minutes
        
    Returns:
        Tuple of (is_valid, message)
    """
    if session_id not in session_store:
        return False, "Session not found"
    
    session = session_store[session_id]
    now = datetime.utcnow()
    
    # Check IP address (IP spoofing protection)
    if session["ip_address"] != ip_address:
        logger.warning(f"Session IP mismatch for {session_id}: "
                      f"expected {session['ip_address']}, got {ip_address}")
        del session_store[session_id]
        return False, "IP address mismatch - session invalidated"
    
    # Check timeout
    created_at = session["created_at"]
    elapsed_minutes = (now - created_at).total_seconds() / 60
    
    if elapsed_minutes > timeout_minutes:
        logger.warning(f"Session timeout for {session_id} after {elapsed_minutes} minutes")
        del session_store[session_id]
        return False, "Session expired"
    
    # Update last activity
    session["last_activity"] = now
    return True, "Session valid"


def invalidate_session(session_id: str) -> None:
    """
    Invalidate a session (logout).
    
    Args:
        session_id: Session ID to invalidate
    """
    if session_id in session_store:
        user_id = session_store[session_id].get("user_id", "unknown")
        del session_store[session_id]
        logger.info(f"Session invalidated: {session_id} for user {user_id}")


# ==================== LOGIN RATE LIMITING ====================

def track_failed_login(ip_address: str, max_attempts: int = 5, 
                      lockout_minutes: int = 15) -> Tuple[bool, str]:
    """
    Track failed login attempts and enforce rate limiting.
    
    Args:
        ip_address: Client IP address
        max_attempts: Maximum failed attempts allowed
        lockout_minutes: Lockout duration in minutes
        
    Returns:
        Tuple of (is_allowed, message)
    """
    now = datetime.utcnow()
    
    if ip_address not in failed_attempts:
        failed_attempts[ip_address] = {
            "count": 0,
            "first_attempt": now,
            "locked_until": None
        }
    
    attempt_data = failed_attempts[ip_address]
    
    # Check if IP is locked out
    if attempt_data["locked_until"] and now < attempt_data["locked_until"]:
        remaining = (attempt_data["locked_until"] - now).total_seconds() / 60
        logger.warning(f"Login attempt from locked IP {ip_address}: "
                      f"{remaining:.1f} minutes remaining")
        return False, f"Too many failed attempts. Try again in {int(remaining)} minutes."
    
    # Reset if lockout period expired
    if attempt_data["locked_until"] and now >= attempt_data["locked_until"]:
        attempt_data["count"] = 0
        attempt_data["locked_until"] = None
    
    # Check if we've exceeded max attempts
    if attempt_data["count"] >= max_attempts:
        attempt_data["locked_until"] = now + timedelta(minutes=lockout_minutes)
        logger.warning(f"IP {ip_address} locked out after {max_attempts} failed attempts")
        return False, f"Too many failed attempts. Try again in {lockout_minutes} minutes."
    
    return True, "Attempt allowed"


def record_failed_login(ip_address: str) -> None:
    """
    Record a failed login attempt.
    
    Args:
        ip_address: Client IP address
    """
    if ip_address not in failed_attempts:
        failed_attempts[ip_address] = {
            "count": 0,
            "first_attempt": datetime.utcnow(),
            "locked_until": None
        }
    
    failed_attempts[ip_address]["count"] += 1
    logger.warning(f"Failed login attempt from IP {ip_address}: "
                  f"{failed_attempts[ip_address]['count']} attempts")


def clear_failed_login(ip_address: str) -> None:
    """
    Clear failed login attempts after successful login.
    
    Args:
        ip_address: Client IP address
    """
    if ip_address in failed_attempts:
        del failed_attempts[ip_address]
        logger.info(f"Failed login attempts cleared for IP {ip_address}")


# ==================== UTILITY FUNCTIONS ====================

def get_client_ip(request: Request) -> str:
    """
    Get client IP address from request, considering proxies.
    
    Args:
        request: FastAPI request object
        
    Returns:
        Client IP address
    """
    # Check X-Forwarded-For header (for proxies)
    if "x-forwarded-for" in request.headers:
        return request.headers["x-forwarded-for"].split(",")[0].strip()
    
    # Fall back to client host
    return request.client.host if request.client else "unknown"
