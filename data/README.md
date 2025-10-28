# 📂 Data Directory# Data directory



Application data storage for cache, analysis reports, and configuration.Stores JSON artifacts used by the app. Common files:



## Structure- `all_tenders.json` — cached results

- `tender_info.json` — per-tender details

```- `cookies_backup.json` — optional cookie backups

data/

├── cache/                      # Cached API resultsNotes:

├── tender_analyses/            # Generated analysis reports (HTML)

├── analysis_templates/         # Report templates- These files can be large; consider adding `data/*.json` or specific filenames to `.gitignore` before committing.

├── all_tenders.json           # Tender listings cache

├── company_profile.json       # Company configuration
└── api_costs.json             # API usage tracking
```

## Important Notes

**Security**: Never commit files with real cookies or sensitive data.

**Already in `.gitignore`:**
- `*.json` (except templates)
- `cache/`
- `tender_analyses/`

---

**Last Updated**: October 28, 2025
