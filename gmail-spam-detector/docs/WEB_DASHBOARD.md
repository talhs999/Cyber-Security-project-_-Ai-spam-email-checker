# Web Dashboard Guide

## 🌐 Web Dashboard Overview

**Urdu:** Ab aapke project mein ek beautiful web dashboard hai jo browser mein khulega!

**English:** Your project now has a beautiful web dashboard that opens in your browser!

---

## ✨ Dashboard Features

### 📊 Statistics Cards
- **Total Emails** - Kitne emails process hue
- **Safe Emails** - Kitne safe hain
- **Suspicious** - Kitne suspicious hain  
- **Spam Detected** - Kitne spam hain

### 📈 Interactive Charts
- **Pie Chart** - Classification distribution
- **Line Chart** - Weekly trend (7 days)

### 📧 Email Management
- **All Emails** - Sab emails dekho
- **Spam Emails** - Sirf spam emails
- **Suspicious** - Sirf suspicious emails
- **Safe Emails** - Sirf safe emails

### 🔍 Email Details
- Click on any email to see full details
- Threat indicators
- Sender information
- Classification reason

### 📥 Export Reports
- Export complete report to text file
- Download button in header

---

## 🚀 How to Run Dashboard

### Step 1: Make Sure Database Has Data

First, run the main application to process some emails:

```powershell
cd "C:\Users\talha\OneDrive\Desktop\cyber security project\gmail-spam-detector"
python main.py
```

This will create `spam_detector.db` with email data.

### Step 2: Start Web Dashboard

```powershell
python web_dashboard.py
```

### Step 3: Open in Browser

Dashboard will automatically open at:
```
http://127.0.0.1:5000
```

Or manually open your browser and go to that URL.

---

## 🎨 Dashboard Features in Detail

### Real-Time Stats
- Auto-refreshes every 30 seconds
- Manual refresh button in header
- Live data from database

### Email Viewer
- **Tabs** - Switch between All/Spam/Suspicious/Safe
- **Click email** - See full details in popup
- **Color coded** - Green (safe), Yellow (suspicious), Red (spam)
- **Threat score** - Shows score 0-100

### Charts
- **Pie Chart** - Visual breakdown of classifications
- **Trend Chart** - See how emails change over time
- **Interactive** - Hover to see details

### Top Threat Domains
- Shows which domains send most spam
- Helps identify patterns
- Click to see more details

---

## 💻 Dashboard URLs

### Main Dashboard
```
http://127.0.0.1:5000/
```

### API Endpoints (for developers)
```
http://127.0.0.1:5000/api/stats/summary
http://127.0.0.1:5000/api/stats/weekly
http://127.0.0.1:5000/api/emails/recent
http://127.0.0.1:5000/api/charts/classification
http://127.0.0.1:5000/api/charts/weekly-trend
```

---

## 🎯 Usage Workflow

### Complete Workflow:

1. **Process Emails**
   ```powershell
   python main.py
   ```
   - Fetches and classifies emails
   - Saves to database

2. **View Dashboard**
   ```powershell
   python web_dashboard.py
   ```
   - Opens web interface
   - Shows statistics and charts

3. **Manage Emails**
   - Click on emails to see details
   - Export reports
   - Track trends

---

## 📱 Dashboard Screenshots

### Main Dashboard
- 4 stat cards at top
- 2 charts in middle
- Email list with tabs
- Threat domains at bottom

### Email Details Modal
- Sender information
- Subject
- Classification
- Threat score
- Threat indicators
- Action taken

---

## 🔧 Customization

### Change Port
Edit `web_dashboard.py`:
```python
run_dashboard(port=8080)  # Change to any port
```

### Change Auto-Refresh Time
Edit `static/js/dashboard.js`:
```javascript
setInterval(refreshData, 60000);  // 60 seconds
```

---

## ❌ Troubleshooting

### Dashboard Not Opening?
```powershell
# Check if Flask is installed
pip install Flask

# Check if port is available
netstat -an | findstr "5000"
```

### No Data Showing?
```powershell
# Make sure database exists
dir spam_detector.db

# Run main.py first to create data
python main.py
```

### Charts Not Loading?
- Check internet connection (Chart.js loads from CDN)
- Clear browser cache
- Try different browser

---

## 🎓 For Viva Presentation

### Demo Points:
1. **Show dashboard** - Beautiful UI
2. **Explain stats** - Real-time data
3. **Click email** - Show details popup
4. **Show charts** - Visual analytics
5. **Export report** - Download functionality

### Technical Points:
- Flask web framework
- REST API architecture
- Chart.js for visualization
- Responsive design
- Real-time data updates

---

## 📊 Dashboard Architecture

```
Browser (Frontend)
    ↓
Flask Server (Backend)
    ↓
SQLite Database
    ↓
Email Classification Data
```

### Technologies Used:
- **Backend**: Flask (Python)
- **Frontend**: HTML, CSS, JavaScript
- **Charts**: Chart.js
- **Database**: SQLite
- **Styling**: Custom CSS with dark theme

---

## ✅ Quick Checklist

- [ ] Run `python main.py` to process emails
- [ ] Check `spam_detector.db` exists
- [ ] Run `python web_dashboard.py`
- [ ] Open `http://127.0.0.1:5000` in browser
- [ ] See statistics and charts
- [ ] Click on emails to see details
- [ ] Export report

---

**Dashboard ab fully ready hai! Browser mein beautiful UI ke saath!** 🎉
