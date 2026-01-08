"""
Verify image homework paths in the system
"""
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

from config.database import SessionLocal
from models.homework import Homework

def verify_image_paths():
    """Verify all image homework paths."""
    db = SessionLocal()
    
    try:
        print("=" * 80)
        print("IMAGE HOMEWORK PATH VERIFICATION")
        print("=" * 80)
        
        # Get all homework with file_path
        homeworks = db.query(Homework).filter(Homework.file_path != None).all()
        
        print(f"\nFound {len(homeworks)} homework records with file paths:\n")
        
        for hw in homeworks:
            if hw.file_path and 'homework' in hw.file_path:
                db_path = hw.file_path
                disk_path = f"uploads/{hw.file_path}"
                url_path = f"/uploads/{hw.file_path}"
                
                exists = os.path.exists(disk_path)
                
                print(f"Homework ID: {hw.id}")
                print(f"  Subject: {hw.subject}")
                print(f"  Type: {hw.submission_type}")
                print(f"  Database Path:  {db_path}")
                print(f"  Disk Path:      {disk_path}")
                print(f"  URL Path:       {url_path}")
                print(f"  File Exists:    {'✓ YES' if exists else '✗ NO'}")
                if exists:
                    size = os.path.getsize(disk_path)
                    print(f"  File Size:      {size} bytes")
                print()
        
        print("=" * 80)
        print("DIRECTORY STRUCTURE")
        print("=" * 80)
        print("\nUploads directory contents:")
        for root, dirs, files in os.walk("uploads"):
            level = root.replace("uploads", "").count(os.sep)
            indent = " " * 2 * level
            print(f"{indent}{os.path.basename(root)}/")
            subindent = " " * 2 * (level + 1)
            for file in files:
                file_path = os.path.join(root, file)
                size = os.path.getsize(file_path)
                print(f"{subindent}{file} ({size} bytes)")
        
        print("\n" + "=" * 80)
        print("SUMMARY")
        print("=" * 80)
        print("""
On Disk:     uploads/homework/{student_id}/homework_*.jpg
In Database: homework/{student_id}/homework_*.jpg
In Frontend: /uploads/homework/{student_id}/homework_*.jpg

Example:
  On Disk:     uploads/homework/6/homework_2348109508833_1767880566319.jpg
  In Database: homework/6/homework_2348109508833_1767880566319.jpg
  In Frontend: /uploads/homework/6/homework_2348109508833_1767880566319.jpg
""")
        
    finally:
        db.close()

if __name__ == "__main__":
    verify_image_paths()
