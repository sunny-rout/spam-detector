import re
from typing import Dict, List
import math


class SpamDetector:
    """
    Simple spam detection using Naive Bayes-like scoring
    """
    
    def __init__(self):
        """Initialize the spam detector with predefined patterns and weights"""
        
        # Spam keywords with weights (higher = more spammy)
        self.spam_keywords = {
            # Money-related
            'free': 3.0, 'money': 2.5, 'cash': 2.5, 'prize': 2.8, 'winner': 2.8,
            'lottery': 3.2, 'jackpot': 3.0, 'million': 2.7, 'dollars': 2.3,
            'earn': 2.2, 'income': 2.1, 'profit': 2.3, 'investment': 2.0,
            
            # Urgency words
            'urgent': 2.8, 'immediate': 2.6, 'asap': 2.5, 'deadline': 2.2,
            'expire': 2.4, 'limited': 2.3, 'hurry': 2.5, 'quick': 2.1,
            
            # Sales/Marketing
            'offer': 2.2, 'deal': 2.1, 'discount': 2.3, 'sale': 2.0,
            'promotion': 2.1, 'special': 1.8, 'exclusive': 2.4,
            
            # Suspicious words
            'click': 2.6, 'here': 1.9, 'now': 2.0, 'guaranteed': 2.9,
            'risk-free': 2.7, 'no-obligation': 2.5, 'trial': 2.1,
            
            # Adult content
            'adult': 3.0, 'xxx': 3.5, 'sex': 3.2, 'dating': 2.8,
            
            # Medical/Pharmaceutical
            'viagra': 3.8, 'pills': 3.2, 'medication': 2.8, 'pharmacy': 2.9,
            'prescription': 2.7, 'doctor': 1.8, 'medical': 1.7,
            
            # Technology scams
            'virus': 2.9, 'security': 2.2, 'alert': 2.5, 'warning': 2.3,
            'infected': 3.1, 'download': 2.4, 'update': 2.0,
            
            # Nigerian prince type scams
            'beneficiary': 3.5, 'inheritance': 3.3, 'deceased': 3.2,
            'transfer': 2.8, 'bank': 2.1, 'account': 2.0, 'fund': 2.6
        }
        
        # Legitimate keywords (negative weights - reduce spam score)
        self.legitimate_keywords = {
            'unsubscribe': -1.5, 'newsletter': -1.0, 'subscription': -1.0,
            'receipt': -2.0, 'invoice': -1.8, 'order': -1.5, 'delivery': -1.3,
            'meeting': -1.8, 'conference': -1.5, 'schedule': -1.2,
            'team': -1.0, 'project': -1.2, 'report': -1.5, 'update': -0.8,
            'thank': -1.5, 'regards': -1.0, 'sincerely': -1.2
        }
        
        # Suspicious patterns (regex patterns with weights)
        self.suspicious_patterns = [
            (r'\b\d+%\s*off\b', 2.2),  # "50% off"
            (r'\$\d+', 2.0),  # Dollar amounts
            (r'\b\d+\s*days?\s*only\b', 2.5),  # "3 days only"
            (r'!!+', 2.8),  # Multiple exclamation marks
            (r'[A-Z]{3,}', 1.8),  # Words in ALL CAPS (3+ chars)
            (r'click\s+here', 3.0),  # "click here"
            (r'act\s+now', 2.7),  # "act now"
            (r'call\s+now', 2.6),  # "call now"
            (r'\bfwd?\b', 2.3),  # "fwd" or "fw"
            (r're:\s*re:', 2.0),  # Multiple "Re:" 
            (r'[^\w\s]{3,}', 1.5),  # Multiple special characters
        ]
        
    def preprocess_text(self, text: str) -> str:
        """
        Preprocess email text for analysis
        
        Args:
            text: Raw email text
            
        Returns:
            Processed text
        """
        if not text:
            return ""
            
        # Convert to lowercase
        text = text.lower()
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove HTML tags if present
        text = re.sub(r'<[^>]+>', '', text)
        
        return text.strip()
    
    def extract_features(self, text: str) -> Dict:
        """
        Extract features from email text
        
        Args:
            text: Email text
            
        Returns:
            Dictionary of extracted features
        """
        processed_text = self.preprocess_text(text)
        
        features = {
            'word_count': len(processed_text.split()),
            'char_count': len(processed_text),
            'exclamation_count': processed_text.count('!'),
            'question_count': processed_text.count('?'),
            'dollar_sign_count': processed_text.count('$'),
            'percentage_count': processed_text.count('%'),
            'caps_ratio': self._calculate_caps_ratio(text),
            'number_count': len(re.findall(r'\d+', processed_text)),
            'url_count': len(re.findall(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', processed_text)),
            'email_count': len(re.findall(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', processed_text))
        }
        
        return features
    
    def _calculate_caps_ratio(self, text: str) -> float:
        """Calculate ratio of uppercase letters to total letters"""
        if not text:
            return 0.0
        
        letters = [c for c in text if c.isalpha()]
        if not letters:
            return 0.0
        
        caps = [c for c in letters if c.isupper()]
        return len(caps) / len(letters)
    
    def calculate_keyword_score(self, text: str) -> float:
        """
        Calculate spam score based on keywords
        
        Args:
            text: Email text
            
        Returns:
            Keyword-based spam score
        """
        processed_text = self.preprocess_text(text)
        words = processed_text.split()
        
        score = 0.0
        word_count = len(words)
        
        if word_count == 0:
            return 0.0
        
        # Check spam keywords
        for word in words:
            word_clean = re.sub(r'[^\w]', '', word)
            if word_clean in self.spam_keywords:
                score += self.spam_keywords[word_clean]
            elif word_clean in self.legitimate_keywords:
                score += self.legitimate_keywords[word_clean]
        
        # Normalize by word count to handle varying email lengths
        normalized_score = score / math.sqrt(word_count)
        
        return normalized_score
    
    def calculate_pattern_score(self, text: str) -> float:
        """
        Calculate spam score based on suspicious patterns
        
        Args:
            text: Email text
            
        Returns:
            Pattern-based spam score
        """
        score = 0.0
        
        for pattern, weight in self.suspicious_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            score += len(matches) * weight
        
        return score
    
    def detect_spam(self, email_text: str, subject: str = "") -> Dict:
        """
        Main spam detection method
        
        Args:
            email_text: Email body text
            subject: Email subject line
            
        Returns:
            Dictionary with detection results
        """
        # Combine subject and body for analysis
        full_text = f"{subject} {email_text}".strip()
        
        if not full_text:
            return {
                'is_spam': False,
                'confidence': 0.0,
                'spam_score': 0.0,
                'features': {},
                'explanation': 'Empty email content'
            }
        
        # Extract features
        features = self.extract_features(full_text)
        
        # Calculate different types of scores
        keyword_score = self.calculate_keyword_score(full_text)
        pattern_score = self.calculate_pattern_score(full_text)
        
        # Feature-based scoring
        feature_score = 0.0
        
        # High caps ratio is suspicious
        if features['caps_ratio'] > 0.3:
            feature_score += 2.5 * features['caps_ratio']
        
        # Too many exclamation marks
        if features['exclamation_count'] > 2:
            feature_score += 1.5 * features['exclamation_count']
        
        # Multiple dollar signs
        if features['dollar_sign_count'] > 1:
            feature_score += 2.0 * features['dollar_sign_count']
        
        # Multiple URLs might be suspicious
        if features['url_count'] > 3:
            feature_score += 1.5 * features['url_count']
        
        # Very short emails with spam keywords are suspicious
        if features['word_count'] < 20 and keyword_score > 2:
            feature_score += 2.0
        
        # Combine all scores
        total_score = keyword_score + pattern_score + feature_score
        
        # Determine if spam (threshold can be adjusted)
        spam_threshold = 5.0
        is_spam = total_score >= spam_threshold
        
        # Calculate confidence (0-1 scale)
        confidence = min(abs(total_score) / 10.0, 1.0)
        
        # Generate explanation
        explanation = self._generate_explanation(
            keyword_score, pattern_score, feature_score, features
        )
        
        return {
            'is_spam': is_spam,
            'confidence': round(confidence, 3),
            'spam_score': round(total_score, 3),
            'features': features,
            'explanation': explanation,
            'scores': {
                'keyword_score': round(keyword_score, 3),
                'pattern_score': round(pattern_score, 3),
                'feature_score': round(feature_score, 3)
            }
        }
    
    def _generate_explanation(self, keyword_score: float, pattern_score: float, 
                            feature_score: float, features: Dict) -> str:
        """Generate human-readable explanation of the decision"""
        
        explanations = []
        
        if keyword_score > 3:
            explanations.append("Contains multiple spam-related keywords")
        elif keyword_score > 1:
            explanations.append("Contains some spam-related keywords")
        elif keyword_score < -1:
            explanations.append("Contains legitimate business keywords")
        
        if pattern_score > 2:
            explanations.append("Matches suspicious patterns (excessive punctuation, caps, etc.)")
        
        if features['caps_ratio'] > 0.3:
            explanations.append(f"High ratio of capital letters ({features['caps_ratio']:.1%})")
        
        if features['exclamation_count'] > 3:
            explanations.append(f"Excessive exclamation marks ({features['exclamation_count']})")
        
        if features['url_count'] > 3:
            explanations.append(f"Multiple URLs ({features['url_count']})")
        
        if not explanations:
            explanations.append("Email appears to be legitimate")
        
        return "; ".join(explanations)
    
    def batch_detect(self, emails: List[Dict]) -> List[Dict]:
        """
        Detect spam for multiple emails
        
        Args:
            emails: List of email dictionaries with 'text' and optional 'subject'
            
        Returns:
            List of detection results
        """
        results = []
        
        for email in emails:
            text = email.get('text', '')
            subject = email.get('subject', '')
            
            result = self.detect_spam(text, subject)
            result['email_id'] = email.get('id', len(results))
            
            results.append(result)
        
        return results