#!/usr/bin/env python
"""
Test actual login from the FastAPI server's perspective.
This script emulates what the frontend does.
"""
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(__file__))

# Load environment first
from dotenv import load_dotenv
load_dotenv()

print("="*80)
print("  LOADING ENVIRONMENT FROM .env")
print("="*80)

env_vars = ['DATABASE_URL', 'SECRET_KEY', 'ADMIN_PASSWORD', 'DEBUG']
for var in env_vars:
    value = os.getenv(var)
    if value:
        if 'PASSWORD' in var or 'URL' in var or 'KEY' in var:
            display = value[:15] + '...'
        else:
            display = value
        print(f"✅ {var}: {display}")
    else:
        print(f"❌ {var}: NOT SET")

print("\n" + "="*80)
print("  IMPORTING MODULES")
print("="*80)

try:
    from config.settings import settings
    print("✅ Imported settings")
    print(f"   DATABASE_URL: {settings.database_url[:30]}...")
    print(f"   SECRET_KEY: {settings.secret_key[:15]}...")
except Exception as e:
    print(f"❌ Failed to import settings: {e}")
    sys.exit(1)

try:
    from admin.auth import AdminAuth
    print("✅ Imported AdminAuth")
except Exception as e:
    print(f"❌ Failed to import AdminAuth: {e}")
    sys.exit(1)

print("\n" + "="*80)
print("  TESTING ADMIN CREDENTIALS")
print("="*80)

username = AdminAuth.ADMIN_USERNAME
password = AdminAuth.ADMIN_PASSWORD

print(f"Testing credentials: {username} / {password}")

is_valid, message = AdminAuth.verify_credentials(username, password, "127.0.0.1")

if is_valid:
    print(f"✅ LOGIN TEST: PASSED")
    print(f"   Credentials are correct and can authenticate")
else:
    print(f"❌ LOGIN TEST: FAILED")
    print(f"   Error: {message}")
    sys.exit(1)

print("\n" + "="*80)
print("  TESTING DATABASE CONNECTION")
print("="*80)

try:
    from config.database import engine
    from sqlalchemy import text
    
    connection = engine.connect()
    result = connection.execute(text("SELECT 1"))
    connection.close()
    
    print("✅ DATABASE: Connected successfully")
except Exception as e:
    print(f"❌ DATABASE: Connection failed")
    print(f"   Error: {e}")
    sys.exit(1)

print("\n" + "="*80)
print("  ALL CHECKS PASSED - SYSTEM READY")
print("="*80)
print("\nTo start the backend server, run:")
print("  python main.py")
print("\nThen test login at:")
print("  POST http://localhost:8000/api/admin/login")
print("  Body: {\"username\": \"admin\", \"password\": \"" + password + "\"}")
