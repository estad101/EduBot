# Railway Environment Variables - Ready to Copy

## How to Use This File

1. Go to your Railway project dashboard
2. Go to your **Backend Service** settings
3. Click on **Variables**
4. Copy each variable below and paste into Railway

---

## BACKEND SERVICE VARIABLES

### Database (Most Important)
```
DATABASE_URL=mysql+pymysql://chatbot_user:ChatbotSecure123!@your-railway-db-host:3306/chatbot
```
*Note: If using Railway MySQL, it provides MYSQL_URL. Just make sure DATABASE_URL is set.*

### API Configuration
```
DEBUG=False
API_TITLE=EduBot API
API_VERSION=1.0.0
API_PORT=8000
ENVIRONMENT=production
```

### Security (CRITICAL - Generate New!)
```
SECRET_KEY=generate-with-this-python-command:
```
Run in Python:
```python
import secrets
print(secrets.token_urlsafe(32))
```
Then paste the output as SECRET_KEY value.

```
ALGORITHM=HS256
ADMIN_ORIGIN=https://proactive-insight-production-6462.up.railway.app
ALLOW_ORIGINS=https://proactive-insight-production-6462.up.railway.app
HTTPS_ONLY=True
SESSION_TIMEOUT_MINUTES=60
RATE_LIMIT_PER_MINUTE=60
```

### WhatsApp Integration (Keep your existing values)
```
WHATSAPP_API_KEY=EAAckpQFzzTUBQT73SGpogTNXAGImnudPIqyXef1CdhXZCZCfzxyS7KV6IcAQVaZBaQ8UiPjZA0ZAf7LZCHwX40n0fBBDMskmmrNwIRdE7xggPwXBNLltUq7FIoWnQjHPrEWUlkP8dBrYieWq2qmcMFPn57Ib0q8dDPN8HysJMNRJIC9ptQ8EJdUKYfeCTjmAZDZD
WHATSAPP_PHONE_NUMBER_ID=797467203457022
WHATSAPP_BUSINESS_ACCOUNT_ID=1516305056071819
WHATSAPP_PHONE_NUMBER=+15551610271
WHATSAPP_WEBHOOK_TOKEN=iloveGOD2020!
```

### Paystack Integration (Keep your existing values)
```
PAYSTACK_PUBLIC_KEY=pk_live_your_key
PAYSTACK_SECRET_KEY=sk_live_your_key
PAYSTACK_WEBHOOK_SECRET=your_webhook_secret
PAYSTACK_WEBHOOK_URL=https://proactive-insight-production-6462.up.railway.app/api/payments/webhook/paystack
```

### File Upload
```
MAX_FILE_SIZE_MB=5
ALLOWED_IMAGE_TYPES=image/jpeg,image/png,image/webp
UPLOADS_DIR=uploads
```

### Logging & Monitoring
```
LOG_LEVEL=INFO
LOG_FILE=logs/chatbot.log
```

*Note: SENTRY_DSN is optional for error tracking*

---

## FRONTEND SERVICE VARIABLES (admin-ui)

### API Connection
```
NEXT_PUBLIC_API_URL=https://proactive-insight-production-6462.up.railway.app
NEXT_PUBLIC_APP_NAME=EduBot Admin
```

---

## Step-by-Step Setup in Railway

### 1. Backend Service Setup:
1. Click your **Backend Service**
2. Go to **Variables** tab
3. Add each variable from the BACKEND section above
4. For SECRET_KEY: Generate new value with Python command above
5. Update WHATSAPP and PAYSTACK values if different
6. Click **Deploy** or trigger redeploy

### 2. Frontend Service Setup:
1. Click your **Admin UI Service** (frontend)
2. Go to **Variables** tab
3. Add both variables from the FRONTEND section
4. Click **Deploy** or trigger redeploy

### 3. Verify Deployment:
- Check service logs appear without errors
- Backend should show: "Database initialized successfully"
- Frontend should show: "Build successful"

### 4. Test Login:
Visit: https://proactive-insight-production-6462.up.railway.app/login

---

## Variable Reference

| Variable | Where It's Used | Critical? |
|----------|-----------------|-----------|
| DATABASE_URL | Backend database connection | ✅ YES |
| SECRET_KEY | JWT token generation | ✅ YES |
| ADMIN_ORIGIN | CORS configuration | ✅ YES |
| HTTPS_ONLY | Security header | ⚠️ Important |
| NEXT_PUBLIC_API_URL | Frontend API calls | ✅ YES |
| WHATSAPP_* | WhatsApp messages | ⚠️ If using WhatsApp |
| PAYSTACK_* | Payment processing | ⚠️ If using Payments |

---

## Common Issues & Fixes

### Login shows "Cannot POST /api/admin/login"
- ❌ NEXT_PUBLIC_API_URL is wrong
- ✅ Set to: https://proactive-insight-production-6462.up.railway.app

### Database connection refused
- ❌ DATABASE_URL is incorrect
- ✅ Verify MySQL service is running on Railway
- ✅ Check credentials are correct

### "Invalid username or password"
- ❌ Admin credentials might be wrong
- ✅ Default: admin / marriage2020!
- ✅ Can override with ADMIN_PASSWORD variable

### Tokens not persisting
- ❌ Frontend can't store in localStorage
- ✅ Check browser privacy settings
- ✅ Make sure HTTPS is working

---

## Generate Required Values

### SECRET_KEY
```python
import secrets
print(secrets.token_urlsafe(32))
# Output example: 
# dJ_Dq7kZpQ_FH8mR2xL9vN4uY5bT3cWs6eJ1pK0aB9iM
```

### Custom ADMIN_PASSWORD (Optional)
Add this variable to set a custom admin password:
```
ADMIN_PASSWORD=your-secure-password-here
```

---

## Testing Variables Locally

Before deploying to Railway, test locally:

### Create .env file in root:
```
DATABASE_URL=mysql+pymysql://root:password@localhost:3306/chatbot
DEBUG=False
SECRET_KEY=your-generated-secret-key
ADMIN_ORIGIN=http://localhost:3000
ALLOW_ORIGINS=http://localhost:3000,http://localhost:8000
HTTPS_ONLY=False
```

### Create admin-ui/.env file:
```
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_APP_NAME=EduBot Admin
```

### Run locally:
```bash
# Backend
uvicorn main:app --reload

# Frontend (in admin-ui/)
npm run dev
```

Visit: http://localhost:3000/login

---

## Troubleshooting Checklist

- [ ] All DATABASE variables set correctly
- [ ] SECRET_KEY generated with secrets.token_urlsafe()
- [ ] ADMIN_ORIGIN matches frontend domain
- [ ] NEXT_PUBLIC_API_URL matches backend domain
- [ ] Both services redeployed after variables set
- [ ] No typos in variable names (case-sensitive!)
- [ ] HTTPS_ONLY=True in production
- [ ] SESSION_TIMEOUT_MINUTES≥30

---

## Safety Reminders

⚠️ **Never commit to GitHub:**
- SECRET_KEY values
- PAYSTACK_SECRET_KEY
- WHATSAPP_API_KEY
- Database passwords

✅ **Always use Railway Variables** for secrets

✅ **Rotate SECRET_KEY** if ever exposed

✅ **Use strong passwords** for admin accounts

---

**Last Updated:** 2024
**Status:** Ready for Production
