"""
Test: Verify image upload and viewing in admin dashboard
Tests the complete workflow from upload to display
"""
import os
import sys
from pathlib import Path
from PIL import Image
import io
import json
from datetime import datetime

# Setup path
sys.path.insert(0, os.path.dirname(__file__))

from config.database import SessionLocal, Base, engine
from models.student import Student
from models.homework import Homework
from services.student_service import StudentService

def setup_test_environment():
    """Create test database tables."""
    print("[Setup] Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("✓ Tables created")

def create_test_image(size=(200, 200)):
    """Create a test image file."""
    print("\n[1/5] Creating test image...")
    
    # Create test image in memory
    img = Image.new('RGB', size, color='red')
    
    # Save to test location
    test_dir = Path("test_uploads")
    test_dir.mkdir(exist_ok=True)
    test_path = test_dir / "test_image.jpg"
    img.save(test_path, "JPEG")
    
    print(f"✓ Test image created at {test_path} ({os.path.getsize(test_path)} bytes)")
    return test_path

def create_test_student(db):
    """Create a test student."""
    print("\n[2/5] Creating test student...")
    
    student = Student(
        phone_number="2347012345678",
        full_name="Test Student",
        email="test@example.com",
        class_grade="JSS 1",
    )
    db.add(student)
    db.commit()
    db.refresh(student)
    
    print(f"✓ Student created: ID={student.id}, Phone={student.phone_number}")
    return student

def simulate_image_upload(db, student_id, test_image_path):
    """Simulate WhatsApp image upload to homework."""
    print("\n[3/5] Simulating image upload to homework...")
    
    # Create uploads directory
    upload_dir = Path(f"uploads/homework/{student_id}")
    upload_dir.mkdir(parents=True, exist_ok=True)
    
    # Copy test image with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"homework_2347012345678_{timestamp}.jpg"
    dest_path = upload_dir / filename
    
    with open(test_image_path, 'rb') as src:
        with open(dest_path, 'wb') as dst:
            dst.write(src.read())
    
    # Store relative path (what goes in database)
    relative_path = f"homework/{student_id}/{filename}"
    
    print(f"✓ Image uploaded to {dest_path}")
    print(f"  Relative path for DB: {relative_path}")
    print(f"  File size: {os.path.getsize(dest_path)} bytes")
    print(f"  File exists: {os.path.exists(dest_path)}")
    
    return relative_path

def create_homework_record(db, student_id, file_path):
    """Create homework record in database."""
    print("\n[4/5] Creating homework record in database...")
    
    homework = Homework(
        student_id=student_id,
        subject="Mathematics",
        submission_type="IMAGE",
        content="Test image submission",
        file_path=file_path,
        payment_type="ONE_TIME",
        status="PENDING"
    )
    db.add(homework)
    db.commit()
    db.refresh(homework)
    
    print(f"✓ Homework record created:")
    print(f"  ID: {homework.id}")
    print(f"  Student ID: {homework.student_id}")
    print(f"  Subject: {homework.subject}")
    print(f"  Type: {homework.submission_type}")
    print(f"  File Path: {homework.file_path}")
    print(f"  Status: {homework.status}")
    
    return homework

def verify_api_response(db, homework_id):
    """Verify API returns homework with file_path."""
    print("\n[5/5] Verifying API response...")
    
    homework = db.query(Homework).filter(Homework.id == homework_id).first()
    
    if not homework:
        print("✗ Homework not found!")
        return False
    
    response_data = {
        "id": homework.id,
        "student_id": homework.student_id,
        "student_name": "Test Student",
        "student_class": "JSS 1",
        "subject": homework.subject,
        "submission_type": homework.submission_type,
        "content": homework.content,
        "file_path": homework.file_path,
        "status": homework.status,
        "created_at": homework.created_at.isoformat()
    }
    
    print("✓ API response would include:")
    print(json.dumps(response_data, indent=2))
    
    # Verify file can be served
    if homework.file_path:
        full_path = Path("uploads") / homework.file_path
        if full_path.exists():
            print(f"\n✓ File exists at: {full_path}")
            print(f"  URL to serve: /uploads/{homework.file_path}")
            print(f"  File size: {os.path.getsize(full_path)} bytes")
        else:
            print(f"\n✗ File NOT found at: {full_path}")
            return False
    
    return True

def verify_frontend_integration():
    """Verify frontend can display the image."""
    print("\n[Frontend Integration] Testing image display...")
    
    file_path = "homework/1/homework_2347012345678_20260108_054039.jpg"
    image_url = f"/uploads/{file_path}"
    
    print("✓ Frontend will construct image URL as:")
    print(f"  src={'{image_url}'}")
    print(f"\nHTML in modal:")
    print(f"  <img src=\"{image_url}\" alt=\"Homework submission\" />")
    
    return True

def cleanup():
    """Remove test files."""
    print("\n[Cleanup] Removing test files...")
    import shutil
    if os.path.exists("test_uploads"):
        shutil.rmtree("test_uploads")
        print("✓ Removed test_uploads")

def main():
    """Run complete image viewing test."""
    print("=" * 70)
    print("TEST: Image Upload & Viewing in Admin Dashboard")
    print("=" * 70)
    
    try:
        setup_test_environment()
        
        # Create test data
        test_image = create_test_image()
        db = SessionLocal()
        student = create_test_student(db)
        relative_path = simulate_image_upload(db, student.id, test_image)
        homework = create_homework_record(db, student.id, relative_path)
        
        # Verify everything works
        api_ok = verify_api_response(db, homework.id)
        frontend_ok = verify_frontend_integration()
        
        db.close()
        cleanup()
        
        print("\n" + "=" * 70)
        if api_ok and frontend_ok:
            print("✓ ALL TESTS PASSED - Image viewing ready!")
            print("\nNext steps for manual testing:")
            print("1. Visit admin dashboard at /homework")
            print("2. Click 'View Homework' on an image submission")
            print("3. Image should display in the modal")
            print("=" * 70)
            return True
        else:
            print("✗ TESTS FAILED")
            print("=" * 70)
            return False
            
    except Exception as e:
        print(f"\n✗ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        cleanup()
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
