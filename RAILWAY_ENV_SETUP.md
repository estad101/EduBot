# Railway Environment Variables Setup Guide

This document explains how to set up environment variables for EduBot on Railway.

## Environment Variables Overview

### 1. API & Server Configuration

| Variable | Value | Description |
|----------|-------|-------------|
| `API_TITLE` | EduBot API | API display name |
| `API_VERSION` | 1.0.0 | Current API version |
| `API_PORT` | 8000 | Backend API port |
| `ENVIRONMENT` | production | deployment environment |
| `DEBUG` | False | Disable debug mode in production |
| `HTTPS_ONLY` | True | Force HTTPS connections |

### 2. Database Configuration

| Variable | Value | Description |
|----------|-------|-------------|
| `DATABASE_URL` | mysql+pymysql://user:pass@host/db | Full MySQL connection string |
| `DATABASE_HOST` | localhost | Database server host |

**Railway Auto-Setup**: Railway MySQL service provides `DATABASE_URL` automatically!

### 3. Security & JWT

| Variable | Value | Description |
|----------|-------|-------------|
| `SECRET_KEY` | [GENERATE] | JWT secret key (keep secret!) |
| `ALGORITHM` | HS256 | JWT algorithm |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | 30 | Token expiration time |
| `SESSION_TIMEOUT_MINUTES` | 60 | Session timeout |

**How to Generate SECRET_KEY**:
```python
import secrets
print(secrets.token_urlsafe(32))
```

### 4. CORS & Origins

| Variable | Value | Description |
|----------|-------|-------------|
| `ALLOW_ORIGINS` | https://youradmindomain.com,https://yourapidomain.com | Allowed frontend domains |
| `ADMIN_ORIGIN` | https://youradmindomain.com | Admin UI domain |

### 5. WhatsApp Integration

| Variable | Value | Description |
|----------|-------|-------------|
| `WHATSAPP_API_KEY` | [Your Meta API Key] | WhatsApp Business API key |
| `WHATSAPP_PHONE_NUMBER_ID` | 797467203457022 | Your WhatsApp phone number ID |
| `WHATSAPP_BUSINESS_ACCOUNT_ID` | 1516305056071819 | WhatsApp business account ID |
| `WHATSAPP_PHONE_NUMBER` | +15551610271 | Your WhatsApp business number |
| `WHATSAPP_WEBHOOK_TOKEN` | iloveGOD2020! | Webhook verification token |

**Get from**: Meta Business Manager → WhatsApp Business Account

### 6. Payment Processing (Paystack)

| Variable | Value | Description |
|----------|-------|-------------|
| `PAYSTACK_PUBLIC_KEY` | pk_live_xxx | Paystack public key |
| `PAYSTACK_SECRET_KEY` | sk_live_xxx | Paystack secret key (keep secret!) |
| `PAYSTACK_WEBHOOK_SECRET` | [Your Secret] | Webhook signature secret |
| `PAYSTACK_WEBHOOK_URL` | https://yourdomain.com/api/payments/webhook/paystack | Webhook endpoint |

**Get from**: Paystack Dashboard → Settings → API Keys

### 7. Frontend Configuration

| Variable | Value | Description |
|----------|-------|-------------|
| `NEXT_PUBLIC_API_URL` | https://yourapidomain.com | Backend API endpoint |
| `NEXT_PUBLIC_APP_NAME` | EduBot | Application name |

### 8. File Upload Settings

| Variable | Value | Description |
|----------|-------|-------------|
| `UPLOADS_DIR` | uploads | Directory for uploads |
| `MAX_FILE_SIZE_MB` | 5 | Maximum file size |
| `ALLOWED_IMAGE_TYPES` | image/jpeg,image/png,image/webp | Allowed image types |

### 9. Logging & Monitoring

| Variable | Value | Description |
|----------|-------|-------------|
| `LOG_LEVEL` | WARNING | Log level (DEBUG, INFO, WARNING, ERROR) |
| `LOG_FILE` | logs/chatbot.log | Log file path |
| `SENTRY_DSN` | [Your Sentry DSN] | Error tracking service |

### 10. Rate Limiting

