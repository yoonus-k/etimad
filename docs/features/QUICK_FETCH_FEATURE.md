# ⚡ Quick Fetch Feature

## Overview

A new "Quick Fetch" button has been added to allow fetching only 10 tenders for fast testing and development.

## Usage

### In the Web Interface

1. Click the **⚡ جلب سريع (10 منافسات)** button
2. The system will fetch only the first page (approximately 10 tenders)
3. Results are displayed immediately (much faster than full fetch)

### Buttons Available

| Button | Purpose | Speed | Tenders Fetched |
|--------|---------|-------|-----------------|
| **جلب المنافسات** | Full fetch | ~1-2 minutes | Up to 2,400 (100 pages × 24) |
| **⚡ جلب سريع** | Quick test | ~5-10 seconds | ~10 (1 page × 10-24) |

## When to Use Quick Fetch?

✅ **Use Quick Fetch when:**
- Testing the application
- Verifying cookies are working
- Checking if classification detection works
- Quick development iterations
- Demonstrating features

❌ **Don't use Quick Fetch when:**
- You need complete tender data
- Looking for specific tenders
- Production use
- Creating reports with all available tenders

## Technical Details

### Frontend Changes

**File:** `templates/index.html`
- Added new button: `<button id="fetchQuickBtn" class="btn-quick">⚡ جلب سريع (10 منافسات)</button>`

**File:** `static/style.css`
- Added `.btn-quick` styling with orange gradient
- Quick button has distinct visual appearance

**File:** `static/script.js`
- Modified `fetchTenders()` to accept `quickMode` parameter
- Quick mode sets `max_pages=1` instead of `max_pages=100`
- Different loading messages for quick vs full fetch

### Backend

**Already Supported!**
The backend already supports the `max_pages` parameter:

```python
@app.route('/api/tenders')
def get_tenders():
    max_pages = request.args.get('max_pages', config.MAX_PAGES, type=int)
    tenders = scraper.fetch_all_tenders(max_pages=max_pages)
```

### API Usage

```bash
# Quick fetch (1 page)
GET /api/tenders?max_pages=1

# Full fetch (100 pages)
GET /api/tenders?max_pages=100

# Custom fetch (e.g., 5 pages)
GET /api/tenders?max_pages=5
```

## Performance

| Mode | Pages | Approx. Tenders | Time | Network Requests |
|------|-------|----------------|------|------------------|
| Quick | 1 | 10-24 | 5-10s | 1 API call |
| Full | 100 | 2,400 | 60-120s | 100 API calls |

## Benefits

1. **Faster Testing** - No need to wait 1-2 minutes for full fetch
2. **Reduced Load** - Less stress on Etimad servers during development
3. **Quick Verification** - Instantly verify cookies and functionality
4. **Better UX** - Users can choose speed vs completeness

## Future Enhancements

Possible improvements:
- [ ] Custom page count selector (1, 5, 10, 50, 100 pages)
- [ ] Remember user's last choice
- [ ] Show estimated time for each option
- [ ] Progress bar showing page fetch progress

---

**Added:** October 13, 2025  
**Version:** 1.1.0
