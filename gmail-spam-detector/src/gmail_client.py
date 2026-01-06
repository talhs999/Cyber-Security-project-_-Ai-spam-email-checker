"""
Gmail API Client Module

This module provides a safe interface to interact with Gmail API.
All operations are designed to be "zero-click" - emails are analyzed
without opening them or executing any content.

Security Features:
1. Read-only email access (metadata and content)
2. No attachment execution
3. No email opening (uses API to fetch content)
4. Rate limiting to respect API quotas
5. Error handling to prevent crashes

Academic Note: This demonstrates secure API interaction patterns
and the principle of least privilege in action.
"""

import base64
import time
import logging
from typing import List, Dict, Optional
from googleapiclient.errors import HttpError

from config.settings import settings

logger = logging.getLogger(__name__)


class GmailClient:
    """
    Safe Gmail API client for zero-click email operations.
    
    This client provides methods to:
    - Fetch emails without opening them
    - Read email metadata and content safely
    - Manage labels and move emails
    - Respect API rate limits
    
    Security Principle: All operations are read-only except for labeling,
    which is explicitly required for spam classification.
    """
    
    def __init__(self, service):
        """
        Initialize Gmail client with authenticated service.
        
        Args:
            service: Authenticated Gmail API service object
        """
        self.service = service
        self.user_id = 'me'  # Special value representing authenticated user
        
    def _rate_limit(self):
        """
        Implement rate limiting to respect Gmail API quotas.
        
        Gmail API quota: 250 units per user per second
        We add a small delay between calls to stay well under the limit.
        """
        time.sleep(settings.API_RATE_LIMIT_DELAY)
        
    def fetch_emails(self, max_results: int = None, unread_only: bool = True) -> List[Dict]:
        """
        Fetch emails from Gmail inbox without opening them.
        
        Args:
            max_results: Maximum number of emails to fetch
            unread_only: If True, only fetch unread emails
            
        Returns:
            List of email dictionaries with metadata
            
        Security Note: This uses the Gmail API to fetch email data.
        No emails are "opened" in the traditional sense - we're reading
        data through the API, which is safe and doesn't trigger any
        malicious content.
        """
        try:
            if max_results is None:
                max_results = settings.MAX_EMAILS_PER_RUN
                
            # Build query
            query = 'is:unread' if unread_only else ''
            
            logger.info(f"Fetching up to {max_results} emails...")
            
            # Get list of message IDs
            results = self.service.users().messages().list(
                userId=self.user_id,
                q=query,
                maxResults=max_results
            ).execute()
            
            messages = results.get('messages', [])
            
            if not messages:
                logger.info("No emails found")
                return []
                
            logger.info(f"Found {len(messages)} emails")
            
            # Fetch full email data for each message
            emails = []
            for msg in messages:
                self._rate_limit()
                email_data = self.get_email_by_id(msg['id'])
                if email_data:
                    emails.append(email_data)
                    
            return emails
            
        except HttpError as error:
            logger.error(f"Gmail API error: {error}")
            return []
        except Exception as e:
            logger.error(f"Error fetching emails: {str(e)}")
            return []
            
    def get_email_by_id(self, message_id: str) -> Optional[Dict]:
        """
        Fetch a single email by its ID.
        
        Args:
            message_id: Gmail message ID
            
        Returns:
            Dictionary containing email data or None
            
        Security Note: We use 'full' format to get all headers and body,
        but we never execute any content. The data is purely for analysis.
        """
        try:
            message = self.service.users().messages().get(
                userId=self.user_id,
                id=message_id,
                format='full'
            ).execute()
            
            return {
                'id': message_id,
                'threadId': message.get('threadId'),
                'labelIds': message.get('labelIds', []),
                'snippet': message.get('snippet', ''),
                'payload': message.get('payload', {}),
                'internalDate': message.get('internalDate')
            }
            
        except HttpError as error:
            logger.error(f"Error fetching email {message_id}: {error}")
            return None
            
    def get_email_labels(self) -> List[Dict]:
        """
        Get all available Gmail labels.
        
        Returns:
            List of label dictionaries
        """
        try:
            results = self.service.users().labels().list(userId=self.user_id).execute()
            return results.get('labels', [])
        except HttpError as error:
            logger.error(f"Error fetching labels: {error}")
            return []
            
    def add_label(self, message_id: str, label_id: str) -> bool:
        """
        Add a label to an email.
        
        Args:
            message_id: Gmail message ID
            label_id: Label ID to add
            
        Returns:
            bool: True if successful
        """
        try:
            self.service.users().messages().modify(
                userId=self.user_id,
                id=message_id,
                body={'addLabelIds': [label_id]}
            ).execute()
            
            logger.info(f"Added label {label_id} to message {message_id}")
            return True
            
        except HttpError as error:
            logger.error(f"Error adding label: {error}")
            return False
            
    def move_to_spam(self, message_id: str) -> bool:
        """
        Move an email to the spam folder.
        
        This is done by adding the SPAM label, which is Gmail's
        built-in spam label.
        
        Args:
            message_id: Gmail message ID
            
        Returns:
            bool: True if successful
            
        Security Note: This is a safe operation that helps protect
        the user by quarantining malicious emails.
        """
        try:
            # SPAM is a system label in Gmail
            self.service.users().messages().modify(
                userId=self.user_id,
                id=message_id,
                body={
                    'addLabelIds': ['SPAM'],
                    'removeLabelIds': ['INBOX']
                }
            ).execute()
            
            logger.info(f"Moved message {message_id} to spam")
            return True
            
        except HttpError as error:
            logger.error(f"Error moving to spam: {error}")
            return False
            
    def mark_as_read(self, message_id: str) -> bool:
        """
        Mark an email as read.
        
        Args:
            message_id: Gmail message ID
            
        Returns:
            bool: True if successful
        """
        try:
            self.service.users().messages().modify(
                userId=self.user_id,
                id=message_id,
                body={'removeLabelIds': ['UNREAD']}
            ).execute()
            
            logger.info(f"Marked message {message_id} as read")
            return True
            
        except HttpError as error:
            logger.error(f"Error marking as read: {error}")
            return False
            
    def create_label(self, label_name: str) -> Optional[str]:
        """
        Create a custom label.
        
        Args:
            label_name: Name for the new label
            
        Returns:
            Label ID if successful, None otherwise
        """
        try:
            label = {
                'name': label_name,
                'labelListVisibility': 'labelShow',
                'messageListVisibility': 'show'
            }
            
            created_label = self.service.users().labels().create(
                userId=self.user_id,
                body=label
            ).execute()
            
            logger.info(f"Created label: {label_name}")
            return created_label['id']
            
        except HttpError as error:
            logger.error(f"Error creating label: {error}")
            return None
