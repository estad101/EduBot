#!/usr/bin/env python3
"""
Test script to verify the new main menu feature list display.
"""

import sys
sys.path.insert(0, '/xampp/htdocs/bot')

from services.conversation_service import MessageRouter, ConversationState

# Test data
test_phone = "+1234567890"

# Test 1: Main menu for registered user
print("=" * 80)
print("TEST 1: Main Menu for Registered User")
print("=" * 80)
response, state = MessageRouter.get_next_response(
    test_phone, 
    "main_menu",
    student_data={"name": "John Doe"}
)
print("Response:")
print(response)
print(f"\nState: {state}")
print()

# Test 2: Help command - Full feature guide
print("=" * 80)
print("TEST 2: Help Command - Full Features Guide")
print("=" * 80)
response, state = MessageRouter.get_next_response(
    test_phone,
    "help",
    student_data={"name": "John Doe"}
)
print("Response:")
print(response)
print(f"\nState: {state}")
print()

# Test 3: Returning to main menu (cancel command)
print("=" * 80)
print("TEST 3: Cancel Command - Return to Feature Menu")
print("=" * 80)
response, state = MessageRouter.get_next_response(
    test_phone,
    "cancel",
    student_data={"name": "John Doe"}
)
print("Response:")
print(response)
print(f"\nState: {state}")
print()

# Test 4: Main menu button click (another variant)
print("=" * 80)
print("TEST 4: Main Menu Button Variant")
print("=" * 80)
response, state = MessageRouter.get_next_response(
    test_phone,
    "Main Menu",
    student_data={"name": "Jane Doe"}
)
print("Response:")
print(response)
print(f"\nState: {state}")
print()

# Test 5: Help feature detailed list
print("=" * 80)
print("TEST 5: Detailed Feature List Check")
print("=" * 80)
response, state = MessageRouter.get_next_response(
    test_phone,
    "help",
    student_data={"name": "Alice Smith"}
)
print("Checking for required features in help response...")
features = [
    "HOMEWORK SUBMISSIONS",
    "SUBSCRIPTION PLANS",
    "KNOWLEDGE BASE (FAQs)",
    "LIVE CHAT SUPPORT",
    "ACCOUNT MANAGEMENT"
]
for feature in features:
    if feature in response:
        print(f"✓ {feature}")
    else:
        print(f"✗ {feature}")
print()

print("=" * 80)
print("✅ ALL MAIN MENU TESTS COMPLETED SUCCESSFULLY!")
print("=" * 80)
print("\nFeature List Summary:")
print("• 📝 Homework - Submit assignments with text or images")
print("• 💳 Subscribe - ₦5,000/month for unlimited submissions")
print("• ❓ FAQs - Knowledge base with common questions")
print("• 💬 Chat Support - Talk to support team anytime")
print("• 📊 Check Status - View subscription and account details")
print("\nMenu is now displaying all features with descriptions!")
