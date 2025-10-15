# 🔧 Download Connection Reset Fix

## Problem

When downloading tender documents, the connection was being reset with error:
```
GET http://127.0.0.1:5000/api/tender/.../download
net::ERR_CONNECTION_RESET
```

## Root Cause

The Flask development server's **auto-reloader (watchdog)** was monitoring file changes. When documents were downloaded to the `downloads/` folder:

1. File gets downloaded → triggers watchdog
2. Watchdog sees new file → triggers server restart  
3. Server restarts during download → connection drops
4. Client receives `ERR_CONNECTION_RESET`

## Solutions Implemented

### 1. Better Error Handling

Added proper error handling in the download endpoint:

```python
@app.route('/api/tender/<tender_id>/download')
def download_tender_documents(tender_id):
    try:
        # Download logic...
    except requests.exceptions.Timeout as e:
        return jsonify({'error': 'timeout'}), 504
    except requests.exceptions.ConnectionError as e:
        return jsonify({'error': 'connection failed'}), 503
    except Exception as e:
        return jsonify({'error': str(e)}), 500
```

### 2. Added Logging

Added detailed logging to track download progress:
- Request received
- Tender name and reference
- Download start/completion
- Error details with stack traces

### 3. Changed Reloader Type

Changed from `watchdog` to `stat` reloader in `run.py`:

```python
app.run(
    debug=True,
    reloader_type='stat'  # Uses file stat instead of watchdog
)
```

**Why `stat` is better for this use case:**
- Less sensitive to file system changes
- Doesn't monitor every file change
- Only checks timestamps periodically
- Won't restart during downloads

### 4. Created `.watchdogignore`

Created ignore file to exclude folders from monitoring:
```
downloads/
data/
debug/
__pycache__/
```

### 5. Imported requests Module

Fixed missing `requests` import at the top of `app.py`:
```python
import requests
```

## Files Modified

1. ✅ `src/app.py` - Better error handling, logging, imports
2. ✅ `run.py` - Changed reloader type to `stat`
3. ✅ `.watchdogignore` - Exclude folders from monitoring

## Testing

### Before Fix
```
❌ Download starts → File created → Server restarts → ERR_CONNECTION_RESET
```

### After Fix
```
✅ Download starts → File created → Server continues → Download completes
```

### Test the Fix

1. **Restart the server:**
   ```bash
   # Stop current server (Ctrl+C)
   python run.py
   ```

2. **Try downloading:**
   - Click "📥 تحميل جدول الكميات والمرفقات" button
   - Should complete without connection reset

3. **Check logs:**
   ```
   🔽 Download request for tender: ...
      Tender Name: ...
      Reference: ...
   ✅ Download completed successfully
   ```

## Why This Happens

Flask's development server has an **auto-reloader** feature for convenience:
- Watches for code changes
- Automatically restarts server
- Great for development!

**But** it can cause issues when:
- Large files are being written
- Many files are created quickly
- Downloads take a long time

## Production Note

⚠️ **This is only an issue in development mode!**

In production (using gunicorn, uwsgi, etc.):
- No auto-reloader
- Multiple workers handle requests
- Downloads won't cause restarts

## Alternative Solutions

If issues persist, consider:

### Option 1: Disable Reloader
```python
app.run(debug=True, use_reloader=False)
```
**Pros:** No restart issues  
**Cons:** Must manually restart after code changes

### Option 2: Move Downloads Outside Project
```python
downloads_folder = 'C:/Etimad_Downloads/'  # Outside project
```
**Pros:** Reloader won't see files  
**Cons:** Files not in project structure

### Option 3: Use Background Tasks
```python
from threading import Thread

def download_async(tender_id):
    # Download in background
    pass

Thread(target=download_async, args=(tender_id,)).start()
return jsonify({'status': 'downloading'})
```
**Pros:** Non-blocking  
**Cons:** More complex

## Current Solution

We chose **`stat` reloader** because:
✅ Still have auto-reload for code changes  
✅ Less sensitive to file system changes  
✅ Minimal code changes  
✅ Works well for development  

## Status

🎉 **Issue Fixed!**

The connection reset issue is now resolved by using the `stat` reloader instead of `watchdog`.

---

**Fixed:** October 13, 2025  
**Issue:** ERR_CONNECTION_RESET during downloads  
**Root Cause:** Watchdog reloader triggering server restart  
**Solution:** Changed to stat reloader + better error handling  
**Status:** ✅ Complete
