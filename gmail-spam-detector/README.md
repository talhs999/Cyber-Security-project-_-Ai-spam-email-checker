# AI-Powered Zero-Click Gmail Spam & Phishing Detection System

## 🎓 Academic Project Overview

This is a comprehensive cybersecurity project that demonstrates secure email analysis, AI-powered threat detection, and automated spam classification without requiring user interaction (zero-click approach).

**Key Features:**
- ✅ Secure OAuth 2.0 authentication (no passwords)
- ✅ Zero-click email analysis (no email opening)
- ✅ AI/NLP-based spam and phishing detection
- ✅ Three-tier classification (Safe/Suspicious/Spam)
- ✅ Automated threat response
- ✅ Comprehensive security documentation

---

## 📋 Table of Contents

1. [Features](#features)
2. [Architecture](#architecture)
3. [Prerequisites](#prerequisites)
4. [Installation](#installation)
5. [Gmail API Setup](#gmail-api-setup)
6. [Usage](#usage)
7. [Project Structure](#project-structure)
8. [Security Principles](#security-principles)
9. [How It Works](#how-it-works)
10. [Academic Value](#academic-value)

---

## ✨ Features

### Security Features
- **OAuth 2.0 Authentication**: Secure, password-free Gmail access
- **Zero-Click Analysis**: Emails analyzed without opening
- **No Attachment Execution**: Attachments detected but never executed
- **Minimal Permissions**: Read-only + label modification only
- **Safe Content Parsing**: HTML parsed without script execution

### Detection Capabilities
- **Phishing Detection**: Identifies spoofed senders, credential requests, urgent language
- **Spam Detection**: Detects promotional content, excessive links, suspicious patterns
- **URL Analysis**: Checks for malicious URLs, IP addresses, URL shorteners
- **Domain Validation**: Verifies sender domain reputation
- **Multi-layered Scoring**: Weighted threat scoring (0-100)

### Classification & Actions
- **Safe (0-30)**: Legitimate emails - no action
- **Suspicious (31-70)**: Potential threats - flagged for review
- **Spam (71-100)**: Clear threats - automatically moved to spam

### Database & Reporting 🆕
- **SQLite Database**: Stores classification history and statistics
- **Historical Analysis**: Track threat patterns over time
- **Automated Reports**: Daily/weekly summaries and threat analysis
- **Export Capability**: Export reports to text files
- **Audit Trail**: Complete classification history for forensics

---

## 🏗️ Architecture

```
┌─────────────┐
│   Gmail     │
│   Account   │
└──────┬──────┘
       │ OAuth 2.0
       ▼
┌─────────────────────────────────────┐
│   Gmail Spam Detection System      │
├─────────────────────────────────────┤
│  1. Authentication (OAuth 2.0)      │
│  2. Email Fetching (Gmail API)      │
│  3. Email Parsing (Zero-Click)      │
│  4. Feature Extraction (NLP)        │
│  5. Threat Detection (AI/Rules)     │
│  6. Classification (3-Tier)         │
│  7. Automated Actions (Labels/Spam) │
│  8. User Notification (Console)     │
└─────────────────────────────────────┘
```

---

## 📦 Prerequisites

- **Python**: 3.8 or higher
- **Gmail Account**: For testing
- **Google Cloud Project**: For OAuth 2.0 credentials
- **Internet Connection**: For Gmail API access

---

## 🚀 Installation

### Step 1: Clone or Download Project

```bash
cd "cyber security project/gmail-spam-detector"
```

### Step 2: Create Virtual Environment

```bash
python -m venv venv
```

### Step 3: Activate Virtual Environment

**Windows:**
```bash
venv\Scripts\activate
```

**macOS/Linux:**
```bash
source venv/bin/activate
```

### Step 4: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 5: Download NLTK Data (Optional for NLP)

```python
python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords')"
```

---

## 🔑 Gmail API Setup

### Step 1: Create Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project: "Gmail Spam Detector"
3. Enable the **Gmail API**:
   - Navigate to "APIs & Services" > "Library"
   - Search for "Gmail API"
   - Click "Enable"

### Step 2: Create OAuth 2.0 Credentials

1. Go to "APIs & Services" > "Credentials"
2. Click "Create Credentials" > "OAuth client ID"
3. Configure consent screen:
   - User Type: External
   - App name: "Gmail Spam Detector"
   - Add your email as test user
4. Create OAuth client ID:
   - Application type: **Desktop app**
   - Name: "Gmail Spam Detector Client"
5. Download the credentials JSON file
6. **Rename it to `credentials.json`**
7. **Place it in the project root directory**

### Step 3: Configure Scopes

The application requests these scopes:
- `https://www.googleapis.com/auth/gmail.readonly` - Read emails
- `https://www.googleapis.com/auth/gmail.modify` - Modify labels

---

## 💻 Usage

### Basic Usage

```bash
python main.py
```

### First Run

On first run, the application will:
1. Open your browser for OAuth authentication
2. Ask you to sign in to your Gmail account
3. Request permission to access your emails
4. Save the authentication token for future use

### What Happens

1. **Authentication**: Securely connects to Gmail
2. **Fetching**: Retrieves unread emails (default: 50 max)
3. **Analysis**: Analyzes each email for threats
4. **Classification**: Categorizes as Safe/Suspicious/Spam
5. **Action**: Moves spam to spam folder
6. **Notification**: Displays results with color coding

### Configuration

Edit `.env` file (copy from `.env.example`):

```env
# Maximum emails to process per run
MAX_EMAILS_PER_RUN=50

# Only process unread emails
FETCH_UNREAD_ONLY=True

# Classification thresholds (0-100)
SAFE_THRESHOLD=30
SUSPICIOUS_THRESHOLD=70

# Logging level
LOG_LEVEL=INFO
```

---

## 📁 Project Structure

```
gmail-spam-detector/
├── src/                          # Source code
│   ├── gmail_auth.py            # OAuth 2.0 authentication
│   ├── gmail_client.py          # Gmail API operations
│   ├── email_parser.py          # Email content extraction
│   ├── feature_extractor.py    # Feature engineering
│   ├── threat_detector.py      # AI/NLP detection engine
│   ├── classifier.py           # Email classification
│   └── notifier.py             # User notifications
├── config/                      # Configuration
│   └── settings.py             # Application settings
├── utils/                       # Utilities
│   ├── url_analyzer.py         # URL safety checking
│   └── domain_validator.py    # Domain reputation
├── docs/                        # Documentation
│   ├── SECURITY.md             # Security explanations
│   └── VIVA_NOTES.md           # Presentation guide
├── main.py                      # Application entry point
├── requirements.txt             # Python dependencies
├── .env.example                 # Environment template
├── .gitignore                   # Git ignore rules
└── README.md                    # This file
```

---

## 🔒 Security Principles

### 1. OAuth 2.0 Authentication
- **No Password Storage**: Uses token-based authentication
- **User Consent**: Explicit permission required
- **Scope Limitation**: Minimal necessary permissions
- **Token Refresh**: Automatic token renewal

### 2. Zero-Click Analysis
- **No Email Opening**: Analysis via API only
- **No Attachment Execution**: Attachments never downloaded
- **No Link Clicking**: URLs analyzed, never visited
- **Safe Parsing**: HTML parsed without script execution

### 3. Least Privilege
- **Read-Only Access**: Emails read but not modified
- **Limited Modification**: Only label changes allowed
- **No Deletion**: Emails moved to spam, not deleted

### 4. Defense in Depth
- **Multi-layered Detection**: Multiple detection algorithms
- **Weighted Scoring**: Combined threat assessment
- **Conservative Classification**: Err on side of caution

---

## ⚙️ How It Works

### 1. Authentication Flow
```
User → OAuth Consent → Google → Access Token → Application
```

### 2. Email Processing Pipeline
```
Fetch Email → Parse Content → Extract Features → Detect Threats → Classify → Take Action
```

### 3. Threat Detection Algorithm

**Phishing Indicators:**
- Sender spoofing (display name mismatch)
- Credential requests
- Urgent/pressure language
- Suspicious URLs (IP addresses, shorteners)
- Domain mismatches

**Spam Indicators:**
- Excessive promotional language
- Money-related terms
- Poor formatting (excessive caps, punctuation)
- Multiple URLs
- Free email provider + promotional content

### 4. Scoring System

Each indicator contributes to a threat score (0-100):
- **High Risk**: 20-25 points (e.g., spoofed sender)
- **Medium Risk**: 10-15 points (e.g., suspicious URL)
- **Low Risk**: 5-10 points (e.g., unknown domain)

**Final Score** = (Phishing Score × 0.6) + (Spam Score × 0.4)

---

## 🎓 Academic Value

### Cybersecurity Concepts Demonstrated

1. **Authentication & Authorization**: OAuth 2.0 implementation
2. **Threat Detection**: Multi-layered security analysis
3. **Risk Assessment**: Weighted scoring system
4. **Secure Coding**: Safe content parsing, no execution
5. **API Security**: Secure API integration practices
6. **Privacy**: Minimal data access, no storage

### Learning Outcomes

- Understanding OAuth 2.0 flow
- Email security threats (phishing, spam)
- NLP for content analysis
- Rule-based vs ML detection systems
- Secure software development practices
- API integration and rate limiting

### Viva Preparation

See [VIVA_NOTES.md](docs/VIVA_NOTES.md) for:
- Key talking points
- Technical explanations
- Security concepts
- Demo scenarios
- Common questions & answers

---

## 📊 Example Output

```
============================================================
AI-Powered Zero-Click Gmail Spam & Phishing Detection System
============================================================

INFO: Initializing AI-Powered Spam Detection System...
INFO: Authenticating with Gmail...
SUCCESS: Authentication successful!
INFO: Fetching emails (max: 50)...
SUCCESS: Fetched 10 emails

✗ SPAM (Score: 85)
  From: winner@prize-claim.tk
  Subject: Congratulations! You've won $1,000,000...
  Action: Moved to spam folder
  Threat Indicators:
    • Uses suspicious top-level domain
    • Contains excessive money-related terms (8 instances)
    • Uses urgent/pressure language

✓ SAFE (Score: 15)
  From: notifications@github.com
  Subject: [GitHub] New pull request
  Action: No action needed (safe email)

============================================================
CLASSIFICATION SUMMARY
============================================================
Total Emails Processed: 10
✓ Safe: 7
⚠ Suspicious: 2
✗ Spam: 1
============================================================
```

---

## 🛠️ Troubleshooting

### Issue: "credentials.json not found"
**Solution**: Download OAuth credentials from Google Cloud Console

### Issue: "Authentication failed"
**Solution**: Delete `token.pickle` and re-authenticate

### Issue: "Gmail API quota exceeded"
**Solution**: Wait a few minutes, the quota resets

### Issue: "Module not found"
**Solution**: Ensure virtual environment is activated and dependencies installed

---

## 📚 Further Enhancements

For production use, consider:
- Machine learning model training on labeled datasets
- Real-time URL reputation checking (VirusTotal API)
- SPF/DKIM/DMARC validation via DNS
- Database storage for historical analysis
- Web dashboard for visualization
- Email attachment sandboxing
- Integration with threat intelligence feeds

---

## 📄 License

This is an academic project for educational purposes.

---

## 👨‍💻 Author

**Cybersecurity Academic Project**  
Created for university submission and viva presentation

---

## 📞 Support

For questions or issues:
1. Review [SECURITY.md](docs/SECURITY.md) for security explanations
2. Check [VIVA_NOTES.md](docs/VIVA_NOTES.md) for presentation guidance
3. Review code comments for implementation details

---

## ⚠️ Disclaimer

This project is for educational purposes. Always review spam classifications manually before taking action on important emails. The system may have false positives/negatives.
