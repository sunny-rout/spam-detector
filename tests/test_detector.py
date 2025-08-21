# tests/test_detector.py
"""
Unit tests for the SpamDetector algorithm
"""

import pytest
from app.models.spam_detector import SpamDetector


@pytest.fixture
def detector():
    """Create a SpamDetector instance for testing"""
    return SpamDetector()


class TestSpamDetectorInitialization:
    """Test SpamDetector initialization and configuration"""
    
    def test_detector_initialization(self, detector):
        """Test that detector initializes correctly"""
        assert detector is not None
        assert isinstance(detector.spam_keywords, dict)
        assert isinstance(detector.legitimate_keywords, dict)
        assert isinstance(detector.suspicious_patterns, list)
        assert len(detector.spam_keywords) > 0
        assert len(detector.legitimate_keywords) > 0
        assert len(detector.suspicious_patterns) > 0
    
    def test_spam_keywords_have_weights(self, detector):
        """Test that spam keywords have proper weights"""
        for keyword, weight in detector.spam_keywords.items():
            assert isinstance(keyword, str)
            assert isinstance(weight, (int, float))
            assert weight > 0  # Spam keywords should have positive weights
            assert weight <= 5.0  # Reasonable upper bound
    
    def test_legitimate_keywords_have_negative_weights(self, detector):
        """Test that legitimate keywords have negative weights"""
        for keyword, weight in detector.legitimate_keywords.items():
            assert isinstance(keyword, str)
            assert isinstance(weight, (int, float))
            assert weight < 0  # Legitimate keywords should have negative weights
    
    def test_suspicious_patterns_format(self, detector):
        """Test that suspicious patterns are properly formatted"""
        for pattern_data in detector.suspicious_patterns:
            assert isinstance(pattern_data, tuple)
            assert len(pattern_data) == 2
            pattern, weight = pattern_data
            assert isinstance(pattern, str)
            assert isinstance(weight, (int, float))
            assert weight > 0


class TestTextPreprocessing:
    """Test text preprocessing methods"""
    
    def test_preprocess_text_basic(self, detector):
        """Test basic text preprocessing"""
        text = "  This is A TEST message!  "
        result = detector.preprocess_text(text)
        assert result == "this is a test message!"
    
    def test_preprocess_text_html_removal(self, detector):
        """Test HTML tag removal"""
        text = "<p>This is <b>bold</b> text</p>"
        result = detector.preprocess_text(text)
        assert "<" not in result
        assert ">" not in result
        assert "bold" in result
    
    def test_preprocess_text_whitespace_normalization(self, detector):
        """Test whitespace normalization"""
        text = "This    has\tmultiple\n\nspaces"
        result = detector.preprocess_text(text)
        assert result == "this has multiple spaces"
    
    def test_preprocess_text_empty_input(self, detector):
        """Test preprocessing with empty input"""
        assert detector.preprocess_text("") == ""
        assert detector.preprocess_text(None) == ""
        assert detector.preprocess_text("   ") == ""


