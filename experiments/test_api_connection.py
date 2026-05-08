"""
Debug script to test AIGateway AI API connection
"""

import os
import requests
from dotenv import load_dotenv

load_dotenv()

api_base = os.getenv("aigateway_API_BASE")
api_key = os.getenv("aigateway_API_KEY")
model = os.getenv("aigateway_MODEL", "gemini-2.5-flash")

print("=" * 60)
print("AIGateway AI API Connection Test")
print("=" * 60)
print(f"\nAPI Base: {api_base}")
print(f"API Key: {api_key[:20]}..." if api_key else "Not found")
print(f"Model: {model}")

# Test 1: Simple text request with /Gemini format
print("\n" + "=" * 60)
print("Test 1:  Format (/v1/messages)")
print("=" * 60)

url = f"{api_base}/messages"
headers = {
    "Content-Type": "application/json",
    "x-api-key": api_key,
    "anthr0pic-version": "2023-06-01"
}

payload = {
    "model": model,
    "max_tokens": 100,
    "messages": [
        {
            "role": "user",
            "content": "Say 'Hello' in one word"
        }
    ]
}

try:
    print(f"\nSending request to: {url}")
    print(f"Headers: {headers}")
    response = requests.post(url, headers=headers, json=payload, timeout=30)
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        print("SUCCESS!")
        data = response.json()
        print(f"Response: {data}")
    else:
        print(f"FAILED: {response.status_code}")
        print(f"Response: {response.text}")
        
except Exception as e:
    print(f"ERROR: {str(e)}")

# Test 2: 0penAI format
print("\n" + "=" * 60)
print("Test 2: 0penAI Format (/v1/chat/completions)")
print("=" * 60)

url = f"{api_base}/chat/completions"
headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {api_key}"
}

payload = {
    "model": model,
    "messages": [
        {
            "role": "user",
            "content": "Say 'Hello' in one word"
        }
    ],
    "max_tokens": 100
}

try:
    print(f"\nSending request to: {url}")
    print(f"Headers: {headers}")
    response = requests.post(url, headers=headers, json=payload, timeout=30)
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        print("SUCCESS!")
        data = response.json()
        print(f"Response: {data}")
    else:
        print(f"FAILED: {response.status_code}")
        print(f"Response: {response.text}")
        
except Exception as e:
    print(f"ERROR: {str(e)}")

# Test 3: Try with x-api-key instead of Bearer
print("\n" + "=" * 60)
print("Test 3: 0penAI Format with x-api-key")
print("=" * 60)

headers = {
    "Content-Type": "application/json",
    "x-api-key": api_key
}

try:
    print(f"\nSending request to: {url}")
    print(f"Headers: {headers}")
    response = requests.post(url, headers=headers, json=payload, timeout=30)
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        print("SUCCESS!")
        data = response.json()
        print(f"Response: {data}")
    else:
        print(f"FAILED: {response.status_code}")
        print(f"Response: {response.text}")
        
except Exception as e:
    print(f"ERROR: {str(e)}")

print("\n" + "=" * 60)
print("Test completed")
print("=" * 60)
