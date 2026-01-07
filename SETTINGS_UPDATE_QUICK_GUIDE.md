# Quick Settings Update Guide

## Update WhatsApp Credentials in Production (Railway)

### Via Admin Dashboard (Recommended)

1. **Open Settings Page**
   - Go to: `https://nurturing-exploration-production.up.railway.app/settings`
   - Login with admin credentials

2. **Update WhatsApp Tab**
   - Scroll to "WhatsApp Settings" section
   - Update any of these fields:
     - **Token** (whatsapp_api_key): Your WhatsApp access token
     - **Phone Number ID** (whatsapp_phone_number_id): From WhatsApp Business
     - **Business Account ID** (whatsapp_business_account_id): From WhatsApp Business
     - **Phone Number** (whatsapp_phone_number): Your WhatsApp phone number

3. **Save**
   - Click "Save Settings" button
   - You'll see "Settings saved successfully" message
   - New settings take effect immediately ✓

### Via API (For Automation)

```bash
curl -X POST "https://api-url/api/admin/settings/update" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN" \
  -d '{
    "whatsapp_api_key": "EAAckpQFzzTUBQa7fNBS...",
    "whatsapp_phone_number_id": "797467203457022",
    "whatsapp_business_account_id": "107234695...",
    "whatsapp_phone_number": "+234811234567"
  }'
```

### Via Database (Direct)

```sql
-- Connect to Railway MySQL database
-- Update WhatsApp token
UPDATE admin_settings 
SET value = 'EAAckpQFzzTUBQa7fNBS...'
WHERE key = 'whatsapp_api_key';

-- Update phone number ID
UPDATE admin_settings 
SET value = '797467203457022'
WHERE key = 'whatsapp_phone_number_id';

-- Verify changes
SELECT key, value FROM admin_settings 
WHERE key LIKE 'whatsapp%';
```

**Note**: After direct database update, restart the app or call the API to refresh cache.

## Verify Settings Were Applied

### Check in Admin Dashboard
1. Go to `/settings`
2. Look at "WhatsApp Settings" section
3. Verify values are displayed correctly

### Check Application Logs
Look for these messages on startup:
```
✓ WhatsApp settings loaded from database
✓ Settings cache initialized with N entries
```

### Check Database
```sql
SELECT * FROM admin_settings WHERE key LIKE 'whatsapp%' ORDER BY updated_at DESC;
```

## Test WhatsApp Connection

### Use Test Message Feature
1. Go to `/settings` → WhatsApp tab
2. Scroll to "Test WhatsApp Connection"
3. Enter your phone number (e.g., +2348109508833)
4. Click "Send Test Message"
5. You should receive a message on WhatsApp within seconds

### Check Webhook Status
Go to `/settings/debug` to see token validation details:
- Token length
- Token preview
- Whether token is valid
- Token prefix

## Troubleshooting

### Settings not updating?
1. Verify you're logged in as admin
2. Check that new values are different from old ones
3. Look for error message in red text
4. Check browser console (F12 → Console tab)

### WhatsApp not sending messages after update?
1. Go to `/settings` → WhatsApp tab
2. Click "Send Test Message" 
3. If test fails, check token validity in debug page
4. Restart app if needed to refresh cache

### Token says "Invalid"?
1. Verify token is correct from WhatsApp Business console
2. Token must start with "EAAC..." (access token format)
3. Token must not have spaces or newlines
4. Token may be expired - generate new one in WhatsApp Business

### Can't see settings page?
1. Make sure you're admin user
2. Log out and log back in
3. Check browser has JavaScript enabled
4. Try incognito/private mode to clear cache

## Current WhatsApp Setup

**Current API Endpoint**: `https://graph.facebook.com/v22.0`

**Required Settings**:
- ✓ whatsapp_api_key (token)
- ✓ whatsapp_phone_number_id
- ✓ whatsapp_business_account_id
- ✓ whatsapp_phone_number

**Where to Get These Values**:
1. Go to: https://developers.facebook.com/apps
2. Select your WhatsApp app
3. Go to "WhatsApp Business Account"
4. Find "Phone Numbers" section
5. Copy the Phone Number ID and Business Account ID
6. Go to "System Users" → find your token
7. Your WhatsApp number is in the phone numbers section

## Environment Variables (Fallback)

If database is empty, these env vars are used:
```
WHATSAPP_API_KEY=...
WHATSAPP_PHONE_NUMBER_ID=...
WHATSAPP_BUSINESS_ACCOUNT_ID=...
WHATSAPP_PHONE_NUMBER=...
WHATSAPP_WEBHOOK_TOKEN=...
```

Settings from database take precedence over env vars.

