#!/usr/bin/env python3
"""
Create test images for database records that are missing actual files.
This allows us to verify the image serving works correctly.
"""
import os
import sys
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO

sys.path.insert(0, os.path.dirname(__file__))

from config.database import SessionLocal
from models.homework import Homework
from sqlalchemy import desc

def create_test_image(student_id, subject, filename):
    """Create a test image with student and subject info"""
    # Create a simple image
    width, height = 800, 600
    img = Image.new('RGB', (width, height), color='white')
    draw = ImageDraw.Draw(img)
    
    # Add text
    text_color = (0, 0, 0)
    draw.rectangle([0, 0, width, height], outline='blue', width=5)
    
    # Try to use a system font, fallback to default if not available
    try:
        title_font = ImageFont.truetype("arial.ttf", 60)
        text_font = ImageFont.truetype("arial.ttf", 40)
    except:
        title_font = ImageFont.load_default()
        text_font = ImageFont.load_default()
    
    # Draw text
    y_pos = 50
    draw.text((50, y_pos), "Homework Submission", fill=text_color, font=title_font)
    
    y_pos += 100
    draw.text((50, y_pos), "Student ID: {}".format(student_id), fill=text_color, font=text_font)
    
    y_pos += 80
    draw.text((50, y_pos), "Subject: {}".format(subject), fill=text_color, font=text_font)
    
    y_pos += 80
    draw.text((50, y_pos), "[TEST IMAGE - Auto-generated]", fill=(200, 0, 0), font=text_font)
    
    # Save to file
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    img.save(filename)
    print("Created test image: {}".format(filename))
    return filename

def sync_missing_images():
    """Create test images for database records"""
    session = SessionLocal()
    
    print("=" * 80)
    print("IMAGE SYNC TOOL - Create test images for database records")
    print("=" * 80)
    
    uploads_base = os.path.join(os.path.dirname(__file__), "uploads")
    
    # Get all IMAGE submissions
    homeworks = session.query(Homework).filter(
        Homework.submission_type == 'IMAGE'
    ).order_by(desc(Homework.created_at)).all()
    
    print("\nChecking {} IMAGE submissions...".format(len(homeworks)))
    
    missing_count = 0
    created_count = 0
    
    for hw in homeworks:
        if not hw.file_path:
            print("  [SKIP] ID {}: No file_path".format(hw.id))
            continue
        
        full_path = os.path.join(uploads_base, hw.file_path)
        
        if os.path.exists(full_path):
            print("  [OK] ID {}: {}".format(hw.id, hw.file_path))
        else:
            missing_count += 1
            print("  [MISSING] ID {}: {}".format(hw.id, hw.file_path))
            
            # Create test image
            try:
                create_test_image(
                    hw.student_id,
                    hw.subject,
                    full_path
                )
                created_count += 1
            except Exception as e:
                print("    ERROR creating image: {}".format(e))
    
    session.close()
    
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print("Total IMAGE submissions: {}".format(len(homeworks)))
    print("Missing files: {}".format(missing_count))
    print("Created: {}".format(created_count))
    print("\nNow verify by opening: https://nurturing-exploration-production.up.railway.app/homework")

if __name__ == "__main__":
    try:
        # Check if PIL is installed
        try:
            from PIL import Image, ImageDraw, ImageFont
        except ImportError:
            print("Installing Pillow for image generation...")
            import subprocess
            subprocess.check_call([sys.executable, "-m", "pip", "install", "Pillow", "-q"])
            from PIL import Image, ImageDraw, ImageFont
        
        sync_missing_images()
    except Exception as e:
        print("Error: {}".format(e))
        import traceback
        traceback.print_exc()
        sys.exit(1)
