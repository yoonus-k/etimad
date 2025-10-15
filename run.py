#!/usr/bin/env python3
"""
Etimad Tenders Application Runner
Run this file to start the Flask application.
"""

import sys
from pathlib import Path

# Add src directory to Python path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

# Import and run the Flask app
from src.app import app

if __name__ == '__main__':
    import os
    from watchdog.observers.polling import PollingObserver
    from werkzeug.serving import run_simple
    
    print("🚀 Starting Etimad Tenders Application...")
    print("📍 Navigate to: http://localhost:5000")
    print("⏹️  Press Ctrl+C to stop the server")
    print("⚠️  Note: Downloads folder is excluded from auto-reload\n")
    
    # Set environment variable to exclude folders from reloader
    excluded_dirs = ['downloads', 'data', 'debug', '__pycache__', '.git']
    os.environ['FLASK_SKIP_DOTENV'] = '1'
    
    # Run with stat reloader instead of watchdog to avoid issues
    app.run(
        debug=True, 
        host='0.0.0.0', 
        port=5000,
        use_reloader=True,
        reloader_type='stat'  # Use stat instead of watchdog
    )
