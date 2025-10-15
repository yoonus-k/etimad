"""
Quick test to extract cookies from browser
Make sure you're logged into Etimad in Chrome/Edge first!
"""

from browser_cookie_extractor import extract_cookies_from_all_browsers, test_cookies, save_cookies_to_file

print("=" * 70)
print("🍪 TESTING BROWSER COOKIE EXTRACTION")
print("=" * 70)
print("\n⚠️  BEFORE RUNNING THIS:")
print("   1. Open Chrome or Edge")
print("   2. Go to https://tenders.etimad.sa")
print("   3. Login to your account")
print("   4. Keep the browser open")
print("\n" + "=" * 70)

input("\n✅ Press ENTER when you're logged in and ready...")

print("\n🔍 Extracting cookies from browser...\n")

result = extract_cookies_from_all_browsers()

if result:
    print("\n" + "=" * 70)
    print("✅ SUCCESS!")
    print("=" * 70)
    print(f"   Browser: {result['browser'].upper()}")
    print(f"   Cookies found: {len(result['cookies'])}")
    print(f"   Timestamp: {result['timestamp']}")
    
    # Test the cookies
    if test_cookies(result['cookies']):
        print("\n✅ Cookies are valid and working!")
        
        # Save to file
        save_cookies_to_file(result)
        print("\n✅ Cookies saved to cookies_backup.json")
        print("\n🎉 YOU'RE ALL SET!")
        print("   You can now use the 'Connect to Browser' button in the app")
    else:
        print("\n⚠️  Cookies extracted but may not be valid")
        print("   Try logging out and back in on the browser")
else:
    print("\n" + "=" * 70)
    print("❌ FAILED TO EXTRACT COOKIES")
    print("=" * 70)
    print("\n📋 Troubleshooting:")
    print("   1. Make sure you're logged in to Etimad")
    print("   2. Try using Chrome or Edge browser")
    print("   3. Close and reopen the browser")
    print("   4. Make sure the browser is not in Incognito/Private mode")
    print("   5. Try clearing browser cache and logging in again")

print("\n" + "=" * 70)
