#!/usr/bin/env python3
"""
Diagnose image serving issues on Railway
"""
import os
import sys

def diagnose_file_serving():
    print("=" * 80)
    print("RAILWAY IMAGE SERVING DIAGNOSTIC")
    print("=" * 80)
    
    # 1. Check environment
    print("\n[1] ENVIRONMENT CHECK")
    print("-" * 80)
    print("Current working directory:", os.getcwd())
    print("Script directory:", os.path.dirname(os.path.abspath(__file__)))
    print("RAILWAY:", os.getenv('RAILWAY_ENVIRONMENT', 'Not set'))
    
    # 2. Check uploads paths
    print("\n[2] UPLOADS PATHS")
    print("-" * 80)
    railway_path = "/app/uploads"
    local_path = os.path.join(os.path.dirname(__file__), "uploads")
    
    print("Railway path: {}".format(railway_path))
    print("  Exists: {}".format("YES" if os.path.exists(railway_path) else "NO"))
    if os.path.exists(railway_path):
        print("  Type: {}".format("Directory" if os.path.isdir(railway_path) else "File"))
        try:
            contents = os.listdir(railway_path)
            print("  Contains: {}".format(contents[:5]))
            print("  Total items: {}".format(len(contents)))
        except Exception as e:
            print("  Error reading: {}".format(e))
    
    print("\nLocal path: {}".format(local_path))
    print("  Exists: {}".format("YES" if os.path.exists(local_path) else "NO"))
    if os.path.exists(local_path):
        print("  Type: {}".format("Directory" if os.path.isdir(local_path) else "File"))
        try:
            contents = os.listdir(local_path)
            print("  Contains: {}".format(contents))
            print("  Total items: {}".format(len(contents)))
        except Exception as e:
            print("  Error reading: {}".format(e))
    
    # 3. Check for homework files
    print("\n[3] HOMEWORK FILES")
    print("-" * 80)
    
    def check_homework_dir(base_path, label):
        hw_path = os.path.join(base_path, "homework")
        print("\n{} homework path: {}".format(label, hw_path))
        if os.path.exists(hw_path):
            print("  Status: EXISTS")
            try:
                students = os.listdir(hw_path)
                print("  Student directories: {}".format(students))
                for student in students[:3]:
                    student_path = os.path.join(hw_path, student)
                    if os.path.isdir(student_path):
                        files = os.listdir(student_path)
                        print("    Student {}: {} files".format(student, len(files)))
                        for f in files[:2]:
                            print("      - {}".format(f))
            except Exception as e:
                print("  Error: {}".format(e))
        else:
            print("  Status: NOT FOUND")
    
    if os.path.exists(railway_path):
        check_homework_dir(railway_path, "Railway")
    if os.path.exists(local_path):
        check_homework_dir(local_path, "Local")
    
    # 4. Test path resolution
    print("\n[4] PATH RESOLUTION TEST")
    print("-" * 80)
    test_path = "homework/6/homework_2348109508833_1767884165205.jpg"
    print("Testing path: {}".format(test_path))
    
    if os.path.exists(railway_path):
        full_path = os.path.join(railway_path, test_path)
        exists = os.path.exists(full_path)
        print("  Railway: {} -> {}".format(full_path, "FOUND" if exists else "NOT FOUND"))
    
    if os.path.exists(local_path):
        full_path = os.path.join(local_path, test_path)
        exists = os.path.exists(full_path)
        print("  Local: {} -> {}".format(full_path, "FOUND" if exists else "NOT FOUND"))
    
    # 5. Check database
    print("\n[5] DATABASE CHECK")
    print("-" * 80)
    try:
        sys.path.insert(0, os.path.dirname(__file__))
        from config.database import SessionLocal
        from models.homework import Homework
        from sqlalchemy import desc
        
        session = SessionLocal()
        image_count = session.query(Homework).filter(
            Homework.submission_type == 'IMAGE'
        ).count()
        
        # Get first few
        homeworks = session.query(Homework).filter(
            Homework.submission_type == 'IMAGE'
        ).order_by(desc(Homework.created_at)).limit(3).all()
        
        print("IMAGE submissions in database: {}".format(image_count))
        print("First 3 submissions:")
        for hw in homeworks:
            print("  ID {}: student_id={} file_path={}".format(
                hw.id, hw.student_id, hw.file_path
            ))
        
        session.close()
    except Exception as e:
        print("Error checking database: {}".format(e))
    
    # 6. Summary
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    
    if os.path.exists(railway_path):
        print("Railway volume EXISTS - file serving from /app/uploads")
    elif os.path.exists(local_path):
        print("Railway volume NOT FOUND - falling back to local uploads")
    else:
        print("WARNING: No uploads directory found!")
    
    print("\nNote: If images show 404, they may be:")
    print("  1. Only in database (uploaded to local, not pushed to Railway)")
    print("  2. Not yet synced to the persistent volume")
    print("  3. Path format issue in the file serving code")

if __name__ == "__main__":
    diagnose_file_serving()
