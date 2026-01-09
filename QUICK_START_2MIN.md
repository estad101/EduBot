# ⚡ 2-Minute Quick Start - Set Variables Now!

## 🎯 What to Do RIGHT NOW (Copy-Paste Friendly)

### Step 1: Open Railway Dashboard
Go to: https://railway.app/dashboard
- Select: **marvelous-possibility**
- Select environment: **production**
- Click service: **edubot-production-0701**
- Click tab: **Variables**

### Step 2: Add These 5 Variables (MINIMUM)

Click **+ New Variable** for each, or find the text input fields:

#### Variable 1:
```
Name: DATABASE_URL
Value: mysql+pymysql://root:ONWxGCHTjbvpVHPnRPQjWjpytDVjGTNH@yamanote.proxy.rlwy.net:27478/railway
```

#### Variable 2:
```
Name: SECRET_KEY
Value: edubot-secret-key-production-xyz-1234567890
```

#### Variable 3:
```
Name: ADMIN_PASSWORD
Value: [your admin password here]
```

#### Variable 4:
```
Name: ENVIRONMENT
Value: production
```

#### Variable 5:
```
Name: DEBUG
Value: False
```

#### Variable 6 (IMPORTANT - For file uploads):
```
Name: UPLOADS_DIR
Value: /app/uploads
```
⚠️ **This MUST match the Railway volume mount path exactly!**

### Step 3: Save
- Each variable should auto-save
- Watch for the service to redeploy
- Check **Deployments** tab for "APPLICATION READY" message

### Step 4: Test
```
Go to: https://edubot-production-0701.up.railway.app/api/health
Should see: {"status":"ok"}
```

---

## 🎉 That's It!

You now have a working backend!

**Next:** Update the frontend's NEXT_PUBLIC_API_URL to point to your new backend.

---

## 📚 Need More Variables?

See: `RAILWAY_VARIABLES_CHECKLIST.md` for all options
See: `RAILWAY_VARIABLES_SETUP_GUIDE.md` for detailed explanations

---

## 🆘 Issues?

**Backend won't start?**
- Check DATABASE_URL is exactly correct
- Check SECRET_KEY is set
- Watch Deploy Logs for error message

**Backend starts but health check fails?**
- Wait 30 more seconds
- Refresh the health check URL
- Check Network tab in browser

**Can't see logs?**
- Click **Deployments** tab
- Click most recent deployment
- Scroll to see full logs

---

**All set? Update the frontend now!** 🚀
