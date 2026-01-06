"""
Threat Detection Module

This module implements AI/NLP-based threat detection algorithms
to identify spam and phishing emails.

Detection Methods:
1. Rule-based detection (heuristics)
2. Pattern matching (regex, keywords)
3. Behavioral analysis (sender patterns)
4. Content analysis (NLP techniques)

Academic Note: This demonstrates a hybrid approach combining
traditional rule-based systems with modern NLP techniques.
Production systems often use machine learning models trained
on labeled datasets.
"""

import logging
from typing import Dict, List
import re

from config.settings import settings

logger = logging.getLogger(__name__)


class ThreatDetector:
    """
    Multi-layered threat detection engine.
    
    This class implements various detection algorithms to identify
    spam and phishing attempts. It uses a scoring system where
    different indicators contribute to an overall threat score.
    
    Threat Score Scale: 0-100
    - 0-30: Safe
    - 31-70: Suspicious
    - 71-100: Spam/Phishing
    """
    
    def __init__(self):
        """Initialize threat detector"""
        self.max_score = 100
        
    def analyze_email(self, parsed_email: Dict, features: Dict) -> Dict:
        """
        Perform comprehensive threat analysis on an email.
        
        Args:
            parsed_email: Parsed email data
            features: Extracted features
            
        Returns:
            Dictionary with threat analysis results
        """
        try:
            # Initialize threat scores
            phishing_score = 0
            spam_score = 0
            threat_indicators = []
            
            # Run detection algorithms
            phishing_score, phishing_indicators = self._detect_phishing(parsed_email, features)
            spam_score, spam_indicators = self._detect_spam(parsed_email, features)
            
            # Combine indicators
            threat_indicators = phishing_indicators + spam_indicators
            
            # Calculate overall threat score (weighted average)
            # Phishing is weighted higher as it's more dangerous
            overall_score = int((phishing_score * 0.6) + (spam_score * 0.4))
            overall_score = min(overall_score, self.max_score)
            
            return {
                'overall_score': overall_score,
                'phishing_score': phishing_score,
                'spam_score': spam_score,
                'threat_indicators': threat_indicators,
                'is_safe': overall_score <= settings.SAFE_THRESHOLD,
                'is_suspicious': settings.SAFE_THRESHOLD < overall_score <= settings.SUSPICIOUS_THRESHOLD,
                'is_spam': overall_score > settings.SUSPICIOUS_THRESHOLD
            }
            
        except Exception as e:
            logger.error(f"Error analyzing email: {str(e)}")
            return {
                'overall_score': 0,
                'phishing_score': 0,
                'spam_score': 0,
                'threat_indicators': [],
                'is_safe': True,
                'is_suspicious': False,
                'is_spam': False
            }
            
    def _detect_phishing(self, email: Dict, features: Dict) -> tuple:
        """
        Detect phishing attempts.
        
        Phishing Indicators:
        1. Spoofed sender (display name mismatch)
        2. Credential requests
        3. Urgent language
        4. Suspicious URLs
        5. Domain mismatches
        
        Args:
            email: Parsed email
            features: Extracted features
            
        Returns:
            Tuple of (score, indicators)
        """
        score = 0
        indicators = []
        
        sender_features = features.get('sender_features', {})
        content_features = features.get('content_features', {})
        url_features = features.get('url_features', {})
        header_features = features.get('header_features', {})
        
        # Check for sender spoofing (HIGH RISK)
        if sender_features.get('has_name_mismatch'):
            score += 25
            indicators.append("Sender display name doesn't match email domain (possible spoofing)")
            
        # Check for credential requests (HIGH RISK)
        if content_features.get('credential_request_count', 0) > 0:
            score += 20
            indicators.append(f"Requests credentials ({content_features['credential_request_count']} instances)")
            
        # Check for phishing keywords (MEDIUM RISK)
        keyword_count = content_features.get('phishing_keyword_count', 0)
        if keyword_count > 0:
            score += min(keyword_count * 5, 20)  # Cap at 20
            matched = content_features.get('matched_keywords', [])
            indicators.append(f"Contains phishing keywords: {', '.join(matched[:3])}")
            
        # Check for urgency tactics (MEDIUM RISK)
        if content_features.get('urgency_count', 0) >= 2:
            score += 15
            indicators.append("Uses urgent/pressure language")
            
        # Check for suspicious URLs (HIGH RISK)
        if url_features.get('ip_address_count', 0) > 0:
            score += 20
            indicators.append("Contains URLs with IP addresses instead of domains")
            
        if url_features.get('shortened_url_count', 0) > 0:
            score += 10
            indicators.append("Contains shortened URLs (potential redirect)")
            
        if url_features.get('suspicious_tld_count', 0) > 0:
            score += 15
            indicators.append("Contains URLs with suspicious top-level domains")
            
        # Check for domain mismatches (MEDIUM RISK)
        if url_features.get('mismatched_domain_count', 0) > 0:
            score += 15
            indicators.append("URL domains don't match sender domain")
            
        # Check for Reply-To mismatch (MEDIUM RISK)
        if header_features.get('has_reply_to_mismatch'):
            score += 10
            indicators.append("Reply-To address differs from sender")
            
        # Check if sender is from untrusted domain (LOW RISK)
        if not sender_features.get('is_trusted_domain') and not sender_features.get('is_free_provider'):
            score += 5
            indicators.append("Sender from unknown domain")
            
        return min(score, self.max_score), indicators
        
    def _detect_spam(self, email: Dict, features: Dict) -> tuple:
        """
        Detect spam emails.
        
        Spam Indicators:
        1. Excessive promotional language
        2. Money-related terms
        3. Excessive punctuation
        4. Poor formatting
        5. Suspicious attachments
        
        Args:
            email: Parsed email
            features: Extracted features
            
        Returns:
            Tuple of (score, indicators)
        """
        score = 0
        indicators = []
        
        content_features = features.get('content_features', {})
        structural_features = features.get('structural_features', {})
        url_features = features.get('url_features', {})
        
        # Check for money-related terms (MEDIUM RISK)
        money_count = content_features.get('money_term_count', 0)
        if money_count >= 3:
            score += 15
            indicators.append(f"Contains excessive money-related terms ({money_count} instances)")
            
        # Check for excessive capitalization (LOW RISK)
        caps_ratio = content_features.get('caps_ratio', 0)
        if caps_ratio > 0.5:
            score += 10
            indicators.append("Subject line has excessive capitalization")
            
        # Check for excessive punctuation (LOW RISK)
        exclamation_count = content_features.get('exclamation_count', 0)
        if exclamation_count >= 3:
            score += 10
            indicators.append(f"Excessive exclamation marks ({exclamation_count})")
            
        # Check for excessive URLs (MEDIUM RISK)
        url_count = url_features.get('url_count', 0)
        if url_count >= 5:
            score += 15
            indicators.append(f"Contains many URLs ({url_count})")
            
        # Check for suspicious attachments (MEDIUM RISK)
        if structural_features.get('has_attachments'):
            score += 10
            indicators.append("Contains attachments (potential malware vector)")
            
        # Check for very short body (LOW RISK)
        body_length = content_features.get('body_length', 0)
        if body_length < 50 and url_count > 0:
            score += 10
            indicators.append("Very short message with links (likely spam)")
            
        # Check for free email provider with promotional content (LOW RISK)
        sender_features = features.get('sender_features', {})
        if sender_features.get('is_free_provider') and money_count >= 2:
            score += 10
            indicators.append("Free email provider sending promotional content")
            
        return min(score, self.max_score), indicators
        
    def get_threat_level(self, score: int) -> str:
        """
        Convert threat score to threat level.
        
        Args:
            score: Threat score (0-100)
            
        Returns:
            Threat level string
        """
        if score <= settings.SAFE_THRESHOLD:
            return "SAFE"
        elif score <= settings.SUSPICIOUS_THRESHOLD:
            return "SUSPICIOUS"
        else:
            return "SPAM"
