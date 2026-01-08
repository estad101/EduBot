#!/usr/bin/env python3
"""Check homework submissions in the database."""

from config.database import SessionLocal
from models.homework import Homework
import os

db = SessionLocal()
homeworks = db.query(Homework).all()

print(f'Total homeworks: {len(homeworks)}')
print()

image_count = 0
text_count = 0
missing_files = 0

for hw in homeworks:
    submission_type = str(hw.submission_type).upper() if hw.submission_type else "UNKNOWN"
    print(f'ID: {hw.id}')
    print(f'  Student: {hw.student_id}')
    print(f'  Subject: {hw.subject}')
    print(f'  Type: {submission_type}')
    print(f'  File Path: {hw.file_path}')
    
    if submission_type == "IMAGE":
        image_count += 1
        # Check if file exists
        if hw.file_path:
            railway_path = f"/app/uploads/{hw.file_path}"
            local_path = f"uploads/{hw.file_path}"
            
            if os.path.exists(railway_path):
                file_size = os.path.getsize(railway_path)
                print(f'  ✓ File exists on Railway: {file_size} bytes')
            elif os.path.exists(local_path):
                file_size = os.path.getsize(local_path)
                print(f'  ✓ File exists locally: {file_size} bytes')
            else:
                print(f'  ✗ FILE MISSING')
                missing_files += 1
    else:
        text_count += 1
    
    content_preview = hw.content[:60] if hw.content else "(empty)"
    print(f'  Content: {content_preview}...' if len(hw.content or "") > 60 else f'  Content: {content_preview}')
    print()

print()
print("=" * 50)
print(f"Summary:")
print(f"  Total: {len(homeworks)}")
print(f"  IMAGE submissions: {image_count}")
print(f"  TEXT submissions: {text_count}")
print(f"  Missing files: {missing_files}")
print("=" * 50)
