"""
Debug script to check browser cookies
"""

print("=" * 70)
print("🔍 BROWSER COOKIE DEBUG")
print("=" * 70)

# Test 1: Check if browser-cookie3 works
print("\n1️⃣ Testing browser-cookie3 library...")
try:
    import browser_cookie3
    print("   ✅ browser-cookie3 installed")
except ImportError as e:
    print(f"   ❌ browser-cookie3 not installed: {e}")
    print("   Run: pip install browser-cookie3")
    exit(1)

# Test 2: Try to get Chrome cookies
print("\n2️⃣ Trying to read Chrome cookies...")
try:
    cj = browser_cookie3.chrome(domain_name='etimad.sa')
    cookies = list(cj)
    if cookies:
        print(f"   ✅ Found {len(cookies)} cookies from Chrome")
        print(f"   Cookie names: {[c.name for c in cookies[:5]]}")
    else:
        print("   ⚠️  Chrome found but NO cookies for etimad.sa")
        print("   Are you sure you're logged in to Etimad in Chrome?")
except Exception as e:
    print(f"   ❌ Chrome error: {e}")

# Test 3: Try Edge
print("\n3️⃣ Trying to read Edge cookies...")
try:
    cj = browser_cookie3.edge(domain_name='etimad.sa')
    cookies = list(cj)
    if cookies:
        print(f"   ✅ Found {len(cookies)} cookies from Edge")
        print(f"   Cookie names: {[c.name for c in cookies[:5]]}")
    else:
        print("   ⚠️  Edge found but NO cookies for etimad.sa")
except Exception as e:
    print(f"   ❌ Edge error: {e}")

# Test 4: Try Firefox
print("\n4️⃣ Trying to read Firefox cookies...")
try:
    cj = browser_cookie3.firefox(domain_name='etimad.sa')
    cookies = list(cj)
    if cookies:
        print(f"   ✅ Found {len(cookies)} cookies from Firefox")
        print(f"   Cookie names: {[c.name for c in cookies[:5]]}")
    else:
        print("   ⚠️  Firefox found but NO cookies for etimad.sa")
except Exception as e:
    print(f"   ❌ Firefox error: {e}")

# Test 5: Check which browsers are open
print("\n5️⃣ Checking browser processes...")
import subprocess
try:
    result = subprocess.run(['tasklist'], capture_output=True, text=True)
    output = result.stdout.lower()
    
    browsers = {
        'Chrome': 'chrome.exe' in output,
        'Edge': 'msedge.exe' in output,
        'Firefox': 'firefox.exe' in output
    }
    
    for browser, running in browsers.items():
        status = "✅ Running" if running else "❌ Not running"
        print(f"   {browser}: {status}")
except Exception as e:
    print(f"   ⚠️  Could not check: {e}")

print("\n" + "=" * 70)
print("📋 RECOMMENDATIONS:")
print("=" * 70)

print("""
If NO cookies were found:

Option 1: Use DevTools (Manual - Always Works)
   1. Login to Etimad in Chrome
   2. Press F12 (DevTools)
   3. Go to: Application → Cookies → https://tenders.etimad.sa
   4. Copy these cookies:
      - MobileAuthCookie
      - .AspNetCore.Antiforgery
      - TSPD_101
   5. I'll help you paste them in the app

Option 2: Try closing ALL Chrome windows
   1. Close ALL Chrome windows completely
   2. Login to Etimad in Chrome
   3. Try the button again
   4. (browser-cookie3 might work better with fresh session)

Option 3: Alternative - Manual Cookie Paste
   We can add a form in the app where you paste cookies directly
   
Which option would you like to try?
""")
