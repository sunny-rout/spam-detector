"""
API Logging Module
Handles request logging, statistics, and monitoring.
"""
import logging
import logging.handlers
import os
import sys
from datetime import datetime
from flask import request, g
import json


def setup_logger(app):
    """
    Setup application logging
    
    Args:
        app: Flask application instance
    """
    # Create logs directory if it doesn't exist
    log_dir = os.path.dirname(app.config.get('LOG_FILE', 'logs/spam_detector.log'))
    if log_dir and not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    # Set log level
    log_level = getattr(logging, app.config.get('LOG_LEVEL', 'INFO').upper())
    app.logger.setLevel(log_level)
    
    # Remove default handlers
    app.logger.handlers = []
    
    # Create formatters
    detailed_formatter = logging.Formatter(
        '[%(asctime)s] %(levelname)s in %(module)s (%(filename)s:%(lineno)d): %(message)s'
    )
    
    simple_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)
    console_handler.setFormatter(simple_formatter)
    app.logger.addHandler(console_handler)
    
    # File handler (if specified)
    log_file = app.config.get('LOG_FILE')
    if log_file:
        file_handler = logging.handlers.RotatingFileHandler(
            log_file,
            maxBytes=10485760,  # 10MB
            backupCount=5
        )
        file_handler.setLevel(log_level)
        file_handler.setFormatter(detailed_formatter)
        app.logger.addHandler(file_handler)
    
    # Error file handler (for errors only)
    if log_file:
        error_file = log_file.replace('.log', '_errors.log')
        error_handler = logging.handlers.RotatingFileHandler(
            error_file,
            maxBytes=10485760,  # 10MB
            backupCount=5
        )
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(detailed_formatter)
        app.logger.addHandler(error_handler)
    
    # JSON formatter for structured logging (production)
    if not app.debug:
        json_formatter = JSONFormatter()
        
        if log_file:
            json_file = log_file.replace('.log', '_json.log')
            json_handler = logging.handlers.RotatingFileHandler(
                json_file,
                maxBytes=10485760,  # 10MB
                backupCount=5
            )
            json_handler.setLevel(log_level)
            json_handler.setFormatter(json_formatter)
            app.logger.addHandler(json_handler)
    
    # Set werkzeug logger level (Flask's HTTP request logger)
    werkzeug_logger = logging.getLogger('werkzeug')
    werkzeug_logger.setLevel(logging.WARNING)
    
    app.logger.info(f"Logging configured with level: {logging.getLevelName(log_level)}")


def get_logger(name):
    """
    Get a logger instance for a specific module
    
    Args:
        name: Logger name (usually __name__)
        
    Returns:
        Logger instance
    """
    return logging.getLogger(name)


class JSONFormatter(logging.Formatter):
    """
    JSON formatter for structured logging
    """
    
    def format(self, record):
        """
        Format log record as JSON
        
        Args:
            record: Log record
            
        Returns:
            JSON formatted log string
        """
        log_entry = {
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'level': record.levelname,
            'logger': record.name,
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno,
            'message': record.getMessage(),
        }
        
        # Add exception info if present
        if record.exc_info:
            log_entry['exception'] = self.formatException(record.exc_info)
        
        # Add extra fields if present
        for key, value in record.__dict__.items():
            if key not in ['name', 'msg', 'args', 'levelname', 'levelno', 'pathname',
                          'filename', 'module', 'lineno', 'funcName', 'created',
                          'msecs', 'relativeCreated', 'thread', 'threadName',
                          'processName', 'process', 'getMessage', 'exc_info',
                          'exc_text', 'stack_info']:
                log_entry[key] = value
        
        # Add request context if available
        try:
            if request:
                log_entry['request'] = {
                    'method': request.method,
                    'url': request.url,
                    'remote_addr': request.remote_addr,
                    'user_agent': request.headers.get('User-Agent'),
                }
                
                # Add request ID if available
                if hasattr(g, 'request_id'):
                    log_entry['request_id'] = g.request_id
        except RuntimeError:
            # Outside request context
            pass
        
        return json.dumps(log_entry, default=str)


