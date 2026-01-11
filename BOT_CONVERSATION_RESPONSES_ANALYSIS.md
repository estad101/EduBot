# Bot Conversation Logic - Complete Response Analysis

## Overview
This document extracts and lists ALL preformatted bot responses used in the EduBot conversation system. The bot uses a message database-driven approach where all responses are stored in the `bot_messages` table with different types and contexts.

---

## Conversation States
The bot tracks 17 different conversation states:

1. **INITIAL** - New user first interaction
2. **IDENTIFYING** - Checking if existing user
3. **REGISTERING_NAME** - Collecting full name
4. **REGISTERING_EMAIL** - Collecting email
5. **REGISTERING_CLASS** - Collecting class/grade
6. **UPDATING_NAME** - Updating existing name
7. **UPDATING_EMAIL** - Updating existing email
8. **UPDATING_CLASS** - Updating existing class
9. **ALREADY_REGISTERED** - User tried to register but has account
10. **REGISTERED** - User is registered
11. **HOMEWORK_SUBJECT** - Selecting homework subject
12. **HOMEWORK_TYPE** - Choosing submission type
13. **HOMEWORK_CONTENT** - Providing homework content
14. **HOMEWORK_SUBMITTED** - Homework submitted
15. **PAYMENT_PENDING** - Waiting for payment
16. **PAYMENT_CONFIRMED** - Payment completed
17. **CHAT_SUPPORT_ACTIVE** - In active support chat
18. **IDLE** - Waiting for input

---

## Message Types
The bot uses 6 message types:

- **greeting** - Welcome/introduction messages
- **prompt** - Questions requiring user input
- **menu** - Messages with menu options
- **confirmation** - Success/confirmation messages
- **error** - Error/warning messages
- **info** - Information/FAQ messages

---

## 📋 All Preformatted Bot Responses

### 1. REGISTRATION FLOW

#### 1.1 Name Registration Prompt
```
KEY: registration_name_prompt
TYPE: prompt
CONTEXT: REGISTERING_NAME
CONTENT: "What is your full name?"
MENU: No
NEXT STATES: REGISTERING_EMAIL
```

#### 1.2 Email Registration Prompt
```
KEY: registration_email_prompt
TYPE: prompt
CONTEXT: REGISTERING_EMAIL
CONTENT: "Great! What is your email address?"
MENU: No
NEXT STATES: REGISTERING_CLASS
```

#### 1.3 Class/Grade Registration Prompt
```
KEY: registration_class_prompt
TYPE: prompt
CONTEXT: REGISTERING_CLASS
CONTENT: "Perfect! What is your class/grade?

(e.g., 10A, SS2, Form 4)"
MENU: No
NEXT STATES: REGISTERED
```

#### 1.4 Registration Complete Confirmation
```
KEY: registration_complete
TYPE: confirmation
CONTEXT: REGISTERED
CONTENT: "✅ Account Created!

Welcome, {full_name}! 👋

📚 **AVAILABLE FEATURES** 📚

🏠 **Home** - Return to home menu
❓ **FAQ** - Get answers to common questions
📝 **Homework** - Submit your homework
💬 **Support** - Chat with our team
💳 **Subscribe** - View subscription plans
📊 **Status** - Check your account details

Just type a command above to get started!"

MENU ITEMS:
- 🏠 Home (main_menu)
- ❓ FAQ (faq)
- 📝 Homework (homework)
- 💬 Support (support)
- 💳 Subscribe (pay)
- 📊 Status (check)

NEXT STATES: IDLE
VARIABLES: {full_name}
```

---

### 2. HOMEWORK SUBMISSION FLOW

#### 2.1 Homework Introduction
```
KEY: homework_intro
TYPE: info
CONTEXT: HOMEWORK_SUBJECT
CONTENT: "📝 **Homework Submission**

Let's get started! Which subject is your homework for?

🔹 Common subjects:
• Mathematics
• English
• Science
• History
• Geography
• Other"

MENU ITEMS:
- 📐 Mathematics (homework_math)
- 📚 English (homework_english)
- 🔬 Science (homework_science)
- 🔹 Other (homework_other)
- ❌ Cancel (main_menu)

NEXT STATES: HOMEWORK_CONTENT
```

