#!/usr/bin/env python3
"""
Fleet Management System - Professional UI
Run this script to start the Streamlit application
"""

import subprocess
import sys
import os

def install_requirements():
    """Install required packages"""
    print("Installing required packages...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])

def run_app():
    """Run the Streamlit application"""
    print("Starting Fleet Management System...")
    subprocess.run(["streamlit", "run", "fleetagents.py", "--server.port", "8501"])

if __name__ == "__main__":
    # Check if we're in the right directory
    if not os.path.exists("fleetagents.py"):
        print("Error: fleetagents.py not found. Please run this script from the project directory.")
        sys.exit(1)
    
    try:
        install_requirements()
        run_app()
    except KeyboardInterrupt:
        print("\nApplication stopped by user.")
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
