"""
Simple Gmail Login with App Password

This is an alternative authentication method using Gmail App Passwords.
Simpler than OAuth 2.0 but requires enabling 2-Step Verification.

IMPORTANT SECURITY NOTE:
- This method uses IMAP instead of Gmail API
- Requires App Password (not your regular Gmail password)
- Less secure than OAuth 2.0 but easier to setup

Setup Steps:
1. Enable 2-Step Verification on your Gmail account
2. Generate an App Password
3. Use that App Password in this application
"""

import imaplib
import email
from email.header import decode_header
import logging
from typing import List, Dict, Optional

logger = logging.getLogger(__name__)


class SimpleGmailLogin:
    """
    Simple Gmail authentication using IMAP and App Password.
    
    This is easier to setup than OAuth 2.0 but less secure.
    Use this for testing or personal projects only.
    """
    
    def __init__(self, email_address: str, app_password: str):
        """
        Initialize Gmail connection with email and app password.
        
        Args:
            email_address: Your Gmail address (e.g., yourname@gmail.com)
            app_password: App Password generated from Google Account settings
        """
        self.email_address = email_address
        self.app_password = app_password
        self.imap = None
        
    def connect(self) -> bool:
        """
        Connect to Gmail using IMAP.
        
        Returns:
            bool: True if connection successful
        """
        try:
            logger.info("Connecting to Gmail via IMAP...")
            
            # Connect to Gmail IMAP server
            self.imap = imaplib.IMAP4_SSL("imap.gmail.com")
            
            # Login with email and app password
            self.imap.login(self.email_address, self.app_password)
            
            logger.info("Successfully connected to Gmail!")
            return True
            
        except imaplib.IMAP4.error as e:
            logger.error(f"IMAP login failed: {str(e)}")
            logger.error("Make sure you're using an App Password, not your regular password")
            return False
        except Exception as e:
            logger.error(f"Connection failed: {str(e)}")
            return False
            
    def fetch_emails(self, folder: str = "INBOX", limit: int = 50, unread_only: bool = True) -> List[Dict]:
        """
        Fetch emails from Gmail.
        
        Args:
            folder: Gmail folder to fetch from (INBOX, SPAM, etc.)
            limit: Maximum number of emails to fetch
            unread_only: If True, only fetch unread emails
            
        Returns:
            List of email dictionaries
        """
        try:
            if not self.imap:
                logger.error("Not connected. Call connect() first.")
                return []
                
            # Select folder
            self.imap.select(folder)
            
            # Search for emails
            if unread_only:
                status, messages = self.imap.search(None, 'UNSEEN')
            else:
                status, messages = self.imap.search(None, 'ALL')
                
            if status != 'OK':
                logger.error("Failed to search emails")
                return []
                
            # Get email IDs
            email_ids = messages[0].split()
            
            # Limit number of emails
            email_ids = email_ids[-limit:] if len(email_ids) > limit else email_ids
            
            logger.info(f"Found {len(email_ids)} emails")
            
            # Fetch emails
            emails = []
            for email_id in email_ids:
                email_data = self._fetch_single_email(email_id)
                if email_data:
                    emails.append(email_data)
                    
            return emails
            
        except Exception as e:
            logger.error(f"Error fetching emails: {str(e)}")
            return []
            
    def _fetch_single_email(self, email_id: bytes) -> Optional[Dict]:
        """
        Fetch a single email by ID.
        
        Args:
            email_id: Email ID from IMAP
            
        Returns:
            Dictionary with email data
        """
        try:
            # Fetch email
            status, msg_data = self.imap.fetch(email_id, '(RFC822)')
            
            if status != 'OK':
                return None
                
            # Parse email
            raw_email = msg_data[0][1]
            email_message = email.message_from_bytes(raw_email)
            
            # Extract subject
            subject = email_message.get('Subject', '')
            if subject:
                decoded_subject = decode_header(subject)[0]
                if isinstance(decoded_subject[0], bytes):
                    subject = decoded_subject[0].decode(decoded_subject[1] or 'utf-8')
                else:
                    subject = decoded_subject[0]
                    
            # Extract sender
            from_header = email_message.get('From', '')
            
            # Extract body
            body = self._get_email_body(email_message)
            
            return {
                'id': email_id.decode(),
                'subject': subject,
                'from': from_header,
                'sender_email': self._extract_email_address(from_header),
                'sender_domain': self._extract_domain(from_header),
                'body_text': body,
                'has_attachments': self._has_attachments(email_message),
                'urls': self._extract_urls(body)
            }
            
        except Exception as e:
            logger.error(f"Error fetching email {email_id}: {str(e)}")
            return None
            
    def _get_email_body(self, email_message) -> str:
        """Extract email body text"""
        body = ""
        
        if email_message.is_multipart():
            for part in email_message.walk():
                content_type = part.get_content_type()
                if content_type == "text/plain":
                    try:
                        body = part.get_payload(decode=True).decode('utf-8', errors='ignore')
                        break
                    except:
                        pass
        else:
            try:
                body = email_message.get_payload(decode=True).decode('utf-8', errors='ignore')
            except:
                pass
                
        return body
        
    def _has_attachments(self, email_message) -> bool:
        """Check if email has attachments"""
        for part in email_message.walk():
            if part.get_content_disposition() == 'attachment':
                return True
        return False
        
    def _extract_urls(self, text: str) -> List[str]:
        """Extract URLs from text"""
        import re
        url_pattern = r'https?://[^\s<>"{}|\\^`\[\]]+'
        return re.findall(url_pattern, text)
        
    def _extract_email_address(self, from_header: str) -> str:
        """Extract email address from From header"""
        import re
        match = re.search(r'[\w\.-]+@[\w\.-]+', from_header)
        return match.group(0) if match else ''
        
    def _extract_domain(self, from_header: str) -> str:
        """Extract domain from From header"""
        email_addr = self._extract_email_address(from_header)
        if '@' in email_addr:
            return email_addr.split('@')[1]
        return ''
        
    def move_to_spam(self, email_id: str) -> bool:
        """
        Move email to spam folder.
        
        Args:
            email_id: Email ID
            
        Returns:
            bool: True if successful
        """
        try:
            # Copy to spam folder
            self.imap.copy(email_id, '[Gmail]/Spam')
            
            # Mark for deletion from current folder
            self.imap.store(email_id, '+FLAGS', '\\Deleted')
            
            # Expunge deleted emails
            self.imap.expunge()
            
            logger.info(f"Moved email {email_id} to spam")
            return True
            
        except Exception as e:
            logger.error(f"Error moving to spam: {str(e)}")
            return False
            
    def disconnect(self):
        """Disconnect from Gmail"""
        try:
            if self.imap:
                self.imap.close()
                self.imap.logout()
                logger.info("Disconnected from Gmail")
        except:
            pass


# Example usage
if __name__ == "__main__":
    # Test connection
    email = "your-email@gmail.com"
    app_password = "your-app-password-here"
    
    gmail = SimpleGmailLogin(email, app_password)
    
    if gmail.connect():
        print("✓ Connected successfully!")
        
        emails = gmail.fetch_emails(limit=5)
        print(f"✓ Fetched {len(emails)} emails")
        
        for e in emails:
            print(f"\nFrom: {e['sender_email']}")
            print(f"Subject: {e['subject'][:50]}...")
            
        gmail.disconnect()
    else:
        print("✗ Connection failed")
