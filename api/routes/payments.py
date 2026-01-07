"""
Payment endpoints - initiation and verification.
"""
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from schemas.payment import PaymentInitiationRequest, PaymentVerificationRequest, PaystackWebhookRequest
from schemas.response import StandardResponse
from services.payment_service import PaymentService
from services.paystack_service import PaystackService
from services.subscription_service import SubscriptionService
from services.student_service import StudentService
from models.payment import PaymentStatus
from models.homework import Homework
from models.student import Student
from config.database import get_db
from utils.logger import get_logger

router = APIRouter(prefix="/api/payments", tags=["payments"])
logger = get_logger("payments_route")


@router.post("/initiate", response_model=StandardResponse)
async def initiate_payment(
    request: PaymentInitiationRequest, db: Session = Depends(get_db)
):
    """
    Initiate payment for homework submission or subscription.
    
    Request:
        {
            "student_id": 1,
            "amount": 5000.0,
            "is_subscription": false,
            "email": "john@example.com"
        }
    
    Response:
        {
            "status": "success",
            "message": "Payment initiated successfully",
            "data": {
                "payment_id": 1,
                "authorization_url": "https://checkout.paystack.com/...",
                "access_code": "xxxxx",
                "amount": 5000.0,
                "reference": "ref_xxxxx"
            }
        }
    """
    try:
        # Validate student exists
        student = StudentService.get_student_by_id(db, request.student_id)
        if not student:
            logger.warning(f"Payment initiation for unknown student: {request.student_id}")
            return StandardResponse(
                status="error",
                message="Student not found",
                error_code="STUDENT_NOT_FOUND",
            )

        # Use student email if not provided
        email = request.email or student.email

        # Initialize Paystack payment
        try:
            payment_data = PaystackService.initialize_payment(
                email=email,
                amount_naira=request.amount,
                metadata={
                    "student_id": request.student_id,
                    "student_name": student.full_name,
                    "is_subscription": request.is_subscription,
                },
            )

            # Create payment record
            payment = PaymentService.create_payment(
                db,
                student_id=request.student_id,
                amount=request.amount,
                reference=payment_data["reference"],
                authorization_url=payment_data["authorization_url"],
                access_code=payment_data["access_code"],
                is_subscription=request.is_subscription,
            )

            logger.info(
                f"Payment initiated: {payment.id} - Student: {request.student_id}, "
                f"Amount: {request.amount}, Subscription: {request.is_subscription}"
            )

            return StandardResponse(
                status="success",
                message="Payment initiated successfully",
                data={
                    "payment_id": payment.id,
                    "authorization_url": payment_data["authorization_url"],
                    "access_code": payment_data["access_code"],
                    "amount": payment_data["amount"],
                    "reference": payment_data["reference"],
                    "message": "Send authorization_url to customer to complete payment",
                },
            )

        except ValueError as e:
            logger.error(f"Paystack error: {str(e)}")
            return StandardResponse(
                status="error",
                message=f"Failed to initiate payment: {str(e)}",
                error_code="PAYSTACK_ERROR",
            )

    except Exception as e:
        logger.error(f"Unexpected error during payment initiation: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/verify", response_model=StandardResponse)
async def verify_payment(
    request: PaymentVerificationRequest, db: Session = Depends(get_db)
):
    """
    Verify payment status with Paystack.
    
    Handles both one-time payments and subscription payments atomically.
    If subscription payment is verified, creates subscription record.
    
    Request:
        {
            "reference": "ref_1234567890",
            "student_id": 1
        }
    
    Response:
        {
            "status": "success",
            "message": "Payment verified successfully",
            "data": {
                "payment_id": 1,
                "payment_status": "SUCCESS",
                "student_status": "ACTIVE_SUBSCRIBER",
                "subscription_id": 1
            }
        }
    """
    try:
        # Get payment from database
        payment = PaymentService.get_payment_by_reference(db, request.reference)
        if not payment:
            logger.warning(f"Payment verification for unknown reference: {request.reference}")
            return StandardResponse(
                status="error",
                message="Payment not found",
                error_code="PAYMENT_NOT_FOUND",
            )

        # Verify with Paystack
        try:
            verification_result = PaystackService.verify_payment(request.reference)
        except ValueError as e:
            logger.error(f"Paystack verification failed: {str(e)}")
            return StandardResponse(
                status="error",
                message=f"Failed to verify payment: {str(e)}",
                error_code="VERIFICATION_ERROR",
            )

        # Update payment status based on verification
        if verification_result["is_success"]:
            payment_status = PaymentStatus.SUCCESS
        else:
            payment_status = PaymentStatus.FAILED

        PaymentService.update_payment_status(db, payment.id, payment_status)

        # If subscription payment, create subscription record
        subscription_id = None
        if payment.is_subscription and verification_result["is_success"]:
            try:
                subscription = SubscriptionService.create_subscription(
                    db,
                    student_id=payment.student_id,
                    payment_id=payment.id,
                    amount=str(payment.amount),
                    days=30,
                )
                subscription_id = subscription.id

                logger.info(
                    f"Subscription created from payment: {subscription.id} - Student: {payment.student_id}"
                )
            except ValueError as e:
                logger.error(f"Subscription creation failed: {str(e)}")
                return StandardResponse(
                    status="error",
                    message=f"Payment verified but subscription creation failed: {str(e)}",
                    error_code="SUBSCRIPTION_ERROR",
                )

        # Get updated student status
        student = StudentService.get_student_by_id(db, payment.student_id)

        logger.info(
            f"Payment verified: {payment.id} - Status: {payment_status.value} - "
            f"Student: {payment.student_id}"
        )

        return StandardResponse(
            status="success",
            message=f"Payment verification successful - Status: {payment_status.value}",
            data={
                "payment_id": payment.id,
                "payment_status": payment_status.value,
                "student_status": student.status.value if student else None,
                "subscription_id": subscription_id,
            },
        )

    except Exception as e:
        logger.error(f"Unexpected error during payment verification: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/webhook/paystack", response_model=StandardResponse)
