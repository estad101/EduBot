# Bot Conversation Logic - Draft Design

**Date:** January 9, 2026  
**Status:** DRAFT

---

## 1. Core Conversation States

### User Registration Flow
```
START → INITIAL (New User)
    ↓
    → Ask: "What is your full name?"
    ↓
REGISTERING_NAME (User enters name)
    ↓
    → Ask: "What is your email address?"
    ↓
REGISTERING_EMAIL (User enters email)
    ↓
    → Ask: "What is your class/grade?"
    ↓
REGISTERING_CLASS (User enters class)
    ↓
    → Response: "✅ Account Created!"
    ↓
REGISTERED (User completes registration)
```

### Main Conversation States
- **INITIAL** - Brand new user, not registered
- **IDENTIFYING** - Checking if user exists
- **REGISTERING_NAME** - Collecting full name
- **REGISTERING_EMAIL** - Collecting email
- **REGISTERING_CLASS** - Collecting class/grade
- **REGISTERED** - User registration complete
- **IDLE** - Registered user, waiting for input
- **HOMEWORK_SUBJECT** - User selecting homework subject
- **HOMEWORK_TYPE** - User choosing text or image submission
- **HOMEWORK_CONTENT** - User submitting homework
- **HOMEWORK_SUBMITTED** - Homework received
- **PAYMENT_PENDING** - Waiting for payment confirmation
- **PAYMENT_CONFIRMED** - Payment successful
- **CHAT_SUPPORT_ACTIVE** - User in live chat
- **HOMEWORK_PAID** - Homework payment confirmed

---

## 2. Intent Recognition System

### Primary Intents
```python
INTENT_HOMEWORK = ["homework", "submit", "hand in", "assignment"]
INTENT_REGISTER = ["register", "reg", "new", "start"]
INTENT_PAY = ["pay", "payment", "subscribe", "buy"]
INTENT_CHECK = ["status", "check", "subscription"]
INTENT_HELP = ["help", "info", "how", "menu"]
INTENT_FAQ = ["faq", "faqs", "question"]
INTENT_SUPPORT = ["support", "chat", "help me", "agent"]
INTENT_MAIN_MENU = ["main_menu", "main menu"]
INTENT_CANCEL = ["cancel", "stop", "reset", "menu"]
INTENT_IMAGE = ["image", "photo", "picture"]
INTENT_TEXT = ["text", "write", "type"]
INTENT_CONFIRM = ["yes", "confirm", "ok", "proceed"]
INTENT_END_CHAT = ["end", "exit", "quit", "close"]
```

### Intent Detection Rules
1. Extract keywords from user message
2. Match against keyword lists
3. Prioritize certain intents (help/cancel over others)
4. Return matched intent or DEFAULT

---

## 3. Conversation Flow Sequences

### Sequence A: New User Registration
```
User: "Hi"
Bot: "Welcome! What's your name?"
State: REGISTERING_NAME

User: "John Smith"
Bot: "What's your email?"
State: REGISTERING_EMAIL

User: "john@email.com"
Bot: "What class are you in?"
State: REGISTERING_CLASS

User: "Form 4"
Bot: "Account created! What would you like to do?"
State: IDLE
```

### Sequence B: Submit Homework (Text)
```
User: "Submit homework"
Bot: "What subject?"
State: HOMEWORK_SUBJECT

User: "Mathematics"
Bot: "Text or Image?"
State: HOMEWORK_TYPE

User: "Text"
Bot: "Send your answer:"
State: HOMEWORK_CONTENT

User: "[Math answer]"
Bot: "Received! Pay ₦500 or subscribe?"
State: PAYMENT_PENDING

User: "Pay"
Bot: "Processing payment..."
State: PAYMENT_CONFIRMED
→ "Done! Tutor will respond in 24 hours"
State: HOMEWORK_SUBMITTED
```

### Sequence C: Submit Homework (Image)
```
User: "Homework"
Bot: "What subject?"
State: HOMEWORK_SUBJECT

User: "English"
Bot: "Text or Image?"
State: HOMEWORK_TYPE

User: "Image"
Bot: "Upload your image:"
State: HOMEWORK_CONTENT

User: "[Image uploaded]"
Bot: "Payment required"
State: PAYMENT_PENDING
```

