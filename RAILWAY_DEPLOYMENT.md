# Railway Deployment Guide for EduBot

This guide will walk you through deploying EduBot to Railway.

## Prerequisites

- GitHub account with EduBot repository
- Railway account (https://railway.app)
- All environment variables ready

## Step 1: Create Railway Account

1. Go to https://railway.app
2. Sign up with GitHub (recommended)
3. Authorize Railway to access your GitHub

## Step 2: Create a New Project

1. Click "Create a New Project"
2. Select "Deploy from GitHub repo"
3. Authorize Railway to access your GitHub
4. Select the `estad101/EduBot` repository
5. Click "Deploy"

Railway will automatically detect and deploy your app!

## Step 3: Add Services

Railway will need these services:

### 1. Backend API (Python/FastAPI)

This will be auto-detected from your Dockerfile.

- **Port**: 8000
- **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`

### 2. MySQL Database

1. In your Railway project, click "Add Service"
2. Select "MySQL"
3. Accept default configuration
4. Railway will automatically provide `DATABASE_URL`

### 3. Frontend (Next.js) - Optional

If you want to deploy the admin UI:

1. In your Railway project, click "Add Service"
2. Select "Node.js"
3. Configure:
   - **Working Directory**: `admin-ui`
   - **Start Command**: `npm run build && npm start`
   - **Port**: 3000

## Step 4: Configure Environment Variables

In your Railway project dashboard:

1. Go to "Variables" tab
2. Add these environment variables:

### Backend Variables

```env
# Database (auto-provided by Railway MySQL service)
DATABASE_URL=mysql+pymysql://user:password@host:3306/railway

# WhatsApp API
WHATSAPP_API_KEY=your_whatsapp_api_key
WHATSAPP_PHONE_NUMBER=your_phone_number

# Paystack (Payments)
PAYSTACK_PUBLIC_KEY=your_paystack_public_key
PAYSTACK_SECRET_KEY=your_paystack_secret_key

# JWT Security
SECRET_KEY=generate-a-strong-random-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Environment
ENVIRONMENT=production
DEBUG=False

# API Settings
API_HOST=0.0.0.0
API_PORT=8000
```

### Frontend Variables (if deploying Next.js)

In `admin-ui` service:

```env
NEXT_PUBLIC_API_BASE_URL=https://your-railway-backend-url
NEXT_PUBLIC_API_TIMEOUT=30000
```

## Step 5: Generate Strong Secret Key

Run this in Python to generate a strong SECRET_KEY:

```python
import secrets
print(secrets.token_urlsafe(32))
```

Copy the output and paste into `SECRET_KEY` variable in Railway.

## Step 6: Database Setup

After deployment:

1. Get your Railway MySQL connection details
2. Connect to MySQL and run migrations:

```bash
# SSH into your Railway backend or run via Railway terminal
alembic upgrade head
```

Or use Railway CLI:

```bash
# Install Railway CLI
npm i -g @railway/cli

# Login
railway login

# Connect to your project
railway link

# Run migrations in Railway environment
railway run alembic upgrade head
```

## Step 7: Set Up Domain (Optional)

To use your domain (e.g., api.yourdomain.com):

1. In Railway project settings, find "Domains"
2. Click "Add Domain"
3. Enter your domain
4. Follow DNS setup instructions
5. Update `WHATSAPP_WEBHOOK_URL` with your domain

## Step 8: Verify Deployment

Your deployed API will be available at:

```
https://your-railway-project-url.railway.app
```

Test it:

```bash
curl https://your-railway-project-url.railway.app/api/health
```

Expected response:
```json
{"status": "healthy"}
```

## Continuous Deployment

Once configured, Railway will automatically:

1. Detect pushes to your GitHub `main` branch
2. Build a Docker image
3. Run tests (if configured)
4. Deploy the new version
5. Keep your app running

No manual deployments needed!

## Monitoring & Logs

In Railway dashboard:

1. **Logs**: Click your service → "Logs" tab
2. **Metrics**: View CPU, RAM, requests
3. **Incidents**: Check service health
4. **Deployments**: See deployment history

## Troubleshooting

### Port Issues
If port is not binding correctly, Railway automatically assigns `$PORT` variable. Make sure your Procfile uses it:
```
web: uvicorn main:app --host 0.0.0.0 --port $PORT
```

### Database Connection Failed
1. Check `DATABASE_URL` is set correctly
2. Verify MySQL service is running
3. Ensure firewall allows connections
4. Check credentials in environment variables

### Build Failures
1. Check build logs in Railway dashboard
2. Ensure `requirements.txt` has all dependencies
3. Verify Python version compatibility
4. Check Dockerfile syntax

### Frontend Not Loading
If deploying Next.js admin UI:
1. Ensure `NEXT_PUBLIC_API_BASE_URL` points to backend
2. Check CORS settings in FastAPI backend
3. Verify both services are running

## Cost Estimation

Railway Free Tier:
- **Includes**: $5/month free credit
- **Backend API**: ~$2-3/month
- **MySQL Database**: ~$1-2/month
- **Frontend**: ~$0.50/month
- **Total**: Usually within free tier!

## Getting Help

- **Railway Docs**: https://docs.railway.app
- **GitHub Issues**: https://github.com/estad101/EduBot/issues
- **Email**: estadenterprise@gmail.com

---

**Deployment Status**: Ready to deploy! 🚀