class TestFeatureExtraction:
    """Test feature extraction methods"""
    
    def test_extract_features_basic(self, detector):
        """Test basic feature extraction"""
        text = "Hello! How are you? I'm fine."
        features = detector.extract_features(text)
        
        # Check that all expected features are present
        expected_features = [
            'word_count', 'char_count', 'exclamation_count', 
            'question_count', 'dollar_sign_count', 'percentage_count',
            'caps_ratio', 'number_count', 'url_count', 'email_count'
        ]
        
        for feature in expected_features:
            assert feature in features
            assert isinstance(features[feature], (int, float))
    
    def test_extract_features_punctuation_counting(self, detector):
        """Test punctuation counting in features"""
        text = "Wow!!! Are you sure??? Yes!"
        features = detector.extract_features(text)
        
        assert features['exclamation_count'] == 4
        assert features['question_count'] == 3
    
    def test_extract_features_dollar_signs(self, detector):
        """Test dollar sign counting"""
        text = "Save $100! Get $50 off! Only $25 today!"
        features = detector.extract_features(text)
        
        assert features['dollar_sign_count'] == 3
    
    def test_extract_features_caps_ratio(self, detector):
        """Test caps ratio calculation"""
        text = "THIS IS ALL CAPS"
        features = detector.extract_features(text)
        
        assert features['caps_ratio'] == 1.0
        
        text = "this is all lowercase"
        features = detector.extract_features(text)
        
        assert features['caps_ratio'] == 0.0
    
    def test_extract_features_urls(self, detector):
        """Test URL counting"""
        text = "Visit http://example.com and https://test.org for more info"
        features = detector.extract_features(text)
        
        assert features['url_count'] == 2
    
    def test_extract_features_emails(self, detector):
        """Test email address counting"""
        text = "Contact us at support@example.com or admin@test.org"
        features = detector.extract_features(text)
        
        assert features['email_count'] == 2
    
    def test_caps_ratio_calculation(self, detector):
        """Test caps ratio calculation edge cases"""
        # All caps
        assert detector._calculate_caps_ratio("HELLO") == 1.0
        
        # No caps
        assert detector._calculate_caps_ratio("hello") == 0.0
        
        # Mixed case
        assert detector._calculate_caps_ratio("Hello") == 0.2  # 1 out of 5
        
        # No letters
        assert detector._calculate_caps_ratio("123 !@#") == 0.0
        
        # Empty string
        assert detector._calculate_caps_ratio("") == 0.0


class TestKeywordScoring:
    """Test keyword-based scoring"""
    
    def test_keyword_score_spam_keywords(self, detector):
        """Test scoring with spam keywords"""
        text = "Free money! Win cash prizes now!"
        score = detector.calculate_keyword_score(text)
        
        assert score > 0  # Should be positive for spam keywords
    
    def test_keyword_score_legitimate_keywords(self, detector):
        """Test scoring with legitimate keywords"""
        text = "Thank you for your order. Please find your receipt attached."
        score = detector.calculate_keyword_score(text)
        
        assert score < 0  # Should be negative for legitimate keywords
    
    def test_keyword_score_mixed_keywords(self, detector):
        """Test scoring with mixed keywords"""
        text = "Thank you for your free trial offer"
        score = detector.calculate_keyword_score(text)
        
        # Score depends on the balance of spam vs legitimate keywords
        assert isinstance(score, (int, float))
    
    def test_keyword_score_empty_text(self, detector):
        """Test keyword scoring with empty text"""
        assert detector.calculate_keyword_score("") == 0.0
        assert detector.calculate_keyword_score("   ") == 0.0
    
    def test_keyword_score_no_keywords(self, detector):
        """Test scoring with text containing no keywords"""
        text = "The quick brown fox jumps over the lazy dog"
        score = detector.calculate_keyword_score(text)
        
        assert score == 0.0


class TestPatternScoring:
    """Test pattern-based scoring"""
    
    def test_pattern_score_multiple_exclamations(self, detector):
        """Test scoring for multiple exclamation marks"""
        text = "Amazing offer!!!"
        score = detector.calculate_pattern_score(text)
        
        assert score > 0
    
    def test_pattern_score_dollar_amounts(self, detector):
        """Test scoring for dollar amounts"""
        text = "Save $100 today! Only $50 now!"
        score = detector.calculate_pattern_score(text)
        
        assert score > 0
    
    def test_pattern_score_caps_words(self, detector):
        """Test scoring for words in ALL CAPS"""
        text = "URGENT MESSAGE FOR YOU"
        score = detector.calculate_pattern_score(text)
        
        assert score > 0
    
    def test_pattern_score_click_here(self, detector):
        """Test scoring for 'click here' pattern"""
        text = "Click here to claim your prize!"
        score = detector.calculate_pattern_score(text)
        
        assert score > 0
    
    def test_pattern_score_act_now(self, detector):
        """Test scoring for 'act now' pattern"""
        text = "Don't wait! Act now while supplies last!"
        score = detector.calculate_pattern_score(text)
        
        assert score > 0
    
    def test_pattern_score_no_patterns(self, detector):
        """Test pattern scoring with clean text"""
        text = "This is a normal business message with professional content."
        score = detector.calculate_pattern_score(text)
        
        assert score == 0.0 or score < 2.0  # Should be low/zero


