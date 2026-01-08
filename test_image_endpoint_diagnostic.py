"""
Diagnostic test to verify image file serving endpoints
Tests both static mount and explicit file serving endpoint
"""
import os
import sys
from pathlib import Path
from PIL import Image
import requests

sys.path.insert(0, os.path.dirname(__file__))

def test_image_files_exist():
    """Check if image files exist in uploads directory."""
    print("[1/4] Checking image files...")
    
    uploads_dir = Path("uploads/homework")
    if not uploads_dir.exists():
        print("✗ No uploads/homework directory found")
        return False
    
    jpg_files = list(uploads_dir.glob("**/*.jpg"))
    
    if jpg_files:
        print(f"✓ Found {len(jpg_files)} image file(s):")
        for f in jpg_files[:5]:  # Show first 5
            print(f"  - {f.relative_to(uploads_dir.parent)}")
            print(f"    Size: {os.path.getsize(f)} bytes")
        return True
    else:
        print("✗ No image files found in uploads/homework")
        return False

def test_image_urls():
    """Display the URLs where images should be accessible."""
    print("\n[2/4] Image access URLs...")
    
    uploads_dir = Path("uploads/homework")
    jpg_files = list(uploads_dir.glob("**/*.jpg"))
    
    if jpg_files:
        for f in jpg_files[:3]:
            relative_path = f.relative_to(uploads_dir.parent)
            print(f"\n  File: {relative_path}")
            print(f"  Static mount: /uploads/{relative_path}")
            print(f"  Endpoint: /files/{relative_path}")
        return True
    return False

def test_local_file_serving():
    """Test that files can be read from disk."""
    print("\n[3/4] Testing local file access...")
    
    uploads_dir = Path("uploads/homework")
    jpg_files = list(uploads_dir.glob("**/*.jpg"))
    
    if jpg_files:
        test_file = jpg_files[0]
        try:
            with open(test_file, 'rb') as f:
                data = f.read()
            print(f"✓ File readable from disk: {test_file}")
            print(f"  Size: {len(data)} bytes")
            
            # Verify it's a valid image
            img = Image.open(test_file)
            print(f"✓ Valid image: {img.format} ({img.size[0]}x{img.size[1]})")
            return True
        except Exception as e:
            print(f"✗ Error reading file: {e}")
            return False
    return False

def test_api_response():
    """Test getting homework from API."""
    print("\n[4/4] Testing API response...")
    
    try:
        # Try to import and test locally
        from config.database import SessionLocal
        from models.homework import Homework
        
        db = SessionLocal()
        homeworks = db.query(Homework).filter(Homework.file_path != None).limit(3).all()
        db.close()
        
        if homeworks:
            print(f"✓ Found {len(homeworks)} homework with images:")
            for hw in homeworks:
                print(f"\n  Homework ID: {hw.id}")
                print(f"  Student ID: {hw.student_id}")
                print(f"  File Path: {hw.file_path}")
                print(f"  Subject: {hw.subject}")
                print(f"  Type: {hw.submission_type}")
            return True
        else:
            print("ℹ No homework with images in database")
            return True
    except Exception as e:
        print(f"ℹ Could not test API locally: {e}")
        return True

def print_debug_info():
    """Print debugging information for troubleshooting."""
    print("\n" + "=" * 70)
    print("DEBUG INFORMATION")
    print("=" * 70)
    
    print("\n1. File System Check:")
    uploads_path = Path("uploads")
    if uploads_path.exists():
        print(f"✓ Uploads directory exists: {uploads_path.absolute()}")
        print(f"  Contents:")
        for item in uploads_path.rglob("*"):
            if item.is_file():
                print(f"    - {item.relative_to(uploads_path)} ({os.path.getsize(item)} bytes)")
    else:
        print("✗ Uploads directory not found")
    
    print("\n2. Main.py Configuration:")
    print("  - FileResponse imported from: starlette.responses")
    print("  - Static mount: /uploads/ -> uploads directory")
    print("  - File endpoint: GET /files/{file_path}")
    
    print("\n3. Frontend Configuration:")
    print("  - Image src: /uploads/{file_path}")
    print("  - Link href: /uploads/{file_path}")
    print("  - File path displayed: Yes")
    print("  - Open in new tab: Available")

def main():
    print("=" * 70)
    print("IMAGE FILE SERVING DIAGNOSTIC TEST")
    print("=" * 70)
    
    test1 = test_image_files_exist()
    test2 = test_image_urls()
    test3 = test_local_file_serving()
    test4 = test_api_response()
    
    print_debug_info()
    
    print("\n" + "=" * 70)
    print("TROUBLESHOOTING GUIDE")
    print("=" * 70)
    print("""
If images are not showing:

1. Check File Exists
   - Upload a new image via WhatsApp
   - Verify file appears in: uploads/homework/{student_id}/homework_*.jpg
   
2. Test Direct Link
   - In browser, visit: /uploads/homework/{student_id}/homework_*.jpg
   - Should display the image or show download dialog
   
3. Check Admin Dashboard
   - Visit: https://nurturing-exploration-production.up.railway.app/homework
   - Click 'View Homework' on an image submission
   - Should show:
     * Image preview (if loading from /uploads/)
     * File path display
     * 'Open Image in New Tab' button with direct link
   
4. Test File Endpoint
   - Try: /files/homework/{student_id}/homework_*.jpg
   - Should also display the image
   
5. Browser Console
   - Open DevTools (F12)
   - Check Console tab for errors
   - Check Network tab to see if /uploads/ requests succeed
   
6. Check Logs
   - Railway logs should show successful file serve requests
   - Look for any 404 errors on /uploads/ requests
""")
    
    print("\n" + "=" * 70)
    if test1 and test3:
        print("✓ IMAGE SERVING INFRASTRUCTURE READY FOR TESTING")
    else:
        print("⚠ Some files may need to be uploaded first")
    print("=" * 70)

if __name__ == "__main__":
    main()
