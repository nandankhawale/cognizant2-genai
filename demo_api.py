#!/usr/bin/env python3
"""
Demo script to test the Multi-Loan API
Run this after starting the backend server
"""

import requests
import json
import time

API_BASE = "http://localhost:8001"

def test_health():
    """Test health endpoint"""
    print("🔍 Testing health endpoint...")
    response = requests.get(f"{API_BASE}/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    print()

def test_loan_types():
    """Test loan types endpoint"""
    print("📋 Testing loan types endpoint...")
    response = requests.get(f"{API_BASE}/loan-types")
    print(f"Status: {response.status_code}")
    data = response.json()
    print("Available loan types:")
    for loan_type in data["available_types"]:
        print(f"  - {loan_type}: {data['descriptions'][loan_type]}")
    print()

def test_education_loan_flow():
    """Test complete education loan flow"""
    print("🎓 Testing Education Loan Flow...")
    
    # Start chat
    print("1. Starting chat session...")
    response = requests.post(f"{API_BASE}/chat/start", json={
        "loan_type": "education"
    })
    
    if response.status_code != 200:
        print(f"❌ Failed to start chat: {response.text}")
        return
    
    data = response.json()
    session_id = data["session_id"]
    print(f"✅ Session started: {session_id}")
    print(f"Bot: {data['message']}")
    print()
    
    # Simulate conversation
    messages = [
        "My name is John Doe, email is john.doe@example.com and phone is +91-9876543210",
        "I am 22 years old and want to pursue MBA",
        "My academic performance is Good and I want to study at a Tier1 university",
        "My co-applicant income is 8 lakhs per year",
        "Guarantor networth is 50 lakhs and my CIBIL score is 750",
        "I want a secured loan for 5 years and need 15 lakhs"
    ]
    
    for i, message in enumerate(messages, 2):
        print(f"{i}. Sending: {message}")
        response = requests.post(f"{API_BASE}/chat/message", json={
            "session_id": session_id,
            "message": message
        })
        
        if response.status_code != 200:
            print(f"❌ Failed to send message: {response.text}")
            return
        
        data = response.json()
        print(f"Bot: {data['message']}")
        
        if data.get("recorded"):
            print(f"📝 Recorded: {data['recorded']}")
        
        if data.get("prediction"):
            print("🎯 PREDICTION RECEIVED!")
            pred = data["prediction"]
            print(f"   Loan Type: {pred['loan_type']}")
            print(f"   Eligible Amount: ₹{pred['result']['eligible_amount']:,}")
            print(f"   Interest Rate: {pred['result']['interest_rate']}%")
            print(f"   Status: {pred['result']['status']}")
            break
        
        print()
        time.sleep(1)  # Be nice to the API

def main():
    print("🤖 Multi-Loan API Demo")
    print("=" * 40)
    
    try:
        test_health()
        test_loan_types()
        test_education_loan_flow()
        
        print("✅ Demo completed successfully!")
        print("💡 Try the frontend at http://localhost:3000")
        
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to API server")
        print("💡 Make sure the backend is running: python loan_app.py")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()