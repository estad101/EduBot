# WhatsApp Bot Interactive Features

## Overview
The WhatsApp bot provides an interactive, conversational interface for students to register, submit homework, and manage subscriptions entirely through WhatsApp messages.

## Auto-Registration Flow

### 1. **Initial Contact**
When a student messages your WhatsApp bot number (+15551610271), they are automatically registered with that phone number. No manual registration needed!

### 2. **Conversation-Driven Registration**
The bot engages in a conversation to collect registration information:

```
Bot: "👋 Hi! Type 'help' for available commands, or:
     • register - Create account
     • homework - Submit homework
     • pay - Get subscription
     • status - Check subscription"

User: "register"

Bot: "✅ Let's register you! What is your full name?"
User: "John Doe"

Bot: "Great! What is your email address?"
User: "john@example.com"

Bot: "Perfect! What is your class or grade?"
User: "10A"

Bot: "✅ Registration complete! You can now:
     • Submit homework (type 'homework')
     • Buy subscription (type 'pay')
     • Check status (type 'status')"
```

## Core Commands

### 📝 **Register** - Auto-Register New Student
**Keywords**: register, reg, new, start

Creates a student account from WhatsApp conversation
- Collects: Full name, Email, Class/Grade
- Result: Phone number + data stored in database

### 📚 **Homework** - Submit Homework
**Keywords**: homework, submit, hand in, assignment

Flow:
1. Bot asks for subject (e.g., "Mathematics", "English")
2. Asks submission type (text, image, document)
3. Student provides content
4. Bot checks if subscription is active
   - **If subscribed**: ✅ Auto-assigns to tutor, sends confirmation
   - **If free**: Initiates payment (₦500 per submission)
5. After payment confirmed, assigns tutor

### 💳 **Pay/Subscribe** - Buy Monthly Subscription
**Keywords**: pay, payment, subscribe, buy

Flow:
1. Bot shows subscription details: "₦5,000/month - Unlimited homework"
2. Student replies "confirm"
3. Bot generates payment link
4. After payment, subscription activated
5. All future homework free (no per-submission fees)

### 📊 **Status/Check** - View Subscription Status
**Keywords**: status, check, subscription, active

Shows current subscription status:
- ✅ Active (has valid subscription)
- ❌ Inactive (free plan, needs payment)

### ❓ **Help** - Show Available Commands
**Keywords**: help, info, how, menu, options

Displays command menu and instructions

### 🔄 **Cancel** - Reset Conversation
**Keywords**: cancel, stop, reset, clear

Clears current conversation state and returns to initial menu

## Dashboard Features

### WhatsApp Registrations Page
Access via admin dashboard → "WhatsApp Registrations"

**Shows**:
- Total registered students (count)
- Students with active subscriptions (count)
- Conversion rate (% with paid subscriptions)
- Table of all registered numbers with:
  - Phone number
  - Full name
  - Email
  - Class/Grade
  - Subscription status (Active/Free)
  - Registration date

## Conversation State Machine

The bot maintains conversation state to handle multi-turn interactions:

```
INITIAL → User starts (reads menu)
    ↓
[User chooses action]
    ↓
REGISTERING_NAME → Collects name
    ↓
REGISTERING_EMAIL → Collects email
    ↓
REGISTERING_CLASS → Collects class/grade
    ↓
REGISTERED → Registration complete
    
[Or for homework]
HOMEWORK_SUBJECT → Collects subject
    ↓
HOMEWORK_TYPE → Collects submission type (text/image/document)
    ↓
HOMEWORK_CONTENT → Collects content or image
    ↓
HOMEWORK_SUBMITTED → Payment/Tutor assignment
    ↓
IDLE → Ready for next action

[Or for payment]
PAYMENT_PENDING → Waiting for payment confirmation
    ↓
PAYMENT_CONFIRMED → Subscription activated
```

**Timeout**: Conversations auto-reset after 30 minutes of inactivity

## Message Types Supported

