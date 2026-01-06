# Security Documentation

## 🔒 Gmail Integration Security

This document explains the security principles and mechanisms used in the AI-Powered Gmail Spam & Phishing Detection System.

---

## Table of Contents

1. [OAuth 2.0 Authentication](#oauth-20-authentication)
2. [Zero-Click Security](#zero-click-security)
3. [API Security](#api-security)
4. [Threat Detection Methodology](#threat-detection-methodology)
5. [Data Privacy](#data-privacy)
6. [Security Best Practices](#security-best-practices)

---

## 1. OAuth 2.0 Authentication

### What is OAuth 2.0?

OAuth 2.0 is an industry-standard protocol for authorization. It allows applications to access user data without exposing passwords.

### Why OAuth 2.0 Instead of Passwords?

**Traditional Password Authentication Problems:**
- Passwords must be stored (security risk)
- Passwords transmitted over network (interception risk)
- Application has full account access
- No way to revoke access without changing password
- User must trust application with credentials

**OAuth 2.0 Benefits:**
- ✅ No password storage or transmission
- ✅ Token-based authentication
- ✅ Limited scope (specific permissions only)
- ✅ User consent required
- ✅ Easy revocation
- ✅ Time-limited access tokens

### OAuth 2.0 Flow in This Project

```
1. User runs application
   ↓
2. Application redirects to Google login
   ↓
3. User authenticates with Google (not the app)
   ↓
4. User grants permission (consent screen)
   ↓
5. Google returns authorization code
   ↓
6. Application exchanges code for access token
   ↓
7. Application uses token to access Gmail API
```

### Security Components

**1. Client ID & Client Secret**
- Identifies the application to Google
- Stored in `credentials.json`
- Should never be committed to public repositories

**2. Access Token**
- Short-lived token (typically 1 hour)
- Grants access to Gmail API
- Stored in `token.pickle`

**3. Refresh Token**
- Long-lived token
- Used to obtain new access tokens
- Stored securely in `token.pickle`

**4. Scopes**
- Define what the application can access
- This project uses minimal scopes:
  - `gmail.readonly`: Read emails only
  - `gmail.modify`: Modify labels only
- Does NOT request:
  - Email sending
  - Email deletion
  - Full account access

### Token Security

**Storage:**
- Tokens stored in `token.pickle` (binary format)
- File permissions should be restricted
- Never commit to version control (in `.gitignore`)

**Refresh Mechanism:**
```python
if token.expired and token.refresh_token:
    token.refresh(Request())  # Get new access token
```

**Revocation:**
- User can revoke access via Google Account settings
- Application can delete `token.pickle` to force re-authentication

---

## 2. Zero-Click Security

### What is Zero-Click?

Zero-click means emails are analyzed without:
- Opening them in an email client
- Clicking any links
- Downloading attachments
- Executing any content

### Why Zero-Click?

**Traditional Email Threats:**
- **Malicious Links**: Clicking leads to phishing sites
- **Malicious Attachments**: Opening executes malware
- **Tracking Pixels**: Opening reveals you read the email
- **Auto-executing Scripts**: Some email clients execute code

**Zero-Click Protection:**
- ✅ No link clicking → No phishing site visits
- ✅ No attachment opening → No malware execution
- ✅ No email rendering → No tracking pixel loading
- ✅ API-based reading → No script execution

### How Zero-Click Works

**Email Fetching:**
```python
# Gmail API returns email data as JSON
# No email "opening" occurs
message = service.users().messages().get(
    userId='me',
    id=message_id,
    format='full'  # Get all data without rendering
).execute()
```

**Content Parsing:**
```python
# HTML parsed with BeautifulSoup (safe parser)
soup = BeautifulSoup(html, 'lxml')
# Scripts removed before processing
for script in soup(['script', 'style']):
    script.decompose()
```

**URL Extraction:**
```python
# URLs extracted via regex, never visited
urls = re.findall(r'https?://[^\s]+', text)
# Analysis performed on URL string only
```

**Attachment Detection:**
```python
# Check for attachments without downloading
has_attachments = bool(part.get('filename'))
# NEVER: download or execute attachments
```

---

## 3. API Security

### Gmail API Security Features

**1. Rate Limiting**
- Gmail API quota: 250 units/user/second
- Application implements delays between calls
- Prevents API abuse

**2. HTTPS Only**
- All API calls use HTTPS
- Data encrypted in transit
- Prevents man-in-the-middle attacks

**3. Scope Validation**
- Google validates requested scopes
- Application can only perform authorized actions
- User can review permissions before granting

### API Security Implementation

**Rate Limiting:**
```python
def _rate_limit(self):
    time.sleep(0.1)  # 100ms delay between calls
```

**Error Handling:**
```python
try:
    # API call
except HttpError as error:
    # Handle API errors gracefully
    logger.error(f"API error: {error}")
```

**Minimal Permissions:**
- Only request necessary scopes
- Never request more than needed
- Principle of least privilege

---

## 4. Threat Detection Methodology

### Multi-Layered Detection

**Layer 1: Sender Analysis**
- Domain validation
- Display name vs email mismatch
- Free provider detection
- Known malicious domains

**Layer 2: Content Analysis**
- Phishing keywords
- Urgency indicators
- Credential requests
- Grammar and formatting

**Layer 3: URL Analysis**
- IP addresses in URLs
- URL shorteners
- Suspicious TLDs
- Domain mismatches
- Homograph attacks

**Layer 4: Structural Analysis**
- HTML complexity
- Attachment presence
- Header anomalies
- Reply-To mismatches

### Threat Scoring System

**Weighted Scoring:**
```
Final Score = (Phishing Score × 0.6) + (Spam Score × 0.4)
```

**Why Weighted?**
- Phishing is more dangerous than spam
- Phishing can lead to account compromise
- Spam is annoying but less harmful

**Risk Levels:**
- **High Risk** (20-25 points): Spoofed sender, credential requests
- **Medium Risk** (10-15 points): Suspicious URLs, urgency language
- **Low Risk** (5-10 points): Unknown domain, promotional content

### False Positive Mitigation

**Conservative Thresholds:**
- Safe: 0-30 (low threshold to avoid false negatives)
- Suspicious: 31-70 (middle ground for review)
- Spam: 71-100 (high threshold to avoid false positives)

**Multiple Indicators Required:**
- Single indicator rarely triggers spam classification
- Multiple indicators needed for high scores
- Reduces false positives

---

## 5. Data Privacy

### What Data is Accessed?

**Accessed:**
- Email headers (From, To, Subject, Date)
- Email body (text and HTML)
- URLs in emails
- Attachment metadata (filename, size)

**NOT Accessed:**
- Attachment contents
- Other Google services
- Contacts
- Calendar
- Drive files

### What Data is Stored?

**Stored Locally:**
- OAuth tokens (`token.pickle`)
- Log files (`spam_detector.log`)

**NOT Stored:**
- Email content
- Personal information
- Classification results (only logged)

### Data Transmission

**To Google:**
- OAuth authentication requests
- Gmail API requests (HTTPS encrypted)

**To Third Parties:**
- None - all processing is local

### GDPR Compliance Considerations

For production use:
- Implement data retention policies
- Provide user data export
- Allow data deletion
- Document data processing
- Obtain explicit consent

---

## 6. Security Best Practices

### For Users

**1. Credential Protection**
- Never share `credentials.json`
- Never commit `token.pickle` to Git
- Keep credentials file secure

**2. Token Management**
- Regularly review Google Account permissions
- Revoke access if suspicious activity
- Delete `token.pickle` when not in use

**3. Review Classifications**
- Manually review suspicious emails
- Report false positives/negatives
- Don't rely solely on automated classification

### For Developers

**1. Secure Coding**
- Never execute email content
- Validate all inputs
- Use safe parsing libraries
- Handle errors gracefully

**2. Dependency Management**
- Keep dependencies updated
- Review security advisories
- Use official Google libraries

**3. Logging**
- Log security events
- Don't log sensitive data
- Implement log rotation

**4. Testing**
- Test with various email types
- Test error conditions
- Test authentication flow

---

## Common Security Questions

### Q: Is my password stored?
**A:** No. OAuth 2.0 never requires or stores your password.

### Q: Can the application send emails?
**A:** No. It only has read and label modification permissions.

### Q: Can the application delete emails?
**A:** No. It can only move emails to spam folder, not delete them.

### Q: What if my token is stolen?
**A:** Revoke access via Google Account settings. The token becomes invalid immediately.

### Q: Are emails downloaded to my computer?
**A:** Email data is processed in memory and not permanently stored.

### Q: Can the application access other Google services?
**A:** No. Scopes are limited to Gmail only.

### Q: Is the analysis performed online?
**A:** Yes, but no data is sent to third parties. All processing is local.

---

## Security Incident Response

If you suspect a security issue:

1. **Revoke Access**
   - Go to Google Account → Security → Third-party access
   - Remove "Gmail Spam Detector"

2. **Delete Tokens**
   - Delete `token.pickle` file
   - Delete `credentials.json` if compromised

3. **Review Activity**
   - Check Gmail activity log
   - Review recent emails
   - Check for unauthorized access

4. **Re-authenticate**
   - Generate new credentials if needed
   - Re-run authentication flow

---

## Conclusion

This project demonstrates multiple layers of security:
- **Authentication**: OAuth 2.0 (no passwords)
- **Authorization**: Minimal scopes (least privilege)
- **Analysis**: Zero-click (no execution)
- **Privacy**: Local processing (no third-party sharing)

These principles make the system secure for analyzing potentially malicious emails without risk to the user.
