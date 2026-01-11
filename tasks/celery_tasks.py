"""
Background tasks for Celery.

These tasks run asynchronously and don't block the API.
Perfect for long-running operations.
"""
from config.celery_config import celery_app
from config.database import async_session_maker
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
import logging
import asyncio

logger = logging.getLogger(__name__)


# ============================================================================
# MESSAGING TASKS
# ============================================================================

@celery_app.task(name='tasks.messaging.send_bulk_messages', bind=True)
def send_bulk_messages(self, phone_numbers: list, message: str, message_type: str = 'text'):
    """
    Send bulk messages to multiple users asynchronously.
    
    Returns immediately - processing happens in background.
    
    Example:
        send_bulk_messages.delay(
            phone_numbers=['+234901234567', '+234902345678'],
            message='Hello from bot!',
            message_type='text'
        )
    
    Args:
        phone_numbers: List of phone numbers to send to
        message: Message content
        message_type: 'text', 'template', or 'button'
    """
    try:
        logger.info(f"Starting bulk message task - {len(phone_numbers)} recipients")
        
        # Run async code in sync task
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        async def send_messages():
            from services.whatsapp_service import WhatsAppService
            
            results = {
                'success': 0,
                'failed': 0,
                'errors': []
            }
            
            for idx, phone_number in enumerate(phone_numbers):
                try:
                    result = await WhatsAppService.send_message(
                        phone_number=phone_number,
                        message_type=message_type,
                        text=message
                    )
                    
                    if result.get('status') == 'success':
                        results['success'] += 1
                    else:
                        results['failed'] += 1
                        results['errors'].append({
                            'phone': phone_number,
                            'error': result.get('error')
                        })
                    
                    # Update task progress
                    self.update_state(
                        state='PROGRESS',
                        meta={'current': idx + 1, 'total': len(phone_numbers)}
                    )
                    
                except Exception as e:
                    logger.error(f"Error sending to {phone_number}: {str(e)}")
                    results['failed'] += 1
                    results['errors'].append({
                        'phone': phone_number,
                        'error': str(e)
                    })
            
            return results
        
        results = loop.run_until_complete(send_messages())
        loop.close()
        
        logger.info(f"Bulk message task complete - Success: {results['success']}, Failed: {results['failed']}")
        return results
        
    except Exception as e:
        logger.error(f"Error in bulk message task: {str(e)}")
        self.retry(exc=e, countdown=60, max_retries=3)


@celery_app.task(name='tasks.messaging.send_template_message')
def send_template_message(phone_number: str, template_name: str, params: list = None):
    """
    Send a template message asynchronously.
    
    Args:
        phone_number: Recipient phone number
        template_name: Template name
        params: Template parameters
    """
    try:
        logger.info(f"Sending template message to {phone_number}")
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        async def send():
            from services.whatsapp_service import WhatsAppService
            result = await WhatsAppService.send_message(
                phone_number=phone_number,
                message_type='template',
                template_name=template_name,
                template_params=params or []
            )
            return result
        
        result = loop.run_until_complete(send())
        loop.close()
        
        return result
        
    except Exception as e:
        logger.error(f"Error sending template message: {str(e)}")
        raise


# ============================================================================
# NOTIFICATION TASKS
# ============================================================================

@celery_app.task(name='tasks.notifications.send_bulk_notifications')
def send_bulk_notifications(user_ids: list, title: str, message: str):
    """
    Send bulk notifications to multiple users.
    
    Args:
        user_ids: List of student/user IDs
        title: Notification title
        message: Notification message
    """
    try:
        logger.info(f"Sending notifications to {len(user_ids)} users")
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        async def send_notifications():
            async with async_session_maker() as session:
                from models.notification import Notification
                from datetime import datetime
                
                notifications = [
                    Notification(
                        user_id=user_id,
                        title=title,
                        message=message,
                        created_at=datetime.now(),
                        is_read=False
                    )
                    for user_id in user_ids
                ]
                
                session.add_all(notifications)
                await session.commit()
                
                logger.info(f"Created {len(notifications)} notifications")
                return len(notifications)
        
        result = loop.run_until_complete(send_notifications())
        loop.close()
        
        return {'created': result}
        
    except Exception as e:
        logger.error(f"Error sending bulk notifications: {str(e)}")
        raise


