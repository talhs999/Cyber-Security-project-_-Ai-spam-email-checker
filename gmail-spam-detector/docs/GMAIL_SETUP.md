# Gmail API Setup Guide

## 🎯 Complete Guide to Connect Gmail

This guide will walk you through setting up Gmail API access for the spam detection system.

---

## 📋 Prerequisites

- Google Account (Gmail)
- Internet connection
- Web browser

---

## 🚀 Step-by-Step Setup

### Step 1: Create Google Cloud Project

1. **Go to Google Cloud Console**
   - Visit: https://console.cloud.google.com/
   - Sign in with your Google account

2. **Create New Project**
   - Click "Select a project" dropdown at the top
   - Click "NEW PROJECT"
   - Enter project name: `Gmail Spam Detector`
   - Click "CREATE"
   - Wait for project creation (takes a few seconds)

3. **Select Your Project**
   - Click "Select a project" dropdown
   - Choose "Gmail Spam Detector"

---

### Step 2: Enable Gmail API

1. **Navigate to APIs & Services**
   - Click hamburger menu (☰) on the left
   - Select "APIs & Services" → "Library"

2. **Search for Gmail API**
   - In the search box, type: `Gmail API`
   - Click on "Gmail API" from results

3. **Enable the API**
   - Click "ENABLE" button
   - Wait for activation (takes a few seconds)

---

### Step 3: Configure OAuth Consent Screen

1. **Go to OAuth Consent Screen**
   - Click hamburger menu (☰)
   - Select "APIs & Services" → "OAuth consent screen"

2. **Choose User Type**
   - Select "External"
   - Click "CREATE"

3. **Fill App Information**
   - **App name:** `Gmail Spam Detector`
   - **User support email:** Your email
   - **Developer contact:** Your email
   - Leave other fields as default
   - Click "SAVE AND CONTINUE"

4. **Scopes**
   - Click "ADD OR REMOVE SCOPES"
   - Search for: `gmail.readonly`
   - Check the box for `https://www.googleapis.com/auth/gmail.readonly`
   - Search for: `gmail.modify`
   - Check the box for `https://www.googleapis.com/auth/gmail.modify`
   - Click "UPDATE"
   - Click "SAVE AND CONTINUE"

5. **Test Users**
   - Click "ADD USERS"
   - Enter your Gmail address
   - Click "ADD"
   - Click "SAVE AND CONTINUE"

6. **Summary**
   - Review the information
   - Click "BACK TO DASHBOARD"

---

### Step 4: Create OAuth 2.0 Credentials

1. **Go to Credentials**
   - Click hamburger menu (☰)
   - Select "APIs & Services" → "Credentials"

2. **Create Credentials**
   - Click "+ CREATE CREDENTIALS" at the top
   - Select "OAuth client ID"

3. **Configure OAuth Client**
   - **Application type:** Desktop app
   - **Name:** `Gmail Spam Detector Client`
   - Click "CREATE"

4. **Download Credentials**
   - A popup will show your Client ID and Client Secret
   - Click "DOWNLOAD JSON"
   - Save the file

5. **Rename and Move File**
   - Rename the downloaded file to: `credentials.json`
   - Move it to your project folder:
     ```
     C:\Users\talha\OneDrive\Desktop\cyber security project\gmail-spam-detector\
     ```

---

### Step 5: Verify Setup

Your project folder should now have:
```
gmail-spam-detector/
├── credentials.json  ← This file should be here
├── main.py
├── requirements.txt
└── ...
```

---

## ✅ Testing the Connection

### Step 1: Install Dependencies

Open PowerShell in the project folder:

