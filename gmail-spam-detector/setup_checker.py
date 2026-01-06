"""
Setup Checker and Connection Tester

This script verifies that your Gmail Spam Detection System is properly configured
and tests the Gmail API connection.

Run this before running the main application to ensure everything is set up correctly.

Usage:
    python setup_checker.py
"""

import os
import sys
from pathlib import Path
from colorama import Fore, Style, init

# Initialize colorama
init(autoreset=True)

def print_header():
    """Print header"""
    print("\n" + "="*70)
    print(f"{Fore.CYAN}Gmail Spam Detection System - Setup Checker{Style.RESET_ALL}")
    print("="*70 + "\n")

def check_python_version():
    """Check Python version"""
    print(f"{Fore.YELLOW}[1/7] Checking Python version...{Style.RESET_ALL}")
    version = sys.version_info
    if version.major >= 3 and version.minor >= 8:
        print(f"{Fore.GREEN}✓ Python {version.major}.{version.minor}.{version.micro} (OK){Style.RESET_ALL}")
        return True
    else:
        print(f"{Fore.RED}✗ Python {version.major}.{version.minor}.{version.micro} (Need 3.8+){Style.RESET_ALL}")
        return False

def check_credentials_file():
    """Check if credentials.json exists"""
    print(f"\n{Fore.YELLOW}[2/7] Checking for credentials.json...{Style.RESET_ALL}")
    if os.path.exists('credentials.json'):
        print(f"{Fore.GREEN}✓ credentials.json found{Style.RESET_ALL}")
        return True
    else:
        print(f"{Fore.RED}✗ credentials.json NOT found{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}  → Please download from Google Cloud Console{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}  → See docs/GMAIL_SETUP.md for instructions{Style.RESET_ALL}")
        return False

def check_dependencies():
    """Check if required packages are installed"""
    print(f"\n{Fore.YELLOW}[3/7] Checking dependencies...{Style.RESET_ALL}")
    
    required_packages = [
        'google.auth',
        'google_auth_oauthlib',
        'googleapiclient',
        'bs4',
        'nltk',
        'tldextract',
        'colorama',
        'dotenv'
    ]
    
    missing = []
    for package in required_packages:
        try:
            __import__(package)
            print(f"{Fore.GREEN}  ✓ {package}{Style.RESET_ALL}")
        except ImportError:
            print(f"{Fore.RED}  ✗ {package} (missing){Style.RESET_ALL}")
            missing.append(package)
    
    if not missing:
        print(f"{Fore.GREEN}✓ All dependencies installed{Style.RESET_ALL}")
        return True
    else:
        print(f"{Fore.RED}✗ Missing dependencies{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}  → Run: pip install -r requirements.txt{Style.RESET_ALL}")
        return False

def check_project_structure():
    """Check if project structure is correct"""
    print(f"\n{Fore.YELLOW}[4/7] Checking project structure...{Style.RESET_ALL}")
    
    required_paths = [
        'src',
        'config',
        'utils',
        'docs',
        'main.py',
        'requirements.txt'
    ]
    
    missing = []
    for path in required_paths:
        if os.path.exists(path):
            print(f"{Fore.GREEN}  ✓ {path}{Style.RESET_ALL}")
        else:
            print(f"{Fore.RED}  ✗ {path} (missing){Style.RESET_ALL}")
            missing.append(path)
    
    if not missing:
        print(f"{Fore.GREEN}✓ Project structure is correct{Style.RESET_ALL}")
        return True
    else:
        print(f"{Fore.RED}✗ Project structure incomplete{Style.RESET_ALL}")
        return False

def check_env_file():
    """Check if .env file exists"""
    print(f"\n{Fore.YELLOW}[5/7] Checking environment configuration...{Style.RESET_ALL}")
    
    if os.path.exists('.env'):
        print(f"{Fore.GREEN}✓ .env file found{Style.RESET_ALL}")
        return True
    elif os.path.exists('.env.example'):
        print(f"{Fore.YELLOW}⚠ .env not found, but .env.example exists{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}  → Copy .env.example to .env (optional){Style.RESET_ALL}")
        return True
    else:
        print(f"{Fore.YELLOW}⚠ No .env file (using defaults){Style.RESET_ALL}")
        return True

