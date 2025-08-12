#!/usr/bin/env python3
"""
Snowflake Semantic Analytics App Launcher
==========================================

This script launches the production-ready Streamlit application for
Snowflake semantic analytics with natural language querying capabilities.

Usage:
    python app.py
"""

import os
import sys
import subprocess
from pathlib import Path

def check_prerequisites():
    """Check if all prerequisites are met"""
    print("🔍 Checking prerequisites...")
    
    # Check Python version
    if sys.version_info < (3, 8):
        print("❌ Python 3.8+ is required")
        return False
    
    # Check if config.toml exists
    config_path = Path("config.toml")
    if not config_path.exists():
        print("❌ config.toml not found. Please configure your Snowflake connection.")
        return False
    
    # Check if token file exists
    token_path = Path("snowflake-pat.token")
    if not token_path.exists():
        print("❌ snowflake-pat.token not found. Please add your Snowflake PAT.")
        return False
    
    # Check if streamlit app directory exists
    app_path = Path("streamlit_app/app.py")
    if not app_path.exists():
        print("❌ Streamlit app not found. Please ensure the app.py file exists.")
        return False
    
    print("✅ All prerequisites met!")
    return True

def test_snowflake_connection():
    """Test Snowflake connection"""
    print("🔗 Testing Snowflake connection...")
    
    try:
        result = subprocess.run([
            "snow", "--config-file=config.toml", "connection", "test", "-c", "semantics"
        ], capture_output=True, text=True, check=True)
        
        if "Status          | OK" in result.stdout:
            print("✅ Snowflake connection successful!")
            return True
        else:
            print("❌ Snowflake connection failed")
            return False
            
    except subprocess.CalledProcessError as e:
        print(f"❌ Error testing connection: {e}")
        return False
    except FileNotFoundError:
        print("❌ Snowflake CLI (snow) not found. Please install it first.")
        return False

def install_dependencies():
    """Install required dependencies"""
    print("📦 Installing dependencies...")
    
    try:
        requirements_path = Path("streamlit_app/requirements.txt")
        if requirements_path.exists():
            subprocess.run([
                sys.executable, "-m", "pip", "install", "-r", str(requirements_path)
            ], check=True)
            print("✅ Dependencies installed!")
        else:
            print("⚠️  requirements.txt not found, installing basic dependencies...")
            subprocess.run([
                sys.executable, "-m", "pip", "install", "streamlit", "snowflake-connector-python", 
                "pandas", "plotly", "toml"
            ], check=True)
            print("✅ Basic dependencies installed!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error installing dependencies: {e}")
        return False

def launch_app():
    """Launch the Streamlit application"""
    print("🚀 Launching Snowflake Semantic Analytics App...")
    print("📱 The app will open in your browser at: http://localhost:8501")
    print("🛑 Press Ctrl+C to stop the application")
    print("-" * 60)
    
    try:
        # Change to streamlit app directory
        os.chdir("streamlit_app")
        
        # Launch Streamlit
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", "app.py",
            "--server.port", "8501",
            "--server.address", "localhost"
        ])
        
    except KeyboardInterrupt:
        print("\n🛑 Application stopped by user")
    except Exception as e:
        print(f"❌ Error launching app: {e}")

def main():
    """Main function"""
    print("=" * 60)
    print("❄️  Snowflake Semantic Analytics App Launcher")
    print("=" * 60)
    
    # Check prerequisites
    if not check_prerequisites():
        print("\n❌ Prerequisites not met. Please fix the issues above and try again.")
        sys.exit(1)
    
    # Test Snowflake connection
    if not test_snowflake_connection():
        print("\n❌ Snowflake connection failed. Please check your configuration.")
        sys.exit(1)
    
    # Install dependencies
    if not install_dependencies():
        print("\n❌ Failed to install dependencies. Please check your Python environment.")
        sys.exit(1)
    
    # Launch the app
    launch_app()

if __name__ == "__main__":
    main()