async def paystack_webhook(request: Request, db: Session = Depends(get_db)):
    """
    Receive Paystack webhook for payment events.
    
    Paystack sends webhooks for charge.success and charge.failed events.
    Validates signature and processes atomically.
    
    This endpoint:
    1. Validates Paystack signature
    2. Prevents duplicate processing
    3. Updates payment status
    4. Creates subscriptions if applicable
    """
    try:
        # Get raw body for signature verification
        body = await request.body()
        signature = request.headers.get("X-Paystack-Signature", "")

        # Verify signature
        if not PaystackService.verify_webhook_signature(body.decode(), signature):
            logger.warning(f"Invalid Paystack webhook signature")
            return StandardResponse(
                status="error",
                message="Invalid signature",
                error_code="INVALID_SIGNATURE",
            )

        # Parse payload
        payload = await request.json()

        try:
            webhook_data = PaystackService.process_webhook_payload(payload)
        except ValueError as e:
            logger.warning(f"Invalid webhook payload: {str(e)}")
            return StandardResponse(
                status="error",
                message=str(e),
                error_code="INVALID_PAYLOAD",
            )

        # Get payment
        reference = webhook_data.get("reference")
        payment = PaymentService.get_payment_by_reference(db, reference)

        if not payment:
            logger.warning(f"Webhook for unknown payment: {reference}")
            return StandardResponse(
                status="error",
                message="Payment not found",
                error_code="PAYMENT_NOT_FOUND",
            )

        # Prevent duplicate webhook processing
        if payment.webhook_processed:
            logger.info(f"Duplicate webhook detected: {reference}")
            return StandardResponse(
                status="success",
                message="Webhook already processed",
            )

        # Process based on event
        if webhook_data["event"] == "charge.success":
            # Update payment status
            PaymentService.update_payment_status(db, payment.id, PaymentStatus.SUCCESS)

            # Create subscription if applicable
            if payment.is_subscription:
                try:
                    subscription = SubscriptionService.create_subscription(
                        db,
                        student_id=payment.student_id,
                        payment_id=payment.id,
                        amount=str(payment.amount),
                        days=30,
                    )
                    logger.info(
                        f"Subscription created via webhook: {subscription.id}"
                    )
                except ValueError as e:
                    logger.error(f"Subscription creation failed: {str(e)}")
            
            else:
                # One-time payment for homework - assign homework to tutor
                try:
                    from services.tutor_service import TutorService
                    from services.homework_service import HomeworkService
                    
                    # Find homework for this payment
                    homeworks = db.query(Homework).filter(
                        Homework.payment_id == payment.id
                    ).all()
                    
                    for homework in homeworks:
                        assignment = TutorService.assign_homework_by_subject(db, homework.id)
                        
                        if assignment:
                            logger.info(
                                f"Homework {homework.id} assigned to tutor {assignment.tutor_id} "
                                f"after payment {payment.id}"
                            )
                            
                            # Send WhatsApp notification to student
                            try:
                                from services.whatsapp_service import WhatsAppService
                                student = db.query(Student).filter(
                                    Student.id == payment.student_id
                                ).first()
                                
                                if student:
                                    await WhatsAppService.send_message(
                                        phone_number=student.phone_number,
                                        message_type="text",
                                        text=(
                                            f"🎓 Great! Your payment has been confirmed!\n\n"
                                            f"Your homework for {homework.subject} has been assigned to a tutor.\n"
                                            f"They'll send you the solution shortly. 📚"
                                        )
                                    )
                            except Exception as e:
                                logger.error(f"Failed to send WhatsApp notification: {str(e)}")
                        else:
                            logger.warning(
                                f"No tutors available to assign homework {homework.id}"
                            )
                            
                except Exception as e:
                    logger.error(f"Error assigning homework after payment: {str(e)}")

        elif webhook_data["event"] == "charge.failed":
            PaymentService.update_payment_status(db, payment.id, PaymentStatus.FAILED)

        # Mark webhook as processed
        PaymentService.mark_webhook_processed(db, payment.id)

        logger.info(
            f"Webhook processed: {reference} - Event: {webhook_data['event']}"
        )

        return StandardResponse(
            status="success",
            message="Webhook processed successfully",
        )

    except Exception as e:
        logger.error(f"Error processing webhook: {str(e)}")
        # Return success to Paystack to prevent retries
        return StandardResponse(
            status="success",
            message="Webhook received",
        )
