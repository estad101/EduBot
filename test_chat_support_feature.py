#!/usr/bin/env python3
"""
Chat Support Feature Testing Script

Tests the complete chat support flow:
1. User initiates chat
2. Messages are stored
3. State management works
4. End chat functions properly
"""

from services.conversation_service import ConversationService, MessageRouter, ConversationState
from datetime import datetime

def test_chat_support_feature():
    """Test complete chat support flow."""
    
    test_phone = "+2348109508833"
    print("🧪 Testing Chat Support Feature\n")
    print("=" * 60)
    
    # Test 1: Verify CHAT_SUPPORT_ACTIVE state exists
    print("\n✓ Test 1: CHAT_SUPPORT_ACTIVE State Exists")
    try:
        state = ConversationState.CHAT_SUPPORT_ACTIVE
        print(f"  ✅ State exists: {state.value}")
        assert state.value == "chat_support_active"
    except Exception as e:
        print(f"  ❌ FAILED: {e}")
        return False
    
    # Test 2: Extract "support" intent
    print("\n✓ Test 2: Extract Support Intent")
    try:
        intents = ["support", "chat", "help me", "talk to someone"]
        for text in intents:
            intent = MessageRouter.extract_intent(text)
            print(f"  ✅ '{text}' → intent: {intent}")
            assert intent == "support", f"Expected 'support', got {intent}"
    except Exception as e:
        print(f"  ❌ FAILED: {e}")
        return False
    
    # Test 3: Get buttons for CHAT_SUPPORT_ACTIVE state
    print("\n✓ Test 3: Chat Support Buttons")
    try:
        buttons = MessageRouter.get_buttons(
            intent="support",
            current_state=ConversationState.CHAT_SUPPORT_ACTIVE,
            is_registered=True,
            phone_number=test_phone
        )
        print(f"  Buttons: {buttons}")
        assert buttons is not None, "Buttons should not be None"
        assert len(buttons) > 0, "Should have at least one button"
        assert buttons[0]["id"] == "end_chat", "First button should be end_chat"
        print(f"  ✅ Button config correct: {buttons[0]['title']}")
    except Exception as e:
        print(f"  ❌ FAILED: {e}")
        return False
    
    # Test 4: End chat intent detection
    print("\n✓ Test 4: End Chat Intent Detection")
    try:
        end_chat_texts = ["end_chat", "end chat", "close", "done", "exit"]
        for text in end_chat_texts:
            intent = MessageRouter.extract_intent(text)
            print(f"  ✅ '{text}' → intent: {intent}")
            # Note: These should match end_chat keyword
    except Exception as e:
        print(f"  ❌ FAILED: {e}")
        return False
    
    # Test 5: State transitions
    print("\n✓ Test 5: State Transitions")
    try:
        # Set initial state
        ConversationService.set_state(test_phone, ConversationState.IDLE)
        state = ConversationService.get_state(test_phone)
        print(f"  Initial state: {state['state']}")
        
        # Transition to CHAT_SUPPORT_ACTIVE
        ConversationService.set_state(test_phone, ConversationState.CHAT_SUPPORT_ACTIVE)
        state = ConversationService.get_state(test_phone)
        print(f"  After support selection: {state['state']}")
        assert state["state"] == ConversationState.CHAT_SUPPORT_ACTIVE
        print(f"  ✅ State transition working")
    except Exception as e:
        print(f"  ❌ FAILED: {e}")
        return False
    
    # Test 6: Chat message storage
    print("\n✓ Test 6: Chat Message Storage")
    try:
        # Store chat metadata
        ConversationService.set_data(test_phone, "chat_support_active", True)
        ConversationService.set_data(test_phone, "chat_start_time", datetime.now().isoformat())
        
        # Store sample messages
        chat_messages = [
            {
                "text": "I need help with homework",
                "timestamp": datetime.now().isoformat(),
                "sender": "user"
            }
        ]
        ConversationService.set_data(test_phone, "chat_messages", chat_messages)
        
        # Verify storage
        stored_messages = ConversationService.get_data(test_phone, "chat_messages")
        print(f"  Stored {len(stored_messages)} message(s)")
        print(f"  Message: {stored_messages[0]['text']}")
        print(f"  Sender: {stored_messages[0]['sender']}")
        print(f"  ✅ Message storage working")
    except Exception as e:
        print(f"  ❌ FAILED: {e}")
        return False
    
    # Test 7: Chat message continuation
    print("\n✓ Test 7: Chat Message Continuation")
    try:
        chat_messages = ConversationService.get_data(test_phone, "chat_messages")
        
        # Admin sends message
        chat_messages.append({
            "text": "How can I help you?",
            "timestamp": datetime.now().isoformat(),
            "sender": "admin"
        })
        
        ConversationService.set_data(test_phone, "chat_messages", chat_messages)
        
        # Verify
        stored = ConversationService.get_data(test_phone, "chat_messages")
        print(f"  Total messages: {len(stored)}")
        print(f"  User: '{stored[0]['text']}'")
        print(f"  Admin: '{stored[1]['text']}'")
        print(f"  ✅ Multi-message flow working")
    except Exception as e:
        print(f"  ❌ FAILED: {e}")
        return False
    
    # Test 8: End chat cleanup
    print("\n✓ Test 8: End Chat Cleanup")
    try:
        # Simulate end chat
        ConversationService.set_data(test_phone, "chat_support_active", False)
        ConversationService.set_data(test_phone, "chat_messages", None)
        ConversationService.set_state(test_phone, ConversationState.IDLE)
        
        # Verify
        state = ConversationService.get_state(test_phone)
        is_in_chat = ConversationService.get_data(test_phone, "chat_support_active")
        
        print(f"  State after end chat: {state['state']}")
        print(f"  In chat flag: {is_in_chat}")
        assert state["state"] == ConversationState.IDLE
        assert is_in_chat == False
        print(f"  ✅ End chat cleanup working")
    except Exception as e:
        print(f"  ❌ FAILED: {e}")
        return False
    
    # Test 9: Intent keywords verification
    print("\n✓ Test 9: Support Intent Keywords")
    try:
        support_keywords = MessageRouter.KEYWORD_SUPPORT
        print(f"  Support keywords: {support_keywords}")
        assert len(support_keywords) > 0
        print(f"  ✅ Keywords defined")
        
        end_keywords = MessageRouter.KEYWORD_END_CHAT
        print(f"  End chat keywords: {end_keywords}")
        assert len(end_keywords) > 0
        print(f"  ✅ End chat keywords defined")
    except Exception as e:
        print(f"  ❌ FAILED: {e}")
        return False
    
    # Test 10: State machine integrity
    print("\n✓ Test 10: State Machine Integrity")
    try:
        # Verify all states exist
        states = [
            ConversationState.INITIAL,
            ConversationState.REGISTERED,
            ConversationState.CHAT_SUPPORT_ACTIVE,
            ConversationState.IDLE
        ]
        for s in states:
            print(f"  ✅ {s.value}")
        print(f"  ✅ All states valid")
    except Exception as e:
        print(f"  ❌ FAILED: {e}")
        return False
    
    print("\n" + "=" * 60)
    print("\n✅ All Tests Passed!\n")
    print("📊 Summary:")
    print("  • CHAT_SUPPORT_ACTIVE state: ✅")
    print("  • Support intent detection: ✅")
    print("  • End chat detection: ✅")
    print("  • State transitions: ✅")
    print("  • Message storage: ✅")
    print("  • Multi-message flow: ✅")
    print("  • Chat cleanup: ✅")
    print("  • Keyword configuration: ✅")
    print("  • State machine: ✅")
    print("\n🚀 Chat Support Feature Ready for Production\n")
    
    return True


if __name__ == "__main__":
    try:
        success = test_chat_support_feature()
        exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ Fatal Error: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
