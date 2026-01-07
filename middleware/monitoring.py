"""
Monitoring middleware - Track all requests for performance and error monitoring.
"""
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
import time
import uuid
import logging
from services.monitoring_service import MonitoringService

logger = logging.getLogger("monitoring")


class MonitoringMiddleware(BaseHTTPMiddleware):
    """Track request metrics and performance."""
    
    async def dispatch(self, request: Request, call_next):
        """Process request and track metrics."""
        # Generate request ID for tracing
        request_id = str(uuid.uuid4())
        
        # Start timer
        start_time = time.time()
        
        # Add request ID to request state
        request.state.request_id = request_id
        
        try:
            # Process request
            response = await call_next(request)
            
            # Calculate response time
            response_time_ms = (time.time() - start_time) * 1000
            
            # Record metric
            MonitoringService.record_request(
                endpoint=request.url.path,
                method=request.method,
                status_code=response.status_code,
                response_time_ms=response_time_ms,
                request_id=request_id,
            )
            
            # Add request ID to response headers
            response.headers["X-Request-ID"] = request_id
            
            return response
            
        except Exception as e:
            # Calculate response time
            response_time_ms = (time.time() - start_time) * 1000
            
            # Record error
            MonitoringService.record_request(
                endpoint=request.url.path,
                method=request.method,
                status_code=500,
                response_time_ms=response_time_ms,
                request_id=request_id,
                error=str(e),
            )
            
            # Re-raise exception
            raise
