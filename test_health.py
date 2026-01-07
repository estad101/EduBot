#!/usr/bin/env python3
"""Test the health endpoint of the deployed application."""
import requests
import time
import sys

def test_health(url: str, max_retries: int = 10, retry_delay: int = 5):
    """
    Test the health endpoint.
    
    Args:
        url: Base URL of the application
        max_retries: Maximum number of retry attempts
        retry_delay: Delay between retries in seconds
    """
    health_endpoint = f"{url}/api/health"
    
    for attempt in range(1, max_retries + 1):
        try:
            print(f"Attempt {attempt}/{max_retries}: Testing {health_endpoint}...")
            response = requests.get(health_endpoint, timeout=10)
            
            if response.status_code == 200:
                print(f"✓ Health check passed!")
                print(f"Response: {response.json()}")
                return True
            else:
                print(f"✗ Status code: {response.status_code}")
                
        except requests.exceptions.ConnectionError:
            print(f"✗ Connection failed - service may not be ready yet")
        except requests.exceptions.Timeout:
            print(f"✗ Request timeout")
        except Exception as e:
            print(f"✗ Error: {e}")
        
        if attempt < max_retries:
            print(f"  Retrying in {retry_delay} seconds...\n")
            time.sleep(retry_delay)
    
    print(f"\n✗ Health check failed after {max_retries} attempts")
    return False

if __name__ == "__main__":
    # Railway production URL
    url = "https://edubot-production-cf26.up.railway.app"
    
    print(f"Testing EduBot deployment at {url}\n")
    success = test_health(url)
    sys.exit(0 if success else 1)
