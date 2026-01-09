# ✅ Railway Variables Checklist

## 🎯 Service: edubot-production-0701 (Backend)

### Phase 1: CRITICAL - Set These First! 
**These MUST be set or backend will crash:**

- [ ] **DATABASE_URL** = `mysql+pymysql://root:ONWxGCHTjbvpVHPnRPQjWjpytDVjGTNH@yamanote.proxy.rlwy.net:27478/railway`
- [ ] **SECRET_KEY** = `your-long-random-key-32-chars-minimum`
- [ ] **ADMIN_PASSWORD** = `your_admin_password_here`

✅ Save and check logs for "APPLICATION READY"

---

### Phase 2: API Configuration 
**These control how the API runs:**

- [ ] **API_TITLE** = `EduBot API`
- [ ] **API_VERSION** = `1.0.0`
- [ ] **API_PORT** = `8000`
- [ ] **ENVIRONMENT** = `production`
- [ ] **DEBUG** = `False`
- [ ] **HTTPS_ONLY** = `True`

---

### Phase 3: Frontend Connection
**These let the frontend talk to the backend:**

- [ ] **NEXT_PUBLIC_API_URL** = `https://edubot-production-0701.up.railway.app`
- [ ] **NEXT_PUBLIC_APP_NAME** = `EduBot Admin`
- [ ] **ADMIN_ORIGIN** = `https://nurturing-exploration-production.up.railway.app`
- [ ] **ALLOW_ORIGINS** = `https://nurturing-exploration-production.up.railway.app,https://edubot-production-0701.up.railway.app,http://localhost:3000`

---

### Phase 4: Logging & Performance
**These control monitoring and limits:**

- [ ] **LOG_LEVEL** = `INFO`
- [ ] **LOG_FILE** = `logs/chatbot.log`
- [ ] **RATE_LIMIT_PER_MINUTE** = `60`
- [ ] **SESSION_TIMEOUT_MINUTES** = `60`
- [ ] **MAX_FILE_SIZE_MB** = `5`
- [ ] **ALGORITHM** = `HS256`

---

### Phase 5: WhatsApp (Optional)
**Only set if you have WhatsApp Business account:**

- [ ] **WHATSAPP_API_KEY** = `EAAckpQFzzTUBQT...` (your actual key)
- [ ] **WHATSAPP_PHONE_NUMBER_ID** = `797467203457022`
- [ ] **WHATSAPP_BUSINESS_ACCOUNT_ID** = `1516305056071819`
- [ ] **WHATSAPP_PHONE_NUMBER** = `+15551610271`
- [ ] **WHATSAPP_WEBHOOK_TOKEN** = `change-me-to-secure-token`

---

### Phase 6: Paystack (Optional)
**Only set if you have Paystack account:**

- [ ] **PAYSTACK_PUBLIC_KEY** = `pk_live_your_key`
- [ ] **PAYSTACK_SECRET_KEY** = `sk_live_your_key`
- [ ] **PAYSTACK_WEBHOOK_SECRET** = `your_webhook_secret`
- [ ] **PAYSTACK_WEBHOOK_URL** = `https://edubot-production-0701.up.railway.app/api/payments/webhook/paystack`

---

### Phase 7: Optional/Legacy
**Usually can leave these as-is:**

- [ ] **DATABASE_HOST** = `localhost` (not used with DATABASE_URL)
- [ ] **UPLOADS_DIR** = `uploads`
- [ ] **ALLOWED_IMAGE_TYPES** = `image/jpeg,image/png,image/webp`
- [ ] **SENTRY_DSN** = (leave blank)

---

## 🚦 Testing After Setup

### Test 1: Backend Health Check
```
URL: https://edubot-production-0701.up.railway.app/api/health
Expected: {"status": "ok"}
```

### Test 2: Frontend Login
```
URL: https://nurturing-exploration-production.up.railway.app
Expected: Login page loads, can login with ADMIN_PASSWORD
```

### Test 3: Dashboard Status
```
After login, check dashboard
Expected: 
  - "Database Connected" ✓
  - "WhatsApp Configured" ✓
```

---

## 💡 Tips

1. **Start with Phase 1** - Get backend running first
2. **Watch Deploy Logs** - Click Deployments tab to see progress
3. **Copy-Paste Carefully** - Values must be exact
4. **Test Between Phases** - Don't set everything at once
5. **Use Provided Values** - Don't guess on DATABASE_URL or SECRET_KEY

---

## 🆘 Troubleshooting

**Backend not starting?**
- Check Phase 1: DATABASE_URL, SECRET_KEY, ADMIN_PASSWORD
- Look for error in Deploy Logs

**Frontend showing disconnected?**
- Check Phase 3: NEXT_PUBLIC_API_URL must be set on BOTH services
- Frontend also needs its own NEXT_PUBLIC_API_URL variable

**Login not working?**
- Check ADMIN_PASSWORD is set
- Backend must have DATABASE_URL configured

**Status indicators gray?**
- Backend health endpoint must return {"status":"ok"}
- Check Network tab in browser DevTools
- Verify NEXT_PUBLIC_API_URL on frontend is correct

---

## 📞 Need Help?

1. Copy this checklist
2. Set the variables you need
3. Check Deploy Logs after each phase
4. Share any error messages

You're doing great! 🎉
