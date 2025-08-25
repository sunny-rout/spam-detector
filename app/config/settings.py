"""
Application Configuration Settings
"""

import os
from datetime import timedelta


class Config:
    """Base configuration class"""
    
    # Flask settings
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    DEBUG = False
    TESTING = False
    
    # API settings
    MAX_BATCH_SIZE = int(os.environ.get('MAX_BATCH_SIZE', 100))
    API_VERSION = '1.0.0'
    
    # Rate limiting
    RATELIMIT_STORAGE_URL = os.environ.get('REDIS_URL', 'memory://')
    RATELIMIT_DEFAULT = "1000 per hour"
    
    # Logging
    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')
    LOG_FILE = os.environ.get('LOG_FILE', 'logs/spam_detector.log')
    
    # Security headers
    CORS_ORIGINS = os.environ.get('CORS_ORIGINS', '*').split(',')
    
    # Performance
    JSON_SORT_KEYS = False
    JSONIFY_PRETTYPRINT_REGULAR = False


class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    LOG_LEVEL = 'DEBUG'


class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    TESTING = False
    
    # In production, these should be set via environment variables
    SECRET_KEY = os.environ.get('SECRET_KEY')
    
    if not SECRET_KEY:
        raise ValueError("SECRET_KEY environment variable must be set in production")
    
    # Stricter settings for production
    MAX_BATCH_SIZE = int(os.environ.get('MAX_BATCH_SIZE', 50))
    RATELIMIT_DEFAULT = "500 per hour"
    
    # Security
    CORS_ORIGINS = os.environ.get('CORS_ORIGINS', '').split(',')
    if not CORS_ORIGINS or CORS_ORIGINS == ['']:
        raise ValueError("CORS_ORIGINS must be set in production")


class TestingConfig(Config):
    """Testing configuration"""
    TESTING = True
    DEBUG = True
    
    # Use in-memory rate limiting for tests
    RATELIMIT_STORAGE_URL = 'memory://'
    
    # Disable CSRF for testing
    WTF_CSRF_ENABLED = False
    
    # Test-specific settings
    MAX_BATCH_SIZE = 10


# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}