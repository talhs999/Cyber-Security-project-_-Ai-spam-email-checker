"""
Database Report Generator

This module generates reports from the stored email classification data.
It provides insights into threat patterns, statistics, and trends.

Reports Include:
- Daily/Weekly summaries
- Threat pattern analysis
- Domain reputation reports
- Detection accuracy metrics
"""

import logging
from typing import Dict, List
from datetime import datetime, timedelta
from colorama import Fore, Style

logger = logging.getLogger(__name__)


class ReportGenerator:
    """Generate reports from database"""
    
    def __init__(self, database):
        """
        Initialize report generator.
        
        Args:
            database: EmailDatabase instance
        """
        self.db = database
        
    def generate_summary_report(self) -> str:
        """
        Generate overall summary report.
        
        Returns:
            Formatted report string
        """
        stats = self.db.get_summary_stats()
        
        report = "\n" + "="*70 + "\n"
        report += f"{Fore.CYAN}EMAIL CLASSIFICATION SUMMARY REPORT{Style.RESET_ALL}\n"
        report += "="*70 + "\n\n"
        
        report += f"Total Emails Processed: {stats.get('total_processed', 0)}\n"
        report += f"{Fore.GREEN}✓ Safe: {stats.get('safe', 0)}{Style.RESET_ALL}\n"
        report += f"{Fore.YELLOW}⚠ Suspicious: {stats.get('suspicious', 0)}{Style.RESET_ALL}\n"
        report += f"{Fore.RED}✗ Spam: {stats.get('spam', 0)}{Style.RESET_ALL}\n"
        report += f"\nAverage Threat Score: {stats.get('avg_threat_score', 0)}\n"
        
        # Top threat domains
        top_domains = stats.get('top_threat_domains', [])
        if top_domains:
            report += f"\n{Fore.RED}Top Threat Domains:{Style.RESET_ALL}\n"
            for i, domain in enumerate(top_domains, 1):
                report += f"  {i}. {domain['sender_domain']} ({domain['count']} emails)\n"
        
        report += "="*70 + "\n"
        
        return report
        
    def generate_weekly_report(self) -> str:
        """
        Generate weekly statistics report.
        
        Returns:
            Formatted report string
        """
        stats = self.db.get_statistics(days=7)
        
        report = "\n" + "="*70 + "\n"
        report += f"{Fore.CYAN}WEEKLY STATISTICS REPORT{Style.RESET_ALL}\n"
        report += "="*70 + "\n\n"
        
        if not stats:
            report += "No data available for the past week.\n"
        else:
            report += f"{'Date':<12} {'Total':<8} {'Safe':<8} {'Suspicious':<12} {'Spam':<8} {'Avg Score':<10}\n"
            report += "-"*70 + "\n"
            
            for day in stats:
                date = day['date']
                total = day['total_processed']
                safe = day['safe_count']
                suspicious = day['suspicious_count']
                spam = day['spam_count']
                avg_score = round(day['avg_threat_score'] or 0, 1)
                
                report += f"{date:<12} {total:<8} {safe:<8} {suspicious:<12} {spam:<8} {avg_score:<10}\n"
        
        report += "="*70 + "\n"
        
        return report
        
    def generate_threat_analysis(self) -> str:
        """
        Generate threat pattern analysis.
        
        Returns:
            Formatted report string
        """
        history = self.db.get_classification_history(limit=50)
        
        report = "\n" + "="*70 + "\n"
        report += f"{Fore.CYAN}THREAT PATTERN ANALYSIS{Style.RESET_ALL}\n"
        report += "="*70 + "\n\n"
        
        if not history:
            report += "No classification history available.\n"
        else:
            # Analyze patterns
            spam_emails = [e for e in history if e['classification'] == 'SPAM']
            
            report += f"Recent Spam Emails: {len(spam_emails)}\n\n"
            
            if spam_emails:
                report += f"{Fore.RED}Recent Spam Examples:{Style.RESET_ALL}\n"
                for i, email in enumerate(spam_emails[:5], 1):
                    report += f"\n{i}. From: {email['sender_email']}\n"
                    report += f"   Subject: {email['subject'][:50]}...\n"
                    report += f"   Threat Score: {email['threat_score']}\n"
                    report += f"   Action: {email['action_taken']}\n"
        
        report += "\n" + "="*70 + "\n"
        
        return report
        
    def export_to_file(self, filename: str = "report.txt"):
        """
        Export all reports to a text file.
        
        Args:
            filename: Output filename
        """
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write("AI-POWERED GMAIL SPAM DETECTION - COMPREHENSIVE REPORT\n")
                f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write("\n")
                
                # Remove color codes for file export
                summary = self.generate_summary_report()
                weekly = self.generate_weekly_report()
                threats = self.generate_threat_analysis()
                
                # Strip ANSI color codes
                import re
                ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
                
                f.write(ansi_escape.sub('', summary))
                f.write("\n\n")
                f.write(ansi_escape.sub('', weekly))
                f.write("\n\n")
                f.write(ansi_escape.sub('', threats))
                
            logger.info(f"Report exported to: {filename}")
            print(f"{Fore.GREEN}✓ Report exported to: {filename}{Style.RESET_ALL}")
            
        except Exception as e:
            logger.error(f"Failed to export report: {str(e)}")
            print(f"{Fore.RED}✗ Failed to export report: {str(e)}{Style.RESET_ALL}")
