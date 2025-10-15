# ✅ CORS Issue Fixed!

## Problem Solved

The app was giving CORS errors when trying to fetch URLs like:
```
https://tenders.etimad.sa/Tender/PrintConditionsTemplateRfp?STenderId=ju2vKtqu4574AJrz6mQ%201Q==
```

**Error was:**
```
Access to fetch at 'https://tenders.etimad.sa/...' from origin 'http://localhost:5000' 
has been blocked by CORS policy
```

## Solution Implemented

✅ **Added backend proxy endpoint** - `/api/proxy/etimad`  
✅ **Added frontend helper function** - `proxyEtimadUrl()`  
✅ **All Etimad requests now go through backend** - No more CORS errors!

## How to Use

### From JavaScript

```javascript
// OLD WAY (causes CORS error):
fetch('https://tenders.etimad.sa/Tender/PrintConditionsTemplateRfp?STenderId=xyz')

// NEW WAY (works!):
const url = proxyEtimadUrl('https://tenders.etimad.sa/Tender/PrintConditionsTemplateRfp?STenderId=xyz');
fetch(url)
```

### API Endpoint

```
GET /api/proxy/etimad?url=<encoded_etimad_url>
```

**Example:**
```
http://localhost:5000/api/proxy/etimad?url=https%3A%2F%2Ftenders.etimad.sa%2FTender%2FPrintConditionsTemplateRfp%3FSTenderId%3Dju2vKtqu4574AJrz6mQ%25201Q%3D%3D
```

## What Changed

### Backend (`src/app.py`)
Added new endpoint that:
- Accepts Etimad URLs
- Validates they're from Etimad domain (security)
- Fetches server-side with proper cookies
- Returns response with CORS headers
- Handles timeouts and errors

### Frontend (`static/script.js`)
Added helper function:
```javascript
function proxyEtimadUrl(etimadUrl) {
    return `/api/proxy/etimad?url=${encodeURIComponent(etimadUrl)}`;
}
```

## Benefits

1. ✅ **No CORS errors** - Backend handles all Etimad requests
2. ✅ **Automatic cookies** - Uses saved authentication cookies
3. ✅ **Secure** - Only allows Etimad URLs
4. ✅ **Better logging** - See requests in backend console
5. ✅ **Easy to use** - Simple helper function

## Testing

**Restart the server:**
```bash
# Stop current server (Ctrl+C)
python run.py
```

**Test the proxy:**
```javascript
// In browser console:
fetch('/api/proxy/etimad?url=' + encodeURIComponent('https://tenders.etimad.sa/'))
    .then(r => r.text())
    .then(html => console.log('Success!', html.length, 'bytes'));
```

## Documentation

Full technical details: [CORS_PROXY_FIX.md](./docs/technical/CORS_PROXY_FIX.md)

## Status

🎉 **CORS issue is now fixed!**

---

**Fixed:** October 13, 2025  
**Files Modified:** `src/app.py`, `static/script.js`  
**New Endpoint:** `/api/proxy/etimad`  
**Status:** ✅ Ready to use
