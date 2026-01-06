"""
Feature Extraction Module

This module extracts features from emails for AI/NLP analysis.
Features are used to detect spam and phishing attempts.

Feature Categories:
1. Sender-based: Domain reputation, email format
2. Content-based: Keywords, urgency, grammar
3. URL-based: Link characteristics, redirects
4. Structural: HTML complexity, header anomalies

Academic Note: Feature engineering is crucial for machine learning
and rule-based detection systems. Good features improve accuracy.
"""

import re
from typing import Dict, List
from urllib.parse import urlparse
import logging

from config.settings import settings

logger = logging.getLogger(__name__)


class FeatureExtractor:
    """
    Extract features from parsed emails for threat detection.
    
    This class implements various feature extraction techniques
    used in spam and phishing detection systems.
    """
    
    def __init__(self):
        """Initialize feature extractor"""
        pass
        
    def extract_features(self, parsed_email: Dict) -> Dict:
        """
        Extract all features from a parsed email.
        
        Args:
            parsed_email: Parsed email dictionary
            
        Returns:
            Dictionary of extracted features
        """
        try:
            features = {
                # Sender features
                'sender_features': self._extract_sender_features(parsed_email),
                
                # Content features
                'content_features': self._extract_content_features(parsed_email),
                
                # URL features
                'url_features': self._extract_url_features(parsed_email),
                
                # Structural features
                'structural_features': self._extract_structural_features(parsed_email),
                
                # Header features
                'header_features': self._extract_header_features(parsed_email)
            }
            
            return features
            
        except Exception as e:
            logger.error(f"Error extracting features: {str(e)}")
            return {}
            
    def _extract_sender_features(self, email: Dict) -> Dict:
        """
        Extract features related to the sender.
        
        Features:
        - Domain reputation
        - Email format validity
        - Display name vs email mismatch
        - Free email provider usage
        """
        sender = email.get('sender', {})
        sender_email = sender.get('email', '')
        sender_domain = sender.get('domain', '')
        sender_name = sender.get('name', '')
        
        # Check if sender uses free email provider
        free_providers = ['gmail.com', 'yahoo.com', 'hotmail.com', 'outlook.com', 
                         'aol.com', 'mail.com', 'protonmail.com']
        is_free_provider = sender_domain in free_providers
        
        # Check if domain is in trusted list
        is_trusted = sender_domain in settings.TRUSTED_DOMAINS
        
        # Check for display name spoofing
        # Example: "PayPal" <scammer@evil.com>
        has_name_mismatch = False
        if sender_name and sender_domain:
            name_lower = sender_name.lower()
            # Check if display name contains a brand but email doesn't match
            brands = ['paypal', 'amazon', 'google', 'microsoft', 'apple', 'bank']
            for brand in brands:
                if brand in name_lower and brand not in sender_domain:
                    has_name_mismatch = True
                    break
                    
        # Check email format validity
        is_valid_format = bool(re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', sender_email))
        
        return {
            'is_free_provider': is_free_provider,
            'is_trusted_domain': is_trusted,
            'has_name_mismatch': has_name_mismatch,
            'is_valid_format': is_valid_format,
            'domain': sender_domain,
            'email': sender_email
        }
        
    def _extract_content_features(self, email: Dict) -> Dict:
        """
        Extract features from email content.
        
        Features:
        - Phishing keywords
        - Urgency indicators
        - Grammar quality
        - Excessive capitalization
        - Special characters
        """
        subject = email.get('subject', '').lower()
        body = email.get('body_text', '').lower()
        combined_text = subject + ' ' + body
        
        # Check for phishing keywords
        phishing_keyword_count = 0
        matched_keywords = []
        for keyword in settings.PHISHING_KEYWORDS:
            if keyword.lower() in combined_text:
                phishing_keyword_count += 1
                matched_keywords.append(keyword)
                
        # Check for urgency indicators
        urgency_words = ['urgent', 'immediate', 'act now', 'expires', 'limited time', 
                        'hurry', 'quick', 'fast', 'deadline', 'today only']
        urgency_count = sum(1 for word in urgency_words if word in combined_text)
        
        # Check for excessive capitalization
        if len(subject) > 0:
            caps_ratio = sum(1 for c in subject if c.isupper()) / len(subject)
        else:
            caps_ratio = 0
            
        # Check for excessive punctuation
        exclamation_count = combined_text.count('!')
        question_count = combined_text.count('?')
        
        # Check for money-related terms
        money_terms = ['$', '€', '£', 'money', 'cash', 'prize', 'winner', 'free', 
                      'credit card', 'bank account', 'payment']
        money_term_count = sum(1 for term in money_terms if term in combined_text)
        
        # Check for credential requests
        credential_terms = ['password', 'username', 'social security', 'ssn', 
                           'credit card', 'account number', 'pin', 'verify']
        credential_request_count = sum(1 for term in credential_terms if term in combined_text)
        
        return {
            'phishing_keyword_count': phishing_keyword_count,
            'matched_keywords': matched_keywords,
            'urgency_count': urgency_count,
            'caps_ratio': caps_ratio,
            'exclamation_count': exclamation_count,
            'question_count': question_count,
            'money_term_count': money_term_count,
            'credential_request_count': credential_request_count,
            'body_length': len(body)
        }
        
    def _extract_url_features(self, email: Dict) -> Dict:
        """
        Extract features from URLs in email.
        
        Features:
        - URL count
        - Shortened URLs
        - Suspicious TLDs
        - IP addresses in URLs
        - Mismatched domains
        """
        urls = email.get('urls', [])
        
        url_count = len(urls)
        shortened_url_count = 0
        suspicious_tld_count = 0
        ip_address_count = 0
        mismatched_domains = []
        
        for url in urls:
            try:
                parsed = urlparse(url)
                domain = parsed.netloc.lower()
                
                # Check for URL shorteners
                if any(shortener in domain for shortener in settings.URL_SHORTENERS):
                    shortened_url_count += 1
                    
                # Check for suspicious TLDs
                if any(domain.endswith(tld) for tld in settings.SUSPICIOUS_TLDS):
                    suspicious_tld_count += 1
                    
                # Check for IP addresses
                if re.match(r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}', domain):
                    ip_address_count += 1
                    
                # Check for domain mismatch with sender
                sender_domain = email.get('sender', {}).get('domain', '')
                if sender_domain and sender_domain not in domain and domain not in sender_domain:
                    # Check if URL domain looks like sender domain (typosquatting)
                    if self._is_similar_domain(sender_domain, domain):
                        mismatched_domains.append(domain)
                        
            except Exception as e:
                logger.error(f"Error parsing URL {url}: {str(e)}")
                
        return {
            'url_count': url_count,
            'shortened_url_count': shortened_url_count,
            'suspicious_tld_count': suspicious_tld_count,
            'ip_address_count': ip_address_count,
            'mismatched_domain_count': len(mismatched_domains),
            'has_urls': url_count > 0
        }
        
    def _extract_structural_features(self, email: Dict) -> Dict:
        """
        Extract structural features from email.
        
        Features:
        - Has HTML
        - Has attachments
        - HTML complexity
        """
        has_html = bool(email.get('body_html'))
        has_attachments = email.get('has_attachments', False)
        
        # Simple HTML complexity measure
        html_length = len(email.get('body_html', ''))
        text_length = len(email.get('body_text', ''))
        
        html_ratio = html_length / text_length if text_length > 0 else 0
        
        return {
            'has_html': has_html,
            'has_attachments': has_attachments,
            'html_ratio': html_ratio,
            'html_length': html_length
        }
        
    def _extract_header_features(self, email: Dict) -> Dict:
        """
        Extract features from email headers.
        
        Features:
        - Reply-To mismatch
        - Missing headers
        - Suspicious routing
        """
        headers = email.get('headers', {})
        sender = email.get('sender', {})
        
        from_email = sender.get('email', '')
        reply_to = headers.get('Reply-To', '')
        
        # Check for Reply-To mismatch
        has_reply_to_mismatch = False
        if reply_to and from_email:
            reply_to_email = re.search(r'[\w\.-]+@[\w\.-]+', reply_to)
            if reply_to_email:
                reply_to_email = reply_to_email.group(0).lower()
                has_reply_to_mismatch = reply_to_email != from_email
                
        # Check for missing important headers
        important_headers = ['From', 'To', 'Subject', 'Date']
        missing_headers = [h for h in important_headers if h not in headers]
        
        return {
            'has_reply_to_mismatch': has_reply_to_mismatch,
            'missing_header_count': len(missing_headers),
            'has_return_path': 'Return-Path' in headers
        }
        
    def _is_similar_domain(self, domain1: str, domain2: str) -> bool:
        """
        Check if two domains are suspiciously similar (typosquatting).
        
        Args:
            domain1: First domain
            domain2: Second domain
            
        Returns:
            bool: True if domains are suspiciously similar
        """
        # Simple similarity check - can be enhanced with Levenshtein distance
        if len(domain1) == 0 or len(domain2) == 0:
            return False
            
        # Check if one domain is a slight variation of the other
        # Example: google.com vs gooogle.com
        if abs(len(domain1) - len(domain2)) <= 2:
            differences = sum(c1 != c2 for c1, c2 in zip(domain1, domain2))
            if differences <= 2:
                return True
                
        return False
