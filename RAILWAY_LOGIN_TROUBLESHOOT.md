# Railway Login Troubleshooting Guide

## Status

**Frontend URL:** https://nurturing-exploration-production.up.railway.app/login
**Backend URL:** https://edubot-production-cf26.up.railway.app
**Status:** LOGIN NOT WORKING

## Root Issues Found

1. **Missing Dependencies in Environment**
   - Python packages not installed on Railway backend
   - Pydantic-settings not available
   - Database driver not available

2. **Environment Variables Not Set on Railway**
   - DATABASE_URL not configured
   - SECRET_KEY not configured
   - ADMIN_PASSWORD not configured

3. **Frontend May Not Have Rebuild**
   - NEXT_PUBLIC_API_URL not set at build time
   - Frontend still trying to use localhost

## Step-by-Step Fix

### IMMEDIATE ACTION REQUIRED (On Railway Admin UI)

1. **Go to:** Admin UI Service → Variables
2. **Ensure these are set:**
   ```
   NEXT_PUBLIC_API_URL=https://edubot-production-cf26.up.railway.app
   ```

3. **Go to:** Backend Service → Variables
4. **Set these exactly:**
   ```
   DATABASE_URL=mysql+pymysql://root:ONWxGCHTjbvpVHPnRPQjWjpytDVjGTNH@yamanote.proxy.rlwy.net:27478/railway
   SECRET_KEY=your-secret-key-change-this
   ADMIN_PASSWORD=marriage2020!
   DEBUG=False
   ```

5. **After setting variables:**
   - Go to Backend Service → Deploy → "Trigger Deploy"
   - Wait for both services to rebuild
   - Watch logs for "Build successful"

### What's Needed

```
Frontend:
- NEXT_PUBLIC_API_URL env var
- Needs rebuild to take effect

Backend:
- DATABASE_URL env var
- SECRET_KEY env var
- ADMIN_PASSWORD env var
- All Python dependencies installed
```

### Test Sequence

```bash
# Step 1: Set variables on Railway
# Step 2: Trigger deployments
# Step 3: Wait for success messages
# Step 4: Hard refresh frontend (Ctrl+Shift+R)
# Step 5: Open DevTools console (F12)
# Step 6: Check console for: "[APIClient] Initialized with API_URL: https://..."
# Step 7: Try login with admin / marriage2020!
```

## Expected Console Output (F12)

### When Working:
```
[APIClient] Initialized with API_URL: https://edubot-production-cf26.up.railway.app
[APIClient] Attempting login for: admin
(Should see 200 OK response)
```

### When Broken:
```
[APIClient] Initialized with API_URL: http://localhost:8000
[APIClient] Login error: Failed to load resource: net::ERR_CONNECTION_REFUSED
```

## Critical Reminder

**Do NOT forget to rebuild BOTH services after setting variables!**

Frontend variables are baked in at build time. Simply setting the variable is not enough - you MUST trigger a rebuild.

---

**Your Task:**
1. Go to Railway Dashboard
2. Set the variables listed above
3. Trigger deployments
4. Test login after successful builds

That's it!
