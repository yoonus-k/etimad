See `../docs/extensions/COOKIE_EXTENSION.md` for the cookie extension documentation.
# Etimad Cookie Extractor — README

Small browser extension to extract authentication cookies from Etimad pages and format them as a Python dictionary for the scraper.

Important: extracted cookies grant access to your account. Treat them like credentials and never commit them to a public repo.

## Install (Chromium browsers)

1. Open extensions page (e.g. `chrome://extensions/`).
2. Enable Developer mode.
3. Click "Load unpacked" and select this project's `cookie_extension` folder.

## Usage

1. Log in to https://tenders.etimad.sa in your browser.
2. Click the extension icon and press the extract button.
3. Click copy and paste the resulting `COOKIES = {...}` block into `config.py`.

Security notes:

- Add `config.py` to `.gitignore` before committing.
- Cookies are sensitive — rotate them if exposed.

## Output example

```python
COOKIES = {
    'MobileAuthCookie': 'CfDJ8PsrcMqZTC9JiEfQ...',
    'TSPD_101': '088c96e98eab2800967b71b...',
    'idsrv.session': '8011FDC7EB2BD19F2819...',
}
```

## Files

- `manifest.json` — extension manifest
- `popup.html` — UI
- `popup.js` — extraction logic

Last updated: October 2025

