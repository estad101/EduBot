import requests
import sys

url = 'https://edubot-production-0701.up.railway.app/api/health'
print("=" * 70)
print("Testing New Backend")
print("=" * 70)
print(f"\nURL: {url}\n")

try:
    response = requests.get(url, timeout=15, verify=True)
    print(f"✓ Status Code: {response.status_code}")
    print(f"✓ Response: {response.json()}")
    print("\n✅ BACKEND IS RUNNING AND RESPONDING!")
    sys.exit(0)
except requests.exceptions.Timeout:
    print("⏳ Backend is starting up (timeout after 15s)")
    print("   Check again in 30 seconds or view Deploy Logs on Railway")
    sys.exit(1)
except requests.exceptions.ConnectionError as e:
    print(f"✗ Connection Error: {e}")
    print("   Backend may still be deploying...")
    sys.exit(1)
except Exception as e:
    print(f"✗ Error: {e}")
    sys.exit(1)
