"""
Launcher script for Commercial Video Generator Streamlit UI

This script ensures the Python path is set correctly before launching Streamlit.
"""

import sys
import os
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# Change to project root directory
os.chdir(project_root)

# Now run streamlit
if __name__ == "__main__":
    import streamlit.web.cli as stcli
    
    app_path = Path(__file__).parent / "app.py"
    
    sys.argv = ["streamlit", "run", str(app_path)]
    sys.exit(stcli.main())
