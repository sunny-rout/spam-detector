"""
API Tests Module
Comprehensive test suite for all API endpoints.
"""
import pytest
import json
from app import create_app
from config import TestingConfig


@pytest.fixture
def app():
    """Create application for testing"""
    app = create_app(TestingConfig)
    return app


@pytest.fixture
def client(app):
    """Create test client"""
    return app.test_client()


@pytest.fixture
def runner(app):
    """Create test CLI runner"""
    return app.test_cli_runner()


class TestHealthEndpoint:
    """Test cases for health check endpoint"""
    
    def test_health_check(self, client):
        """Test health check endpoint"""
        response = client.get('/api/v1/health')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['status'] == 'healthy'
        assert 'timestamp' in data
        assert 'version' in data


class TestSpamDetectionEndpoint:
    """Test cases for spam detection endpoint"""
    
    def test_detect_spam_valid_request(self, client):
        """Test spam detection with valid spam email"""
        spam_email = {
            "text": "FREE MONEY! Click here now to claim your $1,000,000 prize! Act now before it expires!",
            "subject": "URGENT: You've Won!!!"
        }
        
        response = client.post('/api/v1/detect', 
                             data=json.dumps(spam_email),
                             content_type='application/json')
        
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['success'] is True
        assert 'data' in data
        assert data['data']['is_spam'] is True
        assert data['data']['confidence'] > 0.5
        assert data['data']['spam_score'] > 0
        
    def test_detect_ham_valid_request(self, client):
        """Test spam detection with valid legitimate email"""
        ham_email = {
            "text": "Thank you for your order. Your receipt is attached. Please let us know if you have any questions about your purchase.",
            "subject": "Order Confirmation - Invoice #12345"
        }
        
        response = client.post('/api/v1/detect',
                             data=json.dumps(ham_email),
                             content_type='application/json')
        
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['success'] is True
        assert data['data']['is_spam'] is False
        
    def test_detect_missing_text_field(self, client):
        """Test spam detection with missing text field"""
        invalid_email = {
            "subject": "Test Subject"
        }
        
        response = client.post('/api/v1/detect',
                             data=json.dumps(invalid_email),
                             content_type='application/json')
        
        assert response.status_code == 400
        
        data = json.loads(response.data)
        assert 'error' in data
        assert 'text' in data['message']
        
    def test_detect_empty_text_field(self, client):
        """Test spam detection with empty text field"""
        invalid_email = {
            "text": "",
            "subject": "Test Subject"
        }
        
        response = client.post('/api/v1/detect',
                             data=json.dumps(invalid_email),
                             content_type='application/json')
        
        assert response.status_code == 400
        
    def test_detect_invalid_json(self, client):
        """Test spam detection with invalid JSON"""
        response = client.post('/api/v1/detect',
                             data="invalid json",
                             content_type='application/json')
        
        assert response.status_code == 400
        
    def test_detect_oversized_content(self, client):
        """Test spam detection with oversized content"""
        oversized_email = {
            "text": "x" * 60000,  # Exceeds 50KB limit
            "subject": "Test"
        }
        
        response = client.post('/api/v1/detect',
                             data=json.dumps(oversized_email),
                             content_type='application/json')
        
        assert response.status_code == 400


class TestBatchDetectionEndpoint:
    """Test cases for batch spam detection endpoint"""
    
    def test_batch_detect_valid_request(self, client):
        """Test batch detection with valid emails"""
        batch_request = {
            "emails": [
                {
                    "id": "email_1",
                    "text": "Meeting tomorrow at 2 PM in conference room A",
                    "subject": "Team Meeting"
                },
                {
                    "id": "email_2",
                    "text": "FREE VIAGRA! No prescription needed! Order now!",
                    "subject": "Amazing deal!!!"
                },
                {
                    "id": "email_3",
                    "text": "Thank you for subscribing to our newsletter.",
                    "subject": "Welcome to Newsletter"
                }
            ]
        }
        
        response = client.post('/api/v1/detect/batch',
                             data=json.dumps(batch_request),
                             content_type='application/json')
        
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['success'] is True
        assert 'data' in data
        assert 'results' in data['data']
        assert 'summary' in data['data']
        
        results = data['data']['results']
        assert len(results) == 3
        
        # Check that results include spam detection
        spam_found = any(result['is_spam'] for result in results)
        assert spam_found
        
        # Check summary
        summary = data['data']['summary']
        assert summary['total_emails'] == 3
        assert summary['spam_detected'] + summary['ham_detected'] == 3
        
    def test_batch_detect_empty_array(self, client):
        """Test batch detection with empty email array"""
        batch_request = {
            "emails": []
        }
        
        response = client.post('/api/v1/detect/batch',
                             data=json.dumps(batch_request),
                             content_type='application/json')
        
        assert response.status_code == 400
        
    def test_batch_detect_missing_emails_field(self, client):
        """Test batch detection with missing emails field"""
        batch_request = {}
        
        response = client.post('/api/v1/detect/batch',
                             data=json.dumps(batch_request),
                             content_type='application/json')
        
        assert response.status_code == 400


class TestAnalyzeEndpoint:
    """Test cases for detailed analysis endpoint"""
    
    def test_analyze_with_features(self, client):
        """Test detailed analysis with feature extraction"""
        analyze_request = {
            "text": "Click here to claim your FREE prize! Limited time offer!!!",
            "subject": "WINNER WINNER!!!",
            "include_features": True,
            "include_explanations": True
        }
        
        response = client.post('/api/v1/analyze',
                             data=json.dumps(analyze_request),
                             content_type='application/json')
        
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['success'] is True
        assert 'data' in data
        
        analysis = data['data']
        assert 'classification' in analysis
        assert 'features' in analysis
        assert 'explanation' in analysis
        assert 'recommendations' in analysis
        assert 'risk_level' in analysis
        
        # Check classification
        classification = analysis['classification']
        assert 'is_spam' in classification
        assert 'confidence' in classification
        assert 'spam_score' in classification
        
        # Check features
        features = analysis['features']
        assert 'word_count' in features
        assert 'exclamation_count' in features
        assert 'caps_ratio' in features


class TestStatsEndpoint:
    """Test cases for statistics endpoint"""
    
    def test_get_stats(self, client):
        """Test statistics endpoint"""
        response = client.get('/api/v1/stats')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert 'api_version' in data
        assert 'uptime_seconds' in data
        assert 'detector_info' in data
        assert 'supported_features' in data
        
        detector_info = data['detector_info']
        assert 'spam_keywords_count' in detector_info
        assert 'legitimate_keywords_count' in detector_info
        assert 'pattern_rules_count' in detector_info


class TestErrorHandling:
    """Test cases for error handling"""
    
    def test_404_not_found(self, client):
        """Test 404 error handling"""
        response = client.get('/api/v1/nonexistent')
        assert response.status_code == 404
        
        data = json.loads(response.data)
        assert data['error'] == 'Not Found'
        assert 'available_endpoints' in data
        
    def test_405_method_not_allowed(self, client):
        """Test 405 error handling"""
        response = client.put('/api/v1/detect')
        assert response.status_code == 405
        
        data = json.loads(response.data)
        assert data['error'] == 'Method Not Allowed'
        
    def test_415_unsupported_media_type(self, client):
        """Test 415 error handling"""
        response = client.post('/api/v1/detect',
                             data="test",
                             content_type='text/plain')
        
        assert response.status_code == 415
        
        data = json.loads(response.data)
        assert data['error'] == 'Unsupported Media Type'
        assert 'supported_types' in data


if __name__ == '__main__':
    pytest.main([__file__])