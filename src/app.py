from flask import Flask, render_template, jsonify, send_file, request, make_response
import json
import os
import sys
import requests
from datetime import datetime
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.tender_scraper import TenderScraper
import config
from io import BytesIO

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

if __name__ == '__main__':
    # Exclude downloads folder from reloader to prevent restart during file downloads
    import os
    extra_files = []
    extra_dirs = []
    
    app.run(debug=True, port=5000, extra_files=extra_files, extra_dirs=extra_dirs)
