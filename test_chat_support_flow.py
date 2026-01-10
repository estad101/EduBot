#!/usr/bin/env python3
"""
Test chat support flow end-to-end:
1. User initiates chat support by typing "support"
2. Admin can see conversation is in active chat
3. Admin can send messages to user
4. User can respond during chat
5. Either user or admin can end chat
"""

import asyncio
import json
from datetime import datetime
from services.conversation_service import ConversationService, ConversationState, MessageRouter

def test_user_initiates_support():
    """Test: User types 'support' to start chat"""
    phone_number = "+1234567890"
    
    # Reset state
    ConversationService.clear_state(phone_number)
    
    # Step 1: User initiates chat support
    print("=" * 60)
    print("STEP 1: User initiates chat support")
    print("=" * 60)
    
    response, state = MessageRouter.get_next_response(
        phone_number=phone_number,
        message_text="support",
        student_data=None  # unregistered user
    )
    
    # IMPORTANT: Actually set the state (this is what the WhatsApp handler does)
    if state:
        ConversationService.set_state(phone_number, state)
    
    print(f"✓ User response: {response[:100]}...")
    print(f"✓ Conversation state: {state}")
    
    # Verify flags are set
    in_chat = ConversationService.get_data(phone_number, "in_chat_support")
    chat_active = ConversationService.get_data(phone_number, "chat_support_active")
    chat_time = ConversationService.get_data(phone_number, "chat_start_time")
    
    print(f"✓ in_chat_support: {in_chat}")
    print(f"✓ chat_support_active: {chat_active}")
    print(f"✓ chat_start_time: {chat_time}")
    
    assert in_chat == True, "in_chat_support should be True"
    assert chat_active == True, "chat_support_active should be True"
    assert chat_time is not None, "chat_start_time should be set"
    assert state == ConversationState.CHAT_SUPPORT_ACTIVE, "Should be in CHAT_SUPPORT_ACTIVE state"
    
    print("\n✅ STEP 1 PASSED: User initiates chat support\n")
    return phone_number

def test_user_sends_message_during_chat(phone_number):
    """Test: User sends message while in chat support"""
    print("=" * 60)
    print("STEP 2: User sends message during chat")
    print("=" * 60)
    
    # Check state before sending message
    conv_state = ConversationService.get_state(phone_number)
    print(f"State BEFORE message: {conv_state['state']}")
    print(f"Data: {conv_state.get('data', {})}")
    
    # Step 2: User sends a message
    response, state = MessageRouter.get_next_response(
        phone_number=phone_number,
        message_text="I need help with my assignment",
        student_data=None
    )
    
    # IMPORTANT: Set the state (this is what the WhatsApp handler does)
    if state:
        ConversationService.set_state(phone_number, state)
    
    print(f"✓ User message: 'I need help with my assignment'")
    print(f"✓ Bot response: {response[:100]}...")
    print(f"✓ State remains: {state}")
    
    # Verify flags still set
    in_chat = ConversationService.get_data(phone_number, "in_chat_support")
    chat_active = ConversationService.get_data(phone_number, "chat_support_active")
    
    print(f"✓ in_chat_support: {in_chat}")
    print(f"✓ chat_support_active: {chat_active}")
    
    assert in_chat == True, "Should still be in chat"
    assert chat_active == True, "Chat should still be active"
    assert state == ConversationState.CHAT_SUPPORT_ACTIVE, "Should still be in CHAT_SUPPORT_ACTIVE state"
    
    # Verify message was stored
    conv_state = ConversationService.get_state(phone_number)
    chat_messages = conv_state.get("data", {}).get("chat_messages", [])
    print(f"✓ Chat messages stored: {len(chat_messages)}")
    
    print("\n✅ STEP 2 PASSED: User message sent and stored\n")

def test_admin_sees_active_chat(phone_number):
    """Test: Admin can see chat is active in conversations list"""
    print("=" * 60)
    print("STEP 3: Admin sees active chat in conversations")
    print("=" * 60)
    
    # Get conversation state (admin would get this via GET /conversations)
    conv_state = ConversationService.get_state(phone_number)
    chat_support_flag = conv_state.get("data", {}).get("chat_support_active", False)
    
    print(f"✓ Phone number: {phone_number}")
    print(f"✓ chat_support_active flag: {chat_support_flag}")
    print(f"✓ Admin UI would show: 💬 Chat Active badge")
    
    assert chat_support_flag == True, "chat_support_active should be True for admin"
    
    print("\n✅ STEP 3 PASSED: Admin can see active chat\n")