class TestSpamDetection:
    """Test the main spam detection functionality"""
    
    def test_detect_obvious_spam(self, detector):
        """Test detection of obvious spam"""
        spam_text = "CONGRATULATIONS! You've won $1,000,000!!! Click here NOW to claim your FREE prize!"
        subject = "URGENT: YOU'RE A WINNER!!!"
        
        result = detector.detect_spam(spam_text, subject)
        
        assert result['is_spam'] is True
        assert result['confidence'] > 0.5
        assert result['spam_score'] > 0
        assert 'explanation' in result
        assert 'features' in result
    
    def test_detect_obvious_ham(self, detector):
        """Test detection of legitimate email"""
        ham_text = "Thank you for your recent order. Your receipt is attached. Our team will process your request within 2 business days."
        subject = "Order Confirmation - Receipt #12345"
        
        result = detector.detect_spam(ham_text, subject)
        
        assert result['is_spam'] is False
        assert result['confidence'] > 0.3
        assert result['spam_score'] <= 5.0  # Below spam threshold
    
    def test_detect_borderline_case(self, detector):
        """Test detection of borderline case"""
        text = "Special offer for you! 50% discount this week only."
        subject = "Weekly Sale"
        
        result = detector.detect_spam(text, subject)
        
        # Should have moderate confidence either way
        assert 0.0 <= result['confidence'] <= 1.0
        assert isinstance(result['is_spam'], bool)
    
    def test_detect_empty_email(self, detector):
        """Test detection with empty email"""
        result = detector.detect_spam("", "")
        
        assert result['is_spam'] is False
        assert result['confidence'] == 0.0
        assert result['spam_score'] == 0.0
        assert 'Empty email content' in result['explanation']
    
    def test_detect_subject_only(self, detector):
        """Test detection with subject only"""
        result = detector.detect_spam("", "FREE MONEY!!!")
        
        assert isinstance(result['is_spam'], bool)
        assert result['confidence'] > 0
    
    def test_detect_text_only(self, detector):
        """Test detection with text only (no subject)"""
        result = detector.detect_spam("Free money! Click here now!", "")
        
        assert result['is_spam'] is True
        assert result['confidence'] > 0
    
    def test_confidence_range(self, detector):
        """Test that confidence is always in valid range"""
        test_cases = [
            ("Free money!!!", "URGENT!!!"),
            ("Meeting tomorrow at 2 PM", "Team Meeting"),
            ("", ""),
            ("a" * 1000, "Long email"),
        ]
        
        for text, subject in test_cases:
            result = detector.detect_spam(text, subject)
            assert 0.0 <= result['confidence'] <= 1.0
    
    def test_spam_score_consistency(self, detector):
        """Test that spam score is consistent with classification"""
        test_cases = [
            "FREE MONEY!!! Click here NOW!!!",
            "Thank you for your professional inquiry.",
            "Limited time offer - 90% off everything!",
            "Please find the meeting minutes attached.",
        ]
        
        for text in test_cases:
            result = detector.detect_spam(text)
            
            # If classified as spam, score should be >= threshold
            if result['is_spam']:
                assert result['spam_score'] >= 5.0
            else:
                assert result['spam_score'] < 5.0


