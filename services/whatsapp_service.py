"""
WhatsApp Cloud API Integration Service.

Handles sending messages, receiving webhooks, and managing WhatsApp communication.
"""
import httpx
import json
import logging
from typing import Optional, List, Dict, Any
from config.settings import settings

logger = logging.getLogger(__name__)

# WhatsApp Cloud API endpoints
WHATSAPP_API_URL = "https://graph.facebook.com/v22.0"


def get_whatsapp_credentials() -> tuple[Optional[str], Optional[str]]:
    """
    Get WhatsApp API credentials from database.
    Falls back to environment variables if not in database.
    
    Returns:
        Tuple of (api_key, phone_number_id)
    """
    try:
        # Import inside function to avoid circular imports and load-time issues
        from config.database import SessionLocal
        from models.settings import AdminSetting
        
        db = SessionLocal()
        api_key = db.query(AdminSetting).filter(
            AdminSetting.key == "WHATSAPP_API_KEY"
        ).first()
        phone_id = db.query(AdminSetting).filter(
            AdminSetting.key == "WHATSAPP_PHONE_NUMBER_ID"
        ).first()
        db.close()
        
        # Return database values if they exist, otherwise fall back to env vars
        final_api_key = api_key.value if api_key and api_key.value else settings.whatsapp_api_key
        final_phone_id = phone_id.value if phone_id and phone_id.value else settings.whatsapp_phone_number_id
        
        logger.info(f"🔵 [get_whatsapp_credentials] API Key source: {'database' if api_key and api_key.value else 'environment'}")
        logger.info(f"🔵 [get_whatsapp_credentials] Phone ID source: {'database' if phone_id and phone_id.value else 'environment'}")
        
        return final_api_key, final_phone_id
    except Exception as e:
        logger.warning(f"⚠️ Error fetching WhatsApp credentials from database: {str(e)}")
        logger.info(f"🔵 Falling back to environment variables")
        return settings.whatsapp_api_key, settings.whatsapp_phone_number_id


