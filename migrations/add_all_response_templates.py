#!/usr/bin/env python
"""Add templates for all major bot responses."""
import sys
sys.path.insert(0, '/xampp/htdocs/bot')

from config.database import SessionLocal
from models.bot_message import BotMessageTemplate
from datetime import datetime

# Templates to create
TEMPLATES = {
    "help_main": {
        "content": """[?] Help & Features

[Book] HOMEWORK SUBMISSION
• Submit text or images easily
• Get detailed tutor feedback within 24 hours
• Track all your submissions in one place

[Card] PAYMENT OPTIONS
• FREE: Per-submission payment model
• PREMIUM: 5000/month for unlimited submissions
• BONUS: Priority support for subscribers

[Question] KNOWLEDGE BASE (FAQs)
• Registration guide: How to create your account
• Homework help: Submission tips and limits
• Payment info: Accepted methods and refund policy
• Subscription details: Plans and benefits

[Chat] LIVE CHAT SUPPORT
• Talk directly with our support team
• Available for all account types
• Quick responses to your questions

[Info] ACCOUNT MANAGEMENT
• Check your subscription status anytime
• View your submission history
• Track tutor feedback

Ready to get started? Choose an option above!"""
    },
    "support_welcome": {
        "content": """[Chat] Welcome to Chat Support!

Thanks for reaching out. Our support team will respond shortly.

In the meantime, here are quick answers to common questions:
• How do I submit homework? Go to the [Book] Homework section
• What's the pricing? Check the [Card] Subscribe section
• I need help - Try the [?] Help menu

Type your message below and we'll get back to you soon!"""
    },
    "homework_subject": {
        "content": """[Book] What subject is your homework for?

Choose from these common subjects:
1. Mathematics
2. English
3. Science
4. History
5. Economics
6. Other

Just type the subject name or number!"""
    },
    "homework_type": {
        "content": """[Book] How would you like to submit?

[Text] TEXT - Type your homework
[Img] IMAGE - Take a photo or upload image

Which option works best for you?"""
    },
    "payment_info": {
        "content": """[Card] Choose Your Plan

[Free] FREE PLAN
• 5 free submissions per month
• Standard support
• 24-48 hour tutor response

[Premium] PREMIUM PLAN - 5000/month
• Unlimited submissions
• Priority support
• 12-24 hour tutor response
• Exclusive learning resources

Ready to upgrade? Tap [Premium] above!"""
    },
    "subscription_details": {
        "content": """[Star] Subscription Plans

[Pen] ACTIVE SUBSCRIBER
You have unlimited homework submissions!

[Check] BILLING INFO
Next billing date: Check your account

[Pause] PAUSE SUBSCRIPTION
Need a break? You can pause anytime.

[Stop] CANCEL SUBSCRIPTION
Your subscription can be cancelled anytime.

Need help? Use [Chat] Chat Support!"""
    },
    "status_not_subscribed": {
        "content": """[Info] Your Account Status

[User] NAME: {full_name}
[Mail] EMAIL: {email}
[Graduation] CLASS: {class}

[Free] PLAN: Free (5 submissions/month)
[Clock] SUBMISSIONS LEFT: {submissions_left}

Want unlimited access? Tap [Card] Subscribe!"""
    },
    "status_subscribed": {
        "content": """[Info] Your Account Status

[User] NAME: {full_name}
[Mail] EMAIL: {email}
[Graduation] CLASS: {class}

[Premium] PLAN: Premium Subscriber
[Unlimited] SUBMISSIONS: Unlimited!
[Check] VALID UNTIL: {subscription_end}

Thank you for your support! [Heart]"""
    },
}

db = SessionLocal()
try:
    created = 0
    updated = 0
    
    for template_name, template_data in TEMPLATES.items():
        existing = db.query(BotMessageTemplate).filter(
            BotMessageTemplate.template_name == template_name
        ).first()
        
        if existing:
            existing.template_content = template_data["content"]
            existing.updated_at = datetime.utcnow()
            updated += 1
            print(f"✓ Updated template: {template_name}")
        else:
            template = BotMessageTemplate(
                template_name=template_name,
                template_content=template_data["content"],
                is_default=True,
                variables=[]
            )
            db.add(template)
            created += 1
            print(f"✓ Created template: {template_name}")
    
    db.commit()
    print(f"\n✓ Migration complete: {created} created, {updated} updated")
    
except Exception as e:
    print(f"✗ Error: {e}")
    import traceback
    traceback.print_exc()
    db.rollback()
finally:
    db.close()
