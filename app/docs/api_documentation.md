# API Documentation - Spam Email Detector

## Overview

The Spam Email Detector API provides enterprise-grade email spam detection capabilities through RESTful endpoints. This documentation covers all available endpoints, request/response formats, authentication, rate limiting, and error handling.

## Base Information

- **Base URL**: `https://api.spamdetector.com/api/v1` (production) or `http://localhost:5000/api/v1` (development)
- **Protocol**: HTTPS (production), HTTP (development)
- **Content-Type**: `application/json`
- **Rate Limiting**: 1000 requests per hour (configurable)
- **API Version**: 1.0.0

## Authentication

Currently, the API operates without authentication for demonstration purposes. For production deployment, implement one of the following:

- **API Keys**: Header-based authentication
- **OAuth 2.0**: Bearer token authentication
- **JWT Tokens**: JSON Web Token authentication

Example with API key (when implemented):
```http
Authorization: Bearer your-api-key-here
```

## Endpoints

### 1. Health Check

Check API health and status.

**Endpoint:** `GET /health`

**Description:** Returns the current status of the API service, useful for load balancer health checks and monitoring.

**Parameters:** None

**Response:**
```json
{
  "status": "healthy",
  "timestamp": 1692720000.123,
  "version": "1.0.0"
}
```

**Status Codes:**
- `200`: Service is healthy
- `503`: Service unavailable

**Example:**
```bash
curl -X GET https://api.spamdetector.com/api/v1/health
```

### 2. Single Email Detection

Analyze a single email for spam indicators.

**Endpoint:** `POST /detect`

**Description:** Analyzes an individual email and returns spam classification, confidence score, and detailed analysis.

**Request Body:**
```json
{
  "text": "string (required, max 50,000 chars)",
  "subject": "string (optional, max 1,000 chars)"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "is_spam": boolean,
    "confidence": float (0.0-1.0),
    "spam_score": float,
    "explanation": "string",
    "features": {
      "word_count": integer,
      "char_count": integer,
      "exclamation_count": integer,
      "question_count": integer,
      "dollar_sign_count": integer,
      "percentage_count": integer,
      "caps_ratio": float (0.0-1.0),
      "number_count": integer,
      "url_count": integer,
      "email_count": integer
    },
    "scores": {
      "keyword_score": float,
      "pattern_score": float,
      "feature_score": float
    }
  },
  "metadata": {
    "processing_time_ms": float,
    "timestamp": float,
    "api_version": "string"
  }
}
```

**Status Codes:**
- `200`: Success
- `400`: Invalid request (missing fields, invalid data)
- `413`: Payload too large
- `429`: Rate limit exceeded
- `500`: Internal server error

**Examples:**

**Spam Email:**
```bash
curl -X POST https://api.spamdetector.com/api/v1/detect \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Congratulations! You have won $1,000,000! Click here to claim your prize immediately!",
    "subject": "URGENT: You are a WINNER!!!"
  }'
```

**Legitimate Email:**
```bash
curl -X POST https://api.spamdetector.com/api/v1/detect \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Thank you for your order. Your receipt is attached. If you have any questions, please contact our support team.",
    "subject": "Order Confirmation - Invoice #12345"
  }'
```

### 3. Batch Email Detection

Analyze multiple emails simultaneously.

**Endpoint:** `POST /detect/batch`

**Description:** Processes multiple emails in a single request, returning results for each email plus summary statistics.

**Request Body:**
```json
{
  "emails": [
    {
      "id": "string or number (optional)",
      "text": "string (required, max 50,000 chars)",
      "subject": "string (optional, max 1,000 chars)"
    }
  ]
}
```

**Constraints:**
- Maximum 100 emails per batch (configurable)
- Each email follows single detection validation rules

**Response:**
```json
{
  "success": true,
  "data": {
    "results": [
      {
        "email_id": "string or number",
        "is_spam": boolean,
        "confidence": float,
        "spam_score": float,
        "explanation": "string",
        "features": { /* feature object */ },
        "scores": { /* scores object */ }
      }
    ],
    "summary": {
      "total_emails": integer,
      "spam_detected": integer,
      "ham_detected": integer,
      "spam_percentage": float
    }
  },
  "metadata": {
    "processing_time_ms": float,
    "emails_per_second": float,
    "timestamp": float,
    "api_version": "string"
  }
}
```

**Example:**
```bash
curl -X POST https://api.spamdetector.com/api/v1/detect/batch \
  -H "Content-Type: application/json" \
  -d '{
    "emails": [
      {
        "id": "email_1",
        "text": "Team meeting tomorrow at 2 PM in conference room A. Please bring your project updates.",
        "subject": "Team Meeting Tomorrow"
      },
      {
        "id": "email_2",
        "text": "FREE VIAGRA! Best prices online! No prescription needed! Order now and save big!",
        "subject": "Special Pharmacy Deal!!!"
      },
      {
        "id": "email_3",
        "text": "Your monthly newsletter is ready. Click here to view this month\'s featured articles and updates.",
        "subject": "Monthly Newsletter - August 2025"
      }
    ]
  }'
```

