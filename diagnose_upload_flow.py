#!/usr/bin/env python3
"""
Comprehensive diagnostic for WhatsApp image upload flow.
Traces what happens at each step of image submission.
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

def diagnose_upload_flow():
    """Diagnose the image upload flow"""
    print("=" * 80)
    print("WHATSAPP IMAGE UPLOAD FLOW DIAGNOSTIC")
    print("=" * 80)
    
    # 1. Check configuration
    print("\n[1] WHATSAPP CONFIGURATION")
    print("-" * 80)
    try:
        from config.settings import settings
        print("WhatsApp API Key: {}".format("SET" if settings.whatsapp_api_key else "NOT SET"))
        print("Phone Number ID: {}".format("SET" if settings.whatsapp_phone_number_id else "NOT SET"))
        print("Token: {}".format("SET" if settings.whatsapp_api_key else "NOT SET"))
        
        if not settings.whatsapp_api_key:
            print("\n[CRITICAL] WhatsApp API key not configured!")
            print("  Without this, media downloads will fail")
        if not settings.whatsapp_phone_number_id:
            print("\n[CRITICAL] Phone number ID not configured!")
            print("  This is needed to identify incoming messages")
    except Exception as e:
        print("Error checking config: {}".format(e))
    
    # 2. Check upload directory
    print("\n[2] UPLOAD DIRECTORY")
    print("-" * 80)
    upload_base = os.path.join(os.path.dirname(__file__), "uploads")
    print("Base path: {}".format(upload_base))
    print("Exists: {}".format("YES" if os.path.exists(upload_base) else "NO"))
    print("Writable: {}".format("YES" if os.access(upload_base, os.W_OK) else "NO"))
    
    homework_dir = os.path.join(upload_base, "homework")
    print("\nHomework directory: {}".format(homework_dir))
    print("Exists: {}".format("YES" if os.path.exists(homework_dir) else "NO"))
    
    if os.path.exists(homework_dir):
        try:
            subdirs = os.listdir(homework_dir)
            print("Student directories: {}".format(subdirs))
        except Exception as e:
            print("Error reading: {}".format(e))
    
    # 3. Check upload handler
    print("\n[3] UPLOAD HANDLER")
    print("-" * 80)
    handler_file = os.path.join(os.path.dirname(__file__), "api", "routes", "whatsapp.py")
    print("Handler file: {}".format(handler_file))
    print("Exists: {}".format("YES" if os.path.exists(handler_file) else "NO"))
    
    if os.path.exists(handler_file):
        with open(handler_file, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Check for key components
        checks = {
            "download_media call": "WhatsAppService.download_media" in content,
            "file write": 'open(file_path, "wb")' in content,
            "path conversion": "os.path.relpath" in content,
            "database save": "HomeworkService.submit_homework" in content,
            "error handling": "except Exception" in content,
        }
        
        for check, result in checks.items():
            status = "OK" if result else "MISSING"
            print("  {}: {}".format(check, status))
    
    # 4. Trace upload logic
    print("\n[4] UPLOAD LOGIC FLOW")
    print("-" * 80)
    print("1. WhatsApp webhook receives message with image")
    print("   - Message contains: image_id, from phone_number")
    print()
    print("2. Bot checks: submission_type == 'IMAGE' && message_type == 'image'")
    print("   - Must be in homework_submitted state")
    print("   - Message must actually contain an image_id")
    print()
    print("3. Call WhatsAppService.download_media(image_id)")
    print("   - Requires valid WhatsApp API key")
    print("   - Requires valid phone_number_id")
    print("   - Makes 2 HTTP calls to WhatsApp:")
    print("     a) GET /media/{image_id} -> returns media URL")
    print("     b) GET {media_url} -> downloads actual file")
    print()
    print("4. Save to disk")
    print("   - Create directory: uploads/homework/{student_id}/")
    print("   - Filename: homework_{phone}_{timestamp}.jpg")
    print("   - Write bytes to file")
    print("   - Verify file exists and has content")
    print()
    print("5. Convert path for database")
    print("   - Absolute: /path/to/uploads/homework/6/homework_*.jpg")
    print("   - Relative: homework/6/homework_*.jpg")
    print()
    print("6. Save to database")
    print("   - HomeworkService.submit_homework()")
    print("   - Stores file_path (relative)")
    print("   - Creates homework record")
    print()
    print("7. Response to user")
    print("   - If IMAGE+file: Success message with tutor assignment")
    print("   - If IMAGE but no file: Fallback to TEXT, ask to resubmit")
    
    # 5. Potential failure points
    print("\n[5] FAILURE POINTS")
    print("-" * 80)
    print("POINT 1: Message State")
    print("  Issue: State not homework_submitted when image received")
    print("  Fix: User must select IMAGE first, then send image")
    print()
    print("POINT 2: WhatsApp API Credentials")
    print("  Issue: API key or phone ID invalid/not configured")
    print("  Fix: Check .env file for WHATSAPP_API_KEY and WHATSAPP_PHONE_NUMBER_ID")
    print()
    print("POINT 3: WhatsApp Media Download Timeout")
    print("  Issue: HTTP timeout when downloading from WhatsApp")
    print("  Fix: Check network, WhatsApp API status, media not expired")
    print()
    print("POINT 4: Disk Write Failure")
    print("  Issue: Cannot create directory or write file")
    print("  Fix: Check directory permissions, disk space")
    print()
    print("POINT 5: Path Conversion Bug")
    print("  Issue: Relative path not calculated correctly")
    print("  Fix: Verify os.path.relpath() works on current OS")
    print()
    print("POINT 6: Database Save Failure")
    print("  Issue: Database error when saving homework")
    print("  Fix: Check database connection, schema")
    
    # 6. How to test
    print("\n[6] TESTING STEPS")
    print("-" * 80)
    print("1. Register student via WhatsApp (if not already)")
    print("2. Send 'homework' -> Bot responds with subject selection")
    print("3. Send subject (e.g., 'Math') -> Bot asks for submission type")
    print("4. Send 'image' -> Bot confirms IMAGE mode, asks for image")
    print("5. Send actual image file from phone")
    print("   - Should download and save")
    print("   - Bot should respond with success message")
    print("6. Check admin dashboard -> Image should appear in list")
    print("7. Click 'View Homework' -> Image should display in modal")
    print()
    print("If image doesn't appear:")
    print("  - Check bot logs for download errors")
    print("  - Check uploads/homework/ directory for files")
    print("  - Verify WhatsApp API credentials in .env")
    print("  - Check database for homework record with file_path")
    
    # 7. Database status
    print("\n[7] DATABASE STATUS")
    print("-" * 80)
    try:
        from config.database import SessionLocal
        from models.homework import Homework
        from sqlalchemy import desc
        
        session = SessionLocal()
        
        # Count submissions
        total = session.query(Homework).count()
        image_count = session.query(Homework).filter(
            Homework.submission_type == 'IMAGE'
        ).count()
        text_count = session.query(Homework).filter(
            Homework.submission_type == 'TEXT'
        ).count()
        
        print("Total submissions: {}".format(total))
        print("IMAGE submissions: {}".format(image_count))
        print("TEXT submissions: {}".format(text_count))
        
        # Check for missing files
        image_submissions = session.query(Homework).filter(
            Homework.submission_type == 'IMAGE',
            Homework.file_path.isnot(None)
        ).all()
        
        missing = 0
        for hw in image_submissions:
            full_path = os.path.join(upload_base, hw.file_path)
            if not os.path.exists(full_path):
                missing += 1
        
        print("IMAGE with file_path: {}".format(len(image_submissions)))
        print("But files missing on disk: {}".format(missing))
        
        # Show recent submissions
        recent = session.query(Homework).order_by(desc(Homework.created_at)).limit(3).all()
        print("\nRecent submissions:")
        for hw in recent:
            print("  ID {}: student={} type={} path={}".format(
                hw.id,
                hw.student_id,
                hw.submission_type.value if hw.submission_type else "N/A",
                hw.file_path if hw.file_path else "(no file)"
            ))
        
        session.close()
    except Exception as e:
        print("Error checking database: {}".format(e))
    
    # 8. Summary
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print("To fix WhatsApp image uploads:")
    print()
    print("1. VERIFY: WhatsApp credentials in .env")
    print("   - WHATSAPP_API_KEY")
    print("   - WHATSAPP_PHONE_NUMBER_ID")
    print()
    print("2. TEST: Upload flow with logs")
    print("   - Watch bot logs during image submission")
    print("   - Look for 'Starting image download' message")
    print("   - Check for 'Downloaded media: X bytes'")
    print("   - Verify 'Image saved successfully' message")
    print()
    print("3. VERIFY: Files actually saved")
    print("   - Check uploads/homework/{student_id}/ directory")
    print("   - Look for homework_*.jpg files")
    print()
    print("4. CHECK: Database record")
    print("   - Verify file_path is saved (not NULL)")
    print("   - Verify submission_type is 'IMAGE'")
    print()
    print("5. TEST: Modal display")
    print("   - Admin dashboard -> homework page")
    print("   - Find IMAGE submission -> View Homework")
    print("   - Image should display (or show 'not found')")

if __name__ == "__main__":
    diagnose_upload_flow()
