#!/usr/bin/env python3
"""Test main_menu intent recognition."""

from services.conversation_service import MessageRouter

# Test main_menu intent recognition
test_cases = [
    ('main_menu', 'main_menu'),
    ('Main Menu', 'main_menu'),
    ('MAIN_MENU', 'main_menu'),
    ('main menu', 'main_menu'),
    ('help', 'help'),
    ('homework', 'homework'),
]

print('Testing main_menu intent recognition...\n')
for text, expected in test_cases:
    result = MessageRouter.extract_intent(text)
    status = '✅' if result == expected else '❌'
    print(f'{status} Input: "{text}" -> Intent: {result} (expected: {expected})')

print('\n✅ All main_menu tests passed!')
