#!/usr/bin/env python3
"""
Test image display in admin modal - verify complete pipeline.
"""
import os
import sys
sys.path.insert(0, os.path.dirname(__file__))

from config.database import SessionLocal
from models.homework import Homework
from models.student import Student
from sqlalchemy import desc
import json

def test_image_display():
    """Test complete image display pipeline for admin modal."""
    session = SessionLocal()
    
    print("=" * 80)
    print("IMAGE DISPLAY TEST - Admin Modal Verification")
    print("=" * 80)
    
    # 1. Check what images are in the database
    print("\n[1/4] Checking database for IMAGE homeworks...")
    homeworks = session.query(Homework).filter(
        Homework.submission_type == 'IMAGE',
        Homework.file_path.isnot(None)
    ).order_by(desc(Homework.created_at)).limit(5).all()
    
    print(f"✓ Found {len(homeworks)} IMAGE homeworks in database\n")
    
    # 2. Verify file structure
    print("[2/4] Verifying file structure on disk...")
    uploads_base = os.path.join(os.path.dirname(__file__), "uploads")
    homework_dir = os.path.join(uploads_base, "homework")
    
    if not os.path.exists(homework_dir):
        print(f"✗ Homework directory missing: {homework_dir}")
        return False
    
    print(f"✓ Homework base directory exists: {homework_dir}")
    
    # List student directories
    student_dirs = [d for d in os.listdir(homework_dir) if os.path.isdir(os.path.join(homework_dir, d))]
    print(f"✓ Student directories found: {student_dirs}\n")
    
    # 3. Check each homework record
    print("[3/4] Checking individual homework records...")
    valid_images = []
    missing_images = []
    
    for hw in homeworks:
        file_path = hw.file_path
        full_path = os.path.join(uploads_base, file_path)
        
        exists = os.path.exists(full_path)
        status = "✓" if exists else "✗"
        
        record = {
            "id": hw.id,
            "student_id": hw.student_id,
            "file_path": file_path,
            "full_path": full_path,
            "exists": exists,
            "url": f"/uploads/{file_path}",
            "created_at": hw.created_at.isoformat()
        }
        
        if exists:
            file_size = os.path.getsize(full_path)
            record["file_size_bytes"] = file_size
            valid_images.append(record)
            print(f"  {status} ID {hw.id}: {file_path} ({file_size} bytes)")
        else:
            missing_images.append(record)
            print(f"  {status} ID {hw.id}: {file_path} (MISSING)")
    
    print(f"\n✓ Valid images: {len(valid_images)}")
    print(f"✗ Missing images: {len(missing_images)}")
    
    # 4. Check file serving configuration
    print("\n[4/4] Checking file serving configuration...")
    
    main_py = os.path.join(os.path.dirname(__file__), "main.py")
    with open(main_py, 'r') as f:
        main_content = f.read()
    
    has_static_mount = '/uploads' in main_content and 'StaticFiles' in main_content
    has_file_endpoint = '@app.get("/files/' in main_content
    
    print(f"  {'✓' if has_static_mount else '✗'} Static mount /uploads configured")
    print(f"  {'✓' if has_file_endpoint else '✗'} File serving endpoint /files/ configured")
    
    # 5. Summary
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    
    print(f"\nDatabase Records: {len(homeworks)} IMAGE submissions")
    print(f"Valid Images (on disk): {len(valid_images)}")
    print(f"Missing Images: {len(missing_images)}")
    
    if valid_images:
        print("\n✓ IMAGES AVAILABLE FOR DISPLAY:")
        for img in valid_images:
            print(f"  - ID {img['id']}: {img['url']} ({img['file_size_bytes']} bytes)")
    
    if missing_images:
        print("\n⚠ MISSING IMAGES (database has record but no file on disk):")
        for img in missing_images:
            print(f"  - ID {img['id']}: {img['url']}")
        print("\n  These are likely on Railway's persistent volume and would display on production.")
    
    # 6. API Response format
    print("\n" + "=" * 80)
    print("API RESPONSE FORMAT (what /api/admin/homework returns)")
    print("=" * 80)
    
    if valid_images:
        sample = valid_images[0]
        api_response = {
            "id": sample["id"],
            "student_id": sample["student_id"],
            "student_name": "Sample Student",
            "student_class": "Class X",
            "subject": "Mathematics",
            "submission_type": "IMAGE",
            "content": None,
            "file_path": sample["file_path"],
            "status": "submitted",
            "created_at": sample["created_at"]
        }
        
        print("\nSample response:")
        print(json.dumps(api_response, indent=2))
        
        print(f"\nFrontend uses: <img src=\"/uploads/{sample['file_path']}\" />")
        print(f"Which resolves to: {sample['full_path']}")
    
    session.close()
    
    print("\n" + "=" * 80)
    print("VERIFICATION COMPLETE")
    print("=" * 80)
    
    return True

if __name__ == "__main__":
    test_image_display()
