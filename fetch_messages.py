#!/usr/bin/env python
"""Fetch all bot messages from the database"""
import requests
import json

url = 'https://nurturing-exploration-production.up.railway.app/api/messages/list'

try:
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        messages = data.get('data', {}).get('messages', [])
        print(f'\n✅ Successfully pulled {len(messages)} messages from database:\n')
        for i, msg in enumerate(messages, 1):
            print(f'{i:2d}. {msg["message_key"]:35s} | Type: {msg["message_type"]:12s} | Context: {msg["context"]}')
        print('\n')
    else:
        print(f'❌ Error: {response.status_code}')
except Exception as e:
    print(f'❌ Error: {str(e)}')
