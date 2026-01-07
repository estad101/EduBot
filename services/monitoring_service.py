"""
Monitoring service - Track errors, performance, and health in production.
"""
import time
import psutil
import json
import logging
from datetime import datetime
from typing import Dict, Any, Optional
from dataclasses import dataclass, asdict
from config.settings import settings
from utils.logger import get_logger

logger = get_logger("monitoring")


@dataclass
class PerformanceMetric:
    """Performance metric data point."""
    endpoint: str
    method: str
    status_code: int
    response_time_ms: float
    timestamp: datetime
    request_id: str
    error: Optional[str] = None


@dataclass
class HealthStatus:
    """Health check result."""
    service: str
    status: str  # "healthy", "degraded", "down"
    message: str
    response_time_ms: float
    timestamp: datetime


class MonitoringService:
    """Service for production monitoring."""
    
    # Store recent metrics in memory (last 1000)
    metrics_buffer = []
    MAX_METRICS = 1000
    
    # Store health check results
    health_status = {}
    
    @staticmethod
    def record_request(
        endpoint: str,
        method: str,
        status_code: int,
        response_time_ms: float,
        request_id: str,
        error: Optional[str] = None,
    ):
        """Record API request metric."""
        metric = PerformanceMetric(
            endpoint=endpoint,
            method=method,
            status_code=status_code,
            response_time_ms=response_time_ms,
            timestamp=datetime.utcnow(),
            request_id=request_id,
            error=error,
        )
        
        MonitoringService.metrics_buffer.append(metric)
        
        # Keep buffer size manageable
        if len(MonitoringService.metrics_buffer) > MonitoringService.MAX_METRICS:
            MonitoringService.metrics_buffer.pop(0)
        
        # Log slow requests
        if response_time_ms > 1000:  # > 1 second
            logger.warning(
                f"Slow request: {method} {endpoint} took {response_time_ms}ms",
                extra={
                    "endpoint": endpoint,
                    "method": method,
                    "response_time_ms": response_time_ms,
                    "status_code": status_code,
                }
            )
        
        # Log errors
        if status_code >= 400:
            logger.error(
                f"Request error: {method} {endpoint} returned {status_code}",
                extra={
                    "endpoint": endpoint,
                    "method": method,
                    "status_code": status_code,
                    "error": error,
                }
            )
    
    @staticmethod
    def get_metrics_summary() -> Dict[str, Any]:
        """Get summary of recent metrics."""
        if not MonitoringService.metrics_buffer:
            return {
                "total_requests": 0,
                "error_rate": 0,
                "average_response_time": 0,
                "endpoints": {},
            }
        
        metrics = MonitoringService.metrics_buffer
        total = len(metrics)
        errors = sum(1 for m in metrics if m.status_code >= 400)
        avg_time = sum(m.response_time_ms for m in metrics) / total if total > 0 else 0
        
        # Group by endpoint
        endpoints = {}
        for metric in metrics:
            key = f"{metric.method} {metric.endpoint}"
            if key not in endpoints:
                endpoints[key] = {
                    "count": 0,
                    "errors": 0,
                    "avg_response_time": 0,
                    "last_seen": None,
                }
            
            endpoints[key]["count"] += 1
            if metric.status_code >= 400:
                endpoints[key]["errors"] += 1
            endpoints[key]["last_seen"] = metric.timestamp.isoformat()
        
        # Calculate averages per endpoint
        for key in endpoints:
            endpoint_metrics = [m for m in metrics if f"{m.method} {m.endpoint}" == key]
            endpoints[key]["avg_response_time"] = (
                sum(m.response_time_ms for m in endpoint_metrics) / len(endpoint_metrics)
                if endpoint_metrics else 0
            )
        
        return {
            "total_requests": total,
            "error_rate": (errors / total * 100) if total > 0 else 0,
            "average_response_time": avg_time,
            "endpoints": endpoints,
            "timestamp": datetime.utcnow().isoformat(),
        }
    
    @staticmethod
    def get_system_metrics() -> Dict[str, Any]:
        """Get system resource metrics."""
        try:
            # CPU
            cpu_percent = psutil.cpu_percent(interval=0.1)
            
            # Memory
            memory = psutil.virtual_memory()
            
            # Disk
            disk = psutil.disk_usage('/')
            
            # Process
            process = psutil.Process()
            process_memory = process.memory_info()
            process_cpu = process.cpu_percent()
            
            return {
                "cpu": {
                    "percent": cpu_percent,
                    "cores": psutil.cpu_count(),
                },
                "memory": {
                    "percent": memory.percent,
                    "total_gb": memory.total / (1024**3),
                    "used_gb": memory.used / (1024**3),
                    "available_gb": memory.available / (1024**3),
                },
                "disk": {
                    "percent": disk.percent,
                    "total_gb": disk.total / (1024**3),
                    "used_gb": disk.used / (1024**3),
                    "free_gb": disk.free / (1024**3),
                },
                "process": {
                    "memory_mb": process_memory.rss / (1024**2),
                    "cpu_percent": process_cpu,
                    "num_threads": process.num_threads(),
                },
                "timestamp": datetime.utcnow().isoformat(),
            }
        except Exception as e:
            logger.error(f"Error getting system metrics: {str(e)}")
            return {}
    
    @staticmethod
    def update_health_status(
        service: str,
        status: str,
        message: str,
        response_time_ms: float,
    ):
        """Update health status for a service."""
        health = HealthStatus(
            service=service,
            status=status,
            message=message,
            response_time_ms=response_time_ms,
            timestamp=datetime.utcnow(),
        )
        
        MonitoringService.health_status[service] = health
        
        # Log health issues
        if status != "healthy":
            logger.warning(
                f"Service health issue: {service} - {message}",
                extra={
                    "service": service,
                    "status": status,
                    "response_time_ms": response_time_ms,
                }
            )
    
    @staticmethod
    def get_health_status() -> Dict[str, Any]:
        """Get health status of all services."""
        status_dict = {
            k: {
                "status": v.status,
                "message": v.message,
                "response_time_ms": v.response_time_ms,
                "timestamp": v.timestamp.isoformat(),
            }
            for k, v in MonitoringService.health_status.items()
        }
        
        # Overall status
        overall = "healthy"
        if any(v["status"] == "down" for v in status_dict.values()):
            overall = "down"
        elif any(v["status"] == "degraded" for v in status_dict.values()):
            overall = "degraded"
        
        return {
            "overall_status": overall,
            "services": status_dict,
            "timestamp": datetime.utcnow().isoformat(),
        }
    
    @staticmethod
    def check_database_health(db) -> tuple[str, str, float]:
        """Check database health."""
        try:
            start = time.time()
            db.execute("SELECT 1")
            response_time = (time.time() - start) * 1000
            return "healthy", "Database connection OK", response_time
        except Exception as e:
            logger.error(f"Database health check failed: {str(e)}")
            return "down", f"Database connection failed: {str(e)}", 0
    
    @staticmethod
    def check_whatsapp_health() -> tuple[str, str, float]:
        """Check WhatsApp API health."""
        try:
            if not settings.whatsapp_api_key:
                return "degraded", "WhatsApp API key not configured", 0
            
            # Just verify credentials exist - don't make actual API call
            return "healthy", "WhatsApp API configured", 0
        except Exception as e:
            return "degraded", f"WhatsApp check failed: {str(e)}", 0
    
    @staticmethod
    def check_paystack_health() -> tuple[str, str, float]:
        """Check Paystack API health."""
        try:
            if not settings.paystack_secret_key:
                return "degraded", "Paystack API key not configured", 0
            
            # Just verify credentials exist
            return "healthy", "Paystack API configured", 0
        except Exception as e:
            return "degraded", f"Paystack check failed: {str(e)}", 0


# Initialize Sentry if configured
def init_sentry():
    """Initialize Sentry error tracking."""
    try:
        import sentry_sdk
        from sentry_sdk.integrations.fastapi import FastApiIntegration
        from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration
        
        sentry_dsn = getattr(settings, 'sentry_dsn', None)
        
        if sentry_dsn:
            sentry_sdk.init(
                dsn=sentry_dsn,
                integrations=[
                    FastApiIntegration(),
                    SqlalchemyIntegration(),
                ],
                traces_sample_rate=0.1,  # 10% of transactions
                environment=getattr(settings, 'environment', 'production'),
            )
            logger.info("Sentry initialized successfully")
        else:
            logger.info("Sentry DSN not configured - error tracking disabled")
    except Exception as e:
        logger.error(f"Failed to initialize Sentry: {str(e)}")
