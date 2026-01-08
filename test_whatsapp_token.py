#!/usr/bin/env python3
"""
Test WhatsApp API token validity.
"""
import httpx
import json
import asyncio
from config.settings import settings

async def test_token():
    """Test if the WhatsApp API token is valid."""
    
    print("=" * 80)
    print("TESTING WHATSAPP API TOKEN")
    print("=" * 80)
    
    token = settings.whatsapp_api_key
    phone_id = settings.whatsapp_phone_number_id
    
    print(f"\n📋 Configuration:")
    print(f"   Token starts with: {token[:20]}...")
    print(f"   Token length: {len(token)} characters")
    print(f"   Phone ID: {phone_id}")
    
    if len(token) < 100:
        print(f"\n❌ ERROR: Token is too short ({len(token)} chars), should be 200+")
        print(f"   Token: {token}")
        return
    
    # Test 1: Try to get phone number info
    print(f"\n🔍 Test 1: Validating token by getting phone number info...")
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            url = f"https://graph.facebook.com/v22.0/{phone_id}"
            headers = {
                "Authorization": f"Bearer {token}",
            }
            
            response = await client.get(url, headers=headers)
            
            print(f"   Status: {response.status_code}")
            print(f"   Response: {response.text[:200]}...")
            
            if response.status_code == 200:
                print(f"\n✅ SUCCESS: Token is VALID!")
                data = response.json()
                print(f"   Phone ID: {data.get('id')}")
                print(f"   Phone Number: {data.get('phone_number')}")
                return True
            else:
                print(f"\n❌ FAILED: Token is INVALID")
                try:
                    error_data = response.json()
                    print(f"   Error: {error_data.get('error', {}).get('message')}")
                except:
                    pass
                return False
                
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        return False

if __name__ == "__main__":
    result = asyncio.run(test_token())
