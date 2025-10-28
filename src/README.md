# 📁 Source Code Structure

## Overview

This directory contains all the Python source code for the **Etimad Tender Analysis System**, organized into logical modules for maintainability and scalability.

## 🏗️ Directory Structure

```
src/
├── app.py                      # 🚀 Main Flask application
├── __init__.py
│
├── config/                     # ⚙️ Configuration
│   ├── __init__.py
│   ├── browser_config.py      # Browser automation settings
│   └── company_context.py     # Company profile & context
│
├── core/                       # 🧠 Core AI Engine
│   ├── __init__.py
│   ├── ai_analyzer.py         # Claude AI integration
│   ├── cache_manager.py       # Intelligent caching (Phase 5)
│   └── cost_tracker.py        # API cost tracking (Phase 5)
│
├── scrapers/                   # 🕷️ Data Collection
│   ├── __init__.py
│   ├── tender_scraper.py      # Etimad tender scraping
│   ├── attachment_downloader.py # Document downloading
│   └── cookie_manager.py      # Cookie management & automation
│
├── processors/                 # 📄 Document Processing
│   ├── __init__.py
│   ├── document_processor.py  # Extract text from PDF/Word/Excel
│   └── ocr_processor.py       # OCR for images
│
├── evaluators/                 # 📊 Analysis & Evaluation
│   ├── __init__.py
│   ├── financial_evaluator.py # Cost estimation & pricing
│   ├── technical_evaluator.py # Technical feasibility
│   └── market_researcher.py   # Market intelligence (Tavily)
│
├── reports/                    # 📝 Report Generation
│   ├── __init__.py
│   └── report_generator.py    # HTML/PDF report generation
│
└── utils/                      # 🛠️ Utilities
    ├── __init__.py
    └── browser_cookie_extractor.py # Extract cookies from browser
```

## 🎯 Module Responsibilities

### `app.py` - Main Application
Flask web server with API endpoints for:
- Tender fetching and filtering
- Document downloading
- AI analysis orchestration
- Report generation
- Cookie management

### `config/` - Configuration Management
- **browser_config.py**: Selenium/browser automation settings
- **company_context.py**: Company profile, capabilities, pricing strategy

### `core/` - AI & Optimization (Phase 5)
- **ai_analyzer.py**: Claude Sonnet 4 integration for intelligent tender analysis
- **cache_manager.py**: 3-tier caching system (documents, search, analysis)
- **cost_tracker.py**: Real-time API cost monitoring with budget limits

### `scrapers/` - Data Collection
- **tender_scraper.py**: Scrape tenders from Etimad government portal
- **attachment_downloader.py**: Download and organize tender documents
- **cookie_manager.py**: Browser automation for session management

### `processors/` - Document Processing
- **document_processor.py**: Extract text from PDF, Word, Excel, images
- **ocr_processor.py**: Optical Character Recognition for scanned documents

### `evaluators/` - Analysis Modules
- **financial_evaluator.py**: Cost estimation, pricing analysis, profitability calculations
- **technical_evaluator.py**: Capability matching, feasibility assessment, risk analysis
- **market_researcher.py**: Market intelligence and competitive analysis using Tavily API

### `reports/` - Report Generation
- **report_generator.py**: Generate comprehensive bilingual (Arabic/English) HTML reports

### `utils/` - Utility Functions
- **browser_cookie_extractor.py**: Extract authentication cookies from installed browsers

## 🔄 Data Flow

```
User Request
    ↓
app.py (Flask API)
    ↓
scrapers/tender_scraper.py → Fetch tenders from Etimad
    ↓
scrapers/attachment_downloader.py → Download documents
    ↓
processors/document_processor.py → Extract text
processors/ocr_processor.py → Process images
    ↓
core/ai_analyzer.py → Claude AI Analysis
    ↓
evaluators/financial_evaluator.py → Financial analysis
evaluators/technical_evaluator.py → Technical assessment
evaluators/market_researcher.py → Market research
    ↓
core/cost_tracker.py → Track costs
core/cache_manager.py → Cache results
    ↓
reports/report_generator.py → Generate reports
    ↓
Return results to user
```

## 📦 Import Guidelines

### In `app.py`:
```python
from src.config import CompanyContext
from src.core import AIAnalyzer, CacheManager, CostTracker
from src.scrapers import TenderScraper
from src.processors import DocumentProcessor
from src.evaluators import FinancialEvaluator, TechnicalEvaluator, MarketResearcher
from src.reports import ReportGenerator
```

### In module files:
```python
# Relative imports within same package
from .tender_scraper import TenderScraper

# Absolute imports for cross-package dependencies
from src.config import CompanyContext
from src.core import AIAnalyzer
```

## 🚀 Running the Application

From the repository root:

```bash
# Using run.py
python run.py

# Or directly
python src/app.py
```

The server will start on `http://localhost:5000`

## 🛠️ Development Guidelines

1. **Single Responsibility**: Each module should have one clear purpose
2. **Clean Imports**: Use `__init__.py` to expose public APIs only
3. **Type Hints**: Use type annotations for better code clarity
4. **Documentation**: Add docstrings to all public classes/functions
5. **Error Handling**: Always handle exceptions gracefully
6. **Logging**: Use `logging` module, avoid `print()` statements
7. **Testing**: Mirror this structure in `tests/` directory

## 📝 Adding New Features

1. **Identify category**: Which directory best fits your feature?
2. **Create module**: Add new `.py` file in appropriate directory
3. **Update __init__.py**: Export public APIs
4. **Update imports**: Modify `app.py` if needed
5. **Document**: Update this README

## 🔍 Phase Implementation Status

- ✅ **Phase 1**: Authentication & Cookie Management (`scrapers/cookie_manager.py`)
- ✅ **Phase 2**: Data Collection & Processing (`scrapers/`, `processors/`)
- ✅ **Phase 3**: AI Analysis Integration (`core/ai_analyzer.py`)
- ✅ **Phase 4**: Report Generation (`reports/report_generator.py`)
- ✅ **Phase 5**: Optimization (`core/cache_manager.py`, `core/cost_tracker.py`)

---

**Last Updated**: October 28, 2025  
**Project**: Etimad Tender Analysis System  
**Version**: 1.0.0