# ============================================================================
# REPORT/EXPORT TASKS
# ============================================================================

@celery_app.task(name='tasks.reports.generate_student_report')
def generate_student_report(student_id: int):
    """
    Generate a detailed student report asynchronously.
    
    Args:
        student_id: Student ID
    """
    try:
        logger.info(f"Generating report for student {student_id}")
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        async def generate():
            async with async_session_maker() as session:
                from models.student import Student
                from models.homework import Homework
                from models.payment import Payment
                
                # Fetch student data
                result = await session.execute(
                    select(Student).where(Student.id == student_id)
                )
                student = result.scalars().first()
                
                if not student:
                    return {'error': 'Student not found'}
                
                # Fetch related data
                homework_result = await session.execute(
                    select(Homework).where(Homework.student_id == student_id)
                )
                homeworks = homework_result.scalars().all()
                
                payment_result = await session.execute(
                    select(Payment).where(Payment.student_id == student_id)
                )
                payments = payment_result.scalars().all()
                
                report = {
                    'student': {
                        'id': student.id,
                        'name': student.full_name,
                        'email': student.email,
                        'phone': student.phone_number,
                    },
                    'homework_count': len(homeworks),
                    'payment_count': len(payments),
                    'total_paid': sum(p.amount for p in payments if p.status == 'completed'),
                }
                
                return report
        
        result = loop.run_until_complete(generate())
        loop.close()
        
        return result
        
    except Exception as e:
        logger.error(f"Error generating report: {str(e)}")
        raise


@celery_app.task(name='tasks.reports.export_students_csv')
def export_students_csv(filters: dict = None):
    """
    Export students to CSV asynchronously.
    
    Args:
        filters: Filter criteria
    """
    try:
        logger.info(f"Exporting students with filters: {filters}")
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        async def export():
            import csv
            from io import StringIO
            from datetime import datetime
            from models.student import Student
            
            async with async_session_maker() as session:
                stmt = select(Student)
                
                # Apply filters
                if filters:
                    if filters.get('is_active') is not None:
                        stmt = stmt.where(Student.is_active == filters['is_active'])
                    if filters.get('email'):
                        stmt = stmt.where(Student.email.contains(filters['email']))
                
                result = await session.execute(stmt)
                students = result.scalars().all()
                
                # Generate CSV
                output = StringIO()
                writer = csv.writer(output)
                writer.writerow(['ID', 'Name', 'Email', 'Phone', 'Class', 'Active', 'Joined'])
                
                for student in students:
                    writer.writerow([
                        student.id,
                        student.full_name,
                        student.email,
                        student.phone_number,
                        student.class_grade,
                        'Yes' if student.is_active else 'No',
                        student.date_created.strftime('%Y-%m-%d') if student.date_created else '',
                    ])
                
                return {
                    'filename': f'students_export_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv',
                    'rows': len(students),
                    'data': output.getvalue()
                }
        
        result = loop.run_until_complete(export())
        loop.close()
        
        return result
        
    except Exception as e:
        logger.error(f"Error exporting students: {str(e)}")
        raise


# ============================================================================
# SCHEDULED TASKS
# ============================================================================

@celery_app.task(name='tasks.scheduled.cleanup_old_sessions')
def cleanup_old_sessions():
    """
    Clean up old chat sessions and expired data.
    Runs automatically on schedule.
    """
    try:
        logger.info("Running scheduled cleanup task")
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        async def cleanup():
            from datetime import datetime, timedelta
            from models.conversation import Conversation
            
            async with async_session_maker() as session:
                cutoff_date = datetime.now() - timedelta(days=30)
                
                # Delete old conversations
                result = await session.execute(
                    select(Conversation).where(
                        Conversation.created_at < cutoff_date
                    )
                )
                old_conversations = result.scalars().all()
                
                for conv in old_conversations:
                    await session.delete(conv)
                
                await session.commit()
                
                logger.info(f"Cleaned up {len(old_conversations)} old conversations")
                return {'cleaned': len(old_conversations)}
        
        result = loop.run_until_complete(cleanup())
        loop.close()
        
        return result
        
    except Exception as e:
        logger.error(f"Error in cleanup task: {str(e)}")
        raise


