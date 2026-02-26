"""
Point of entry for Streamlit Cloud
"""
import subprocess
import sys

# Run the main app
subprocess.run([sys.executable, "-m", "streamlit", "run", "app/main.py"])
