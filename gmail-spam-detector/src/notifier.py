"""
Notifier Module

This module handles user notifications about email classification results.

Features:
- Console notifications with color coding
- Summary reports
- Detailed threat information

Academic Note: User notification is an important aspect of security
systems. Users need clear, actionable information about threats.
"""

import logging
from typing import Dict, List
from colorama import Fore, Style, init

# Initialize colorama for Windows color support
init(autoreset=True)

logger = logging.getLogger(__name__)


class Notifier:
    """
    Handle user notifications about email classification.
    
    This class provides clear, color-coded notifications to help
    users understand the security status of their emails.
    """
    
    def __init__(self):
        """Initialize notifier"""
        pass
        
    def notify_classification(self, result: Dict, email: Dict):
        """
        Notify user about a single email classification.
        
        Args:
            result: Classification result
            email: Parsed email data
        """
        category = result.get('category', 'UNKNOWN')
        score = result.get('score', 0)
        subject = email.get('subject', 'No Subject')
        sender = email.get('sender', {}).get('email', 'Unknown')
        
        # Color code based on category
        if category == 'SAFE':
            color = Fore.GREEN
            icon = '✓'
        elif category == 'SUSPICIOUS':
            color = Fore.YELLOW
            icon = '⚠'
        else:  # SPAM
            color = Fore.RED
            icon = '✗'
            
        print(f"\n{color}{icon} {category} (Score: {score}){Style.RESET_ALL}")
        print(f"  From: {sender}")
        print(f"  Subject: {subject[:60]}...")
        print(f"  Action: {result.get('action_taken', 'None')}")
        
        # Show threat indicators if any
        indicators = result.get('threat_indicators', [])
        if indicators:
            print(f"  {color}Threat Indicators:{Style.RESET_ALL}")
            for indicator in indicators[:3]:  # Show top 3
                print(f"    • {indicator}")
                
    def notify_summary(self, summary: Dict):
        """
        Display summary of all classifications.
        
        Args:
            summary: Classification summary dictionary
        """
        print("\n" + "="*60)
        print(f"{Fore.CYAN}CLASSIFICATION SUMMARY{Style.RESET_ALL}")
        print("="*60)
        print(f"Total Emails Processed: {summary.get('total', 0)}")
        print(f"{Fore.GREEN}✓ Safe: {summary.get('safe', 0)}{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}⚠ Suspicious: {summary.get('suspicious', 0)}{Style.RESET_ALL}")
        print(f"{Fore.RED}✗ Spam: {summary.get('spam', 0)}{Style.RESET_ALL}")
        print("="*60 + "\n")
        
    def notify_error(self, message: str):
        """
        Display error notification.
        
        Args:
            message: Error message
        """
        print(f"{Fore.RED}ERROR: {message}{Style.RESET_ALL}")
        
    def notify_info(self, message: str):
        """
        Display informational notification.
        
        Args:
            message: Info message
        """
        print(f"{Fore.CYAN}INFO: {message}{Style.RESET_ALL}")
        
    def notify_success(self, message: str):
        """
        Display success notification.
        
        Args:
            message: Success message
        """
        print(f"{Fore.GREEN}SUCCESS: {message}{Style.RESET_ALL}")
