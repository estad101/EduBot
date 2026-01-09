# 🎯 Setting Environment Variables on Railway - Step by Step

## Access Railway Dashboard

1. Go to: **https://railway.app/dashboard**
2. Login with your Railway account
3. Select project: **marvelous-possibility**
4. Select environment: **production**

---

## 📍 For the NEW BACKEND SERVICE (edubot-production-0701)

### Step 1: Select the Backend Service
1. You should see multiple services in the project
2. Look for and click on: **edubot-production-0701** (or similar backend name)
3. You'll see tabs at the top: Deployments, Logs, Settings, Variables, etc.
4. Click the **Variables** tab

### Step 2: Add Variables One by One

You'll see an interface to add variables. For each variable:
1. Click **+ New Variable** (or similar button)
2. Enter the **Name** (left side)
3. Enter the **Value** (right side)
4. Click **Save** or **Add** after each one

---

## 📝 REQUIRED Variables (Set These First!)

### 1. DATABASE_URL
```
Name:  DATABASE_URL
Value: mysql+pymysql://root:ONWxGCHTjbvpVHPnRPQjWjpytDVjGTNH@yamanote.proxy.rlwy.net:27478/railway
```
⚠️ **This is CRITICAL - without it, backend will crash!**

### 2. SECRET_KEY
```
Name:  SECRET_KEY
Value: edubot-production-secret-key-xyz-12345678901234567890
```
(Use any long random string, 32+ characters)

### 3. ADMIN_PASSWORD
```
Name:  ADMIN_PASSWORD
Value: your_admin_password_here
```
(This is what you use to login to the admin panel)

---

## 🔧 API Configuration Variables

### 4. API_TITLE
```
Name:  API_TITLE
Value: EduBot API
```

### 5. API_VERSION
```
Name:  API_VERSION
Value: 1.0.0
```

### 6. API_PORT
```
Name:  API_PORT
Value: 8000
```

### 7. ENVIRONMENT
```
Name:  ENVIRONMENT
Value: production
```

### 8. DEBUG
```
Name:  DEBUG
Value: False
```

### 9. HTTPS_ONLY
```
Name:  HTTPS_ONLY
Value: True
```

---

## 🌐 Frontend Integration

### 10. NEXT_PUBLIC_API_URL
```
Name:  NEXT_PUBLIC_API_URL
Value: https://edubot-production-0701.up.railway.app
```
(This tells frontend where to find the backend)

### 11. NEXT_PUBLIC_APP_NAME
```
Name:  NEXT_PUBLIC_APP_NAME
Value: EduBot Admin
```

---

## 📊 Logging & Performance

### 12. LOG_LEVEL
```
Name:  LOG_LEVEL
Value: INFO
```

### 13. LOG_FILE
```
Name:  LOG_FILE
Value: logs/chatbot.log
```

### 14. RATE_LIMIT_PER_MINUTE
```
Name:  RATE_LIMIT_PER_MINUTE
Value: 60
```

### 15. SESSION_TIMEOUT_MINUTES
```
Name:  SESSION_TIMEOUT_MINUTES
Value: 60
```

### 16. MAX_FILE_SIZE_MB
```
Name:  MAX_FILE_SIZE_MB
Value: 5
```

---

## 🤝 CORS & Origins

### 17. ADMIN_ORIGIN
```
Name:  ADMIN_ORIGIN
Value: https://nurturing-exploration-production.up.railway.app
```

### 18. ALLOW_ORIGINS
```
Name:  ALLOW_ORIGINS
Value: https://nurturing-exploration-production.up.railway.app,https://edubot-production-0701.up.railway.app,http://localhost:3000
```

### 19. ALGORITHM
```
Name:  ALGORITHM
Value: HS256
```

---

## 📱 WhatsApp Integration (Optional)

### 20. WHATSAPP_API_KEY
```
Name:  WHATSAPP_API_KEY
Value: EAAckpQFzzTUBQT73SGpogTNXAGImnudPIqyXef1CdhXZCZCfzxyS7KV6IcAQVaZBaQ8UiPjZA0ZAf7LZCHwX40n0fBBDMskmmrNwIRdE7xggPwXBNLltUq7FIoWnQjHPrEWUlkP8dBrYieWq2qmcMFPn57Ib0q8dDPN8HysJMNRJIC9ptQ8EJdUKYfeCTjmAZDZD
```

