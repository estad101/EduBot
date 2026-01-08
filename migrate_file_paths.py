"""
Migration script to fix incorrect file paths in homework records.
Removes the 'uploads/' prefix from stored paths.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

from config.database import SessionLocal
from models.homework import Homework

def fix_file_paths():
    """Fix all homework records with incorrect file paths."""
    db = SessionLocal()
    
    try:
        # Get all homework with file_path
        homeworks = db.query(Homework).filter(Homework.file_path != None).all()
        
        if not homeworks:
            print("No homework records with file paths found")
            return 0
        
        fixed_count = 0
        
        print(f"Found {len(homeworks)} homework records with file paths")
        print("=" * 70)
        
        for hw in homeworks:
            original_path = hw.file_path
            
            # Check if path starts with 'uploads/'
            if original_path.startswith('uploads/') or original_path.startswith('uploads\\'):
                # Remove the 'uploads/' prefix
                new_path = original_path[8:]  # Remove 'uploads/'
                # Normalize path separators
                new_path = new_path.replace('\\', '/')
                
                print(f"\nHomework ID: {hw.id}")
                print(f"  Before: {original_path}")
                print(f"  After:  {new_path}")
                
                hw.file_path = new_path
                fixed_count += 1
            else:
                print(f"\nHomework ID: {hw.id}")
                print(f"  Path: {original_path}")
                print(f"  Status: ✓ Already correct")
        
        if fixed_count > 0:
            print(f"\n" + "=" * 70)
            print(f"Committing {fixed_count} changes...")
            db.commit()
            print(f"✓ Successfully fixed {fixed_count} file paths")
        else:
            print(f"\n" + "=" * 70)
            print("No paths needed fixing")
            db.close()
        
        return fixed_count
        
    except Exception as e:
        print(f"Error: {str(e)}")
        db.rollback()
        return 0
    finally:
        db.close()

if __name__ == "__main__":
    print("=" * 70)
    print("HOMEWORK FILE PATH MIGRATION")
    print("=" * 70)
    
    fixed = fix_file_paths()
    
    print(f"\n" + "=" * 70)
    if fixed > 0:
        print(f"✓ Migration complete - {fixed} records updated")
        print(f"\nNext steps:")
        print(f"1. git add -A")
        print(f"2. git commit -m 'Fix: Correct homework file paths - remove uploads/ prefix'")
        print(f"3. git push origin main")
    else:
        print("✓ No migration needed")
    print("=" * 70)
