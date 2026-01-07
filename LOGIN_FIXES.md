# Railway Login Fix & Deployment Guide

## Summary of Fixes Applied

This guide documents all the fixes applied to make the login system work 100% on Railway.

## 1. Frontend Configuration Fixes

### ✅ Fixed Files:
- **admin-ui/.env** - Created with dev API URL
- **admin-ui/.env.production** - Created with Railway API URL  
- **admin-ui/Dockerfile** - Updated to pass API_URL at build time
- **admin-ui/railway.json** - Updated to pass build args
- **admin-ui/next.config.js** - Enhanced to use publicRuntimeConfig
- **admin-ui/lib/api-client.ts** - Improved error handling and logging
- **admin-ui/pages/login.tsx** - Fixed state management and error handling

### Environment Variables for Frontend:

**Development (.env):**
```
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_APP_NAME=EduBot Admin
```

**Production (.env.production & Railway):**
```
NEXT_PUBLIC_API_URL=https://proactive-insight-production-6462.up.railway.app
NEXT_PUBLIC_APP_NAME=EduBot Admin
```

## 2. Docker & Build Configuration

### What Changed:
- Added `ARG NEXT_PUBLIC_API_URL` to builder and production stages
- Ensured environment variable is available at build time (required for Next.js)
- Updated railway.json to pass buildArgs

### Why This Matters:
Next.js variables with `NEXT_PUBLIC_` prefix are baked into the static bundle at build time. They cannot be changed at runtime without a rebuild.

## 3. API Client Improvements

### Changes in admin-ui/lib/api-client.ts:
1. Added better logging (console.log for API_URL)
2. Improved error handling in login method
3. Added timeout increase (10s → 15s)
4. Better cleanup on 401 response
5. Handles network errors gracefully

### Changes in admin-ui/pages/login.tsx:
1. Fixed setAuthError call (was passing `error` instead of `errorMsg`)
2. Added small delay before navigation (ensures state is set)
3. Better error message handling

## 4. Backend CORS Configuration

Already configured in main.py:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:8000",
        "https://proactive-insight-production-6462.up.railway.app",  # ✅ Added
        os.getenv("ADMIN_ORIGIN", ""),
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization", "X-CSRF-Token"],
)
```

## 5. Required Railway Environment Variables

Add these to your Railway project:

### Backend Service:
```
# Database
DATABASE_URL=mysql+pymysql://user:password@host:port/database
# or let Railway set MYSQL_URL and settings.py will convert it

# API Configuration
DEBUG=False
API_TITLE=EduBot API
API_VERSION=1.0.0
API_PORT=8000
ENVIRONMENT=production

# Security
SECRET_KEY=your-super-secret-key-generate-with-secrets.token_urlsafe(32)
ALGORITHM=HS256
ADMIN_ORIGIN=https://proactive-insight-production-6462.up.railway.app
ALLOW_ORIGINS=https://proactive-insight-production-6462.up.railway.app
HTTPS_ONLY=True
SESSION_TIMEOUT_MINUTES=60
RATE_LIMIT_PER_MINUTE=60

# WhatsApp Integration
WHATSAPP_API_KEY=your_actual_whatsapp_api_key
WHATSAPP_PHONE_NUMBER_ID=your_phone_id
WHATSAPP_BUSINESS_ACCOUNT_ID=your_account_id
WHATSAPP_PHONE_NUMBER=your_whatsapp_number
WHATSAPP_WEBHOOK_TOKEN=your_webhook_token

# Paystack Integration
PAYSTACK_PUBLIC_KEY=pk_live_your_key
PAYSTACK_SECRET_KEY=sk_live_your_key
PAYSTACK_WEBHOOK_SECRET=your_secret

