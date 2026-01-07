# Railway Deployment - 100% Compatible Setup

## ✅ What's Fixed

This version is optimized for Railway deployment:

1. ✅ **No $PORT variable issues** - Using hardcoded port 8000
2. ✅ **Removed problematic config files** - railway.json deleted
3. ✅ **Clean Dockerfile** - Railway auto-detects and uses it
4. ✅ **Environment variables** - Reads from Railway service variables
5. ✅ **Database auto-connection** - Uses MYSQL_URL from Railway MySQL service

---

## 🚀 Complete Deployment Steps

### Step 1: Verify Code is Pushed

```bash
git log --oneline -1
```

Should show the latest commit.

### Step 2: Go to Railway Dashboard

https://railway.app → Your EduBot Project

### Step 3: Add MySQL Service (if not already added)

1. Click "Add Service"
2. Select "MySQL"
3. Click "Deploy"

### Step 4: Configure Backend Service Variables

Click **EduBot Backend Service** → **Variables** tab

Add these variables:

```
DATABASE_URL = ${{ MYSQL_URL }}
API_TITLE = EduBot API
API_VERSION = 1.0.0
API_PORT = 8000
ENVIRONMENT = production
DEBUG = False
HTTPS_ONLY = True
SECRET_KEY = [Generate: python -c "import secrets; print(secrets.token_urlsafe(32))"]
ALGORITHM = HS256
SESSION_TIMEOUT_MINUTES = 60
ADMIN_ORIGIN = https://youradmindomain.com
ALLOW_ORIGINS = https://youradmindomain.com,https://edubot-production-cf26.up.railway.app
NEXT_PUBLIC_API_URL = https://edubot-production-cf26.up.railway.app
NEXT_PUBLIC_APP_NAME = EduBot
WHATSAPP_API_KEY = [Your WhatsApp API key]
WHATSAPP_PHONE_NUMBER_ID = 797467203457022
WHATSAPP_BUSINESS_ACCOUNT_ID = 1516305056071819
WHATSAPP_PHONE_NUMBER = +15551610271
WHATSAPP_WEBHOOK_TOKEN = [Generate: python -c "import secrets; print(secrets.token_hex(16))"]
PAYSTACK_PUBLIC_KEY = pk_live_your_key
PAYSTACK_SECRET_KEY = sk_live_your_key
PAYSTACK_WEBHOOK_SECRET = your_webhook_secret
PAYSTACK_WEBHOOK_URL = https://edubot-production-cf26.up.railway.app/api/payments/webhook/paystack
MAX_FILE_SIZE_MB = 5
ALLOWED_IMAGE_TYPES = image/jpeg,image/png,image/webp
UPLOADS_DIR = uploads
LOG_LEVEL = WARNING
LOG_FILE = logs/chatbot.log
RATE_LIMIT_PER_MINUTE = 60
```

### Step 5: Redeploy Backend

1. Go to **EduBot Backend Service** → **Deployments**
2. Click three dots (⋯) on latest deployment
3. Select **"Rebuild"**
4. Wait for deployment (should take 3-5 minutes)

Watch the logs. You should see:
```
✓ Building image from Dockerfile
✓ Successfully built
✓ Starting container
✓ uvicorn main:app --host 0.0.0.0 --port 8000
✓ Application startup complete
```

### Step 6: Run Database Migrations

```bash
# Install Railway CLI (one time)
npm i -g @railway/cli

# Login
railway login

# Link your project
railway link

# Run migrations
railway run alembic upgrade head
```

### Step 7: Test Your API

```bash
# Health check
curl https://edubot-production-cf26.up.railway.app/api/health

# Should return:
# {"status": "healthy"}
```

Visit API docs:
```
https://edubot-production-cf26.up.railway.app/docs
```

---

## 🔍 Troubleshooting

### "Application failed to respond"

1. Check Backend Logs
   - Go to EduBot service → Logs
   - Look for ERROR messages
   - Share the error

2. Check Deployment Status
   - Go to Deployments tab
   - Latest deployment should be ✅ green

3. Check Database Connection
   - MySQL service should be ✅ running
   - DATABASE_URL should be set

### "Connection refused to MySQL"

```
Error: Can't connect to MySQL server
```

Solutions:
1. Wait 2-3 minutes for MySQL to initialize
2. Check MySQL service is running (green status)
3. Verify DATABASE_URL is set to `${{ MYSQL_URL }}`
4. Restart both services

### "ModuleNotFoundError"

```
ModuleNotFoundError: No module named 'xxx'
```

Solution:
1. Check requirements.txt has all dependencies
2. Go to Deployments → Rebuild
3. Clear Docker cache if needed

---

## ✅ Deployment Checklist

- [ ] Code pushed to GitHub
- [ ] MySQL service running (green)
- [ ] DATABASE_URL = ${{ MYSQL_URL }} set
- [ ] All environment variables added
- [ ] Backend service redeployed
- [ ] Logs show "Application startup complete"
- [ ] Health check returns 200
- [ ] Database migrations run
- [ ] API docs load at /docs

---

## 🎯 Your Live URLs

- **API**: https://edubot-production-cf26.up.railway.app
- **API Docs**: https://edubot-production-cf26.up.railway.app/docs
- **ReDoc**: https://edubot-production-cf26.up.railway.app/redoc
- **Health**: https://edubot-production-cf26.up.railway.app/api/health

---

## 📊 Architecture

```
GitHub (your code)
    ↓
Railway (auto-deploys on push)
    ├─ Backend Service (FastAPI/Python)
    │   └─ Uses Dockerfile
    └─ MySQL Service
        └─ Provides MYSQL_URL automatically
```

---

## 🚀 What Happens on Each Push

1. You push code to GitHub
2. Railway detects new commit
3. Railway builds Docker image from Dockerfile
4. Railway starts new container
5. Your app goes live (zero downtime)

---

**Status**: Ready for 100% Railway deployment! 🎉