#### 2.2 Homework Subject Prompt
```
KEY: homework_subject_prompt
TYPE: prompt
CONTEXT: HOMEWORK_SUBJECT
CONTENT: "What subject is your homework for?

(e.g., Mathematics, English, Science)"

MENU: No
NEXT STATES: HOMEWORK_TYPE
```

#### 2.3 Homework Type Selection
```
KEY: homework_type_prompt
TYPE: prompt
CONTEXT: HOMEWORK_TYPE
CONTENT: "How would you like to submit?"

MENU ITEMS:
- 📝 Text (text)
- 🖼️ Image (image)

NEXT STATES: HOMEWORK_CONTENT
```

---

### 3. PAYMENT & SUBSCRIPTION FLOW

#### 3.1 Subscription Offer
```
KEY: subscription_offer
TYPE: info
CONTEXT: PAYMENT_PENDING
CONTENT: "💰 Monthly Subscription
Price: ₦5,000/month
Unlimited homework submissions

Tap 'Confirm Payment' to proceed."

MENU ITEMS:
- ✅ Confirm Payment (payment_confirm)
- ❌ Cancel (cancel)

NEXT STATES: PAYMENT_CONFIRMED, IDLE
```

#### 3.2 Subscription Plans
```
KEY: subscription_plans
TYPE: info
CONTEXT: PAYMENT_PENDING
CONTENT: "💳 **Subscription Plans**

🎯 **Basic** - Free
• Limited submissions (5/month)
• Standard support

⭐ **Premium** - ₦5,000/month
• Unlimited submissions
• Priority support
• Detailed feedback

👑 **Pro** - ₦10,000/month
• Everything in Premium
• Direct tutor access
• Weekly progress reports"

MENU ITEMS:
- 🎯 Basic (Free) (subscribe_basic)
- ⭐ Premium (subscribe_premium)
- 👑 Pro (subscribe_pro)
- ⬅️ Back (main_menu)

NEXT STATES: PAYMENT_CONFIRMED, IDLE
```

---

### 4. MAIN MENU

#### 4.1 Main Menu (Registered Users)
```
KEY: main_menu
TYPE: menu
CONTEXT: IDLE
CONTENT: "Welcome back! 👋

📚 **AVAILABLE FEATURES** 📚

Just type a command below to get started!"

MENU ITEMS:
- 🏠 Home (main_menu)
- ❓ FAQ (faq)
- 📝 Homework (homework)
- 💬 Support (support)
- 💳 Subscribe (pay)
- 📊 Status (check)

NEXT STATES: HOMEWORK_SUBJECT, PAYMENT_PENDING, CHAT_SUPPORT_ACTIVE
```

#### 4.2 Welcome Message (Unregistered Users)
```
KEY: welcome_unregistered
TYPE: greeting
CONTEXT: IDLE
CONTENT: "👋 Welcome to {bot_name}!

I'm here to help you with homework submission and learning support.

📌 **To get started:**

Type 'Register' to create an account, or ask me anything!"

MENU ITEMS:
- 📝 Register (register)
- ❓ FAQ (faq_menu)
- 💬 Support (support_intro)

NEXT STATES: REGISTERING_NAME, FAQ_MENU, CHAT_SUPPORT_ACTIVE
VARIABLES: {bot_name}
```

---

### 5. FAQ SECTION

#### 5.1 FAQ Menu Introduction
```
KEY: faq_intro
TYPE: info
CONTEXT: FAQ_MENU
CONTENT: "❓ **Frequently Asked Questions**

Choose a topic below to learn more:"

MENU ITEMS:
- 📝 How do I register? (faq_registration)
- 📤 How do I submit homework? (faq_homework)
- 💰 What's the pricing? (faq_pricing)
- 💳 Payment methods? (faq_payment)
- 🆘 Need help? (support)

NEXT STATES: IDLE
```

#### 5.2 FAQ: How to Register
```
KEY: faq_registration
TYPE: info
CONTEXT: FAQ_REGISTRATION
CONTENT: "📝 **How do I register?**

Registration is simple:
1. Send 'Register' to start
2. Provide your full name
3. Enter your email address
4. Tell us your class/grade
5. Done! Your account is ready

You'll then have access to all features."

MENU ITEMS:
- ⬅️ Back to FAQ (faq_menu)
- 🏠 Home (main_menu)

NEXT STATES: FAQ_MENU, IDLE
```

