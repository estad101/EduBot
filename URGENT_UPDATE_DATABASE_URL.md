# ⚠️ URGENT: Update DATABASE_URL on Railway

## Current Issue
Your Railway deployment is using **localhost DATABASE_URL** instead of the Railway MySQL database.

### Current (WRONG):
```
mysql+pymysql://chatbot_user:ChatbotSecure123!@localhost:3306/chatbot
```

### Should Be (CORRECT):
```
mysql+pymysql://root:ONWxGCHTjbvpVHPnRPQjWjpytDVjGTNH@yamanote.proxy.rlwy.net:27478/railway
```

---

## How to Fix (5 Steps)

### Step 1: Open Railway Dashboard
Go to: https://railway.app/dashboard

### Step 2: Select Your Project
- Click **marvelous-possibility** project
- Select **production** environment

### Step 3: Go to Variables
- You should be on the "nurturing-exploration" (frontend) service
- Look for the **Variables** tab
- **IMPORTANT**: Make sure you're on the Backend/API service, not the frontend!
  - Look for "edubot" or "Backend" service
  - Switch to that service

### Step 4: Update DATABASE_URL
1. Find the **DATABASE_URL** variable
2. Click to edit it
3. Replace the value with:
   ```
   mysql+pymysql://root:ONWxGCHTjbvpVHPnRPQjWjpytDVjGTNH@yamanote.proxy.rlwy.net:27478/railway
   ```
4. Click **Save** or **Update**

### Step 5: Redeploy
The service should automatically redeploy with the new DATABASE_URL.

**Watch the Deploy Logs** - you should see:
```
[Settings] ✓ Database URL configured: mysql+pymysql://...railway
✓ Database engine created successfully
=== APPLICATION READY ===
```

---

## Need Help?

Check the Services:
1. **nurturing-exploration** = Frontend (Next.js admin)
   - URL: https://nurturing-exploration-production.up.railway.app

2. **edubot-production-cf26** = Backend (FastAPI)
   - URL: https://edubot-production-cf26.up.railway.app
   - **Edit variables on THIS service**

---

## CLI Command (If Available)
Once the CLI supports variable setting, you can use:
```bash
railway variable set DATABASE_URL "mysql+pymysql://root:ONWxGCHTjbvpVHPnRPQjWjpytDVjGTNH@yamanote.proxy.rlwy.net:27478/railway"
```

But the web UI is the most reliable way right now.
