"""
Paystack service - integration with Paystack payment gateway.
"""
import requests
import json
from typing import Optional
from decimal import Decimal
from utils.logger import get_logger
from utils.security import verify_paystack_webhook_signature, generate_idempotency_key
from config.settings import settings

logger = get_logger("paystack_service")


class PaystackService:
    """Service for Paystack integration."""

    BASE_URL = "https://api.paystack.co"
    HEADERS = {
        "Authorization": f"Bearer {settings.paystack_secret_key}",
        "Content-Type": "application/json",
    }

    @staticmethod
    def initialize_payment(
        email: str, amount_naira: float, metadata: Optional[dict] = None
    ) -> dict:
        """
        Initialize payment with Paystack.
        
        Converts naira to kobo (multiply by 100).
        
        Args:
            email: Customer email
            amount_naira: Amount in naira
            metadata: Additional metadata (student_id, etc.)
        
        Returns:
            Dictionary with authorization_url, access_code, reference
        
        Raises:
            ValueError: If API call fails
        """
        # Convert naira to kobo
        amount_kobo = int(amount_naira * 100)

        if amount_kobo <= 0:
            raise ValueError("Amount must be greater than 0")

        payload = {
            "email": email,
            "amount": amount_kobo,
            "metadata": metadata or {},
        }

        try:
            response = requests.post(
                f"{PaystackService.BASE_URL}/transaction/initialize",
                headers=PaystackService.HEADERS,
                json=payload,
                timeout=30,
            )

            if response.status_code != 200:
                logger.error(
                    f"Paystack initialization failed: {response.status_code} - {response.text}"
                )
                raise ValueError(
                    f"Failed to initialize payment: {response.status_code}"
                )

            data = response.json()

            if not data.get("status"):
                raise ValueError(f"Paystack error: {data.get('message', 'Unknown error')}")

            result = data.get("data", {})

            logger.info(
                f"Payment initialized: {result.get('reference')} - {email} - {amount_naira} NGN"
            )

            return {
                "authorization_url": result.get("authorization_url"),
                "access_code": result.get("access_code"),
                "reference": result.get("reference"),
                "amount": amount_naira,
            }

        except requests.exceptions.RequestException as e:
            logger.error(f"Paystack API error: {str(e)}")
            raise ValueError(f"Failed to connect to Paystack: {str(e)}")

    @staticmethod
    def verify_payment(reference: str) -> dict:
        """
        Verify payment with Paystack.
        
        Args:
            reference: Paystack transaction reference
        
        Returns:
            Dictionary with verification status and details
        
        Raises:
            ValueError: If API call fails
        """
        try:
            response = requests.get(
                f"{PaystackService.BASE_URL}/transaction/verify/{reference}",
                headers=PaystackService.HEADERS,
                timeout=30,
            )

            if response.status_code != 200:
                logger.error(
                    f"Paystack verification failed: {response.status_code} - {response.text}"
                )
                raise ValueError(
                    f"Failed to verify payment: {response.status_code}"
                )

            data = response.json()

            if not data.get("status"):
                raise ValueError(
                    f"Paystack error: {data.get('message', 'Unknown error')}"
                )

            result = data.get("data", {})

            # Check if payment was successful
            payment_status = result.get("status")
            is_success = payment_status == "success"

            logger.info(
                f"Payment verified: {reference} - Status: {payment_status}"
            )

            return {
                "status": payment_status,
                "is_success": is_success,
                "amount": result.get("amount") / 100,  # Convert kobo to naira
                "customer_email": result.get("customer", {}).get("email"),
                "authorization": result.get("authorization", {}),
                "metadata": result.get("metadata", {}),
            }

        except requests.exceptions.RequestException as e:
            logger.error(f"Paystack verification error: {str(e)}")
            raise ValueError(f"Failed to verify payment: {str(e)}")

    @staticmethod
    def verify_webhook_signature(payload_body: str, signature: str) -> bool:
        """
        Verify Paystack webhook signature.
        
        Args:
            payload_body: Raw request body
            signature: X-Paystack-Signature header
        
        Returns:
            True if signature is valid
        """
        return verify_paystack_webhook_signature(payload_body, signature)

    @staticmethod
    def process_webhook_payload(payload: dict) -> dict:
        """
        Process Paystack webhook payload.
        
        Args:
            payload: Webhook payload from Paystack
        
        Returns:
            Processed data for payment verification
        
        Raises:
            ValueError: If payload is invalid
        """
        event = payload.get("event")
        data = payload.get("data", {})

        if event not in ["charge.success", "charge.failed"]:
            raise ValueError(f"Unsupported event: {event}")

        return {
            "event": event,
            "reference": data.get("reference"),
            "status": data.get("status"),
            "amount": data.get("amount") / 100 if data.get("amount") else 0,
            "customer_email": data.get("customer", {}).get("email"),
            "metadata": data.get("metadata", {}),
            "timestamp": data.get("paid_at"),
        }
