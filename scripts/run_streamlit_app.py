#!/usr/bin/env python3
"""
Launcher script for the Aircraft Design Studio Streamlit application.

This script sets up the proper Python path and launches the Streamlit web app
for interactive aircraft design and analysis.

Usage:
    python scripts/run_streamlit_app.py
    
Or from the project root:
    streamlit run src/streamlit_app.py

Author: Aircraft Design System
Version: 1.0
"""

import os
import sys
import subprocess
from pathlib import Path

def main():
    """Launch the Streamlit application."""
    # Get the project root directory
    project_root = Path(__file__).parent.parent
    src_dir = project_root / "src"
    streamlit_app = src_dir / "streamlit_app.py"
    
    # Add src directory to Python path
    sys.path.insert(0, str(src_dir))
    
    # Check if streamlit is installed
    try:
        import streamlit
    except ImportError:
        print("❌ Streamlit is not installed!")
        print("Please install it with: pip install streamlit>=1.28.0")
        print("Or install all dependencies: pip install -r requirements.txt")
        return 1
    
    # Check if the Streamlit app file exists
    if not streamlit_app.exists():
        print(f"❌ Streamlit app not found at: {streamlit_app}")
        return 1
    
    print("🚀 Launching Aircraft Design Studio...")
    print(f"📁 Project root: {project_root}")
    print(f"🎯 App location: {streamlit_app}")
    print("🌐 Opening in your default web browser...")
    print("\n" + "="*60)
    print("🛩️  AIRCRAFT DESIGN STUDIO")
    print("="*60)
    print("✨ Interactive aircraft design and analysis")
    print("📊 Real-time performance calculations")
    print("🎨 3D visualization and plotting")
    print("⚖️  Design comparison tools")
    print("="*60)
    print("\n💡 Use Ctrl+C to stop the server")
    print("-" * 60)
    
    # Change to src directory for proper imports
    os.chdir(src_dir)
    
    # Launch Streamlit with optimized settings
    cmd = [
        sys.executable, "-m", "streamlit", "run", 
        "streamlit_app.py",
        "--server.port=8501",
        "--server.address=localhost",
        "--browser.gatherUsageStats=false",
        "--theme.base=light",
        "--theme.primaryColor=#1f77b4",
        "--theme.backgroundColor=#ffffff",
        "--theme.secondaryBackgroundColor=#f0f2f6"
    ]
    
    try:
        # Run Streamlit
        subprocess.run(cmd, check=True)
    except KeyboardInterrupt:
        print("\n👋 Aircraft Design Studio stopped.")
        return 0
    except subprocess.CalledProcessError as e:
        print(f"❌ Error launching Streamlit: {e}")
        return 1
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
