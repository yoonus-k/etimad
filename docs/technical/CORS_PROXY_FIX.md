# 🔄 CORS Proxy Fix

## Problem

When the frontend tries to directly fetch URLs from `https://tenders.etimad.sa`, browsers block the request with a CORS (Cross-Origin Resource Sharing) error:

```
Access to fetch at 'https://tenders.etimad.sa/...' from origin 'http://localhost:5000' 
has been blocked by CORS policy: No 'Access-Control-Allow-Origin' header is present
```

## Solution

All requests to Etimad are now proxied through our backend server, which:
1. Accepts the request from the frontend
2. Makes the request to Etimad server-side (no CORS restrictions)
3. Returns the response to the frontend

## Backend Proxy Endpoint

**New endpoint added:** `/api/proxy/etimad`

### Usage

```javascript
// Instead of fetching directly:
fetch('https://tenders.etimad.sa/Tender/PrintConditionsTemplateRfp?STenderId=xyz')

// Use the proxy:
fetch('/api/proxy/etimad?url=' + encodeURIComponent('https://tenders.etimad.sa/Tender/PrintConditionsTemplateRfp?STenderId=xyz'))
```

### Features

✅ **Automatic cookie forwarding** - Uses saved cookies  
✅ **Proper headers** - Mimics browser requests  
✅ **Security** - Only allows Etimad domain URLs  
✅ **Error handling** - Proper timeout and error responses  
✅ **CORS headers** - Returns with Access-Control-Allow-Origin: *

## Frontend Helper Function

Added `proxyEtimadUrl()` helper:

```javascript
// Helper function to proxy Etimad URLs
function proxyEtimadUrl(etimadUrl) {
    return `/api/proxy/etimad?url=${encodeURIComponent(etimadUrl)}`;
}

// Usage example:
const url = proxyEtimadUrl('https://tenders.etimad.sa/Tender/PrintConditionsTemplateRfp?STenderId=xyz');
const response = await fetch(url);
```

## Examples

### Example 1: Fetch tender template

```javascript
const tenderId = 'ju2vKtqu4574AJrz6mQ%201Q==';
const etimadUrl = `https://tenders.etimad.sa/Tender/PrintConditionsTemplateRfp?STenderId=${tenderId}`;
const proxyUrl = proxyEtimadUrl(etimadUrl);

const response = await fetch(proxyUrl);
const html = await response.text();
```

### Example 2: Load in iframe

```html
<iframe id="tenderFrame"></iframe>

<script>
const tenderId = 'ju2vKtqu4574AJrz6mQ%201Q==';
const etimadUrl = `https://tenders.etimad.sa/Tender/PrintConditionsTemplateRfp?STenderId=${tenderId}`;
const proxyUrl = proxyEtimadUrl(etimadUrl);

document.getElementById('tenderFrame').src = proxyUrl;
</script>
```

## Technical Details

### Request Flow

```
Frontend (localhost:5000)
    ↓ fetch('/api/proxy/etimad?url=...')
Backend (Flask)
    ↓ requests.get('https://tenders.etimad.sa/...')
Etimad Server
    ↓ Response
Backend (Flask)
    ↓ Return with CORS headers
Frontend (receives response)
```

### Security

- **URL validation**: Only allows `https://tenders.etimad.sa` URLs
- **Timeout**: 30-second timeout to prevent hanging
- **Cookie control**: Only uses configured cookies
- **No bypass**: Cannot be used to proxy arbitrary websites

### Error Handling

| Error | Status Code | Description |
|-------|-------------|-------------|
| Missing URL | 400 | No `url` parameter provided |
| Invalid URL | 403 | URL is not from Etimad domain |
| Timeout | 504 | Request took longer than 30 seconds |
| Server Error | 500 | Other errors (network, parsing, etc.) |

## Files Modified

1. **`src/app.py`** - Added `/api/proxy/etimad` endpoint
2. **`static/script.js`** - Added `proxyEtimadUrl()` helper function

## Existing Endpoints

These endpoints already handle CORS properly:

- `/api/tenders` - Fetch tenders (uses backend scraper)
- `/api/tender/<id>/download` - Download attachments (backend fetch)
- `/api/tender/<id>/download-pdf` - Download PDF (backend HTML fetch + convert)
- `/api/tender/<id>/classification` - Check classification (backend scrape)

## Testing

Test the proxy endpoint:

```bash
# Test in terminal
curl "http://localhost:5000/api/proxy/etimad?url=https%3A%2F%2Ftenders.etimad.sa%2F"

# Test in browser console
fetch('/api/proxy/etimad?url=' + encodeURIComponent('https://tenders.etimad.sa/'))
    .then(r => r.text())
    .then(html => console.log(html.substring(0, 200)));
```

## Benefits

1. ✅ **No CORS errors** - All requests go through backend
2. ✅ **Consistent cookies** - Uses same authentication
3. ✅ **Better control** - Can add logging, caching, rate limiting
4. ✅ **Security** - Validates URLs before proxying
5. ✅ **Debugging** - Server-side logging of requests

---

**Added:** October 13, 2025  
**Issue:** CORS blocking frontend requests to Etimad  
**Solution:** Backend proxy endpoint  
**Status:** ✅ Fixed and ready to use
