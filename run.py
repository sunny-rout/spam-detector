"""
Application Entry Point
Main script to run the Flask application with proper configuration.
"""
import os
import time
from app import create_app
from app.config.settings import config

# Get configuration environment
config_name = os.environ.get('FLASK_ENV', 'development')

# Create Flask application
app = create_app(config[config_name])

# Store start time for uptime calculation
app.config['START_TIME'] = time.time()

if __name__ == '__main__':
    # Development server settings
    host = os.environ.get('HOST', '0.0.0.0')
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_ENV') == 'development'
    
    print(f"Starting Spam Detector API on {host}:{port}")
    print(f"Environment: {config_name}")
    print(f"Debug mode: {debug}")
    
    app.run(
        host=host,
        port=port,
        debug=debug,
        threaded=True
    )