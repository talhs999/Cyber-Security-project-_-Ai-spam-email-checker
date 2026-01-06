"""
Email Parser Module

This module safely extracts and parses email components without executing
any content. It implements zero-click analysis principles.

Security Features:
1. No attachment execution
2. Safe HTML parsing with BeautifulSoup
3. URL extraction without clicking
4. Header analysis without triggering read receipts
5. Text-only processing (no script execution)

Academic Note: This demonstrates secure content parsing and the importance
of treating all email content as potentially malicious.
"""

import base64
import re
from typing import Dict, List, Optional
from bs4 import BeautifulSoup
from email.utils import parseaddr
import logging

logger = logging.getLogger(__name__)


class EmailParser:
    """
    Safely parse email content for analysis.
    
    This parser extracts all necessary information from emails
    without opening them or executing any content.
    
    Security Principle: Treat all email content as untrusted input.
    Never execute scripts, open attachments, or follow links during parsing.
    """
    
    def __init__(self):
        """Initialize the email parser"""
        pass
        
    def parse_email(self, email_data: Dict) -> Dict:
        """
        Parse email data into structured format for analysis.
        
        Args:
            email_data: Raw email data from Gmail API
            
        Returns:
            Dictionary with parsed email components
            
        Security Note: All parsing is done in a safe, read-only manner.
        No content is executed or rendered.
        """
        try:
            payload = email_data.get('payload', {})
            headers = payload.get('headers', [])
            
            # Extract headers
            parsed_headers = self._parse_headers(headers)
            
            # Extract body
            body_text, body_html = self._extract_body(payload)
            
            # Extract URLs from body
            urls = self._extract_urls(body_text, body_html)
            
            # Parse sender information
            sender_info = self._parse_sender(parsed_headers.get('From', ''))
            
            return {
                'id': email_data.get('id'),
                'thread_id': email_data.get('threadId'),
                'labels': email_data.get('labelIds', []),
                'snippet': email_data.get('snippet', ''),
                'headers': parsed_headers,
                'sender': sender_info,
                'subject': parsed_headers.get('Subject', ''),
                'body_text': body_text,
                'body_html': body_html,
                'urls': urls,
                'has_attachments': self._has_attachments(payload),
                'timestamp': email_data.get('internalDate')
            }
            
        except Exception as e:
            logger.error(f"Error parsing email: {str(e)}")
            return {}
            
    def _parse_headers(self, headers: List[Dict]) -> Dict:
        """
        Extract important headers from email.
        
        Key headers for security analysis:
        - From: Sender address
        - Reply-To: Reply address (may differ from From)
        - Return-Path: Actual sender (harder to spoof)
        - Subject: Email subject
        - Received: Email routing information
        - Authentication-Results: SPF/DKIM/DMARC results
        
        Args:
            headers: List of header dictionaries
            
        Returns:
            Dictionary of parsed headers
        """
        parsed = {}
        for header in headers:
            name = header.get('name', '')
            value = header.get('value', '')
            parsed[name] = value
            
        return parsed
        
    def _parse_sender(self, from_header: str) -> Dict:
        """
        Parse sender information from From header.
        
        Args:
            from_header: From header value
            
        Returns:
            Dictionary with sender name, email, and domain
            
        Security Note: The From header can be spoofed. Always verify
        with Return-Path and authentication headers.
        """
        name, email = parseaddr(from_header)
        
        # Extract domain from email
        domain = ''
        if email and '@' in email:
            domain = email.split('@')[1].lower()
            
        return {
            'name': name,
            'email': email.lower() if email else '',
            'domain': domain
        }
        
    def _extract_body(self, payload: Dict) -> tuple:
        """
        Extract email body text safely.
        
        Args:
            payload: Email payload from Gmail API
            
        Returns:
            Tuple of (plain_text, html_text)
            
        Security Note: We extract text content only. No scripts or
        embedded content is executed.
        """
        plain_text = ''
        html_text = ''
        
        # Check if payload has parts (multipart email)
        if 'parts' in payload:
            for part in payload['parts']:
                mime_type = part.get('mimeType', '')
                
                if mime_type == 'text/plain':
                    plain_text = self._decode_body(part)
                elif mime_type == 'text/html':
                    html_text = self._decode_body(part)
                    
                # Handle nested parts
                if 'parts' in part:
                    nested_plain, nested_html = self._extract_body(part)
                    plain_text += nested_plain
                    html_text += nested_html
                    
        # Single part email
        elif 'body' in payload:
            mime_type = payload.get('mimeType', '')
            if mime_type == 'text/plain':
                plain_text = self._decode_body(payload)
            elif mime_type == 'text/html':
                html_text = self._decode_body(payload)
                
        # Convert HTML to plain text if no plain text available
        if not plain_text and html_text:
            plain_text = self._html_to_text(html_text)
            
        return plain_text, html_text
        
    def _decode_body(self, part: Dict) -> str:
        """
        Decode base64 encoded email body.
        
        Args:
            part: Email part containing body data
            
        Returns:
            Decoded text string
        """
        try:
            body_data = part.get('body', {}).get('data', '')
            if body_data:
                # Gmail API returns base64url encoded data
                decoded = base64.urlsafe_b64decode(body_data).decode('utf-8', errors='ignore')
                return decoded
        except Exception as e:
            logger.error(f"Error decoding body: {str(e)}")
            
        return ''
        
    def _html_to_text(self, html: str) -> str:
        """
        Convert HTML to plain text safely.
        
        Args:
            html: HTML content
            
        Returns:
            Plain text string
            
        Security Note: BeautifulSoup is used to safely parse HTML
        without executing any scripts or loading external resources.
        """
        try:
            soup = BeautifulSoup(html, 'lxml')
            # Remove script and style elements
            for script in soup(['script', 'style']):
                script.decompose()
            text = soup.get_text(separator=' ', strip=True)
            return text
        except Exception as e:
            logger.error(f"Error converting HTML to text: {str(e)}")
            return ''
            
    def _extract_urls(self, plain_text: str, html_text: str) -> List[str]:
        """
        Extract all URLs from email content.
        
        Args:
            plain_text: Plain text body
            html_text: HTML body
            
        Returns:
            List of unique URLs
            
        Security Note: URLs are extracted for analysis only.
        They are NEVER clicked or visited during this process.
        """
        urls = set()
        
        # Extract from plain text using regex
        url_pattern = r'https?://[^\s<>"{}|\\^`\[\]]+'
        urls.update(re.findall(url_pattern, plain_text))
        
        # Extract from HTML links
        if html_text:
            try:
                soup = BeautifulSoup(html_text, 'lxml')
                for link in soup.find_all('a', href=True):
                    href = link['href']
                    if href.startswith('http'):
                        urls.add(href)
            except Exception as e:
                logger.error(f"Error extracting URLs from HTML: {str(e)}")
                
        return list(urls)
        
    def _has_attachments(self, payload: Dict) -> bool:
        """
        Check if email has attachments.
        
        Args:
            payload: Email payload
            
        Returns:
            bool: True if email has attachments
            
        Security Note: We only detect attachments, we NEVER download
        or execute them. Attachments are a common vector for malware.
        """
        if 'parts' in payload:
            for part in payload['parts']:
                if part.get('filename'):
                    return True
                # Check nested parts
                if 'parts' in part and self._has_attachments(part):
                    return True
                    
        return False
        
    def get_header_value(self, headers: Dict, header_name: str) -> str:
        """
        Get a specific header value.
        
        Args:
            headers: Parsed headers dictionary
            header_name: Name of header to retrieve
            
        Returns:
            Header value or empty string
        """
        return headers.get(header_name, '')
