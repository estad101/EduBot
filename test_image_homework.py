#!/usr/bin/env python3
"""
Test script to verify image homework upload flow.
"""
import requests
import json
import time
import os
from pathlib import Path

BASE_URL = "https://edubot-production-cf26.up.railway.app"
API_KEY = "your-api-key"  # Not needed for webhook testing

def create_test_image():
    """Create a simple test image file."""
    # Create a minimal valid JPEG
    jpeg_header = bytes([
        0xFF, 0xD8, 0xFF, 0xE0, 0x00, 0x10, 0x4A, 0x46, 0x49, 0x46, 0x00, 0x01
    ])
    return jpeg_header + b'\xFF\xD9'  # Minimal JPEG with just header and end marker


def test_image_homework_submission():
    """Test the image homework submission flow."""
    print("\n" + "="*60)
    print("🧪 Testing Image Homework Submission")
    print("="*60)
    
    # Simulate WhatsApp webhook with image submission
    webhook_payload = {
        "object": "whatsapp_business_account",
        "entry": [{
            "id": "123456789",
            "changes": [{
                "value": {
                    "messaging_product": "whatsapp",
                    "metadata": {
                        "display_phone_number": "2347001234567",
                        "phone_number_id": "797467203457022"
                    },
                    "contacts": [{
                        "profile": {
                            "name": "Test Student"
                        },
                        "wa_id": "2347001234567"
                    }],
                    "messages": [{
                        "from": "2347001234567",
                        "id": "wamid.test123",
                        "timestamp": str(int(time.time())),
                        "type": "image",
                        "image": {
                            "id": "test_image_id_123",
                            "mime_type": "image/jpeg"
                        }
                    }]
                },
                "field": "messages"
            }]
        }]
    }
    
    print("\n📤 Sending webhook payload with image message...")
    print(f"   From: {webhook_payload['entry'][0]['changes'][0]['value']['contacts'][0]['wa_id']}")
    print(f"   Type: image")
    
    # Send webhook
    response = requests.post(
        f"{BASE_URL}/api/whatsapp",
        json=webhook_payload,
        headers={"Content-Type": "application/json"}
    )
    
    print(f"\n📨 Response Status: {response.status_code}")
    try:
        response_data = response.json()
        print(f"   Response: {json.dumps(response_data, indent=2)}")
    except:
        print(f"   Response: {response.text}")
    
    return response


def check_uploads_directory():
    """Check what files are in the uploads directory."""
    print("\n" + "="*60)
    print("📁 Checking Uploads Directory")
    print("="*60)
    
    upload_dir = "uploads/homework"
    if not os.path.exists(upload_dir):
        print(f"❌ Directory does not exist: {upload_dir}")
        return
    
    print(f"\n📂 Directory: {upload_dir}")
    
    # Walk through directory
    for root, dirs, files in os.walk(upload_dir):
        level = root.replace(upload_dir, '').count(os.sep)
        indent = ' ' * 2 * level
        rel_path = os.path.relpath(root, upload_dir)
        print(f"{indent}📁 {rel_path}")
        
        sub_indent = ' ' * 2 * (level + 1)
        for file in files:
            file_path = os.path.join(root, file)
            file_size = os.path.getsize(file_path)
            print(f"{sub_indent}📄 {file} ({file_size} bytes)")


def test_image_status_endpoint():
    """Test the image status check endpoint."""
    print("\n" + "="*60)
    print("🔍 Testing Image Status Endpoint")
    print("="*60)
    
    # Try to check status of homework ID 1
    homework_id = 1
    print(f"\n🔗 Checking status for homework ID: {homework_id}")
    
    response = requests.get(
        f"{BASE_URL}/api/homework/{homework_id}/image-status",
        headers={"Content-Type": "application/json"}
    )
    
    print(f"📨 Response Status: {response.status_code}")
    try:
        response_data = response.json()
        print(f"   Response: {json.dumps(response_data, indent=2)}")
    except:
        print(f"   Response: {response.text}")
    
    return response


def test_text_homework_submission():
    """Test text homework submission via API endpoint."""
    print("\n" + "="*60)
    print("✏️ Testing Text Homework Submission (API)")
    print("="*60)
    
    request_payload = {
        "student_id": 1,
        "subject": "Mathematics",
        "submission_type": "TEXT",
        "content": "This is a test text homework submission to verify the API works correctly."
    }
    
    print(f"\n📤 Sending text homework submission...")
    print(f"   Student ID: {request_payload['student_id']}")
    print(f"   Subject: {request_payload['subject']}")
    print(f"   Type: {request_payload['submission_type']}")
    
    response = requests.post(
        f"{BASE_URL}/api/homework/submit",
        json=request_payload,
        headers={"Content-Type": "application/json"}
    )
    
    print(f"\n📨 Response Status: {response.status_code}")
    try:
        response_data = response.json()
        print(f"   Response: {json.dumps(response_data, indent=2)}")
    except:
        print(f"   Response: {response.text}")
    
    return response


if __name__ == "__main__":
    print("\n" + "="*60)
    print("🤖 Image Homework Upload Test Suite")
    print("="*60)
    
    # Check if server is running
    try:
        response = requests.get(f"{BASE_URL}/api/health", timeout=2)
        print(f"\n✓ Server is running (Health check: {response.status_code})")
    except requests.exceptions.ConnectionError:
        print(f"\n❌ Cannot connect to server at {BASE_URL}")
        print("   Make sure the bot is running: python main.py")
        exit(1)
    
    # Run tests
    print("\n1️⃣ Running Text Homework Submission Test...")
    test_text_homework_submission()
    
    print("\n2️⃣ Checking Uploads Directory...")
    check_uploads_directory()
    
    print("\n3️⃣ Testing Image Status Endpoint...")
    test_image_status_endpoint()
    
    print("\n" + "="*60)
    print("✅ Test Suite Complete")
    print("="*60)