---

### 6. SUPPORT SECTION

#### 6.1 Support Chat Introduction
```
KEY: support_intro
TYPE: info
CONTEXT: CHAT_SUPPORT_ACTIVE
CONTENT: "💬 **Chat Support**

Hello! Welcome to our support team. How can we help you today?

You can ask about:
✅ Account issues
✅ Homework submission
✅ Payment problems
✅ Technical issues
✅ Other questions"

MENU ITEMS:
- 📋 Report an issue (support_issue)
- 💳 Billing question (support_billing)
- ❓ Other (support_other)
- ✅ Close chat (main_menu)

NEXT STATES: IDLE
```

---

### 7. ACCOUNT INFORMATION

#### 7.1 Account Status Check
```
KEY: status_check
TYPE: info
CONTEXT: IDLE
CONTENT: "📊 **Account Status**

Name: {full_name}
Email: {email}
Class: {class}
Subscription: {subscription_status}
Joined: {join_date}"

MENU ITEMS:
- ⬅️ Back to menu (main_menu)

NEXT STATES: IDLE
VARIABLES: {full_name}, {email}, {class}, {subscription_status}, {join_date}
```

---

### 8. ERROR MESSAGES

#### 8.1 Registration Required Error
```
KEY: registration_required
TYPE: error
CONTEXT: IDLE
CONTENT: "❌ Registration Required

You need to create an account first. Choose 'Register' to get started."

MENU: No
```

#### 8.2 Generic Error Message
```
KEY: error_generic
TYPE: error
CONTEXT: IDLE
CONTENT: "❌ Error processing your message. Please try again."

MENU: No
```

---

## 📊 Message Statistics

| Category | Count |
|----------|-------|
| **Total Messages** | 17 |
| **Greeting Messages** | 1 |
| **Prompt Messages** | 3 |
| **Menu Messages** | 1 |
| **Confirmation Messages** | 1 |
| **Error Messages** | 2 |
| **Info Messages** | 9 |

---

## 🎯 Response Flow Diagram

```
┌─────────────────────────────────────────────────────────┐
│                    NEW USER (INITIAL)                   │
└────────────────┬────────────────────────────────────────┘
                 │
        ┌────────▼────────┐
        │ welcome_        │
        │ unregistered    │
        │ [greeting]      │
        └────────┬────────┘
                 │
    ┌────────────┼────────────┬────────────────┐
    │            │            │                │
    ▼            ▼            ▼                ▼
  FAQ       REGISTER     SUPPORT          HOMEWORK
  Menu      Flow         Chat             (Error)
    │            │            │
    │    ┌───────▼──────┐     │
    │    │registration_ │     │
    │    │name_prompt   │     │
    │    │[prompt]      │     │
    │    └───────┬──────┘     │
    │           │             │
    │    ┌──────▼────────┐    │
    │    │registration_ │    │
    │    │email_prompt  │    │
    │    │[prompt]      │    │
    │    └──────┬───────┘    │
    │          │             │
    │    ┌─────▼──────────┐  │
    │    │registration_  │  │
    │    │class_prompt   │  │
    │    │[prompt]       │  │
    │    └─────┬─────────┘  │
    │         │             │
    │    ┌────▼────────────────┐
    │    │registration_        │
    │    │complete [conf]      │
    │    └────┬────────────────┘
    │         │
    └─────────┼─────────────────────────┐
              │                         │
    ┌─────────▼─────────┐     ┌────────▼──────┐
    │   MAIN MENU       │     │  HOMEWORK     │
    │   [menu]          │     │  FLOW         │
    │                   │     │               │
    │ - Home            │     └───────────────┘
    │ - FAQ             │
    │ - Homework        │
    │ - Support         │
    │ - Subscribe       │
    │ - Status          │
    └───────────────────┘
```

---

## 📝 Template Variables

Variables used in bot responses:

| Variable | Used In | Example |
|----------|---------|---------|
| `{bot_name}` | welcome_unregistered | "Welcome to EduBot!" |
| `{full_name}` | registration_complete, status_check | "Welcome, John Doe!" |
| `{email}` | status_check | john@example.com |
| `{class}` | status_check | "SS2" |
| `{subscription_status}` | status_check | "Premium - Active" |
| `{join_date}` | status_check | "2024-01-10" |

