"""
Script to inspect Etimad login page and save HTML for analysis
This will help us find the correct selectors for automation
"""

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

def inspect_etimad_login():
    print("🌐 Inspecting Etimad login page...")
    print("=" * 70)
    
    # Setup Chrome
    options = Options()
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--start-maximized')
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    
    try:
        # Navigate to Etimad
        print("\n📍 Step 1: Opening Etimad homepage...")
        driver.get("https://tenders.etimad.sa")
        time.sleep(3)
        
        # Save homepage HTML
        with open('etimad_homepage.html', 'w', encoding='utf-8') as f:
            f.write(driver.page_source)
        print("   ✅ Saved homepage HTML to etimad_homepage.html")
        
        # Try to find login button
        print("\n� Step 2: Looking for login button...")
        login_selectors = [
            (By.LINK_TEXT, "تسجيل الدخول"),
            (By.PARTIAL_LINK_TEXT, "تسجيل"),
            (By.LINK_TEXT, "Login"),
            (By.CSS_SELECTOR, "a[href*='login']"),
            (By.CSS_SELECTOR, "a[href*='Login']"),
            (By.CSS_SELECTOR, "button[class*='login']"),
            (By.XPATH, "//a[contains(text(), 'تسجيل')]"),
        ]
        
        login_button = None
        for by, selector in login_selectors:
            try:
                elements = driver.find_elements(by, selector)
                if elements:
                    login_button = elements[0]
                    print(f"   ✅ Found login element: {by} = '{selector}'")
                    print(f"      Text: '{login_button.text}'")
                    print(f"      Tag: {login_button.tag_name}")
                    if login_button.get_attribute('href'):
                        print(f"      URL: {login_button.get_attribute('href')}")
                    break
            except:
                continue
        
        if login_button:
            print("\n📍 Step 3: Clicking login button...")
            # Scroll to element and use JavaScript click to avoid overlay issues
            driver.execute_script("arguments[0].scrollIntoView(true);", login_button)
            time.sleep(1)
            try:
                login_button.click()
            except:
                print("   ⚠️  Normal click failed, trying JavaScript click...")
                driver.execute_script("arguments[0].click();", login_button)
            time.sleep(3)
            
            # Click "أعمال" (Business) tab
            print("\n📍 Step 3.5: Selecting Business (أعمال) login type...")
            try:
                business_tab = WebDriverWait(driver, 5).until(
                    EC.presence_of_element_located((By.LINK_TEXT, "أعمال"))
                )
                driver.execute_script("arguments[0].click();", business_tab)
                time.sleep(2)
                print("   ✅ Clicked Business tab")
            except:
                print("   ⚠️  Business tab not found - may already be selected")
            
            # Save login page HTML
            with open('etimad_login_page.html', 'w', encoding='utf-8') as f:
                f.write(driver.page_source)
            print("   ✅ Saved login page HTML to etimad_login_page.html")
            print(f"   Current URL: {driver.current_url}")
            
            # Try to find username/email field
            print("\n📍 Step 4: Looking for username/email field...")
            username_selectors = [
                (By.ID, "username"),
                (By.ID, "email"),
                (By.ID, "Username"),
                (By.ID, "Email"),
                (By.NAME, "username"),
                (By.NAME, "email"),
                (By.CSS_SELECTOR, "input[type='email']"),
                (By.CSS_SELECTOR, "input[type='text']"),
                (By.CSS_SELECTOR, "input[placeholder*='email']"),
                (By.CSS_SELECTOR, "input[placeholder*='اسم']"),
            ]
            
            username_field = None
            for by, selector in username_selectors:
                try:
                    elements = driver.find_elements(by, selector)
                    if elements:
                        username_field = elements[0]
                        print(f"   ✅ Found username field: {by} = '{selector}'")
                        print(f"      ID: {username_field.get_attribute('id')}")
                        print(f"      Name: {username_field.get_attribute('name')}")
                        print(f"      Type: {username_field.get_attribute('type')}")
                        print(f"      Placeholder: {username_field.get_attribute('placeholder')}")
                        break
                except:
                    continue
            
            # Try to find password field
            print("\n📍 Step 5: Looking for password field...")
            password_selectors = [
                (By.ID, "password"),
                (By.ID, "Password"),
                (By.NAME, "password"),
                (By.NAME, "Password"),
                (By.CSS_SELECTOR, "input[type='password']"),
            ]
            
            password_field = None
            for by, selector in password_selectors:
                try:
                    elements = driver.find_elements(by, selector)
                    if elements:
                        password_field = elements[0]
                        print(f"   ✅ Found password field: {by} = '{selector}'")
                        print(f"      ID: {password_field.get_attribute('id')}")
                        print(f"      Name: {password_field.get_attribute('name')}")
                        break
                except:
                    continue
            
            # Try to find submit button
            print("\n📍 Step 6: Looking for submit button...")
            submit_selectors = [
                (By.CSS_SELECTOR, "button[type='submit']"),
                (By.CSS_SELECTOR, "input[type='submit']"),
                (By.XPATH, "//button[contains(text(), 'دخول')]"),
                (By.XPATH, "//button[contains(text(), 'Login')]"),
                (By.XPATH, "//button[contains(text(), 'تسجيل')]"),
            ]
            
            submit_button = None
            for by, selector in submit_selectors:
                try:
                    elements = driver.find_elements(by, selector)
                    if elements:
                        submit_button = elements[0]
                        print(f"   ✅ Found submit button: {by} = '{selector}'")
                        print(f"      Text: '{submit_button.text}'")
                        print(f"      Type: {submit_button.get_attribute('type')}")
                        break
                except:
                    continue
            
            print("\n" + "=" * 70)
            print("📋 SUMMARY - Use these selectors in cookie_manager.py:")
            print("=" * 70)
            if username_field:
                print(f"✅ Username field: ID='{username_field.get_attribute('id')}' or NAME='{username_field.get_attribute('name')}'")
            else:
                print("❌ Username field not found - check etimad_login_page.html")
            
            if password_field:
                print(f"✅ Password field: ID='{password_field.get_attribute('id')}' or NAME='{password_field.get_attribute('name')}'")
            else:
                print("❌ Password field not found - check etimad_login_page.html")
            
            if submit_button:
                print(f"✅ Submit button found")
            else:
                print("❌ Submit button not found - check etimad_login_page.html")
            
            print("\n⏳ Browser will stay open for 30 seconds for manual inspection...")
            time.sleep(30)
        else:
            print("   ❌ Could not find login button")
            print("   📄 Check etimad_homepage.html for the page structure")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        print("\n🔒 Closing browser...")
        driver.quit()
        print("✅ Done! Check the saved HTML files for details.")

if __name__ == "__main__":
    inspect_etimad_login()