def test_imports():
    """Test if all modules can be imported"""
    print(f"\n{Fore.YELLOW}[6/7] Testing module imports...{Style.RESET_ALL}")
    
    modules = [
        ('src.gmail_auth', 'Gmail Authentication'),
        ('src.gmail_client', 'Gmail Client'),
        ('src.email_parser', 'Email Parser'),
        ('src.feature_extractor', 'Feature Extractor'),
        ('src.threat_detector', 'Threat Detector'),
        ('src.classifier', 'Classifier'),
        ('config.settings', 'Settings')
    ]
    
    failed = []
    for module_name, display_name in modules:
        try:
            __import__(module_name)
            print(f"{Fore.GREEN}  ✓ {display_name}{Style.RESET_ALL}")
        except Exception as e:
            print(f"{Fore.RED}  ✗ {display_name}: {str(e)}{Style.RESET_ALL}")
            failed.append(display_name)
    
    if not failed:
        print(f"{Fore.GREEN}✓ All modules imported successfully{Style.RESET_ALL}")
        return True
    else:
        print(f"{Fore.RED}✗ Some modules failed to import{Style.RESET_ALL}")
        return False

def test_gmail_connection():
    """Test Gmail API connection"""
    print(f"\n{Fore.YELLOW}[7/7] Testing Gmail API connection...{Style.RESET_ALL}")
    
    if not os.path.exists('credentials.json'):
        print(f"{Fore.RED}✗ Cannot test - credentials.json missing{Style.RESET_ALL}")
        return False
    
    try:
        from src.gmail_auth import GmailAuthenticator
        
        print(f"{Fore.CYAN}  → Attempting authentication...{Style.RESET_ALL}")
        print(f"{Fore.CYAN}  → Browser will open for authorization{Style.RESET_ALL}")
        
        authenticator = GmailAuthenticator()
        success = authenticator.authenticate()
        
        if success:
            print(f"{Fore.GREEN}✓ Gmail API connection successful!{Style.RESET_ALL}")
            
            # Try to get service
            service = authenticator.get_gmail_service()
            if service:
                print(f"{Fore.GREEN}✓ Gmail service created successfully{Style.RESET_ALL}")
                
                # Try to get user profile
                try:
                    profile = service.users().getProfile(userId='me').execute()
                    email = profile.get('emailAddress', 'Unknown')
                    print(f"{Fore.GREEN}✓ Connected to: {email}{Style.RESET_ALL}")
                    return True
                except Exception as e:
                    print(f"{Fore.YELLOW}⚠ Connected but couldn't fetch profile: {str(e)}{Style.RESET_ALL}")
                    return True
            else:
                print(f"{Fore.RED}✗ Failed to create Gmail service{Style.RESET_ALL}")
                return False
        else:
            print(f"{Fore.RED}✗ Gmail API authentication failed{Style.RESET_ALL}")
            return False
            
    except Exception as e:
        print(f"{Fore.RED}✗ Connection test failed: {str(e)}{Style.RESET_ALL}")
        return False

def print_summary(results):
    """Print summary of checks"""
    print("\n" + "="*70)
    print(f"{Fore.CYAN}SETUP CHECK SUMMARY{Style.RESET_ALL}")
    print("="*70)
    
    checks = [
        "Python Version",
        "Credentials File",
        "Dependencies",
        "Project Structure",
        "Environment Config",
        "Module Imports",
        "Gmail Connection"
    ]
    
    for i, (check, result) in enumerate(zip(checks, results), 1):
        status = f"{Fore.GREEN}PASS{Style.RESET_ALL}" if result else f"{Fore.RED}FAIL{Style.RESET_ALL}"
        print(f"{i}. {check}: {status}")
    
    print("="*70)
    
    all_passed = all(results)
    
    if all_passed:
        print(f"\n{Fore.GREEN}✓ ALL CHECKS PASSED!{Style.RESET_ALL}")
        print(f"{Fore.GREEN}✓ Your system is ready to run!{Style.RESET_ALL}")
        print(f"\n{Fore.CYAN}Next step: Run 'python main.py' to start detection{Style.RESET_ALL}\n")
    else:
        print(f"\n{Fore.RED}✗ SOME CHECKS FAILED{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}Please fix the issues above before running the application{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}See docs/GMAIL_SETUP.md for detailed setup instructions{Style.RESET_ALL}\n")

def main():
    """Main function"""
    print_header()
    
    # Run all checks
    results = [
        check_python_version(),
        check_credentials_file(),
        check_dependencies(),
        check_project_structure(),
        check_env_file(),
        test_imports(),
        test_gmail_connection()
    ]
    
    # Print summary
    print_summary(results)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}Setup check cancelled by user{Style.RESET_ALL}")
    except Exception as e:
        print(f"\n{Fore.RED}Unexpected error: {str(e)}{Style.RESET_ALL}")