### 4. Detailed Email Analysis

Get comprehensive analysis with detailed explanations and recommendations.

**Endpoint:** `POST /analyze`

**Description:** Provides in-depth analysis including risk assessment, feature breakdown, and actionable recommendations.

**Request Body:**
```json
{
  "text": "string (required, max 50,000 chars)",
  "subject": "string (optional, max 1,000 chars)",
  "include_features": boolean (optional, default: true),
  "include_explanations": boolean (optional, default: true)
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "classification": {
      "is_spam": boolean,
      "confidence": float,
      "spam_score": float
    },
    "risk_level": "VERY_LOW|LOW|MEDIUM|HIGH|VERY_HIGH",
    "features": { /* feature object (if requested) */ },
    "scores": { /* scores object (if requested) */ },
    "explanation": "string (if requested)",
    "recommendations": [
      "string array of recommendations"
    ]
  },
  "metadata": {
    "processing_time_ms": float,
    "timestamp": float,
    "api_version": "string"
  }
}
```

**Risk Levels:**
- `VERY_LOW`: Score < 0 (highly legitimate)
- `LOW`: Score 0-2 (likely legitimate)
- `MEDIUM`: Score 2-5 (uncertain, manual review suggested)
- `HIGH`: Score 5-8 (likely spam)
- `VERY_HIGH`: Score >= 8 (almost certainly spam)

**Example:**
```bash
curl -X POST https://api.spamdetector.com/api/v1/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Click here for amazing deals! Limited time offer - 90% off everything! Free shipping worldwide!",
    "subject": "DONT MISS OUT!!!",
    "include_features": true,
    "include_explanations": true
  }'
```

### 5. API Statistics

Get API usage and detector information.

**Endpoint:** `GET /stats`

**Description:** Returns API statistics, detector configuration, and supported features.

**Parameters:** None

**Response:**
```json
{
  "api_version": "string",
  "uptime_seconds": float,
  "detector_info": {
    "spam_keywords_count": integer,
    "legitimate_keywords_count": integer,
    "pattern_rules_count": integer
  },
  "supported_features": [
    "single_email_detection",
    "batch_detection",
    "detailed_analysis",
    "feature_extraction",
    "confidence_scoring"
  ]
}
```

**Example:**
```bash
curl -X GET https://api.spamdetector.com/api/v1/stats
```

## Error Handling

### Error Response Format

All errors follow a consistent format:

```json
{
  "error": "Error Type",
  "message": "Human-readable error description",
  "status_code": integer,
  "timestamp": float,
  "additional_info": "object (optional)"
}
```

### Common Error Codes

| Status Code | Error Type | Description |
|-------------|------------|-------------|
| 400 | Bad Request | Invalid request format or missing required fields |
| 401 | Unauthorized | Authentication required (when auth is enabled) |
| 403 | Forbidden | Insufficient permissions |
| 404 | Not Found | Endpoint does not exist |
| 405 | Method Not Allowed | HTTP method not supported for endpoint |
| 413 | Payload Too Large | Request body exceeds size limits |
| 415 | Unsupported Media Type | Content-Type must be application/json |
| 422 | Unprocessable Entity | Valid JSON but semantic errors |
| 429 | Too Many Requests | Rate limit exceeded |
| 500 | Internal Server Error | Server-side error |
| 503 | Service Unavailable | Service temporarily down |

### Error Examples

**400 Bad Request:**
```json
{
  "error": "Bad Request",
  "message": "Missing required field: 'text'",
  "status_code": 400,
  "timestamp": 1692720000.123
}
```

**429 Rate Limit Exceeded:**
```json
{
  "error": "Too Many Requests",
  "message": "Rate limit exceeded. Please try again later",
  "status_code": 429,
  "timestamp": 1692720000.123,
  "retry_after": 3600
}
```

## Rate Limiting

### Default Limits

- **Single Detection**: 1000 requests per hour
- **Batch Detection**: 100 requests per hour
- **Analysis**: 500 requests per hour
- **Health/Stats**: Unlimited

### Rate Limit Headers

Rate limit information is included in response headers:

```http
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 999
X-RateLimit-Reset: 1692723600
```

### Exceeding Limits

When rate limits are exceeded:
1. API returns 429 status code
2. Response includes `retry_after` in seconds
3. Security logging captures the event
4. Client should implement exponential backoff

## Data Formats

### Text Content Guidelines

**Email Text:**
- Maximum length: 50,000 characters
- Encoding: UTF-8
- Line breaks: Preserved in analysis
- HTML tags: Stripped during processing
- Special characters: Handled safely

**Email Subject:**
- Maximum length: 1,000 characters
- Optional field
- Used in combined analysis with body text

### Timestamp Format

All timestamps are Unix timestamps (seconds since epoch) with millisecond precision:
```json
{
  "timestamp": 1692720000.123
}
```

### Confidence Scores

Confidence scores range from 0.0 to 1.0:
- `0.0 - 0.3`: Low confidence
- `0.3 - 0.7`: Medium confidence  
- `0.7 - 1.0`: High confidence

