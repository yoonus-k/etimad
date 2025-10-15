# Etimad Tenders — README

A lightweight Python Flask application to fetch and display tender listings from the Etimad platform. Use it with either locally cached data or by supplying authentication cookies to call Etimad's web endpoints.

Quick links: [Documentation Index](./docs/INDEX.md) · [Project Structure](./PROJECT_STRUCTURE.md) · [Cookie Extension](./cookie_extension/README.md)

## Features

- Fetch tender listings and cache results to JSON
- Pagination support for large result sets
- Filters to exclude tenders that don't require registration
- Download tender attachments (specifications, annexes)
- Simple RTL Arabic UI and compact card layouts

## Requirements

- Python 3.8+
- Install dependencies: `pip install -r requirements.txt`

## Quick start

1. Install dependencies:

```powershell
pip install -r requirements.txt
```

2. Configure authentication (optional)

Open `config.py` and set:

- To use local cached data (default):

```python
USE_API = False
```

- To call Etimad endpoints with authentication cookies:

```python
USE_API = True
COOKIES = {
    'MobileAuthCookie': 'your_cookie_here',
    # add other cookies copied from the browser
}
```

Tip: keep `config.py` out of version control — add it to `.gitignore` to avoid leaking cookies.

3. Run the app:

```powershell
python run.py
```

Or run the app module directly:

```powershell
python src/app.py
```

Open http://localhost:5000 in your browser.

## Configuration options

- `USE_API`: bool — Use live Etimad API (True) or local cached files (False)
- `COOKIES`: dict — Authentication cookies when `USE_API` is True
- `MAX_PAGES`: int — Maximum pages to fetch per query (default: 100)

## Documentation

See the Documentation Index for full guides and technical details: `docs/INDEX.md`

## Contributing

Small documentation and README improvements are welcome. Please do not commit `config.py` containing real cookies or other secrets.

## Security

- Cookies provide full access to your account — never share them publicly.
- Add `config.py` to `.gitignore` before committing.

---

Last updated: October 2025
### Popular Guides
- [Cookie Management Guide](./docs/guides/COOKIE_MANAGEMENT_GUIDE.md) - Managing authentication cookies
- [Quick Cookie Update](./docs/guides/QUICK_COOKIE_UPDATE.md) - Fast cookie refresh
- [PDF Download Feature](./docs/features/PDF_DOWNLOAD_FEATURE.md) - Download tender documents
- [Browser Automation](./docs/guides/BROWSER_AUTOMATION_GUIDE.md) - Automate browser tasks

## �🔮 TODO

- [ ] تحديد الحقل الصحيح للتحقق من "يتطلب تصنيف"
- [ ] تنفيذ تحميل المستندات الفعلي من Etimad
- [ ] إضافة خيارات بحث وتصفية متقدمة
- [ ] حفظ المنافسات المفضلة
- [ ] تصدير البيانات (Excel/PDF)

---

**Need help?** Check the [Documentation Index](./docs/INDEX.md) or [Troubleshooting Guide](./docs/troubleshooting/TROUBLESHOOTING.md)
