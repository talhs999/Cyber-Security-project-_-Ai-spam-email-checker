# Gmail Simple Login Setup Guide

## 🔐 Simple Login Method (App Password)

**Urdu:** Yeh method OAuth 2.0 se zyada simple hai. Bas email aur password chahiye!

**English:** This method is simpler than OAuth 2.0. Just need email and App Password!

---

## ⚡ Quick Setup (5 Minutes)

### Step 1: Enable 2-Step Verification

1. **Go to Google Account:**
   - Open: https://myaccount.google.com/security
   - Sign in with your Gmail account

2. **Enable 2-Step Verification:**
   - Find "2-Step Verification"
   - Click "Get Started"
   - Follow the steps to enable it
   - Use your phone number for verification

### Step 2: Generate App Password

1. **Go to App Passwords:**
   - After enabling 2-Step Verification
   - Go to: https://myaccount.google.com/apppasswords
   - Or search for "App Passwords" in Google Account settings

2. **Create App Password:**
   - Select app: **Mail**
   - Select device: **Windows Computer** (or Other)
   - Click **Generate**

3. **Copy the Password:**
   - You'll see a 16-character password like: `abcd efgh ijkl mnop`
   - **Copy this password** (remove spaces)
   - Keep it safe!

### Step 3: Run the Application

```powershell
cd "C:\Users\talha\OneDrive\Desktop\cyber security project\gmail-spam-detector"
.\venv\Scripts\python.exe main_simple.py
```

### Step 4: Enter Credentials

When prompted:
```
Enter your Gmail address: yourname@gmail.com
Enter your App Password: abcdefghijklmnop
```

**That's it! System will start working!**

---

## 🆚 Comparison: OAuth vs App Password

### OAuth 2.0 (Original Method)
- ✅ More secure
- ✅ No password storage
- ✅ Easy to revoke access
- ❌ Complex setup (Google Cloud Console)
- ❌ Requires browser authentication
- **File needed:** `credentials.json`
- **Command:** `python main.py`

### App Password (Simple Method)
- ✅ Very easy setup (5 minutes)
- ✅ No Google Cloud Console needed
- ✅ Direct login
- ❌ Less secure than OAuth
- ❌ Password stored in memory
- **File needed:** None (just email + password)
- **Command:** `python main_simple.py`

---

## 🚀 Usage

### Run Simple Version

```powershell
# Navigate to project
cd "C:\Users\talha\OneDrive\Desktop\cyber security project\gmail-spam-detector"

# Activate virtual environment
.\venv\Scripts\activate

# Run simple version
python main_simple.py
```

### First Time Login

```
============================================================
Gmail Login
============================================================

NOTE: Use App Password, not your regular Gmail password
How to get App Password:
1. Go to: https://myaccount.google.com/security
2. Enable 2-Step Verification
3. Go to App Passwords
4. Generate new App Password for 'Mail'
5. Copy the 16-character password

Enter your Gmail address: talha@gmail.com
Enter your App Password: abcdefghijklmnop

INFO: Connecting to Gmail...
SUCCESS: Successfully connected to Gmail!
```

---

## 📧 What It Does

Same features as OAuth version:
- ✅ Fetches emails from Gmail
- ✅ Analyzes for spam/phishing
- ✅ Classifies emails (Safe/Suspicious/Spam)
- ✅ Moves spam to spam folder
- ✅ Saves to database
- ✅ Generates reports

---

## 🔒 Security Notes

### App Password Security

**Safe:**
- App Password is specific to this app
- Can be revoked anytime
- Doesn't give access to your full account
- Separate from your main password

**Important:**
- Don't share your App Password
- Don't commit it to Git
- Revoke if compromised
- Use different App Passwords for different apps

### How to Revoke App Password

If you want to stop the app from accessing Gmail:

1. Go to: https://myaccount.google.com/apppasswords
2. Find the App Password you created
3. Click **Remove**
4. Done! App can't access Gmail anymore

---

## ❌ Troubleshooting

### Error: "Invalid credentials"
**Solution:**
- Make sure you're using **App Password**, not regular password
- App Password should be 16 characters
- Remove spaces from App Password
- Check if 2-Step Verification is enabled

### Error: "IMAP access disabled"
**Solution:**
1. Go to Gmail settings
2. Go to "Forwarding and POP/IMAP"
3. Enable IMAP access
4. Save changes

### Error: "Connection failed"
**Solution:**
- Check internet connection
- Make sure Gmail is accessible
- Try again after a few minutes
- Check if firewall is blocking

---

## 💡 Which Method to Use?

### Use OAuth 2.0 (`main.py`) if:
- ✅ For production/deployment
- ✅ For university project submission
- ✅ Maximum security needed
- ✅ You have time for setup

### Use App Password (`main_simple.py`) if:
- ✅ For testing/development
- ✅ Quick demo needed
- ✅ Don't want Google Cloud setup
- ✅ Personal use only

---

## 🎯 Quick Commands

### Simple Login Version
```powershell
# Run application
python main_simple.py

# With virtual environment
.\venv\Scripts\python.exe main_simple.py
```

### OAuth Version (Original)
```powershell
# Run application
python main.py

# With virtual environment
.\venv\Scripts\python.exe main.py
```

### Web Dashboard (Works with both)
```powershell
# Run dashboard
python web_dashboard.py
```

---

## 📝 Example Session

```
C:\...\gmail-spam-detector> python main_simple.py

============================================================
AI-Powered Gmail Spam Detection - Simple Login Version
============================================================

============================================================
Gmail Login
============================================================

Enter your Gmail address: talha@gmail.com
Enter your App Password: abcdefghijklmnop

INFO: Connecting to Gmail...
SUCCESS: Successfully connected to Gmail!
INFO: Fetching emails (max: 50)...
SUCCESS: Fetched 10 emails

✓ SAFE (Score: 15)
  From: notifications@github.com
  Subject: [GitHub] New pull request
  Action: No action needed (safe email)

✗ SPAM (Score: 85)
  From: winner@prize-claim.tk
  Subject: Congratulations! You've won...
  Action: Moved to spam folder

============================================================
CLASSIFICATION SUMMARY
============================================================
Total Emails Processed: 10
✓ Safe: 7
⚠ Suspicious: 2
✗ Spam: 1
============================================================

SUCCESS: Spam detection complete!
```

---

## ✅ Setup Checklist

- [ ] Enable 2-Step Verification on Gmail
- [ ] Generate App Password
- [ ] Copy App Password (16 characters)
- [ ] Run `python main_simple.py`
- [ ] Enter Gmail address
- [ ] Enter App Password
- [ ] Start detecting spam!

---

**Simple login ab ready hai! Bas 5 minute mein setup ho jayega!** 🎉
