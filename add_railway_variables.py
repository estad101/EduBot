#!/usr/bin/env python3
"""
Railway Variables Setup Script
Adds all required environment variables to your Railway backend service
"""

import subprocess
import json

# Variables to add to backend service
VARIABLES = {
    # Database (from MySQL service)
    "DATABASE_URL": "${{ MYSQL_URL }}",  # This references the MySQL service
    
    # API Configuration
    "API_TITLE": "EduBot API",
    "API_VERSION": "1.0.0",
    "API_PORT": "8000",
    
    # Environment
    "ENVIRONMENT": "production",
    "DEBUG": "False",
    "HTTPS_ONLY": "True",
    
    # Security
    "SECRET_KEY": "change-me-to-a-secure-key",
    "ALGORITHM": "HS256",
    "SESSION_TIMEOUT_MINUTES": "60",
    
    # WhatsApp
    "WHATSAPP_API_KEY": "EAAckpQFzzTUBQT73SGpogTNXAGImnudPIqyXef1CdhXZCZCfzxyS7KV6IcAQVaZBaQ8UiPjZA0ZAf7LZCHwX40n0fBBDMskmmrNwIRdE7xggPwXBNLltUq7FIoWnQjHPrEWUlkP8dBrYieWq2qmcMFPn57Ib0q8dDPN8HysJMNRJIC9ptQ8EJdUKYfeCTjmAZDZD",
    "WHATSAPP_PHONE_NUMBER_ID": "797467203457022",
    "WHATSAPP_BUSINESS_ACCOUNT_ID": "1516305056071819",
    "WHATSAPP_PHONE_NUMBER": "+15551610271",
    "WHATSAPP_WEBHOOK_TOKEN": "change-me-to-secure-token",
    
    # Paystack
    "PAYSTACK_PUBLIC_KEY": "pk_live_your_key",
    "PAYSTACK_SECRET_KEY": "sk_live_your_key",
    "PAYSTACK_WEBHOOK_SECRET": "your_webhook_secret",
    "PAYSTACK_WEBHOOK_URL": "https://edubot-production-cf26.up.railway.app/api/payments/webhook/paystack",
    
    # CORS & Frontend
    "ADMIN_ORIGIN": "https://youradmindomain.com",
    "ALLOW_ORIGINS": "https://youradmindomain.com,https://edubot-production-cf26.up.railway.app",
    "NEXT_PUBLIC_API_URL": "https://edubot-production-cf26.up.railway.app",
    "NEXT_PUBLIC_APP_NAME": "EduBot",
    
    # File Upload
    "MAX_FILE_SIZE_MB": "5",
    "ALLOWED_IMAGE_TYPES": "image/jpeg,image/png,image/webp",
    "UPLOADS_DIR": "uploads",
    
    # Logging & Monitoring
    "LOG_LEVEL": "WARNING",
    "LOG_FILE": "logs/chatbot.log",
    "RATE_LIMIT_PER_MINUTE": "60",
}


def check_railway_cli():
    """Check if Railway CLI is installed"""
    try:
        result = subprocess.run(["railway", "--version"], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✓ Railway CLI found")
            return True
    except FileNotFoundError:
        pass
    
    print("\n❌ Railway CLI not found!")
    print("\nInstall it with:")
    print("  npm i -g @railway/cli")
    return False


def check_railway_login():
    """Check if user is logged into Railway"""
    try:
        result = subprocess.run(["railway", "whoami"], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✓ Logged in: {result.stdout.strip()}")
            return True
    except Exception as e:
        print(f"Not logged in: {e}")
    return False


def set_variable(key: str, value: str) -> bool:
    """Set a single variable"""
    try:
        result = subprocess.run(
            ["railway", "variables", "set", key, value],
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            print(f"  ✓ {key}")
            return True
        else:
            print(f"  ✗ {key}: {result.stderr.strip()}")
            return False
    except Exception as e:
        print(f"  ✗ {key}: {e}")
        return False


def main():
    print("=" * 60)
    print("Railway Variables Setup")
    print("=" * 60)
    
    # Check Railway CLI
    if not check_railway_cli():
        print("\nPlease install Railway CLI first:")
        print("  npm i -g @railway/cli")
        return
    
    # Check login
    print("\nChecking Railway login...")
    if not check_railway_login():
        print("\nPlease log in to Railway:")
        print("  railway login")
        return
    
    # Check linked project
    print("\nChecking linked project...")
    try:
        result = subprocess.run(["railway", "status"], capture_output=True, text=True)
        if "not linked" in result.stderr.lower() or result.returncode != 0:
            print("\n⚠️  Not linked to a Railway project!")
            print("Link with: railway link")
            return
        print("✓ Linked to Railway project")
    except Exception as e:
        print(f"Error: {e}")
        return
    
    # Add variables
    print("\n" + "=" * 60)
    print("Adding Variables to Backend Service")
    print("=" * 60 + "\n")
    
    success = 0
    failed = 0
    
    for key, value in VARIABLES.items():
        if set_variable(key, value):
            success += 1
        else:
            failed += 1
    
    # Summary
    print("\n" + "=" * 60)
    print(f"Results: {success} added, {failed} failed")
    print("=" * 60)
    
    if failed == 0:
        print("\n✅ All variables added successfully!")
        print("\nNext steps:")
        print("1. Check Railway dashboard to verify variables")
        print("2. Backend service will auto-redeploy")
        print("3. Wait for deployment to complete")
        print("4. Test the API: curl https://edubot-production-cf26.up.railway.app/api/health")
    else:
        print(f"\n⚠️  {failed} variables failed. Check errors above.")
        print("\nYou can also add them manually:")
        print("1. Go to Railway dashboard")
        print("2. Click backend service → Variables")
        print("3. Add each variable manually")


if __name__ == "__main__":
    main()
