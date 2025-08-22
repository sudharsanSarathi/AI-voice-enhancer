#!/usr/bin/env python3
"""
Main application entry point for Render deployment
"""

import os
import sys
from pathlib import Path

# Add current directory to Python path
current_dir = Path(__file__).parent.absolute()
sys.path.insert(0, str(current_dir))

# Import the Flask app
from backend.app import app
from config import Config

# Initialize configuration
Config.init_app(app)

# For Gunicorn (Render deployment)
if __name__ != '__main__':
    # This is when running with Gunicorn
    application = app
else:
    # This is when running directly with python
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)