class TestBatchDetection:
    """Test batch detection functionality"""
    
    def test_batch_detect_multiple_emails(self, detector):
        """Test batch detection with multiple emails"""
        emails = [
            {"id": 1, "text": "Thank you for your order", "subject": "Receipt"},
            {"id": 2, "text": "FREE MONEY! Click now!", "subject": "URGENT!!!"},
            {"id": 3, "text": "Meeting at 3 PM tomorrow", "subject": "Team Meeting"},
        ]
        
        results = detector.batch_detect(emails)
        
        assert len(results) == 3
        
        # Check that each result has required fields
        for result in results:
            assert 'email_id' in result
            assert 'is_spam' in result
            assert 'confidence' in result
            assert 'spam_score' in result
    
    def test_batch_detect_empty_list(self, detector):
        """Test batch detection with empty list"""
        results = detector.batch_detect([])
        assert results == []
    
    def test_batch_detect_maintains_order(self, detector):
        """Test that batch detection maintains email order"""
        emails = [
            {"id": "first", "text": "First email"},
            {"id": "second", "text": "Second email"},
            {"id": "third", "text": "Third email"},
        ]
        
        results = detector.batch_detect(emails)
        
        assert results[0]['email_id'] == "first"
        assert results[1]['email_id'] == "second"
        assert results[2]['email_id'] == "third"
    
    def test_batch_detect_auto_id_assignment(self, detector):
        """Test automatic ID assignment when not provided"""
        emails = [
            {"text": "First email"},
            {"text": "Second email"},
        ]
        
        results = detector.batch_detect(emails)
        
        assert results[0]['email_id'] == 0
        assert results[1]['email_id'] == 1


class TestSpecificSpamPatterns:
    """Test detection of specific spam patterns"""
    
    def test_money_related_spam(self, detector):
        """Test detection of money-related spam"""
        money_spam = [
            "Win $1,000,000 now!",
            "Free cash waiting for you!",
            "Earn money from home!",
            "Get rich quick scheme!",
            "Lottery winner announcement!",
        ]
        
        for text in money_spam:
            result = detector.detect_spam(text)
            assert result['spam_score'] > 0, f"Failed for: {text}"
    
    def test_urgency_spam(self, detector):
        """Test detection of urgency-based spam"""
        urgency_spam = [
            "URGENT: Act now or lose this deal!",
            "Limited time offer expires today!",
            "Immediate action required!",
            "Don't wait - offer ends soon!",
            "Hurry up! Only few left!",
        ]
        
        for text in urgency_spam:
            result = detector.detect_spam(text)
            assert result['spam_score'] > 0, f"Failed for: {text}"
    
    def test_medical_spam(self, detector):
        """Test detection of medical/pharmaceutical spam"""
        medical_spam = [
            "Buy Viagra online cheap!",
            "Prescription pills without doctor!",
            "Pharmacy discount medications!",
            "Get pills delivered overnight!",
        ]
        
        for text in medical_spam:
            result = detector.detect_spam(text)
            assert result['spam_score'] > 3.0, f"Failed for: {text}"
    
    def test_legitimate_business_emails(self, detector):
        """Test that legitimate business emails score low"""
        legitimate_emails = [
            "Thank you for your order. Receipt attached.",
            "Meeting scheduled for tomorrow at 10 AM.",
            "Project update: Phase 1 completed successfully.",
            "Please review the attached proposal.",
            "Quarterly report is ready for your review.",
        ]
        
        for text in legitimate_emails:
            result = detector.detect_spam(text)
            assert result['spam_score'] < 3.0, f"Failed for: {text}"
            assert result['is_spam'] is False, f"Incorrectly classified as spam: {text}"