```powershell
# Create virtual environment
python -m venv venv

# Activate virtual environment
.\venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Step 2: Run Connection Test

```powershell
python setup_checker.py
```

This will:
- ✓ Check if credentials.json exists
- ✓ Verify dependencies are installed
- ✓ Test OAuth authentication
- ✓ Verify Gmail API connection

### Step 3: First Authentication

When you run the application for the first time:

1. **Browser Opens Automatically**
   - A browser window will open
   - You'll see Google's sign-in page

2. **Sign In**
   - Enter your Gmail credentials
   - Click "Next"

3. **Grant Permissions**
   - You'll see: "Gmail Spam Detector wants to access your Google Account"
   - Review the permissions:
     - Read your email messages and settings
     - Manage labels on your emails
   - Click "Allow"

4. **Success**
   - Browser will show: "The authentication flow has completed"
   - You can close the browser
   - Return to the terminal

5. **Token Saved**
   - A `token.pickle` file is created
   - You won't need to authenticate again (until token expires)

---

## 🔧 Troubleshooting

### Issue 1: "credentials.json not found"

**Solution:**
- Make sure you downloaded the credentials file
- Rename it to exactly `credentials.json`
- Place it in the project root folder
- Check the file path is correct

### Issue 2: "Access blocked: This app's request is invalid"

**Solution:**
- Go back to OAuth consent screen
- Make sure you added your email as a test user
- Verify scopes are correctly configured

### Issue 3: "The OAuth client was not found"

**Solution:**
- Delete `credentials.json`
- Go back to Google Cloud Console
- Create new OAuth client ID
- Download new credentials

### Issue 4: "Invalid grant: account not found"

**Solution:**
- Make sure you're using the same Google account
- Check that your email is added as a test user
- Try deleting `token.pickle` and re-authenticating

### Issue 5: "Access denied: Gmail API has not been used"

**Solution:**
- Go to Google Cloud Console
- Make sure Gmail API is enabled
- Wait a few minutes for activation
- Try again

---

## 🔒 Security Best Practices

### DO:
- ✅ Keep `credentials.json` secure
- ✅ Never commit `credentials.json` to Git
- ✅ Never share your credentials file
- ✅ Use the same Google account for testing
- ✅ Review permissions before granting

### DON'T:
- ❌ Share credentials.json with anyone
- ❌ Upload credentials to GitHub
- ❌ Use credentials on untrusted computers
- ❌ Grant permissions to unknown apps

---

## 📊 What Happens During Authentication?

```
1. You run the application
   ↓
2. App checks for existing token
   ↓
3. If no token, browser opens
   ↓
4. You sign in to Google
   ↓
5. Google shows permission request
   ↓
6. You click "Allow"
   ↓
7. Google sends authorization code
   ↓
8. App exchanges code for access token
   ↓
9. Token saved to token.pickle
   ↓
10. App can now access Gmail API
```

---

## 🎯 Verification Checklist

Before running the main application, verify:

- [ ] Google Cloud Project created
- [ ] Gmail API enabled
- [ ] OAuth consent screen configured
- [ ] Test user added (your email)
- [ ] OAuth client ID created
- [ ] credentials.json downloaded
- [ ] credentials.json in project folder
- [ ] Virtual environment created
- [ ] Dependencies installed
- [ ] Connection test passed

---

## 🚀 Next Steps

Once setup is complete:

1. **Run the Application**
   ```powershell
   python main.py
   ```

2. **Authenticate** (first time only)
   - Browser opens
   - Sign in
   - Grant permissions

3. **Start Detection**
   - Application fetches emails
   - Analyzes for threats
   - Classifies and takes action
   - Displays results

---

## 📞 Need Help?

If you encounter issues:

1. Check the troubleshooting section above
2. Review error messages carefully
3. Verify all setup steps were completed
4. Check Google Cloud Console for API status
5. Review the SECURITY.md documentation

---

## 🎓 For Viva Presentation

Be prepared to explain:
- Why OAuth 2.0 is more secure than passwords
- What scopes you requested and why
- How the authentication flow works
- What happens if credentials are compromised
- How to revoke access

---

**Setup Complete! You're ready to run the spam detection system! 🎉**