| Variable | Value | Description |
|----------|-------|-------------|
| `RATE_LIMIT_PER_MINUTE` | 60 | Requests per minute limit |

---

## Setting Up on Railway

### Step 1: Go to Railway Dashboard

1. Navigate to your EduBot project on Railway
2. Click the backend service
3. Go to "Variables" tab

### Step 2: Add Variables One by One

Click "Add Variable" and enter each variable:

```
Key: API_TITLE
Value: EduBot API
```

Continue for all variables above.

### Step 3: Critical Variables (Must Change!)

These require YOUR actual values:

1. **WHATSAPP_API_KEY** - From Meta Business Manager
2. **WHATSAPP_PHONE_NUMBER_ID** - Your WhatsApp phone ID
3. **WHATSAPP_BUSINESS_ACCOUNT_ID** - Your business account ID
4. **WHATSAPP_PHONE_NUMBER** - Your WhatsApp number
5. **WHATSAPP_WEBHOOK_TOKEN** - Generate a strong random token
6. **PAYSTACK_PUBLIC_KEY** - From Paystack dashboard
7. **PAYSTACK_SECRET_KEY** - From Paystack dashboard
8. **SECRET_KEY** - Generate using Python (see above)

### Step 4: Database Connection

Railway will provide:
```
DATABASE_URL=mysql://user:pass@host:port/railway
```

**Just copy it to the DATABASE_URL variable!**

### Step 5: Domain Configuration

If using custom domain:
1. Go to Railway project settings
2. Add domain: `api.yourdomain.com`
3. Update `ALLOW_ORIGINS` and `ADMIN_ORIGIN`

### Step 6: Frontend (Optional)

If deploying admin-ui service, set:
```
NEXT_PUBLIC_API_URL=https://api.yourdomain.com
```

---

## Production Checklist

Before going live, verify:

- [ ] `SECRET_KEY` is a strong random string
- [ ] `DEBUG=False`
- [ ] `HTTPS_ONLY=True`
- [ ] `WHATSAPP_API_KEY` is valid
- [ ] `PAYSTACK_SECRET_KEY` is from live account (pk_live_, sk_live_)
- [ ] `PAYSTACK_WEBHOOK_SECRET` is set
- [ ] `ALLOW_ORIGINS` includes your actual domains
- [ ] `DATABASE_URL` connects successfully
- [ ] All WhatsApp values are correct
- [ ] Log level is WARNING (not DEBUG)

---

## Generating Strong Keys

### SECRET_KEY (JWT Secret)
```bash
python3 -c "import secrets; print(secrets.token_urlsafe(32))"
```

### WHATSAPP_WEBHOOK_TOKEN
```bash
python3 -c "import secrets; print(secrets.token_hex(16))"
```

### PAYSTACK_WEBHOOK_SECRET (if needed)
```bash
python3 -c "import secrets; print(secrets.token_urlsafe(32))"
```

---

## Updating Variables

To update variables after deployment:

1. Go to Railway dashboard
2. Click your service
3. Go to "Variables" tab
4. Edit the variable value
5. Click "Save"
6. Railway automatically redeploys with new variables

---

## Troubleshooting

### Database Connection Error
- Check `DATABASE_URL` is correct
- Ensure MySQL service is running
- Verify user credentials
- Check firewall/networking settings

### WhatsApp Not Sending Messages
- Verify `WHATSAPP_API_KEY` is valid
- Check phone number format (must include country code: +234...)
- Ensure webhook token matches Meta configuration
- Test with simple message first

### Paystack Payments Not Working
- Verify secret keys are from live environment (sk_live_, pk_live_)
- Check webhook URL is accessible
- Verify webhook secret matches Paystack settings
- Test with Paystack test mode first

### CORS Errors
- Add your frontend domain to `ALLOW_ORIGINS`
- Use exact domain with protocol: https://yourdomain.com
- Separate multiple domains with commas (no spaces)

---

## Getting Help

- **Railway Support**: https://railway.app/support
- **GitHub Issues**: https://github.com/estad101/EduBot/issues
- **Meta (WhatsApp)**: https://developers.facebook.com/docs/whatsapp
- **Paystack Support**: https://paystack.com/support

---

**Status**: Environment setup guide complete! 🚀