### 21. WHATSAPP_PHONE_NUMBER_ID
```
Name:  WHATSAPP_PHONE_NUMBER_ID
Value: 797467203457022
```

### 22. WHATSAPP_BUSINESS_ACCOUNT_ID
```
Name:  WHATSAPP_BUSINESS_ACCOUNT_ID
Value: 1516305056071819
```

### 23. WHATSAPP_PHONE_NUMBER
```
Name:  WHATSAPP_PHONE_NUMBER
Value: +15551610271
```

### 24. WHATSAPP_WEBHOOK_TOKEN
```
Name:  WHATSAPP_WEBHOOK_TOKEN
Value: change-me-to-secure-token
```

---

## 💳 Paystack Integration (Optional)

### 25. PAYSTACK_PUBLIC_KEY
```
Name:  PAYSTACK_PUBLIC_KEY
Value: pk_live_your_actual_key
```

### 26. PAYSTACK_SECRET_KEY
```
Name:  PAYSTACK_SECRET_KEY
Value: sk_live_your_actual_key
```

### 27. PAYSTACK_WEBHOOK_SECRET
```
Name:  PAYSTACK_WEBHOOK_SECRET
Value: your_webhook_secret
```

### 28. PAYSTACK_WEBHOOK_URL
```
Name:  PAYSTACK_WEBHOOK_URL
Value: https://edubot-production-0701.up.railway.app/api/payments/webhook/paystack
```

---

## 🔍 Optional/Advanced

### 29. SENTRY_DSN (Skip if you don't use Sentry)
```
Name:  SENTRY_DSN
Value: [leave blank or set if you have Sentry account]
```

### 30. UPLOADS_DIR
```
Name:  UPLOADS_DIR
Value: uploads
```

### 31. DATABASE_HOST (Legacy - usually ignored)
```
Name:  DATABASE_HOST
Value: localhost
```

### 32. ALLOWED_IMAGE_TYPES
```
Name:  ALLOWED_IMAGE_TYPES
Value: image/jpeg,image/png,image/webp
```

---

## ✅ After Setting Variables

1. **Save Each Variable** - Most variables auto-save when you click outside the field
2. **Wait for Redeployment** - Railway should automatically redeploy the service
3. **Check Deployment Logs** - Click the **Deployments** tab and watch the logs
4. **Look for** - "APPLICATION READY" message in logs (means it started successfully)

---

## 🚦 What You Should See in Logs

```
[Settings] ✓ Database URL configured: mysql+pymysql://...railway
[Settings] ✓ Using DATABASE_URL from explicit environment variable
✓ Database engine created successfully
Database initialization started in background
Settings initialization started in background
=== APPLICATION READY ===
```

---

## ⚠️ Common Mistakes

❌ **Don't:**
- Include quotes around values (Railway handles that)
- Copy values with extra spaces
- Use localhost for DATABASE_URL on Railway

✅ **Do:**
- Copy the exact values provided
- Add all REQUIRED variables first
- Then add the others
- Save after each variable or group

---

## 🆘 If Redeployment Fails

1. Check the **Deployments** tab for error logs
2. Most common error: DATABASE_URL pointing to wrong place
3. Verify DATABASE_URL matches exactly:
   ```
   mysql+pymysql://root:ONWxGCHTjbvpVHPnRPQjWjpytDVjGTNH@yamanote.proxy.rlwy.net:27478/railway
   ```
4. If still failing, check Secret_KEY and ADMIN_PASSWORD are set

---

## 📋 Quick Minimum Setup

If you just want to get it working quickly, set ONLY these:

1. **DATABASE_URL** = mysql+pymysql://root:ONWxGCHTjbvpVHPnRPQjWjpytDVjGTNH@yamanote.proxy.rlwy.net:27478/railway
2. **SECRET_KEY** = any-long-random-string-32-chars-minimum
3. **ADMIN_PASSWORD** = your-password
4. **NEXT_PUBLIC_API_URL** = https://edubot-production-0701.up.railway.app
5. **ENVIRONMENT** = production
6. **DEBUG** = False

That's the bare minimum. After that works, you can add the others.

---

## Need Help?

If you get stuck:
1. Share the error from Deploy Logs
2. Tell me which variable is failing
3. I can help debug the exact issue

You got this! 🚀
