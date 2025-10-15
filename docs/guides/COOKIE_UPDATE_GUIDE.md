# 🔄 Cookie Update Workflow

## Overview
The application now supports automatic updating of `config.py` with fresh cookies from your browser!

---

## 🎯 How It Works

### **1. Extract Cookies (Browser Extension - Recommended)**
- Install the browser extension from `cookie_extension/` folder
- Login to https://tenders.etimad.sa
- Click extension icon → Extract → Copy
- **Result:** Cookies in clipboard, formatted as Python dict

### **2. Update Application**
- Click "🍪 تحديث الكوكيز" button in the web app
- Paste cookies from clipboard
- Click "💾 حفظ"
- **Result:** 
  - ✅ `config.py` file updated automatically
  - ✅ `cookies_backup.json` updated
  - ✅ App reloaded with new cookies
  - ✅ Ready to fetch tenders!

### **3. Verify**
- Connection status shows: "✅ متصل - X منافسة"
- Click "جلب المنافسات" to fetch tenders
- Done! 🎉

---

## 📋 Three Ways to Get Cookies

### **Method 1: Browser Extension (⭐ Recommended)**
**Pros:**
- ✅ Easiest and fastest
- ✅ One-click extraction
- ✅ Perfect formatting
- ✅ No manual copying

**Steps:**
1. Install extension: See `cookie_extension/INSTALL.md`
2. Login to Etimad
3. Click extension → Extract → Copy
4. Paste in app → Save

**Time:** ~30 seconds

---

### **Method 2: Console Script (⚡ Quick)**
**Pros:**
- ✅ No extension needed
- ✅ Fast one-liner
- ✅ Auto-copies to clipboard

**Steps:**
1. Login to https://tenders.etimad.sa
2. Press F12 → Console tab
3. Paste this code:
```javascript
const c=['login.etimad.ssk4','MobileAuthCookie','TS00000000076','TS01369bcc','TS0145fac2','TS0147caf9','TS0147caf9030','TS0f286a6e029','TS0f286a6e077','TS1c26927f027','TSPD_101','TSPD_101_DID','url','X-CSRF-TOKEN-SSK3','.AspNetCore.Antiforgery','_ga','_gid','ADRUM','Dammam','Identity.TwoFactorUserId','idsrv.session','langcookie','language','SameSite'];copy(document.cookie.split('; ').filter(x=>c.some(n=>x.startsWith(n+'='))).join('; '));
```
4. Paste in app → Save

**Time:** ~1 minute

---

### **Method 3: Manual DevTools (🔧 Advanced)**
**Pros:**
- ✅ Works in any browser
- ✅ No code needed
- ✅ Full control

**Steps:**
1. Login to https://tenders.etimad.sa
2. Press F12 → Application → Cookies
3. Copy cookies manually from:
   - `https://tenders.etimad.sa`
   - `https://login.etimad.sa`
4. Format as: `name=value; name2=value2; ...`
5. Paste in app → Save

**Time:** ~3-5 minutes

---

## 🔄 What Happens Behind the Scenes

When you click "💾 حفظ":

```
1. Parse Cookies
   ↓
2. Test with Etimad API
   ↓ (Success?)
3. Save to cookies_backup.json
   ↓
4. Update config.py file ⭐ NEW!
   ↓
5. Reload app configuration
   ↓
6. ✅ Ready!
```

---

## 📝 Updated Files

After clicking Save:

### **1. `config.py`**
```python
COOKIES = {
    '.AspNetCore.Antiforgery.uI0FgwZS2KM': 'CfDJ8...',
    'MobileAuthCookie': 'CfDJ8...',
    'TSPD_101': '088c96e...',
    # ... all your cookies
}
```

### **2. `cookies_backup.json`**
```json
{
  "cookies": { ... },
  "timestamp": "2025-10-13T09:45:00",
  "method": "manual_paste"
}
```

---

## 🔒 Security Notes

⚠️ **Important:**
- Cookies give FULL ACCESS to your Etimad account
- Never share `config.py` or `cookies_backup.json`
- Add both to `.gitignore`:
  ```gitignore
  config.py
  cookies_backup.json
  ```

---

## ⏰ When to Update Cookies?

Update cookies when you see:
- ❌ "Unauthorized" errors
- ❌ "Invalid cookies" messages
- ❌ API returning empty results
- ❌ After logging out/in to Etimad
- 📅 Every few days (cookies expire)

---

## 🐛 Troubleshooting

### **"لم يتم العثور على كوكيز صالحة"**
**Solution:** Make sure you're copying the correct format:
```
name=value; name2=value2; name3=value3
```

### **"الكوكيز غير صالحة"**
**Solution:**
- Make sure you're logged into Etimad
- Extract fresh cookies
- Don't modify the cookies after copying

### **"Failed to update config.py"**
**Solution:**
- Check file permissions
- Make sure `config.py` exists
- Close any text editors that have `config.py` open

### **Extension not extracting cookies**
**Solution:**
- Make sure extension is installed and enabled
- Reload the Etimad page
- Check extension popup shows cookies
- See `cookie_extension/README.md` for help

---

## 🎯 Quick Reference

| Action | Button | Result |
|--------|--------|--------|
| Extract cookies | Browser extension | Cookies in clipboard |
| Update app | 🍪 تحديث الكوكيز | Opens modal |
| Save cookies | 💾 حفظ | Updates config.py + JSON |
| Fetch tenders | جلب المنافسات | Gets tenders from API |

---

## 📚 Related Files

- `app.py` - Flask app with cookie update endpoint
- `config.py` - Configuration (updated automatically)
- `cookies_backup.json` - Cookie backup (updated automatically)
- `cookie_extension/` - Browser extension for easy extraction
- `templates/index.html` - Web interface
- `static/script.js` - Frontend logic

---

## ✅ Success Indicators

After updating cookies successfully:

1. ✅ Alert shows: "تم حفظ X كوكي"
2. ✅ Status badge: "✅ متصل - X منافسة"
3. ✅ `config.py` file updated
4. ✅ Console shows: "✅ config.py updated with X cookies"
5. ✅ Ready to fetch tenders!

---

**🎉 You can now update cookies without manually editing config.py!**

**See `cookie_extension/INSTALL.md` for extension installation guide.**
