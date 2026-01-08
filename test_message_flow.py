#!/usr/bin/env python3
"""
Test the complete message flow for WhatsApp bot.
Validates: phone number → message routing → response generation → button creation
"""
import sys
import os
import logging
from datetime import datetime

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_message_flow():
    """Test the complete message flow."""
    print("\n" + "="*70)
    print("🧪 WHATSAPP MESSAGE FLOW TEST")
    print("="*70)
    
    test_phone_number = "+2348123456789"
    test_message = "Hello"
    
    # Import services
    try:
        from services.conversation_service import MessageRouter, ConversationService, ConversationState
        print("✅ Imported ConversationService and MessageRouter")
    except Exception as e:
        print(f"❌ Failed to import: {str(e)}")
        return False
    
    print("\n" + "-"*70)
    print("1️⃣ Test: Extract Intent from Message")
    print("-"*70)
    try:
        intent = MessageRouter.extract_intent(test_message)
        print(f"   Input message: '{test_message}'")
        print(f"   ✅ Extracted intent: '{intent}'")
    except Exception as e:
        print(f"   ❌ Error extracting intent: {str(e)}")
        return False
    
    print("\n" + "-"*70)
    print("2️⃣ Test: Get Next Response from MessageRouter")
    print("-"*70)
    try:
        response_text, next_state = MessageRouter.get_next_response(
            phone_number=test_phone_number,
            message_text=test_message,
            student_data=None
        )
        print(f"   Input: phone={test_phone_number}, message='{test_message}'")
        print(f"   ✅ Response text: {response_text[:100]}...")
        print(f"   ✅ Next state: {next_state}")
        
        if not response_text:
            print(f"   ⚠️  WARNING: Response text is empty!")
            return False
    except Exception as e:
        print(f"   ❌ Error getting response: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    
    print("\n" + "-"*70)
    print("3️⃣ Test: Get Buttons for State")
    print("-"*70)
    try:
        buttons = MessageRouter.get_buttons(
            intent=intent,
            current_state=next_state or ConversationState.IDLE,
            is_registered=False,
            phone_number=test_phone_number
        )
        
        if buttons:
            print(f"   State: {next_state or ConversationState.IDLE}")
            print(f"   ✅ Got {len(buttons)} buttons:")
            for btn in buttons:
                print(f"      - {btn.get('title')} (id: {btn.get('id')})")
        else:
            print(f"   ⚠️  State: {next_state or ConversationState.IDLE}")
            print(f"   ℹ️  No buttons for this state (text-only response)")
    except Exception as e:
        print(f"   ❌ Error getting buttons: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    
    print("\n" + "-"*70)
    print("4️⃣ Test: Menu State Persistence")
    print("-"*70)
    try:
        # Set menu state
        ConversationService.set_data(test_phone_number, "menu_state", "homework_menu")
        menu_state = ConversationService.get_data(test_phone_number, "menu_state")
        print(f"   Set menu_state to: 'homework_menu'")
        print(f"   ✅ Retrieved menu_state: '{menu_state}'")
        
        # Get buttons with homework menu active
        buttons = MessageRouter.get_buttons(
            intent=intent,
            current_state=ConversationState.IDLE,
            is_registered=False,
            phone_number=test_phone_number
        )
        
        if buttons and buttons[0]['id'] == 'homework':
            print(f"   ✅ Menu toggle works - showing homework menu")
            for btn in buttons:
                print(f"      - {btn.get('title')}")
        else:
            print(f"   ⚠️  Menu toggle issue - not showing homework menu")
            if buttons:
                print(f"   Current buttons:")
                for btn in buttons:
                    print(f"      - {btn.get('title')}")
    except Exception as e:
        print(f"   ❌ Error testing menu state: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    
    print("\n" + "-"*70)
    print("5️⃣ Test: All Intent Handlers")
    print("-"*70)
    
    test_intents = [
        ("hello", "greeting"),
        ("homework", "homework intent"),
        ("faq", "FAQ intent"),
        ("support", "support intent"),
        ("register", "registration intent"),
        ("pay", "payment intent"),
        ("help", "help intent"),
    ]
    
    all_ok = True
    for test_input, description in test_intents:
        try:
            response_text, next_state = MessageRouter.get_next_response(
                phone_number=test_phone_number,
                message_text=test_input,
                student_data=None
            )
            
            if response_text:
                print(f"   ✅ {description:20} → Response OK ({len(response_text)} chars)")
            else:
                print(f"   ❌ {description:20} → No response text!")
                all_ok = False
        except Exception as e:
            print(f"   ❌ {description:20} → Error: {str(e)}")
            all_ok = False
    
    if not all_ok:
        return False
    
    print("\n" + "="*70)
    print("✅ ALL TESTS PASSED - Message flow is working correctly!")
    print("="*70 + "\n")
    return True


if __name__ == "__main__":
    success = test_message_flow()
    sys.exit(0 if success else 1)