class RequestLogger:
    """
    Request logging middleware
    """
    
    def __init__(self, app=None):
        self.app = app
        if app is not None:
            self.init_app(app)
    
    def init_app(self, app):
        """Initialize request logging for Flask app"""
        app.before_request(self.before_request)
        app.after_request(self.after_request)
        app.teardown_request(self.teardown_request)
    
    def before_request(self):
        """Called before each request"""
        import uuid
        
        # Generate unique request ID
        g.request_id = str(uuid.uuid4())
        g.start_time = datetime.utcnow()
        
        logger = get_logger('request')
        logger.info(
            f"Request started: {request.method} {request.path}",
            extra={
                'request_id': g.request_id,
                'method': request.method,
                'path': request.path,
                'remote_addr': request.remote_addr,
                'user_agent': request.headers.get('User-Agent', ''),
                'content_length': request.content_length,
            }
        )
    
    def after_request(self, response):
        """Called after each request"""
        if hasattr(g, 'start_time'):
            duration = (datetime.utcnow() - g.start_time).total_seconds()
            
            logger = get_logger('request')
            
            # Determine log level based on status code
            if response.status_code >= 500:
                log_level = logging.ERROR
            elif response.status_code >= 400:
                log_level = logging.WARNING
            else:
                log_level = logging.INFO
            
            logger.log(
                log_level,
                f"Request completed: {request.method} {request.path} - "
                f"Status: {response.status_code} - Duration: {duration:.3f}s",
                extra={
                    'request_id': getattr(g, 'request_id', 'unknown'),
                    'method': request.method,
                    'path': request.path,
                    'status_code': response.status_code,
                    'duration_seconds': duration,
                    'response_size': len(response.get_data()),
                }
            )
        
        return response
    
    def teardown_request(self, exception):
        """Called when request context is torn down"""
        if exception:
            logger = get_logger('request')
            logger.error(
                f"Request exception: {request.method} {request.path}",
                exc_info=exception,
                extra={
                    'request_id': getattr(g, 'request_id', 'unknown'),
                    'method': request.method,
                    'path': request.path,
                }
            )


class SecurityLogger:
    """
    Security event logger
    """
    
    def __init__(self):
        self.logger = get_logger('security')
    
    def log_suspicious_activity(self, event_type, details, ip_address=None):
        """
        Log suspicious security events
        
        Args:
            event_type: Type of security event
            details: Event details
            ip_address: IP address of the client
        """
        self.logger.warning(
            f"Security event: {event_type}",
            extra={
                'event_type': event_type,
                'details': details,
                'ip_address': ip_address or (request.remote_addr if request else 'unknown'),
                'timestamp': datetime.utcnow().isoformat(),
                'user_agent': request.headers.get('User-Agent', '') if request else '',
            }
        )
    
    def log_rate_limit_exceeded(self, ip_address, endpoint):
        """Log rate limit violations"""
        self.log_suspicious_activity(
            'RATE_LIMIT_EXCEEDED',
            f'Rate limit exceeded for endpoint: {endpoint}',
            ip_address
        )
    
    def log_malicious_input(self, input_data, ip_address):
        """Log potentially malicious input"""
        self.log_suspicious_activity(
            'MALICIOUS_INPUT',
            f'Potentially malicious input detected: {str(input_data)[:200]}...',
            ip_address
        )
    
    def log_authentication_failure(self, username, ip_address):
        """Log authentication failures"""
        self.log_suspicious_activity(
            'AUTH_FAILURE',
            f'Authentication failed for user: {username}',
            ip_address
        )


class PerformanceLogger:
    """
    Performance monitoring logger
    """
    
    def __init__(self):
        self.logger = get_logger('performance')
    
    def log_slow_request(self, duration, endpoint, method):
        """
        Log slow requests
        
        Args:
            duration: Request duration in seconds
            endpoint: API endpoint
            method: HTTP method
        """
        self.logger.warning(
            f"Slow request detected: {method} {endpoint} took {duration:.3f}s",
            extra={
                'duration_seconds': duration,
                'endpoint': endpoint,
                'method': method,
                'request_id': getattr(g, 'request_id', 'unknown'),
            }
        )
    
    def log_high_memory_usage(self, memory_mb):
        """Log high memory usage"""
        self.logger.warning(
            f"High memory usage detected: {memory_mb:.1f}MB",
            extra={'memory_usage_mb': memory_mb}
        )
    
    def log_detection_performance(self, duration, email_count=1):
        """
        Log spam detection performance
        
        Args:
            duration: Detection duration in seconds
            email_count: Number of emails processed
        """
        emails_per_second = email_count / duration if duration > 0 else 0
        
        self.logger.info(
            f"Spam detection completed: {email_count} emails in {duration:.3f}s "
            f"({emails_per_second:.1f} emails/sec)",
            extra={
                'detection_duration_seconds': duration,
                'emails_processed': email_count,
                'emails_per_second': emails_per_second,
            }
        )


# Global logger instances
security_logger = SecurityLogger()
performance_logger = PerformanceLogger()


def log_api_usage(endpoint, method, status_code, duration):
    """
    Log API usage for analytics
    
    Args:
        endpoint: API endpoint
        method: HTTP method
        status_code: Response status code
        duration: Request duration
    """
    logger = get_logger('api_usage')
    logger.info(
        f"API call: {method} {endpoint}",
        extra={
            'endpoint': endpoint,
            'method': method,
            'status_code': status_code,
            'duration_seconds': duration,
            'timestamp': datetime.utcnow().isoformat(),
        }
    )