### Sequence D: Check Subscription Status
```
User: "Check status"
Bot: "Status: ACTIVE until Jan 31, 2026"
State: IDLE
```

### Sequence E: Chat Support
```
User: "Chat support"
Bot: "Connected to support team!"
State: CHAT_SUPPORT_ACTIVE

User: "[Support message]"
Bot: "Message sent to admin"
State: CHAT_SUPPORT_ACTIVE

User: "End"
Bot: "Chat ended. Anything else?"
State: IDLE
```

---

## 4. Bot Response Templates

### Welcome Messages
```
New User:
"👋 Welcome! I'm EduBot, your AI tutor.
Let's create your account first.

What's your full name?"

Returning User:
"Hey John! 👋
What can I help you with today?"
```

### Question Prompts
```
Subject Selection:
"📚 What subject is your homework for?
(e.g., Mathematics, English, Science)"

Content Request:
"📝 Send your homework answer:
- Type it directly
- Or share an image
- Maximum 5MB per image"

Payment Confirmation:
"💳 This homework costs ₦500
Subscribe for ₦5,000/month for unlimited.
Pay or Subscribe?"
```

### Success Messages
```
Registration Complete:
"✅ Account Created!
Welcome, John!
You're now registered as a FREE user.

What would you like to do?"

Homework Received:
"✅ Homework Submitted!
A tutor will respond within 24 hours.
We'll send you a message when ready."

Payment Confirmed:
"✅ Payment Successful!
Thank you for your purchase.
A tutor is reviewing your work."
```

### Error Messages
```
Invalid Input:
"❌ I didn't understand that.
Please try again or type 'help'"

Unauthorized Action:
"❌ You need to register first.
Type 'register' to get started."

Payment Failed:
"❌ Payment failed.
Please try again or contact support."
```

---

## 5. State Transition Logic

### From IDLE State
```
Input: "homework" → State: HOMEWORK_SUBJECT
Input: "pay" → State: PAYMENT_PENDING
Input: "faq" → State: IDLE (return FAQ text)
Input: "support" → State: CHAT_SUPPORT_ACTIVE
Input: "status" → State: IDLE (return status)
Input: "help" → State: IDLE (return help text)
Input: Other → State: IDLE (ask for clarification)
```

### From HOMEWORK_SUBJECT
```
Input: [Subject name] → State: HOMEWORK_TYPE
Input: "cancel" → State: IDLE
Input: "help" → State: IDLE
```

### From HOMEWORK_TYPE
```
Input: "text" → State: HOMEWORK_CONTENT
Input: "image" → State: HOMEWORK_CONTENT
Input: "cancel" → State: IDLE
```

### From HOMEWORK_CONTENT
```
Input: [Content/Image] → State: HOMEWORK_SUBMITTED
Input: "cancel" → State: IDLE
```

### From HOMEWORK_SUBMITTED
```
Auto: → State: PAYMENT_PENDING
```

### From PAYMENT_PENDING
```
Input: "confirm"/"yes" → State: PAYMENT_CONFIRMED
Input: "cancel" → State: IDLE
```

### From CHAT_SUPPORT_ACTIVE
```
Input: [Any message] → State: CHAT_SUPPORT_ACTIVE (stays)
Input: "end"/"exit" → State: IDLE
```

---

## 6. Message Handling Logic

### Algorithm
```
1. Extract message text
2. Identify user by phone number
3. Get user conversation state
4. Extract intent from message
5. Check state-specific handlers
6. Generate response
7. Update user state
8. Return (response, new_state)
```

### Priority Order
```
1. Check cancel/exit intents
2. Check end_chat intents  
3. Check state-specific intents
4. Check global intents
5. Return default "didn't understand" response
```

---

## 7. Data Persistence

### Conversation State Storage
```
User {
  phone_number: str (unique)
  state: ConversationState
  last_updated: datetime
  timeout: 30 minutes
}
```

### User Data Storage
```
Student {
  phone_number: str (unique)
  full_name: str
  email: str
  class_grade: str
  has_subscription: bool
  subscription_expiry: date
  created_at: datetime
}
```

### Homework Data Storage
```
Homework {
  id: uuid
  student_id: str
  subject: str
  content_type: "text" | "image"
  content: str | url
  submitted_at: datetime
  status: "pending" | "reviewed" | "completed"
  tutor_response: str
}
```