class WhatsAppService:
    """Service for WhatsApp Cloud API integration."""

    @staticmethod
    async def send_interactive_message(
        phone_number: str,
        body_text: str,
        buttons: List[Dict[str, str]],
    ) -> Dict[str, Any]:
        """
        Send an interactive message with buttons via WhatsApp Cloud API.

        Args:
            phone_number: Recipient phone number (e.g., "+234901234567")
            body_text: Message body text
            buttons: List of button dicts with keys:
                    - id: Button ID/payload (max 256 chars)
                    - title: Button display text (max 20 chars)

        Returns:
            Dict with response from WhatsApp API
        """
        logger.info(f"🔵 [send_interactive_message] Starting - phone: {phone_number}, buttons: {len(buttons)}")
        
        # Get WhatsApp credentials from database
        whatsapp_api_key, whatsapp_phone_number_id = get_whatsapp_credentials()
        
        # Check if WhatsApp credentials are properly configured
        if not whatsapp_api_key or whatsapp_api_key == "placeholder_api_key":
            logger.error(f"🔴 [send_interactive_message] WhatsApp API Key not configured")
            return {"status": "error", "message": "WhatsApp API key not configured"}
        
        if not whatsapp_phone_number_id or whatsapp_phone_number_id == "placeholder_phone_id":
            logger.error(f"🔴 [send_interactive_message] WhatsApp Phone Number ID not configured")
            return {"status": "error", "message": "WhatsApp phone number ID not configured"}

        clean_phone = phone_number.replace("+", "")
        logger.info(f"🔵 [send_interactive_message] Clean phone: {clean_phone}")

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                # Build interactive button payload
                interactive_buttons = []
                for idx, button in enumerate(buttons):
                    if idx >= 3:  # WhatsApp allows max 3 buttons
                        logger.warning(f"Max 3 buttons allowed, ignoring button {idx + 1}")
                        break
                    interactive_buttons.append({
                        "type": "reply",
                        "reply": {
                            "id": str(button.get("id", f"button_{idx}"))[:256],
                            "title": str(button.get("title", f"Option {idx + 1}"))[:20],
                        }
                    })

                payload = {
                    "messaging_product": "whatsapp",
                    "recipient_type": "individual",
                    "to": clean_phone,
                    "type": "interactive",
                    "interactive": {
                        "type": "button",
                        "body": {
                            "text": body_text,
                        },
                        "action": {
                            "buttons": interactive_buttons,
                        }
                    }
                }

                url = f"{WHATSAPP_API_URL}/{whatsapp_phone_number_id}/messages"
                headers = {
                    "Authorization": f"Bearer {whatsapp_api_key}",
                    "Content-Type": "application/json",
                }

                logger.info(f"🔵 [send_interactive_message] Making API call with {len(interactive_buttons)} buttons")
                response = await client.post(url, json=payload, headers=headers)
                
                logger.info(f"🔵 [send_interactive_message] API response status: {response.status_code}")

                if response.status_code in [200, 201]:
                    result = response.json()
                    logger.info(f"✓ Interactive message sent to {phone_number}")
                    return {
                        "status": "success",
                        "message": "Interactive message sent successfully",
                        "data": result,
                    }
                else:
                    error_text = response.text
                    logger.error(f"❌ WhatsApp API error ({response.status_code}) sending interactive message to {phone_number}")
                    logger.error(f"   Response: {error_text}")
                    return {
                        "status": "error",
                        "message": f"Failed to send interactive message: {response.status_code}",
                        "error": error_text,
                    }

        except httpx.TimeoutException:
            logger.error(f"WhatsApp API timeout for {phone_number}")
            return {"status": "error", "message": "Request timeout"}
        except httpx.RequestError as e:
            logger.error(f"WhatsApp API error: {str(e)}")
            return {"status": "error", "message": str(e)}
        except Exception as e:
            logger.error(f"Unexpected error sending interactive message: {str(e)}")
            return {"status": "error", "message": "Internal server error"}

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
        logger.info(f"🔵 [send_message] Starting - phone: {phone_number}, type: {message_type}")
        
        # Get WhatsApp credentials from database
        whatsapp_api_key, whatsapp_phone_number_id = get_whatsapp_credentials()
        
        # Check if WhatsApp credentials are properly configured (not placeholders)
        if not whatsapp_api_key or whatsapp_api_key == "placeholder_api_key":
            logger.error(f"🔴 [send_message] WhatsApp API Key not configured (WHATSAPP_API_KEY env var missing)")
            return {"status": "error", "message": "WhatsApp API key not configured"}
        
        if not whatsapp_phone_number_id or whatsapp_phone_number_id == "placeholder_phone_id":
            logger.error(f"🔴 [send_message] WhatsApp Phone Number ID not configured (WHATSAPP_PHONE_NUMBER_ID env var missing)")
            return {"status": "error", "message": "WhatsApp phone number ID not configured"}

        logger.info(f"🔵 [send_message] API Key exists: {bool(whatsapp_api_key)}")
        logger.info(f"🔵 [send_message] Phone ID: {whatsapp_phone_number_id}")
        logger.info(f"🔵 [send_message] API URL base: {WHATSAPP_API_URL}")

        # Clean phone number - ensure it starts with country code (no +)
        clean_phone = phone_number.replace("+", "")
        logger.info(f"🔵 [send_message] Clean phone: {clean_phone}")

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
                url = f"{WHATSAPP_API_URL}/{whatsapp_phone_number_id}/messages"
                headers = {
                    "Authorization": f"Bearer {whatsapp_api_key}",
                    "Content-Type": "application/json",
                }

                logger.info(f"🔵 [send_message] Prepared API call")
                logger.info(f"🔵 [send_message] URL: {url}")
                logger.info(f"🔵 [send_message] Payload type: {message_type}")
                logger.info(f"🔵 [send_message] Making POST request to WhatsApp API...")
                
                response = await client.post(url, json=payload, headers=headers)
                
                logger.info(f"🔵 [send_message] API response status: {response.status_code}")

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
                    logger.error(f"   Phone ID: {whatsapp_phone_number_id}")
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

        if not settings.whatsapp_webhook_token:
            logger.warning("WhatsApp webhook token not configured")
            return False

        # Create signature: SHA256 hash of body with token
        expected_signature = hmac.new(
            settings.whatsapp_webhook_token.encode(),
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
            elif message_type == "interactive":
                # Handle interactive message responses (button clicks)
                interactive = message.get("interactive", {})
                button_reply = interactive.get("button_reply", {})
                message_data["button_id"] = button_reply.get("id")
                message_data["button_text"] = button_reply.get("title")
                message_data["text"] = button_reply.get("id")  # Use button ID as message text for intent matching
                logger.info(f"Interactive button response: id={message_data.get('button_id')}, text={message_data.get('button_text')}")

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
        # Get WhatsApp credentials from database
        whatsapp_api_key, whatsapp_phone_number_id = get_whatsapp_credentials()
        
        if not whatsapp_api_key or not whatsapp_phone_number_id:
            logger.error("WhatsApp API credentials not configured")
            return None

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                # Get media URL
                url = f"{WHATSAPP_API_URL}/{media_id}"
                headers = {
                    "Authorization": f"Bearer {whatsapp_api_key}",
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
                    media_url, headers={"Authorization": f"Bearer {whatsapp_api_key}"}
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
