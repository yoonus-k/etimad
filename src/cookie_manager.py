"""
Automated Cookie Management using Selenium
Automatically logs into Etimad and retrieves cookies
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time
import json
import os

class EtimadBrowserAutomation:
    def __init__(self, username, password, headless=False, browser="chrome"):
        self.username = username
        self.password = password
        self.headless = headless
        self.browser_type = browser
        self.driver = None
        self.cookies = {}
        
    def _setup_browser(self):
        """Setup browser driver"""
        if self.browser_type == "chrome":
            options = Options()
            if self.headless:
                options.add_argument('--headless')
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--disable-blink-features=AutomationControlled')
            options.add_experimental_option("excludeSwitches", ["enable-automation"])
            options.add_experimental_option('useAutomationExtension', False)
            
            # Use webdriver-manager to automatically download and manage ChromeDriver
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=options)
        else:
            raise ValueError(f"Browser '{self.browser_type}' not supported yet")
    
    def login_and_get_cookies(self):
        """
        Automatically login to Etimad and retrieve cookies
        Returns: dict of cookies
        """
        try:
            print("🌐 Starting browser automation...")
            self._setup_browser()
            
            # Navigate to Etimad homepage
            print("📱 Opening Etimad website...")
            self.driver.get("https://tenders.etimad.sa")
            time.sleep(3)
            
            # Click login button
            print("🔍 Looking for login button...")
            try:
                login_button = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.LINK_TEXT, "تسجيل الدخول"))
                )
                # Use JavaScript click to avoid overlay issues
                self.driver.execute_script("arguments[0].click();", login_button)
                time.sleep(3)
                print("   ✅ Clicked login button")
            except Exception as e:
                print(f"   ⚠️  Login button click failed: {e}")
                return None
            
            # Click "أعمال" (Business) tab on login page
            print("🏢 Selecting Business (أعمال) login type...")
            try:
                # Wait for the login page to load
                time.sleep(2)
                
                # Find and click the "أعمال" tab
                business_tab = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.LINK_TEXT, "أعمال"))
                )
                self.driver.execute_script("arguments[0].click();", business_tab)
                time.sleep(2)
                print("   ✅ Selected Business login")
            except Exception as e:
                print(f"   ⚠️  Could not find Business tab: {e}")
                print("   Continuing anyway - may already be on correct tab")
            
            # Wait for login form (redirects to login.etimad.sa)
            print("⌨️  Waiting for login form...")
            try:
                username_field = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.ID, "Username"))
                )
                password_field = self.driver.find_element(By.ID, "Password")
                print("   ✅ Login form loaded")
            except Exception as e:
                print(f"   ❌ Login form not found: {e}")
                return None
            
            # Enter credentials
            print("✍️  Entering credentials...")
            username_field.clear()
            username_field.send_keys(self.username)
            time.sleep(0.5)
            
            password_field.clear()
            password_field.send_keys(self.password)
            time.sleep(0.5)
            
            # Click login button
            print("🔐 Logging in...")
            submit_button = self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
            submit_button.click()
            
            # Wait for login to complete and redirect
            print("⏳ Waiting for login to complete...")
            time.sleep(5)
            
            # Check current URL to verify login success
            current_url = self.driver.current_url
            print(f"   Current URL: {current_url}")
            
            # If still on login page, login might have failed
            if 'login.etimad.sa' in current_url.lower():
                print("   ⚠️  Still on login page - checking for errors...")
                time.sleep(3)  # Wait a bit more
                current_url = self.driver.current_url
                if 'login.etimad.sa' in current_url.lower():
                    print("   ❌ Login failed - check credentials or look for CAPTCHA")
                    return None
            
            # Navigate to tenders page to ensure we get all cookies
            print("📋 Navigating to tenders page...")
            self.driver.get("https://tenders.etimad.sa/Tender/AllSuppliersTenders")
            time.sleep(3)
            
            # Extract cookies from all domains
            print("🍪 Extracting cookies...")
            
            # Get cookies from current domain
            selenium_cookies = self.driver.get_cookies()
            
            # Convert to dict format (requests library format)
            self.cookies = {cookie['name']: cookie['value'] for cookie in selenium_cookies}
            
            # Filter important cookies
            important_cookies = ['MobileAuthCookie', '.AspNetCore.Antiforgery', 'TSPD_101', '__RequestVerificationToken']
            found_important = [c for c in important_cookies if c in self.cookies]
            
            if found_important:
                print(f"✅ Successfully retrieved {len(self.cookies)} cookies!")
                print(f"   Important cookies found: {', '.join(found_important)}")
                
                # Save cookies to file for backup
                self._save_cookies_to_file()
                
                return self.cookies
            else:
                print(f"⚠️  Retrieved {len(self.cookies)} cookies but missing important auth cookies")
                print(f"   Found cookies: {', '.join(list(self.cookies.keys())[:5])}...")
                return self.cookies if self.cookies else None
            
        except Exception as e:
            print(f"❌ Error during automation: {e}")
            import traceback
            traceback.print_exc()
            return {}
        
        finally:
            if self.driver:
                self.driver.quit()
                print("🔒 Browser closed")
    
    def _save_cookies_to_file(self, filepath='cookies_backup.json'):
        """Save cookies to JSON file for backup"""
        try:
            from datetime import datetime
            data = {
                'cookies': self.cookies,
                'timestamp': datetime.now().isoformat(),
                'method': 'browser_automation',
                'username': self.username if self.username else 'unknown'
            }
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            print(f"💾 Cookies saved to {filepath}")
        except Exception as e:
            print(f"⚠️  Could not save cookies: {e}")
    
    @staticmethod
    def load_cookies_from_file():
        """Load cookies from backup file"""
        try:
            if os.path.exists('cookies_backup.json'):
                with open('cookies_backup.json', 'r') as f:
                    cookies = json.load(f)
                print(f"📂 Loaded {len(cookies)} cookies from backup file")
                return cookies
        except Exception as e:
            print(f"⚠️  Could not load cookies from file: {e}")
        return {}


def get_etimad_cookies(username=None, password=None, use_automation=False):
    """
    Main function to get Etimad cookies
    
    Args:
        username: Etimad username
        password: Etimad password
        use_automation: If True, use browser automation
    
    Returns:
        dict: Cookies dictionary
    """
    if use_automation and username and password:
        automation = EtimadBrowserAutomation(username, password)
        return automation.login_and_get_cookies()
    else:
        # Try loading from backup file
        cookies = EtimadBrowserAutomation.load_cookies_from_file()
        if cookies:
            return cookies
        else:
            print("⚠️  No cookies available. Please enable browser automation or copy manually.")
            return {}


if __name__ == "__main__":
    # Test the automation
    import browser_config
    
    if browser_config.USE_BROWSER_AUTOMATION:
        cookies = get_etimad_cookies(
            username=browser_config.ETIMAD_USERNAME,
            password=browser_config.ETIMAD_PASSWORD,
            use_automation=True
        )
        
        print("\n" + "="*60)
        print("Cookies retrieved:")
        print("="*60)
        for key, value in cookies.items():
            print(f"{key}: {value[:50]}..." if len(value) > 50 else f"{key}: {value}")
    else:
        print("Browser automation is disabled in browser_config.py")
