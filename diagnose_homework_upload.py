#!/usr/bin/env python3
"""
Diagnostic script to verify Celery and WhatsApp configuration for homework uploads.
Run this to troubleshoot image homework upload issues.
"""

import os
import sys
import asyncio
import logging
from pathlib import Path

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def check_redis_connection():
    """Check if Redis is accessible."""
    logger.info("\n" + "="*80)
    logger.info("📍 CHECKING REDIS CONNECTION")
    logger.info("="*80)
    
    try:
        import redis
        from config.settings import settings
        
        redis_url = getattr(settings, 'redis_url', 'redis://localhost:6379/0')
        logger.info(f"📌 Redis URL: {redis_url}")
        
        # Try to connect
        r = redis.from_url(redis_url)
        ping = r.ping()
        
        if ping:
            logger.info("✅ Redis connection successful!")
            logger.info(f"   🔗 Server: Connected")
            logger.info(f"   📊 DB size: {r.dbsize()} keys")
            return True
        else:
            logger.error("❌ Redis connection failed")
            return False
            
    except Exception as e:
        logger.error(f"❌ Error checking Redis: {str(e)}")
        return False

def check_celery_config():
    """Check Celery configuration."""
    logger.info("\n" + "="*80)
    logger.info("📍 CHECKING CELERY CONFIGURATION")
    logger.info("="*80)
    
    try:
        from config.celery_config import celery_app
        from config.settings import settings
        
        redis_url = getattr(settings, 'redis_url', 'redis://localhost:6379/0')
        
        logger.info(f"✅ Celery app loaded successfully")
        logger.info(f"   📌 Broker URL: {celery_app.conf.get('broker_url', 'Not set')}")
        logger.info(f"   📌 Backend URL: {celery_app.conf.get('result_backend', 'Not set')}")
        logger.info(f"   📌 Task serializer: {celery_app.conf.get('task_serializer', 'Not set')}")
        logger.info(f"   📌 Task timeout (soft): {celery_app.conf.get('task_soft_time_limit', 'Not set')}s")
        logger.info(f"   📌 Task timeout (hard): {celery_app.conf.get('task_time_limit', 'Not set')}s")
        
        # Try to inspect active tasks
        try:
            from celery.app.control import Inspect
            inspector = celery_app.control.inspect()
            stats = inspector.stats()
            
            if stats:
                logger.info(f"✅ Celery workers found: {len(stats)} worker(s) active")
                for worker_name, worker_stats in stats.items():
                    logger.info(f"   🤖 Worker: {worker_name}")
                    logger.info(f"      Pool: {worker_stats.get('pool', {}).get('implementation', 'Unknown')}")
            else:
                logger.warning("⚠️  No Celery workers are currently running!")
                logger.warning("   This means tasks will be queued but not executed.")
                logger.warning("   You need to start a Celery worker with: celery -A tasks.celery_tasks worker")
        except Exception as e:
            logger.warning(f"⚠️  Could not inspect Celery workers: {str(e)}")
            logger.warning("   Workers might not be running or Celery is not properly configured")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Error checking Celery: {str(e)}")
        return False

def check_whatsapp_config():
    """Check WhatsApp API configuration."""
    logger.info("\n" + "="*80)
    logger.info("📍 CHECKING WHATSAPP API CONFIGURATION")
    logger.info("="*80)
    
    try:
        from config.settings import settings
        
        api_key = getattr(settings, 'whatsapp_api_key', None)
        phone_id = getattr(settings, 'whatsapp_phone_number_id', None)
        
        if not api_key:
            logger.error("❌ WhatsApp API key is not configured (WHATSAPP_API_KEY env var missing)")
            return False
        
        if not phone_id:
            logger.error("❌ WhatsApp phone number ID is not configured (WHATSAPP_PHONE_NUMBER_ID env var missing)")
            return False
        
        logger.info("✅ WhatsApp API configuration found")
        logger.info(f"   🔑 API Key: {'*' * 20}...{api_key[-4:]}" if len(api_key) > 20 else "   🔑 API Key: ***")
        logger.info(f"   📱 Phone ID: {phone_id}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Error checking WhatsApp config: {str(e)}")
        return False

async def test_whatsapp_api():
    """Test WhatsApp API with a test message."""
    logger.info("\n" + "="*80)
    logger.info("📍 TESTING WHATSAPP API")
    logger.info("="*80)
    
    try:
        from services.whatsapp_service import WhatsAppService
        
        test_phone = os.getenv('TEST_PHONE_NUMBER', '2348012345678')
        
        logger.info(f"📞 Test phone number: {test_phone}")
        logger.warning(f"⚠️  WARNING: This will send a test message to {test_phone}!")
        logger.info(f"   Make sure this is a valid phone number with country code (e.g., 234XXXXXXXXXX)")
        
        test_message = (
            "🧪 Test message from EduBot homework upload diagnostic.\n"
            "This confirms your WhatsApp integration is working correctly.\n"
            "If you received this, WhatsApp API is configured properly!"
        )
        
        logger.info("   Sending test message...")
        result = await WhatsAppService.send_message(
            phone_number=test_phone,
            message_type='text',
            text=test_message
        )
        
        if result.get('status') == 'success':
            logger.info("✅ WhatsApp test message sent successfully!")
            logger.info(f"   Response: {result}")
            return True
        else:
            logger.error(f"❌ WhatsApp test message failed")
            logger.error(f"   Response: {result}")
            return False
            
    except Exception as e:
        logger.error(f"❌ Error testing WhatsApp API: {str(e)}")
        import traceback
        logger.error(f"   {traceback.format_exc()}")
        return False

