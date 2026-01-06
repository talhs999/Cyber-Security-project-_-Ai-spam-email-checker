"""
Simple Login Version of Main Application

This version uses simple email/password login instead of OAuth 2.0.
Easier to setup but requires Gmail App Password.
"""

import logging
import sys
from typing import List, Dict

from src.simple_gmail_login import SimpleGmailLogin
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
    format='%(levelname)s: %(message)s'
)

logger = logging.getLogger(__name__)


class SimpleSpamDetectionSystem:
    """
    Spam detection system with simple email/password login.
    
    Uses IMAP and App Password instead of OAuth 2.0.
    """
    
    def __init__(self):
        """Initialize the spam detection system"""
        self.gmail = None
        self.email_parser = EmailParser()
        self.feature_extractor = FeatureExtractor()
        self.threat_detector = ThreatDetector()
        self.classifier = None
        self.notifier = Notifier()
        self.database = EmailDatabase()
        self.report_generator = ReportGenerator(self.database)
        
    def initialize(self) -> bool:
        """
        Initialize the system with user credentials.
        
        Returns:
            bool: True if initialization successful
        """
        try:
            self.notifier.notify_info("Initializing Simple Gmail Spam Detection System...")
            
            # Get credentials from user
            print("\n" + "="*60)
            print("Gmail Login")
            print("="*60)
            print("\nNOTE: Use App Password, not your regular Gmail password")
            print("How to get App Password:")
            print("1. Go to: https://myaccount.google.com/security")
            print("2. Enable 2-Step Verification")
            print("3. Go to App Passwords")
            print("4. Generate new App Password for 'Mail'")
            print("5. Copy the 16-character password\n")
            
            email_address = input("Enter your Gmail address: ").strip()
            app_password = input("Enter your App Password (16 characters): ").strip().replace(" ", "")
            
            # Validate inputs
            if not email_address or '@' not in email_address:
                self.notifier.notify_error("Invalid email address")
                return False
                
            if len(app_password) != 16:
                self.notifier.notify_error("App Password should be 16 characters")
                return False
            
            # Connect to Gmail
            self.notifier.notify_info("Connecting to Gmail...")
            self.gmail = SimpleGmailLogin(email_address, app_password)
            
            if not self.gmail.connect():
                self.notifier.notify_error("Failed to connect to Gmail")
                self.notifier.notify_error("Please check your email and App Password")
                return False
                
            self.notifier.notify_success("Successfully connected to Gmail!")
            
            # Initialize classifier with Gmail client
            self.classifier = EmailClassifier(self.gmail)
            
            return True
            
        except KeyboardInterrupt:
            self.notifier.notify_info("\nSetup cancelled by user")
            return False
        except Exception as e:
            logger.error(f"Initialization failed: {str(e)}")
            self.notifier.notify_error(f"Initialization failed: {str(e)}")
            return False
            
    def process_emails(self, max_emails: int = 50, unread_only: bool = True) -> List[Dict]:
        """
        Process emails from Gmail.
        
        Args:
            max_emails: Maximum number of emails to process
            unread_only: If True, only process unread emails
            
        Returns:
            List of classification results
        """
        try:
            self.notifier.notify_info(f"Fetching emails (max: {max_emails})...")
            
            # Fetch emails
            emails = self.gmail.fetch_emails(limit=max_emails, unread_only=unread_only)
            
            if not emails:
                self.notifier.notify_info("No emails found to process")
                return []
                
            self.notifier.notify_success(f"Fetched {len(emails)} emails")
            print()
            
            # Process each email
            results = []
            for email_data in emails:
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
            email_data: Email data from IMAP
            
        Returns:
            Classification result dictionary
        """
        try:
            # Step 1: Parse email (already parsed by simple_gmail_login)
            parsed_email = email_data
            
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
            print("AI-Powered Gmail Spam Detection - Simple Login Version")
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
            
            # Disconnect and close database
            self.gmail.disconnect()
            self.database.close()
            
        except KeyboardInterrupt:
            self.notifier.notify_info("\nOperation cancelled by user")
            if self.gmail:
                self.gmail.disconnect()
            self.database.close()
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}")
            self.notifier.notify_error(f"Unexpected error: {str(e)}")
            if self.gmail:
                self.gmail.disconnect()
            self.database.close()


def main():
    """Main entry point"""
    system = SimpleSpamDetectionSystem()
    system.run()


if __name__ == "__main__":
    main()
