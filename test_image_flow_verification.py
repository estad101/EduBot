#!/usr/bin/env python3
"""
Test script to verify image homework upload flow is 100% working.
"""

from services.conversation_service import MessageRouter, ConversationState, ConversationService
import json

def test_image_flow():
    """Test the complete image homework submission flow."""
    print("\n" + "="*70)
    print("🧪 TESTING IMAGE UPLOAD FLOW - 100% VERIFICATION")
    print("="*70)
    
    phone_number = "+2347001234567"
    student_data = {
        "status": "RETURNING_USER",
        "student_id": 1,
        "phone_number": phone_number,
        "user_status": "ACTIVE_SUBSCRIBER",
        "name": "Test Student",
        "email": "test@example.com",
        "has_subscription": True,
    }
    
    # Clear any previous state
    ConversationService.clear_state(phone_number)
    ConversationService.set_state(phone_number, ConversationState.REGISTERED)
    
    tests = [
        {
            "name": "User selects Homework",
            "current_state": ConversationState.REGISTERED,
            "message": "homework",
            "expected_state": ConversationState.HOMEWORK_SUBJECT,
            "expected_in_response": "subject",
        },
        {
            "name": "User provides subject",
            "current_state": ConversationState.HOMEWORK_SUBJECT,
            "message": "Mathematics",
            "expected_state": ConversationState.HOMEWORK_TYPE,
            "expected_in_response": "submit",
        },
        {
            "name": "User selects Image submission type",
            "current_state": ConversationState.HOMEWORK_TYPE,
            "message": "image",
            "expected_state": ConversationState.HOMEWORK_CONTENT,
            "expected_in_response": "Image",
        },
        {
            "name": "User sends content (simulating image message)",
            "current_state": ConversationState.HOMEWORK_CONTENT,
            "message": "test_image_content",
            "expected_state": ConversationState.HOMEWORK_SUBMITTED,
            "expected_in_response": "Processing",
        },
        {
            "name": "User clicks Main Menu from homework submitted state",
            "current_state": ConversationState.HOMEWORK_SUBMITTED,
            "message": "main_menu",
            "expected_state": ConversationState.REGISTERED,
            "expected_in_response": "Welcome",
        },
    ]
    
    print("\n📋 Test Sequence:")
    for i, test in enumerate(tests, 1):
        print(f"   {i}. {test['name']}")
    
    print("\n" + "-"*70)
    
    # Run tests
    all_pass = True
    for i, test in enumerate(tests, 1):
        print(f"\n✓ Test {i}: {test['name']}")
        print(f"  Current State: {test['current_state'].value}")
        print(f"  Message: {test['message']}")
        
        # Set current state
        ConversationService.set_state(phone_number, test['current_state'])
        
        # Get response
        response_text, next_state = MessageRouter.get_next_response(
            phone_number=phone_number,
            message_text=test['message'],
            student_data=student_data,
        )
        
        # Check state
        state_ok = next_state == test['expected_state']
        print(f"  Next State: {next_state.value} {'✅' if state_ok else '❌'}")
        
        # Check response contains expected text
        response_ok = test['expected_in_response'].lower() in response_text.lower()
        print(f"  Response Contains '{test['expected_in_response']}': {'✅' if response_ok else '❌'}")
        
        if not state_ok:
            print(f"  ❌ FAILED: Expected state {test['expected_state'].value}")
            all_pass = False
        if not response_ok:
            print(f"  ❌ FAILED: Expected '{test['expected_in_response']}' in response")
            print(f"  Response: {response_text[:100]}...")
            all_pass = False
    
    print("\n" + "-"*70)
    print("\n✅ IMAGE UPLOAD FLOW TESTS COMPLETE")
    
    # Check intent recognition
    print("\n" + "="*70)
    print("🧪 TESTING INTENT RECOGNITION FOR IMAGE")
    print("="*70)
    
    intent_tests = [
        ("image", "image"),
        ("Image", "image"),
        ("IMAGE", "image"),
        ("📷", "image"),
        ("text", "text"),
        ("Text", "text"),
        ("TEXT", "text"),
    ]
    
    print("\n📋 Intent Recognition Tests:")
    for message, expected_intent in intent_tests:
        intent = MessageRouter.extract_intent(message)
        passed = intent == expected_intent
        status = "✅" if passed else "❌"
        print(f"  {status} Message: '{message}' → Intent: {intent} (expected: {expected_intent})")
        if not passed:
            all_pass = False
    
    print("\n" + "="*70)
    if all_pass:
        print("✅ ALL IMAGE UPLOAD TESTS PASSED - 100% WORKING")
    else:
        print("❌ SOME TESTS FAILED - CHECK LOGS")
    print("="*70)

if __name__ == "__main__":
    test_image_flow()
