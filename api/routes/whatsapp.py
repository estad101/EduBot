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
                logger.info(f"  Content length: {len(str(homework_data.get('content', '')))}")
                
                # Handle image submission
                file_path = None
                submission_content = homework_data["content"]
                
                # If submission type is IMAGE and incoming message is image, download it
                if homework_data.get("submission_type") == "IMAGE" and message_type == "image" and message_data.get("image_id"):
                    try:
                        import os
                        import time
                        
                        logger.info(f"📸 Starting image download for homework")
                        logger.info(f"   Image ID: {message_data.get('image_id')}")
                        
                        media_bytes = await WhatsAppService.download_media(
                            message_data.get("image_id"), 
                            media_type="image"
                        )
                        
                        if not media_bytes:
                            logger.warning(f"❌ Failed to download media - no bytes received")
                        else:
                            logger.info(f"✓ Downloaded media: {len(media_bytes)} bytes")
                            
                            # Save file with proper directory structure
                            upload_dir = "uploads/homework"
                            student_dir = os.path.join(upload_dir, str(student.id))
                            os.makedirs(student_dir, exist_ok=True)
                            
                            # Create unique filename
                            clean_phone = phone_number.replace('+', '').replace(' ', '')
                            timestamp = int(time.time() * 1000)  # milliseconds for uniqueness
                            filename = f"homework_{clean_phone}_{timestamp}.jpg"
                            file_path = os.path.join(student_dir, filename)
                            
                            # Ensure absolute path
                            file_path = os.path.abspath(file_path)
                            
                            # Write file
                            logger.info(f"📝 Saving image to: {file_path}")
                            with open(file_path, "wb") as f:
                                bytes_written = f.write(media_bytes)
                                logger.info(f"   Written {bytes_written} bytes")
                            
                            # Verify file was saved
                            if os.path.exists(file_path):
                                actual_size = os.path.getsize(file_path)
                                logger.info(f"✓ Image saved successfully: {file_path}")
                                logger.info(f"   File size: {actual_size} bytes")
                                
                                # Store relative path for database (without 'uploads/' prefix)
                                # Format: homework/{student_id}/homework_*.jpg
                                relative_path = os.path.relpath(file_path)
                                # Remove 'uploads/' prefix if present
                                if relative_path.startswith('uploads/') or relative_path.startswith('uploads\\'):
                                    relative_path = relative_path[8:]  # Remove 'uploads/'
                                # Normalize path separators to forward slash
                                relative_path = relative_path.replace('\\', '/')
                                file_path = relative_path
                                submission_content = f"Image submission: {message_data.get('image_id')}"
                            else:
                                logger.error(f"❌ File not found after write: {file_path}")
                                file_path = None
                    except Exception as e:
                        logger.error(f"❌ Failed to download/save image: {str(e)}")
                        import traceback
                        logger.error(f"   Traceback: {traceback.format_exc()}")
                        file_path = None

                # For now, accept all homework submissions without payment
                try:
                    from services.homework_service import HomeworkService

                    logger.info(f"📚 Submitting homework with:")
                    logger.info(f"   student_id: {student.id}")
                    logger.info(f"   subject: {homework_data.get('subject')}")
                    logger.info(f"   submission_type: {homework_data.get('submission_type')}")
                    logger.info(f"   file_path: {file_path}")
                    logger.info(f"   content length: {len(submission_content)}")
                    
                    # Validate before submitting
                    if homework_data.get('submission_type') == 'IMAGE':
                        if not file_path:
                            logger.warning(f"⚠️ Image submission without file_path - likely download failed")
                        elif not os.path.exists(file_path):
                            logger.error(f"❌ File path specified but file does not exist: {file_path}")
                            file_path = None
                    
                    homework = HomeworkService.submit_homework(
                        db,
                        student_id=student.id,
                        subject=homework_data["subject"],
                        submission_type=homework_data["submission_type"],
                        content=submission_content,
                        file_path=file_path,
                        payment_required=False,  # Disabled for now
                    )
                    
                    logger.info(f"✅ Homework created: {homework.id}")
                    if file_path:
                        logger.info(f"   Image path: {homework.file_path}")

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
                            f"⏳ A tutor will be assigned to you shortly"
                        )

                    # Reset homework state
                    ConversationService.reset_homework_state(phone_number)

                except Exception as e:
                    logger.error(f"Error submitting homework: {str(e)}", exc_info=True)
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
