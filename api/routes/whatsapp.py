"""
WhatsApp Webhook Routes.

Handles incoming WhatsApp messages and sends responses.
"""
from fastapi import APIRouter, Request, HTTPException, Depends, Header, Query
from sqlalchemy.orm import Session
from typing import Optional
import json
import logging
import time

from config.database import get_db
from services.whatsapp_service import WhatsAppService
from services.conversation_service import ConversationService, MessageRouter, ConversationState
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
        
        # Validate phone number
        if not phone_number:
            logger.error("❌ No phone number in message data - cannot process")
            return StandardResponse(
                status="success", message="Webhook received (no phone number)"
            )

        # Check if user is registered
        student = StudentService.get_student_by_phone(db, phone_number)
        
        # If not registered, save as a lead (require manual registration)
        if not student:
            try:
                LeadService.get_or_create_lead(
                    db,
                    phone_number=phone_number,
                    sender_name=sender_name,
                    first_message=message_text
                )
                logger.info(f"Saved/updated lead for {phone_number} (requires manual registration)")
            except Exception as e:
                logger.warning(f"Could not save lead: {str(e)}")
                # Continue without saving lead

        # Get conversation state and next response
        # Pass student data if registered, so bot knows user is a registered student
        student_data = None
        if student:
            student_data = {
                "status": "RETURNING_USER",
                "student_id": student.id,
                "phone_number": student.phone_number,
                "user_status": student.status.value,
                "name": student.full_name,
                "email": student.email,
                "has_subscription": student.status.value == "ACTIVE_SUBSCRIBER",
            }
            logger.info(f"✓ User is registered: {student.full_name} ({student.phone_number})")
        
        # Check if user has a registration state set
        current_state = ConversationService.get_state(phone_number)
        state_value = current_state.get("state")
        
        # If unregistered and no registration state set, prompt to register
        if not student and state_value in [None, "idle", "initial"]:
            logger.info(f"Prompting unregistered user {phone_number} to register")
            response_text = (
                "👋 Welcome! I'm EduBot, your AI tutor assistant.\n\n"
                "I can help you with:\n"
                "📝 Homework submissions\n"
                "💳 Premium subscription\n"
                "❓ FAQs and support\n\n"
                "To get started, let's create your free account!\n\n"
                "👤 What is your full name?"
            )
            next_state = ConversationState.REGISTERING_NAME
            ConversationService.set_state(phone_number, next_state)
            logger.info(f"Set state to REGISTERING_NAME for {phone_number}")
        else:
            # User is registered or already in registration flow - use normal flow
            try:
                response_text, next_state = MessageRouter.get_next_response(
                    phone_number,
                    message_text,
                    student_data=student_data,  # Pass actual student data if registered
                )
            except Exception as e:
                logger.error(f"❌ Error in MessageRouter.get_next_response: {str(e)}", exc_info=True)
                response_text = "❌ Error processing your message. Please try again."
                next_state = ConversationState.IDLE
        
        logger.info(f"✓ Got response from MessageRouter")
        logger.info(f"  Response text length: {len(response_text) if response_text else 0}")
        logger.info(f"  Response text: {response_text[:150] if response_text else 'NONE'}")
        logger.info(f"  Next state: {next_state}")
        
        # Validate response text
        if not response_text:
            logger.error("❌ No response text from MessageRouter - using default message")
            response_text = "👋 Thanks for your message! Choose an option above to continue."
        
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
                logger.info(f"Processing homework submission for {phone_number}")
                logger.info(f"  Subject: {homework_data.get('subject')}")
                logger.info(f"  Type: {homework_data.get('submission_type')}")
                logger.info(f"  Message type: {message_type}")
                
                submission_type = homework_data.get("submission_type", "TEXT").upper()
                
                try:
                    from services.homework_service import HomeworkService
                    
                    # For IMAGE submissions, create homework record first without file
                    # Then send upload link to user
                    if submission_type == "IMAGE":
                        logger.info(f"📷 IMAGE submission - creating homework record and sending upload link")
                        
                        # Create homework record (without file initially)
                        homework = HomeworkService.submit_homework(
                            db,
                            student_id=student.id,
                            subject=homework_data["subject"],
                            submission_type="IMAGE",
                            content="Image submission pending",
                            file_path=None,  # No file yet
                            payment_required=False,
                        )
                        
                        logger.info(f"✅ Homework created: {homework.id}")
                        
                        # Generate secure upload token (just use homework_id + student_id hash)
                        import hashlib
                        upload_token = hashlib.sha256(
                            f"{homework.id}{student.id}{int(time.time())}".encode()
                        ).hexdigest()[:32]
                        
                        # Get app URL from environment
                        import os
                        app_url = os.getenv("APP_URL", "https://nurturing-exploration-production.up.railway.app")
                        upload_page = f"{app_url}/homework-upload?student_id={student.id}&homework_id={homework.id}&subject={homework_data['subject']}&token={upload_token}"
                        
                        logger.info(f"   Upload link: {upload_page}")
                        
                        # Send WhatsApp message with upload link
                        response_text = (
                            f"📷 Great! Let's upload your homework image for {homework_data['subject']}!\n\n"
                            f"🔗 Tap the link below to open the upload page:\n\n"
                            f"{upload_page}\n\n"
                            f"ℹ️ Tips:\n"
                            f"✓ Make sure the image is clear and readable\n"
                            f"✓ Landscape orientation works best\n"
                            f"✓ File size must be less than 10MB\n\n"
                            f"Once you upload, you'll get a confirmation!"
                        )
                        
                    # For TEXT submissions, accept directly from message
                    else:
                        logger.info(f"📝 TEXT submission - accepting directly from message")
                        
                        submission_content = homework_data.get("content", message_text)
                        
                        homework = HomeworkService.submit_homework(
                            db,
                            student_id=student.id,
                            subject=homework_data["subject"],
                            submission_type="TEXT",
                            content=submission_content,
                            file_path=None,
                            payment_required=False,
                        )
                        
                        logger.info(f"✅ Homework created: {homework.id}")
                        
                        # Auto-assign to tutor
                        from services.tutor_service import TutorService
                        assignment = TutorService.assign_homework_by_subject(db, homework.id)
                        
                        if assignment:
                            response_text = (
                                f"✅ Homework submitted successfully for {homework_data['subject']}!\n\n"
                                f"🎓 A tutor has been assigned and will respond soon!"
                            )
                        else:
                            response_text = (
                                f"✅ Homework submitted successfully for {homework_data['subject']}!\n\n"
                                f"⏳ A tutor will be assigned to you shortly"
                            )
                    
                    # Reset homework state
                    ConversationService.reset_homework_state(phone_number)

                except Exception as e:
                    logger.error(f"❌ Error submitting homework: {str(e)}", exc_info=True)
                    logger.error(f"Homework data: student_id={student.id}, subject={homework_data.get('subject')}, type={submission_type}")
                    response_text = f"❌ Error submitting homework: {str(e)}"
            else:
                response_text = "❌ You need to register first!"
                            response_text = (
                                f"✅ Homework submitted successfully for {homework_data['subject']}!\n\n"
                                f"🎓 A tutor has been assigned and will respond soon with solutions!"
                            )
                        else:
                            response_text = (
                                f"✅ Homework submitted successfully for {homework_data['subject']}!\n\n"
                                f"⏳ A tutor will be assigned to you shortly"
                            )

                    # Reset homework state
                    ConversationService.reset_homework_state(phone_number)

                except Exception as e:
                    logger.error(f"Error submitting homework: {str(e)}", exc_info=True)
                    logger.error(f"Exception details: {type(e).__name__}: {str(e)}")
                    logger.error(f"Homework data: student_id={student.id}, subject={homework_data.get('subject')}, type={homework_data.get('submission_type')}")
                    logger.error(f"File path: {file_path}")
                    response_text = f"❌ Error submitting homework: {str(e)}"
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

        # Get buttons for interactive message
        buttons = MessageRouter.get_buttons(
            intent=MessageRouter.extract_intent(message_text),
            current_state=next_state or ConversationState.IDLE,
            is_registered=bool(student_data),
            phone_number=phone_number
        )

        # Send response message
        try:
            logger.info(f"📤 Sending message to {phone_number}")
            logger.info(f"   Message text: {response_text[:100]}...")
            logger.info(f"   Has buttons: {buttons is not None and len(buttons) > 0}")
            
            # Send interactive message if buttons available, otherwise text
            if buttons and len(buttons) > 0:
                logger.info(f"   Sending with {len(buttons)} buttons")
                result = await WhatsAppService.send_interactive_message(
                    phone_number=phone_number,
                    body_text=response_text,
                    buttons=buttons,
                )
            else:
                logger.info(f"   Sending as text message")
                result = await WhatsAppService.send_message(
                    phone_number=phone_number,
                    message_type="text",
                    text=response_text,
                )
            
            logger.info(f"   Result: {result.get('status')}")
            
            if result.get('status') == 'error':
                logger.error(f"   ❌ Error sending WhatsApp message to {phone_number}")
                logger.error(f"   Message: {result.get('message')}")
                logger.error(f"   Details: {result.get('error')}")
            else:
                logger.info(f"   ✅ Message sent successfully to {phone_number}")
            
            # Add bot message to conversation
            conv_state["data"]["messages"].append({
                "id": f"msg_{uuid.uuid4().hex[:12]}",
                "phone_number": phone_number,
                "text": response_text,
                "timestamp": datetime.now().isoformat(),
                "sender_type": "bot",
                "message_type": "interactive" if buttons else "text",
                "buttons": buttons,
                "send_result": result.get('status')
            })
        except Exception as e:
            logger.error(f"❌ Exception sending WhatsApp message to {phone_number}: {str(e)}", exc_info=True)
            logger.error(f"   Response text was: {response_text[:100] if response_text else 'NONE'}")
            logger.error(f"   Buttons: {buttons}")
            # Still return success to prevent WhatsApp retries

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
