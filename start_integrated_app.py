#!/usr/bin/env python3
"""
Integrated Loan Application Startup Script
Starts both the FastAPI backend and Next.js frontend
"""

import subprocess
import sys
import time
import os
from pathlib import Path

def run_command(command, cwd=None, shell=True):
    """Run a command in a subprocess"""
    try:
        process = subprocess.Popen(
            command,
            shell=shell,
            cwd=cwd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        return process
    except Exception as e:
        print(f"Error running command '{command}': {e}")
        return None

def check_dependencies():
    """Check if required dependencies are installed"""
    print("🔍 Checking dependencies...")
    
    # Check Python dependencies
    try:
        import fastapi
        import uvicorn
        print("✅ FastAPI dependencies found")
    except ImportError:
        print("❌ FastAPI dependencies missing. Run: pip install -r requirements.txt")
        return False
    
    # Check Node.js
    try:
        result = subprocess.run(['node', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ Node.js found: {result.stdout.strip()}")
        else:
            print("❌ Node.js not found. Please install Node.js")
            return False
    except FileNotFoundError:
        print("❌ Node.js not found. Please install Node.js")
        return False
    
    # Check if npm dependencies are installed
    frontend_path = Path("Banking-Marketing-master")
    node_modules = frontend_path / "node_modules"
    if not node_modules.exists():
        print("📦 Installing npm dependencies...")
        npm_install = subprocess.run(['npm', 'install'], cwd=frontend_path)
        if npm_install.returncode != 0:
            print("❌ Failed to install npm dependencies")
            return False
        print("✅ npm dependencies installed")
    else:
        print("✅ npm dependencies found")
    
    return True

def start_backend():
    """Start the FastAPI backend server"""
    print("🚀 Starting FastAPI backend server...")
    backend_process = run_command(
        [sys.executable, "loan_app.py"],
        shell=False
    )
    
    if backend_process:
        print("✅ Backend server starting on http://localhost:8001")
        return backend_process
    else:
        print("❌ Failed to start backend server")
        return None

def start_frontend():
    """Start the Next.js frontend server"""
    print("🚀 Starting Next.js frontend server...")
    frontend_path = Path("Banking-Marketing-master")
    
    frontend_process = run_command(
        "npm run dev",
        cwd=frontend_path
    )
    
    if frontend_process:
        print("✅ Frontend server starting on http://localhost:3000")
        return frontend_process
    else:
        print("❌ Failed to start frontend server")
        return None

def wait_for_backend():
    """Wait for backend to be ready"""
    import requests
    max_attempts = 30
    for attempt in range(max_attempts):
        try:
            response = requests.get("http://localhost:8001/health", timeout=2)
            if response.status_code == 200:
                print("✅ Backend server is ready!")
                return True
        except:
            pass
        
        print(f"⏳ Waiting for backend... ({attempt + 1}/{max_attempts})")
        time.sleep(2)
    
    print("❌ Backend server failed to start properly")
    return False

def main():
    """Main function to start the integrated application"""
    print("🏦 NextBank Loan Application - Integrated Startup")
    print("=" * 50)
    
    # Check dependencies
    if not check_dependencies():
        print("❌ Dependency check failed. Please install missing dependencies.")
        sys.exit(1)
    
    # Start backend
    backend_process = start_backend()
    if not backend_process:
        sys.exit(1)
    
    # Wait for backend to be ready
    if not wait_for_backend():
        backend_process.terminate()
        sys.exit(1)
    
    # Start frontend
    frontend_process = start_frontend()
    if not frontend_process:
        backend_process.terminate()
        sys.exit(1)
    
    print("\n🎉 Application started successfully!")
    print("=" * 50)
    print("🔗 Frontend: http://localhost:3000")
    print("🔗 Backend API: http://localhost:8001")
    print("🔗 API Docs: http://localhost:8001/docs")
    print("=" * 50)
    print("Press Ctrl+C to stop both servers")
    
    try:
        # Keep the script running and monitor processes
        while True:
            time.sleep(1)
            
            # Check if processes are still running
            if backend_process.poll() is not None:
                print("❌ Backend process stopped unexpectedly")
                break
            
            if frontend_process.poll() is not None:
                print("❌ Frontend process stopped unexpectedly")
                break
                
    except KeyboardInterrupt:
        print("\n🛑 Shutting down servers...")
        
        # Terminate processes
        if backend_process:
            backend_process.terminate()
            print("✅ Backend server stopped")
        
        if frontend_process:
            frontend_process.terminate()
            print("✅ Frontend server stopped")
        
        print("👋 Application stopped successfully!")

if __name__ == "__main__":
    main()