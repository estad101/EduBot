"""
WhatsApp Webhook Routes.

Handles incoming WhatsApp messages and sends responses.
"""
from fastapi import APIRouter, Request, HTTPException, Depends, Header, Query
from sqlalchemy.orm import Session
from typing import Optional
import json
import logging

from config.database import get_db
from services.whatsapp_service import WhatsAppService
from services.conversation_service import ConversationService, MessageRouter
from services.student_service import StudentService
from services.lead_service import LeadService
from services.payment_service import PaymentService
from schemas.response import StandardResponse

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/webhook", tags=["webhooks"])


@router.post("/whatsapp", response_model=StandardResponse)
async def whatsapp_webhook(request: Request, db: Session = Depends(get_db)):
    """
    Receive WhatsApp Cloud API webhooks.

    WhatsApp sends POST requests with incoming messages and status updates.
    """
    try:
        # Get raw body for signature verification
        body = await request.body()
        body_str = body.decode("utf-8")

        # Parse JSON
        webhook_data = json.loads(body_str)

        # Check if this is a verification request from WhatsApp
        if webhook_data.get("object") == "whatsapp_business_account":
            # Check for verify token challenge
            if "entry" not in webhook_data:
                # This might be a webhook verification request
                logger.debug("Received WhatsApp webhook verification")
                return StandardResponse(
                    status="success", message="Webhook verified"
                )

        # Parse incoming message
        message_data = WhatsAppService.parse_message(webhook_data)

        if not message_data:
            # Could be a status update or other event
            logger.debug(
                "Received non-message webhook event"
            )
            return StandardResponse(
                status="success", message="Webhook received"
            )

        phone_number = message_data.get("phone_number")
        sender_name = message_data.get("sender_name")
        message_text = message_data.get("text", "")
        message_type = message_data.get("type")

        logger.info(
            f"WhatsApp message from {phone_number} ({sender_name}): {message_type}"
        )

        # Check if user is registered
        student = StudentService.get_student_by_phone(db, phone_number)
        
        # If not registered, save as a lead (DO NOT create a student record)
        if not student:
            try:
                LeadService.get_or_create_lead(
                    db,
                    phone_number=phone_number,
                    sender_name=sender_name,
                    first_message=message_text
                )
                logger.info(f"Saved/updated lead for {phone_number} (not yet registered)")
            except Exception as e:
                logger.warning(f"Could not save lead: {str(e)}")
                # Continue without saving lead

        # Get conversation state and next response
        response_text, next_state = MessageRouter.get_next_response(
            phone_number,
            message_text,
            student_data=None,  # Simplified - remove subscription check for now
        )
        
        logger.info(f"✓ Got response from MessageRouter")
        logger.info(f"  Response text length: {len(response_text) if response_text else 0}")
        logger.info(f"  Response text: {response_text[:150] if response_text else 'NONE'}")
        logger.info(f"  Next state: {next_state}")
        
        # Update conversation state for next message
        if next_state:
            ConversationService.set_state(phone_number, next_state)
            logger.info(f"✓ Updated conversation state to: {next_state}")

        # Handle registration completion
        if next_state and next_state.value == "registered":
            # Extract registration data from conversation
            reg_data = ConversationService.get_registration_data(phone_number)

            # Register student if not already registered
            if not student:
                try:
                    student = StudentService.create_student(
                        db,
                        phone_number=phone_number,
                        full_name=reg_data["full_name"],
                        email=reg_data["email"],
                        class_grade=reg_data["class_grade"],
                    )
                    logger.info(f"Registered new student: {phone_number}")
                    
                    # Mark the lead as converted
                    try:
                        LeadService.convert_lead_to_student(
                            db,
                            phone_number=phone_number,
                            student_id=student.id
                        )
                        logger.info(f"Lead {phone_number} marked as converted to student {student.id}")
                    except ValueError:
                        # Lead might not exist if user registered through webhook
                        logger.info(f"No existing lead for {phone_number} - direct webhook registration")
                except Exception as e:
                    logger.error(f"Error registering student: {str(e)}")
                    response_text = "❌ Error during registration. Please try again."

        # Handle homework submission
        elif next_state and next_state.value == "homework_submitted":
            if student:
                homework_data = ConversationService.get_homework_data(phone_number)
                
                # Download image if image submission
                file_path = None
                if message_type == "image" and message_data.get("image_id"):
                    try:
                        media_bytes = await WhatsAppService.download_media(
                            message_data.get("image_id"), 
                            media_type="image"
                        )
                        if media_bytes:
                            # Save file
                            import os
                            upload_dir = "uploads/homework"
                            os.makedirs(upload_dir, exist_ok=True)
                            
                            import time
                            filename = f"homework_{phone_number.replace('+', '')}_{int(time.time())}.jpg"
                            file_path = os.path.join(upload_dir, filename)
                            
                            with open(file_path, "wb") as f:
                                f.write(media_bytes)
                            logger.info(f"Saved homework image: {file_path}")
                    except Exception as e:
                        logger.error(f"Failed to download image: {str(e)}")

                # For now, accept all homework submissions without payment
                try:
                    from services.homework_service import HomeworkService

                    homework = HomeworkService.submit_homework(
                        db,
                        student_id=student.id,
                        subject=homework_data["subject"],
                        submission_type=homework_data["submission_type"],
                        content=homework_data["content"],
                        file_path=file_path,
                        payment_required=False,  # Disabled for now
                    )

                    # Auto-assign to tutor (no payment needed)
                    from services.tutor_service import TutorService
                    
                    assignment = TutorService.assign_homework_by_subject(db, homework.id)
                    if assignment:
                        response_text = (
                            f"✅ Homework submitted successfully for {homework_data['subject']}!\n\n"
                            f"🎓 A tutor has been assigned and will respond soon with solutions!"
                        )
                    else:
                        response_text = (
                            f"✅ Homework submitted successfully for {homework_data['subject']}!\n\n"
                            f"⏳ No tutors currently available. We'll assign one shortly."
                        )

                    # Reset homework state
                    ConversationService.reset_homework_state(phone_number)

                except Exception as e:
                    logger.error(f"Error submitting homework: {str(e)}")
                    response_text = "❌ Error submitting homework. Please try again."
            else:
                response_text = "❌ You need to register first!"

        # Handle payment confirmation
        elif next_state and next_state.value == "payment_confirmed":
            if student:
                response_text = (
                    "💳 Opening payment page...\n\n"
                    "After payment, we'll send you a confirmation message."
                )

        # Store messages in conversation service
        import uuid
        from datetime import datetime
        
        # Initialize messages list if not exists
        conv_state = ConversationService.get_state(phone_number)
        if "messages" not in conv_state["data"]:
            conv_state["data"]["messages"] = []
        
        # Add user message
        conv_state["data"]["messages"].append({
            "id": f"msg_{uuid.uuid4().hex[:12]}",
            "phone_number": phone_number,
            "text": message_text,
            "timestamp": datetime.now().isoformat(),
            "sender_type": "user",
            "message_type": message_type
        })
        
        # Store last message for preview
        ConversationService.set_data(phone_number, "last_message", message_text)

        # Send response message
        try:
            logger.info(f"📤 Sending message to {phone_number}")
            logger.info(f"   Message text: {response_text[:100]}...")
            
            result = await WhatsAppService.send_message(
                phone_number=phone_number,
                message_type="text",
                text=response_text,
            )
            
            logger.info(f"   Result: {result.get('status')}")
            
            if result.get('status') == 'error':
                logger.error(f"   Error: {result.get('message')}")
                logger.error(f"   Details: {result.get('error')}")
            
            # Add bot message to conversation
            conv_state["data"]["messages"].append({
                "id": f"msg_{uuid.uuid4().hex[:12]}",
                "phone_number": phone_number,
                "text": response_text,
                "timestamp": datetime.now().isoformat(),
                "sender_type": "bot",
                "message_type": "text"
            })
        except Exception as e:
            logger.error(f"❌ Exception sending WhatsApp message: {str(e)}", exc_info=True)

        return StandardResponse(
            status="success",
            message="Webhook processed successfully",
        )

    except json.JSONDecodeError:
        logger.error("Invalid JSON in webhook request")
        raise HTTPException(status_code=400, detail="Invalid JSON")
    except Exception as e:
        logger.error(f"Error processing WhatsApp webhook: {str(e)}")
        # Always return 200 to prevent WhatsApp retries
        return StandardResponse(
            status="success",
            message="Webhook received",
        )


@router.get("/whatsapp")
async def verify_whatsapp_webhook(
    hub_mode: str = Query(None, alias="hub.mode"),
    hub_challenge: str = Query(None, alias="hub.challenge"),
    hub_verify_token: str = Query(None, alias="hub.verify_token"),
):
    """
    Verify webhook endpoint for WhatsApp.

    WhatsApp calls this endpoint with GET request during webhook setup.
    """
    from config.settings import settings

    if not hub_mode or not hub_challenge or not hub_verify_token:
        logger.warning("Missing webhook verification parameters")
        raise HTTPException(status_code=400, detail="Missing parameters")

    if hub_mode != "subscribe":
        logger.warning(f"Invalid hub.mode: {hub_mode}")
        raise HTTPException(status_code=403, detail="Forbidden")

    if hub_verify_token != settings.whatsapp_webhook_token:
        logger.warning("Invalid webhook verification token")
        raise HTTPException(status_code=403, detail="Forbidden")

    logger.info("WhatsApp webhook verified successfully")
    return int(hub_challenge)
