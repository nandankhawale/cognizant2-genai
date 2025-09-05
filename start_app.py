#!/usr/bin/env python3
"""
Startup script to run both backend and frontend servers
"""

import subprocess
import sys
import time
import webbrowser
from pathlib import Path

def start_backend():
    """Start the FastAPI backend server"""
    print("🚀 Starting FastAPI backend server...")
    return subprocess.Popen([
        sys.executable, "loan_app.py"
    ], cwd=Path.cwd())

def start_frontend():
    """Start the frontend server"""
    print("🌐 Starting frontend server...")
    frontend_dir = Path.cwd() / "frontend"
    return subprocess.Popen([
        sys.executable, "server.py"
    ], cwd=frontend_dir)

def main():
    print("🎯 Loan Assistant - Full Stack Startup")
    print("=" * 50)
    
    # Start backend
    backend_process = start_backend()
    
    # Wait a bit for backend to start
    print("⏳ Waiting for backend to initialize...")
    time.sleep(3)
    
    # Start frontend
    frontend_process = start_frontend()
    
    print("\n✅ Both servers are starting up!")
    print("📱 Backend API: http://localhost:8001")
    print("🌐 Frontend UI: http://localhost:3000")
    print("\n💡 Press Ctrl+C to stop both servers")
    
    try:
        # Wait for both processes
        backend_process.wait()
        frontend_process.wait()
    except KeyboardInterrupt:
        print("\n🛑 Stopping servers...")
        backend_process.terminate()
        frontend_process.terminate()
        
        # Wait for clean shutdown
        backend_process.wait()
        frontend_process.wait()
        
        print("👋 Servers stopped successfully!")

if __name__ == "__main__":
    main()