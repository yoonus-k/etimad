from flask import Flask, render_template, jsonify, send_file, request, make_response
import json
import os
import sys
import requests
from datetime import datetime
from pathlib import Path
import threading
import time
import traceback

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import scrapers
from src.scrapers import TenderScraper

# Import config
import config
from io import BytesIO

# Import Phase 1-3 modules for AI analysis
from src.config import CompanyContext
from src.processors import DocumentProcessor
from src.core import AIAnalyzer
from src.evaluators import FinancialEvaluator, TechnicalEvaluator, MarketResearcher
from src.reports import ReportGenerator

# Import Phase 5 modules for optimization
from src.core import CacheManager, CostTracker

# Import WeasyPrint for PDF generation
try:
    from weasyprint import HTML as WeasyHTML
    WEASYPRINT_AVAILABLE = True
    print("✅ WeasyPrint loaded successfully")
except ImportError:
    WEASYPRINT_AVAILABLE = False
    WeasyHTML = None
    print("⚠️  WeasyPrint not available. PDF download will not work.")

# Import CORS
from flask_cors import CORS

# Get the parent directory (project root) for templates and static files
root_dir = Path(__file__).parent.parent

app = Flask(__name__, 
            template_folder=str(root_dir / 'templates'),
            static_folder=str(root_dir / 'static'))

# Configure app to not watch downloads folder
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0

# Enable CORS for all routes
CORS(app)

