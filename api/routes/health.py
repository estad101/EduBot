"""
Health check routes - Monitor system health and performance.
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
import time
from typing import Dict, Any
from config.database import get_db
from services.monitoring_service import MonitoringService
from schemas.response import StandardResponse
from utils.logger import get_logger

router = APIRouter(prefix="/api/health", tags=["health"])
logger = get_logger("health_routes")


@router.get("/status")
async def health_status(db: Session = Depends(get_db)):
    """
    Get overall health status of the application.
    
    Returns status of:
    - Database connection
    - WhatsApp API
    - Paystack API
    - System resources
    """
    try:
        # Check services
        db_status, db_msg, db_time = MonitoringService.check_database_health(db)
        whatsapp_status, whatsapp_msg, _ = MonitoringService.check_whatsapp_health()
        paystack_status, paystack_msg, _ = MonitoringService.check_paystack_health()
        
        # Update health status
        MonitoringService.update_health_status("database", db_status, db_msg, db_time)
        MonitoringService.update_health_status("whatsapp", whatsapp_status, whatsapp_msg, 0)
        MonitoringService.update_health_status("paystack", paystack_status, paystack_msg, 0)
        
        # Get health status
        health = MonitoringService.get_health_status()
        
        return StandardResponse(
            status="success",
            message="Health check complete",
            data=health,
        )
    except Exception as e:
        logger.error(f"Health check error: {str(e)}")
        return StandardResponse(
            status="error",
            message=f"Health check failed: {str(e)}",
            error_code="HEALTH_CHECK_ERROR",
        )


@router.get("/metrics")
async def get_metrics():
    """
    Get performance metrics from last requests.
    
    Returns:
    - Total requests
    - Error rate
    - Average response time
    - Per-endpoint statistics
    """
    try:
        metrics = MonitoringService.get_metrics_summary()
        
        return StandardResponse(
            status="success",
            message="Performance metrics",
            data=metrics,
        )
    except Exception as e:
        logger.error(f"Metrics error: {str(e)}")
        return StandardResponse(
            status="error",
            message=f"Failed to get metrics: {str(e)}",
            error_code="METRICS_ERROR",
        )


@router.get("/system")
async def get_system_metrics():
    """
    Get system resource usage.
    
    Returns:
    - CPU usage
    - Memory usage
    - Disk usage
    - Process-specific metrics
    """
    try:
        metrics = MonitoringService.get_system_metrics()
        
        return StandardResponse(
            status="success",
            message="System metrics",
            data=metrics,
        )
    except Exception as e:
        logger.error(f"System metrics error: {str(e)}")
        return StandardResponse(
            status="error",
            message=f"Failed to get system metrics: {str(e)}",
            error_code="SYSTEM_METRICS_ERROR",
        )


@router.get("/ping")
async def ping():
    """Quick ping to check if server is alive."""
    return {"status": "alive", "timestamp": time.time()}


@router.get("/ready")
async def readiness(db: Session = Depends(get_db)):
    """
    Kubernetes-style readiness probe.
    Returns 200 only if system is ready to accept requests.
    """
    try:
        # Quick database check
        db.execute(text("SELECT 1"))
        
        return {
            "ready": True,
            "timestamp": time.time(),
        }
    except Exception as e:
        logger.error(f"Readiness check failed: {str(e)}")
        return {
            "ready": False,
            "error": str(e),
            "timestamp": time.time(),
        }
