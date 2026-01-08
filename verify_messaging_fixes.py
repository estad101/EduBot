#!/usr/bin/env python3
"""
Messaging Logic Verification Script

This script tests the complete messaging logic to ensure all fixes are working.
Run this after deploying to production to verify everything is functional.
"""

import sys
import json
from datetime import datetime
from typing import Dict, Any, Tuple

sys.path.insert(0, '/xampp/htdocs/bot')

from services.conversation_service import MessageRouter, ConversationService, ConversationState

class Colors:
    """ANSI color codes for terminal output."""
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    BOLD = '\033[1m'
    END = '\033[0m'

def print_test(name: str, passed: bool, details: str = ""):
    """Print a test result."""
    symbol = f"{Colors.GREEN}✓{Colors.END}" if passed else f"{Colors.RED}✗{Colors.END}"
    status = f"{Colors.GREEN}PASS{Colors.END}" if passed else f"{Colors.RED}FAIL{Colors.END}"
    print(f"  {symbol} {name:<50} [{status}]")
    if details:
        print(f"      {details}")

def section(title: str):
    """Print a section header."""
    print(f"\n{Colors.BLUE}{Colors.BOLD}{title}{Colors.END}")
    print("-" * 70)

def test_scenario(
    scenario_name: str,
    phone: str,
    initial_state: ConversationState,
    student_data: Dict[str, Any],
    message_text: str,
    button_id: str = None,
    expected_intent: str = None,
    expected_next_state: ConversationState = None,
    check_buttons: bool = False
) -> bool:
    """Test a complete messaging scenario."""
    
    # Reset conversation
    ConversationService.clear_state(phone)
    
    # Set up initial state if needed
    if initial_state:
        ConversationService.set_state(phone, initial_state)
    
    try:
        # Get response from router
        response_data = MessageRouter.get_next_response(
            phone,
            message_text,
            student_data,
            button_id
        )
        
        # Parse response
        if len(response_data) == 3:
            response_text, next_state, button_data = response_data
        else:
            response_text, next_state = response_data
            button_data = None
        
        # Validate response
        checks_passed = True
        
        # Check intent was extracted correctly
        intent = MessageRouter.extract_intent(message_text, button_id)
        if expected_intent and intent != expected_intent:
            print_test(f"{scenario_name} - Intent", False, f"Expected {expected_intent}, got {intent}")
            checks_passed = False
        
        # Check state transition
        if expected_next_state and next_state != expected_next_state:
            print_test(f"{scenario_name} - State", False, f"Expected {expected_next_state}, got {next_state}")
            checks_passed = False
        
        # Check response text
        if not response_text or not response_text.strip():
            print_test(f"{scenario_name} - Response", False, "Response text is empty")
            checks_passed = False
        
        # Check buttons
        if check_buttons:
            if not button_data or "buttons" not in button_data:
                print_test(f"{scenario_name} - Buttons", False, "Expected buttons but none found")
                checks_passed = False
            elif len(button_data.get("buttons", [])) == 0:
                print_test(f"{scenario_name} - Buttons", False, "Button data exists but buttons list is empty")
                checks_passed = False
        
        if checks_passed:
            print_test(scenario_name, True, f"Intent: {intent}, State: {next_state.value if next_state else 'None'}")
        
        return checks_passed
        
    except Exception as e:
        print_test(scenario_name, False, f"Exception: {str(e)}")
        return False
    finally:
        ConversationService.clear_state(phone)

