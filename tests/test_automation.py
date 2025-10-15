"""
Test full browser automation for Etimad login and cookie extraction
"""

from cookie_manager import EtimadBrowserAutomation
import browser_config

def test_full_automation():
    print("=" * 70)
    print("🤖 TESTING FULL BROWSER AUTOMATION")
    print("=" * 70)
    
    # Check if automation is enabled
    if not browser_config.USE_BROWSER_AUTOMATION:
        print("\n⚠️  Browser automation is DISABLED in browser_config.py")
        print("   Set USE_BROWSER_AUTOMATION = True to enable it")
        return
    
    # Check credentials
    if not browser_config.ETIMAD_USERNAME or not browser_config.ETIMAD_PASSWORD:
        print("\n❌ ERROR: Missing credentials!")
        print("   Please set ETIMAD_USERNAME and ETIMAD_PASSWORD in browser_config.py")
        return
    
    print(f"\n📋 Configuration:")
    print(f"   Username: {browser_config.ETIMAD_USERNAME}")
    print(f"   Password: {'*' * len(browser_config.ETIMAD_PASSWORD)}")
    print(f"   Headless: {browser_config.HEADLESS_BROWSER}")
    
    print("\n" + "=" * 70)
    print("Starting automation...")
    print("=" * 70 + "\n")
    
    # Create automation instance
    automation = EtimadBrowserAutomation(
        username=browser_config.ETIMAD_USERNAME,
        password=browser_config.ETIMAD_PASSWORD,
        headless=browser_config.HEADLESS_BROWSER
    )
    
    # Run login and get cookies
    cookies = automation.login_and_get_cookies()
    
    if cookies:
        print("\n" + "=" * 70)
        print("✅ SUCCESS!")
        print("=" * 70)
        print(f"   Retrieved {len(cookies)} cookies")
        print(f"   Cookie names: {', '.join(list(cookies.keys())[:10])}")
        
        # Test if cookies work with API
        print("\n🧪 Testing cookies with Etimad API...")
        import requests
        
        try:
            url = "https://tenders.etimad.sa/Tender/AllSupplierTendersAsync"
            params = {
                'PageSize': 1,
                'PageNumber': 1,
                'Sort': 'OffersDueDate'
            }
            
            response = requests.get(url, cookies=cookies, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                total = data.get('total', 0)
                print(f"   ✅ API Test Passed! {total} tenders available")
                print("\n🎉 AUTOMATION IS FULLY WORKING!")
                print("   You can now enable it in your app")
            else:
                print(f"   ⚠️  API returned status {response.status_code}")
                print("   Cookies may not be fully valid yet")
        except Exception as e:
            print(f"   ❌ API test failed: {e}")
    else:
        print("\n" + "=" * 70)
        print("❌ AUTOMATION FAILED")
        print("=" * 70)
        print("\n📋 Troubleshooting:")
        print("   1. Check your username and password in browser_config.py")
        print("   2. Make sure your Etimad account is active")
        print("   3. Check if there's a CAPTCHA or 2FA requirement")
        print("   4. Try running with HEADLESS_BROWSER = False to see what's happening")
        print("   5. Check if Etimad website structure has changed")

if __name__ == "__main__":
    test_full_automation()
