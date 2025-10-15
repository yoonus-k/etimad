# Data directory

Stores JSON artifacts used by the app. Common files:

- `all_tenders.json` — cached results
- `tender_info.json` — per-tender details
- `cookies_backup.json` — optional cookie backups

Notes:

- These files can be large; consider adding `data/*.json` or specific filenames to `.gitignore` before committing.