def run_all_tests():
    """Run all messaging tests."""
    
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*70}")
    print("MESSAGING LOGIC VERIFICATION SUITE")
    print(f"{'='*70}{Colors.END}\n")
    
    test_phone = "+2349012345678"
    all_passed = True
    
    # ============ BUTTON ROUTING TESTS ============
    section("1. BUTTON ROUTING TESTS")
    
    test_cases = [
        ("Register Button", ConversationState.INITIAL, None, "", "btn_register", "register", ConversationState.REGISTERING_NAME, False),
        ("Homework Button (Registered)", ConversationState.INITIAL, {"has_subscription": False}, "", "btn_homework", "homework", ConversationState.HOMEWORK_SUBJECT, False),
        ("Subscribe Button", ConversationState.INITIAL, {"has_subscription": False}, "", "btn_pay", "pay", ConversationState.PAYMENT_PENDING, False),  # No buttons in first message
        ("Status Button", ConversationState.INITIAL, {"has_subscription": True}, "", "btn_status", "check", ConversationState.IDLE, False),
        ("Help Button", ConversationState.INITIAL, None, "", "btn_help", "help", ConversationState.IDLE, True),  # Help shows buttons
    ]
    
    for scenario_name, initial, student_data, msg, btn_id, exp_intent, exp_state, check_btn in test_cases:
        result = test_scenario(scenario_name, test_phone, initial, student_data, msg, btn_id, exp_intent, exp_state, check_btn)
        all_passed = all_passed and result
    
    # ============ TEXT-BASED ROUTING TESTS ============
    section("2. TEXT-BASED MESSAGE ROUTING")
    
    test_cases = [
        ("Text: Register", ConversationState.INITIAL, None, "register", None, "register", ConversationState.REGISTERING_NAME, False),
        ("Text: Homework", ConversationState.INITIAL, {"has_subscription": False}, "homework submit", None, "homework", ConversationState.HOMEWORK_SUBJECT, False),
        ("Text: Pay", ConversationState.INITIAL, {"has_subscription": False}, "pay now", None, "pay", ConversationState.PAYMENT_PENDING, False),  # No buttons in first message
        ("Text: Check Status", ConversationState.INITIAL, {"has_subscription": True}, "check status", None, "check", ConversationState.IDLE, False),
        ("Text: Help", ConversationState.INITIAL, None, "help", None, "help", ConversationState.IDLE, True),  # Help shows buttons
    ]
    
    for scenario_name, initial, student_data, msg, btn_id, exp_intent, exp_state, check_btn in test_cases:
        result = test_scenario(scenario_name, test_phone, initial, student_data, msg, btn_id, exp_intent, exp_state, check_btn)
        all_passed = all_passed and result
    
    # ============ HOMEWORK SUBMISSION TESTS ============
    section("3. HOMEWORK TYPE SELECTION")
    
    # Set up homework subject selection
    ConversationService.set_state(test_phone, ConversationState.HOMEWORK_SUBJECT)
    ConversationService.set_data(test_phone, "homework_subject", "Mathematics")
    ConversationService.set_state(test_phone, ConversationState.HOMEWORK_TYPE)
    
    # Test text submission button
    result = test_scenario("Text Submission Button", test_phone, ConversationState.HOMEWORK_TYPE, {"has_subscription": False}, "text", "btn_text", "text_submission", ConversationState.HOMEWORK_CONTENT, False)
    all_passed = all_passed and result
    
    # Test image submission button
    ConversationService.set_state(test_phone, ConversationState.HOMEWORK_TYPE)
    result = test_scenario("Image Submission Button", test_phone, ConversationState.HOMEWORK_TYPE, {"has_subscription": False}, "image", "btn_image", "image_submission", ConversationState.HOMEWORK_CONTENT, False)
    all_passed = all_passed and result
    
    # ============ PAYMENT FLOW TESTS ============
    section("4. PAYMENT FLOW (Confirm/Cancel)")
    
    # Test confirm button
    result = test_scenario("Payment Confirm Button", test_phone, ConversationState.PAYMENT_PENDING, {"has_subscription": False}, "confirm", "btn_confirm", "confirm", ConversationState.PAYMENT_CONFIRMED, False)
    all_passed = all_passed and result
    
    # Test cancel button
    result = test_scenario("Payment Cancel Button", test_phone, ConversationState.PAYMENT_PENDING, {"has_subscription": False}, "cancel", "btn_cancel", "cancel", ConversationState.IDLE, False)
    all_passed = all_passed and result
    
    # ============ BUTTON PRECEDENCE TESTS ============
    section("5. BUTTON PRECEDENCE (Button > Text)")
    
    # Button says register, text says homework - button should win
    ConversationService.clear_state(test_phone)
    intent = MessageRouter.extract_intent("homework", "btn_register")
    passed = intent == "register"
    print_test("Button Precedence (btn_register vs 'homework')", passed, f"Intent: {intent}")
    all_passed = all_passed and passed
    
    # ============ EDGE CASE TESTS ============
    section("6. EDGE CASE HANDLING")
    
    # Empty message, empty button
    intent = MessageRouter.extract_intent("", None)
    passed = intent == "unknown"
    print_test("Empty Message (No Button)", passed, f"Intent: {intent}")
    all_passed = all_passed and passed
    
    # Non-existent button ID
    intent = MessageRouter.extract_intent("", "btn_nonexistent")
    passed = intent == "unknown"
    print_test("Non-existent Button ID", passed, f"Intent: {intent}")
    all_passed = all_passed and passed
    
    # Mixed case button ID
    intent = MessageRouter.extract_intent("", "BTN_REGISTER")
    passed = intent == "register"
    print_test("Mixed Case Button ID", passed, f"Intent: {intent}")
    all_passed = all_passed and passed
    
    # ============ FINAL RESULTS ============
    section("FINAL RESULTS")
    
    if all_passed:
        print(f"{Colors.GREEN}{Colors.BOLD}✓ ALL TESTS PASSED{Colors.END}")
        print(f"\n{Colors.GREEN}The messaging logic is working correctly!{Colors.END}")
        return 0
    else:
        print(f"{Colors.RED}{Colors.BOLD}✗ SOME TESTS FAILED{Colors.END}")
        print(f"\n{Colors.RED}Please review the failed tests above.{Colors.END}")
        return 1

if __name__ == "__main__":
    try:
        exit_code = run_all_tests()
        sys.exit(exit_code)
    except Exception as e:
        print(f"\n{Colors.RED}Fatal Error: {str(e)}{Colors.END}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