The bot can handle:
- **Text messages**: Registration info, homework descriptions
- **Images**: Homework image submissions (auto-saved with timestamp)
- **Documents**: Homework file submissions
- **Buttons**: Quick-action replies (native WhatsApp buttons)

## Webhook Integration

The bot receives messages via webhook at:
```
POST /api/webhook/whatsapp
```

Process:
1. WhatsApp Cloud API sends message
2. Bot verifies webhook signature (HMAC-SHA256)
3. Parses message (phone, name, content)
4. Gets/creates student record
5. Routes to conversation handler
6. Sends response back via WhatsApp API
7. Updates subscription/homework status as needed

## Backend Endpoints

### Get All Registered Students
```bash
GET /api/students/list

Response:
{
  "status": "success",
  "data": {
    "students": [
      {
        "student_id": 1,
        "phone_number": "+15551610271",
        "full_name": "John Doe",
        "email": "john@example.com",
        "class_grade": "10A",
        "has_active_subscription": true,
        "created_at": "2026-01-07T10:30:00"
      }
    ],
    "total": 1
  }
}
```

### Get Registration Statistics
```bash
GET /api/students/stats

Response:
{
  "status": "success",
  "data": {
    "total_registered": 42,
    "with_active_subscription": 18,
    "total_subscriptions": 20
  }
}
```

## Environment Variables Required

```bash
# WhatsApp API Configuration
WHATSAPP_API_KEY=your_access_token
WHATSAPP_PHONE_NUMBER_ID=your_phone_id
WHATSAPP_WEBHOOK_TOKEN=your_webhook_token

# Message pricing (optional)
PER_SUBMISSION_FEE=500  # ₦500 per homework without subscription
MONTHLY_SUBSCRIPTION=5000  # ₦5000/month unlimited homework
```

## How to Deploy

1. **Set WhatsApp Credentials on Railway**:
   - `WHATSAPP_API_KEY` - Your WhatsApp Cloud API token
   - `WHATSAPP_PHONE_NUMBER_ID` - Your business phone number ID
   - `WHATSAPP_WEBHOOK_TOKEN` - Your chosen webhook secret

2. **Register Webhook with WhatsApp**:
   - Go to WhatsApp Dashboard → Webhooks
   - Set webhook URL to: `https://your-backend-url/api/webhook/whatsapp`
   - Set verify token to your `WHATSAPP_WEBHOOK_TOKEN`
   - Subscribe to message events

3. **Rebuild Services**:
   - Backend: Go to Railway → Backend → Deploy
   - Frontend: Go to Railway → Frontend → Deploy

4. **Test**:
   - Message your WhatsApp bot number
   - Type "help" to see menu
   - Type "register" to auto-register
   - Type "homework" to test submission flow

## Key Features

✅ **Fully Interactive** - Conversational flow, not just default messages  
✅ **Auto-Registration** - Students register by chatting  
✅ **State Management** - Tracks conversation progress per user  
✅ **Payment Integration** - Initiate payments, confirm subscriptions  
✅ **Tutor Assignment** - Auto-assign homework after payment/subscription  
✅ **Media Support** - Accept images and documents for homework  
✅ **Dashboard Integration** - View all registrations in admin panel  
✅ **Scalable** - Handles unlimited concurrent conversations  

## Troubleshooting

**Bot not responding?**
- Check WHATSAPP_API_KEY and WHATSAPP_PHONE_NUMBER_ID are set
- Verify webhook is registered in WhatsApp Dashboard
- Check backend logs: `docker logs backend`

**Students not auto-registering?**
- Ensure webhook is receiving messages (check status endpoint)
- Verify DATABASE_URL is correct
- Check Student model fields match registration schema

**Conversations timing out?**
- Default timeout is 30 minutes
- Modify `TIMEOUT_MINUTES` in `conversation_service.py` if needed

**Payment not initiating?**
- Check NEXT_PUBLIC_API_URL is set correctly on frontend
- Verify Paystack API key configured
- Check payment service logs

