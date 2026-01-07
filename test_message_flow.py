#!/usr/bin/env python3
"""
Test script to verify message tracking flow.
Simulates a WhatsApp message and checks if it gets stored.
"""
import json
import sys
import os
from datetime import datetime

# Add project root to path
sys.path.insert(0, os.path.dirname(__file__))

# Test the message tracking directly
from services.conversation_service import ConversationService
from utils.logger import get_logger

logger = get_logger("test_message_flow")

def test_message_tracking():
    """Test message tracking functionality."""
    phone_number = "+15551234567"
    
    logger.info("=" * 60)
    logger.info("Testing Message Tracking Flow")
    logger.info("=" * 60)
    
    # Get conversation state
    conv_state = ConversationService.get_state(phone_number)
    logger.info(f"Initial state for {phone_number}")
    logger.info(f"  - Has messages: {'messages' in conv_state.get('data', {})}")
    logger.info(f"  - Has last_message: {'last_message' in conv_state.get('data', {})}")
    
    # Simulate adding a user message
    logger.info("\n1. Adding user message...")
    if "messages" not in conv_state["data"]:
        conv_state["data"]["messages"] = []
    
    user_msg = {
        "id": "msg_test_001",
        "phone_number": phone_number,
        "text": "Hello, I need homework help",
        "timestamp": datetime.now().isoformat(),
        "sender_type": "user",
        "message_type": "text"
    }
    conv_state["data"]["messages"].append(user_msg)
    ConversationService.set_data(phone_number, "last_message", user_msg["text"])
    logger.info(f"Added user message: {user_msg['text']}")
    
    # Simulate adding a bot response
    logger.info("\n2. Adding bot response...")
    bot_msg = {
        "id": "msg_test_002",
        "phone_number": phone_number,
        "text": "Sure! I can help you with that. What subject?",
        "timestamp": datetime.now().isoformat(),
        "sender_type": "bot",
        "message_type": "text"
    }
    conv_state["data"]["messages"].append(bot_msg)
    ConversationService.set_data(phone_number, "last_message", bot_msg["text"])
    logger.info(f"Added bot message: {bot_msg['text']}")
    
    # Verify messages are stored
    logger.info("\n3. Verifying messages storage...")
    conv_state = ConversationService.get_state(phone_number)
    messages = conv_state.get("data", {}).get("messages", [])
    last_message = conv_state.get("data", {}).get("last_message")
    
    logger.info(f"Total messages stored: {len(messages)}")
    logger.info(f"Last message: {last_message}")
    
    for i, msg in enumerate(messages, 1):
        logger.info(f"\n  Message {i}:")
        logger.info(f"    - ID: {msg['id']}")
        logger.info(f"    - From: {msg['sender_type']}")
        logger.info(f"    - Text: {msg['text'][:50]}...")
        logger.info(f"    - Time: {msg['timestamp']}")
    
    # Check if messages are accessible
    logger.info("\n4. Checking message accessibility...")
    assert len(messages) == 2, f"Expected 2 messages, got {len(messages)}"
    assert messages[0]["sender_type"] == "user", "First message should be from user"
    assert messages[1]["sender_type"] == "bot", "Second message should be from bot"
    assert last_message == "Sure! I can help you with that. What subject?", "Last message mismatch"
    
    logger.info("\n✅ All tests passed!")
    logger.info("=" * 60)
    
    return True

if __name__ == "__main__":
    try:
        test_message_tracking()
    except Exception as e:
        logger.error(f"❌ Test failed: {str(e)}", exc_info=True)
        sys.exit(1)
