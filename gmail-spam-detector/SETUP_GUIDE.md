# Quick Setup Guide

## ⚡ Fast Setup (Recommended)

### Option 1: Using Setup Script (Easiest)

1. **Open PowerShell in project folder:**
   ```powershell
   cd "C:\Users\talha\OneDrive\Desktop\cyber security project\gmail-spam-detector"
   ```

2. **Run setup script:**
   ```powershell
   .\setup.bat
   ```

   This will automatically:
   - ✅ Create virtual environment
   - ✅ Activate it
   - ✅ Install all dependencies

---

### Option 2: Manual Setup

1. **Navigate to project folder:**
   ```powershell
   cd "C:\Users\talha\OneDrive\Desktop\cyber security project\gmail-spam-detector"
   ```

2. **Create virtual environment:**
   ```powershell
   python -m venv venv
   ```

3. **Activate virtual environment:**
   ```powershell
   .\venv\Scripts\activate
   ```

4. **Install dependencies:**
   ```powershell
   pip install -r requirements.txt
   ```

---

## ✅ Verify Installation

```powershell
python setup_checker.py
```

---

## 🚀 Run the Application

```powershell
python main.py
```

---

## ❌ Common Errors

### Error: "requirements.txt not found"
**Solution:** Make sure you're in the correct directory
```powershell
cd "C:\Users\talha\OneDrive\Desktop\cyber security project\gmail-spam-detector"
```

### Error: "Python not found"
**Solution:** Install Python 3.8+ from python.org

### Error: "pip not found"
**Solution:** Reinstall Python with "Add to PATH" option checked

---

## 📁 Correct Directory Structure

You should be in this folder:
```
C:\Users\talha\OneDrive\Desktop\cyber security project\gmail-spam-detector\
```

When you run `dir` or `ls`, you should see:
- main.py
- requirements.txt
- setup.bat
- src/
- config/
- docs/

---

## 💡 Pro Tip

Always make sure you're in the `gmail-spam-detector` folder before running commands!

```powershell
# Check current directory
Get-Location

# Should show: ...\cyber security project\gmail-spam-detector
```