### Chat Data Storage
```
ChatSession {
  id: uuid
  student_id: str
  admin_id: str
  started_at: datetime
  ended_at: datetime
  messages: []
  status: "active" | "closed"
}
```

---

## 8. Error Handling

### Timeout
```
If message older than 30 minutes:
→ Reset to IDLE state
→ Show welcome message
```

### Invalid Input
```
If intent not recognized:
→ Stay in current state
→ Show: "❌ I didn't understand. Try again or type 'help'"
```

### Missing Data
```
If user not in database:
→ Initialize as INITIAL state
→ Start registration
```

### Payment Failure
```
If payment doesn't go through:
→ Stay in PAYMENT_PENDING
→ Show: "Payment failed. Try again?"
```

---

## 9. Special Features

### Personalization
```
Use first_name in responses:
"Hey {first_name}! 👋"
"Thanks {first_name}!"
```

### Emoji Usage
```
✅ Success
❌ Error
📚 Education
📝 Homework
💳 Payment
💬 Chat
❓ Question
📊 Status
👋 Welcome
⭐ Premium
```

### Response Templates
```
All responses follow pattern:
[Emoji] [Greeting/Action]

[Details]

[Call to action or options]
```

---

## 10. Conversation Examples

### Example 1: Complete Homework Flow
```
User: "Hi bot"
Bot: "Hey! 👋 What would you like to do?"

User: "I want to submit homework"
Bot: "📚 What subject?"

User: "Math"
Bot: "📝 Text or 🖼️ Image?"

User: "Text"
Bot: "Send your answer:"

User: "2x + 3 = 7, so x = 2"
Bot: "✅ Received!
💳 Cost: ₦500
📱 Subscribe: ₦5,000/month

Pay or Subscribe?"

User: "Pay"
Bot: "✅ Payment confirmed!
A tutor will review your work.
We'll message you when done. ⏱️"
```

### Example 2: New User Registration
```
User: "Hello"
Bot: "👋 Welcome to EduBot!
Let's create your account.
What's your name?"

User: "Amara Johnson"
Bot: "Nice to meet you, Amara!
What's your email?"

User: "amara@email.com"
Bot: "And what's your class?"

User: "SS2"
Bot: "✅ All set, Amara!
You're now registered.
📝 Submit homework
💬 Chat with tutors
❓ Ask questions"
```

### Example 3: Chat Support
```
User: "I need help"
Bot: "💬 Connecting to support team...

You're now chatting with admin.
How can we help?"

User: "How do I submit image homework?"
Bot: "📸 To submit image homework:
1. Choose 'Homework'
2. Select 'Image'
3. Upload your image
4. Confirm payment

Any other questions?"

User: "No, thanks!"
Bot: "Great! Type 'end' to close chat."

User: "end"
Bot: "Thanks for chatting! 👋
Anything else?"
```

---

## 11. Key Design Decisions

✅ **Simple & Direct** - Each interaction has clear purpose
✅ **Stateful** - Track user progress through flows
✅ **Flexible** - Handle interruptions (cancel, help, etc.)
✅ **Personalized** - Use names and relevant emojis
✅ **Safe** - Timeout prevents stale conversations
✅ **Clear Feedback** - Every action gets acknowledgment
✅ **Intuitive** - Mimic natural conversation patterns
✅ **Accessible** - Text-based, emoji-enhanced clarity

---

## 12. Future Enhancements

1. **Natural Language Processing** - Better intent detection
2. **Conversation Memory** - Remember recent interactions
3. **Predictive Suggestions** - Recommend actions
4. **Multi-language Support** - Support other languages
5. **Rich Media** - Handle videos, PDFs, documents
6. **Scheduled Messages** - Remind users of homework
7. **Group Chats** - Study group support
8. **Analytics** - Track conversation patterns

---

## Summary

This conversation logic provides:
- ✅ Clear user states and transitions
- ✅ Intent recognition and routing
- ✅ State-based response generation
- ✅ Data persistence structure
- ✅ Error handling strategy
- ✅ Example conversation flows
- ✅ Template-based responses
- ✅ Scalable architecture

The bot can handle multiple concurrent users with independent conversation states, maintain context across interactions, and gracefully handle errors or unexpected inputs.
