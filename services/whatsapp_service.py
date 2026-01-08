"""
WhatsApp Cloud API Integration Service.

Handles sending messages, receiving webhooks, and managing WhatsApp communication.
Uses configuration from database via SettingsService with fallback to environment variables.
"""
import httpx
import json
import logging
from typing import Optional, List, Dict, Any
from config.settings import settings
from services.settings_service import get_setting, get_whatsapp_config

logger = logging.getLogger(__name__)

# WhatsApp Cloud API endpoints
WHATSAPP_API_URL = "https://graph.facebook.com/v22.0"


class WhatsAppService:
    """Service for WhatsApp Cloud API integration."""

    @staticmethod
    def get_api_credentials() -> tuple:
        """
        Get WhatsApp API credentials from database (or env fallback).
        
        Returns:
            Tuple of (api_key, phone_number_id)
        """
        api_key = get_setting("whatsapp_api_key", settings.whatsapp_api_key)
        phone_number_id = get_setting("whatsapp_phone_number_id", settings.whatsapp_phone_number_id)
        return api_key, phone_number_id

    @staticmethod
    async def send_interactive_buttons(
        phone_number: str,
        text: str,
        buttons: List[Dict[str, str]],
    ) -> Dict[str, Any]:
        """
        Send an interactive button message via WhatsApp.

        Args:
            phone_number: Recipient phone number
            text: Message body text
            buttons: List of button dicts with format:
                [
                    {"id": "btn_1", "title": "Button 1"},
                    {"id": "btn_2", "title": "Button 2"},
                    ...
                ]

        Returns:
            Response from WhatsApp API
        """
        api_key, phone_number_id = WhatsAppService.get_api_credentials()
        
        if not api_key or not phone_number_id:
            logger.error("WhatsApp API credentials not configured")
            return {"status": "error", "message": "WhatsApp not configured"}

        clean_phone = phone_number.replace("+", "")

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                # Build interactive buttons payload
                payload = {
                    "messaging_product": "whatsapp",
                    "recipient_type": "individual",
                    "to": clean_phone,
                    "type": "interactive",
                    "interactive": {
                        "type": "button",
                        "body": {"text": text},
                        "action": {
                            "buttons": [
                                {
                                    "type": "reply",
                                    "reply": {
                                        "id": btn["id"],
                                        "title": btn["title"]
                                    }
                                }
                                for btn in buttons[:3]  # WhatsApp allows max 3 buttons
                            ]
                        }
                    }
                }

                url = f"{WHATSAPP_API_URL}/{phone_number_id}/messages"
                headers = {
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json",
                }

                response = await client.post(url, json=payload, headers=headers)

                if response.status_code in [200, 201]:
                    result = response.json()
                    logger.info(
                        f"✓ Interactive button message sent to {phone_number}: {result.get('messages', [{}])[0].get('id', 'unknown')}"
                    )
                    return {
                        "status": "success",
                        "message": "Button message sent successfully",
                        "data": result,
                    }
                else:
                    error_text = response.text
                    logger.error(
                        f"❌ WhatsApp API error ({response.status_code}) sending button message to {phone_number}"
                    )
                    logger.error(f"   Response: {error_text}")
                    return {
                        "status": "error",
                        "message": f"Failed to send button message: {response.status_code}",
                        "error": error_text,
                    }

        except httpx.TimeoutException:
            logger.error(f"WhatsApp API timeout for {phone_number}")
            return {"status": "error", "message": "Request timeout"}
        except httpx.RequestError as e:
            logger.error(f"WhatsApp API error: {str(e)}")
            return {"status": "error", "message": str(e)}
        except Exception as e:
            logger.error(f"Unexpected error sending button message: {str(e)}")
            return {"status": "error", "message": "Internal server error"}

    @staticmethod
    async def send_message_with_link(
        phone_number: str,
        text: str,
        link_url: str,
        link_text: str = "Click here",
    ) -> Dict[str, Any]:
        """
        Send a text message with a clickable link.

        Args:
            phone_number: Recipient phone number
            text: Message body
            link_url: URL to link to
            link_text: Text for the link

        Returns:
            Response from WhatsApp API
        """
        # For now, just send as regular text with URL embedded
        # WhatsApp will auto-detect and make URLs clickable
        message_with_link = f"{text}\n\n🔗 {link_text}: {link_url}"
        return await WhatsAppService.send_message(
            phone_number=phone_number,
            message_type="text",
            text=message_with_link,
        )

    @staticmethod
    async def send_message(
        phone_number: str,
        message_type: str = "text",
        text: Optional[str] = None,
        template_name: Optional[str] = None,
        template_params: Optional[List[str]] = None,
        button_text: Optional[str] = None,
        button_url: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Send a message via WhatsApp Cloud API.

        Args:
            phone_number: Recipient phone number (e.g., "+234901234567")
            message_type: "text", "template", or "button"
            text: Message text (for text messages)
            template_name: Template name (for template messages)
            template_params: Template parameters
            button_text: Button text (for button messages)
            button_url: Button URL (for button messages)

        Returns:
            Dict with response from WhatsApp API
        """
        api_key, phone_number_id = WhatsAppService.get_api_credentials()
        
        if not api_key or not phone_number_id:
            logger.error("WhatsApp API credentials not configured")
            return {"status": "error", "message": "WhatsApp not configured"}

        # Clean phone number - ensure it starts with country code (no +)
        clean_phone = phone_number.replace("+", "")

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                if message_type == "text":
                    payload = {
                        "messaging_product": "whatsapp",
                        "recipient_type": "individual",
                        "to": clean_phone,
                        "type": "text",
                        "text": {"preview_url": True, "body": text},
                    }

                elif message_type == "template":
                    payload = {
                        "messaging_product": "whatsapp",
                        "to": clean_phone,
                        "type": "template",
                        "template": {
                            "name": template_name,
                            "language": {"code": "en_US"},
                        },
                    }
                    if template_params:
                        payload["template"]["components"] = [
                            {
                                "type": "body",
                                "parameters": [
                                    {"type": "text", "text": param}
                                    for param in template_params
                                ],
                            }
                        ]

                elif message_type == "button":
                    # Send text with button
                    payload = {
                        "messaging_product": "whatsapp",
                        "recipient_type": "individual",
                        "to": clean_phone,
                        "type": "text",
                        "text": {"preview_url": True, "body": text},
                    }

                else:
                    return {
                        "status": "error",
                        "message": f"Unknown message type: {message_type}",
                    }

                # Make API request
                url = f"{WHATSAPP_API_URL}/{phone_number_id}/messages"
                headers = {
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json",
                }

                response = await client.post(url, json=payload, headers=headers)

                if response.status_code in [200, 201]:
                    result = response.json()
                    logger.info(
                        f"✓ Message sent to {phone_number}: {result.get('messages', [{}])[0].get('id', 'unknown')}"
                    )
                    return {
                        "status": "success",
                        "message": "Message sent successfully",
                        "data": result,
                    }
                else:
                    error_text = response.text
                    logger.error(
                        f"❌ WhatsApp API error ({response.status_code}) sending to {phone_number}"
                    )
                    logger.error(f"   Status: {response.status_code}")
                    logger.error(f"   Phone ID: {phone_number_id}")
                    logger.error(f"   Response: {error_text}")
                    return {
                        "status": "error",
                        "message": f"Failed to send message: {response.status_code}",
                        "error": error_text,
                    }

        except httpx.TimeoutException:
            logger.error(f"WhatsApp API timeout for {phone_number}")
            return {"status": "error", "message": "Request timeout"}
        except httpx.RequestError as e:
            logger.error(f"WhatsApp API error: {str(e)}")
            return {"status": "error", "message": str(e)}
        except Exception as e:
            logger.error(f"Unexpected error sending WhatsApp message: {str(e)}")
            return {"status": "error", "message": "Internal server error"}

    @staticmethod
    def verify_webhook_signature(
        request_body: str, signature_header: str
    ) -> bool:
        """
        Verify WhatsApp webhook signature using the token.

        Args:
            request_body: Raw request body
            signature_header: X-Hub-Signature header value

        Returns:
            True if signature is valid, False otherwise
        """
        import hmac
        import hashlib

        webhook_token = get_setting("whatsapp_webhook_token", settings.whatsapp_webhook_token)
        
        if not webhook_token:
            logger.warning("WhatsApp webhook token not configured")
            return False

        # Create signature: SHA256 hash of body with token
        expected_signature = hmac.new(
            webhook_token.encode(),
            request_body.encode(),
            hashlib.sha256,
        ).hexdigest()

        # Compare with provided signature
        provided_signature = signature_header.replace("sha256=", "")

        if not hmac.compare_digest(expected_signature, provided_signature):
            logger.warning(f"Invalid webhook signature")
            return False

        return True

    @staticmethod
    def parse_message(webhook_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Parse incoming WhatsApp webhook message.

        Args:
            webhook_data: Raw webhook payload from WhatsApp

        Returns:
            Parsed message data or None if invalid
        """
        try:
            # Extract message from webhook payload
            entry = webhook_data.get("entry", [{}])[0]
            changes = entry.get("changes", [{}])[0]
            value = changes.get("value", {})
            messages = value.get("messages", [])

            if not messages:
                return None

            message = messages[0]
            sender = value.get("contacts", [{}])[0]

            # Extract phone and name
            phone_number = message.get("from")
            sender_name = sender.get("profile", {}).get("name", "User")

            # Parse message type
            message_type = message.get("type")  # text, image, document, etc.

            message_data = {
                "phone_number": f"+{phone_number}" if phone_number else None,
                "sender_name": sender_name,
                "message_id": message.get("id"),
                "timestamp": message.get("timestamp"),
                "type": message_type,
            }

            # Extract content based on type
            if message_type == "text":
                message_data["text"] = message.get("text", {}).get("body", "")
            elif message_type == "image":
                message_data["image_id"] = message.get("image", {}).get("id")
                message_data["image_caption"] = (
                    message.get("image", {}).get("caption", "")
                )
            elif message_type == "document":
                message_data["document_id"] = message.get("document", {}).get("id")
                message_data["document_filename"] = (
                    message.get("document", {}).get("filename", "")
                )
            elif message_type == "button":
                message_data["button_id"] = message.get("button", {}).get("payload")
                message_data["button_text"] = message.get("button", {}).get("text")

            return message_data

        except Exception as e:
            logger.error(f"Error parsing webhook message: {str(e)}")
            return None

    @staticmethod
    async def download_media(
        media_id: str, media_type: str = "image"
    ) -> Optional[bytes]:
        """
        Download media from WhatsApp (image, document, etc.).

        Args:
            media_id: WhatsApp media ID
            media_type: Type of media (image, document, etc.)

        Returns:
            Media bytes or None if failed
        """
        api_key, phone_number_id = WhatsAppService.get_api_credentials()
        
        if not api_key or not phone_number_id:
            logger.error("WhatsApp API credentials not configured")
            return None

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                # Get media URL
                url = f"{WHATSAPP_API_URL}/{media_id}"
                headers = {
                    "Authorization": f"Bearer {api_key}",
                }

                response = await client.get(url, headers=headers)

                if response.status_code != 200:
                    logger.error(
                        f"Failed to get media URL: {response.status_code}"
                    )
                    return None

                # Download from provided URL
                media_url = response.json().get("url")
                if not media_url:
                    logger.error("No media URL in response")
                    return None

                media_response = await client.get(
                    media_url, headers={"Authorization": f"Bearer {api_key}"}
                )

                if media_response.status_code == 200:
                    logger.info(f"Downloaded media: {media_id}")
                    return media_response.content
                else:
                    logger.error(
                        f"Failed to download media: {media_response.status_code}"
                    )
                    return None

        except Exception as e:
            logger.error(f"Error downloading media: {str(e)}")
            return None