# ============================================================================
# HOMEWORK TASKS
# ============================================================================

@celery_app.task(name='tasks.homework.send_submission_confirmation', bind=True)
def send_homework_submission_confirmation(self, student_phone: str, subject: str, homework_id: int):
    """
    Send WhatsApp confirmation to student after homework image upload.
    
    This task runs asynchronously and doesn't block the upload response.
    It includes retry logic with exponential backoff for reliability.
    
    Args:
        student_phone: Student's phone number (with country code)
        subject: Homework subject
        homework_id: Homework ID for reference
    
    Returns:
        Dict with result status and message
    """
    task_id = self.request.id
    retry_count = self.request.retries
    
    try:
        logger.info(f"📸 [Task {task_id}] Sending homework confirmation to {student_phone}")
        logger.info(f"   📚 Subject: {subject}")
        logger.info(f"   📋 Homework ID: {homework_id}")
        logger.info(f"   🔄 Attempt: {retry_count + 1}/4 (3 retries available)")
        
        # Validate phone number
        clean_phone = student_phone.replace('+', '').replace(' ', '')
        if not clean_phone or not clean_phone.isdigit():
            logger.error(f"❌ [Task {task_id}] Invalid phone number format: {student_phone}")
            return {
                'status': 'error',
                'message': f'Invalid phone number format: {student_phone}',
                'task_id': task_id
            }
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        async def send_confirmation():
            from services.whatsapp_service import WhatsAppService
            
            confirmation_message = (
                f"✅ Homework Submitted Successfully!\n\n"
                f"📚 Subject: {subject}\n"
                f"📷 Type: Image\n"
                f"📊 Reference ID: {homework_id}\n\n"
                f"🎓 A tutor has been assigned and will review your work shortly.\n"
                f"You'll receive feedback soon!"
            )
            
            logger.info(f"   [Task {task_id}] Calling WhatsApp API...")
            result = await WhatsAppService.send_message(
                phone_number=student_phone,
                message_type='text',
                text=confirmation_message
            )
            
            return result
        
        result = loop.run_until_complete(send_confirmation())
        loop.close()
        
        if result.get('status') == 'success':
            logger.info(f"✅ [Task {task_id}] Homework confirmation sent successfully to {student_phone}")
            return {
                'status': 'success',
                'message': f'Confirmation sent to {student_phone}',
                'task_id': task_id,
                'api_response': result
            }
        else:
            error_msg = result.get('error') or result.get('message', 'Unknown error')
            logger.warning(f"⚠️ [Task {task_id}] Failed to send confirmation: {error_msg}")
            logger.warning(f"   Response: {result}")
            
            # Retry on failure with exponential backoff
            if retry_count < 3:
                countdown = 30 * (retry_count + 1)  # 30s, 60s, 90s
                logger.info(f"   🔄 Retrying in {countdown}s...")
                self.retry(exc=Exception(error_msg), countdown=countdown, max_retries=3)
            else:
                logger.error(f"❌ [Task {task_id}] Max retries reached. Giving up.")
                return {
                    'status': 'error',
                    'message': f'Failed after 3 retries: {error_msg}',
                    'task_id': task_id
                }
        
    except Exception as e:
        logger.error(f"❌ [Task {task_id}] Error sending homework confirmation: {str(e)}")
        import traceback
        logger.error(f"   Traceback:\n{traceback.format_exc()}")
        
        # Retry with exponential backoff
        if retry_count < 3:
            countdown = 30 * (retry_count + 1)
            logger.info(f"   🔄 Retrying in {countdown}s...")
            self.retry(exc=e, countdown=countdown, max_retries=3)
        else:
            logger.error(f"❌ [Task {task_id}] Max retries reached after exception.")
            return {
                'status': 'error',
                'message': str(e),
                'task_id': task_id
            }


@celery_app.on_after_finalize.connect
def setup_periodic_tasks(sender, **kwargs):
    """
    Set up periodic/scheduled tasks.
    These run automatically on a schedule.
    """
    # Clean up old sessions every day at 2 AM
    sender.add_periodic_task(
        86400.0,  # 24 hours
        cleanup_old_sessions.s(),
        name='Cleanup old sessions'
    )
