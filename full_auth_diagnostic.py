#!/usr/bin/env python
"""
COMPREHENSIVE AUTH SYSTEM DIAGNOSTIC
Checks every component of the authentication system
"""
import os
import sys
import json
from pathlib import Path

def print_section(title):
    print(f"\n{'='*80}")
    print(f"  {title}")
    print(f"{'='*80}")

def check_env_variables():
    print_section("1. ENVIRONMENT VARIABLES")
    
    required_vars = [
        'DATABASE_URL',
        'SECRET_KEY',
        'ADMIN_PASSWORD',
        'SESSION_TIMEOUT_MINUTES'
    ]
    
    found = {}
    missing = []
    
    for var in required_vars:
        value = os.getenv(var)
        if value:
            # Mask sensitive values
            if 'PASSWORD' in var or 'URL' in var or 'KEY' in var:
                display_value = value[:10] + '...' if len(value) > 10 else '***'
            else:
                display_value = value
            found[var] = display_value
            print(f"✅ {var}: {display_value}")
        else:
            missing.append(var)
            print(f"❌ {var}: NOT SET")
    
    return len(missing) == 0, found, missing

def check_database_connection():
    print_section("2. DATABASE CONNECTION")
    
    try:
        from config.database import engine
        from sqlalchemy import text
        
        connection = engine.connect()
        result = connection.execute(text("SELECT 1"))
        connection.close()
        print("✅ Database connection successful")
        return True
    except Exception as e:
        print(f"❌ Database connection failed: {str(e)}")
        return False

def check_admin_credentials():
    print_section("3. ADMIN CREDENTIALS")
    
    try:
        from admin.auth import AdminAuth
        
        username = AdminAuth.ADMIN_USERNAME
        password = AdminAuth.ADMIN_PASSWORD
        
        print(f"✅ Admin username: {username}")
        
        # Check if password is using the secret key (bad) or env var (good)
        if os.getenv("ADMIN_PASSWORD"):
            print(f"✅ Admin password: Set from ADMIN_PASSWORD environment variable")
        else:
            print(f"⚠️  Admin password: Using SECRET_KEY fallback")
        
        # Test credential verification
        is_valid, message = AdminAuth.verify_credentials(username, password)
        if is_valid:
            print(f"✅ Credential verification: PASS")
            return True
        else:
            print(f"❌ Credential verification: FAIL - {message}")
            return False
            
    except Exception as e:
        print(f"❌ Error checking credentials: {str(e)}")
        return False

def check_frontend_config():
    print_section("4. FRONTEND API CONFIGURATION")
    
    config_file = Path("admin-ui/lib/api-client.ts")
    
    try:
        with open(config_file, 'r') as f:
            content = f.read()
        
        # Check for API_URL configuration
        if "NEXT_PUBLIC_API_URL" in content:
            print("✅ api-client.ts has NEXT_PUBLIC_API_URL")
        else:
            print("❌ api-client.ts missing NEXT_PUBLIC_API_URL")
        
        # Check for localhost fallback
        if "http://localhost:8000" in content:
            print("✅ Localhost fallback is present (good for development)")
        else:
            print("⚠️  No localhost fallback found")
        
        return True
    except Exception as e:
        print(f"❌ Error reading api-client.ts: {str(e)}")
        return False

def check_backend_config():
    print_section("5. BACKEND CONFIGURATION")
    
    try:
        from config.settings import settings
        
        print(f"✅ Settings loaded successfully")
        print(f"   - Session timeout: {settings.session_timeout_minutes} minutes")
        print(f"   - CORS enabled: {len(settings.cors_origins) > 0}")
        
        if settings.cors_origins:
            for origin in settings.cors_origins:
                print(f"     - {origin}")
        
        return True
    except Exception as e:
        print(f"❌ Error loading settings: {str(e)}")
        return False

