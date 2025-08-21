"""
Error Handlers Module
Centralized error handling for consistent API responses.
"""
from flask import jsonify, request, current_app
from app.utils.logger import get_logger, security_logger
import time


logger = get_logger(__name__)


def register_error_handlers(app):
    """
    Register error handlers with the Flask application
    
    Args:
        app: Flask application instance
    """
    
    @app.errorhandler(400)
    def bad_request(error):
        """Handle 400 Bad Request errors"""
        logger.warning(f"Bad request: {request.url} - {str(error)}")
        return jsonify({
            'error': 'Bad Request',
            'message': 'The request was invalid or cannot be served',
            'status_code': 400,
            'timestamp': time.time()
        }), 400
    
    @app.errorhandler(401)
    def unauthorized(error):
        """Handle 401 Unauthorized errors"""
        security_logger.log_suspicious_activity(
            'UNAUTHORIZED_ACCESS',
            f'Unauthorized access attempt to {request.url}',
            request.remote_addr
        )
        return jsonify({
            'error': 'Unauthorized',
            'message': 'Authentication required',
            'status_code': 401,
            'timestamp': time.time()
        }), 401
    
    @app.errorhandler(403)
    def forbidden(error):
        """Handle 403 Forbidden errors"""
        security_logger.log_suspicious_activity(
            'FORBIDDEN_ACCESS',
            f'Forbidden access attempt to {request.url}',
            request.remote_addr
        )
        return jsonify({
            'error': 'Forbidden',
            'message': 'You do not have permission to access this resource',
            'status_code': 403,
            'timestamp': time.time()
        }), 403
    
    @app.errorhandler(404)
    def not_found(error):
        """Handle 404 Not Found errors"""
        logger.info(f"Resource not found: {request.url}")
        return jsonify({
            'error': 'Not Found',
            'message': 'The requested resource was not found',
            'status_code': 404,
            'timestamp': time.time(),
            'available_endpoints': [
                '/api/v1/health',
                '/api/v1/detect',
                '/api/v1/detect/batch',
                '/api/v1/analyze',
                '/api/v1/stats'
            ]
        }), 404
    
    @app.errorhandler(405)
    def method_not_allowed(error):
        """Handle 405 Method Not Allowed errors"""
        logger.warning(f"Method not allowed: {request.method} {request.url}")
        return jsonify({
            'error': 'Method Not Allowed',
            'message': f'The {request.method} method is not allowed for this endpoint',
            'status_code': 405,
            'timestamp': time.time()
        }), 405
    
    @app.errorhandler(413)
    def payload_too_large(error):
        """Handle 413 Payload Too Large errors"""
        logger.warning(f"Payload too large: {request.url} - Content length: {request.content_length}")
        security_logger.log_suspicious_activity(
            'LARGE_PAYLOAD',
            f'Payload too large from {request.remote_addr}',
            request.remote_addr
        )
        return jsonify({
            'error': 'Payload Too Large',
            'message': 'The request payload is too large',
            'status_code': 413,
            'timestamp': time.time(),
            'max_content_length': current_app.config.get('MAX_CONTENT_LENGTH', '16MB')
        }), 413
    
    @app.errorhandler(415)
    def unsupported_media_type(error):
        """Handle 415 Unsupported Media Type errors"""
        logger.warning(f"Unsupported media type: {request.content_type}")
        return jsonify({
            'error': 'Unsupported Media Type',
            'message': 'The request content type is not supported',
            'status_code': 415,
            'timestamp': time.time(),
            'supported_types': ['application/json']
        }), 415
    
    @app.errorhandler(422)
    def unprocessable_entity(error):
        """Handle 422 Unprocessable Entity errors"""
        logger.warning(f"Unprocessable entity: {request.url}")
        return jsonify({
            'error': 'Unprocessable Entity',
            'message': 'The request was well-formed but contains semantic errors',
            'status_code': 422,
            'timestamp': time.time()
        }), 422
    
    @app.errorhandler(429)
    def rate_limit_exceeded(error):
        """Handle 429 Too Many Requests errors"""
        security_logger.log_rate_limit_exceeded(request.remote_addr, request.endpoint)
        return jsonify({
            'error': 'Too Many Requests',
            'message': 'Rate limit exceeded. Please try again later',
            'status_code': 429,
            'timestamp': time.time(),
            'retry_after': 3600  # 1 hour
        }), 429
    
    @app.errorhandler(500)
    def internal_server_error(error):
        """Handle 500 Internal Server Error"""
        logger.error(f"Internal server error: {request.url}", exc_info=True)
        
        # Don't expose internal error details in production
        if current_app.debug:
            error_message = str(error)
        else:
            error_message = 'An internal server error occurred'
        
        return jsonify({
            'error': 'Internal Server Error',
            'message': error_message,
            'status_code': 500,
            'timestamp': time.time()
        }), 500
    
    @app.errorhandler(502)
    def bad_gateway(error):
        """Handle 502 Bad Gateway errors"""
        logger.error(f"Bad gateway: {request.url}")
        return jsonify({
            'error': 'Bad Gateway',
            'message': 'The server received an invalid response from an upstream server',
            'status_code': 502,
            'timestamp': time.time()
        }), 502
    
    @app.errorhandler(503)
    def service_unavailable(error):
        """Handle 503 Service Unavailable errors"""
        logger.error(f"Service unavailable: {request.url}")
        return jsonify({
            'error': 'Service Unavailable',
            'message': 'The service is temporarily unavailable',
            'status_code': 503,
            'timestamp': time.time(),
            'retry_after': 300  # 5 minutes
        }), 503
    
    @app.errorhandler(504)
    def gateway_timeout(error):
        """Handle 504 Gateway Timeout errors"""
        logger.error(f"Gateway timeout: {request.url}")
        return jsonify({
            'error': 'Gateway Timeout',
            'message': 'The server did not receive a timely response from an upstream server',
            'status_code': 504,
            'timestamp': time.time()
        }), 504


