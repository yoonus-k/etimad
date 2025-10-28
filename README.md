# 🎯 Etimad Tender Analysis System# Etimad Tenders — README



> **AI-powered intelligent analysis system for Saudi government tenders from the Etimad platform**A lightweight Python Flask application to fetch and display tender listings from the Etimad platform. Use it with either locally cached data or by supplying authentication cookies to call Etimad's web endpoints.



A professional Python Flask application that fetches, analyzes, and evaluates government tenders using **Claude AI (Anthropic)** and advanced market research tools.Quick links: [Documentation Index](./docs/INDEX.md) · [Project Structure](./PROJECT_STRUCTURE.md) · [Cookie Extension](./cookie_extension/README.md)



[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/downloads/)## Features

[![Flask](https://img.shields.io/badge/Flask-3.0+-green.svg)](https://flask.palletsprojects.com/)

[![AI](https://img.shields.io/badge/AI-Claude%20Sonnet%204-purple.svg)](https://www.anthropic.com/)- Fetch tender listings and cache results to JSON

- Pagination support for large result sets

---- Filters to exclude tenders that don't require registration

- Download tender attachments (specifications, annexes)

## ✨ Features- Simple RTL Arabic UI and compact card layouts



### 🤖 AI-Powered Analysis (Phase 5)## Requirements

- **Claude AI Integration**: Intelligent tender evaluation using Anthropic's Claude Sonnet 4

- **Smart Caching**: 3-tier caching system (documents, search, analysis) for cost optimization- Python 3.8+

- **Cost Tracking**: Real-time API usage monitoring with budget limits- Install dependencies: `pip install -r requirements.txt`

- **Comprehensive Reports**: Bilingual (Arabic/English) analysis reports

## Quick start

### 📊 Tender Management

- **Quick Fetch**: Fast 10-tender fetch for rapid testing1. Install dependencies:

- **Bulk Operations**: Download and analyze multiple tenders simultaneously

- **Smart Filtering**: Exclude non-registration tenders, filter by classification```powershell

- **Downloads Management**: Track and manage downloaded tender documentspip install -r requirements.txt

```

### 🔐 Authentication & Automation

- **Cookie Management**: Browser extension and automated cookie extraction2. Configure authentication (optional)

- **Auto-Login**: Selenium-based browser automation

- **Session Keep-Alive**: Automatic session refresh to prevent timeoutsOpen `config.py` and set:

- **Multi-Browser Support**: Chrome, Edge, Firefox cookie extraction

- To use local cached data (default):

### 📄 Document Processing

- **Multi-Format Support**: PDF, Word (DOC/DOCX), Excel (XLS/XLSX), images```python

- **OCR Integration**: Extract text from scanned documents and imagesUSE_API = False

- **Intelligent Extraction**: Smart document structure recognition```



### 💡 Intelligent Evaluation- To call Etimad endpoints with authentication cookies:

- **Financial Analysis**: Cost estimation, pricing strategy, profitability calculations

- **Technical Assessment**: Capability matching, feasibility analysis, risk evaluation```python

- **Market Research**: Competitive intelligence using Tavily APIUSE_API = True

- **Recommendation Engine**: AI-powered bid/no-bid recommendations with confidence scoresCOOKIES = {

    'MobileAuthCookie': 'your_cookie_here',

---    # add other cookies copied from the browser

}

## 🚀 Quick Start```



### PrerequisitesTip: keep `config.py` out of version control — add it to `.gitignore` to avoid leaking cookies.



- **Python 3.8+**3. Run the app:

- **Anthropic API Key** (for Claude AI)

- **Tavily API Key** (for market research)```powershell

python run.py

### Installation```



1. **Clone the repository**Or run the app module directly:

   ```bash

   git clone https://github.com/yoonus-k/etimad.git```powershell

   cd etimadpython src/app.py

   ``````



2. **Install dependencies**Open http://localhost:5000 in your browser.

   ```bash

   pip install -r requirements.txt## Configuration options

   ```

- `USE_API`: bool — Use live Etimad API (True) or local cached files (False)

3. **Configure API keys**- `COOKIES`: dict — Authentication cookies when `USE_API` is True

   - `MAX_PAGES`: int — Maximum pages to fetch per query (default: 100)

   Create `.env` file or set environment variables:

   ```bash## Documentation

   ANTHROPIC_API_KEY=your_claude_api_key_here

   TAVILY_API_KEY=your_tavily_api_key_hereSee the Documentation Index for full guides and technical details: `docs/INDEX.md`

   ```

## Contributing

4. **Configure authentication**

   Small documentation and README improvements are welcome. Please do not commit `config.py` containing real cookies or other secrets.

   Edit `config.py`:

   ```python## Security

   USE_API = True  # Use Etimad API (requires cookies)

   - Cookies provide full access to your account — never share them publicly.

   COOKIES = {- Add `config.py` to `.gitignore` before committing.

       'MobileAuthCookie': 'your_cookie_here',

       'login.etimad.ssk4': 'your_cookie_here',---

       # ... other cookies

   }Last updated: October 2025

   ```### Popular Guides

- [Cookie Management Guide](./docs/guides/COOKIE_MANAGEMENT_GUIDE.md) - Managing authentication cookies

   > 💡 **Tip**: Use the [Cookie Extension](./cookie_extension/README.md) for easy cookie management- [Quick Cookie Update](./docs/guides/QUICK_COOKIE_UPDATE.md) - Fast cookie refresh

- [PDF Download Feature](./docs/features/PDF_DOWNLOAD_FEATURE.md) - Download tender documents

5. **Run the application**- [Browser Automation](./docs/guides/BROWSER_AUTOMATION_GUIDE.md) - Automate browser tasks

   ```bash

   python run.py## �🔮 TODO

   ```

- [ ] تحديد الحقل الصحيح للتحقق من "يتطلب تصنيف"

6. **Open in browser**- [ ] تنفيذ تحميل المستندات الفعلي من Etimad

   ```- [ ] إضافة خيارات بحث وتصفية متقدمة

   http://localhost:5000- [ ] حفظ المنافسات المفضلة

   ```- [ ] تصدير البيانات (Excel/PDF)



------



## 📁 Project Structure**Need help?** Check the [Documentation Index](./docs/INDEX.md) or [Troubleshooting Guide](./docs/troubleshooting/TROUBLESHOOTING.md)


```
Etimad/
├── src/                        # 🐍 Source code (modular architecture)
│   ├── config/                 # ⚙️ Configuration
│   ├── core/                   # 🧠 AI engine (Claude, caching, cost tracking)
│   ├── scrapers/               # 🕷️ Data collection
│   ├── processors/             # 📄 Document processing
│   ├── evaluators/             # 📊 Analysis modules
│   ├── reports/                # 📝 Report generation
│   └── utils/                  # 🛠️ Utilities
│
├── data/                       # 📂 Data storage
│   ├── cache/                  # 💾 Cached results
│   ├── tender_analyses/        # 📊 Analysis reports
│   └── company_profile.json    # 🏢 Company context
│
├── downloads/                  # 📥 Downloaded tender documents
├── static/                     # 🎨 Frontend assets
├── templates/                  # 🖼️ HTML templates
├── docs/                       # 📚 Documentation
└── tests/                      # 🧪 Test suites
```

> 📖 **Detailed structure**: See [src/README.md](./src/README.md)

---

## 📚 Documentation

### 📖 Getting Started
- [**Quick Start Guide**](./docs/QUICK_REFERENCE.md) - Get up and running in 5 minutes
- [**Project Structure**](./docs/PROJECT_STRUCTURE.md) - Understand the codebase
- [**Source Code Guide**](./src/README.md) - Detailed module documentation

### 🔧 Configuration & Setup
- [**Cookie Management Guide**](./docs/guides/COOKIE_MANAGEMENT_GUIDE.md) - Complete authentication setup
- [**Browser Extension**](./cookie_extension/README.md) - Install cookie extraction extension
- [**Browser Automation**](./docs/guides/BROWSER_AUTOMATION_GUIDE.md) - Selenium setup

### 🎯 Features
- [**AI Analysis**](./docs/features/AI_ANALYSIS_PHASE1_COMPLETE.md) - Claude AI integration
- [**PDF Download**](./docs/features/PDF_DOWNLOAD_FEATURE.md) - Document downloading
- [**Bulk Operations**](./docs/features/BULK_CHECK_READY.md) - Batch processing

### 🐛 Troubleshooting
- [**Troubleshooting Guide**](./docs/troubleshooting/TROUBLESHOOTING.md) - Common issues

---

## 🎯 Usage

### 1. Fetch Tenders
```bash
# Quick fetch (10 tenders for testing)
Click "Quick Fetch (10)" button

# Full fetch (all pages)
Click "تحديث المناقصات" button
```

### 2. Download Documents
```bash
# Click on any tender card
# Click "تحميل المستندات" button
# Documents saved to downloads/{tender_id}/
```

### 3. AI Analysis
```bash
# Navigate to Downloads tab
# Click "تحليل" on any downloaded tender
# Wait for AI analysis (uses Claude Sonnet 4)
# View comprehensive report
```

---

## ⚙️ Configuration

### `config.py` - Main Configuration
```python
# API Mode
USE_API = True  # True: Live API | False: Local cache

# Authentication (Required when USE_API=True)
COOKIES = {
    'MobileAuthCookie': '...',
    'login.etimad.ssk4': '...',
}

# Limits
MAX_PAGES = 100  # Maximum pages to fetch
```

### Environment Variables
```bash
# API Keys
ANTHROPIC_API_KEY=sk-ant-...        # Claude AI
TAVILY_API_KEY=tvly-...             # Market research
```

---

## 🔐 Security & Best Practices

### ⚠️ Important Security Notes

1. **Never commit `config.py` with real cookies**
   ```bash
   echo "config.py" >> .gitignore
   ```

2. **Store API keys securely**
   - Use `.env` files (not committed)
   - Never hardcode in source files

3. **Cookie expiration**
   - Cookies expire after ~1 hour
   - Use Auto-Login feature for refresh

---

## 🛠️ Technology Stack

### Backend
- **Flask 3.0+** - Web framework
- **Python 3.8+** - Programming language

### AI & Intelligence
- **Anthropic Claude Sonnet 4** - AI analysis
- **Tavily API** - Market research

### Document Processing
- **PyPDF2** - PDF extraction
- **python-docx** - Word documents
- **openpyxl** - Excel files
- **Tesseract OCR** - Image text extraction
- **WeasyPrint** - PDF generation

---

## 📊 API Costs

| Service | Model | Input | Output | Avg Cost/Tender |
|---------|-------|-------|--------|-----------------|
| **Claude AI** | Sonnet 4 | $3/1M tokens | $15/1M tokens | ~$0.05-0.15 |
| **Tavily** | Research API | Free tier: 1000 searches/month | - | $0.00 |

> 💡 **Cost Optimization**: Caching reduces repeated API calls by ~80%

---

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 📧 Support

Need help?

1. **Documentation**: Check the [docs/](./docs/) folder
2. **Troubleshooting**: See [Troubleshooting Guide](./docs/troubleshooting/TROUBLESHOOTING.md)
3. **Issues**: Open an issue on GitHub
4. **Quick Reference**: See [QUICK_REFERENCE.md](./docs/QUICK_REFERENCE.md)

---

## 🗺️ Roadmap

### ✅ Completed
- [x] Phase 1: Authentication & Cookie Management
- [x] Phase 2: Data Collection & Document Processing
- [x] Phase 3: AI Analysis Integration (Claude)
- [x] Phase 4: Report Generation (Bilingual)
- [x] Phase 5: Optimization (Caching, Cost Tracking)
- [x] Code Reorganization (Professional structure)

### 🔄 Future
- [ ] Enhanced UI/UX improvements
- [ ] Advanced filtering options
- [ ] Tender comparison features
- [ ] Mobile app (React Native)
- [ ] Historical analysis dashboard

---

<div align="center">

**Built with ❤️ for government procurement professionals**

[⭐ Star this repo](https://github.com/yoonus-k/etimad) • [🐛 Report Bug](https://github.com/yoonus-k/etimad/issues) • [💡 Request Feature](https://github.com/yoonus-k/etimad/issues)

</div>

---

**Last Updated**: October 28, 2025  
**Version**: 2.0.0
