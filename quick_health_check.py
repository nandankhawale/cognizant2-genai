import requests
import time

def quick_test():
    """Quick test of the running server"""
    
    print("🔍 QUICK HEALTH CHECK")
    print("=" * 30)
    
    try:
        # Test health
        response = requests.get("http://localhost:8001/health", timeout=5)
        print(f"✅ Health: {response.status_code} - {response.json()}")
        
        # Test gold loan start
        response = requests.post(
            "http://localhost:8001/chat/start",
            json={"loan_type": "gold"},
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Gold loan session started!")
            print(f"📝 Message: {data['message'][:80]}...")
            
            # Test one message
            session_id = data["session_id"]
            response = requests.post(
                "http://localhost:8001/chat/message",
                json={
                    "session_id": session_id,
                    "message": "My name is John Doe"
                },
                timeout=15
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Message response received!")
                print(f"📝 Response: {data['message'][:80]}...")
                print(f"\\n🎉 SERVER IS WORKING PERFECTLY!")
                return True
            else:
                print(f"❌ Message failed: {response.status_code}")
        else:
            print(f"❌ Session start failed: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        
    return False

if __name__ == "__main__":
    quick_test()