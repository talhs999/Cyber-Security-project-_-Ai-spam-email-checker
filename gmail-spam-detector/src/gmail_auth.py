"""
Gmail OAuth 2.0 Authentication Module

This module handles secure authentication with Gmail using OAuth 2.0 flow.
It implements Google's recommended authentication practices without using passwords.

Security Features:
1. OAuth 2.0 flow - No password storage or transmission
2. Token-based authentication with automatic refresh
3. Minimal scope requests (principle of least privilege)
4. Secure token storage using pickle serialization
5. User consent required for all permissions

Academic Note: OAuth 2.0 is an industry-standard protocol for authorization.
It allows applications to access user data without exposing passwords.
"""

import os
import pickle
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from typing import Optional
import logging

from config.settings import settings

logger = logging.getLogger(__name__)


class GmailAuthenticator:
    """
    Handles OAuth 2.0 authentication for Gmail API access.
    
    This class implements the OAuth 2.0 authorization code flow, which is
    the most secure method for desktop applications to access user data.
    
    Security Principles Applied:
    - Authorization, not Authentication: OAuth 2.0 grants limited access
    - Consent-based: User must explicitly approve access
    - Token-based: Short-lived access tokens with refresh capability
    - Scope limitation: Only requests necessary permissions
    """
    
    def __init__(self):
        """Initialize the authenticator with configuration from settings"""
        self.scopes = settings.GMAIL_SCOPES
        self.credentials_file = settings.CREDENTIALS_FILE
        self.token_file = settings.TOKEN_FILE
        self.creds = None
        
    def authenticate(self) -> bool:
        """
        Perform OAuth 2.0 authentication flow.
        
        Process:
        1. Check for existing valid token
        2. Refresh token if expired but refreshable
        3. Initiate new OAuth flow if no valid token exists
        4. Save token for future use
        
        Returns:
            bool: True if authentication successful, False otherwise
            
        Security Note: The token file contains sensitive access credentials
        and should never be committed to version control or shared.
        """
        try:
            # Step 1: Check for existing token
            if os.path.exists(self.token_file):
                logger.info("Loading existing authentication token...")
                with open(self.token_file, 'rb') as token:
                    self.creds = pickle.load(token)
                    
            # Step 2: Validate and refresh if needed
            if self.creds and self.creds.expired and self.creds.refresh_token:
                logger.info("Token expired. Refreshing...")
                self.creds.refresh(Request())
                logger.info("Token refreshed successfully")
                
            # Step 3: Initiate new OAuth flow if no valid credentials
            elif not self.creds or not self.creds.valid:
                if not os.path.exists(self.credentials_file):
                    logger.error(f"Credentials file not found: {self.credentials_file}")
                    logger.error("Please download credentials.json from Google Cloud Console")
                    return False
                    
                logger.info("Starting OAuth 2.0 authentication flow...")
                logger.info("A browser window will open for you to authorize the application")
                
                # Create OAuth flow
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.credentials_file, 
                    self.scopes
                )
                
                # Run local server to receive OAuth callback
                # This opens a browser for user consent
                self.creds = flow.run_local_server(port=0)
                logger.info("Authentication successful!")
                
            # Step 4: Save credentials for future use
            with open(self.token_file, 'wb') as token:
                pickle.dump(self.creds, token)
                logger.info("Authentication token saved")
                
            return True
            
        except Exception as e:
            logger.error(f"Authentication failed: {str(e)}")
            return False
            
    def get_gmail_service(self):
        """
        Build and return authenticated Gmail API service.
        
        Returns:
            Gmail API service object or None if authentication failed
            
        Security Note: This service object has the permissions defined
        in the SCOPES. It can only perform actions the user consented to.
        """
        if not self.creds:
            logger.error("Not authenticated. Call authenticate() first.")
            return None
            
        try:
            service = build('gmail', 'v1', credentials=self.creds)
            logger.info("Gmail API service created successfully")
            return service
        except Exception as e:
            logger.error(f"Failed to create Gmail service: {str(e)}")
            return None
            
    def revoke_access(self) -> bool:
        """
        Revoke access and delete stored tokens.
        
        This is useful for testing or if the user wants to remove access.
        The user will need to re-authenticate on next use.
        
        Returns:
            bool: True if successful
        """
        try:
            if os.path.exists(self.token_file):
                os.remove(self.token_file)
                logger.info("Access token deleted")
            self.creds = None
            return True
        except Exception as e:
            logger.error(f"Failed to revoke access: {str(e)}")
            return False


def get_authenticated_service():
    """
    Convenience function to get an authenticated Gmail service.
    
    Returns:
        Authenticated Gmail API service or None
        
    Usage:
        service = get_authenticated_service()
        if service:
            # Use service to interact with Gmail
    """
    authenticator = GmailAuthenticator()
    if authenticator.authenticate():
        return authenticator.get_gmail_service()
    return None
