#!/usr/bin/env python3
"""
Debug WhatsApp API token - detailed testing
"""
import httpx
import json
from urllib.parse import quote

# Your token
token = "EAAckpQFzzTUBQa7fNBSkrrmAOynrz5SdZAX6GwZB50SkV0rQKlKJ6IuiPSFOVEcu2NkbKR2fhiLjMvP13Co8mMZCAHinYkhE4BZA5KWIafLa0Nsv46VyZBuyVq3XcJp356LOc07As2FlMxdDIjWRuHsgPzWDaNPhemkIrr4Y2ZAdKVKcYTRPbgJAsXk2ZAT8QZDZD"
phone_id = "797467203457022"

print("=" * 80)
print("WHATSAPP API TOKEN DEBUG")
print("=" * 80)

print(f"\n📋 Token Analysis:")
print(f"   Length: {len(token)} characters")
print(f"   Starts with: {token[:20]}")
print(f"   Ends with: {token[-20:]}")
print(f"   Contains special chars: {any(c in token for c in '!@#$%^&*()[]{}|;:,.<>?/')}")

# Test 1: Basic info request
print(f"\n🔍 Test 1: GET /{phone_id} (get phone number info)")
try:
    response = httpx.get(
        f"https://graph.instagram.com/v18.0/{phone_id}",
        headers={"Authorization": f"Bearer {token}"},
        timeout=30
    )
    print(f"   Status: {response.status_code}")
    print(f"   Response: {response.text}")
except Exception as e:
    print(f"   Error: {e}")

# Test 2: Me endpoint
print(f"\n🔍 Test 2: GET /me (test with Bearer token)")
try:
    response = httpx.get(
        f"https://graph.instagram.com/v18.0/me",
        headers={"Authorization": f"Bearer {token}"},
        timeout=30
    )
    print(f"   Status: {response.status_code}")
    print(f"   Response: {response.text}")
except Exception as e:
    print(f"   Error: {e}")

# Test 3: Check if token is URL-encoded properly
print(f"\n🔍 Test 3: Testing with token as URL parameter")
try:
    response = httpx.get(
        f"https://graph.instagram.com/v18.0/{phone_id}?access_token={token}",
        timeout=30
    )
    print(f"   Status: {response.status_code}")
    print(f"   Response: {response.text[:200]}")
except Exception as e:
    print(f"   Error: {e}")

print("\n" + "=" * 80)
