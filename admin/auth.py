"""
Admin authentication and authorization.
"""
from functools import wraps
from fastapi import Request, HTTPException
from starlette.responses import RedirectResponse
from config.settings import settings
from utils.logger import get_logger
import time
import os
from datetime import datetime, timedelta

logger = get_logger("admin_auth")


class AdminAuth:
    """Admin authentication manager with rate limiting and security features."""
    
    ADMIN_USERNAME = "admin"
    # Allow admin password to be set via environment variable, default to "marriage2020!"
    ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "marriage2020!")
    ADMIN_SESSION_KEY = "admin_session"
    FAILED_ATTEMPTS = {}  # Track failed login attempts by IP
    MAX_FAILED_ATTEMPTS = 5
    LOCKOUT_DURATION = 900  # 15 minutes in seconds
    
    @staticmethod
    def verify_credentials(username: str, password: str, ip_address: str = None) -> tuple:
        """Verify admin credentials with rate limiting.
        Returns (is_valid: bool, message: str)
        """
        # Check if IP is locked out
        if ip_address:
            if ip_address in AdminAuth.FAILED_ATTEMPTS:
                attempt_data = AdminAuth.FAILED_ATTEMPTS[ip_address]
                if attempt_data['count'] >= AdminAuth.MAX_FAILED_ATTEMPTS:
                    lockout_time = attempt_data['timestamp'] + AdminAuth.LOCKOUT_DURATION
                    if time.time() < lockout_time:
                        remaining = int(lockout_time - time.time())
                        logger.warning(f"IP {ip_address} locked out - {remaining}s remaining")
                        return False, f"Too many failed attempts. Try again in {remaining} seconds."
                    else:
                        # Reset after lockout period
                        del AdminAuth.FAILED_ATTEMPTS[ip_address]
        
        # Verify credentials
        is_valid = (
            username == AdminAuth.ADMIN_USERNAME and 
            password == AdminAuth.ADMIN_PASSWORD
        )
        
        if not is_valid:
            # Track failed attempt
            if ip_address:
                if ip_address not in AdminAuth.FAILED_ATTEMPTS:
                    AdminAuth.FAILED_ATTEMPTS[ip_address] = {'count': 0, 'timestamp': time.time()}
                AdminAuth.FAILED_ATTEMPTS[ip_address]['count'] += 1
                AdminAuth.FAILED_ATTEMPTS[ip_address]['timestamp'] = time.time()
            logger.warning(f"Failed login attempt for user '{username}' from IP {ip_address}")
            return False, "Invalid username or password"
        
        # Clear failed attempts on successful login
        if ip_address and ip_address in AdminAuth.FAILED_ATTEMPTS:
            del AdminAuth.FAILED_ATTEMPTS[ip_address]
        
        return True, "Login successful"
    
    @staticmethod
    def create_session(request: Request, session_token: str, ip_address: str = None) -> None:
        """Create admin session with IP tracking and timestamp."""
        request.session[AdminAuth.ADMIN_SESSION_KEY] = session_token
        request.session["admin_ip"] = ip_address
        request.session["admin_login_time"] = datetime.utcnow().isoformat()
        logger.info(f"Admin session created from IP: {ip_address}")
    
    @staticmethod
    def is_authenticated(request: Request, ip_address: str = None) -> bool:
        """Check if request is authenticated with session validation."""
        if AdminAuth.ADMIN_SESSION_KEY not in request.session:
            return False
        
        # Validate IP address hasn't changed (IP spoofing check)
        if ip_address and "admin_ip" in request.session:
            if request.session["admin_ip"] != ip_address:
                logger.warning(f"IP mismatch detected for session - possible session hijacking")
                return False
        
        # Check session timeout (1 hour)
        if "admin_login_time" in request.session:
            try:
                login_time = datetime.fromisoformat(request.session["admin_login_time"])
                if datetime.utcnow() - login_time > timedelta(hours=1):
                    logger.info("Admin session expired due to timeout")
                    return False
            except (ValueError, TypeError):
                return False
        
        return True
    
    @staticmethod
    def destroy_session(request: Request) -> None:
        """Destroy admin session securely."""
        if AdminAuth.ADMIN_SESSION_KEY in request.session:
            ip = request.session.get("admin_ip", "unknown")
            del request.session[AdminAuth.ADMIN_SESSION_KEY]
            if "admin_ip" in request.session:
                del request.session["admin_ip"]
            if "admin_login_time" in request.session:
                del request.session["admin_login_time"]
            logger.info(f"Admin session destroyed from IP: {ip}")


def require_admin(func):
    """Decorator to require admin authentication."""
    @wraps(func)
    async def wrapper(request: Request, *args, **kwargs):
        if not AdminAuth.is_authenticated(request):
            return RedirectResponse(url="/admin/login", status_code=302)
        return await func(request, *args, **kwargs)
    return wrapper


def admin_session_required(func):
    """Decorator for API endpoints requiring admin auth."""
    @wraps(func)
    async def wrapper(request: Request, *args, **kwargs):
        if not AdminAuth.is_authenticated(request):
            raise HTTPException(status_code=401, detail="Unauthorized")
        return await func(request, *args, **kwargs)
    return wrapper
