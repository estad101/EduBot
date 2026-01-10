#!/usr/bin/env python
"""
Quick test to verify templates endpoint works end-to-end.
"""
import requests
import json
import time
import subprocess
import os
import signal

def test_templates_endpoint():
    """Test the templates endpoint."""
    url = "http://127.0.0.1:8000/api/bot-messages/templates/list"
    
    try:
        print(f"Testing templates endpoint: {url}")
        response = requests.get(url, timeout=5)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Response Status: {data.get('status')}")
            print(f"Message: {data.get('message')}")
            
            templates = data.get('data', {}).get('templates', [])
            print(f"Templates Count: {len(templates)}")
            
            if templates:
                first = templates[0]
                print(f"\nFirst Template:")
                print(f"  ID: {first.get('id')}")
                print(f"  Name: {first.get('template_name')}")
                print(f"  Variables: {first.get('variables')}")
                print(f"  Is Default: {first.get('is_default')}")
                print("\n✓ Templates endpoint working correctly!")
                return True
            else:
                print("\n✗ No templates returned!")
                return False
        else:
            print(f"✗ Error: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("✗ Could not connect to server. Make sure backend is running on http://127.0.0.1:8000")
        return False
    except Exception as e:
        print(f"✗ Error: {e}")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("TEMPLATES ENDPOINT TEST")
    print("=" * 60)
    
    # Check if server is running
    import socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_running = sock.connect_ex(('127.0.0.1', 8000)) == 0
    sock.close()
    
    if not server_running:
        print("\n! Backend server is not running on http://127.0.0.1:8000")
        print("  Start it with: python -m uvicorn main:app --host 127.0.0.1 --port 8000")
        print("\n  Once running, this test should show templates from the database.\n")
        exit(1)
    
    # Run test
    success = test_templates_endpoint()
    
    print("\n" + "=" * 60)
    if success:
        print("✓ All tests passed!")
    else:
        print("✗ Tests failed!")
    print("=" * 60)
    
    exit(0 if success else 1)
