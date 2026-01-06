"""
AI-Powered Zero-Click Gmail Spam & Phishing Detection System

Main application entry point that orchestrates the entire detection pipeline.

Process Flow:
1. Authenticate with Gmail using OAuth 2.0
2. Fetch emails from inbox
3. Parse email content safely
4. Extract features for analysis
5. Detect threats using AI/NLP
6. Classify emails (Safe/Suspicious/Spam)
7. Take appropriate actions
8. Notify user of results

Security Principles Applied:
- Zero-click analysis (no email opening)
- OAuth 2.0 authentication (no passwords)
- Least privilege (minimal API scopes)
- Safe content parsing (no execution)
- Automated threat response

Author: Cybersecurity Academic Project
Purpose: Demonstrate secure email analysis and threat detection
"""

import logging
import sys
from typing import List, Dict

from src.gmail_auth import get_authenticated_service
from src.gmail_client import GmailClient
from src.email_parser import EmailParser
from src.feature_extractor import FeatureExtractor
from src.threat_detector import ThreatDetector
from src.classifier import EmailClassifier
from src.notifier import Notifier
from src.database import EmailDatabase
from src.reports import ReportGenerator
from config.settings import settings

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format=settings.LOG_FORMAT,
    handlers=[
        logging.FileHandler('spam_detector.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)


class SpamDetectionSystem:
    """
    Main spam detection system orchestrator.
    
    This class coordinates all components of the detection system
    to provide end-to-end spam and phishing detection.
    """
    
    def __init__(self):
        """Initialize the spam detection system"""
        self.gmail_service = None
        self.gmail_client = None
        self.email_parser = EmailParser()
        self.feature_extractor = FeatureExtractor()
        self.threat_detector = ThreatDetector()
        self.classifier = None
        self.notifier = Notifier()
        self.database = EmailDatabase()  # Initialize database
        self.report_generator = ReportGenerator(self.database)  # Initialize report generator
        
    def initialize(self) -> bool:
        """
        Initialize the system and authenticate with Gmail.
        
        Returns:
            bool: True if initialization successful
        """
        try:
            self.notifier.notify_info("Initializing AI-Powered Spam Detection System...")
            
            # Authenticate with Gmail
            self.notifier.notify_info("Authenticating with Gmail...")
            self.gmail_service = get_authenticated_service()
            
            if not self.gmail_service:
                self.notifier.notify_error("Failed to authenticate with Gmail")
                return False
                
            self.notifier.notify_success("Authentication successful!")
            
            # Initialize Gmail client
            self.gmail_client = GmailClient(self.gmail_service)
            self.classifier = EmailClassifier(self.gmail_client)
            
            return True
            
        except Exception as e:
            logger.error(f"Initialization failed: {str(e)}")
            self.notifier.notify_error(f"Initialization failed: {str(e)}")
            return False
            
    def process_emails(self, max_emails: int = None, unread_only: bool = True) -> List[Dict]:
        """
        Process emails through the detection pipeline.
        
        Args:
            max_emails: Maximum number of emails to process
            unread_only: If True, only process unread emails
            
        Returns:
            List of classification results
        """
        try:
            # Fetch emails
            self.notifier.notify_info(f"Fetching emails (max: {max_emails or settings.MAX_EMAILS_PER_RUN})...")
            emails = self.gmail_client.fetch_emails(max_emails, unread_only)
            
            if not emails:
                self.notifier.notify_info("No emails to process")
                return []
                
            self.notifier.notify_success(f"Fetched {len(emails)} emails")
            
            # Process each email
            results = []
            for i, email_data in enumerate(emails, 1):
                self.notifier.notify_info(f"Processing email {i}/{len(emails)}...")
                result = self._process_single_email(email_data)
                if result:
                    results.append(result)
                    
            return results
            
        except Exception as e:
            logger.error(f"Error processing emails: {str(e)}")
            self.notifier.notify_error(f"Error processing emails: {str(e)}")
            return []
            
    def _process_single_email(self, email_data: Dict) -> Dict:
        """
        Process a single email through the detection pipeline.
        
        Args:
            email_data: Raw email data from Gmail API
            
        Returns:
            Classification result dictionary
        """
        try:
            # Step 1: Parse email
            parsed_email = self.email_parser.parse_email(email_data)
            
            if not parsed_email:
                logger.warning(f"Failed to parse email {email_data.get('id')}")
                return None
                
            # Step 2: Extract features
            features = self.feature_extractor.extract_features(parsed_email)
            
            # Step 3: Detect threats
            threat_analysis = self.threat_detector.analyze_email(parsed_email, features)
            
            # Step 4: Classify and act
            result = self.classifier.classify_and_act(parsed_email, threat_analysis)
            
            # Step 5: Save to database
            self.database.save_email_classification(parsed_email, result)
            
            # Step 6: Notify user
            self.notifier.notify_classification(result, parsed_email)
            
            return result
            
        except Exception as e:
            logger.error(f"Error processing email: {str(e)}")
            return None
            
    def run(self):
        """
        Run the spam detection system.
        
        This is the main entry point for the application.
        """
        try:
            print("\n" + "="*60)
            print("AI-Powered Zero-Click Gmail Spam & Phishing Detection System")
            print("="*60 + "\n")
            
            # Initialize system
            if not self.initialize():
                return
                
            # Process emails
            results = self.process_emails(
                max_emails=settings.MAX_EMAILS_PER_RUN,
                unread_only=settings.FETCH_UNREAD_ONLY
            )
            
            # Display summary
            if results:
                summary = self.classifier.get_classification_summary(results)
                self.notifier.notify_summary(summary)
                
                # Log summary
                logger.info(f"Processing complete. Total: {summary['total']}, "
                          f"Safe: {summary['safe']}, "
                          f"Suspicious: {summary['suspicious']}, "
                          f"Spam: {summary['spam']}")
                
                # Generate and display database reports
                print("\n")
                print(self.report_generator.generate_summary_report())
                
                # Ask if user wants detailed reports
                try:
                    response = input("\nGenerate detailed reports? (y/n): ").lower()
                    if response == 'y':
                        print(self.report_generator.generate_weekly_report())
                        print(self.report_generator.generate_threat_analysis())
                        
                        # Export to file
                        export = input("\nExport reports to file? (y/n): ").lower()
                        if export == 'y':
                            self.report_generator.export_to_file("spam_detection_report.txt")
                except:
                    pass  # Skip if input not available
                    
            else:
                self.notifier.notify_info("No emails were processed")
                
            self.notifier.notify_success("Spam detection complete!")
            
            # Close database connection
            self.database.close()
            
        except KeyboardInterrupt:
            self.notifier.notify_info("\nOperation cancelled by user")
            self.database.close()
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}")
            self.notifier.notify_error(f"Unexpected error: {str(e)}")
            self.database.close()


def main():
    """Main function"""
    system = SpamDetectionSystem()
    system.run()


if __name__ == "__main__":
    main()
