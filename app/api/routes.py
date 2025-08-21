"""
API Routes Module
Defines all REST API endpoints for the spam detection service.
"""
from flask import Blueprint, request, jsonify, current_app
from app.models.spam_detector import SpamDetector
from app.utils.validators import validate_email_data, validate_batch_data
from app.utils.logger import get_logger
import time
from functools import wraps

# Create blueprint
api_bp = Blueprint('api', __name__)

# Initialize spam detector
detector = SpamDetector()
logger = get_logger(__name__)


def rate_limit(max_requests=100, window=3600):
    """
    Simple rate limiting decorator
    
    Args:
        max_requests: Maximum requests allowed
        window: Time window in seconds
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # In production, you'd use Redis or similar for distributed rate limiting
            # This is a simple in-memory implementation
            client_ip = request.remote_addr
            current_time = time.time()
            
            # For demo purposes, we'll skip actual rate limiting implementation
            # In production, implement proper rate limiting here
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator


@api_bp.route('/health', methods=['GET'])
def health_check():
    """
    Health check endpoint
    
    Returns:
        JSON response with API status
    """
    return jsonify({
        'status': 'healthy',
        'timestamp': time.time(),
        'version': '1.0.0'
    })


@api_bp.route('/detect', methods=['POST'])
@rate_limit(max_requests=1000, window=3600)
def detect_spam():
    """
    Single email spam detection endpoint
    
    Expected JSON payload:
    {
        "text": "Email body text",
        "subject": "Email subject (optional)"
    }
    
    Returns:
        JSON response with detection results
    """
    try:
        # Get JSON data
        data = request.get_json()
        
        # Validate input
        validation_error = validate_email_data(data)
        if validation_error:
            logger.warning(f"Validation error: {validation_error}")
            return jsonify({
                'error': 'Invalid input',
                'message': validation_error
            }), 400
        
        # Extract email data
        email_text = data.get('text', '')
        subject = data.get('subject', '')
        
        # Log request (in production, be careful about logging sensitive data)
        logger.info(f"Processing spam detection request from {request.remote_addr}")
        
        # Perform spam detection
        start_time = time.time()
        result = detector.detect_spam(email_text, subject)
        processing_time = time.time() - start_time
        
        # Add metadata to response
        response = {
            'success': True,
            'data': result,
            'metadata': {
                'processing_time_ms': round(processing_time * 1000, 2),
                'timestamp': time.time(),
                'api_version': '1.0.0'
            }
        }
        
        # Log result
        logger.info(f"Spam detection completed. Result: {'SPAM' if result['is_spam'] else 'HAM'}, "
                   f"Score: {result['spam_score']}, Time: {processing_time:.3f}s")
        
        return jsonify(response)
        
    except Exception as e:
        logger.error(f"Error processing spam detection request: {str(e)}", exc_info=True)
        return jsonify({
            'error': 'Internal server error',
            'message': 'An error occurred while processing your request'
        }), 500


@api_bp.route('/detect/batch', methods=['POST'])
@rate_limit(max_requests=100, window=3600)
def detect_spam_batch():
    """
    Batch email spam detection endpoint
    
    Expected JSON payload:
    {
        "emails": [
            {
                "id": "email_1",
                "text": "Email body text",
                "subject": "Email subject (optional)"
            },
            ...
        ]
    }
    
    Returns:
        JSON response with detection results for all emails
    """
    try:
        # Get JSON data
        data = request.get_json()
        
        # Validate input
        validation_error = validate_batch_data(data)
        if validation_error:
            logger.warning(f"Batch validation error: {validation_error}")
            return jsonify({
                'error': 'Invalid input',
                'message': validation_error
            }), 400
        
        emails = data.get('emails', [])
        
        # Limit batch size for performance
        max_batch_size = current_app.config.get('MAX_BATCH_SIZE', 100)
        if len(emails) > max_batch_size:
            return jsonify({
                'error': 'Batch too large',
                'message': f'Maximum batch size is {max_batch_size} emails'
            }), 400
        
        # Log request
        logger.info(f"Processing batch spam detection request with {len(emails)} emails from {request.remote_addr}")
        
        # Perform batch spam detection
        start_time = time.time()
        results = detector.batch_detect(emails)
        processing_time = time.time() - start_time
        
        # Calculate statistics
        spam_count = sum(1 for r in results if r['is_spam'])
        ham_count = len(results) - spam_count
        
        # Prepare response
        response = {
            'success': True,
            'data': {
                'results': results,
                'summary': {
                    'total_emails': len(results),
                    'spam_detected': spam_count,
                    'ham_detected': ham_count,
                    'spam_percentage': round((spam_count / len(results)) * 100, 2) if results else 0
                }
            },
            'metadata': {
                'processing_time_ms': round(processing_time * 1000, 2),
                'emails_per_second': round(len(results) / processing_time, 2) if processing_time > 0 else 0,
                'timestamp': time.time(),
                'api_version': '1.0.0'
            }
        }
        
        # Log result
        logger.info(f"Batch spam detection completed. Processed {len(results)} emails, "
                   f"Found {spam_count} spam, Time: {processing_time:.3f}s")
        
        return jsonify(response)
        
    except Exception as e:
        logger.error(f"Error processing batch spam detection request: {str(e)}", exc_info=True)
        return jsonify({
            'error': 'Internal server error',
            'message': 'An error occurred while processing your request'
        }), 500


@api_bp.route('/analyze', methods=['POST'])
@rate_limit(max_requests=500, window=3600)
def analyze_email():
    """
    Detailed email analysis endpoint (returns more detailed information)
    
    Expected JSON payload:
    {
        "text": "Email body text",
        "subject": "Email subject (optional)",
        "include_features": true,
        "include_explanations": true
    }
    
    Returns:
        JSON response with detailed analysis
    """
    try:
        # Get JSON data
        data = request.get_json()
        
        # Validate input
        validation_error = validate_email_data(data)
        if validation_error:
            logger.warning(f"Analysis validation error: {validation_error}")
            return jsonify({
                'error': 'Invalid input',
                'message': validation_error
            }), 400
        
        # Extract email data and options
        email_text = data.get('text', '')
        subject = data.get('subject', '')
        include_features = data.get('include_features', True)
        include_explanations = data.get('include_explanations', True)
        
        # Log request
        logger.info(f"Processing email analysis request from {request.remote_addr}")
        
        # Perform analysis
        start_time = time.time()
        result = detector.detect_spam(email_text, subject)
        processing_time = time.time() - start_time
        
        # Prepare detailed response
        analysis = {
            'classification': {
                'is_spam': result['is_spam'],
                'confidence': result['confidence'],
                'spam_score': result['spam_score']
            },
            'risk_level': _get_risk_level(result['spam_score'])
        }
        
        # Add optional details
        if include_features:
            analysis['features'] = result['features']
            analysis['scores'] = result['scores']
        
        if include_explanations:
            analysis['explanation'] = result['explanation']
            analysis['recommendations'] = _get_recommendations(result)
        
        response = {
            'success': True,
            'data': analysis,
            'metadata': {
                'processing_time_ms': round(processing_time * 1000, 2),
                'timestamp': time.time(),
                'api_version': '1.0.0'
            }
        }
        
        # Log result
        logger.info(f"Email analysis completed. Risk level: {analysis['risk_level']}, "
                   f"Time: {processing_time:.3f}s")
        
        return jsonify(response)
        
    except Exception as e:
        logger.error(f"Error processing email analysis request: {str(e)}", exc_info=True)
        return jsonify({
            'error': 'Internal server error',
            'message': 'An error occurred while processing your request'
        }), 500


@api_bp.route('/stats', methods=['GET'])
def get_stats():
    """
    Get API usage statistics
    
    Returns:
        JSON response with API statistics
    """
    # In production, these would come from a database or analytics service
    stats = {
        'api_version': '1.0.0',
        'uptime_seconds': time.time() - current_app.config.get('START_TIME', time.time()),
        'detector_info': {
            'spam_keywords_count': len(detector.spam_keywords),
            'legitimate_keywords_count': len(detector.legitimate_keywords),
            'pattern_rules_count': len(detector.suspicious_patterns)
        },
        'supported_features': [
            'single_email_detection',
            'batch_detection',
            'detailed_analysis',
            'feature_extraction',
            'confidence_scoring'
        ]
    }
    
    return jsonify(stats)


def _get_risk_level(spam_score: float) -> str:
    """
    Convert spam score to risk level
    
    Args:
        spam_score: Numerical spam score
        
    Returns:
        Risk level string
    """
    if spam_score >= 8:
        return 'VERY_HIGH'
    elif spam_score >= 5:
        return 'HIGH'
    elif spam_score >= 2:
        return 'MEDIUM'
    elif spam_score >= 0:
        return 'LOW'
    else:
        return 'VERY_LOW'


def _get_recommendations(result: dict) -> list:
    """
    Generate recommendations based on analysis result
    
    Args:
        result: Spam detection result
        
    Returns:
        List of recommendations
    """
    recommendations = []
    
    if result['is_spam']:
        recommendations.extend([
            "Do not click any links in this email",
            "Do not download any attachments",
            "Do not reply with personal information",
            "Consider blocking the sender",
            "Report as spam to your email provider"
        ])
        
        if result['spam_score'] > 8:
            recommendations.append("This email shows very high spam indicators - exercise extreme caution")
    else:
        if result['confidence'] < 0.5:
            recommendations.append("Email appears legitimate but some suspicious elements detected - verify sender if unsure")
        else:
            recommendations.append("Email appears to be legitimate")
    
    return recommendations
