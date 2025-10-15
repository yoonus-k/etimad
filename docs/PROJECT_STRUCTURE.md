# 📁 Project Structure

This document describes the organized structure of the Etimad Tenders Application.

## 📂 Directory Layout

```
Etimad/
├── 📄 run.py                      # Main entry point - run this to start the app
├── 📄 config.py                   # Application configuration
├── 📄 requirements.txt            # Python dependencies
├── 📄 README.md                   # Project overview and quick start
│
├── 📁 src/                        # Source code (main application)
│   ├── app.py                     # Flask application
│   ├── tender_scraper.py          # Tender fetching and filtering logic
│   ├── attachment_downloader.py   # Document download functionality
│   ├── browser_config.py          # Browser automation config
│   ├── browser_cookie_extractor.py # Cookie extraction from browser
│   ├── cookie_manager.py          # Cookie management
│   ├── __init__.py                # Package initialization
│   └── README.md                  # Source code documentation
│
├── 📁 scripts/                    # Utility scripts
│   ├── count_tenders.py           # Tender counting utility
│   ├── debug_cookies.py           # Cookie debugging
│   ├── SETUP_AUTOMATION.py        # Automation setup
│   └── README.md                  # Scripts documentation
│
├── 📁 data/                       # Data files
│   ├── all_tenders.json           # Cached tender data
│   ├── tender_info.json           # Tender details
│   ├── cookies_backup.json        # Cookie backups
│   └── README.md                  # Data directory documentation
│
├── 📁 debug/                      # Debug files
│   ├── attachments_response.html  # API response samples
│   ├── etimad_homepage.html       # Homepage snapshot
│   ├── etimad_login_page.html     # Login page snapshot
│   └── README.md                  # Debug files documentation
│
├── 📁 templates/                  # Flask HTML templates
│   └── index.html                 # Main web interface
│
├── 📁 static/                     # Static web assets
│   ├── style.css                  # Stylesheets
│   └── script.js                  # JavaScript
│
├── 📁 downloads/                  # Downloaded tender documents
│   └── [tender folders]/          # Organized by tender name
│
├── 📁 tests/                      # Test files
│   ├── test_api.py
│   ├── test_attachments.py
│   ├── test_automation.py
│   ├── test_browser_cookies.py
│   ├── test_download.py
│   ├── test_scraper.py
│   ├── test_tender_details.py
│   └── inspect_login_page.py
│
├── 📁 docs/                       # Documentation
│   ├── INDEX.md                   # Documentation index
│   ├── features/                  # Feature documentation
│   ├── guides/                    # User guides
│   ├── technical/                 # Technical docs
│   ├── troubleshooting/          # Problem solving
│   └── changelog/                 # Version history
│
└── 📁 cookie_extension/           # Browser extension
    ├── manifest.json
    ├── popup.html
    ├── popup.js
    ├── README.md
    ├── INSTALL.md
    └── SUCCESS.md
```

## 🗂️ Directory Purposes

### `/src/` - Source Code
Contains all main application Python modules. This is where the core logic lives.

**Key Files:**
- `app.py` - Flask web server with API endpoints
- `tender_scraper.py` - Business logic for tender operations

### `/scripts/` - Utilities
Standalone scripts for maintenance, debugging, and analysis tasks.

**Usage:** Run independently for specific tasks
```bash
python scripts/count_tenders.py
```

### `/data/` - Data Storage
JSON files for caching and storing application data.

**Contents:**
- API response caches
- Tender information
- Cookie backups

### `/debug/` - Debug Files
HTML snapshots and debug outputs for troubleshooting.

**Purpose:** Help diagnose issues with API responses and web scraping

### `/templates/` & `/static/` - Web Interface
Flask templates and static assets for the web UI.

**Contents:**
- HTML templates
- CSS stylesheets
- JavaScript files

### `/downloads/` - Downloaded Files
Tender documents organized by tender name.

**Structure:** Each tender gets its own folder

### `/tests/` - Test Suite
Unit tests and integration tests for the application.

**Usage:**
```bash
python -m pytest tests/
```

### `/docs/` - Documentation
Comprehensive documentation organized by topic.

**See:** [Documentation Index](./docs/INDEX.md)

### `/cookie_extension/` - Browser Extension
Chrome/Edge extension for easy cookie extraction.

**See:** [Extension README](./cookie_extension/README.md)

## 🚀 Running the Application

### Quick Start
```bash
python run.py
```

### Alternative Methods
```bash
# Run directly from src
python src/app.py

# With specific port
python run.py --port 8080
```

## 📝 Important Notes

### File Paths
- All imports now use relative paths from the project root
- Data files are referenced from the `/data/` directory
- Templates and static files remain in their respective folders

### Configuration
- `config.py` stays at the root for easy access
- Cookie management is centralized
- Environment-specific settings can be added to config

### Development
- Add new features to `/src/`
- Add utility scripts to `/scripts/`
- Add tests to `/tests/`
- Update documentation in `/docs/`

## 🔄 Migration from Old Structure

### What Changed
- **Python files** → Moved to `/src/`
- **Utility scripts** → Moved to `/scripts/`
- **Data files** → Moved to `/data/`
- **Debug HTML** → Moved to `/debug/`
- **Documentation** → Organized in `/docs/`

### Imports Updated
All import statements have been updated to work with the new structure.

### Running Scripts
Use `python run.py` instead of `python app.py` for the main application.

## 📚 Further Reading

- [Main README](./README.md) - Getting started guide
- [Documentation Index](./docs/INDEX.md) - All documentation
- [Troubleshooting](./docs/troubleshooting/TROUBLESHOOTING.md) - Common issues

---

**Last Updated:** October 13, 2025
**Version:** 1.0.0
