# WhatsApp Message Delivery Troubleshooting Guide

## Quick Checklist

### 1. **Check Environment Variables** ✅
```bash
# Required variables in Railway:
- WHATSAPP_API_KEY: Your Meta/Facebook API token
- WHATSAPP_PHONE_NUMBER_ID: Your WhatsApp Business Phone Number ID
- WHATSAPP_WEBHOOK_TOKEN: Custom token for webhook verification
```

### 2. **Check Webhook URL Configuration**
In your Meta Business Manager:
- Go to WhatsApp > Configuration
- Webhook URL should be: `https://your-railway-domain.com/api/webhook/whatsapp`
- Verify Token should match `WHATSAPP_WEBHOOK_TOKEN`

### 3. **Common Issues & Solutions**

#### Issue: "Webhook verified but messages not delivering"
**Cause:** Webhook URL is correct but message sending fails
**Solution:**
1. Check application logs for errors
2. Verify `WHATSAPP_API_KEY` is valid (hasn't expired)
3. Verify `WHATSAPP_PHONE_NUMBER_ID` is correct
4. Check if phone number format is correct (include country code, e.g., +2349012345678)

#### Issue: "Webhook not responding to verification"
**Cause:** Verify token mismatch or URL not accessible
**Solution:**
1. Confirm `WHATSAPP_WEBHOOK_TOKEN` matches Meta settings
2. Test webhook publicly: `https://your-domain.com/api/webhook/whatsapp?hub.mode=subscribe&hub.challenge=test123&hub.verify_token=YOUR_TOKEN`
3. Ensure Railway app is running and accessible

#### Issue: "Message queued but not delivered"
**Cause:** Invalid phone number format or recipient not opted in
**Solution:**
1. Check phone number format: Must include country code
2. Ensure phone number is registered with WhatsApp
3. Send test message from WhatsApp Business app first
4. Check Business account is in good standing

#### Issue: "Interactive buttons not showing"
**Cause:** WhatsApp API limit or button configuration issue
**Solution:**
1. Maximum 3 buttons per message (we handle this)
2. Button text max 20 characters (we handle this)
3. Button ID max 256 characters
4. Ensure phone number is in test/production mode

### 4. **View Logs in Railway**
```bash
# In Railway dashboard:
1. Go to Deployments
2. Click on active deployment
3. View Logs tab
4. Search for "WhatsApp" or "send_interactive_message"
```

### 5. **Test Message Flow**
1. Send a message to your WhatsApp number
2. Check Railway logs for:
   - `WhatsApp message from {phone_number}`
   - `Got response from MessageRouter`
   - `Sending message to {phone_number}`
   - `Result: success` or `Result: error`

### 6. **Debug Specific Errors**

**Error: "API error (403) sending message"**
- Token has expired: Regenerate in Meta App Dashboard
- Phone number ID incorrect: Double-check in Business Manager

**Error: "API error (400)"**
- Invalid phone number format
- Message text too long (check in logs)
- Button configuration malformed

**Error: "timeout"**
- Network connectivity issue
- WhatsApp API temporarily unavailable
- Check Railway network settings

## How to Get Help

1. **Check logs in Railway:** Look for error details
2. **Verify credentials:** Run diagnostic tool
3. **Test webhook:** Use curl to verify it responds
4. **Contact Meta Support:** If API key issues

## Diagnostic Command
```bash
python diagnose_whatsapp.py
```

This checks if all required environment variables are set and valid.
