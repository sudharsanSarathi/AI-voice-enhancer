#!/usr/bin/env python3
"""
Voice Enhancer AI - Main Application Runner

This script starts the Flask web application for voice enhancement using AI models.
"""

import os
import sys
import logging
from pathlib import Path

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from backend.app import app
from config import Config

def setup_logging():
    """Configure logging for the application"""
    log_level = getattr(logging, Config.LOG_LEVEL.upper(), logging.INFO)
    
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler('voice_enhancer.log', mode='a')
        ]
    )

def check_dependencies():
    """Check if required dependencies are available"""
    try:
        import clearvoice
        logging.info("ClearerVoice library found")
        return True
    except ImportError:
        logging.warning("ClearerVoice library not found. Install with: pip install clearvoice")
        logging.warning("The application will still run, but audio processing will fail until ClearerVoice is installed")
        return False

def create_directories():
    """Create necessary directories if they don't exist"""
    directories = [
        Config.UPLOAD_FOLDER,
        Config.PROCESSED_FOLDER,
        Path('checkpoints'),
        Path('logs')
    ]
    
    for directory in directories:
        directory.mkdir(exist_ok=True)
        logging.info(f"Directory ensured: {directory}")

def main():
    """Main application entry point"""
    # Setup logging
    setup_logging()
    
    # Create necessary directories
    create_directories()
    
    # Check dependencies
    deps_ok = check_dependencies()
    
    # Initialize Flask app configuration
    Config.init_app(app)
    
    # Get port from environment or use default
    port = int(os.environ.get('PORT', Config.PORT))
    host = os.environ.get('HOST', '0.0.0.0')
    debug = os.environ.get('DEBUG', 'False').lower() == 'true'
    
    # Log startup information
    logging.info("=" * 50)
    logging.info("🎵 Voice Enhancer AI Starting Up")
    logging.info("=" * 50)
    logging.info(f"Host: {host}")
    logging.info(f"Port: {port}")
    logging.info(f"Debug Mode: {debug}")
    logging.info(f"Upload Directory: {Config.UPLOAD_FOLDER}")
    logging.info(f"Processed Directory: {Config.PROCESSED_FOLDER}")
    logging.info(f"Max File Size: {Config.MAX_CONTENT_LENGTH / (1024*1024):.0f}MB")
    logging.info(f"Dependencies OK: {deps_ok}")
    
    if not deps_ok:
        logging.warning("⚠️  Some dependencies are missing. Please install them for full functionality.")
    
    logging.info("=" * 50)
    logging.info(f"🚀 Server starting at http://{host}:{port}")
    logging.info("=" * 50)
    
    try:
        # Start the Flask application
        app.run(
            host=host,
            port=port,
            debug=debug,
            threaded=True
        )
    except KeyboardInterrupt:
        logging.info("🛑 Server stopped by user")
    except Exception as e:
        logging.error(f"❌ Server error: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()