"""
Extract cookies from browser (Chrome/Edge/Firefox)
Reads cookies from your logged-in browser session
"""

import browser_cookie3
import json
from datetime import datetime

def extract_cookies_from_browser(browser_name='chrome', domain='etimad.sa'):
    """
    Extract cookies from specified browser for Etimad domain
    
    Args:
        browser_name: 'chrome', 'edge', 'firefox', 'chromium'
        domain: Domain to extract cookies for
    
    Returns:
        dict: Cookies in format ready for requests library
    """
    cookies = {}
    
    try:
        print(f"🔍 Looking for cookies in {browser_name.upper()}...")
        
        # Get cookie jar from browser
        if browser_name.lower() == 'chrome':
            cj = browser_cookie3.chrome(domain_name=domain)
        elif browser_name.lower() == 'edge':
            cj = browser_cookie3.edge(domain_name=domain)
        elif browser_name.lower() == 'firefox':
            cj = browser_cookie3.firefox(domain_name=domain)
        elif browser_name.lower() == 'chromium':
            cj = browser_cookie3.chromium(domain_name=domain)
        else:
            raise ValueError(f"Browser '{browser_name}' not supported")
        
        # Convert cookie jar to dictionary
        for cookie in cj:
            cookies[cookie.name] = cookie.value
        
        if cookies:
            print(f"✅ Found {len(cookies)} cookies from {browser_name.upper()}")
            print(f"   Cookie names: {', '.join(list(cookies.keys())[:5])}...")
            return cookies
        else:
            print(f"⚠️  No cookies found in {browser_name.upper()} for {domain}")
            return None
            
    except Exception as e:
        print(f"❌ Error reading cookies from {browser_name}: {e}")
        return None

def extract_cookies_from_all_browsers(domain='etimad.sa'):
    """
    Try to extract cookies from all supported browsers
    Returns cookies from the first browser that has them
    """
    browsers = ['chrome', 'edge', 'firefox', 'chromium']
    
    print("🌐 Searching for Etimad cookies in all browsers...")
    print("=" * 60)
    
    for browser in browsers:
        cookies = extract_cookies_from_browser(browser, domain)
        if cookies:
            return {
                'cookies': cookies,
                'browser': browser,
                'timestamp': datetime.now().isoformat()
            }
    
    print("\n❌ No cookies found in any browser!")
    print("   Make sure you're logged in to Etimad in your browser.")
    return None

def save_cookies_to_file(cookies_data, filepath='cookies_backup.json'):
    """Save extracted cookies to file"""
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(cookies_data, f, indent=2, ensure_ascii=False)
        print(f"\n💾 Cookies saved to {filepath}")
        return True
    except Exception as e:
        print(f"❌ Error saving cookies: {e}")
        return False

def load_cookies_from_file(filepath='cookies_backup.json'):
    """Load cookies from file"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        print(f"✅ Cookies loaded from {filepath}")
        return data.get('cookies', {})
    except FileNotFoundError:
        print(f"⚠️  Cookie file {filepath} not found")
        return None
    except Exception as e:
        print(f"❌ Error loading cookies: {e}")
        return None

def test_cookies(cookies):
    """Test if cookies work with Etimad API"""
    import requests
    
    if not cookies:
        print("❌ No cookies to test")
        return False
    
    try:
        print("\n🧪 Testing cookies with Etimad API...")
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
            print(f"✅ Cookies work! Found {total} tenders available")
            return True
        else:
            print(f"⚠️  API returned status {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Cookie test failed: {e}")
        return False

if __name__ == "__main__":
    # Test the extractor
    print("🍪 Browser Cookie Extractor for Etimad\n")
    
    # Extract cookies
    result = extract_cookies_from_all_browsers()
    
    if result:
        cookies = result['cookies']
        print(f"\n✅ Extracted from: {result['browser'].upper()}")
        print(f"   Timestamp: {result['timestamp']}")
        
        # Test cookies
        if test_cookies(cookies):
            # Save to file
            save_cookies_to_file(result)
            print("\n✅ SUCCESS! Cookies are ready to use.")
        else:
            print("\n⚠️  Cookies extracted but may not be valid.")
            print("   Make sure you're logged in to Etimad in your browser.")
    else:
        print("\n❌ Failed to extract cookies.")
        print("\n📋 Troubleshooting:")
        print("   1. Open Chrome/Edge and go to https://tenders.etimad.sa")
        print("   2. Log in to your account")
        print("   3. Keep the browser open")
        print("   4. Run this script again")
