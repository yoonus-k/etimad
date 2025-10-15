# Cookie Management Guide for Etimad Tenders App

## 🍪 Three Methods to Handle Cookies

### **Method 1: Browser Automation (Recommended)** ⭐

Automatically logs into Etimad and gets fresh cookies.

#### Setup:

1. **Install Selenium:**
```bash
pip install selenium
```

2. **Install Chrome Driver:**
   - Download from: https://chromedriver.chromium.org/
   - Or use: `pip install webdriver-manager`
   - Add to PATH

3. **Configure `browser_config.py`:**
```python
USE_BROWSER_AUTOMATION = True
ETIMAD_USERNAME = "your_email@example.com"
ETIMAD_PASSWORD = "your_password"
HEADLESS_BROWSER = False  # True to hide browser
```

4. **Run:**
The app will automatically login and get cookies when started!

#### Pros:
- ✅ Fully automated
- ✅ Always fresh cookies
- ✅ No manual copying

#### Cons:
- ❌ Requires Selenium setup
- ❌ Needs valid credentials
- ❌ Slower (opens browser)

---

### **Method 2: Cookie File Cache** 📁

Save cookies once, reuse until they expire.

#### Setup:

1. **First time - Get cookies manually:**
   - Login to Etimad in browser
   - Copy cookies from DevTools → Network tab
   - Paste into `config.py`
   - Run app once

2. **Cookies are auto-saved** to `cookies_backup.json`

3. **Next time:**
   - App automatically loads from `cookies_backup.json`
   - No need to copy again!

#### Usage:
```python
# In app.py, it automatically tries to load from file:
from cookie_manager import EtimadBrowserAutomation
cookies = EtimadBrowserAutomation.load_cookies_from_file()
```

#### Pros:
- ✅ Fast - no browser needed
- ✅ No Selenium required
- ✅ Reusable until expiry

#### Cons:
- ❌ Manual copy first time
- ❌ Expires after some time
- ❌ Need to refresh when expired

---

### **Method 3: Manual Config (Current)** 📋

Copy-paste cookies each time.

#### Setup:

1. Login to Etimad in browser
2. Open DevTools (F12) → Network tab
3. Find API request
4. Copy cookies from Request Headers
5. Paste into `config.py` → `COOKIES = {...}`

#### Pros:
- ✅ Simple
- ✅ No dependencies
- ✅ Works immediately

#### Cons:
- ❌ Manual process
- ❌ Time-consuming
- ❌ Needs repetition

---

## 🚀 Recommended Workflow

### **For Development:**
Use **Method 2** (Cookie File Cache):
1. Copy cookies manually once
2. App saves to `cookies_backup.json`
3. Reuse for days/weeks

### **For Production/Long-term:**
Use **Method 1** (Browser Automation):
1. Set credentials in `browser_config.py`
2. App auto-logs in when needed
3. Never worry about cookies again

### **For Quick Testing:**
Use **Method 3** (Manual):
- Just paste and go

---

## 📝 Cookie Expiration

Etimad cookies typically expire after:
- **Session cookies**: When browser closes
- **Auth cookies**: 1-24 hours (varies)
- **Remember-me cookies**: Days/weeks

### Signs cookies expired:
- API returns 302 redirect
- "Authentication required" errors
- Empty responses

### Solutions:
1. **Automated**: Browser automation gets fresh cookies
2. **Manual**: Copy new cookies from browser
3. **File cache**: Delete `cookies_backup.json` and get new ones

---

## 🔒 Security Best Practices

### **DO:**
- ✅ Use environment variables for credentials
- ✅ Add `cookies_backup.json` to `.gitignore`
- ✅ Add `browser_config.py` to `.gitignore`
- ✅ Use strong passwords
- ✅ Rotate cookies regularly

### **DON'T:**
- ❌ Commit credentials to git
- ❌ Share cookie files
- ❌ Store passwords in plain text (use keyring/env vars)
- ❌ Reuse old expired cookies

### **Example `.gitignore`:**
```
cookies_backup.json
browser_config.py
.env
__pycache__/
*.pyc
```

### **Example with environment variables:**
```python
# browser_config.py
import os
from dotenv import load_dotenv

load_dotenv()

ETIMAD_USERNAME = os.getenv('ETIMAD_USERNAME')
ETIMAD_PASSWORD = os.getenv('ETIMAD_PASSWORD')
```

Then create `.env` file:
```
ETIMAD_USERNAME=your_email@example.com
ETIMAD_PASSWORD=your_secure_password
```

---

## 🛠️ Troubleshooting

### Browser automation not working?

1. **Check Chrome Driver:**
```bash
chromedriver --version
```

2. **Update Selenium:**
```bash
pip install --upgrade selenium
```

3. **Check login selectors:**
   - Open `cookie_manager.py`
   - Update CSS selectors for Etimad's login form
   - Inspect Etimad website to get correct IDs/classes

### Cookies not loading from file?

1. Check if `cookies_backup.json` exists
2. Check file permissions
3. Verify JSON format
4. Try deleting and regenerating

### API still failing?

1. Verify cookies are recent (< 24 hours)
2. Check if you're logged in on browser
3. Try manual copy-paste to confirm cookies work
4. Check for Etimad website changes

---

## 📊 Performance Comparison

| Method | Setup Time | Runtime | Maintenance | Best For |
|--------|-----------|---------|-------------|----------|
| Browser Auto | 30 min | ~10 sec | None | Production |
| File Cache | 5 min | <1 sec | Weekly | Development |
| Manual | 2 min | <1 sec | Daily | Testing |

---

## 💡 Tips

1. **Start with Method 3** (Manual) to test
2. **Move to Method 2** (File Cache) for daily work
3. **Upgrade to Method 1** (Browser Auto) for production

4. **Monitor cookie expiry** - add logging to see when they fail

5. **Combine methods**:
   - Try file cache first (fast)
   - Fall back to browser automation if expired
   - Alert if both fail

---

## 📞 Support

If cookies keep failing:
1. Check Etimad's authentication system hasn't changed
2. Verify your account is active
3. Try logging in manually first
4. Check for CAPTCHA or 2FA requirements
