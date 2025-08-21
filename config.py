"""
Application Configuration Module
Manages environment-specific settings and security configurations.
"""
import os
from datetime import timedelta

class Config:
    """Base configuration class with common settings."""
    
    # Flask Settings
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-key-change-in-production')
    DEBUG = False
    TESTING = False
    
    # API Settings
    API_VERSION = 'v1'
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max request size
    JSONIFY_PRETTYPRINT_REGULAR = True
    
    # Rate Limiting
    RATELIMIT_STORAGE_URL = os.environ.get('REDIS_URL', 'memory://')
    RATELIMIT_DEFAULT = "100 per hour"
    
    # Logging
    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')
    LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    
    # Spam Detection Settings
    SPAM_THRESHOLD = float(os.environ.get('SPAM_THRESHOLD', '5.0'))
    MAX_BATCH_SIZE = int(os.environ.get('MAX_BATCH_SIZE', '50'))
    
    # Database (for future expansion)
    DATABASE_URL = os.environ.get('DATABASE_URL', 'sqlite:///spam_detector.db')

class DevelopmentConfig(Config):
    """Development environment configuration."""
    DEBUG = True
    LOG_LEVEL = 'DEBUG'

class ProductionConfig(Config):
    """Production environment configuration."""
    DEBUG = False
    TESTING = False
    LOG_LEVEL = 'WARNING'

class TestingConfig(Config):
    """Testing environment configuration."""
    TESTING = True
    DEBUG = True
    SPAM_THRESHOLD = 3.0  # Lower threshold for testing

# Configuration mapping
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}