def check_student_database():
    """Check if student records have valid phone numbers."""
    logger.info("\n" + "="*80)
    logger.info("📍 CHECKING STUDENT DATABASE")
    logger.info("="*80)
    
    try:
        from config.database import get_db_sync, SessionLocal
        from models.student import Student
        from sqlalchemy.orm import Session
        
        try:
            db = SessionLocal()
        except:
            db = next(get_db_sync())
        
        # Check a few students
        students = db.query(Student).limit(5).all()
        
        if not students:
            logger.warning("⚠️  No students found in database")
            return True
        
        logger.info(f"✅ Found {db.query(Student).count()} total students in database")
        
        students_with_phone = 0
        students_without_phone = 0
        
        for student in students:
            if student.phone_number:
                phone = student.phone_number.replace('+', '')
                if phone.isdigit():
                    students_with_phone += 1
                    logger.info(f"   ✅ Student {student.id}: Valid phone {student.phone_number}")
                else:
                    students_without_phone += 1
                    logger.warning(f"   ⚠️  Student {student.id}: Invalid phone format {student.phone_number}")
            else:
                students_without_phone += 1
                logger.warning(f"   ❌ Student {student.id}: No phone number")
        
        if students_without_phone > 0:
            logger.warning(f"⚠️  {students_without_phone} out of {len(students)} sample students have no/invalid phone")
        
        db.close()
        return True
        
    except Exception as e:
        logger.error(f"❌ Error checking student database: {str(e)}")
        return False

def check_homework_upload_endpoint():
    """Verify homework upload endpoint configuration."""
    logger.info("\n" + "="*80)
    logger.info("📍 CHECKING HOMEWORK UPLOAD ENDPOINT")
    logger.info("="*80)
    
    try:
        from api.routes import homework
        
        logger.info("✅ Homework routes module loaded")
        
        # Check if upload endpoint exists
        router = homework.router
        routes = [route for route in router.routes if 'upload' in route.path.lower()]
        
        if routes:
            for route in routes:
                logger.info(f"   ✅ Endpoint found: POST {route.path}")
        else:
            logger.warning("⚠️  No upload endpoint found in homework router")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Error checking homework endpoint: {str(e)}")
        return False

def main():
    """Run all diagnostic checks."""
    logger.info("\n")
    logger.info("╔" + "="*78 + "╗")
    logger.info("║" + " "*78 + "║")
    logger.info("║" + "  EduBot Homework Upload - Diagnostic Report".center(78) + "║")
    logger.info("║" + " "*78 + "║")
    logger.info("╚" + "="*78 + "╝")
    
    results = []
    
    # Run checks
    results.append(("Redis Connection", check_redis_connection()))
    results.append(("Celery Configuration", check_celery_config()))
    results.append(("WhatsApp Configuration", check_whatsapp_config()))
    results.append(("Student Database", check_student_database()))
    results.append(("Homework Upload Endpoint", check_homework_upload_endpoint()))
    
    # Summary
    logger.info("\n" + "="*80)
    logger.info("📊 DIAGNOSTIC SUMMARY")
    logger.info("="*80)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for check_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        logger.info(f"{status}  {check_name}")
    
    logger.info(f"\nTotal: {passed}/{total} checks passed")
    
    if passed == total:
        logger.info("\n🎉 All checks passed! Your system is configured correctly.")
    else:
        logger.warning(f"\n⚠️  {total - passed} check(s) failed. Review the output above.")
    
    # Recommendations
    logger.info("\n" + "="*80)
    logger.info("💡 TROUBLESHOOTING GUIDE")
    logger.info("="*80)
    
    if not results[0][1]:  # Redis failed
        logger.info("""
🔴 Redis Connection Failed:
  1. Verify Redis is running: redis-cli ping
  2. Check REDIS_URL environment variable
  3. On Railway: Ensure Redis add-on is connected
  4. Verify network connectivity to Redis server
        """)
    
    if not results[1][1]:  # Celery failed
        logger.info("""
🔴 Celery Configuration Failed:
  1. Ensure Redis is running (see above)
  2. Start Celery worker: celery -A tasks.celery_tasks worker -l info
  3. On Railway: Create a Celery worker dyno/service
  4. Check logs: docker logs <container> or Railway logs
        """)
    
    if not results[2][1]:  # WhatsApp failed
        logger.info("""
🔴 WhatsApp Configuration Failed:
  1. Set WHATSAPP_API_KEY environment variable
  2. Set WHATSAPP_PHONE_NUMBER_ID environment variable
  3. Verify credentials are correct
  4. Check WhatsApp Business account settings
        """)
    
    if not results[3][1]:  # Student DB failed
        logger.info("""
🔴 Student Database Failed:
  1. Ensure database is accessible
  2. Run migrations: alembic upgrade head
  3. Verify student records exist with phone numbers
  4. Check phone number format (should include country code)
        """)
    
    logger.info("\n" + "="*80)
    logger.info("📚 For more info:")
    logger.info("  - Frontend logs: Browser DevTools → Console")
    logger.info("  - Backend logs: docker logs <backend-container> or Railway logs")
    logger.info("  - Celery logs: celery -A tasks.celery_tasks worker -l info")
    logger.info("="*80 + "\n")

if __name__ == "__main__":
    main()