class APIException(Exception):
    """
    Custom API exception with HTTP status code and message
    """
    
    def __init__(self, message, status_code=400, payload=None):
        super().__init__()
        self.message = message
        self.status_code = status_code
        self.payload = payload
    
    def to_dict(self):
        """Convert exception to dictionary for JSON response"""
        result = {
            'error': self.__class__.__name__,
            'message': self.message,
            'status_code': self.status_code,
            'timestamp': time.time()
        }
        if self.payload:
            result.update(self.payload)
        return result


class ValidationError(APIException):
    """Validation error exception"""
    
    def __init__(self, message, field=None):
        super().__init__(message, status_code=400)
        if field:
            self.payload = {'field': field}


class RateLimitError(APIException):
    """Rate limit exceeded exception"""
    
    def __init__(self, message="Rate limit exceeded", retry_after=3600):
        super().__init__(message, status_code=429)
        self.payload = {'retry_after': retry_after}


class ServiceError(APIException):
    """Service error exception"""
    
    def __init__(self, message="Service temporarily unavailable"):
        super().__init__(message, status_code=503)


def register_api_exceptions(app):
    """
    Register custom API exception handlers
    
    Args:
        app: Flask application instance
    """
    
    @app.errorhandler(APIException)
    def handle_api_exception(error):
        """Handle custom API exceptions"""
        logger.warning(f"API exception: {error.message} (Status: {error.status_code})")
        response = jsonify(error.to_dict())
        response.status_code = error.status_code
        return response
    
    @app.errorhandler(ValidationError)
    def handle_validation_error(error):
        """Handle validation errors"""
        logger.warning(f"Validation error: {error.message}")
        response = jsonify(error.to_dict())
        response.status_code = error.status_code
        return response
    
    @app.errorhandler(RateLimitError)
    def handle_rate_limit_error(error):
        """Handle rate limit errors"""
        security_logger.log_rate_limit_exceeded(request.remote_addr, request.endpoint)
        response = jsonify(error.to_dict())
        response.status_code = error.status_code
        return response
    
    @app.errorhandler(ServiceError)
    def handle_service_error(error):
        """Handle service errors"""
        logger.error(f"Service error: {error.message}")
        response = jsonify(error.to_dict())
        response.status_code = error.status_code
        return response


def handle_json_decode_error(app):
    """
    Handle JSON decode errors
    
    Args:
        app: Flask application instance
    """
    
    @app.before_request
    def check_json():
        """Check if JSON is valid for POST requests"""
        if request.method == 'POST' and request.content_type == 'application/json':
            try:
                request.get_json()
            except Exception as e:
                logger.warning(f"Invalid JSON in request: {str(e)}")
                return jsonify({
                    'error': 'Invalid JSON',
                    'message': 'The request body contains invalid JSON',
                    'status_code': 400,
                    'timestamp': time.time()
                }), 400


# Health check response for load balancers
def health_check_response():
    """
    Generate a simple health check response
    
    Returns:
        Tuple of (response_dict, status_code)
    """
    return {
        'status': 'healthy',
        'timestamp': time.time(),
        'version': current_app.config.get('API_VERSION', '1.0.0')
    }, 200