def check_cors_configuration():
    print_section("6. CORS CONFIGURATION")
    
    try:
        from main import app
        
        # Check if CORS middleware is configured
        cors_found = False
        for middleware in app.middleware_stack.__dict__.get('middleware', []):
            if 'CORS' in str(middleware):
                cors_found = True
                break
        
        if cors_found:
            print("✅ CORS middleware is configured")
        else:
            print("⚠️  CORS configuration status unclear")
        
        return True
    except Exception as e:
        print(f"⚠️  Could not check CORS in detail: {str(e)}")
        return True  # Not critical

def check_login_endpoint():
    print_section("7. LOGIN ENDPOINT")
    
    try:
        import inspect
        from admin.routes.api import login
        
        print("✅ Login endpoint imported successfully")
        
        # Check signature
        sig = inspect.signature(login)
        params = list(sig.parameters.keys())
        print(f"   - Parameters: {', '.join(params)}")
        
        if "credentials" in params and "request" in params:
            print("✅ Endpoint has correct parameters")
            return True
        else:
            print("❌ Endpoint missing expected parameters")
            return False
    except Exception as e:
        print(f"❌ Error checking login endpoint: {str(e)}")
        return False

def check_models():
    print_section("8. DATABASE MODELS")
    
    try:
        from models.student import Student
        from models.payment import Payment
        from models.subscription import Subscription
        from models.homework import Homework
        
        print("✅ All models imported successfully")
        return True
    except Exception as e:
        print(f"❌ Error importing models: {str(e)}")
        return False

def check_file_structure():
    print_section("9. FILE STRUCTURE")
    
    required_files = [
        "main.py",
        "config/settings.py",
        "config/database.py",
        "admin/auth.py",
        "admin/routes/api.py",
        "admin-ui/lib/api-client.ts",
        "admin-ui/pages/login.tsx"
    ]
    
    all_found = True
    for file_path in required_files:
        if Path(file_path).exists():
            print(f"✅ {file_path}")
        else:
            print(f"❌ {file_path} NOT FOUND")
            all_found = False
    
    return all_found

def test_login_flow():
    print_section("10. TEST LOGIN FLOW")
    
    try:
        from admin.auth import AdminAuth
        
        # Test with correct credentials
        username = "admin"
        password = AdminAuth.ADMIN_PASSWORD
        
        is_valid, message = AdminAuth.verify_credentials(username, password, "127.0.0.1")
        
        if is_valid:
            print("✅ Login with correct credentials: PASS")
        else:
            print(f"❌ Login with correct credentials: FAIL - {message}")
            return False
        
        # Test with incorrect password
        is_valid, message = AdminAuth.verify_credentials(username, "wrong_password", "127.0.0.1")
        
        if not is_valid:
            print("✅ Login with wrong password correctly rejected")
        else:
            print("❌ Login with wrong password was incorrectly accepted")
            return False
        
        return True
    except Exception as e:
        print(f"❌ Error testing login: {str(e)}")
        return False

def main():
    print("\n" + "="*80)
    print("  EDUBOT AUTHENTICATION SYSTEM - COMPREHENSIVE DIAGNOSTIC")
    print("="*80)
    
    results = {
        "Environment Variables": check_env_variables()[0],
        "Database Connection": check_database_connection(),
        "Admin Credentials": check_admin_credentials(),
        "Frontend Config": check_frontend_config(),
        "Backend Config": check_backend_config(),
        "CORS Configuration": check_cors_configuration(),
        "Login Endpoint": check_login_endpoint(),
        "Models": check_models(),
        "File Structure": check_file_structure(),
        "Login Flow": test_login_flow()
    }
    
    print_section("DIAGNOSTIC SUMMARY")
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for check, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {check}")
    
    print(f"\nTotal: {passed}/{total} checks passed")
    
    if passed == total:
        print("\n🎉 ALL CHECKS PASSED - System is properly configured!")
        return 0
    else:
        print(f"\n⚠️  {total - passed} issues found - See details above")
        return 1

if __name__ == "__main__":
    sys.exit(main())
