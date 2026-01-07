#!/usr/bin/env python3
"""
Login System Validation Script
Verifies all components needed for successful login functionality.
"""
import os
import sys
from pathlib import Path

def check_file_exists(path: str, description: str) -> bool:
    """Check if a file exists."""
    exists = Path(path).exists()
    status = "✅" if exists else "❌"
    print(f"{status} {description}: {path}")
    return exists

def check_env_var(var_name: str, description: str, required: bool = False) -> bool:
    """Check if environment variable is set."""
    value = os.getenv(var_name)
    exists = value is not None and value != ""
    status = "✅" if exists else ("❌" if required else "⚠️")
    print(f"{status} {description}: {var_name}" + (f" = {value[:30]}..." if exists and len(str(value)) > 30 else f" = {value}" if exists else ""))
    return exists

def main():
    print("=" * 70)
    print("LOGIN SYSTEM VALIDATION")
    print("=" * 70)
    
    all_good = True
    
    # Check backend files
    print("\n📁 Backend Files:")
    all_good &= check_file_exists("admin/auth.py", "Authentication module")
    all_good &= check_file_exists("admin/routes/api.py", "Admin API routes")
    all_good &= check_file_exists("main.py", "Main FastAPI application")
    all_good &= check_file_exists("config/settings.py", "Settings configuration")
    all_good &= check_file_exists("utils/security.py", "Security utilities")
    
    # Check frontend files
    print("\n📁 Frontend Files:")
    all_good &= check_file_exists("admin-ui/pages/login.tsx", "Login page")
    all_good &= check_file_exists("admin-ui/lib/api-client.ts", "API client")
    all_good &= check_file_exists("admin-ui/.env", "Frontend .env")
    all_good &= check_file_exists("admin-ui/.env.production", "Frontend .env.production")
    all_good &= check_file_exists("admin-ui/Dockerfile", "Frontend Dockerfile")
    all_good &= check_file_exists("admin-ui/railway.json", "Railway config")
    
    # Check backend environment
    print("\n🔐 Backend Environment Variables:")
    all_good &= check_env_var("DEBUG", "Debug mode (should be False in production)", required=False)
    all_good &= check_env_var("DATABASE_URL", "Database URL", required=True)
    all_good &= check_env_var("SECRET_KEY", "Secret key for JWT", required=True)
    all_good &= check_env_var("ADMIN_ORIGIN", "Admin origin for CORS", required=False)
    all_good &= check_env_var("SESSION_TIMEOUT_MINUTES", "Session timeout", required=False)
    
    # Check frontend environment
    print("\n🌐 Frontend Environment Variables:")
    all_good &= check_env_var("NEXT_PUBLIC_API_URL", "API URL for frontend", required=True)
    
    # Check optional services
    print("\n📱 Optional: WhatsApp Configuration:")
    all_good_wa = check_env_var("WHATSAPP_API_KEY", "WhatsApp API key", required=False)
    all_good_wa &= check_env_var("WHATSAPP_PHONE_NUMBER_ID", "WhatsApp Phone ID", required=False)
    
    print("\n💳 Optional: Paystack Configuration:")
    all_good_ps = check_env_var("PAYSTACK_PUBLIC_KEY", "Paystack Public Key", required=False)
    all_good_ps &= check_env_var("PAYSTACK_SECRET_KEY", "Paystack Secret Key", required=False)
    
    # Summary
    print("\n" + "=" * 70)
    if all_good:
        print("✅ All essential components are configured!")
        print("\nNext steps:")
        print("1. Verify DATABASE_URL points to a running MySQL server")
        print("2. Ensure admin credentials are set (default: admin/marriage2020!)")
        print("3. Start the backend: uvicorn main:app --reload")
        print("4. Start the frontend: npm run dev (in admin-ui/)")
        print("5. Visit http://localhost:3000/login")
        return 0
    else:
        print("❌ Some components are missing or misconfigured")
        print("\nRead LOGIN_FIXES.md for complete setup instructions")
        return 1

if __name__ == "__main__":
    sys.exit(main())
