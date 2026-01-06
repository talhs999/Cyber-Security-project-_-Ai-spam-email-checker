"""
URL Analyzer Utility

This module analyzes URLs for safety without visiting them.
It checks for common phishing and malware indicators.

Security Features:
- No URL visiting or clicking
- Pattern-based analysis
- Domain reputation checking
- Homograph attack detection

Academic Note: URL analysis is a critical component of phishing
detection as malicious URLs are the primary attack vector.
"""

import re
from urllib.parse import urlparse
from typing import Dict
import logging

from config.settings import settings

logger = logging.getLogger(__name__)


class URLAnalyzer:
    """
    Analyze URLs for security threats without visiting them.
    
    This analyzer uses static analysis techniques to identify
    potentially malicious URLs.
    """
    
    def __init__(self):
        """Initialize URL analyzer"""
        pass
        
    def analyze_url(self, url: str) -> Dict:
        """
        Perform comprehensive URL analysis.
        
        Args:
            url: URL to analyze
            
        Returns:
            Dictionary with analysis results
            
        Security Note: This analysis is performed entirely offline.
        The URL is never visited or clicked.
        """
        try:
            parsed = urlparse(url)
            
            analysis = {
                'url': url,
                'is_suspicious': False,
                'risk_score': 0,
                'warnings': []
            }
            
            # Check for IP address instead of domain
            if self._has_ip_address(parsed.netloc):
                analysis['risk_score'] += 30
                analysis['warnings'].append("Uses IP address instead of domain name")
                analysis['is_suspicious'] = True
                
            # Check for URL shortener
            if self._is_url_shortener(parsed.netloc):
                analysis['risk_score'] += 15
                analysis['warnings'].append("Uses URL shortening service")
                
            # Check for suspicious TLD
            if self._has_suspicious_tld(parsed.netloc):
                analysis['risk_score'] += 20
                analysis['warnings'].append("Uses suspicious top-level domain")
                analysis['is_suspicious'] = True
                
            # Check for excessive subdomains
            subdomain_count = parsed.netloc.count('.')
            if subdomain_count > 3:
                analysis['risk_score'] += 10
                analysis['warnings'].append("Has excessive subdomains")
                
            # Check for suspicious characters
            if self._has_suspicious_characters(url):
                analysis['risk_score'] += 15
                analysis['warnings'].append("Contains suspicious characters")
                
            # Check for homograph attack
            if self._is_homograph_attack(parsed.netloc):
                analysis['risk_score'] += 25
                analysis['warnings'].append("Possible homograph attack (lookalike domain)")
                analysis['is_suspicious'] = True
                
            # Check URL length
            if len(url) > 200:
                analysis['risk_score'] += 10
                analysis['warnings'].append("Unusually long URL")
                
            # Cap risk score at 100
            analysis['risk_score'] = min(analysis['risk_score'], 100)
            
            return analysis
            
        except Exception as e:
            logger.error(f"Error analyzing URL {url}: {str(e)}")
            return {
                'url': url,
                'is_suspicious': False,
                'risk_score': 0,
                'warnings': ['Error analyzing URL']
            }
            
    def _has_ip_address(self, netloc: str) -> bool:
        """Check if netloc is an IP address"""
        ip_pattern = r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}'
        return bool(re.match(ip_pattern, netloc))
        
    def _is_url_shortener(self, netloc: str) -> bool:
        """Check if domain is a known URL shortener"""
        return any(shortener in netloc.lower() for shortener in settings.URL_SHORTENERS)
        
    def _has_suspicious_tld(self, netloc: str) -> bool:
        """Check for suspicious top-level domains"""
        return any(netloc.lower().endswith(tld) for tld in settings.SUSPICIOUS_TLDS)
        
    def _has_suspicious_characters(self, url: str) -> bool:
        """Check for suspicious characters in URL"""
        # Check for @ symbol (can be used to hide real domain)
        if '@' in url:
            return True
            
        # Check for excessive hyphens
        if url.count('-') > 5:
            return True
            
        return False
        
    def _is_homograph_attack(self, domain: str) -> bool:
        """
        Detect potential homograph attacks.
        
        Homograph attacks use lookalike characters to create
        fake domains that appear legitimate.
        Example: paypal.com vs pаypal.com (Cyrillic 'а')
        
        Args:
            domain: Domain to check
            
        Returns:
            bool: True if potential homograph attack detected
        """
        # Check for non-ASCII characters
        try:
            domain.encode('ascii')
        except UnicodeEncodeError:
            # Contains non-ASCII characters
            return True
            
        # Check for common brand names with slight variations
        # This is a simplified check - production systems use more sophisticated methods
        common_brands = ['paypal', 'google', 'amazon', 'microsoft', 'apple', 'facebook']
        domain_lower = domain.lower()
        
        for brand in common_brands:
            if brand in domain_lower and brand != domain_lower.split('.')[0]:
                # Brand name appears but isn't the exact domain
                return True
                
        return False
