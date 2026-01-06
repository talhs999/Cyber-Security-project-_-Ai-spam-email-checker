"""
Database Module for Email Classification Storage

This module handles persistent storage of email classification results,
threat statistics, and detection patterns using SQLite database.

Database Purpose:
- Store classification history
- Track threat patterns
- Generate statistics and reports
- Analyze detection accuracy
- Maintain audit trail

Academic Note: Databases are essential for security systems to:
1. Track incidents over time
2. Identify patterns and trends
3. Generate compliance reports
4. Support forensic analysis
"""

import sqlite3
import logging
from datetime import datetime
from typing import Dict, List, Optional
from pathlib import Path

logger = logging.getLogger(__name__)


class EmailDatabase:
    """
    SQLite database for storing email classification data.
    
    Tables:
    1. emails - Classified email records
    2. threat_indicators - Detected threat indicators
    3. statistics - Daily/weekly statistics
    """
    
    def __init__(self, db_path: str = "spam_detector.db", check_same_thread: bool = True):
        """
        Initialize database connection.
        
        Args:
            db_path: Path to SQLite database file
            check_same_thread: Whether to check if connection is used by same thread
        """
        self.db_path = db_path
        self.check_same_thread = check_same_thread
        self.conn = None
        self._connect()
        self._create_tables()
        
    def _connect(self):
        """Establish database connection"""
        try:
            self.conn = sqlite3.connect(
                self.db_path, 
                check_same_thread=self.check_same_thread
            )
            self.conn.row_factory = sqlite3.Row  # Return rows as dictionaries
            logger.info(f"Connected to database: {self.db_path}")
        except Exception as e:
            logger.error(f"Database connection failed: {str(e)}")
            raise
            
    def _create_tables(self):
        """Create database tables if they don't exist"""
        try:
            cursor = self.conn.cursor()
            
            # Table 1: Email Classification Records
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS emails (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    email_id TEXT UNIQUE NOT NULL,
                    sender_email TEXT NOT NULL,
                    sender_domain TEXT,
                    subject TEXT,
                    classification TEXT NOT NULL,
                    threat_score INTEGER NOT NULL,
                    phishing_score INTEGER,
                    spam_score INTEGER,
                    action_taken TEXT,
                    processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    has_attachments BOOLEAN,
                    url_count INTEGER,
                    body_length INTEGER
                )
            """)
            
            # Table 2: Threat Indicators
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS threat_indicators (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    email_id TEXT NOT NULL,
                    indicator_type TEXT NOT NULL,
                    indicator_description TEXT NOT NULL,
                    severity TEXT,
                    detected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (email_id) REFERENCES emails(email_id)
                )
            """)
            
            # Table 3: Daily Statistics
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS statistics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    date DATE UNIQUE NOT NULL,
                    total_processed INTEGER DEFAULT 0,
                    safe_count INTEGER DEFAULT 0,
                    suspicious_count INTEGER DEFAULT 0,
                    spam_count INTEGER DEFAULT 0,
                    avg_threat_score REAL,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Create indexes for better performance
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_emails_classification 
                ON emails(classification)
            """)
            
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_emails_processed_at 
                ON emails(processed_at)
            """)
            
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_threat_indicators_email_id 
                ON threat_indicators(email_id)
            """)
            
            self.conn.commit()
            logger.info("Database tables created successfully")
            
        except Exception as e:
            logger.error(f"Failed to create tables: {str(e)}")
            raise
            
    def save_email_classification(self, email_data: Dict, classification_result: Dict) -> bool:
        """
        Save email classification result to database.
        
        Args:
            email_data: Parsed email data
            classification_result: Classification result
            
        Returns:
            bool: True if saved successfully
        """
        try:
            cursor = self.conn.cursor()
            
            # Extract data
            email_id = email_data.get('id', '')
            sender = email_data.get('sender', {})
            sender_email = sender.get('email', '')
            sender_domain = sender.get('domain', '')
            subject = email_data.get('subject', '')
            
            classification = classification_result.get('category', 'UNKNOWN')
            threat_score = classification_result.get('score', 0)
            action_taken = classification_result.get('action_taken', '')
            
            has_attachments = email_data.get('has_attachments', False)
            url_count = len(email_data.get('urls', []))
            body_length = len(email_data.get('body_text', ''))
            
            # Insert email record
            cursor.execute("""
                INSERT OR REPLACE INTO emails 
                (email_id, sender_email, sender_domain, subject, classification, 
                 threat_score, action_taken, has_attachments, url_count, body_length)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (email_id, sender_email, sender_domain, subject, classification,
                  threat_score, action_taken, has_attachments, url_count, body_length))
            
            # Save threat indicators
            threat_indicators = classification_result.get('threat_indicators', [])
            for indicator in threat_indicators:
                self._save_threat_indicator(email_id, indicator)
            
            # Update daily statistics
            self._update_statistics(classification, threat_score)
            
            self.conn.commit()
            logger.info(f"Saved classification for email: {email_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to save email classification: {str(e)}")
            self.conn.rollback()
            return False
            
    def _save_threat_indicator(self, email_id: str, indicator: str):
        """Save individual threat indicator"""
        try:
            cursor = self.conn.cursor()
            
            # Determine severity based on keywords
            severity = 'HIGH' if any(word in indicator.lower() for word in 
                                    ['spoofing', 'credential', 'malicious']) else 'MEDIUM'
            
            cursor.execute("""
                INSERT INTO threat_indicators 
                (email_id, indicator_type, indicator_description, severity)
                VALUES (?, ?, ?, ?)
            """, (email_id, 'THREAT', indicator, severity))
            
        except Exception as e:
            logger.error(f"Failed to save threat indicator: {str(e)}")
            
    def _update_statistics(self, classification: str, threat_score: int):
        """Update daily statistics"""
        try:
            cursor = self.conn.cursor()
            today = datetime.now().date()
            
            # Get or create today's statistics
            cursor.execute("""
                INSERT OR IGNORE INTO statistics (date, total_processed)
                VALUES (?, 0)
            """, (today,))
            
            # Update counts
            cursor.execute("""
                UPDATE statistics 
                SET total_processed = total_processed + 1,
                    safe_count = safe_count + CASE WHEN ? = 'SAFE' THEN 1 ELSE 0 END,
                    suspicious_count = suspicious_count + CASE WHEN ? = 'SUSPICIOUS' THEN 1 ELSE 0 END,
                    spam_count = spam_count + CASE WHEN ? = 'SPAM' THEN 1 ELSE 0 END,
                    updated_at = CURRENT_TIMESTAMP
                WHERE date = ?
            """, (classification, classification, classification, today))
            
            # Update average threat score
            cursor.execute("""
                UPDATE statistics 
                SET avg_threat_score = (
                    SELECT AVG(threat_score) 
                    FROM emails 
                    WHERE DATE(processed_at) = ?
                )
                WHERE date = ?
            """, (today, today))
            
        except Exception as e:
            logger.error(f"Failed to update statistics: {str(e)}")
            
    def get_classification_history(self, limit: int = 100) -> List[Dict]:
        """
        Get recent classification history.
        
        Args:
            limit: Maximum number of records to return
            
        Returns:
            List of email classification records
        """
        try:
            cursor = self.conn.cursor()
            cursor.execute("""
                SELECT * FROM emails 
                ORDER BY processed_at DESC 
                LIMIT ?
            """, (limit,))
            
            return [dict(row) for row in cursor.fetchall()]
            
        except Exception as e:
            logger.error(f"Failed to get classification history: {str(e)}")
            return []
            
    def get_statistics(self, days: int = 7) -> List[Dict]:
        """
        Get statistics for the last N days.
        
        Args:
            days: Number of days to retrieve
            
        Returns:
            List of daily statistics
        """
        try:
            cursor = self.conn.cursor()
            cursor.execute("""
                SELECT * FROM statistics 
                ORDER BY date DESC 
                LIMIT ?
            """, (days,))
            
            return [dict(row) for row in cursor.fetchall()]
            
        except Exception as e:
            logger.error(f"Failed to get statistics: {str(e)}")
            return []
            
    def get_threat_indicators(self, email_id: str) -> List[Dict]:
        """
        Get threat indicators for a specific email.
        
        Args:
            email_id: Gmail message ID
            
        Returns:
            List of threat indicators
        """
        try:
            cursor = self.conn.cursor()
            cursor.execute("""
                SELECT * FROM threat_indicators 
                WHERE email_id = ?
                ORDER BY detected_at DESC
            """, (email_id,))
            
            return [dict(row) for row in cursor.fetchall()]
            
        except Exception as e:
            logger.error(f"Failed to get threat indicators: {str(e)}")
            return []
            
    def get_summary_stats(self) -> Dict:
        """
        Get overall summary statistics.
        
        Returns:
            Dictionary with summary statistics
        """
        try:
            cursor = self.conn.cursor()
            
            # Total emails processed
            cursor.execute("SELECT COUNT(*) as total FROM emails")
            total = cursor.fetchone()['total']
            
            # Classification breakdown
            cursor.execute("""
                SELECT classification, COUNT(*) as count 
                FROM emails 
                GROUP BY classification
            """)
            breakdown = {row['classification']: row['count'] for row in cursor.fetchall()}
            
            # Average threat score
            cursor.execute("SELECT AVG(threat_score) as avg_score FROM emails")
            avg_score = cursor.fetchone()['avg_score'] or 0
            
            # Top threat domains
            cursor.execute("""
                SELECT sender_domain, COUNT(*) as count 
                FROM emails 
                WHERE classification = 'SPAM'
                GROUP BY sender_domain 
                ORDER BY count DESC 
                LIMIT 5
            """)
            top_threat_domains = [dict(row) for row in cursor.fetchall()]
            
            return {
                'total_processed': total,
                'safe': breakdown.get('SAFE', 0),
                'suspicious': breakdown.get('SUSPICIOUS', 0),
                'spam': breakdown.get('SPAM', 0),
                'avg_threat_score': round(avg_score, 2),
                'top_threat_domains': top_threat_domains
            }
            
        except Exception as e:
            logger.error(f"Failed to get summary stats: {str(e)}")
            return {}
            
    def clear_all_data(self) -> bool:
        """
        Clear all data from the database.
        
        Returns:
            bool: True if successful
        """
        try:
            cursor = self.conn.cursor()
            
            # Delete all data from tables
            cursor.execute("DELETE FROM threat_indicators")
            cursor.execute("DELETE FROM emails")
            cursor.execute("DELETE FROM statistics")
            
            # Reset auto-increment counters
            cursor.execute("DELETE FROM sqlite_sequence WHERE name='threat_indicators'")
            cursor.execute("DELETE FROM sqlite_sequence WHERE name='emails'")
            cursor.execute("DELETE FROM sqlite_sequence WHERE name='statistics'")
            
            self.conn.commit()
            logger.info("Database cleared successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to clear database: {str(e)}")
            self.conn.rollback()
            return False

    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()
            logger.info("Database connection closed")