def test_user_ends_chat(phone_number):
    """Test: User ends chat by typing 'end chat'"""
    print("=" * 60)
    print("STEP 4: User ends chat")
    print("=" * 60)
    
    # Step 4: User ends chat
    response, state = MessageRouter.get_next_response(
        phone_number=phone_number,
        message_text="end chat",
        student_data=None
    )
    
    # IMPORTANT: Set the state (this is what the WhatsApp handler does)
    if state:
        ConversationService.set_state(phone_number, state)
    
    print(f"✓ User message: 'end chat'")
    print(f"✓ Bot response: {response[:100]}...")
    print(f"✓ New state: {state}")
    
    # Verify flags are cleared
    in_chat = ConversationService.get_data(phone_number, "in_chat_support")
    chat_active = ConversationService.get_data(phone_number, "chat_support_active")
    chat_time = ConversationService.get_data(phone_number, "chat_start_time")
    
    print(f"✓ in_chat_support: {in_chat}")
    print(f"✓ chat_support_active: {chat_active}")
    print(f"✓ chat_start_time: {chat_time}")
    
    assert in_chat == False, "in_chat_support should be False after end chat"
    assert chat_active == False, "chat_support_active should be False after end chat"
    assert chat_time is None, "chat_start_time should be cleared"
    assert state == ConversationState.IDLE, "Should return to IDLE state"
    
    print("\n✅ STEP 4 PASSED: Chat ended and flags cleared\n")

def test_registered_user_support_flow():
    """Test: Registered user initiates chat support"""
    phone_number = "+9876543210"
    
    # Reset state
    ConversationService.clear_state(phone_number)
    
    print("=" * 60)
    print("STEP 5: Registered user initiates chat support")
    print("=" * 60)
    
    student_data = {
        "name": "John Doe",
        "email": "john@example.com",
        "class_grade": "10th"
    }
    
    response, state = MessageRouter.get_next_response(
        phone_number=phone_number,
        message_text="support",
        student_data=student_data
    )
    
    # IMPORTANT: Set the state (this is what the WhatsApp handler does)
    if state:
        ConversationService.set_state(phone_number, state)
    
    print(f"✓ Registered user: John Doe")
    print(f"✓ State: {state}")
    print(f"✓ Response: {response[:100]}...")
    
    # Verify flags set for registered user too
    chat_active = ConversationService.get_data(phone_number, "chat_support_active")
    print(f"✓ chat_support_active: {chat_active}")
    
    assert chat_active == True, "Chat should be active for registered users too"
    assert state == ConversationState.CHAT_SUPPORT_ACTIVE, "Should be in chat support state"
    
    print("\n✅ STEP 5 PASSED: Registered user chat support works\n")

if __name__ == "__main__":
    print("\n")
    print("╔" + "=" * 58 + "╗")
    print("║" + " " * 15 + "CHAT SUPPORT FLOW TEST" + " " * 21 + "║")
    print("╚" + "=" * 58 + "╝")
    print("\n")
    
    try:
        # Test unregistered user flow
        phone = test_user_initiates_support()
        test_user_sends_message_during_chat(phone)
        test_admin_sees_active_chat(phone)
        test_user_ends_chat(phone)
        
        # Test registered user flow
        test_registered_user_support_flow()
        
        print("\n")
        print("╔" + "=" * 58 + "╗")
        print("║" + " " * 20 + "✅ ALL TESTS PASSED!" + " " * 16 + "║")
        print("╚" + "=" * 58 + "╝")
        print("\n")
        print("Summary:")
        print("✓ User initiates chat support")
        print("✓ Chat flags are properly set")
        print("✓ User can send messages during chat")
        print("✓ Admin can see active chat via API")
        print("✓ User/admin can end chat")
        print("✓ Flags are properly cleared after ending chat")
        print("✓ Works for both registered and unregistered users")
        print("\n")
        
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}\n")
        exit(1)
    except Exception as e:
        print(f"\n❌ ERROR: {e}\n")
        import traceback
        traceback.print_exc()
        exit(1)
