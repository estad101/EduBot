"""
Alerting service - Send alerts for critical errors and issues.
"""
import asyncio
from datetime import datetime
from typing import Optional, List
from enum import Enum
from services.whatsapp_service import WhatsAppService
from utils.logger import get_logger
from config.settings import settings

logger = get_logger("alerting")


class AlertSeverity(str, Enum):
    """Alert severity levels."""
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"


class AlertType(str, Enum):
    """Alert types."""
    SERVICE_DOWN = "service_down"
    HIGH_ERROR_RATE = "high_error_rate"
    PAYMENT_FAILURE = "payment_failure"
    DATABASE_ERROR = "database_error"
    QUOTA_EXCEEDED = "quota_exceeded"
    CUSTOM = "custom"


class AlertingService:
    """Service for sending alerts."""
    
    # Track recent alerts to avoid spam
    recent_alerts: dict[str, datetime] = {}
    ALERT_COOLDOWN_MINUTES = 15  # Don't repeat same alert within 15 mins
    
    # Admin phone numbers to notify
    admin_numbers = getattr(settings, 'admin_alert_numbers', [])
    
    @staticmethod
    def should_send_alert(alert_key: str) -> bool:
        """Check if alert should be sent (respects cooldown)."""
        now = datetime.utcnow()
        last_alert_time = AlertingService.recent_alerts.get(alert_key)
        
        if last_alert_time is None:
            return True
        
        # Check if enough time has passed
        from datetime import timedelta
        if (now - last_alert_time).total_seconds() > (AlertingService.ALERT_COOLDOWN_MINUTES * 60):
            return True
        
        return False
    
    @staticmethod
    async def send_alert(
        alert_type: AlertType,
        severity: AlertSeverity,
        title: str,
        message: str,
        details: Optional[dict] = None,
        contact_phone: Optional[str] = None,
    ):
        """Send alert through multiple channels."""
        
        alert_key = f"{alert_type}_{severity}"
        
        if not AlertingService.should_send_alert(alert_key):
            logger.debug(f"Alert {alert_key} on cooldown, skipping")
            return
        
        AlertingService.recent_alerts[alert_key] = datetime.utcnow()
        
        # Log alert
        log_level = "critical" if severity == AlertSeverity.CRITICAL else "warning"
        getattr(logger, log_level)(
            f"[{alert_type.upper()}] {title}: {message}",
            extra={
                "alert_type": alert_type.value,
                "severity": severity.value,
                "details": details or {},
            }
        )
        
        # Send WhatsApp notification
        if contact_phone or AlertingService.admin_numbers:
            await AlertingService._send_whatsapp_alert(
                title=title,
                message=message,
                severity=severity,
                contact_phone=contact_phone,
            )
    
    @staticmethod
    async def _send_whatsapp_alert(
        title: str,
        message: str,
        severity: AlertSeverity,
        contact_phone: Optional[str] = None,
    ):
        """Send alert via WhatsApp."""
        try:
            phones = [contact_phone] if contact_phone else AlertingService.admin_numbers
            
            if not phones:
                logger.warning("No admin phones configured for alerts")
                return
            
            emoji = "🔴" if severity == AlertSeverity.CRITICAL else "🟡"
            
            alert_message = (
                f"{emoji} **ALERT: {title}**\n\n"
                f"{message}\n\n"
                f"Time: {datetime.utcnow().isoformat()}\n"
                f"Check: http://localhost:8000/admin/monitoring"
            )
            
            for phone in phones:
                try:
                    await WhatsAppService.send_message(
                        phone_number=phone,
                        message_type="text",
                        text=alert_message,
                    )
                except Exception as e:
                    logger.error(f"Failed to send WhatsApp alert to {phone}: {str(e)}")
        
        except Exception as e:
            logger.error(f"Error sending WhatsApp alert: {str(e)}")
    
    @staticmethod
    async def alert_service_down(
        service_name: str,
        error: str,
        contact_phone: Optional[str] = None,
    ):
        """Alert that a service is down."""
        await AlertingService.send_alert(
            alert_type=AlertType.SERVICE_DOWN,
            severity=AlertSeverity.CRITICAL,
            title=f"{service_name} Down",
            message=f"Service {service_name} is not responding.\n\nError: {error}",
            contact_phone=contact_phone,
        )
    
    @staticmethod
    async def alert_high_error_rate(
        endpoint: str,
        error_rate: float,
        contact_phone: Optional[str] = None,
    ):
        """Alert about high error rate on endpoint."""
        await AlertingService.send_alert(
            alert_type=AlertType.HIGH_ERROR_RATE,
            severity=AlertSeverity.WARNING,
            title="High Error Rate Detected",
            message=f"Endpoint {endpoint} has {error_rate:.1f}% error rate",
            contact_phone=contact_phone,
        )
    
    @staticmethod
    async def alert_payment_failure(
        student_id: int,
        amount: float,
        error: str,
        contact_phone: Optional[str] = None,
    ):
        """Alert about payment failure."""
        await AlertingService.send_alert(
            alert_type=AlertType.PAYMENT_FAILURE,
            severity=AlertSeverity.WARNING,
            title="Payment Processing Failed",
            message=f"Student {student_id} payment of ₦{amount} failed.\n\nReason: {error}",
            details={
                "student_id": student_id,
                "amount": amount,
            },
            contact_phone=contact_phone,
        )
    
    @staticmethod
    async def alert_database_error(
        error: str,
        contact_phone: Optional[str] = None,
    ):
        """Alert about database error."""
        await AlertingService.send_alert(
            alert_type=AlertType.DATABASE_ERROR,
            severity=AlertSeverity.CRITICAL,
            title="Database Connection Failed",
            message=f"Database error occurred:\n\n{error}",
            contact_phone=contact_phone,
        )
    
    @staticmethod
    async def alert_custom(
        title: str,
        message: str,
        severity: AlertSeverity = AlertSeverity.INFO,
        contact_phone: Optional[str] = None,
    ):
        """Send custom alert."""
        await AlertingService.send_alert(
            alert_type=AlertType.CUSTOM,
            severity=severity,
            title=title,
            message=message,
            contact_phone=contact_phone,
        )
