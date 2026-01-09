# BOT NOT RECEIVING MESSAGES - DIAGNOSTIC & FIX

## ⚠️ Root Cause: Webhook Not Registered in Meta Dashboard

**Just having Railway variables set is NOT enough!**

You must manually register the webhook URL in Meta Business Dashboard for messages to flow to your bot.

---

## 🔧 Fix: Register Webhook in Meta Dashboard (5 minutes)

### Step 1: Go to Meta Business Dashboard
```
URL: https://business.facebook.com/
```
- Log in with your Meta account

### Step 2: Navigate to App Settings
```
1. Click: Settings (bottom left)
2. Click: Apps and Websites
3. Select your App (EduBot or similar)
```

### Step 3: Configure Webhook
```
1. Left sidebar: Click "Webhooks"
2. Click: "Webhook" under "Products"
3. Click: "Add Subscription"
```

### Step 4: Set Webhook URL and Token
```
Callback URL: https://edubot-production-0701.up.railway.app/api/webhook/whatsapp

Verify Token: iloveGOD2020!

Click: Save
```

### Step 5: Subscribe to Events
After saving, subscribe to these webhook fields:
```
✓ messages
✓ message_template_status_update  
✓ message_template_quality_update
```

**Click each checkbox, then "Subscribe"**

### Step 6: Verify Success
You should see a **GREEN CHECKMARK** next to the webhook URL
- Green = ✅ Webhook is registered and active
- Gray = ⚠️ Not yet registered or not responding

---

## 🧪 Test the Webhook Registration

### Test 1: Check if Webhook is Responding (Do This First)
```
Open browser and visit:
https://edubot-production-0701.up.railway.app/api/webhook/whatsapp?hub.mode=subscribe&hub.challenge=TEST_CHALLENGE&hub.verify_token=iloveGOD2020!

Expected: You see "TEST_CHALLENGE" on page

If you see "TEST_CHALLENGE":
✅ Webhook endpoint is working

If you see error or nothing:
❌ Check Railway backend logs
```

### Test 2: Send Test Message from WhatsApp
```
1. Open WhatsApp
2. Send message to: +15551610271
3. Expected: Bot responds within 1-2 seconds

If message doesn't deliver:
- Webhook not registered (see Step 1-6 above)
- Phone number not verified with Meta

If message sends but no response:
- Check Backend Logs (Railway Deployments tab)
- Look for errors starting with "Webhook received:"
```

---

## 📋 Complete Checklist: Why Bot Doesn't Respond

### Backend Setup (✓ You're Done)
- [x] DATABASE_URL set in Railway
- [x] WHATSAPP_API_KEY set in Railway
- [x] WHATSAPP_PHONE_NUMBER_ID set in Railway (797467203457022)
- [x] WHATSAPP_BUSINESS_ACCOUNT_ID set in Railway
- [x] WHATSAPP_WEBHOOK_TOKEN set in Railway (iloveGOD2020!)
- [x] Code deployed to Railway

### Meta Dashboard Setup (⚠️ LIKELY MISSING)
- [ ] Webhook URL registered in Meta Dashboard
- [ ] Verify token set to iloveGOD2020!
- [ ] Webhook fields subscribed (messages, message_template_*)
- [ ] Green checkmark appears next to webhook

### Phone Number Setup (⚠️ VERIFY)
- [ ] Phone number +15551610271 verified with Meta
- [ ] Phone number claimed in business account
- [ ] Phone number linked to app

---

## 🚨 Message Flow (With Webhook Registration)

```
User sends message to +15551610271 on WhatsApp
    ↓
Meta receives message
    ↓
Meta sends POST to: https://edubot-production-0701.up.railway.app/api/webhook/whatsapp
    ↓
Webhook URL must be REGISTERED in Meta Dashboard OR Meta won't send!
    ↓
Backend receives webhook from Meta
    ↓
Verifies token: iloveGOD2020!
    ↓
Looks up user state in database
    ↓
Generates response (3-tier fallback)
    ↓
Uses WHATSAPP_API_KEY to send message back
    ↓
User receives response! ✓
```

**If webhook not registered in Step 3 → Message never reaches your bot!**

---

## 🔍 Debug: Check What's Happening

### Check Railway Backend Logs
```
1. Go to: https://railway.app
2. Click: edubot-production-0701
3. Click: Logs
4. Send a message to bot
5. Look for entries starting with:
   - "Webhook received:"
   - "Message from:"
   - "Sending message to:"
```

**If you see "Webhook received:" → Webhook IS registered ✅**

**If you DON'T see it → Webhook NOT registered ⚠️**

### Check Meta Webhook Logs
```
1. Go to: Meta Business Dashboard
2. Webhooks → Select your webhook
3. Click: "Logs"
4. Send message to bot
5. Look for entries
```

**If you see Failed delivery attempts → Check error message (usually "webhook URL not registered")**

---

## 🆘 Common Issues & Solutions

| Issue | Cause | Solution |
|-------|-------|----------|
| Green check missing from webhook | Webhook not registered in Meta | Complete Step 1-6 above |
| Bot receives message but doesn't respond | Variables not set in Railway | Check Phase 1-5 in RAILWAY_VARIABLES_CHECKLIST.md |
| Error: "Invalid token" | Verify token doesn't match | Must be: `iloveGOD2020!` (exact match) |
| Error: "URL not reachable" | Railway backend down | Check Railway dashboard, redeploy if needed |
| Message stuck on "Sending..." | API key wrong or account suspended | Check WHATSAPP_API_KEY in Railway is complete |
| "Operation not allowed" | Phone number not verified with Meta | Verify number in Meta Business Dashboard |

---

## ✅ After You Register Webhook

### Expected Behavior
```
Time: 0s   - You send message to +15551610271
Time: 0.1s - Meta receives and validates message
Time: 0.2s - Meta POST to https://edubot-production-0701.up.railway.app/api/webhook/whatsapp
Time: 0.3s - Backend receives webhook, checks token (✓ iloveGOD2020!)
Time: 0.5s - Database lookup for user state
Time: 0.7s - Generate response based on conversation state
Time: 0.8s - Send response back via WhatsApp API
Time: 1.0s - You see response! ✅
```

---

## 📞 Quick Fix Summary

**BEFORE:** Variables set, but webhook not in Meta Dashboard
```
Message → Meta → ❌ STOPS HERE (not registered)
```

**AFTER:** Webhook registered in Meta Dashboard
```
Message → Meta → ✅ Sends to your bot → Bot responds ✓
```

**Action Required:** Go to Meta Business Dashboard and register webhook URL:
```
https://edubot-production-0701.up.railway.app/api/webhook/whatsapp

Token: iloveGOD2020!
```

This is the ONLY missing step preventing your bot from receiving messages.

