"""
Data Validation Module
Input validation and sanitization for API requests.
"""
import re
from typing import Dict, List, Optional, Any


def validate_email_data(data: Dict[str, Any]) -> Optional[str]:
    """
    Validate email data for single email detection
    
    Args:
        data: Dictionary containing email data
        
    Returns:
        Error message if validation fails, None if valid
    """
    if not isinstance(data, dict):
        return "Request data must be a JSON object"
    
    # Check required fields
    if 'text' not in data:
        return "Missing required field: 'text'"
    
    email_text = data.get('text')
    subject = data.get('subject', '')
    
    # Validate email text
    if not isinstance(email_text, str):
        return "Field 'text' must be a string"
    
    if len(email_text.strip()) == 0:
        return "Field 'text' cannot be empty"
    
    if len(email_text) > 50000:  # 50KB limit
        return "Email text too long (maximum 50,000 characters)"
    
    # Validate subject if provided
    if subject is not None:
        if not isinstance(subject, str):
            return "Field 'subject' must be a string"
        
        if len(subject) > 1000:  # 1KB limit for subject
            return "Subject too long (maximum 1,000 characters)"
    
    # Check for potentially malicious content
    if _contains_malicious_patterns(email_text + " " + str(subject)):
        return "Content contains potentially malicious patterns"
    
    return None


def validate_batch_data(data: Dict[str, Any]) -> Optional[str]:
    """
    Validate batch email data
    
    Args:
        data: Dictionary containing batch email data
        
    Returns:
        Error message if validation fails, None if valid
    """
    if not isinstance(data, dict):
        return "Request data must be a JSON object"
    
    # Check required fields
    if 'emails' not in data:
        return "Missing required field: 'emails'"
    
    emails = data.get('emails')
    
    if not isinstance(emails, list):
        return "Field 'emails' must be an array"
    
    if len(emails) == 0:
        return "Email array cannot be empty"
    
    if len(emails) > 1000:  # Reasonable batch size limit
        return "Too many emails in batch (maximum 1000)"
    
    # Validate each email in the batch
    for i, email in enumerate(emails):
        if not isinstance(email, dict):
            return f"Email at index {i} must be an object"
        
        # Validate individual email
        email_error = validate_email_data(email)
        if email_error:
            return f"Email at index {i}: {email_error}"
        
        # Check for ID field (optional but useful for tracking)
        if 'id' in email and not isinstance(email['id'], (str, int)):
            return f"Email at index {i}: 'id' field must be a string or number"
    
    return None


def validate_analysis_data(data: Dict[str, Any]) -> Optional[str]:
    """
    Validate data for detailed analysis endpoint
    
    Args:
        data: Dictionary containing analysis request data
        
    Returns:
        Error message if validation fails, None if valid
    """
    # First validate as regular email data
    email_error = validate_email_data(data)
    if email_error:
        return email_error
    
    # Validate analysis-specific options
    include_features = data.get('include_features')
    include_explanations = data.get('include_explanations')
    
    if include_features is not None and not isinstance(include_features, bool):
        return "Field 'include_features' must be a boolean"
    
    if include_explanations is not None and not isinstance(include_explanations, bool):
        return "Field 'include_explanations' must be a boolean"
    
    return None


def sanitize_text(text: str) -> str:
    """
    Sanitize input text by removing or escaping potentially dangerous content
    
    Args:
        text: Input text to sanitize
        
    Returns:
        Sanitized text
    """
    if not isinstance(text, str):
        return ""
    
    # Remove null bytes
    text = text.replace('\x00', '')
    
    # Limit line length to prevent extremely long lines
    lines = text.split('\n')
    sanitized_lines = []
    
    for line in lines:
        if len(line) > 10000:  # Truncate very long lines
            line = line[:10000] + "... [truncated]"
        sanitized_lines.append(line)
    
    # Limit total number of lines
    if len(sanitized_lines) > 1000:
        sanitized_lines = sanitized_lines[:1000] + ["... [remaining lines truncated]"]
    
    return '\n'.join(sanitized_lines)


def validate_content_length(text: str, max_length: int = 50000) -> bool:
    """
    Validate that content doesn't exceed maximum length
    
    Args:
        text: Text to validate
        max_length: Maximum allowed length
        
    Returns:
        True if valid, False otherwise
    """
    return len(text) <= max_length


