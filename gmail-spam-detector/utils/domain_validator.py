"""
Domain Validator Utility

This module validates email domains and checks reputation.

Security Features:
- Domain format validation
- Known malicious domain checking
- Trusted domain verification

Academic Note: Domain validation is crucial for email authentication.
In production systems, this would integrate with DNS queries for
SPF, DKIM, and DMARC validation.
"""

import re
from typing import Dict
import logging

from config.settings import settings

logger = logging.getLogger(__name__)


class DomainValidator:
    """
    Validate and check reputation of email domains.
    
    This validator performs basic domain checks. In a production
    system, this would be enhanced with:
    - DNS lookups for SPF/DKIM/DMARC records
    - Real-time domain reputation APIs
    - Domain age checking via WHOIS
    """
    
    def __init__(self):
        """Initialize domain validator"""
        # In a real system, this would load from a database or API
        self.known_malicious_domains = [
            'example-phishing.com',
            'fake-paypal.com',
            'secure-login-verify.com'
        ]
        
    def validate_domain(self, domain: str) -> Dict:
        """
        Validate a domain and check its reputation.
        
        Args:
            domain: Domain to validate
            
        Returns:
            Dictionary with validation results
        """
        try:
            validation = {
                'domain': domain,
                'is_valid': False,
                'is_trusted': False,
                'is_malicious': False,
                'warnings': []
            }
            
            # Check basic format
            if not self._is_valid_format(domain):
                validation['warnings'].append("Invalid domain format")
                return validation
                
            validation['is_valid'] = True
            
            # Check if trusted
            if domain in settings.TRUSTED_DOMAINS:
                validation['is_trusted'] = True
                return validation
                
            # Check if known malicious
            if domain in self.known_malicious_domains:
                validation['is_malicious'] = True
                validation['warnings'].append("Known malicious domain")
                return validation
                
            # Check for suspicious patterns
            if self._has_suspicious_pattern(domain):
                validation['warnings'].append("Domain has suspicious pattern")
                
            return validation
            
        except Exception as e:
            logger.error(f"Error validating domain {domain}: {str(e)}")
            return {
                'domain': domain,
                'is_valid': False,
                'is_trusted': False,
                'is_malicious': False,
                'warnings': ['Error validating domain']
            }
            
    def _is_valid_format(self, domain: str) -> bool:
        """
        Check if domain has valid format.
        
        Args:
            domain: Domain to check
            
        Returns:
            bool: True if valid format
        """
        # Basic domain format check
        pattern = r'^[a-zA-Z0-9]([a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?(\.[a-zA-Z0-9]([a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?)*\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, domain))
        
    def _has_suspicious_pattern(self, domain: str) -> bool:
        """
        Check for suspicious patterns in domain.
        
        Args:
            domain: Domain to check
            
        Returns:
            bool: True if suspicious pattern found
        """
        # Check for excessive hyphens
        if domain.count('-') > 3:
            return True
            
        # Check for numbers in unusual places
        if re.search(r'\d{3,}', domain):
            return True
            
        # Check for common typosquatting patterns
        typosquat_patterns = [
            'secure-', 'verify-', 'account-', 'login-',
            '-secure', '-verify', '-account', '-login'
        ]
        
        for pattern in typosquat_patterns:
            if pattern in domain.lower():
                return True
                
        return False
