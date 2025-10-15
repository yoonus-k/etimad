# 🚀 Quick Reference - Organized Structure

## ✅ Organization Complete!

Your project has been reorganized for better maintainability and clarity.

## 📍 Quick Navigation

| What You Need | Where to Find It |
|---------------|------------------|
| **Run the app** | `python run.py` |
| **Main source code** | `src/` folder |
| **Utility scripts** | `scripts/` folder |
| **Data files** | `data/` folder |
| **Documentation** | `docs/` folder → [INDEX.md](docs/INDEX.md) |
| **Configuration** | `config.py` (root) |
| **Project structure** | [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md) |

## 🎯 Common Tasks

### Start the Application
```bash
python run.py
```

### Run a Utility Script
```bash
python scripts/count_tenders.py
python scripts/debug_cookies.py
```

### Access Data Files
```bash
# Data files are now in data/ folder
data/all_tenders.json
data/tender_info.json
data/cookies_backup.json
```

### Find Documentation
```bash
# All docs organized in docs/ folder
docs/INDEX.md              # Start here!
docs/features/             # Feature documentation
docs/guides/               # User guides
docs/troubleshooting/      # Problem solving
```

## 📂 New Directory Structure

```
Etimad/
├── 🚀 run.py              ← Run this to start!
├── ⚙️ config.py           ← Configuration
├── 📦 requirements.txt    ← Dependencies
│
├── 📁 src/                ← Main application code
├── 📁 scripts/            ← Utility scripts
├── 📁 data/               ← JSON data files
├── 📁 debug/              ← Debug HTML files
├── 📁 templates/          ← Flask templates
├── 📁 static/             ← CSS, JS
├── 📁 downloads/          ← Downloaded docs
├── 📁 tests/              ← Test suite
├── 📁 docs/               ← Documentation
└── 📁 cookie_extension/   ← Browser extension
```

## 🔄 What Changed?

### ✅ Files Moved
- **Python modules** → `src/`
- **Utility scripts** → `scripts/`
- **JSON data** → `data/`
- **Debug HTML** → `debug/`
- **Documentation** → `docs/` (organized)

### ✅ Files Created
- `run.py` - Easy app launcher
- `PROJECT_STRUCTURE.md` - Detailed structure guide
- `.gitignore` - Proper Git ignores
- `README.md` files in each folder

### ✅ Imports Updated
All Python imports updated to work with new structure.

## 📚 Documentation

### Main Docs
- [README.md](README.md) - Getting started
- [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md) - Detailed structure
- [docs/INDEX.md](docs/INDEX.md) - Documentation index

### Feature Docs
- [docs/features/](docs/features/) - All feature documentation

### User Guides
- [Cookie Management](docs/guides/COOKIE_MANAGEMENT_GUIDE.md)
- [Quick Cookie Update](docs/guides/QUICK_COOKIE_UPDATE.md)
- [Browser Automation](docs/guides/BROWSER_AUTOMATION_GUIDE.md)

### Troubleshooting
- [Troubleshooting Guide](docs/troubleshooting/TROUBLESHOOTING.md)

## 🎓 Best Practices

### Adding New Code
```bash
# Add main features to src/
src/my_new_feature.py

# Add utilities to scripts/
scripts/my_utility.py

# Add tests to tests/
tests/test_my_feature.py
```

### Working with Data
```bash
# Store data files in data/
data/my_data.json

# Reference in code:
from pathlib import Path
data_file = Path(__file__).parent.parent / 'data' / 'my_data.json'
```

### Documentation
```bash
# Add feature docs to docs/features/
docs/features/MY_FEATURE.md

# Add guides to docs/guides/
docs/guides/HOW_TO_USE_X.md

# Update the index
docs/INDEX.md
```

## ⚡ Quick Tips

1. **Always run from root**: `python run.py`
2. **Check docs first**: `docs/INDEX.md`
3. **Use relative paths**: All imports use proper paths
4. **Each folder has README**: Check folder README for details

## 🆘 Need Help?

1. **Structure questions** → [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md)
2. **Feature questions** → [docs/features/](docs/features/)
3. **Problems** → [Troubleshooting](docs/troubleshooting/TROUBLESHOOTING.md)
4. **General help** → [README.md](README.md)

---

**Organized on:** October 13, 2025  
**Status:** ✅ Complete and ready to use!