def validate_email_format(email: str) -> bool:
    """
    Validate email address format
    
    Args:
        email: Email address to validate
        
    Returns:
        True if valid format, False otherwise
    """
    if not isinstance(email, str):
        return False
    
    # Basic email regex pattern
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


def validate_ip_address(ip: str) -> bool:
    """
    Validate IPv4 address format
    
    Args:
        ip: IP address to validate
        
    Returns:
        True if valid format, False otherwise
    """
    if not isinstance(ip, str):
        return False
    
    try:
        parts = ip.split('.')
        if len(parts) != 4:
            return False
        
        for part in parts:
            if not part.isdigit():
                return False
            if not 0 <= int(part) <= 255:
                return False
        
        return True
    except ValueError:
        return False


def _contains_malicious_patterns(text: str) -> bool:
    """
    Check for potentially malicious patterns in text
    
    Args:
        text: Text to check
        
    Returns:
        True if malicious patterns found, False otherwise
    """
    if not isinstance(text, str):
        return False
    
    # Convert to lowercase for case-insensitive matching
    text_lower = text.lower()
    
    # Patterns that might indicate malicious content
    malicious_patterns = [
        # Script injection attempts
        r'<script[^>]*>',
        r'javascript:',
        r'vbscript:',
        r'onload\s*=',
        r'onerror\s*=',
        r'onclick\s*=',
        
        # SQL injection attempts
        r'union\s+select',
        r'drop\s+table',
        r'insert\s+into',
        r'delete\s+from',
        
        # Command injection
        r';\s*rm\s+',
        r';\s*del\s+',
        r'\|\s*nc\s+',
        
        # Null bytes and control characters
        r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]',
    ]
    
    for pattern in malicious_patterns:
        if re.search(pattern, text_lower, re.IGNORECASE):
            return True
    
    # Check for excessive repeated characters (possible DoS attempt)
    if re.search(r'(.)\1{1000,}', text):
        return True
    
    # Check for extremely long words (possible buffer overflow attempt)
    words = text.split()
    for word in words:
        if len(word) > 1000:
            return True
    
    return False


def normalize_whitespace(text: str) -> str:
    """
    Normalize whitespace in text
    
    Args:
        text: Text to normalize
        
    Returns:
        Text with normalized whitespace
    """
    if not isinstance(text, str):
        return ""
    
    # Replace multiple whitespace characters with single space
    text = re.sub(r'\s+', ' ', text)
    
    # Remove leading and trailing whitespace
    text = text.strip()
    
    return text


def extract_urls(text: str) -> List[str]:
    """
    Extract URLs from text for validation
    
    Args:
        text: Text to extract URLs from
        
    Returns:
        List of URLs found in text
    """
    if not isinstance(text, str):
        return []
    
    # URL pattern
    url_pattern = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
    
    urls = re.findall(url_pattern, text, re.IGNORECASE)
    
    # Limit number of URLs to prevent abuse
    return urls[:50]  # Maximum 50 URLs per email


def validate_file_extension(filename: str, allowed_extensions: List[str]) -> bool:
    """
    Validate file extension
    
    Args:
        filename: Name of the file
        allowed_extensions: List of allowed extensions
        
    Returns:
        True if extension is allowed, False otherwise
    """
    if not isinstance(filename, str) or not filename:
        return False
    
    extension = filename.lower().split('.')[-1] if '.' in filename else ''
    return extension in [ext.lower() for ext in allowed_extensions]


class ValidationError(Exception):
    """Custom exception for validation errors"""
    pass


def validate_and_sanitize_email(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate and sanitize email data in one step
    
    Args:
        data: Raw email data
        
    Returns:
        Sanitized email data
        
    Raises:
        ValidationError: If validation fails
    """
    # Validate first
    error = validate_email_data(data)
    if error:
        raise ValidationError(error)
    
    # Sanitize
    sanitized_data = {
        'text': sanitize_text(data.get('text', '')),
        'subject': sanitize_text(data.get('subject', ''))
    }
    
    # Preserve other fields that might be present
    for key, value in data.items():
        if key not in ['text', 'subject']:
            sanitized_data[key] = value
    
    return sanitized_data