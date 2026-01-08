"""
Test script to validate the messaging logic of the bot.

Tests:
1. Button ID extraction and routing
2. Intent detection with buttons
3. Conversation state transitions
4. Message type handling
"""
import sys
sys.path.insert(0, '/xampp/htdocs/bot')

from services.conversation_service import MessageRouter, ConversationService, ConversationState

def test_button_intent_extraction():
    """Test that button IDs are properly extracted as intents."""
    print("Testing button ID intent extraction...")
    
    test_cases = [
        ("btn_register", None, "register"),
        ("btn_homework", None, "homework"),
        ("btn_pay", None, "pay"),
        ("btn_status", None, "check"),
        ("btn_confirm", None, "confirm"),
        ("btn_text", None, "text_submission"),
        ("btn_image", None, "image_submission"),
        ("btn_cancel", None, "cancel"),
    ]
    
    for button_id, message_text, expected_intent in test_cases:
        intent = MessageRouter.extract_intent(message_text or "", button_id)
        status = "✓" if intent == expected_intent else "✗"
        print(f"  {status} Button ID: {button_id} -> Intent: {intent} (expected: {expected_intent})")
        assert intent == expected_intent, f"Expected {expected_intent}, got {intent}"

def test_text_intent_extraction():
    """Test that text-based intents work without button IDs."""
    print("\nTesting text-based intent extraction...")
    
    test_cases = [
        ("register", "register"),
        ("homework submit", "homework"),
        ("pay now", "pay"),
        ("check status", "check"),
        ("confirm payment", "confirm"),
        ("image submission", "image_submission"),
        ("cancel", "cancel"),
    ]
    
    for message_text, expected_intent in test_cases:
        intent = MessageRouter.extract_intent(message_text, None)
        status = "✓" if intent == expected_intent else "✗"
        print(f"  {status} Text: '{message_text}' -> Intent: {intent} (expected: {expected_intent})")
        assert intent == expected_intent, f"Expected {expected_intent}, got {intent}"

def test_button_takes_precedence():
    """Test that button ID takes precedence over message text."""
    print("\nTesting button precedence over text...")
    
    # Button says "register" but text says "homework"
    intent = MessageRouter.extract_intent("homework", "btn_register")
    status = "✓" if intent == "register" else "✗"
    print(f"  {status} Button: btn_register, Text: 'homework' -> Intent: {intent} (should use button)")
    assert intent == "register", "Button should take precedence"

def test_homework_type_detection():
    """Test homework type (TEXT vs IMAGE) detection from buttons."""
    print("\nTesting homework type detection...")
    
    # Test with button ID
    phone = "+2349012345678"
    
    # Set up initial state
    ConversationService.set_state(phone, ConversationState.HOMEWORK_TYPE)
    ConversationService.set_data(phone, "homework_subject", "Mathematics")
    
    # Get response for button click
    response_text, next_state = MessageRouter.get_next_response(
        phone,
        "Image",  # Fallback text
        None,
        button_id="btn_image"  # Button ID should take precedence
    )
    
    # Check that submission type was set to IMAGE
    submission_type = ConversationService.get_data(phone, "homework_type")
    status = "✓" if submission_type == "IMAGE" else "✗"
    print(f"  {status} Button click (btn_image) -> Type: {submission_type} (expected: IMAGE)")
    assert submission_type == "IMAGE", f"Expected IMAGE, got {submission_type}"
    
    # Clear state
    ConversationService.clear_state(phone)

def test_payment_confirmation():
    """Test payment confirmation with button clicks."""
    print("\nTesting payment confirmation...")
    
    phone = "+2349012345678"
    
    # Set up payment pending state
    ConversationService.set_state(phone, ConversationState.PAYMENT_PENDING)
    
    # Confirm button click
    response_text, next_state = MessageRouter.get_next_response(
        phone,
        "Confirm",
        None,
        button_id="btn_confirm"
    )
    
    status = "✓" if next_state == ConversationState.PAYMENT_CONFIRMED else "✗"
    print(f"  {status} Confirm button -> State: {next_state} (expected: PAYMENT_CONFIRMED)")
    assert next_state == ConversationState.PAYMENT_CONFIRMED
    
    # Cancel button click (reset state first)
    ConversationService.set_state(phone, ConversationState.PAYMENT_PENDING)
    response_text, next_state = MessageRouter.get_next_response(
        phone,
        "Cancel",
        None,
        button_id="btn_cancel"
    )
    
    status = "✓" if next_state == ConversationState.IDLE else "✗"
    print(f"  {status} Cancel button -> State: {next_state} (expected: IDLE)")
    assert next_state == ConversationState.IDLE
    
    # Clear state
    ConversationService.clear_state(phone)

def test_initial_state_buttons():
    """Test main menu buttons in INITIAL/IDLE state."""
    print("\nTesting initial state button routing...")
    
    phone = "+2349012345678"
    
    # Test register button
    response_text, next_state = MessageRouter.get_next_response(
        phone,
        "",
        None,
        button_id="btn_register"
    )
    
    status = "✓" if next_state == ConversationState.REGISTERING_NAME else "✗"
    print(f"  {status} Register button -> State: {next_state} (expected: REGISTERING_NAME)")
    assert next_state == ConversationState.REGISTERING_NAME
    
    # Test homework button (requires registration)
    ConversationService.clear_state(phone)
    response_text, next_state = MessageRouter.get_next_response(
        phone,
        "",
        None,  # No student data = not registered
        button_id="btn_homework"
    )
    
    status = "✓" if next_state == ConversationState.IDLE else "✗"
    print(f"  {status} Homework button (not registered) -> Shows error, State: {next_state}")
    
    # Test with registered student
    ConversationService.clear_state(phone)
    response_text, next_state = MessageRouter.get_next_response(
        phone,
        "",
        {"has_subscription": False},  # Registered
        button_id="btn_homework"
    )
    
    status = "✓" if next_state == ConversationState.HOMEWORK_SUBJECT else "✗"
    print(f"  {status} Homework button (registered) -> State: {next_state} (expected: HOMEWORK_SUBJECT)")
    assert next_state == ConversationState.HOMEWORK_SUBJECT
    
    # Clear state
    ConversationService.clear_state(phone)

def main():
    """Run all tests."""
    print("=" * 60)
    print("Testing Messaging Logic")
    print("=" * 60)
    
    try:
        test_button_intent_extraction()
        test_text_intent_extraction()
        test_button_takes_precedence()
        test_homework_type_detection()
        test_payment_confirmation()
        test_initial_state_buttons()
        
        print("\n" + "=" * 60)
        print("✅ All tests passed!")
        print("=" * 60)
        return 0
    except AssertionError as e:
        print(f"\n❌ Test failed: {str(e)}")
        return 1
    except Exception as e:
        print(f"\n❌ Unexpected error: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())
