# 🔄 Session Keep-Alive Feature

## Overview

Automatic session keep-alive feature that prevents Etimad cookies from expiring due to inactivity. The system automatically pings the Etimad server every 60 seconds to maintain an active session.

## Problem Solved

- ❌ **Before**: Etimad sessions expire after periods of inactivity
- ❌ **Result**: Need to manually update cookies frequently
- ✅ **After**: Automatic keep-alive maintains session indefinitely

## How It Works

### Backend Process

1. **Background Thread**: A daemon thread runs continuously in the background
2. **Periodic Ping**: Makes a lightweight request to Etimad every 60 seconds
3. **Session Refresh**: Each request uses stored cookies to keep them active
4. **Status Tracking**: Monitors success/failure of each ping

### Technical Implementation

**File**: `src/app.py`

```python
# Keep-alive tracking variables
last_keep_alive_time = None
keep_alive_status = "starting"

# Background thread function
def keep_session_alive():
    """Pings Etimad every minute to keep session active"""
    while True:
        time.sleep(60)  # Wait 1 minute
        
        # Make request to keep session alive
        url = "https://tenders.etimad.sa/Tender/AllTendersForVisitors"
        response = requests.get(url, cookies=scraper.cookies, headers=headers, timeout=10)
        
        if response.status_code == 200:
            last_keep_alive_time = datetime.now()
            keep_alive_status = "active"

# Start thread on application startup
keep_alive_thread = threading.Thread(target=keep_session_alive, daemon=True)
keep_alive_thread.start()
```

## Features

### 1. Automatic Operation

- ✅ Starts automatically when server starts
- ✅ Runs in background (daemon thread)
- ✅ No manual intervention required
- ✅ Works even when browser is closed

### 2. Visual Indicator

- 🔄 **Active**: Green badge showing last refresh time
- ⚠️ **Starting**: Orange badge during initialization
- ⚠️ **No Cookies**: Red badge when cookies missing
- ⚠️ **Error**: Red badge with error status

### 3. Status Monitoring

**API Endpoint**: `/api/keep-alive-status`

**Response**:
```json
{
    "status": "active",
    "last_ping": "2025-10-15 14:30:45",
    "cookies_count": 7
}
```

### 4. Frontend Integration

**UI Badge** (updates every 10 seconds):
```javascript
// Check status periodically
setInterval(updateKeepAliveStatus, 10000);

// Display in UI
keepAliveStatus.textContent = `🔄 نشط - آخر تحديث: ${lastPing}`;
keepAliveStatus.style.background = '#10b981';
```

## Configuration

### Timing

| Parameter | Value | Description |
|-----------|-------|-------------|
| **Ping Interval** | 60 seconds | Time between keep-alive requests |
| **Status Check** | 10 seconds | UI update frequency |
| **Request Timeout** | 10 seconds | Max wait for response |

### Endpoint Used

**URL**: `https://tenders.etimad.sa/Tender/AllTendersForVisitors`
- Lightweight endpoint
- Minimal server load
- Returns quickly
- Maintains session

## Status Values

| Status | Meaning | Badge Color | Action |
|--------|---------|-------------|--------|
| `starting` | Thread initializing | 🟠 Orange | Wait for first ping |
| `active` | Working normally | 🟢 Green | No action needed |
| `no_cookies` | No cookies available | 🔴 Red | Update cookies |
| `error` | Request failed | 🔴 Red | Check connection |
| `error_XXX` | HTTP error code | 🔴 Red | Check Etimad status |

## Benefits

### 1. Convenience
- ✅ No need to manually update cookies frequently
- ✅ Session stays active during long operations
- ✅ Download operations don't time out

### 2. Reliability
- ✅ Automatic recovery from temporary network issues
- ✅ Continuous monitoring
- ✅ Visual feedback of status

### 3. Efficiency
- ✅ Minimal server overhead
- ✅ Lightweight requests
- ✅ Daemon thread (no resource waste)

## Troubleshooting

### Badge Shows "⚠️ لا توجد كوكيز"

**Problem**: No cookies loaded
**Solution**: Click "🍪 تحديث الكوكيز" to load cookies

### Badge Shows "⚠️ خطأ"

**Problem**: Keep-alive request failed
**Solutions**:
1. Check internet connection
2. Verify Etimad website is accessible
3. Update cookies if expired
4. Check server logs for details

### Badge Not Updating

**Problem**: Status not refreshing in UI
**Solutions**:
1. Refresh browser page (F5)
2. Check browser console for errors
3. Verify `/api/keep-alive-status` endpoint works

## Console Output

The keep-alive process logs activity to the console:

```
✅ Session keep-alive started (pings every 60 seconds)
🔄 Keep-alive: Session refreshed at 14:30:45
🔄 Keep-alive: Session refreshed at 14:31:45
🔄 Keep-alive: Session refreshed at 14:32:45
⚠️  Keep-alive: Got status 401  ← Authentication issue
⚠️  Keep-alive error: Connection timeout  ← Network issue
```

## Technical Details

### Threading Model

- **Type**: Daemon thread
- **Lifecycle**: Starts with Flask app, ends with app
- **Safety**: Thread-safe using global variables
- **Resource**: Minimal CPU/memory usage

### Error Handling

```python
try:
    response = requests.get(url, cookies=scraper.cookies, timeout=10)
    if response.status_code == 200:
        keep_alive_status = "active"
    else:
        keep_alive_status = f"error_{response.status_code}"
except Exception as e:
    keep_alive_status = "error"
    print(f"⚠️  Keep-alive error: {e}")
```

### State Management

Global variables track state:
- `last_keep_alive_time`: Timestamp of last successful ping
- `keep_alive_status`: Current status string

## Integration Points

### Startup

**File**: `src/app.py` (after scraper initialization)

```python
# Initialize scraper with configuration
cookies = get_cookies()
scraper = TenderScraper(cookies=cookies, use_api=config.USE_API)

# Start keep-alive thread
keep_alive_thread = threading.Thread(target=keep_session_alive, daemon=True)
keep_alive_thread.start()
```

### UI Components

**Files**:
- `templates/index.html` - Status badge display
- `static/script.js` - Status polling logic
- `static/style.css` - Badge styling

## Future Enhancements

Potential improvements:

1. **Configurable Interval**: Allow user to set ping frequency
2. **Smart Timing**: Increase frequency during active operations
3. **Notification**: Alert user when session about to expire
4. **Auto-Recovery**: Attempt cookie refresh on failure
5. **Statistics**: Track uptime and success rate

## Related Features

- [Cookie Management](../guides/COOKIE_MANAGEMENT_GUIDE.md)
- [Cookie Update Guide](../guides/COOKIE_UPDATE_GUIDE.md)
- [Browser Automation](../guides/BROWSER_AUTOMATION_GUIDE.md)

---

**Status**: ✅ Active and Working
**Added**: October 15, 2025
**Version**: 1.1.0
