"""
Configuration settings for Gmail Spam & Phishing Detection System

This module centralizes all configuration parameters including:
- Gmail API scopes and permissions
- Classification thresholds
- Rate limiting parameters
- Logging configuration

Security Note: All sensitive credentials are loaded from environment variables
or secure OAuth tokens, never hardcoded.
"""

import os
from typing import List
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Settings:
    """Central configuration class for the application"""
    
    # Gmail API Configuration
    # Using read-only scope for fetching emails and modify scope for labeling
    GMAIL_SCOPES: List[str] = [
        'https://www.googleapis.com/auth/gmail.readonly',
        'https://www.googleapis.com/auth/gmail.modify'
    ]
    
    # OAuth 2.0 Credentials
    CREDENTIALS_FILE: str = 'credentials.json'
    TOKEN_FILE: str = 'token.pickle'
    
    # Classification Thresholds (0-100 scale)
    SAFE_THRESHOLD: int = int(os.getenv('SAFE_THRESHOLD', '30'))
    SUSPICIOUS_THRESHOLD: int = int(os.getenv('SUSPICIOUS_THRESHOLD', '70'))
    
    # Email Processing Configuration
    MAX_EMAILS_PER_RUN: int = int(os.getenv('MAX_EMAILS_PER_RUN', '50'))
    FETCH_UNREAD_ONLY: bool = os.getenv('FETCH_UNREAD_ONLY', 'True').lower() == 'true'
    
    # Rate Limiting (Gmail API quota: 250 units/user/second)
    API_RATE_LIMIT_DELAY: float = 0.1  # seconds between API calls
    
    # Logging Configuration
    LOG_LEVEL: str = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FORMAT: str = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    
    # Phishing Detection Keywords
    PHISHING_KEYWORDS: List[str] = [
        'verify your account', 'confirm your identity', 'suspended account',
        'unusual activity', 'click here immediately', 'urgent action required',
        'verify your password', 'confirm your information', 'account will be closed',
        'security alert', 'unauthorized access', 'update payment method',
        'prize winner', 'claim your reward', 'act now', 'limited time offer'
    ]
    
    # Suspicious TLDs (Top Level Domains)
    SUSPICIOUS_TLDS: List[str] = [
        '.tk', '.ml', '.ga', '.cf', '.gq', '.xyz', '.top', '.work', '.click'
    ]
    
    # URL Shortener Domains
    URL_SHORTENERS: List[str] = [
        'bit.ly', 'tinyurl.com', 'goo.gl', 'ow.ly', 't.co', 'is.gd',
        'buff.ly', 'adf.ly', 'short.link'
    ]
    
    # Trusted Email Domains (examples - customize based on your needs)
    TRUSTED_DOMAINS: List[str] = [
        'google.com', 'github.com', 'microsoft.com', 'amazon.com'
    ]

    # ============================================
    # Machine Learning Configuration (NEW)
    # ============================================

    # Enable/disable ML classifier
    ENABLE_ML_CLASSIFIER: bool = os.getenv('ENABLE_ML_CLASSIFIER', 'True').lower() == 'true'

    # Path to save/load trained ML model
    ML_MODEL_PATH: str = os.getenv('ML_MODEL_PATH', 'models/spam_classifier.joblib')

    # ML prediction confidence threshold (0.0-1.0)
    # Used to determine if ML prediction should be trusted
    ML_CONFIDENCE_THRESHOLD: float = float(os.getenv('ML_CONFIDENCE_THRESHOLD', '0.85'))

    # Weight of ML score in hybrid classification (0.0-1.0)
    # Final Score = (ML_Score × ML_WEIGHT) + (Threat_Score × (1-ML_WEIGHT))
    # Higher value = more weight on ML model
    ML_WEIGHT: float = float(os.getenv('ML_WEIGHT', '0.6'))

    # Automatically retrain model on startup if new labeled data exists
    RETRAIN_ON_STARTUP: bool = os.getenv('RETRAIN_ON_STARTUP', 'False').lower() == 'true'

    # Collect user feedback to improve ML model over time
    COLLECT_FEEDBACK: bool = os.getenv('COLLECT_FEEDBACK', 'True').lower() == 'true'

    # Minimum training samples required before training ML model
    MIN_TRAINING_SAMPLES: int = int(os.getenv('MIN_TRAINING_SAMPLES', '50'))

    # Enable NLP text processing (tokenization, stemming, etc.)
    ENABLE_NLP_FEATURES: bool = os.getenv('ENABLE_NLP_FEATURES', 'True').lower() == 'true'

# Create a singleton instance
settings = Settings()
