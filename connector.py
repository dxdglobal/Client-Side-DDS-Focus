#!/usr/bin/env python3
"""
DDSFocusPro Connector - Flask Backend Server
This runs the Flask application as a standalone server
"""

import os
import sys
import logging

# Setup logging
log_folder = "logs"
os.makedirs(log_folder, exist_ok=True)
log_file = os.path.join(log_folder, "connector.log")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(log_file, mode='w', encoding='utf-8'),
        logging.StreamHandler()
    ]
)

def handle_exception(exc_type, exc_value, exc_traceback):
    logging.error("❌ Uncaught exception", exc_info=(exc_type, exc_value, exc_traceback))

sys.excepthook = handle_exception

if __name__ == '__main__':
    try:
        logging.info("🚀 Starting DDSFocusPro Connector...")
        
        # Import and run the Flask app
        from app import app
        
        logging.info("🌐 Flask server starting on http://127.0.0.1:5000")
        app.run(
            host='127.0.0.1',
            port=5000,
            debug=False,
            use_reloader=False,
            threaded=True
        )
        
    except Exception as e:
        logging.error(f"❌ Failed to start connector: {e}")
        sys.exit(1)