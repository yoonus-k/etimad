# 🤖 AI Tender Analysis - Architecture & Flow Diagrams

This document provides comprehensive Mermaid diagrams to visualize the AI Tender Analysis system architecture, workflows, and data flows.

---

## 📊 Table of Contents

1. [System Architecture Overview](#1-system-architecture-overview)
2. [AI Analysis Workflow](#2-ai-analysis-workflow)
3. [Document Processing Pipeline](#3-document-processing-pipeline)
4. [API Integration Architecture](#4-api-integration-architecture)
5. [Data Flow Diagram](#5-data-flow-diagram)
6. [User Interface Flow](#6-user-interface-flow)
7. [Analysis Components Breakdown](#7-analysis-components-breakdown)
8. [Error Handling & Retry Logic](#8-error-handling--retry-logic)
9. [Database & Storage Schema](#9-database--storage-schema)
10. [Deployment Architecture](#10-deployment-architecture)

---

## 1. System Architecture Overview

```mermaid
graph TB
    subgraph "Frontend Layer"
        UI[Web UI - Flask Templates]
        JS[JavaScript Client]
        CSS[RTL Arabic Styling]
    end

    subgraph "Backend Layer - Flask App"
        API[Flask REST API]
        Routes[Route Handlers]
        Auth[Cookie Authentication]
        KeepAlive[Session Keep-Alive]
    end

    subgraph "AI Analysis Engine"
        Orchestrator[AI Analyzer Orchestrator]
        DocProc[Document Processor]
        OCR[OCR Processor]
        FinEval[Financial Evaluator]
        TechEval[Technical Evaluator]
        Market[Market Researcher]
        Report[Report Generator]
    end

    subgraph "External Services"
        OpenAI[OpenAI GPT-4o API]
        Search[Tavily/SerpAPI]
        Etimad[Etimad Platform API]
    end

    subgraph "Data Storage"
        JSON[(JSON Files)]
        Downloads[(Downloads Folder)]
        Cache[(Analysis Cache)]
        CompanyProfile[(Company Profile)]
    end

    UI --> JS
    JS --> API
    API --> Routes
    Routes --> Auth
    Routes --> Orchestrator
    
    Orchestrator --> DocProc
    Orchestrator --> FinEval
    Orchestrator --> TechEval
    Orchestrator --> Market
    Orchestrator --> Report
    
    DocProc --> OCR
    DocProc --> Downloads
    
    FinEval --> OpenAI
    TechEval --> OpenAI
    Market --> Search
    Market --> OpenAI
    Report --> OpenAI
    
    Auth --> Etimad
    KeepAlive --> Etimad
    Routes --> Etimad
    
    Orchestrator --> Cache
    Orchestrator --> CompanyProfile
    Report --> Downloads

    style Orchestrator fill:#ff9999
    style OpenAI fill:#99ccff
    style Etimad fill:#99ff99
```

---

## 2. AI Analysis Workflow

```mermaid
sequenceDiagram
    participant User
    participant WebUI
    participant FlaskAPI
    participant AIAnalyzer
    participant DocProcessor
    participant OpenAI
    participant MarketSearch
    participant ReportGen

    User->>WebUI: Click "🤖 تحليل" button
    WebUI->>FlaskAPI: POST /api/tender/{id}/analyze
    
    FlaskAPI->>AIAnalyzer: Start analysis task
    AIAnalyzer-->>FlaskAPI: Return task_id
    FlaskAPI-->>WebUI: Return {task_id, status: "started"}
    
    WebUI->>WebUI: Show progress modal
    
    loop Progress Polling
        WebUI->>FlaskAPI: GET /api/tender/{id}/status
        FlaskAPI-->>WebUI: Return progress %
        WebUI->>WebUI: Update progress bar
    end
    
    par Document Processing
        AIAnalyzer->>DocProcessor: Extract text from PDFs
        DocProcessor->>DocProcessor: Run OCR on scanned docs
        DocProcessor->>DocProcessor: Parse Excel BOQ
        DocProcessor-->>AIAnalyzer: Combined text data
    end
    
    AIAnalyzer->>OpenAI: Analyze tender requirements
    OpenAI-->>AIAnalyzer: Structured requirements
    
    AIAnalyzer->>MarketSearch: Search for similar projects
    MarketSearch-->>AIAnalyzer: Market data & prices
    
    AIAnalyzer->>OpenAI: Financial evaluation
    OpenAI-->>AIAnalyzer: Cost breakdown & pricing
    
    AIAnalyzer->>OpenAI: Technical evaluation
    OpenAI-->>AIAnalyzer: Feasibility assessment
    
    AIAnalyzer->>OpenAI: Generate recommendations
    OpenAI-->>AIAnalyzer: Priority & bid strategy
    
    AIAnalyzer->>ReportGen: Create PDF report
    ReportGen->>ReportGen: Render HTML template
    ReportGen->>ReportGen: Convert to PDF
    ReportGen-->>AIAnalyzer: PDF path
    
    AIAnalyzer-->>FlaskAPI: Analysis complete
    FlaskAPI-->>WebUI: {status: "complete", results}
    
    WebUI->>WebUI: Show results modal
    User->>WebUI: Click "View Report"
    WebUI->>FlaskAPI: GET /api/tender/{id}/report.pdf
    FlaskAPI-->>WebUI: PDF file
    WebUI->>User: Download/Display PDF
```

---

## 3. Document Processing Pipeline

```mermaid
flowchart TD
    Start([Start Document Processing]) --> FindFolder[Find Tender Folder in downloads/]
    
    FindFolder --> ListFiles[List All Files in Folder]
    
    ListFiles --> CheckFileType{Check File Type}
    
    CheckFileType -->|PDF| IsPDFScanned{Is Scanned PDF?}
    CheckFileType -->|Excel| ProcessExcel[Extract Tables & BOQ]
    CheckFileType -->|Word| ProcessWord[Extract Text with python-docx]
    CheckFileType -->|Image| ProcessImage[Run OCR with Tesseract]
    
    IsPDFScanned -->|Yes| RunOCR[Run OCR with pytesseract]
    IsPDFScanned -->|No| ExtractPDF[Extract text with pdfplumber]
    
    RunOCR --> CleanText[Clean & Normalize Arabic Text]
    ExtractPDF --> CleanText
    ProcessExcel --> CleanText
    ProcessWord --> CleanText
    ProcessImage --> CleanText
    
    CleanText --> StructureData[Structure Data by Document Type]
    
    StructureData --> CombineData[Combine All Extracted Content]
    
    CombineData --> SaveCache{Save to Cache?}
    
    SaveCache -->|Yes| CacheFile[Save to analysis_cache/{tender_id}.json]
    SaveCache -->|No| ReturnData[Return Structured Data]
    
    CacheFile --> ReturnData
    
    ReturnData --> End([End - Ready for AI Analysis])
    
    style Start fill:#90EE90
    style End fill:#FFB6C1
    style RunOCR fill:#FFD700
    style CleanText fill:#87CEEB
```

---

## 4. API Integration Architecture

```mermaid
graph LR
    subgraph "Flask Backend"
        A[Flask Routes] --> B[TenderScraper]
        A --> C[AI Analyzer]
        A --> D[Attachment Downloader]
    end
    
    subgraph "Etimad Platform"
        E[Tender Listings API]
        F[Tender Details API]
        G[Attachments API]
        H[Classification API]
        I[Conditions Template]
    end
    
    subgraph "AI Services"
        J[OpenAI GPT-4o]
        K[Tavily Search API]
        L[SerpAPI Alternative]
    end
    
    subgraph "Authentication"
        M[Cookie Manager]
        N[Browser Automation]
        O[Session Keep-Alive]
    end
    
    B --> M
    M --> E
    B --> F
    D --> G
    D --> H
    D --> I
    
    C --> J
    C --> K
    C --> L
    
    M --> N
    M --> O
    O --> E
    
    style J fill:#ff9999
    style K fill:#ffcc99
    style M fill:#99ccff
```

---

## 5. Data Flow Diagram

```mermaid
flowchart TD
    subgraph "Input Sources"
        A1[Etimad API - Tender List]
        A2[Downloaded Documents]
        A3[Company Profile JSON]
    end
    
    subgraph "Processing Layer"
        B1[Text Extraction]
        B2[OCR Processing]
        B3[Data Normalization]
    end
    
    subgraph "AI Analysis Layer"
        C1[Requirement Analysis]
        C2[Financial Evaluation]
        C3[Technical Assessment]
        C4[Market Research]
        C5[Company Fit Analysis]
    end
    
    subgraph "Knowledge Augmentation"
        D1[Internet Search Results]
        D2[Historical Tender Data]
        D3[Market Pricing Data]
        D4[Company Capabilities]
    end
    
    subgraph "Output Generation"
        E1[Analysis Summary JSON]
        E2[PDF Report Arabic]
        E3[PDF Report English]
        E4[Bid Price Recommendation]
        E5[Action Items List]
    end
    
    subgraph "Storage"
        F1[(Analysis Cache)]
        F2[(Report PDFs)]
        F3[(Tender Metadata)]
    end
    
    A1 --> B3
    A2 --> B1
    A2 --> B2
    A3 --> D4
    
    B1 --> B3
    B2 --> B3
    
    B3 --> C1
    C1 --> C2
    C1 --> C3
    C2 --> C4
    C3 --> C5
    
    D1 --> C4
    D2 --> C2
    D3 --> C2
    D4 --> C5
    
    C4 --> D1
    
    C5 --> E1
    E1 --> E2
    E1 --> E3
    E1 --> E4
    E1 --> E5
    
    E1 --> F1
    E2 --> F2
    E3 --> F2
    E1 --> F3
    
    style C1 fill:#FFE4B5
    style C2 fill:#FFE4B5
    style C3 fill:#FFE4B5
    style C4 fill:#FFE4B5
    style C5 fill:#FFE4B5
```

---

## 6. User Interface Flow

```mermaid
stateDiagram-v2
    [*] --> HomePage: User visits app
    
    HomePage --> TenderList: Fetch tenders
    
    TenderList --> TenderSelected: User clicks tender
    
    TenderSelected --> DownloadDocs: Click "📥 Download"
    TenderSelected --> AnalyzeTender: Click "🤖 Analyze"
    
    DownloadDocs --> DownloadProgress: Show progress
    DownloadProgress --> DownloadComplete: Files saved
    DownloadComplete --> TenderSelected: Return to tender
    
    AnalyzeTender --> AnalysisProgress: Show progress modal
    
    state AnalysisProgress {
        [*] --> ExtractingDocs: Step 1
        ExtractingDocs --> RunningOCR: Step 2
        RunningOCR --> AIAnalysis: Step 3
        AIAnalysis --> MarketSearch: Step 4
        MarketSearch --> GeneratingReport: Step 5
        GeneratingReport --> [*]
    }
    
    AnalysisProgress --> AnalysisComplete: 100% done
    
    AnalysisComplete --> ViewResults: Show results modal
    
    ViewResults --> ViewPDFReport: Click "View Report"
    ViewResults --> DownloadReport: Click "Download"
    ViewResults --> EmailReport: Click "Email"
    ViewResults --> ReAnalyze: Click "Re-analyze"
    
    ViewPDFReport --> ViewResults: Back
    DownloadReport --> ViewResults: Back
    EmailReport --> ViewResults: Back
    ReAnalyze --> AnalysisProgress: Start over
    
    ViewResults --> TenderList: Close / Back
    TenderList --> [*]: Logout
```

---

## 7. Analysis Components Breakdown

```mermaid
graph TD
    subgraph "AI Analyzer - Main Orchestrator"
        A[ai_analyzer.py]
    end
    
    subgraph "Document Processing"
        B1[document_processor.py<br/>Extract PDF, Word, Excel]
        B2[ocr_processor.py<br/>Tesseract OCR for Arabic]
    end
    
    subgraph "AI Evaluation Modules"
        C1[financial_evaluator.py<br/>Cost & Pricing Analysis]
        C2[technical_evaluator.py<br/>Feasibility & Requirements]
        C3[company_context.py<br/>Capability Matching]
    end
    
    subgraph "External Research"
        D1[market_researcher.py<br/>Internet Search & Data]
    end
    
    subgraph "Report Generation"
        E1[report_generator.py<br/>PDF Creation]
        E2[Templates<br/>HTML Jinja2 Templates]
    end
    
    subgraph "Supporting Services"
        F1[OpenAI API Client]
        F2[Search API Client]
        F3[Cache Manager]
    end
    
    A --> B1
    A --> B2
    A --> C1
    A --> C2
    A --> C3
    A --> D1
    A --> E1
    
    C1 --> F1
    C2 --> F1
    C3 --> F1
    D1 --> F2
    D1 --> F1
    E1 --> E2
    E1 --> F1
    
    A --> F3
    
    style A fill:#ff6b6b
    style C1 fill:#4ecdc4
    style C2 fill:#4ecdc4
    style C3 fill:#4ecdc4
    style D1 fill:#ffe66d
    style E1 fill:#95e1d3
```

---

## 8. Error Handling & Retry Logic

```mermaid
flowchart TD
    Start([API Call / Processing Task]) --> Try{Execute}
    
    Try -->|Success| SaveResult[Save Result]
    Try -->|Error| CheckErrorType{Error Type?}
    
    CheckErrorType -->|Network/Timeout| CheckRetries{Retry Count < 3?}
    CheckErrorType -->|Authentication| RefreshCookies[Refresh Session Cookies]
    CheckErrorType -->|API Rate Limit| WaitBackoff[Exponential Backoff Wait]
    CheckErrorType -->|Invalid Data| LogError[Log Error & Continue]
    CheckErrorType -->|Critical Error| FailGracefully[Return Partial Results]
    
    CheckRetries -->|Yes| IncrementRetry[Increment Retry Count]
    CheckRetries -->|No| FailGracefully
    
    IncrementRetry --> Wait[Wait 2^retry seconds]
    Wait --> Try
    
    RefreshCookies --> BrowserAuth{Browser Auth Available?}
    BrowserAuth -->|Yes| RunAutomation[Run Browser Automation]
    BrowserAuth -->|No| UseManualCookies[Use Manual Cookies]
    
    RunAutomation --> Try
    UseManualCookies --> Try
    
    WaitBackoff --> Try
    
    LogError --> ContinueNext[Continue with Next Step]
    ContinueNext --> SaveResult
    
    SaveResult --> NotifyUser[Update Progress/Status]
    FailGracefully --> NotifyUser
    
    NotifyUser --> End([End])
    
    style Start fill:#90EE90
    style End fill:#FFB6C1
    style FailGracefully fill:#FFA07A
    style SaveResult fill:#98FB98
```

---

## 9. Database & Storage Schema

```mermaid
erDiagram
    TENDER ||--o{ ANALYSIS : has
    TENDER ||--o{ DOCUMENT : contains
    ANALYSIS ||--|| REPORT : generates
    ANALYSIS ||--o{ MARKET_DATA : uses
    COMPANY_PROFILE ||--o{ ANALYSIS : influences
    
    TENDER {
        string tender_id PK
        string tender_name
        string reference_number
        string agency_name
        datetime submission_deadline
        float budget_range
        string status
        datetime created_at
    }
    
    DOCUMENT {
        string document_id PK
        string tender_id FK
        string file_name
        string file_type
        string file_path
        text extracted_text
        boolean is_processed
        datetime uploaded_at
    }
    
    ANALYSIS {
        string analysis_id PK
        string tender_id FK
        string status
        int progress_percent
        json requirements
        json financial_eval
        json technical_eval
        json company_fit
        float fit_score
        float suggested_bid_price
        string priority_level
        datetime started_at
        datetime completed_at
    }
    
    REPORT {
        string report_id PK
        string analysis_id FK
        string pdf_path_ar
        string pdf_path_en
        string html_content
        float file_size_mb
        datetime generated_at
    }
    
    MARKET_DATA {
        string data_id PK
        string analysis_id FK
        string search_query
        json search_results
        json pricing_data
        json supplier_info
        datetime fetched_at
    }
    
    COMPANY_PROFILE {
        string profile_id PK
        string company_name
        json classifications
        json certifications
        json capabilities
        json past_projects
        json pricing_strategy
        datetime updated_at
    }
```

---

## 10. Deployment Architecture

```mermaid
graph TB
    subgraph "Client Devices"
        Browser[Web Browser]
        Mobile[Mobile Device]
    end
    
    subgraph "Web Server - Flask"
        NGINX[NGINX Reverse Proxy]
        Gunicorn[Gunicorn WSGI Server]
        Flask[Flask Application]
    end
    
    subgraph "Background Processing"
        Celery[Celery Worker Queue]
        Redis[Redis Message Broker]
    end
    
    subgraph "File Storage"
        Static[Static Files - CSS/JS]
        Downloads[Downloads Folder]
        Reports[Generated Reports]
        Cache[Analysis Cache]
    end
    
    subgraph "External APIs"
        OpenAI_API[OpenAI API]
        Search_API[Search API]
        Etimad_API[Etimad Platform]
    end
    
    subgraph "Configuration"
        EnvVars[Environment Variables]
        CompanyProfile[company_profile.json]
        CookiesFile[cookies_backup.json]
    end
    
    Browser --> NGINX
    Mobile --> NGINX
    
    NGINX --> Gunicorn
    Gunicorn --> Flask
    
    Flask --> Celery
    Celery --> Redis
    
    Flask --> Static
    Flask --> Downloads
    Flask --> Reports
    Flask --> Cache
    
    Celery --> OpenAI_API
    Celery --> Search_API
    Flask --> Etimad_API
    
    Flask --> EnvVars
    Flask --> CompanyProfile
    Flask --> CookiesFile
    
    style Flask fill:#ff9999
    style Celery fill:#99ccff
    style OpenAI_API fill:#ffcc99
```

---

## 11. AI Analysis Multi-Step Process

```mermaid
graph TD
    Start([Start AI Analysis]) --> LoadDocs[Load Extracted Documents]
    
    LoadDocs --> Step1[Step 1: Document Understanding]
    
    Step1 --> SubStep1A[Summarize Requirements]
    Step1 --> SubStep1B[Extract Key Dates]
    Step1 --> SubStep1C[Identify Budget Info]
    Step1 --> SubStep1D[List Technical Requirements]
    Step1 --> SubStep1E[Find Evaluation Criteria]
    
    SubStep1A --> Combine1[Combine Understanding Results]
    SubStep1B --> Combine1
    SubStep1C --> Combine1
    SubStep1D --> Combine1
    SubStep1E --> Combine1
    
    Combine1 --> Step2[Step 2: Internet Research]
    
    Step2 --> SubStep2A[Search Similar Tenders]
    Step2 --> SubStep2B[Find Product Specs]
    Step2 --> SubStep2C[Research Suppliers]
    Step2 --> SubStep2D[Get Market Rates]
    Step2 --> SubStep2E[Find Licensing Info]
    
    SubStep2A --> Combine2[Aggregate Research Data]
    SubStep2B --> Combine2
    SubStep2C --> Combine2
    SubStep2D --> Combine2
    SubStep2E --> Combine2
    
    Combine2 --> Step3[Step 3: Financial Evaluation]
    
    Step3 --> SubStep3A[Calculate Material Costs]
    Step3 --> SubStep3B[Calculate Labor Costs]
    Step3 --> SubStep3C[Add Overhead & Profit]
    Step3 --> SubStep3D[Suggest Bid Price Range]
    Step3 --> SubStep3E[Calculate ROI]
    
    SubStep3A --> Combine3[Financial Analysis Complete]
    SubStep3B --> Combine3
    SubStep3C --> Combine3
    SubStep3D --> Combine3
    SubStep3E --> Combine3
    
    Combine3 --> Step4[Step 4: Technical Evaluation]
    
    Step4 --> SubStep4A[Match to Capabilities]
    Step4 --> SubStep4B[Check Certifications]
    Step4 --> SubStep4C[Assess Feasibility]
    Step4 --> SubStep4D[List Required Team]
    Step4 --> SubStep4E[Identify Risks]
    
    SubStep4A --> Combine4[Technical Analysis Complete]
    SubStep4B --> Combine4
    SubStep4C --> Combine4
    SubStep4D --> Combine4
    SubStep4E --> Combine4
    
    Combine4 --> Step5[Step 5: Company Fit Analysis]
    
    Step5 --> SubStep5A[Compare Requirements]
    Step5 --> SubStep5B[Calculate Fit Score]
    Step5 --> SubStep5C[Identify Gaps]
    Step5 --> SubStep5D[Suggest Partnerships]
    Step5 --> SubStep5E[Evaluate Advantage]
    
    SubStep5A --> Combine5[Fit Analysis Complete]
    SubStep5B --> Combine5
    SubStep5C --> Combine5
    SubStep5D --> Combine5
    SubStep5E --> Combine5
    
    Combine5 --> Step6[Step 6: Generate Recommendations]
    
    Step6 --> SubStep6A[Assign Priority Score]
    Step6 --> SubStep6B[Recommend Bid Price]
    Step6 --> SubStep6C[Estimate Win Probability]
    Step6 --> SubStep6D[Create Implementation Timeline]
    Step6 --> SubStep6E[List Action Items]
    
    SubStep6A --> FinalOutput[Generate Final Report]
    SubStep6B --> FinalOutput
    SubStep6C --> FinalOutput
    SubStep6D --> FinalOutput
    SubStep6E --> FinalOutput
    
    FinalOutput --> End([Analysis Complete])
    
    style Start fill:#90EE90
    style End fill:#FFB6C1
    style Step1 fill:#FFE4B5
    style Step2 fill:#FFE4B5
    style Step3 fill:#FFE4B5
    style Step4 fill:#FFE4B5
    style Step5 fill:#FFE4B5
    style Step6 fill:#FFE4B5
```

---

## 12. Cost Calculation Workflow

```mermaid
flowchart TD
    Start([Begin Cost Calculation]) --> LoadBOQ[Load Bill of Quantities]
    
    LoadBOQ --> HasBOQ{BOQ Available?}
    
    HasBOQ -->|Yes| ParseBOQ[Parse Excel BOQ]
    HasBOQ -->|No| EstimateFromDocs[Estimate from Documents]
    
    ParseBOQ --> ExtractItems[Extract Line Items]
    EstimateFromDocs --> ExtractItems
    
    ExtractItems --> CategorizeItems[Categorize Items]
    
    CategorizeItems --> Materials[Materials & Equipment]
    CategorizeItems --> Labor[Labor & Services]
    CategorizeItems --> Subcontractors[Subcontractor Work]
    CategorizeItems --> Other[Other Costs]
    
    Materials --> SearchMarket1[Search Market Prices]
    Labor --> GetSalaryData[Get Saudi Salary Data]
    Subcontractors --> SearchMarket2[Search Subcontractor Rates]
    Other --> EstimateOther[Estimate Miscellaneous]
    
    SearchMarket1 --> CalcMaterial[Calculate Material Total]
    GetSalaryData --> CalcLabor[Calculate Labor Total]
    SearchMarket2 --> CalcSub[Calculate Subcontractor Total]
    EstimateOther --> CalcOther[Calculate Other Total]
    
    CalcMaterial --> SumDirect[Sum Direct Costs]
    CalcLabor --> SumDirect
    CalcSub --> SumDirect
    CalcOther --> SumDirect
    
    SumDirect --> AddOverhead[Add Overhead 15-20%]
    
    AddOverhead --> AddContingency[Add Contingency 5-10%]
    
    AddContingency --> MinPrice[Minimum Viable Price]
    
    MinPrice --> AddProfit10[+ 10% Profit = Low Bid]
    MinPrice --> AddProfit20[+ 20% Profit = Target Bid]
    MinPrice --> AddProfit30[+ 30% Profit = High Bid]
    
    AddProfit10 --> BidRange[Bid Price Range]
    AddProfit20 --> BidRange
    AddProfit30 --> BidRange
    
    BidRange --> CheckBudget{Within Client Budget?}
    
    CheckBudget -->|Yes| RecommendTarget[Recommend Target Price]
    CheckBudget -->|No| AdjustDown[Adjust to Budget Limit]
    
    AdjustDown --> RecalcProfit[Recalculate Profit Margin]
    RecalcProfit --> RecommendAdjusted[Recommend Adjusted Price]
    
    RecommendTarget --> FinalOutput[Output: Suggested Bid Price]
    RecommendAdjusted --> FinalOutput
    
    FinalOutput --> End([Cost Analysis Complete])
    
    style Start fill:#90EE90
    style End fill:#FFB6C1
    style FinalOutput fill:#98FB98
```

---

## 13. Report Generation Pipeline

```mermaid
sequenceDiagram
    participant Analyzer as AI Analyzer
    participant ReportGen as Report Generator
    participant Template as Jinja2 Template
    participant WeasyPrint as WeasyPrint
    participant FileSystem as File System

    Analyzer->>ReportGen: generate_report(analysis_data)
    
    ReportGen->>ReportGen: Load company profile
    ReportGen->>ReportGen: Prepare template context
    
    par Generate Arabic Report
        ReportGen->>Template: Render analysis_template_ar.html
        Template-->>ReportGen: HTML content (Arabic)
        ReportGen->>ReportGen: Add RTL styling
        ReportGen->>ReportGen: Format Arabic numbers
        ReportGen->>WeasyPrint: Convert HTML to PDF
        WeasyPrint-->>ReportGen: PDF bytes (Arabic)
        ReportGen->>FileSystem: Save tender_analysis_ar.pdf
    and Generate English Report
        ReportGen->>Template: Render analysis_template_en.html
        Template-->>ReportGen: HTML content (English)
        ReportGen->>ReportGen: Add LTR styling
        ReportGen->>WeasyPrint: Convert HTML to PDF
        WeasyPrint-->>ReportGen: PDF bytes (English)
        ReportGen->>FileSystem: Save tender_analysis_en.pdf
    end
    
    ReportGen->>ReportGen: Generate charts & visualizations
    ReportGen->>FileSystem: Save chart images
    
    ReportGen->>ReportGen: Create analysis summary JSON
    ReportGen->>FileSystem: Save analysis_summary.json
    
    ReportGen-->>Analyzer: Return report paths
    
    Analyzer->>Analyzer: Update analysis status
    Analyzer-->>Analyzer: Analysis complete!
```

---

## 14. Current vs. Future Architecture

```mermaid
graph TB
    subgraph "Current System - Phase 1"
        A1[Manual Tender Review]
        A2[Manual Document Reading]
        A3[Manual Cost Estimation]
        A4[Manual Bid Decision]
        
        A1 --> A2
        A2 --> A3
        A3 --> A4
    end
    
    subgraph "AI-Enhanced System - Phase 2"
        B1[Automated Tender Scraping]
        B2[AI Document Analysis]
        B3[AI Cost Calculation]
        B4[AI Recommendations]
        B5[Human Review & Decision]
        
        B1 --> B2
        B2 --> B3
        B3 --> B4
        B4 --> B5
    end
    
    subgraph "Future Advanced System - Phase 3"
        C1[Real-time Tender Monitoring]
        C2[Multi-Model AI Analysis]
        C3[Predictive Pricing Engine]
        C4[Auto-Bid Submission]
        C5[Learning from Outcomes]
        
        C1 --> C2
        C2 --> C3
        C3 --> C4
        C4 --> C5
        C5 --> C1
    end
    
    A4 -.->|Upgrade| B1
    B5 -.->|Upgrade| C1
    
    style A1 fill:#ffcccc
    style B1 fill:#ccffcc
    style C1 fill:#ccccff
```

---

## 15. Integration Points Summary

```mermaid
mindmap
  root((AI Tender<br/>Analysis))
    Frontend
      Flask Templates
      JavaScript/AJAX
      Progress Modals
      Result Display
    Backend
      Flask REST API
      TenderScraper
      Attachment Downloader
      Cookie Manager
    AI Core
      Document Processor
      OCR Engine
      Financial Evaluator
      Technical Evaluator
      Report Generator
    External APIs
      OpenAI GPT-4o
      Tavily Search
      Etimad Platform
    Data Storage
      JSON Cache
      PDF Reports
      Company Profile
      Download Files
    Authentication
      Browser Automation
      Cookie Management
      Session Keep-Alive
```

---

## 16. Performance Optimization Strategy

```mermaid
flowchart LR
    subgraph "Input Optimization"
        A1[Cache Extracted Text]
        A2[Compress Large PDFs]
        A3[Batch API Calls]
    end
    
    subgraph "Processing Optimization"
        B1[Parallel Document Processing]
        B2[Async API Calls]
        B3[Smart Token Management]
        B4[Result Caching]
    end
    
    subgraph "Output Optimization"
        C1[Lazy Report Generation]
        C2[Progressive Download]
        C3[Thumbnail Previews]
    end
    
    subgraph "Cost Optimization"
        D1[API Rate Limiting]
        D2[Token Usage Tracking]
        D3[Cache Search Results]
        D4[Reuse Analysis Components]
    end
    
    A1 --> B1
    A2 --> B1
    A3 --> B2
    
    B1 --> B4
    B2 --> B4
    B3 --> B4
    
    B4 --> C1
    C1 --> C2
    C2 --> C3
    
    B2 --> D1
    B3 --> D2
    B4 --> D3
    D3 --> D4
    
    style B4 fill:#98FB98
    style D3 fill:#FFD700
```

---

## Summary

These diagrams provide a comprehensive view of:

1. **System Architecture** - How all components fit together
2. **Workflows** - Step-by-step process flows
3. **Data Flow** - How information moves through the system
4. **Integration Points** - External services and APIs
5. **User Experience** - Frontend interaction flows
6. **Error Handling** - Resilience and recovery
7. **Storage Schema** - Data organization
8. **Deployment** - Production environment setup

Use these diagrams to:
- Understand the system architecture
- Plan implementation phases
- Communicate with stakeholders
- Debug issues
- Onboard new developers
- Document the system

---

**Document Version**: 1.0  
**Date**: October 20, 2025  
**Last Updated**: October 20, 2025
