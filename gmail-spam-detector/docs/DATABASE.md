# Database Documentation

## 📊 Database Overview

The Gmail Spam Detection System now includes a **SQLite database** to store:
- Email classification history
- Threat indicators
- Daily/weekly statistics
- Detection patterns

---

## 🗄️ Database Structure

### Database File
- **Location**: `spam_detector.db` (project root)
- **Type**: SQLite 3
- **Size**: Grows with usage (typically < 10MB)

---

## 📋 Database Tables

### 1. `emails` Table
Stores all classified email records.

| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER | Primary key (auto-increment) |
| email_id | TEXT | Gmail message ID (unique) |
| sender_email | TEXT | Sender email address |
| sender_domain | TEXT | Sender domain |
| subject | TEXT | Email subject |
| classification | TEXT | SAFE/SUSPICIOUS/SPAM |
| threat_score | INTEGER | Threat score (0-100) |
| phishing_score | INTEGER | Phishing score |
| spam_score | INTEGER | Spam score |
| action_taken | TEXT | Action performed |
| processed_at | TIMESTAMP | Processing timestamp |
| has_attachments | BOOLEAN | Has attachments flag |
| url_count | INTEGER | Number of URLs |
| body_length | INTEGER | Email body length |

### 2. `threat_indicators` Table
Stores detected threat indicators for each email.

| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER | Primary key |
| email_id | TEXT | Reference to emails table |
| indicator_type | TEXT | Type of threat |
| indicator_description | TEXT | Description |
| severity | TEXT | HIGH/MEDIUM/LOW |
| detected_at | TIMESTAMP | Detection timestamp |

### 3. `statistics` Table
Stores daily aggregated statistics.

| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER | Primary key |
| date | DATE | Statistics date (unique) |
| total_processed | INTEGER | Total emails processed |
| safe_count | INTEGER | Safe emails count |
| suspicious_count | INTEGER | Suspicious emails count |
| spam_count | INTEGER | Spam emails count |
| avg_threat_score | REAL | Average threat score |
| updated_at | TIMESTAMP | Last update time |

---

## 🔍 What Gets Stored

### Automatically Saved
Every time an email is classified, the system saves:
- ✅ Email metadata (sender, subject, date)
- ✅ Classification result (Safe/Suspicious/Spam)
- ✅ Threat scores
- ✅ Detected threat indicators
- ✅ Action taken (moved to spam, etc.)
- ✅ Email characteristics (URLs, attachments, length)

### NOT Stored
For privacy and security:
- ❌ Email body content
- ❌ Attachment contents
- ❌ Personal information
- ❌ OAuth tokens

---

## 📊 Reports Available

### 1. Summary Report
Overall statistics:
- Total emails processed
- Classification breakdown
- Average threat score
- Top threat domains

### 2. Weekly Report
Daily statistics for the past 7 days:
- Emails processed per day
- Classification counts
- Trend analysis

### 3. Threat Analysis
Recent spam patterns:
- Recent spam examples
- Common threat indicators
- Domain patterns

---

## 💻 Using the Database

### Automatic Operation
The database works automatically:
```python
python main.py  # Database saves results automatically
```

### View Reports
After processing emails, you'll be asked:
```
Generate detailed reports? (y/n): y
Export reports to file? (y/n): y
```

### Report Files
Reports are exported to:
- `spam_detection_report.txt` - Complete report

---

## 🔧 Database Management

### View Database
You can view the database using:
- **DB Browser for SQLite** (free tool)
- **SQLite command line**
- **Python scripts**

### Example: View Recent Classifications
```python
from src.database import EmailDatabase

db = EmailDatabase()
history = db.get_classification_history(limit=10)
for email in history:
    print(f"{email['sender_email']}: {email['classification']}")
db.close()
```

### Example: Get Statistics
```python
from src.database import EmailDatabase

db = EmailDatabase()
stats = db.get_summary_stats()
print(f"Total processed: {stats['total_processed']}")
print(f"Spam detected: {stats['spam']}")
db.close()
```

---

## 📈 Benefits of Database Storage

### 1. Historical Analysis
- Track threat patterns over time
- Identify recurring spam sources
- Analyze detection accuracy

### 2. Reporting
- Generate compliance reports
- Create statistics dashboards
- Export data for analysis

### 3. Forensics
- Investigate past incidents
- Review classification decisions
- Audit trail for security

### 4. Improvement
- Identify false positives/negatives
- Tune detection thresholds
- Improve accuracy over time

---

## 🔒 Security Considerations

### Data Privacy
- Only metadata stored (no email content)
- Database file should be protected
- Consider encryption for sensitive deployments

### Access Control
- Database file permissions should be restricted
- No remote access by default
- Local storage only

### Backup
- Regular backups recommended
- Export reports periodically
- Archive old data as needed

---

## 🎓 Academic Value

### Demonstrates
- Database design for security systems
- Data persistence and retrieval
- Statistical analysis
- Audit logging
- Forensic capabilities

### Learning Outcomes
- SQL database operations
- Data modeling for security
- Report generation
- Trend analysis
- Compliance reporting

---

## 🛠️ Troubleshooting

### Database Locked
If you see "database is locked":
- Close other connections
- Restart the application
- Check file permissions

### Database Corrupted
If database is corrupted:
- Delete `spam_detector.db`
- Run application again (creates new database)
- Previous data will be lost

### Large Database
If database grows too large:
- Export old data
- Delete old records
- Optimize database (VACUUM command)

---

## 📝 Database Schema Diagram

```
┌─────────────────┐
│     emails      │
├─────────────────┤
│ id (PK)         │
│ email_id (UK)   │◄─┐
│ sender_email    │  │
│ classification  │  │
│ threat_score    │  │
│ ...             │  │
└─────────────────┘  │
                     │
┌─────────────────┐  │
│threat_indicators│  │
├─────────────────┤  │
│ id (PK)         │  │
│ email_id (FK)   │──┘
│ indicator_type  │
│ severity        │
│ ...             │
└─────────────────┘

┌─────────────────┐
│   statistics    │
├─────────────────┤
│ id (PK)         │
│ date (UK)       │
│ total_processed │
│ safe_count      │
│ spam_count      │
│ ...             │
└─────────────────┘
```

---

## ✅ Database Features Summary

- ✅ Automatic data storage
- ✅ Three normalized tables
- ✅ Indexed for performance
- ✅ Daily statistics aggregation
- ✅ Comprehensive reporting
- ✅ Export capabilities
- ✅ Historical analysis
- ✅ Threat pattern tracking

**Your system now has complete data persistence and reporting capabilities!** 📊
