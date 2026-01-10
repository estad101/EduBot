#!/usr/bin/env python3
"""
Diagnose login issue - check what admin password is configured
"""

import os
import sys
sys.path.insert(0, '/xampp/htdocs/bot')

from config.settings import settings
from admin.auth import AdminAuth

print("=" * 70)
print("  ADMIN LOGIN DIAGNOSIS")
print("=" * 70)
print()

# Check environment variable
admin_password_env = os.getenv("ADMIN_PASSWORD")
print(f"1. ADMIN_PASSWORD environment variable: {admin_password_env}")
print()

# Check what AdminAuth is using
print(f"2. AdminAuth.ADMIN_PASSWORD being used: {AdminAuth.ADMIN_PASSWORD}")
print()

# Check SECRET_KEY
print(f"3. SECRET_KEY environment variable: {os.getenv('SECRET_KEY')}")
print(f"   Settings secret_key: {settings.secret_key}")
print()

# Try login
print("4. Testing login attempts:")
print()

# Test with admin/admin
result, message = AdminAuth.verify_credentials("admin", "admin", "127.0.0.1")
print(f"   admin/admin: {result} - {message}")

# Test with admin/password
result, message = AdminAuth.verify_credentials("admin", "password", "127.0.0.1")
print(f"   admin/password: {result} - {message}")

# Test with admin/<secret_key>
result, message = AdminAuth.verify_credentials("admin", settings.secret_key, "127.0.0.1")
print(f"   admin/{settings.secret_key[:20]}...: {result} - {message}")

print()
print("=" * 70)
print("  SOLUTION:")
print("=" * 70)
print()
print("To fix login, you need to:")
print()
print("Option 1: Set ADMIN_PASSWORD environment variable")
print("  export ADMIN_PASSWORD='your_password'")
print()
print("Option 2: Use the current SECRET_KEY as password:")
print(f"  Username: admin")
print(f"  Password: {settings.secret_key}")
print()
print("Option 3: Update code to use a hardcoded default password")
print()
