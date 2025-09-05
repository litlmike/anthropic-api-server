#!/usr/bin/env python3
"""
Simple test script to verify the Anthropic API is working
"""

import requests
import json
import sys
import time

def test_health_check(base_url="http://localhost:8000"):
    """Test the health endpoint"""
    try:
        response = requests.get(f"{base_url}/health")
        if response.status_code == 200:
            data = response.json()
            print("✅ Health check passed")
            print(f"   Status: {data.get('status')}")
            print(f"   Version: {data.get('version')}")
            print(f"   Clients initialized: {data.get('clients_initialized')}")
            return True
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Health check error: {e}")
        return False

def test_create_message(base_url="http://localhost:8000"):
    """Test message creation"""
    try:
        payload = {
            "model": "claude-sonnet-4-20250514",
            "messages": [
                {
                    "role": "user",
                    "content": "Hello! Please respond with just 'Hello, world!'"
                }
            ],
            "max_tokens": 1024
        }

        response = requests.post(
            f"{base_url}/api/v1/messages/create",
            json=payload,
            headers={"Content-Type": "application/json"}
        )

        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                print("✅ Message creation passed")
                content = data.get("data", {}).get("content", [])
                if content and len(content) > 0:
                    print(f"   Response: {content[0].get('text', '')[:100]}...")
                return True
            else:
                print(f"❌ Message creation failed: {data.get('error')}")
                return False
        else:
            print(f"❌ Message creation HTTP error: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Message creation error: {e}")
        return False

def test_token_counting(base_url="http://localhost:8000"):
    """Test token counting"""
    try:
        payload = {
            "model": "claude-sonnet-4-20250514",
            "messages": [
                {
                    "role": "user",
                    "content": "Hello, world! This is a test message for token counting."
                }
            ]
        }

        response = requests.post(
            f"{base_url}/api/v1/messages/count-tokens",
            json=payload,
            headers={"Content-Type": "application/json"}
        )

        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                print("✅ Token counting passed")
                tokens = data.get("data", {}).get("input_tokens")
                print(f"   Input tokens: {tokens}")
                return True
            else:
                print(f"❌ Token counting failed: {data.get('error')}")
                return False
        else:
            print(f"❌ Token counting HTTP error: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Token counting error: {e}")
        return False

def test_models_list(base_url="http://localhost:8000"):
    """Test models listing"""
    try:
        response = requests.get(f"{base_url}/api/v1/models")

        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                models = data.get("data", [])
                print("✅ Models list passed")
                print(f"   Found {len(models)} models")
                if models:
                    print(f"   First model: {models[0].get('id')}")
                return True
            else:
                print(f"❌ Models list failed: {data.get('error')}")
                return False
        else:
            print(f"❌ Models list HTTP error: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Models list error: {e}")
        return False

def test_streaming(base_url="http://localhost:8000"):
    """Test streaming endpoint"""
    try:
        payload = {
            "model": "claude-sonnet-4-20250514",
            "messages": [
                {
                    "role": "user",
                    "content": "Say 'Hello' and stop."
                }
            ],
            "max_tokens": 1024
        }

        response = requests.post(
            f"{base_url}/api/v1/messages/stream",
            json=payload,
            headers={"Content-Type": "application/json"},
            stream=True
        )

        if response.status_code == 200:
            print("✅ Streaming test passed")
            print("   Received streaming response (first few events):")

            event_count = 0
            for line in response.iter_lines():
                if line and event_count < 5:  # Show first 5 events
                    line_str = line.decode('utf-8')
                    if line_str.startswith('data: '):
                        try:
                            event_data = json.loads(line_str[6:])  # Remove 'data: ' prefix
                            print(f"   Event: {event_data.get('type', 'unknown')}")
                            event_count += 1
                        except:
                            pass
                elif event_count >= 5:
                    break

            return True
        else:
            print(f"❌ Streaming HTTP error: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Streaming error: {e}")
        return False

def main():
    """Run all tests"""
    base_url = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8000"

    print("🧪 Testing Anthropic API Client")
    print(f"📍 Base URL: {base_url}")
    print("-" * 50)

    tests = [
        ("Health Check", test_health_check),
        ("Models List", test_models_list),
        ("Token Counting", test_token_counting),
        ("Message Creation", test_create_message),
        ("Streaming", test_streaming),
    ]

    passed = 0
    total = len(tests)

    for test_name, test_func in tests:
        print(f"\n🔍 Testing {test_name}...")
        if test_func(base_url):
            passed += 1
        time.sleep(0.5)  # Brief pause between tests

    print("\n" + "=" * 50)
    print("📊 Test Results:")
    print(f"   Passed: {passed}/{total}")
    print(f"   Success Rate: {(passed/total)*100:.1f}%")
    if passed == total:
        print("🎉 All tests passed!")
        return 0
    else:
        print("⚠️  Some tests failed. Check your configuration.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
