#!/usr/bin/env python3
"""
Startup script for the Order Analysis Dashboard
"""

import os
import sys
import subprocess

def install_requirements():
    """Install required packages"""
    print("📦 Installing required packages...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Packages installed successfully!")
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install packages: {e}")
        sys.exit(1)

def start_app():
    """Start the Flask application"""
    print("🚀 Starting Order Analysis Dashboard...")
    os.environ['FLASK_ENV'] = 'development'
    try:
        subprocess.run([sys.executable, "app.py"])
    except KeyboardInterrupt:
        print("\n👋 Dashboard stopped by user")
    except Exception as e:
        print(f"❌ Error starting application: {e}")

if __name__ == "__main__":
    # Check if requirements are installed
    try:
        import flask
        import pandas
        import plotly
    except ImportError:
        install_requirements()
    
    # Start the application
    start_app()