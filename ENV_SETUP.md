# EduBot Environment Configuration Guide

## Overview
The EduBot project requires environment variables to be configured for proper operation. Two configuration files have been created:

- **`.env`** - Local development configuration (copy this and update with your values)
- **`.env.example`** - Template showing all available options with descriptions
- **`.env.production`** - Production configuration (to be updated before deployment)

## Quick Start

### 1. Database Configuration
```env
DATABASE_URL=mysql+mysqlconnector://payroll_user:password@localhost:3306/whatsapp_chatbot
```
Update with your MySQL credentials and database name.

### 2. Paystack Integration (Payments)
```env
PAYSTACK_PUBLIC_KEY=pk_test_your_public_key_here
PAYSTACK_SECRET_KEY=sk_test_your_secret_key_here
PAYSTACK_WEBHOOK_SECRET=your_webhook_secret_here
```
Get these from: https://dashboard.paystack.com/settings/api-keys-and-webhooks

### 3. WhatsApp Cloud API
```env
WHATSAPP_API_KEY=your_whatsapp_api_key_here
WHATSAPP_PHONE_NUMBER_ID=your_phone_number_id_here
WHATSAPP_BUSINESS_ACCOUNT_ID=your_business_account_id_here
WHATSAPP_PHONE_NUMBER=+1234567890
WHATSAPP_WEBHOOK_TOKEN=your_webhook_verification_token_here
```
Get these from: https://www.meta.com/developers/

### 4. Security
```env
SECRET_KEY=your-super-secret-key-change-this-in-production
ALGORITHM=HS256
HTTPS_ONLY=False  # Set to True in production
```

### 5. Admin UI Configuration
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_APP_NAME=EduBot
```

## Environment Variables Reference

| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| `DATABASE_URL` | MySQL connection string | ✓ | None |
| `DEBUG` | Enable debug mode | | `True` |
| `API_PORT` | FastAPI server port | | `8000` |
| `PAYSTACK_PUBLIC_KEY` | Paystack public key | ✓ | None |
| `PAYSTACK_SECRET_KEY` | Paystack secret key | ✓ | None |
| `WHATSAPP_API_KEY` | WhatsApp Cloud API key | ✓ | None |
| `WHATSAPP_PHONE_NUMBER_ID` | WhatsApp phone number ID | ✓ | None |
| `SECRET_KEY` | JWT secret key | ✓ | None |
| `ADMIN_ORIGIN` | Admin UI origin URL | | `http://localhost:3000` |
| `HTTPS_ONLY` | Enforce HTTPS cookies | | `False` |
| `LOG_LEVEL` | Logging level (DEBUG, INFO, WARNING, ERROR) | | `INFO` |
| `NEXT_PUBLIC_API_URL` | API URL for Next.js frontend | | `http://localhost:8000` |

## Running the Application

### Development
```bash
# Backend
python main.py

# Frontend (in admin-ui directory)
npm run dev
```

### Production
1. Copy `.env.example` to `.env.production`
2. Update all values with production credentials
3. Set `DEBUG=False` and `HTTPS_ONLY=True`
4. Deploy with Gunicorn:
```bash
gunicorn main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

## Security Notes

⚠️ **IMPORTANT:**
- Never commit `.env` file to version control (it's in `.gitignore`)
- Keep `SECRET_KEY` secret and change it in production
- Use strong, random values for all API keys
- Set `HTTPS_ONLY=True` in production
- Use environment variables from CI/CD pipeline, not .env files in production

## Getting API Keys

### Paystack
1. Go to https://dashboard.paystack.com
2. Navigate to Settings > API Keys and Webhooks
3. Copy your Public and Secret keys from there

### WhatsApp Cloud API
1. Go to https://www.meta.com/developers/
2. Create a Meta Business Account
3. Create a WhatsApp Business App
4. Get your API key, Phone Number ID, and Business Account ID

### Database
Ensure MySQL is running and create database:
```sql
CREATE DATABASE whatsapp_chatbot;
CREATE USER 'payroll_user'@'localhost' IDENTIFIED BY 'password';
GRANT ALL PRIVILEGES ON whatsapp_chatbot.* TO 'payroll_user'@'localhost';
FLUSH PRIVILEGES;
```

## Configuration Files Status

✅ `.env` - Created with defaults
✅ `.env.example` - Created as template
✅ `.env.production` - Exists, update before deploying
✅ `.gitignore` - Configured to exclude .env files

## Next Steps

1. **Update `.env`** with your actual API keys and database credentials
2. **Test database connection**: `python -c "from config.database import init_db; init_db()"`
3. **Start backend**: `python main.py`
4. **Start frontend**: `cd admin-ui && npm run dev`
5. **Access admin UI**: http://localhost:3000

For production deployment, follow the same process with `.env.production` and update all settings to use production endpoints.
