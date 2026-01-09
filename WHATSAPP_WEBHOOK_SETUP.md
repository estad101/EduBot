# WHATSAPP WEBHOOK SETUP GUIDE

## Bot Information
- **Bot Phone Number:** +15551610271
- **Phone Number ID:** 797467203457022
- **Webhook URL:** https://edubot-production-0701.up.railway.app/api/webhook/whatsapp
- **Backend Status:** ✅ RUNNING AND RESPONDING

---

## Problem Identified

When you tried sending a message via API:
```bash
curl -i -X POST \
  https://graph.facebook.com/v22.0/797467203457022/messages \
  -H 'Authorization: Bearer <access token>' \
  ...
```

The bot didn't respond because the **webhook is not registered in Meta Business Dashboard**.

---

## Solution: Register Webhook (5 Steps)

### Step 1: Open Meta Business Dashboard
- Go to: https://business.facebook.com
- Log in with your Meta business account

### Step 2: Navigate to WhatsApp Settings
```
Your Business 
  → WhatsApp
    → API Setup (or Configuration)
```

### Step 3: Find Webhook Section
Look for **"Webhook URL"** or **"Edit Webhook"** button

### Step 4: Configure Webhook
Enter these values:

**Callback URL:**
```
https://edubot-production-0701.up.railway.app/api/webhook/whatsapp
```

**Verify Token:**
```
change-me-to-secure-token
```

Click **Verify and Save**

### Step 5: Configure Railway Variable
1. Go to: https://railway.app/dashboard
2. Click: **edubot-production-0701** (backend service)
3. Click: **Variables** tab
4. Add/Update variable:
   ```
   WHATSAPP_WEBHOOK_TOKEN = change-me-to-secure-token
   ```
5. Save and **Redeploy** the backend

---

## After Setup: How Messages Flow

### Receiving Messages (What You Want)
1. User sends WhatsApp message to **+15551610271**
2. Meta sends webhook to your bot
3. Bot processes the message
4. Bot sends response back to user

### Sending Messages (What You Tried)
- The curl command you used is for *sending* messages
- But the bot needs to *receive* messages first via webhook
- The webhook setup enables bidirectional communication

---

## Testing

### Test 1: Verify Webhook Configuration
```bash
# This will test if webhook is properly configured
curl "https://edubot-production-0701.up.railway.app/api/webhook/whatsapp?hub.mode=subscribe&hub.challenge=12345&hub.verify_token=change-me-to-secure-token"

# If successful, you'll get: 12345
# If failed (403), token doesn't match
```

### Test 2: Send a Real Message
1. Open WhatsApp on your phone
2. Send ANY message to bot number: **+15551610271**
3. Bot should respond within 1-2 seconds

### Test 3: Check Logs
Go to Railway Dashboard → **edubot-production-0701** → **Logs**
You should see:
```
✓ Webhook received: whatsapp_business_account
WhatsApp message from [your phone]: text
```

---

## Checklist

- [ ] Webhook URL configured in Meta Dashboard
- [ ] Verify Token set in Meta Dashboard
- [ ] WHATSAPP_WEBHOOK_TOKEN set in Railway
- [ ] Backend redeployed after variable change
- [ ] Webhook events subscribed (messages, status updates)
- [ ] Test webhook verification passes (returns 12345)
- [ ] Test by sending real WhatsApp message to +15551610271

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| "Callback URL failed validation" | Check URL is exactly: `https://edubot-production-0701.up.railway.app/api/webhook/whatsapp` |
| "Invalid verify token" | Token must match between Meta Dashboard and Railway WHATSAPP_WEBHOOK_TOKEN |
| "Webhook verification timeout" | Backend might not be running - check Railway Logs |
| "Messages not being received" | Webhook events might not be subscribed - check Meta Dashboard webhook fields |
| Bot doesn't respond | Check Railway Logs for errors - might be database or API key issue |

---

## Meta Dashboard Webhook Fields

Make sure these are enabled:
- [x] `messages` - For incoming messages
- [x] `message_template_status_update` - For template status
- [x] `message_template_quality_update` - For template quality
- [x] `account_update` - For account changes

---

## Next Actions

1. ✅ Backend is running and responding
2. ⏳ Configure webhook in Meta Business Dashboard
3. ⏳ Set WHATSAPP_WEBHOOK_TOKEN in Railway
4. ⏳ Redeploy backend
5. ⏳ Test by sending WhatsApp message to +15551610271

Once webhook is registered, messages will flow automatically!