def update_config_file_with_cookies(cookies):
    """
    Update the config.py file with new cookies
    Preserves other settings and only updates the COOKIES dictionary
    """
    import re
    
    config_path = Path(__file__).parent.parent / 'config.py'
    
    # Read current config
    with open(config_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Format cookies as Python dictionary
    cookie_lines = ['COOKIES = {']
    for key, value in sorted(cookies.items()):
        # Escape single quotes in values
        escaped_value = value.replace("'", "\\'")
        cookie_lines.append(f"    '{key}': '{escaped_value}',")
    cookie_lines.append('}')
    
    new_cookies_block = '\n'.join(cookie_lines)
    
    # Replace COOKIES = {...} block (handles multi-line)
    pattern = r'COOKIES\s*=\s*\{[^}]*\}'
    
    if re.search(pattern, content, re.DOTALL):
        # Replace existing COOKIES block
        content = re.sub(pattern, new_cookies_block, content, flags=re.DOTALL)
    else:
        # Append if not found
        content += f'\n\n# Auto-updated cookies\n{new_cookies_block}\n'
    
    # Write back to config.py
    with open(config_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✅ config.py updated with {len(cookies)} cookies")

# Get cookies (smart approach: file cache → automation → manual)
def get_cookies():
    """
    Get cookies with smart fallback:
    1. Try loading from cookies_backup.json (fastest)
    2. If enabled, try browser automation
    3. Fall back to manual config.COOKIES
    """
    # Try loading from file first (fastest)
    try:
        if os.path.exists('cookies_backup.json'):
            print("📁 Loading cookies from file...")
            with open('cookies_backup.json', 'r', encoding='utf-8') as f:
                data = json.load(f)
                cookies = data.get('cookies', {})
                if cookies:
                    timestamp = data.get('timestamp', 'unknown')
                    print(f"   ✅ Loaded {len(cookies)} cookies from {timestamp}")
                    return cookies
    except Exception as e:
        print(f"   ⚠️  Could not load from file: {e}")
    
    # Try browser automation if enabled
    try:
        import browser_config
        if browser_config.USE_BROWSER_AUTOMATION:
            if browser_config.ETIMAD_USERNAME and browser_config.ETIMAD_PASSWORD:
                from cookie_manager import EtimadBrowserAutomation
                print("🤖 Running browser automation...")
                
                automation = EtimadBrowserAutomation(
                    username=browser_config.ETIMAD_USERNAME,
                    password=browser_config.ETIMAD_PASSWORD,
                    headless=browser_config.HEADLESS_BROWSER
                )
                
                cookies = automation.login_and_get_cookies()
                if cookies:
                    return cookies
            else:
                print("   ⚠️  Automation enabled but credentials missing")
    except Exception as e:
        print(f"   ⚠️  Browser automation failed: {e}")
    
    # Fall back to manual cookies from config
    print("📋 Using manual cookies from config.py")
    return config.COOKIES

# Initialize scraper with configuration
cookies = get_cookies()
scraper = TenderScraper(cookies=cookies, use_api=config.USE_API)

# Keep-alive tracking
last_keep_alive_time = None
keep_alive_status = "starting"

# Analysis tracking
analysis_tasks = {}  # {tender_id: {'status': 'processing', 'progress': 0, 'step': 'Extracting documents', 'result': None, 'error': None}}
analysis_lock = threading.Lock()

# Initialize analysis modules
try:
    company_context = CompanyContext()
    document_processor = DocumentProcessor()
    ai_analyzer = AIAnalyzer()
    report_generator = ReportGenerator()
    cache_manager = CacheManager()
    cost_tracker = CostTracker()
    print("✅ AI Analysis modules initialized")
    print("✅ AI Analyzer (Claude) initialized")
    print("✅ Cache Manager initialized")
    print("✅ Cost Tracker initialized")
except Exception as e:
    print(f"⚠️ Failed to initialize AI modules: {e}")
    company_context = None
    document_processor = None
    ai_analyzer = None
    report_generator = None
    cache_manager = None
    cost_tracker = None

# Keep-alive function to maintain session
def keep_session_alive():
    """
    Background task that pings Etimad every minute to keep session active
    Prevents cookies from expiring due to inactivity
    """
    global last_keep_alive_time, keep_alive_status
    
    while True:
        try:
            time.sleep(60)  # Wait 1 minute
            
            if not scraper.cookies:
                print("⚠️  Keep-alive: No cookies available")
                keep_alive_status = "no_cookies"
                continue
            
            # Make a lightweight request to keep session alive
            # Using the main tenders page as it's lightweight
            url = "https://tenders.etimad.sa/Tender/AllTendersForVisitors"
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            }
            
            response = requests.get(url, cookies=scraper.cookies, headers=headers, timeout=10)
            
            if response.status_code == 200:
                last_keep_alive_time = datetime.now()
                keep_alive_status = "active"
                print(f"🔄 Keep-alive: Session refreshed at {last_keep_alive_time.strftime('%H:%M:%S')}")
            else:
                keep_alive_status = f"error_{response.status_code}"
                print(f"⚠️  Keep-alive: Got status {response.status_code}")
                
        except Exception as e:
            keep_alive_status = "error"
            print(f"⚠️  Keep-alive error: {e}")

# Start keep-alive thread
keep_alive_thread = threading.Thread(target=keep_session_alive, daemon=True)
keep_alive_thread.start()
print("✅ Session keep-alive started (pings every 60 seconds)")

@app.route('/')
def index():
    """Main page to display tenders"""
    return render_template('index.html')

@app.route('/api/tenders')
def get_tenders():
    """API endpoint to fetch and filter tenders"""
    try:
        # Get max_pages from query parameter (default from config)
        max_pages = request.args.get('max_pages', config.MAX_PAGES, type=int)
        
        # Fetch all tenders (from API or local JSON based on config)
        tenders = scraper.fetch_all_tenders(max_pages=max_pages)
        print(f"Fetched {len(tenders)} tenders")
        
        # Check if we got tenders from API or fell back to JSON
        if config.USE_API and len(tenders) == 0:
            # API returned nothing, likely authentication issue
            return jsonify({
                'success': False,
                'error': 'فشل جلب المنافسات من الموقع. الكوكيز قد تكون منتهية الصلاحية.',
                'action': 'update_cookies',
                'count': 0,
                'tenders': []
            })
        
        # Filter tenders (exclude those requiring تصنيف)
        filtered_tenders = scraper.filter_tenders(tenders)
        print(f"Filtered to {len(filtered_tenders)} tenders")
        
        return jsonify({
            'success': True,
            'count': len(filtered_tenders),
            'tenders': filtered_tenders,
            'source': 'API' if config.USE_API else 'Local JSON'
        })
    except Exception as e:
        print(f"Error in get_tenders: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/tender/<tender_id>/download')
def download_tender_documents(tender_id):
    """Download all tender documents"""
    try:
        print(f"\n🔽 Download request for tender: {tender_id}")
        
        # Get tender name and reference number from request
        tender_name = request.args.get('tenderName', '')
        reference_number = request.args.get('referenceNumber', '')
        
        print(f"   Tender Name: {tender_name[:50]}..." if len(tender_name) > 50 else f"   Tender Name: {tender_name}")
        print(f"   Reference: {reference_number}")
        
        # Call the download function with error handling
        folder_path = scraper.download_tender_documents(
            tender_id, 
            tender_name=tender_name,
            reference_number=reference_number
        )
        
        print(f"✅ Download completed successfully")
        
        return jsonify({
            'success': True,
            'message': f'تم تحميل المستندات بنجاح',
            'folder': folder_path
        })
        
    except requests.exceptions.Timeout as e:
        error_msg = 'انتهت مهلة الاتصال. الرجاء المحاولة مرة أخرى'
        print(f"⏱️ Timeout error: {e}")
        return jsonify({
            'success': False,
            'error': error_msg
        }), 504
        
    except requests.exceptions.ConnectionError as e:
        error_msg = 'فشل الاتصال بالخادم. تحقق من الاتصال بالإنترنت'
        print(f"🔌 Connection error: {e}")
        return jsonify({
            'success': False,
            'error': error_msg
        }), 503
        
    except Exception as e:
        error_msg = str(e)
        print(f"❌ Download error: {error_msg}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': error_msg
        }), 500

@app.route('/api/tender/<path:tender_id_str>/download-pdf', methods=['GET'])
def download_tender_pdf(tender_id_str):
    """Download tender conditions template as PDF and save to downloads folder"""
    try:
        print(f"🔍 PDF Download request for tender: {tender_id_str}")
        
        # Get tender info from query params for folder naming
        tender_name = request.args.get('tenderName', '').strip()
        reference_number = request.args.get('referenceNumber', '').strip()
        
        if not WEASYPRINT_AVAILABLE:
            error_msg = 'WeasyPrint is not installed. Please install it first: pip install weasyprint'
            print(f"❌ {error_msg}")
            return jsonify({
                'success': False,
                'error': error_msg
            }), 500
        
        # Fetch HTML from Etimad (server-side to avoid CORS)
        import requests
        rfp_url = f"https://tenders.etimad.sa/Tender/PrintConditionsTemplateRfp?STenderId={tender_id_str}"
        
        print(f"📄 Fetching RFP HTML from: {rfp_url}")
        print(f"   Using {len(scraper.cookies)} cookies")
        print(f"   Tender: {tender_name}")
        print(f"   Reference: {reference_number}")
        
        # Add headers to mimic a real browser request
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }
        
        response = requests.get(rfp_url, cookies=scraper.cookies, headers=headers, timeout=30)
        
        print(f"   Response status: {response.status_code}")
        
        if response.status_code != 200:
            error_msg = f'Failed to fetch HTML: HTTP {response.status_code}'
            print(f"❌ {error_msg}")
            return jsonify({
                'success': False,
                'error': error_msg
            }), 500
        
        html_content = response.text
        
        print(f"   HTML length: {len(html_content)} bytes")
        
        if not html_content or len(html_content) < 100:
            error_msg = 'HTML content is empty or too short'
            print(f"❌ {error_msg}")
            return jsonify({
                'success': False,
                'error': error_msg
            }), 400
        
        print(f"✅ Fetched HTML successfully")
        
        # Save HTML directly (skip PDF conversion issues)
        print("� Saving HTML file...")
        html_buffer = BytesIO(html_content.encode('utf-8'))
        file_extension = 'html'
        print(f"✅ HTML ready ({len(html_content)} bytes)")
        
        # Determine folder name (same logic as download endpoint)
        if tender_name and reference_number:
            # Clean strings for safe folder naming
            clean_name = "".join(c if c.isalnum() or c in (' ', '_', '-', 'ا', 'ب', 'ت', 'ث', 'ج', 'ح', 'خ', 'د', 'ذ', 'ر', 'ز', 'س', 'ش', 'ص', 'ض', 'ط', 'ظ', 'ع', 'غ', 'ف', 'ق', 'ك', 'ل', 'م', 'ن', 'ه', 'و', 'ي', 'أ', 'إ', 'آ', 'ة', 'ى', 'ئ', 'ء', 'ؤ') else '_' for c in tender_name)
            clean_ref = "".join(c if c.isalnum() or c in ('_', '-') else '_' for c in reference_number)
            # Limit folder name length
            if len(clean_name) > 50:
                clean_name = clean_name[:50]
            folder_name = f"{clean_name}_{clean_ref}"
        else:
            folder_name = f"tender_{tender_id_str}"
        
        # Create downloads folder structure
        downloads_dir = Path(__file__).parent.parent / 'downloads'
        tender_folder = downloads_dir / folder_name
        tender_folder.mkdir(parents=True, exist_ok=True)
        
        # Save HTML to the folder
        html_filename = f"كراسة_الشروط_والمواصفات.{file_extension}"
        html_path = tender_folder / html_filename
        
        print(f"💾 Saving HTML to: {html_path}")
        with open(html_path, 'wb') as f:
            f.write(html_buffer.getvalue())
        
        print(f"✅ HTML saved successfully!")
        
        return jsonify({
            'success': True,
            'message': 'تم تحميل وحفظ كراسة الشروط بنجاح (HTML)',
            'folder': folder_name,
            'file': html_filename,
            'path': str(html_path)
        })
        
    except Exception as e:
        print(f"❌ Error generating PDF: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/tender/<tender_id>/delete', methods=['DELETE'])
def delete_tender(tender_id):
    """Delete a tender from the list (UI only - doesn't modify JSON file)"""
    try:
        return jsonify({
            'success': True,
            'message': 'تم حذف المنافسة من القائمة'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/keep-alive-status', methods=['GET'])
def get_keep_alive_status():
    """Get the current keep-alive status"""
    try:
        global last_keep_alive_time, keep_alive_status
        
        response = {
            'status': keep_alive_status,
            'last_ping': last_keep_alive_time.strftime('%Y-%m-%d %H:%M:%S') if last_keep_alive_time else None,
            'cookies_count': len(scraper.cookies) if scraper.cookies else 0
        }
        
        return jsonify(response)
    except Exception as e:
        return jsonify({
            'status': 'error',
            'error': str(e)
        }), 500

@app.route('/api/update-cookies', methods=['POST'])
def update_cookies():
    """Update cookies manually from user input"""
    try:
        from datetime import datetime
        import requests
        
        data = request.get_json()
        cookie_string = data.get('cookies', '').strip()
        
        if not cookie_string:
            return jsonify({
                'success': False,
                'error': 'يرجى إدخال الكوكيز'
            }), 400
        
        print("🔍 Parsing cookies...")
        
        # Parse cookies - supports multiple formats
        cookies = {}
        try:
            # Check if it's a Python dictionary format (from browser extension)
            if 'COOKIES' in cookie_string and '{' in cookie_string:
                print("   📋 Detected Python dictionary format")
                # Extract the dictionary part
                import re
                dict_match = re.search(r'\{([^}]+)\}', cookie_string, re.DOTALL)
                if dict_match:
                    dict_content = dict_match.group(1)
                    # Parse key-value pairs
                    for line in dict_content.split('\n'):
                        line = line.strip().rstrip(',')
                        if ':' in line:
                            # Match: 'key': 'value'
                            match = re.search(r"'([^']+)'\s*:\s*'([^']*(?:\\'[^']*)*)'", line)
                            if match:
                                key = match.group(1)
                                value = match.group(2).replace("\\'", "'")  # Unescape quotes
                                cookies[key] = value
            else:
                print("   🍪 Detected cookie string format")
                # Standard cookie string format: "name=value; name2=value2"
                for item in cookie_string.split(';'):
                    item = item.strip()
                    if '=' in item:
                        name, value = item.split('=', 1)
                        cookies[name.strip()] = value.strip()
        except Exception as e:
            return jsonify({
                'success': False,
                'error': f'خطأ في تحليل الكوكيز: {str(e)}'
            }), 400
        
        if not cookies:
            return jsonify({
                'success': False,
                'error': 'لم يتم العثور على كوكيز صالحة'
            }), 400
        
        print(f"✅ Parsed {len(cookies)} cookies")
        
        # Test if cookies work with API
        print("🧪 Testing cookies with API...")
        try:
            url = "https://tenders.etimad.sa/Tender/AllSupplierTendersAsync"
            params = {'PageSize': 1, 'PageNumber': 1, 'Sort': 'OffersDueDate'}
            response = requests.get(url, cookies=cookies, params=params, timeout=10)
            
            if response.status_code != 200:
                return jsonify({
                    'success': False,
                    'error': 'الكوكيز غير صالحة. تأكد من نسخ الكوكيز الصحيحة'
                }), 400
            
            data_response = response.json()
            total_tenders = data_response.get('total', 0)
            print(f"✅ API test passed! {total_tenders} tenders available")
        except Exception as e:
            return jsonify({
                'success': False,
                'error': f'خطأ في اختبار الكوكيز: {str(e)}'
            }), 400
        
        # Save cookies to file
        cookie_data = {
            'cookies': cookies,
            'timestamp': datetime.now().isoformat(),
            'method': 'manual_paste'
        }
        
        with open('cookies_backup.json', 'w', encoding='utf-8') as f:
            json.dump(cookie_data, f, indent=2, ensure_ascii=False)
        
        print("💾 Cookies saved to cookies_backup.json")
        
        # Update config.py file
        try:
            update_config_file_with_cookies(cookies)
            print("✅ Updated config.py file")
        except Exception as e:
            print(f"⚠️  Failed to update config.py: {e}")
        
        # Update config
        config.COOKIES = cookies
        
        # Update the scraper with new cookies
        global scraper
        scraper = TenderScraper(cookies=cookies, use_api=config.USE_API)
        print("✅ Updated scraper with new cookies")
        
        return jsonify({
            'success': True,
            'message': f'تم تحديث الكوكيز بنجاح! وجدنا {total_tenders} منافسة',
            'cookie_count': len(cookies),
            'total_tenders': total_tenders,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/tender/<tender_id_str>/classification')
def get_tender_classification(tender_id_str):
    """Get classification (التصنيف) for a specific tender"""
    try:
        classification_info = scraper.get_tender_classification(tender_id_str)
        
        if classification_info:
            return jsonify({
                'success': True,
                'classification': classification_info['classification'],
                'requires_classification': classification_info['requires_classification'],
                'bundles': classification_info.get('bundles', [])
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Failed to fetch classification'
            }), 500
            
    except Exception as e:
        print(f"Error getting classification: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/proxy/etimad', methods=['GET', 'POST'])
def proxy_etimad():
    """
    Proxy endpoint to bypass CORS issues when fetching from Etimad
    Accepts a 'url' parameter and forwards the request with proper cookies
    """
    try:
        import requests
        
        # Get the target URL from query parameter
        target_url = request.args.get('url')
        
        if not target_url:
            return jsonify({
                'success': False,
                'error': 'Missing url parameter'
            }), 400
        
        # Validate it's an Etimad URL for security
        if not target_url.startswith('https://tenders.etimad.sa'):
            return jsonify({
                'success': False,
                'error': 'Only Etimad URLs are allowed'
            }), 403
        
        print(f"🔄 Proxying request to: {target_url}")
        
        # Prepare headers to mimic browser request
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'ar,en-US;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }
        
        # Forward the request with cookies
        if request.method == 'POST':
            response = requests.post(
                target_url, 
                cookies=scraper.cookies, 
                headers=headers,
                data=request.get_data(),
                timeout=30
            )
        else:
            response = requests.get(
                target_url, 
                cookies=scraper.cookies, 
                headers=headers,
                timeout=30
            )
        
        print(f"   Status: {response.status_code}, Content-Length: {len(response.content)}")
        
        # Return the response with proper headers
        return response.content, response.status_code, {
            'Content-Type': response.headers.get('Content-Type', 'text/html; charset=utf-8'),
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
            'Access-Control-Allow-Headers': 'Content-Type'
        }
        
    except requests.exceptions.Timeout:
        return jsonify({
            'success': False,
            'error': 'Request timeout'
        }), 504
    except Exception as e:
        print(f"❌ Proxy error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# =============================================================================
# PHASE 4: AI ANALYSIS ENDPOINTS
# =============================================================================

def analyze_tender_task(tender_id, tender_folder):
    """
    Background task to analyze a tender
    This runs in a separate thread to avoid blocking the Flask app
    Phase 5: Added caching and cost tracking
    """
    global analysis_tasks
    
    # Initialize cost tracking
    total_cost = 0.0
    costs_breakdown = {
        'anthropic': {'input_tokens': 0, 'output_tokens': 0, 'cost': 0},
        'tavily': {'num_searches': 0, 'cost': 0},
        'total': 0
    }
    
    try:
        print(f"\n🤖 Starting AI analysis for tender: {tender_id}")
        print(f"   Folder: {tender_folder}")
        
        # Update status
        with analysis_lock:
            analysis_tasks[tender_id]['status'] = 'processing'
            analysis_tasks[tender_id]['progress'] = 10
            analysis_tasks[tender_id]['step'] = 'جاري استخراج النصوص من المستندات...'
        
        # Step 1: Extract text from all documents in folder (with caching)
        print("📄 Step 1: Extracting documents...")
        
        # Try to get from cache first
        folder_path = Path(tender_folder)
        extracted_data = None
        if cache_manager:
            extracted_data = cache_manager.get_document_cache(folder_path)
            if extracted_data:
                print("✅ Using cached document extraction")
        
        # If not in cache, process documents
        if not extracted_data:
            extracted_data = document_processor.process_folder(tender_folder)
            # Cache the results
            if cache_manager:
                cache_manager.set_document_cache(folder_path, extracted_data)
        
        with analysis_lock:
            analysis_tasks[tender_id]['progress'] = 25
            analysis_tasks[tender_id]['step'] = 'جاري تحليل المتطلبات...'
        
        # Prepare tender data structure
        tender_data = {
            'tender_id': tender_id,
            'folder_path': tender_folder,
            'extracted_text': extracted_data.get('combined_text', ''),
            'documents': extracted_data.get('documents', []),
            'excel_data': extracted_data.get('excel_data', [])
        }
        
        # Step 1.5: AI-Powered Initial Analysis
        print("🤖 Step 1.5: AI-powered tender analysis...")
        with analysis_lock:
            analysis_tasks[tender_id]['progress'] = 30
            analysis_tasks[tender_id]['step'] = 'جاري التحليل الذكي للمنافسة...'
        
        ai_summary = None
        if ai_analyzer and ai_analyzer.client:
            try:
                # Get company context summary
                company_summary = json.dumps(company_context.profile, ensure_ascii=False) if company_context else "No company profile"
                
                # Use AI to analyze tender
                ai_summary = ai_analyzer.analyze_tender_summary(
                    tender_data['extracted_text'],
                    company_summary
                )
                
                print(f"✅ AI Analysis complete")
                print(f"   Recommendation: {ai_summary.get('recommendation', 'N/A')}")
                print(f"   Confidence: {ai_summary.get('confidence', 'N/A')}")
                
                # Track tokens for cost calculation
                if ai_summary.get('usage'):
                    costs_breakdown['anthropic']['input_tokens'] += ai_summary['usage'].get('input_tokens', 0)
                    costs_breakdown['anthropic']['output_tokens'] += ai_summary['usage'].get('output_tokens', 0)
                    
            except Exception as e:
                print(f"⚠️ AI Analysis failed: {e}")
                ai_summary = None
        else:
            print("⚠️ AI Analyzer not available, using rule-based analysis")
        
        # Step 2: Financial Analysis (enhanced with AI insights)
        print("💰 Step 2: Financial evaluation...")
        with analysis_lock:
            analysis_tasks[tender_id]['progress'] = 45
            analysis_tasks[tender_id]['step'] = 'جاري التقييم المالي...'
        
        financial_evaluator = FinancialEvaluator(company_context)
        
        # Pass AI insights to financial evaluator if available
        if ai_summary and 'financial_insights' in ai_summary:
            tender_data['ai_financial_insights'] = ai_summary['financial_insights']
            
        financial_eval = financial_evaluator.evaluate_tender(tender_data)
        
        # Step 3: Technical Analysis (enhanced with AI insights)
        print("🔧 Step 3: Technical evaluation...")
        with analysis_lock:
            analysis_tasks[tender_id]['progress'] = 60
            analysis_tasks[tender_id]['step'] = 'جاري التقييم الفني...'
        
        technical_evaluator = TechnicalEvaluator(company_context)
        
        # Pass AI insights to technical evaluator if available
        if ai_summary and 'technical_requirements' in ai_summary:
            tender_data['ai_technical_requirements'] = ai_summary['technical_requirements']
            
        technical_eval = technical_evaluator.evaluate_tender(tender_data)
        
        # Step 4: Market Research
        print("📊 Step 4: Market research...")
        with analysis_lock:
            analysis_tasks[tender_id]['progress'] = 70
            analysis_tasks[tender_id]['step'] = 'جاري البحث في السوق...'
        
        market_researcher = MarketResearcher()
        market_eval = market_researcher.research_tender(tender_data)
        
        # Step 5: Generate Recommendation (AI-enhanced)
        print("💡 Step 5: Generating recommendation...")
        with analysis_lock:
            analysis_tasks[tender_id]['progress'] = 85
            analysis_tasks[tender_id]['step'] = 'جاري إنشاء التوصيات...'
        
        # Calculate recommendation using both AI and rule-based logic
        should_bid = (
            technical_eval['feasibility']['score'] >= 70 and
            financial_eval['profitability']['profit_margin_percentage'] >= 10
        )
        
        # Use AI recommendation if available, otherwise use rule-based
        if ai_summary and 'recommendation' in ai_summary:
            recommendation = {
                'should_bid': ai_summary['recommendation'] in ['PROCEED', 'CONSIDER'],
                'confidence': ai_summary.get('confidence', 'Medium'),
                'priority': ai_summary.get('priority', 'Medium'),
                'key_strengths': ai_summary.get('key_strengths', ['قدرة فنية عالية']),
                'key_concerns': ai_summary.get('key_concerns', []),
                'ai_insights': ai_summary.get('analysis_summary', '')
            }
            print(f"✅ Using AI-powered recommendation: {ai_summary['recommendation']}")
        else:
            # Fallback to rule-based recommendation
            recommendation = {
                'should_bid': should_bid,
                'confidence': 'High' if technical_eval['feasibility']['score'] >= 80 else 'Medium',
                'priority': 'High' if (should_bid and financial_eval['profitability']['profit_margin_percentage'] >= 15) else ('Medium' if should_bid else 'Low'),
                'key_strengths': ['قدرة فنية عالية', 'خبرة سابقة في مشاريع مماثلة'],
                'key_concerns': [risk['description'] for risk in technical_eval.get('risks', [])[:3]]
            }
            print("⚠️ Using rule-based recommendation (AI not available)")
        
        # Step 6: Generate Report
        print("📄 Step 6: Generating reports...")
        with analysis_lock:
            analysis_tasks[tender_id]['progress'] = 95
            analysis_tasks[tender_id]['step'] = 'جاري إنشاء التقرير...'
        
        # Prepare complete analysis data
        analysis_data = {
            'tender': tender_data,
            'financial_evaluation': financial_eval,  # Changed from 'financial'
            'technical_evaluation': technical_eval,  # Changed from 'technical'
            'market': market_eval,
            'company': company_context.profile if company_context else {},
            'recommendation': recommendation
        }
        
        # Generate reports (Arabic and English)
        try:
            ar_report_path = report_generator.generate_report(analysis_data, language='ar', format='html')
            en_report_path = report_generator.generate_report(analysis_data, language='en', format='html')
            print(f"✅ Reports generated: {ar_report_path}, {en_report_path}")
        except Exception as e:
            print(f"⚠️ Report generation error: {e}")
            ar_report_path = None
            en_report_path = None
        
        # Save analysis results
        analysis_result = {
            'tender_id': tender_id,
            'timestamp': datetime.now().isoformat(),
            'financial': {
                'total_cost': financial_eval['cost_breakdown']['total_cost'],
                'recommended_bid': financial_eval['pricing_analysis']['recommended_bid'],
                'profit_margin': financial_eval['profitability']['profit_margin_percentage'],
                'expected_profit': financial_eval['profitability']['expected_profit']
            },
            'technical': {
                'feasibility_score': technical_eval['feasibility']['score'],
                'feasibility_level': technical_eval['feasibility']['level'],
                'capability_match': technical_eval['capability_match'].get('overall_score', 0),
                'risk_count': len(technical_eval.get('risks', []))
            },
            'market': {
                'similar_tenders': len(market_eval.get('similar_tenders', [])),
                'suppliers_found': len(market_eval.get('suppliers', []))
            },
            'recommendation': recommendation,
            'reports': {
                'arabic': str(ar_report_path) if ar_report_path else None,
                'english': str(en_report_path) if en_report_path else None
            }
        }
        
        # Track API costs (Phase 5) - Now using REAL token counts from AI
        if cost_tracker:
            try:
                # Use actual token counts from AI analysis if available
                if costs_breakdown['anthropic']['input_tokens'] == 0:
                    # Fallback: estimate if AI wasn't used
                    costs_breakdown['anthropic']['input_tokens'] = len(tender_data['extracted_text']) // 4
                    costs_breakdown['anthropic']['output_tokens'] = 3000
                
                costs_breakdown['anthropic']['cost'] = cost_tracker.calculate_anthropic_cost(
                    costs_breakdown['anthropic']['input_tokens'],
                    costs_breakdown['anthropic']['output_tokens'],
                    'sonnet_4'
                )
                
                costs_breakdown['tavily']['num_searches'] = len(market_eval.get('search_queries', []))
                costs_breakdown['tavily']['cost'] = cost_tracker.calculate_tavily_cost(
                    costs_breakdown['tavily']['num_searches']
                )
                
                costs_breakdown['total'] = costs_breakdown['anthropic']['cost'] + costs_breakdown['tavily']['cost']
                
                # Track the analysis
                cost_summary = cost_tracker.track_analysis(tender_id, costs_breakdown)
                
                # Add cost info to analysis result
                analysis_result['cost_info'] = {
                    'analysis_cost': cost_summary['analysis_cost'],
                    'monthly_total': cost_summary['monthly_total'],
                    'budget_warning': cost_summary.get('warning'),
                    'anthropic_tokens': {
                        'input': costs_breakdown['anthropic']['input_tokens'],
                        'output': costs_breakdown['anthropic']['output_tokens']
                    }
                }
                
                print(f"💰 Analysis cost: ${cost_summary['analysis_cost']:.4f}")
                print(f"   Anthropic tokens: {costs_breakdown['anthropic']['input_tokens']:,} input + {costs_breakdown['anthropic']['output_tokens']:,} output")
                print(f"   Tavily searches: {costs_breakdown['tavily']['num_searches']}")
                if cost_summary.get('warning'):
                    print(f"⚠️ {cost_summary['warning']['message']}")
            except Exception as e:
                print(f"⚠️ Cost tracking error: {e}")
        
        # Save to JSON file
        analysis_file = Path(tender_folder) / 'analysis_result.json'
        with open(analysis_file, 'w', encoding='utf-8') as f:
            json.dump(analysis_result, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Analysis complete for {tender_id}")
        
        # Update status to complete
        with analysis_lock:
            analysis_tasks[tender_id]['status'] = 'completed'
            analysis_tasks[tender_id]['progress'] = 100
            analysis_tasks[tender_id]['step'] = 'تم التحليل بنجاح!'
            analysis_tasks[tender_id]['result'] = analysis_result
            analysis_tasks[tender_id]['error'] = None
        
    except Exception as e:
        error_msg = str(e)
        print(f"❌ Analysis error for {tender_id}: {error_msg}")
        traceback.print_exc()
        
        with analysis_lock:
            analysis_tasks[tender_id]['status'] = 'error'
            analysis_tasks[tender_id]['error'] = error_msg
            analysis_tasks[tender_id]['step'] = f'خطأ: {error_msg}'

@app.route('/api/tender/<tender_id>/analyze', methods=['POST'])
def analyze_tender(tender_id):
    """
    Start AI analysis for a tender
    Requires the tender to be downloaded first
    """
    try:
        # Try to get JSON data, but don't fail if Content-Type is wrong
        try:
            data = request.get_json(force=True, silent=True) or {}
        except:
            data = {}
        
        tender_name = data.get('tenderName', '')
        reference_number = data.get('referenceNumber', '')
        
        # Find the tender folder
        downloads_dir = Path(__file__).parent.parent / 'downloads'
        
        # Try to find folder by reference number or name
        tender_folder = None
        for folder in downloads_dir.iterdir():
            if folder.is_dir():
                if reference_number and reference_number in folder.name:
                    tender_folder = folder
                    break
                elif tender_id in folder.name:
                    tender_folder = folder
                    break
        
        if not tender_folder or not tender_folder.exists():
            return jsonify({
                'success': False,
                'error': 'لم يتم العثور على مجلد المنافسة. يرجى تحميل المستندات أولاً'
            }), 404
        
        # Check if analysis is already in progress
        with analysis_lock:
            if tender_id in analysis_tasks and analysis_tasks[tender_id]['status'] == 'processing':
                return jsonify({
                    'success': False,
                    'error': 'التحليل قيد التنفيذ بالفعل'
                }), 400
            
            # Initialize analysis task
            analysis_tasks[tender_id] = {
                'status': 'queued',
                'progress': 0,
                'step': 'في الانتظار...',
                'result': None,
                'error': None,
                'started_at': datetime.now().isoformat()
            }
        
        # Start analysis in background thread
        thread = threading.Thread(
            target=analyze_tender_task,
            args=(tender_id, str(tender_folder)),
            daemon=True
        )
        thread.start()
        
        return jsonify({
            'success': True,
            'message': 'تم بدء التحليل',
            'tender_id': tender_id
        })
        
    except Exception as e:
        print(f"❌ Error starting analysis: {e}")
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/tender/<tender_id>/analysis-status', methods=['GET'])
def get_analysis_status(tender_id):
    """
    Get the current status of an analysis
    """
    try:
        with analysis_lock:
            if tender_id not in analysis_tasks:
                return jsonify({
                    'success': False,
                    'error': 'لم يتم العثور على تحليل لهذه المنافسة'
                }), 404
            
            task = analysis_tasks[tender_id]
            
            return jsonify({
                'success': True,
                'status': task['status'],
                'progress': task['progress'],
                'step': task['step'],
                'error': task.get('error'),
                'started_at': task.get('started_at')
            })
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/tender/<tender_id>/analysis-result', methods=['GET'])
def get_analysis_result(tender_id):
    """
    Get the analysis result for a completed analysis
    """
    try:
        with analysis_lock:
            if tender_id not in analysis_tasks:
                return jsonify({
                    'success': False,
                    'error': 'لم يتم العثور على تحليل لهذه المنافسة'
                }), 404
            
            task = analysis_tasks[tender_id]
            
            if task['status'] != 'completed':
                return jsonify({
                    'success': False,
                    'error': 'التحليل لم يكتمل بعد',
                    'status': task['status']
                }), 400
            
            return jsonify({
                'success': True,
                'result': task['result']
            })
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/downloads', methods=['GET'])
def get_downloads():
    """
    Get all downloaded tenders from the downloads folder
    """
    try:
        downloads_dir = Path(__file__).parent.parent / 'downloads'
        
        if not downloads_dir.exists():
            return jsonify({
                'success': True,
                'count': 0,
                'tenders': []
            })
        
        tenders = []
        for folder in downloads_dir.iterdir():
            if folder.is_dir():
                # Get folder info
                tender_info = {
                    'folder_name': folder.name,
                    'folder_path': str(folder),
                    'created_at': datetime.fromtimestamp(folder.stat().st_ctime).isoformat(),
                    'modified_at': datetime.fromtimestamp(folder.stat().st_mtime).isoformat(),
                }
                
                # Count files in folder
                files = list(folder.glob('*'))
                tender_info['file_count'] = len([f for f in files if f.is_file()])
                
                # Check for analysis result
                analysis_file = folder / 'analysis_result.json'
                if analysis_file.exists():
                    try:
                        with open(analysis_file, 'r', encoding='utf-8') as f:
                            analysis_data = json.load(f)
                            tender_info['analyzed'] = True
                            tender_info['tender_id'] = analysis_data.get('tender_id')
                            tender_info['analysis_date'] = analysis_data.get('timestamp')
                            tender_info['recommendation'] = analysis_data.get('recommendation', {})
                            tender_info['reports'] = analysis_data.get('reports', {})
                    except Exception as e:
                        print(f"Error reading analysis file {analysis_file}: {e}")
                        tender_info['analyzed'] = False
                else:
                    tender_info['analyzed'] = False
                
                # Try to extract tender_id from folder name (format: name_tenderid)
                if not tender_info.get('tender_id'):
                    parts = folder.name.split('_')
                    if len(parts) > 1:
                        tender_info['tender_id'] = parts[-1]
                
                tenders.append(tender_info)
        
        # Sort by modified date (newest first)
        tenders.sort(key=lambda x: x.get('modified_at', ''), reverse=True)
        
        return jsonify({
            'success': True,
            'count': len(tenders),
            'tenders': tenders
        })
        
    except Exception as e:
        print(f"Error getting downloads: {e}")
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/downloads/<path:folder_name>/delete', methods=['DELETE'])
def delete_download(folder_name):
    """
    Delete a downloaded tender folder
    """
    try:
        downloads_dir = Path(__file__).parent.parent / 'downloads'
        folder_path = downloads_dir / folder_name
        
        if not folder_path.exists():
            return jsonify({
                'success': False,
                'error': 'المجلد غير موجود'
            }), 404
        
        # Delete the folder and all its contents
        import shutil
        shutil.rmtree(folder_path)
        
        return jsonify({
            'success': True,
            'message': f'تم حذف المجلد: {folder_name}'
        })
        
    except Exception as e:
        print(f"Error deleting folder: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/analyses/list', methods=['GET'])
def list_analyses():
    """
    List all analyses with their status
    """
    try:
        downloads_dir = Path(__file__).parent.parent / 'downloads'
        
        analyses = []
        for folder in downloads_dir.iterdir():
            if folder.is_dir():
                analysis_file = folder / 'analysis_result.json'
                if analysis_file.exists():
                    try:
                        with open(analysis_file, 'r', encoding='utf-8') as f:
                            analysis_data = json.load(f)
                            analyses.append({
                                'folder_name': folder.name,
                                'tender_id': analysis_data.get('tender_id'),
                                'timestamp': analysis_data.get('timestamp'),
                                'recommendation': analysis_data.get('recommendation', {}).get('priority', 'Unknown'),
                                'has_report': analysis_data.get('reports', {}).get('arabic') is not None
                            })
                    except Exception as e:
                        print(f"Error reading analysis file {analysis_file}: {e}")
        
        # Sort by timestamp (newest first)
        analyses.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
        
        return jsonify({
            'success': True,
            'count': len(analyses),
            'analyses': analyses
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# ===========================
# Phase 5: Optimization Endpoints
# ===========================

@app.route('/api/batch-analyze', methods=['POST'])
def batch_analyze():
    """
    Analyze multiple tenders at once
    Accepts a list of tender IDs to analyze
    """
    try:
        data = request.get_json() or {}
        tender_ids = data.get('tender_ids', [])
        
        if not tender_ids:
            return jsonify({
                'success': False,
                'error': 'لم يتم تحديد منافسات للتحليل'
            }), 400
        
        downloads_dir = Path(__file__).parent.parent / 'downloads'
        started = []
        failed = []
        
        for tender_id in tender_ids:
            try:
                # Find tender folder
                tender_folder = None
                for folder in downloads_dir.iterdir():
                    if folder.is_dir() and tender_id in folder.name:
                        tender_folder = folder
                        break
                
                if not tender_folder:
                    failed.append({
                        'tender_id': tender_id,
                        'error': 'لم يتم العثور على المجلد'
                    })
                    continue
                
                # Check if already in progress
                with analysis_lock:
                    if tender_id in analysis_tasks and analysis_tasks[tender_id]['status'] == 'processing':
                        failed.append({
                            'tender_id': tender_id,
                            'error': 'التحليل قيد التنفيذ بالفعل'
                        })
                        continue
                    
                    # Initialize analysis task
                    analysis_tasks[tender_id] = {
                        'status': 'queued',
                        'progress': 0,
                        'step': 'في الانتظار...',
                        'result': None,
                        'error': None,
                        'started_at': datetime.now().isoformat()
                    }
                
                # Start analysis in background thread
                thread = threading.Thread(
                    target=analyze_tender_task,
                    args=(tender_id, str(tender_folder)),
                    daemon=True
                )
                thread.start()
                
                started.append(tender_id)
                
                # Small delay between starting threads to avoid overwhelming
                time.sleep(0.5)
                
            except Exception as e:
                failed.append({
                    'tender_id': tender_id,
                    'error': str(e)
                })
        
        return jsonify({
            'success': True,
            'started': started,
            'failed': failed,
            'message': f'تم بدء تحليل {len(started)} منافسة'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/cache/stats', methods=['GET'])
def get_cache_stats():
    """
    Get cache statistics
    """
    try:
        if not cache_manager:
            return jsonify({
                'success': False,
                'error': 'Cache manager not initialized'
            }), 500
        
        stats = cache_manager.get_cache_stats()
        
        return jsonify({
            'success': True,
            'stats': stats
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/cache/clear', methods=['POST'])
def clear_cache():
    """
    Clear cache
    Accepts cache_type parameter: 'documents', 'search', 'analysis', 'all'
    """
    try:
        if not cache_manager:
            return jsonify({
                'success': False,
                'error': 'Cache manager not initialized'
            }), 500
        
        data = request.get_json() or {}
        cache_type = data.get('cache_type', 'all')
        
        if cache_type not in ['documents', 'search', 'analysis', 'all']:
            return jsonify({
                'success': False,
                'error': 'Invalid cache_type. Must be: documents, search, analysis, or all'
            }), 400
        
        cache_manager.clear_cache(cache_type)
        
        return jsonify({
            'success': True,
            'message': f'تم مسح {cache_type} cache'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/costs/summary', methods=['GET'])
def get_cost_summary():
    """
    Get cost tracking summary
    """
    try:
        if not cost_tracker:
            return jsonify({
                'success': False,
                'error': 'Cost tracker not initialized'
            }), 500
        
        # Get monthly and total summary
        month = request.args.get('month')  # Optional
        
        if month:
            summary = cost_tracker.get_monthly_summary(month)
        else:
            summary = cost_tracker.get_total_summary()
        
        return jsonify({
            'success': True,
            'summary': summary
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/costs/recent', methods=['GET'])
def get_recent_costs():
    """
    Get recent analysis costs
    """
    try:
        if not cost_tracker:
            return jsonify({
                'success': False,
                'error': 'Cost tracker not initialized'
            }), 500
        
        limit = int(request.args.get('limit', 10))
        recent = cost_tracker.get_recent_analyses(limit)
        
        return jsonify({
            'success': True,
            'analyses': recent
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/costs/budget', methods=['POST'])
def set_budget_limit():
    """
    Set monthly budget limit
    """
    try:
        if not cost_tracker:
            return jsonify({
                'success': False,
                'error': 'Cost tracker not initialized'
            }), 500
        
        data = request.get_json() or {}
        limit = data.get('limit')
        
        if not limit or limit <= 0:
            return jsonify({
                'success': False,
                'error': 'يرجى تحديد حد ميزانية صالح'
            }), 400
        
        cost_tracker.set_budget_limit(float(limit))
        
        return jsonify({
            'success': True,
            'message': f'تم تحديد حد الميزانية إلى ${limit:.2f}/شهر'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/data/tender_analyses/<path:filename>')
def serve_report(filename):
    """
    Serve analysis report files
    """
    try:
        reports_dir = Path(__file__).parent.parent / 'data' / 'tender_analyses'
        file_path = reports_dir / filename
        
        if not file_path.exists():
            return jsonify({
                'success': False,
                'error': 'الملف غير موجود'
            }), 404
        
        return send_file(file_path, mimetype='text/html')
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

if __name__ == '__main__':
    # Run Flask app
    app.run(debug=True, port=5000)