### Spam Scores

Spam scores are unbounded floats:
- Negative values: Legitimate indicators
- `0 - 5`: Low to medium spam likelihood
- `5+`: High spam likelihood
- `8+`: Very high spam likelihood

## Security Considerations

### Input Validation

All inputs are validated for:
- **Size limits**: Text and subject length restrictions
- **Malicious content**: Script injection, SQL injection attempts
- **Character encoding**: UTF-8 validation
- **Content structure**: JSON format validation

### Malicious Content Detection

The API detects and blocks:
- Script injection attempts (`<script>`, `javascript:`)
- SQL injection patterns (`UNION SELECT`, `DROP TABLE`)
- Command injection (`rm`, `del`, `nc`)
- Buffer overflow attempts (extremely long words)
- DoS attempts (excessive repeated characters)

### Privacy

- **No Data Persistence**: Email content is not stored
- **Anonymized Logging**: Only metadata is logged, not content
- **In-Memory Processing**: All analysis happens in memory
- **No External Calls**: No data sent to third-party services

## SDKs and Integration

### Python SDK Example

```python
import requests

class SpamDetectorClient:
    def __init__(self, base_url, api_key=None):
        self.base_url = base_url
        self.headers = {'Content-Type': 'application/json'}
        if api_key:
            self.headers['Authorization'] = f'Bearer {api_key}'
    
    def detect_spam(self, text, subject=None):
        data = {'text': text}
        if subject:
            data['subject'] = subject
        
        response = requests.post(
            f'{self.base_url}/detect',
            json=data,
            headers=self.headers
        )
        return response.json()
    
    def batch_detect(self, emails):
        response = requests.post(
            f'{self.base_url}/detect/batch',
            json={'emails': emails},
            headers=self.headers
        )
        return response.json()

# Usage
client = SpamDetectorClient('https://api.spamdetector.com/api/v1')
result = client.detect_spam('Free money!', 'Win big!')
print(f"Is spam: {result['data']['is_spam']}")
```

### JavaScript/Node.js Example

```javascript
class SpamDetectorClient {
    constructor(baseUrl, apiKey = null) {
        this.baseUrl = baseUrl;
        this.headers = {
            'Content-Type': 'application/json'
        };
        if (apiKey) {
            this.headers['Authorization'] = `Bearer ${apiKey}`;
        }
    }
    
    async detectSpam(text, subject = null) {
        const data = { text };
        if (subject) data.subject = subject;
        
        const response = await fetch(`${this.baseUrl}/detect`, {
            method: 'POST',
            headers: this.headers,
            body: JSON.stringify(data)
        });
        
        return await response.json();
    }
    
    async batchDetect(emails) {
        const response = await fetch(`${this.baseUrl}/detect/batch`, {
            method: 'POST',
            headers: this.headers,
            body: JSON.stringify({ emails })
        });
        
        return await response.json();
    }
}

// Usage
const client = new SpamDetectorClient('https://api.spamdetector.com/api/v1');
client.detectSpam('Free money!', 'Win big!')
    .then(result => console.log('Is spam:', result.data.is_spam));
```

## Testing

### Test Emails

Use these sample emails for testing:

**High Spam Score:**
```json
{
  "text": "CONGRATULATIONS! You've won $1,000,000! Click here NOW to claim your prize! FREE MONEY waiting for you! Act fast - offer expires soon! No questions asked!",
  "subject": "URGENT: YOU'RE A WINNER!!! CLAIM NOW!!!"
}
```

**Medium Spam Score:**
```json
{
  "text": "Special offer just for you! 50% off all items this week only. Limited time deal. Visit our website for more details.",
  "subject": "Weekly Sale - Don't Miss Out"
}
```

**Low/No Spam Score:**
```json
{
  "text": "Thank you for your recent order. Your receipt is attached. If you have any questions about your purchase, please contact our customer service team.",
  "subject": "Order Confirmation - Receipt #12345"
}
```

### Performance Testing

Test API performance with tools like:
- **curl**: Multiple concurrent requests
- **Postman**: Collection-based testing
- **Custom scripts**: Language-specific load testing

## Monitoring and Observability

### Health Monitoring

Monitor these endpoints:
- `GET /health`: Basic health check
- `GET /stats`: Detailed statistics

### Metrics to Track

- **Response Time**: 95th percentile < 100ms
- **Throughput**: Requests per second
- **Error Rate**: < 1% error rate
- **Availability**: > 99.9% uptime

### Logging

The API provides structured logging:
- **Access logs**: All requests with timing
- **Error logs**: Failed requests with stack traces
- **Security logs**: Suspicious activity detection
- **Performance logs**: Slow queries and bottlenecks

## Support

For API support:
- **Documentation**: Check this documentation first
- **GitHub Issues**: Submit bug reports and feature requests
- **Email Support**: <-TODO->
- **Status Page**: <-TODO->

---

**API Version**: 1.0.0  
**Last Updated**: August 22, 2025  
**Documentation Version**: 1.0