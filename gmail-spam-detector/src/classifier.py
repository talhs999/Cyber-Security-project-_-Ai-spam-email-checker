"""
Email Classifier Module

This module classifies emails based on threat analysis results
and takes appropriate actions (labeling, moving to spam).

Classification Tiers:
1. SAFE (0-30): Legitimate emails - no action
2. SUSPICIOUS (31-70): Potential threats - label for review
3. SPAM (71-100): Clear threats - move to spam folder

Academic Note: This demonstrates automated decision-making based
on risk assessment, a key concept in cybersecurity systems.
"""

import logging
from typing import Dict
from enum import Enum

logger = logging.getLogger(__name__)


class EmailCategory(Enum):
    """Email classification categories"""
    SAFE = "SAFE"
    SUSPICIOUS = "SUSPICIOUS"
    SPAM = "SPAM"


class EmailClassifier:
    """
    Classify emails and execute appropriate actions.
    
    This class takes threat analysis results and determines
    the appropriate classification and action for each email.
    """
    
    def __init__(self, gmail_client):
        """
        Initialize email classifier.
        
        Args:
            gmail_client: Gmail client instance (GmailClient or SimpleGmailLogin)
        """
        self.gmail_client = gmail_client
        
    def classify_and_act(self, email: Dict, threat_analysis: Dict) -> Dict:
        """
        Classify email and take appropriate action.
        
        Args:
            email: Parsed email data
            threat_analysis: Threat analysis results
            
        Returns:
            Dictionary with classification results and actions taken
        """
        try:
            email_id = email.get('id')
            overall_score = threat_analysis.get('overall_score', 0)
            
            # Determine category
            if threat_analysis.get('is_spam'):
                category = EmailCategory.SPAM
                action_taken = self._handle_spam(email_id)
            elif threat_analysis.get('is_suspicious'):
                category = EmailCategory.SUSPICIOUS
                action_taken = self._handle_suspicious(email_id)
            else:
                category = EmailCategory.SAFE
                action_taken = self._handle_safe(email_id)
                
            return {
                'email_id': email_id,
                'category': category.value,
                'score': overall_score,
                'action_taken': action_taken,
                'threat_indicators': threat_analysis.get('threat_indicators', [])
            }
            
        except Exception as e:
            logger.error(f"Error classifying email: {str(e)}")
            return {
                'email_id': email.get('id'),
                'category': EmailCategory.SAFE.value,
                'score': 0,
                'action_taken': 'Error occurred, no action taken',
                'threat_indicators': []
            }
            
    def _handle_spam(self, email_id: str) -> str:
        """
        Handle spam emails.
        
        Action: Move to spam folder
        
        Args:
            email_id: Gmail message ID
            
        Returns:
            Description of action taken
        """
        try:
            success = self.gmail_client.move_to_spam(email_id)
            if success:
                logger.info(f"Email {email_id} moved to spam")
                return "Moved to spam folder"
            else:
                logger.warning(f"Failed to move email {email_id} to spam")
                return "Failed to move to spam"
        except Exception as e:
            logger.error(f"Error handling spam: {str(e)}")
            return f"Error: {str(e)}"
            
    def _handle_suspicious(self, email_id: str) -> str:
        """
        Handle suspicious emails.
        
        Action: Add warning label (create if doesn't exist)
        
        Args:
            email_id: Gmail message ID
            
        Returns:
            Description of action taken
        """
        try:
            # Try to add a custom "Suspicious" label
            # Note: In practice, you might want to create this label once
            # and reuse the label ID
            
            # For now, we'll just log it
            # In a full implementation, you would:
            # 1. Check if "Suspicious" label exists
            # 2. Create it if it doesn't
            # 3. Add the label to the email
            
            logger.info(f"Email {email_id} marked as suspicious")
            return "Marked as suspicious (requires user review)"
            
        except Exception as e:
            logger.error(f"Error handling suspicious email: {str(e)}")
            return f"Error: {str(e)}"
            
    def _handle_safe(self, email_id: str) -> str:
        """
        Handle safe emails.
        
        Action: No action needed
        
        Args:
            email_id: Gmail message ID
            
        Returns:
            Description of action taken
        """
        logger.info(f"Email {email_id} classified as safe")
        return "No action needed (safe email)"
        
    def get_classification_summary(self, results: list) -> Dict:
        """
        Generate summary of classification results.
        
        Args:
            results: List of classification results
            
        Returns:
            Summary dictionary with counts
        """
        summary = {
            'total': len(results),
            'safe': 0,
            'suspicious': 0,
            'spam': 0
        }
        
        for result in results:
            category = result.get('category', '').upper()
            if category == 'SAFE':
                summary['safe'] += 1
            elif category == 'SUSPICIOUS':
                summary['suspicious'] += 1
            elif category == 'SPAM':
                summary['spam'] += 1
                
        return summary
