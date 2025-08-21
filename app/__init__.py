from flask import Flask
from flask_cors import CORS
from config import Config
from app.utils.logger import setup_logger
from app.api.errors import register_error_handlers


def create_app(config_class=Config):
    """
    Application factory function
    
    Args:
        config_class: Configuration class to use
        
    Returns:
        Flask app instance
    """
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Initialize CORS
    CORS(app)
    
    # Setup logging
    setup_logger(app)
    
    # Register blueprints
    from app.api.routes import api_bp
    app.register_blueprint(api_bp, url_prefix='/api/v1')
    
    # Register error handlers
    register_error_handlers(app)
    
    return app