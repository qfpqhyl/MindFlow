#!/usr/bin/env python3
"""
Test script for MindFlow API
Run this to verify the API is working correctly
"""
import requests
import json
from typing import Optional

BASE_URL = "http://localhost:8000/api/v1"


def print_response(title: str, response: requests.Response):
    """Pretty print API response"""
    print(f"\n{'='*60}")
    print(f"{title}")
    print(f"{'='*60}")
    print(f"Status Code: {response.status_code}")
    try:
        print(f"Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    except:
        print(f"Response: {response.text}")


def test_health():
    """Test health endpoint"""
    response = requests.get(f"{BASE_URL}/../health")
    print_response("Health Check", response)
    return response.status_code == 200


def test_register(username: str, email: str, password: str):
    """Test user registration"""
    data = {
        "username": username,
        "email": email,
        "password": password
    }
    response = requests.post(f"{BASE_URL}/auth/register", json=data)
    print_response("Register User", response)

    if response.status_code == 201:
        return response.json()["data"]["token"]
    return None


def test_login(username: str, password: str) -> Optional[str]:
    """Test user login"""
    data = {
        "username": username,
        "password": password
    }
    response = requests.post(f"{BASE_URL}/auth/login", json=data)
    print_response("Login", response)

    if response.status_code == 200:
        return response.json()["data"]["token"]
    return None


def test_create_conversation(token: str):
    """Test creating a conversation"""
    data = {"title": "测试对话"}
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.post(f"{BASE_URL}/conversations", json=data, headers=headers)
    print_response("Create Conversation", response)

    if response.status_code == 201:
        return response.json()["data"]["conversation_id"]
    return None


def test_get_conversations(token: str):
    """Test getting conversations list"""
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/conversations", headers=headers)
    print_response("Get Conversations", response)
    return response.status_code == 200


def test_send_message(token: str, conversation_id: str):
    """Test sending a message"""
    data = {
        "content": "你好，请介绍一下 MindFlow 是什么？",
        "stream": False
    }
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.post(
        f"{BASE_URL}/conversations/{conversation_id}/messages",
        json=data,
        headers=headers,
        timeout=60
    )
    print_response("Send Message", response)
    return response.status_code == 200


def test_create_document(token: str):
    """Test creating a document"""
    data = {
        "title": "测试文档",
        "content": "# MindFlow 测试\n\n这是一个测试文档。",
        "summary": "测试文档摘要",
        "tags": ["测试", "MindFlow"]
    }
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.post(f"{BASE_URL}/documents", json=data, headers=headers)
    print_response("Create Document", response)
    return response.status_code == 200


def test_get_documents(token: str):
    """Test getting documents list"""
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/documents", headers=headers)
    print_response("Get Documents", response)
    return response.status_code == 200


def test_create_task(token: str):
    """Test creating a task"""
    from datetime import datetime, timedelta
    due_date = (datetime.utcnow() + timedelta(days=1)).isoformat()

    data = {
        "title": "测试任务",
        "description": "这是一个测试任务",
        "due_date": due_date,
        "reminder_enabled": False
    }
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.post(f"{BASE_URL}/tasks", json=data, headers=headers)
    print_response("Create Task", response)
    return response.status_code == 200


def test_get_tasks(token: str):
    """Test getting tasks list"""
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/tasks", headers=headers)
    print_response("Get Tasks", response)
    return response.status_code == 200


def main():
    """Run all tests"""
    print("🧪 MindFlow API Test Suite")
    print("=" * 60)

    # Test health
    if not test_health():
        print("\n❌ Health check failed. Is the server running?")
        return

    # Test authentication
    print("\n" + "="*60)
    print("Testing Authentication")
    print("="*60)

    test_username = "testuser"
    test_email = "test@example.com"
    test_password = "testpass123"

    # Try to register
    token = test_register(test_username, test_email, test_password)

    # If registration fails (user exists), try login
    if not token:
        print("\n⚠️  Registration failed (user may already exist), trying login...")
        token = test_login(test_username, test_password)

    if not token:
        print("\n❌ Authentication failed")
        return

    print(f"\n✅ Authentication successful! Token: {token[:20]}...")

    # Test conversations
    print("\n" + "="*60)
    print("Testing Conversations")
    print("="*60)

    test_get_conversations(token)
    conversation_id = test_create_conversation(token)

    # Test messages
    if conversation_id:
        print("\n" + "="*60)
        print("Testing Messages")
        print("="*60)
        test_send_message(token, conversation_id)

    # Test documents
    print("\n" + "="*60)
    print("Testing Documents")
    print("="*60)

    test_create_document(token)
    test_get_documents(token)

    # Test tasks
    print("\n" + "="*60)
    print("Testing Tasks")
    print("="*60)

    test_create_task(token)
    test_get_tasks(token)

    print("\n" + "="*60)
    print("✅ All tests completed!")
    print("="*60)


if __name__ == "__main__":
    try:
        main()
    except requests.exceptions.ConnectionError:
        print("\n❌ Cannot connect to server. Is it running on http://localhost:8000 ?")
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
