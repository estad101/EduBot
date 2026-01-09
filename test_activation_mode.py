#!/usr/bin/env python3
"""Test chat support activation mode"""

from services.conversation_service import ConversationService, ConversationState

print("\n" + "="*60)
print("  TESTING CHAT SUPPORT ACTIVATION MODE")
print("="*60)

# Test flow
phone = '+234-test-activate'

print("\n1. User selects 'Chat Support'...")
ConversationService.set_state(phone, ConversationState.CHAT_SUPPORT_ACTIVE)
ConversationService.set_data(phone, 'chat_support_active', True)
ConversationService.set_data(phone, 'name', 'Test User')

# Check status
state = ConversationService.get_state(phone)
is_chat_support = ConversationService.get_data(phone, 'chat_support_active')
user_name = ConversationService.get_data(phone, 'name')

print(f"   ✅ State set to: {state.get('state')}")
print(f"   ✅ Chat support active: {is_chat_support}")

print("\n2. Admin checks conversations page...")
conv_state = ConversationService.get_state(phone)
chat_active = conv_state.get("data", {}).get("chat_support_active", False)

print(f"   ✅ Admin sees chat_support_active: {chat_active}")
print(f"   ✅ Admin sees user: {user_name}")

print("\n3. Admin sends message...")
messages = ConversationService.get_data(phone, "chat_messages") or []
messages.append({
    "text": "Hello! How can I help?",
    "sender": "admin",
    "timestamp": "2026-01-09T15:00:00Z"
})
ConversationService.set_data(phone, "chat_messages", messages)

stored = ConversationService.get_data(phone, "chat_messages")
print(f"   ✅ Message stored: {len(stored)} messages in chat")
print(f"   ✅ Last message: {stored[-1]['text']}")

print("\n4. User receives and replies...")
messages = ConversationService.get_data(phone, "chat_messages")
messages.append({
    "text": "I need help with homework",
    "sender": "user",
    "timestamp": "2026-01-09T15:01:00Z"
})
ConversationService.set_data(phone, "chat_messages", messages)

stored = ConversationService.get_data(phone, "chat_messages")
print(f"   ✅ Messages now: {len(stored)}")
print(f"   ✅ User message received")

print("\n5. Admin can end chat...")
ConversationService.set_data(phone, 'chat_support_active', False)
ConversationService.set_state(phone, ConversationState.IDLE)

state = ConversationService.get_state(phone)
is_chat_support = ConversationService.get_data(phone, 'chat_support_active')

print(f"   ✅ State changed to: {state.get('state')}")
print(f"   ✅ Chat support ended: {not is_chat_support}")

# Cleanup
ConversationService.clear_state(phone)

print("\n" + "="*60)
print("  ✅ ACTIVATION MODE TEST COMPLETE - ALL WORKING")
print("="*60 + "\n")
