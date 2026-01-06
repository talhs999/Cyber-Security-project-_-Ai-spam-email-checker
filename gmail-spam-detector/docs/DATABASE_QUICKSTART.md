# Database Quick Start Guide (Urdu/English)

## 🗄️ Database Kya Hai? (What is Database?)

**Urdu:** Yeh system ab ek **SQLite database** use karta hai jo emails ki classification history, statistics, aur threat patterns ko store karta hai.

**English:** This system now uses a **SQLite database** to store email classification history, statistics, and threat patterns.

---

## 📊 Database Mein Kya Store Hota Hai? (What Gets Stored?)

### ✅ Stored Data
- Email sender information (from, domain)
- Classification result (Safe/Suspicious/Spam)
- Threat scores
- Detected threat indicators
- Action taken (moved to spam, etc.)
- Processing timestamp
- Email characteristics (URLs count, attachments, length)

### ❌ NOT Stored (Privacy)
- Email body content
- Attachment contents
- Personal information
- OAuth tokens

---

## 🚀 Kaise Use Karein? (How to Use?)

### Automatic Operation
Database automatically kaam karta hai:

```powershell
python main.py
```

Jab app run hogi, automatically:
1. ✅ Database create hoga (`spam_detector.db`)
2. ✅ Har email ki classification save hogi
3. ✅ Statistics update hongi
4. ✅ Reports generate hongi

---

## 📈 Reports Dekhna (View Reports)

### After Processing
Jab emails process ho jayein, aapko poocha jayega:

```
Generate detailed reports? (y/n): y
```

**Type 'y'** to see:
- Summary report (total stats)
- Weekly report (daily breakdown)
- Threat analysis (spam patterns)

### Export Reports
Reports ko file mein save karne ke liye:

```
Export reports to file? (y/n): y
```

File create hogi: `spam_detection_report.txt`

---

## 🗂️ Database Tables

### 1. emails
Har classified email ka record

### 2. threat_indicators  
Detected threats ki details

### 3. statistics
Daily/weekly statistics

---

## 💻 Database File Location

```
gmail-spam-detector/
└── spam_detector.db  ← Database file yahan banti hai
```

---

## 🔍 Database Manually Dekhna (View Manually)

### Option 1: Python Script
```python
from src.database import EmailDatabase

db = EmailDatabase()

# Recent emails dekhein
history = db.get_classification_history(limit=10)
for email in history:
    print(f"{email['sender_email']}: {email['classification']}")

# Statistics dekhein
stats = db.get_summary_stats()
print(f"Total: {stats['total_processed']}")
print(f"Spam: {stats['spam']}")

db.close()
```

### Option 2: DB Browser
Download **DB Browser for SQLite** (free):
- https://sqlitebrowser.org/
- Open `spam_detector.db`
- View all tables and data

---

## 📊 Example Reports

### Summary Report
```
============================================================
EMAIL CLASSIFICATION SUMMARY REPORT
============================================================

Total Emails Processed: 25
✓ Safe: 18
⚠ Suspicious: 4
✗ Spam: 3

Average Threat Score: 28.5

Top Threat Domains:
  1. spam-sender.tk (2 emails)
  2. phishing-site.xyz (1 email)
============================================================
```

### Weekly Report
```
============================================================
WEEKLY STATISTICS REPORT
============================================================

Date         Total    Safe     Suspicious   Spam     Avg Score
----------------------------------------------------------------------
2026-01-04   10       7        2            1        25.3
2026-01-03   8        6        1            1        22.1
2026-01-02   7        5        1            1        30.5
============================================================
```

---

## 🎯 Benefits (Fayde)

### 1. History Tracking
- Purani emails ki classification dekh sakte hain
- Patterns identify kar sakte hain

### 2. Statistics
- Daily/weekly stats
- Threat trends
- Detection accuracy

### 3. Reports
- Professional reports
- Export kar sakte hain
- Viva presentation ke liye

### 4. Forensics
- Past incidents investigate kar sakte hain
- Audit trail available hai

---

## 🔧 Troubleshooting

### Database File Nahi Bani?
- Check permissions
- Run application once
- Database automatically create hogi

### Database Corrupt Ho Gayi?
```powershell
# Delete old database
Remove-Item spam_detector.db

# Run again (new database banegi)
python main.py
```

### Database Bahut Badi Ho Gayi?
- Export old data
- Delete database
- Fresh start karein

---

## 📚 Complete Documentation

Detailed information ke liye dekhen:
- [DATABASE.md](DATABASE.md) - Complete database documentation
- [README.md](../README.md) - Main documentation

---

## ✅ Quick Checklist

- [ ] Run `python main.py`
- [ ] Process some emails
- [ ] Check `spam_detector.db` file created
- [ ] Generate reports (type 'y')
- [ ] Export reports to file
- [ ] View database with DB Browser (optional)

---

**Database ab fully integrated hai! Automatic storage aur reporting ready hai!** 🎉