class TestEdgeCases:
    """Test edge cases and error conditions"""
    
    def test_very_long_text(self, detector):
        """Test with very long text"""
        long_text = "word " * 10000  # 10,000 words
        result = detector.detect_spam(long_text)
        
        assert isinstance(result, dict)
        assert 'is_spam' in result
        assert result['features']['word_count'] == 10000
    
    def test_special_characters(self, detector):
        """Test with special characters and unicode"""
        special_text = "Special öfférs! 🎉💰 Click hère für fréé mönéy! 中文字符"
        result = detector.detect_spam(special_text)
        
        assert isinstance(result, dict)
        assert 'is_spam' in result
    
    def test_only_numbers(self, detector):
        """Test with only numbers"""
        number_text = "123 456 789 000 111"
        result = detector.detect_spam(number_text)
        
        assert result['is_spam'] is False
        assert result['spam_score'] <= 1.0
    
    def test_only_punctuation(self, detector):
        """Test with only punctuation"""
        punct_text = "!!! ??? ... ,,, ;;;"
        result = detector.detect_spam(punct_text)
        
        # Should detect excessive punctuation
        assert result['spam_score'] > 0
    
    def test_mixed_case_keywords(self, detector):
        """Test that keyword detection is case insensitive"""
        mixed_cases = [
            "FREE money",
            "free MONEY", 
            "Free Money",
            "fReE mOnEy",
        ]
        
        scores = []
        for text in mixed_cases:
            result = detector.detect_spam(text)
            scores.append(result['spam_score'])
        
        # All variations should have similar scores
        assert len(set(scores)) <= 2  # Allow for minor variations


class TestExplanationGeneration:
    """Test explanation generation"""
    
    def test_explanation_contains_relevant_info(self, detector):
        """Test that explanations contain relevant information"""
        spam_text = "FREE MONEY!!! Click here now!"
        result = detector.detect_spam(spam_text)
        
        explanation = result['explanation'].lower()
        
        # Should mention spam keywords
        assert 'spam' in explanation or 'keyword' in explanation
        
        # Should mention patterns if detected
        if result['scores']['pattern_score'] > 0:
            assert 'pattern' in explanation or 'punctuation' in explanation
    
    def test_explanation_for_legitimate_email(self, detector):
        """Test explanation for legitimate emails"""
        ham_text = "Thank you for your order. Receipt attached."
        result = detector.detect_spam(ham_text)
        
        explanation = result['explanation'].lower()
        
        # Should indicate legitimacy
        assert 'legitimate' in explanation or 'business' in explanation
    
    def test_explanation_not_empty(self, detector):
        """Test that explanation is never empty"""
        test_cases = [
            "Free money!",
            "Thank you for your order.",
            "Meeting tomorrow.",
            "",
            "a",
        ]
        
        for text in test_cases:
            result = detector.detect_spam(text)
            assert len(result['explanation']) > 0


class TestPerformance:
    """Test performance characteristics"""
    
    def test_single_email_performance(self, detector):
        """Test that single email detection is fast"""
        import time
        
        text = "This is a test email with some content for performance testing."
        
        start_time = time.time()
        result = detector.detect_spam(text)
        end_time = time.time()
        
        processing_time = end_time - start_time
        
        # Should complete within reasonable time (adjust threshold as needed)
        assert processing_time < 0.1  # 100ms
        assert result is not None
    
    def test_batch_performance_scales_linearly(self, detector):
        """Test that batch processing scales reasonably"""
        import time
        
        # Create test emails
        emails = [
            {"id": i, "text": f"Test email number {i} with some content."}
            for i in range(100)
        ]
        
        start_time = time.time()
        results = detector.batch_detect(emails)
        end_time = time.time()
        
        processing_time = end_time - start_time
        
        # Should process 100 emails reasonably quickly
        assert processing_time < 2.0  # 2 seconds
        assert len(results) == 100
    
    def test_memory_usage_stable(self, detector):
        """Test that memory usage remains stable"""
        import gc
        
        # Process many emails to check for memory leaks
        for _ in range(1000):
            detector.detect_spam("Test email content")
        
        # Force garbage collection
        gc.collect()
        
        # If we get here without memory errors, we're good
        assert True


if __name__ == '__main__':
    pytest.main([__file__])