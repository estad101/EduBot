#!/usr/bin/env python
"""Query bot messages directly from local database"""
import os
import sys
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Add the project root to path
sys.path.insert(0, '/xampp/htdocs/bot')

from models.bot_message import BotMessage

# Get database URL from environment
db_url = os.getenv('DATABASE_URL')
if not db_url:
    print("❌ DATABASE_URL environment variable not set")
    sys.exit(1)

try:
    engine = create_engine(db_url)
    Session = sessionmaker(bind=engine)
    session = Session()
    
    # Query all messages
    messages = session.query(BotMessage).all()
    
    print(f'\n✅ Successfully pulled {len(messages)} messages from database:\n')
    for i, msg in enumerate(messages, 1):
        print(f'{i:2d}. {msg.message_key:35s} | Type: {msg.message_type:12s} | Context: {msg.context}')
    print('\n')
    
except Exception as e:
    print(f'❌ Error: {str(e)}')
