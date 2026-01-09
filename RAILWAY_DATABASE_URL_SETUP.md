# Railway DATABASE_URL Configuration Guide

## Issue
The backend deployment hangs because the Railway MySQL service URL (MYSQL_URL) may not be automatically passed to the Python backend.

## Solution

### Option 1: Manual Environment Variable Setup (Recommended for Quick Fix)

1. **Go to Railway Dashboard**
   - https://railway.app/dashboard
   - Select your project

2. **Configure Backend Service Environment Variables**
   - Click on the **Backend** service (the Python API)
   - Click the **Variables** tab
   - Add the following variable:
     ```
     DATABASE_URL=mysql+pymysql://root:ONWxGCHTjbvpVHPnRPQjWjpytDVjGTNH@yamanote.proxy.rlwy.net:27478/railway
     ```
   - Save the changes
   - The service will automatically redeploy

3. **Verify Deployment**
   - Watch the Deploy Logs
   - Should see: `[Settings] Database URL configured: mysql+pymysql://...railway`
   - Should see: `✓ Database engine created successfully`
   - Should see: `=== APPLICATION READY ===`
   - If you see these messages, deployment succeeded!

### Option 2: Link MySQL Plugin (Automatic)

If the MySQL database is a separate service on Railway:

1. **Go to Backend Service**
   - Click on the Backend service
   - Go to the **Plugins** or **Variables** tab

2. **Link to MySQL Service**
   - Look for "MySQL" or database service
   - Click "Link" or "Add"
   - This should automatically set DATABASE_URL from the MySQL plugin

### Option 3: Check MySQL Service Connection

1. **Verify MySQL Service Exists**
   - In Railway project, check all services
   - Should see a MySQL database service
   - Click it and get its connection URL

2. **Check Service Logs**
   - Open MySQL service logs
   - Verify it's running and accessible

## What Database URL Should Be

The DATABASE_URL format must be:
```
mysql+pymysql://USERNAME:PASSWORD@HOST:PORT/DATABASE
```

From your Railway MySQL service:
- **Driver**: mysql+pymysql (required by SQLAlchemy)
- **Username**: root
- **Password**: ONWxGCHTjbvpVHPnRPQjWjpytDVjGTNH
- **Host**: yamanote.proxy.rlwy.net
- **Port**: 27478
- **Database**: railway

## Testing (What You'll See in Logs)

**Successful startup logs should contain:**
```
[Settings] Database URL configured: mysql+pymysql://...railway
2026-01-09 07:49:37,915 - chatbot.main - INFO - Starting WhatsApp Chatbot API
2026-01-09 07:49:37,915 - chatbot.main - INFO - Environment: production
2026-01-09 07:49:37,915 - chatbot.main - INFO - Database URL: mysql+pymysql://...railway
[✓] Database engine created successfully
Database initialization started in background
Settings initialization started in background
=== APPLICATION READY ===
```

**If something fails, you might see:**
```
✗ Failed to create database engine: [error message]
```

## Next Steps

1. **Add DATABASE_URL environment variable** to backend service on Railway
2. **Trigger a redeploy** (save variables, or commit & push)
3. **Check Deploy Logs** - should show the messages above
4. **Test Frontend** - https://nurturing-exploration-production.up.railway.app
5. **Test Backend** - https://edubot-production-cf26.up.railway.app/api/health

## If Still Having Issues

1. Check that the MySQL credentials are correct
2. Verify the host/port are accessible from Railway containers
3. Make sure the "railway" database exists in MySQL
4. Check if there's a firewall blocking the connection
5. Review full Deploy Logs for specific error messages