# Logging
LOG_LEVEL=INFO
```

### Frontend Service (admin-ui):
```
NEXT_PUBLIC_API_URL=https://proactive-insight-production-6462.up.railway.app
NEXT_PUBLIC_APP_NAME=EduBot Admin
```

## 6. Deployment Steps

### 1. Update Environment Variables in Railway Dashboard:
- Go to your Railway project
- For each service, set the environment variables from section 5 above
- Backend service should have all the backend variables
- Frontend service should have the frontend variables

### 2. Redeploy Both Services:
```bash
# Or trigger via Railway dashboard
git push  # This triggers auto-deploy on Railway
```

### 3. Verify Login Works:
1. Navigate to: https://proactive-insight-production-6462.up.railway.app/login
2. Enter credentials:
   - Username: admin
   - Password: marriage2020! (or from ADMIN_PASSWORD env var)
3. Click Login
4. Should redirect to /dashboard

### 4. Monitor Logs:
Check both frontend and backend logs in Railway dashboard:
- Backend logs: Should show "Admin login successful"
- Frontend logs: Should show "API_URL configured as: https://..."

## 7. Testing the Login Locally

If you want to test locally:

```bash
# Terminal 1: Backend
cd c:\xampp\htdocs\bot
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Terminal 2: Frontend
cd c:\xampp\htdocs\bot\admin-ui
npm install
npm run dev  # Starts on http://localhost:3000
```

Then visit http://localhost:3000/login

## 8. Troubleshooting

### Login shows "Login failed. Please try again."
- Check backend logs for error messages
- Verify DATABASE_URL is correct
- Check admin credentials in AdminAuth.verify_credentials()

### Network Error / Cannot reach API
- Verify NEXT_PUBLIC_API_URL in frontend environment
- Check CORS headers in main.py
- Verify backend service is running
- Check firewall/network policies

### Session expires immediately
- Check SESSION_TIMEOUT_MINUTES (should be 60)
- Verify time sync on Railway servers
- Check JWT/session token generation

### Token not being stored
- Check browser localStorage (F12 → Application → LocalStorage)
- Verify login response includes "token" field
- Check api-client.ts localStorage.setItem calls

## 9. Default Credentials

- **Username:** admin
- **Password:** marriage2020! (or override with ADMIN_PASSWORD env var)

These are read from AdminAuth class in admin/auth.py

## 10. Key Files Modified

1. ✅ admin-ui/.env - New
2. ✅ admin-ui/.env.production - New
3. ✅ admin-ui/Dockerfile - Updated for build args
4. ✅ admin-ui/railway.json - Updated for build args
5. ✅ admin-ui/next.config.js - Enhanced config
6. ✅ admin-ui/lib/api-client.ts - Better error handling
7. ✅ admin-ui/pages/login.tsx - Fixed state management

## 11. Login Flow Summary

```
User enters credentials
         ↓
POST /api/admin/login (with username/password)
         ↓
Backend: AdminAuth.verify_credentials()
         ↓
If valid:
  - Generate session_id
  - Generate token
  - Generate CSRF token
  - Return: {status: "success", token, session_id, csrf_token}
         ↓
Frontend: Store token in localStorage
         ↓
Frontend: Set authenticated = true
         ↓
Frontend: Redirect to /dashboard
```

## Testing Checklist

- [ ] Backend service is running and healthy
- [ ] Frontend service is running and healthy  
- [ ] NEXT_PUBLIC_API_URL is set correctly
- [ ] DATABASE_URL is accessible
- [ ] CORS allows frontend origin
- [ ] Admin credentials are configured
- [ ] Login page loads without errors
- [ ] Can submit login form
- [ ] API returns success response
- [ ] Token is stored in localStorage
- [ ] Redirects to dashboard
- [ ] Dashboard loads data from API

## Success Indicators

When login is working:
1. ✅ Login page loads at /login
2. ✅ Can enter username and password
3. ✅ Click Login → redirects to /dashboard
4. ✅ Dashboard shows data
5. ✅ localStorage has "admin_token" key
6. ✅ Network tab shows successful POST to /api/admin/login
7. ✅ Backend logs show "Admin login successful"