---

## 🎨 Emoji Usage Guide

The bot uses emojis consistently across all messages:

| Emoji | Usage | Examples |
|-------|-------|----------|
| 👋 | Welcome/Greeting | Welcome messages |
| ✅ | Success/Confirmation | Registration complete, confirmations |
| ❌ | Error/Cancel/Negative | Errors, cancel options |
| 📚 | Education/Features | Features list, homework |
| 📝 | Writing/Form | Registration, homework text |
| 📐 | Math/Calculation | Mathematics subject |
| 📚 | Literature/English | English subject |
| 🔬 | Science | Science subject |
| 📤 | Upload/Submit | Homework submission |
| 🖼️ | Images/Visual | Image submission option |
| 💬 | Chat/Support | Support, chat features |
| 💳 | Payment/Cards | Payment, subscription |
| 💰 | Money/Pricing | Pricing, payment info |
| ⭐ | Premium/Special | Premium subscription |
| 👑 | VIP/Pro | Pro subscription |
| 📊 | Status/Analytics | Account status |
| ❓ | Questions/FAQ | FAQ section |
| 🏠 | Home/Return | Home menu option |
| ⬅️ | Back/Return | Back navigation |
| 🎯 | Target/Basic | Basic plan |
| 🔹 | Other/Options | Other options |
| ℹ️ | Info/Help | Help information |

---

## 🔄 Conversation Flow Sequences

### Registration Flow
```
INITIAL → REGISTERING_NAME → REGISTERING_EMAIL → REGISTERING_CLASS → REGISTERED → IDLE
```

### Homework Flow
```
IDLE → HOMEWORK_SUBJECT → HOMEWORK_TYPE → HOMEWORK_CONTENT → HOMEWORK_SUBMITTED → IDLE
```

### Payment Flow
```
IDLE → PAYMENT_PENDING → PAYMENT_CONFIRMED → IDLE
```

### Support Flow
```
IDLE → CHAT_SUPPORT_ACTIVE → IDLE
```

### FAQ Flow
```
IDLE → FAQ_MENU → (specific FAQ) → IDLE
```

---

## 💡 Key Features

1. **Personalization** - All registered user messages include `{full_name}`
2. **Context-Aware** - Messages change based on user's conversation state
3. **Menu-Driven** - Many messages include quick-action buttons/menus
4. **Error Handling** - Specific error messages for different scenarios
5. **Variable Support** - Dynamic content insertion via template variables
6. **Next States** - Clear defined next conversation states for each message
7. **Descriptions** - Admin descriptions for each message for management

---

## 📌 Implementation Details

### Message Storage
- **Table**: `bot_messages`
- **Fields**: message_key, message_type, context, content, menu_items, next_states, variables, is_active
- **Total Pre-seeded**: 17 messages

### Message Retrieval
- Stored in database (initially seeded from migration)
- Loaded at runtime via `BotMessageService`
- Can be updated/managed through admin dashboard

### Conversation Context
- Stored in-memory or in Redis for session management
- Timeout: 30 minutes of inactivity
- Tracked per phone number (WhatsApp identifier)

---

## 🚀 Usage in Code

### Fetching Messages
```python
# Via API
GET /api/messages/list?context=REGISTERING_NAME

# Via Service
messages = BotMessageService.get_message_by_context(db, "REGISTERING_NAME")
```

### Sending Messages
```python
# The bot retrieves the appropriate message based on conversation state
next_response, next_state = MessageRouter.get_next_response(
    phone_number="1234567890",
    message_text="Hello",
    student_data=student_info,
    db=db
)
# Returns: ("response text", ConversationState.NEXT_STATE)
```

---

## ✅ Summary

The EduBot system has **17 preformatted bot responses** organized by:
- **6 message types** (greeting, prompt, menu, confirmation, error, info)
- **18 conversation states** for tracking user progress
- **Template variables** for personalization
- **Menu items** for rich interaction
- **Clear flow sequences** for registration, homework, payment, support, and FAQ

All responses are stored in the database and can be managed through the admin dashboard.
