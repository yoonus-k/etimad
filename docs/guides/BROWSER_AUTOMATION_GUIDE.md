# 🤖 Browser Automation Setup Guide

## Quick Start

### Step 1: Install Dependencies

Already done! ✅ You have:
- `selenium`
- `webdriver-manager` (auto-manages ChromeDriver)
- `browser-cookie3` (for reading cookies from browser)

### Step 2: Configure Credentials

Edit `browser_config.py`:

```python
USE_BROWSER_AUTOMATION = True  # Enable automation

ETIMAD_USERNAME = "your_username_or_email"  # Your Etimad login
ETIMAD_PASSWORD = "your_password_here"       # Your password

HEADLESS_BROWSER = False  # Set True to hide browser
```

### Step 3: Test Automation

Run the test script:

```bash
python test_automation.py
```

This will:
1. ✅ Open Chrome browser
2. ✅ Navigate to Etimad
3. ✅ Click login button
4. ✅ Enter your credentials
5. ✅ Login automatically
6. ✅ Extract cookies
7. ✅ Test cookies with API
8. ✅ Save cookies to `cookies_backup.json`

### Step 4: Use in Your App

Once automation works, just run:

```bash
python app.py
```

The app will **automatically**:
- Login to Etimad when started
- Get fresh cookies
- Use them for API calls
- No manual copying needed! 🎉

---

## How It Works

### The Automation Flow

```
1. Browser Opens → https://tenders.etimad.sa
2. Finds "تسجيل الدخول" button
3. Clicks it → redirects to login.etimad.sa
4. Enters username (ID='Username')
5. Enters password (ID='Password')
6. Clicks submit button
7. Waits for redirect back to tenders.etimad.sa
8. Extracts all cookies
9. Saves to cookies_backup.json
10. Returns cookies to app
```

### Selectors Used (Found via inspection)

- **Login Button**: `link text = "تسجيل الدخول"`
- **Login URL**: `https://login.etimad.sa/Account/PrivateSectorLogin`
- **Username Field**: `ID = "Username"`
- **Password Field**: `ID = "Password"`
- **Submit Button**: `button[type='submit']`

---

## Troubleshooting

### Problem: "Login failed - check credentials"

**Solutions:**
1. Verify username/password in `browser_config.py`
2. Try logging in manually first in Chrome
3. Check for CAPTCHA or 2FA
4. Set `HEADLESS_BROWSER = False` to watch what happens

### Problem: "Missing important auth cookies"

**Solutions:**
1. Wait longer after login (increase `time.sleep(5)` to `time.sleep(10)`)
2. Check if you need to accept terms/conditions after login
3. Navigate to tenders page manually to see what happens

### Problem: "ChromeDriver version mismatch"

**Solution:**
```bash
pip install --upgrade webdriver-manager
```
The webdriver-manager auto-downloads the correct version.

### Problem: "Element not clickable"

**Solution:**
Already handled! We use JavaScript click:
```python
driver.execute_script("arguments[0].click();", element)
```

---

## Advanced Configuration

### Using Environment Variables (Recommended for Production)

1. Create `.env` file:
```env
ETIMAD_USERNAME=your_username
ETIMAD_PASSWORD=your_password
```

2. Update `browser_config.py`:
```python
import os
from dotenv import load_dotenv

load_dotenv()

ETIMAD_USERNAME = os.getenv('ETIMAD_USERNAME')
ETIMAD_PASSWORD = os.getenv('ETIMAD_PASSWORD')
```

3. Add to `.gitignore`:
```
.env
cookies_backup.json
browser_config.py
```

### Running Headless (No Browser Window)

```python
HEADLESS_BROWSER = True
```

Good for:
- Production servers
- Background tasks
- Scheduled jobs

Bad for:
- Debugging
- Initial setup
- Seeing what's happening

### Custom Browser Options

Edit `cookie_manager.py` → `_setup_browser()`:

```python
options.add_argument('--window-size=1920,1080')
options.add_argument('--disable-gpu')
options.add_argument('--disable-notifications')
options.add_argument(f'user-data-dir=/path/to/profile')  # Use browser profile
```

---

## Files Created

| File | Purpose |
|------|---------|
| `cookie_manager.py` | Main automation class |
| `browser_config.py` | Configuration settings |
| `inspect_login_page.py` | Tool to find selectors |
| `test_automation.py` | Test automation end-to-end |
| `browser_cookie_extractor.py` | Alternative: read from browser |
| `cookies_backup.json` | Saved cookies (auto-generated) |

---

## Comparison: Automation vs Browser Reading

### Method 1: Full Automation (Current)
✅ Completely hands-off
✅ Always fresh login
✅ Works on servers
❌ Slower (~10 seconds)
❌ Needs credentials

### Method 2: Browser Cookie Reading
✅ Very fast (<1 second)
✅ No credentials needed
✅ Uses your existing session
❌ Requires you to login first
❌ Only works on your PC

**Recommendation**: Use Automation for production, Browser Reading for development

---

## Security Best Practices

### ✅ DO:
- Use environment variables
- Add sensitive files to `.gitignore`
- Rotate passwords regularly
- Use strong passwords
- Enable 2FA if available

### ❌ DON'T:
- Commit credentials to git
- Share `browser_config.py`
- Share `cookies_backup.json`
- Use same password everywhere
- Store passwords in plain text

---

## Next Steps

1. ✅ Test automation: `python test_automation.py`
2. ✅ If successful, enable in `browser_config.py`
3. ✅ Run app: `python app.py`
4. ✅ App will auto-login and get cookies
5. 🎉 Enjoy automated tender fetching!

---

## Support

If automation fails:

1. Check `inspect_login_page.py` output
2. Look at saved HTML files:
   - `etimad_homepage.html`
   - `etimad_login_page.html`
3. Watch browser with `HEADLESS_BROWSER = False`
4. Check for Etimad website changes
5. Verify credentials work manually first

---

**Happy Automating! 🤖✨**
