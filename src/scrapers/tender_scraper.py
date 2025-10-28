import json
import os
import sys
import requests
from datetime import datetime, timedelta
import time
import re
from bs4 import BeautifulSoup
from pathlib import Path

class TenderScraper:
    def __init__(self, cookies=None, use_api=False):
        self.base_url = "https://tenders.etimad.sa"
        self.api_url = "https://tenders.etimad.sa/Tender/AllSupplierTendersAsync"
        self.use_api = use_api
        self.cookies = cookies or {}
        
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'Accept-Language': 'ar,en-US;q=0.9,en;q=0.8',
            'X-Requested-With': 'XMLHttpRequest',
            'Referer': 'https://tenders.etimad.sa/Tender/AllSuppliersTenders'
        }
        self.api_params = {
            'MultipleSearch': '',
            'TenderCategory': '2',
            'TenderActivityId': '9',
            'TenderSubActivityId': '',
            'ReferenceNumber': '',
            'TenderNumber': '',
            'AgencyCode': '',
            'ConditionaBookletRange': '',
            'PublishDateId': '5',
            'LastOfferPresentationDate': '',
            'TenderTypeId': '',
            'TenderAreasIdString': '',
            'FromLastOfferPresentationDateString': '',
            'ToLastOfferPresentationDateString': '',
            'SortDirection': 'DESC',
            'Sort': 'SubmitionDate',
            'PageSize': '24',
            'TenderTabId': '1'
        }
        
    def fetch_page(self, page_number):
        """
        Fetch a single page of tenders from Etimad API
        """
        try:
            params = self.api_params.copy()
            params['PageNumber'] = str(page_number)
            params['_'] = str(int(time.time() * 1000))  # Timestamp
            
            print(f"Fetching page {page_number}...")
            response = requests.get(self.api_url, params=params, headers=self.headers, 
                                  cookies=self.cookies, timeout=30)
            
            print(f"Status Code: {response.status_code}")
            
            if response.status_code == 200:
                # Check if response is HTML (login page) or JSON
                content_type = response.headers.get('Content-Type', '').lower()
                
                if 'text/html' in content_type or response.text.strip().startswith('<!DOCTYPE') or response.text.strip().startswith('<html'):
                    print(f"✗ Page {page_number}: Received HTML instead of JSON - Authentication required")
                    print(f"   Response starts with: {response.text[:100]}")
                    print(f"\n⚠️  Your cookies have expired! Please update them:")
                    print(f"   1. Click '🍪 تحديث الكوكيز' button in the UI")
                    print(f"   2. Paste fresh cookies from the browser extension")
                    print(f"   3. Try fetching tenders again\n")
                    return [], 0
                
                try:
                    data = response.json()
                    tenders = data.get('data', [])
                    total_count = data.get('totalCount', 0)
                    print(f"✓ Page {page_number}: {len(tenders)} tenders (Total: {total_count})")
                    return tenders, total_count
                except json.JSONDecodeError as je:
                    print(f"✗ JSON Error on page {page_number}: {je}")
                    print(f"   Response type: {content_type}")
                    print(f"   Response preview: {response.text[:500]}")
                    print(f"\n⚠️  Response is not valid JSON. Cookies may be expired.")
                    return [], 0
            elif response.status_code == 302:
                print(f"✗ Page {page_number}: Redirect detected - Authentication required")
                print(f"Location: {response.headers.get('Location', 'N/A')[:100]}")
                return [], 0
            else:
                print(f"✗ Page {page_number}: HTTP {response.status_code}")
                print(f"Response: {response.text[:200]}")
                return [], 0
                
        except Exception as e:
            print(f"✗ Error fetching page {page_number}: {e}")
            import traceback
            traceback.print_exc()
            return [], 0
    
    def fetch_all_tenders(self, max_pages=100):
        """
        Fetch all tenders - either from Etimad API with pagination or from local JSON
        """
        # Try to use API if enabled and authenticated
        if self.use_api:
            return self._fetch_from_api(max_pages)
        else:
            return self._fetch_from_json()
    
    def _fetch_from_json(self):
        """
        Fetch tenders from local JSON file
        """
        try:
            data_file = Path(__file__).parent.parent / 'data' / 'all_tenders.json'
            with open(data_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                tenders = data.get('data', [])
                print(f"✓ Loaded {len(tenders)} tenders from local JSON file")
                return tenders
        except FileNotFoundError:
            print("✗ all_tenders.json not found in data/ folder")
            return []
        except Exception as e:
            print(f"✗ Error reading JSON file: {e}")
            return []
    
    def _fetch_from_api(self, max_pages=100):
        """
        Fetch all tenders from Etimad API with pagination (1 to max_pages)
        """
        all_tenders = []
        total_count = 0
        
        print(f"\n{'='*60}")
        print(f"Starting to fetch tenders from Etimad API...")
        print(f"{'='*60}\n")
        
        for page in range(1, max_pages + 1):
            tenders, count = self.fetch_page(page)
            
            if not tenders:
                if page == 1:
                    print(f"\n⚠ No tenders found. This might be due to:")
                    print(f"  - Missing authentication cookies")
                    print(f"  - API access restrictions")
                    print(f"  - Network issues")
                    print(f"\nFalling back to local JSON file...\n")
                    return self._fetch_from_json()
                else:
                    print(f"\nNo more tenders found at page {page}. Stopping.")
                break
            
            all_tenders.extend(tenders)
            total_count = count
            
            # Small delay to avoid overwhelming the server
            time.sleep(1)
            
            # Stop if we've fetched all available tenders
            if len(all_tenders) >= total_count:
                print(f"\n✓ Fetched all available tenders ({len(all_tenders)}/{total_count})")
                break
        
        print(f"\n{'='*60}")
        print(f"Finished! Total tenders collected: {len(all_tenders)}")
        print(f"{'='*60}\n")
        
        return all_tenders
    
    def get_tender_classification(self, tender_id_str):
        """
        Get tender classification (التصنيف) from relations details endpoint
        Returns: dict with classification info or None
        """
        try:
            url = f"{self.base_url}/Tender/GetRelationsDetailsViewComponenet"
            params = {'tenderIdStr': tender_id_str}
            
            print(f"🔍 Fetching classification for tender: {tender_id_str}")
            print(f"   URL: {url}")
            print(f"   Params: {params}")
            
            response = requests.get(url, params=params, headers=self.headers, 
                                  cookies=self.cookies, timeout=10)
            
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Find ALL "مجال التصنيف" sections (can be multiple)
                classifications = []
                bundles = []
                
                # Find all list items
                all_items = soup.find_all('li', class_='list-group-item')
                print(f"   Found {len(all_items)} list items")
                
                for item in all_items:
                    title_div = item.find('div', class_='etd-item-title')
                    info_div = item.find('div', class_='etd-item-info')
                    
                    if title_div and info_div:
                        title = title_div.get_text(strip=True)
                        value = info_div.get_text(strip=True)
                        
                        # Debug: print what we find
                        if 'التصنيف' in title or 'الحزمة' in title:
                            print(f"   📋 {title}: {value}")
                        
                        # Collect classification fields
                        if 'مجال التصنيف' in title:
                            if value and value not in classifications:
                                classifications.append(value)
                                print(f"   ✅ Added classification: {value}")
                        
                        # Collect bundle names
                        elif 'الحزمة' in title:
                            if value and value not in bundles:
                                bundles.append(value)
                                print(f"   ✅ Added bundle: {value}")
                
                # Build response
                print(f"   📊 Total classifications found: {len(classifications)}")
                print(f"   📦 Total bundles found: {len(bundles)}")
                
                if classifications:
                    # Join all unique classifications
                    classification_text = ', '.join(classifications)
                    requires_classification = 'غير مطلوب' not in classification_text
                    
                    result = {
                        'classification': classification_text,
                        'requires_classification': requires_classification,
                        'bundles': bundles if bundles else []
                    }
                    
                    print(f"   ✅ Returning: {result}")
                    return result
                else:
                    # No classification found - check if it says "غير مطلوب"
                    print(f"   ⚠️  No classifications found")
                    return {
                        'classification': 'غير محدد',
                        'requires_classification': False,
                        'bundles': []
                    }
            else:
                print(f"Failed to fetch classification for {tender_id_str}: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"Error fetching classification for {tender_id_str}: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def get_tender_details(self, tender_id, group_id):
        """
        Get detailed information about a specific tender
        """
        # For now, read from local JSON file
        try:
            data_file = Path(__file__).parent.parent / 'data' / 'tender_info.json'
            with open(data_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            return []
    
    def requires_classification(self, tender_id, group_id):
        """
        Check if tender requires تصنيف (classification)
        Returns True if classification is required, False otherwise
        
        TODO: Need to identify the correct field/API that indicates classification requirement
        For now, returning False to show all tenders
        """
        try:
            tender_details = self.get_tender_details(tender_id, group_id)
            
            # Search for classification indicators in the tender details
            for detail in tender_details:
                # Check if there's a field indicating classification requirement
                if 'requiresClassification' in detail:
                    return detail['requiresClassification']
                
                # Check in criteria names
                if 'tenderCriteria' in detail:
                    for criteria in detail.get('tenderCriteria', []):
                        criteria_name = criteria.get('name', '')
                        if 'تصنيف' in criteria_name or 'classification' in criteria_name.lower():
                            return True
                        
                        # Check child criteria recursively
                        for child in criteria.get('childCriteria', []):
                            child_name = child.get('name', '')
                            if 'تصنيف' in child_name or 'classification' in child_name.lower():
                                return True
            
            # For testing: return False to show all tenders
            # Change this logic once we know where the classification flag is
            return False
        except Exception as e:
            print(f"Error checking classification for {tender_id}: {e}")
            return False
    
    def filter_tenders(self, tenders):
        """
        Filter out tenders that require classification
        """
        filtered = []
        
        for tender in tenders:
            # Extract tender IDs from the actual API structure
            tender_id = tender.get('tenderIdString', '')
            group_id = tender.get('groupIdStr', '')  # May not exist in main list
            
            # Skip if requires classification
            if not self.requires_classification(tender_id, group_id):
                filtered.append(self.format_tender_data(tender))
        
        return filtered
    
    def format_tender_data(self, tender):
        """
        Format tender data for display using actual API field names
        """
        # Use the pre-calculated remaining time from API
        remaining_days = tender.get('remainingDays', 0)
        remaining_hours = tender.get('remainingHours', 0)
        
        if remaining_days or remaining_hours:
            remaining_time = f'{remaining_days} يوم و {remaining_hours} ساعة'
        else:
            remaining_time = 'منتهي'
        
        return {
            'tenderName': tender.get('tenderName', 'N/A'),
            'agencyName': tender.get('agencyName', 'N/A'),
            'remainingTime': remaining_time,
            'referenceNumber': tender.get('referenceNumber', 'N/A'),
            'tenderType': tender.get('tenderTypeName', 'N/A'),
            'documentPrice': tender.get('condetionalBookletPrice', 0),
            'tenderId': tender.get('tenderIdString', ''),
            'tenderIdString': tender.get('tenderIdString', ''),  # Add this field for JavaScript
            'tenderNumber': tender.get('tenderNumber', 'N/A'),
            'branchName': tender.get('branchName', 'N/A'),
            'lastOfferDate': tender.get('lastOfferPresentationDate', 'N/A')
        }
    
    def calculate_remaining_time(self, end_date_str):
        """
        Calculate remaining time in days and hours
        """
        if not end_date_str:
            return 'N/A'
        
        try:
            # Parse date (adjust format based on actual API response)
            # Common formats: "2025-10-15T23:59:59" or "/Date(1728950400000)/"
            if '/Date(' in end_date_str:
                timestamp = int(end_date_str.split('(')[1].split(')')[0]) / 1000
                end_date = datetime.fromtimestamp(timestamp)
            else:
                end_date = datetime.fromisoformat(end_date_str.replace('Z', ''))
            
            now = datetime.now()
            delta = end_date - now
            
            if delta.total_seconds() < 0:
                return 'منتهي'
            
            days = delta.days
            hours = delta.seconds // 3600
            
            return f'{days} يوم و {hours} ساعة'
        except Exception as e:
            return 'N/A'
    
    def download_tender_documents(self, tender_id, tender_name='', reference_number=''):
        """
        Download tender documents (كراسة، جدول الكميات، المرفقات)
        1. Fetch attachments from GetAttachmentsViewComponenet API
        2. Parse the HTML response to extract download links
        3. Download each file to the tender folder
        
        Args:
            tender_id: The tender ID string
            tender_name: Optional tender name for folder naming
            reference_number: Optional reference number for folder naming
        """
        import re
        from urllib.parse import urljoin, unquote
        from bs4 import BeautifulSoup
        
        print(f"\n📥 Downloading documents for tender: {tender_id}")
        
        # Create folder name with tender name and reference number if provided
        if tender_name and reference_number:
            # Clean the tender name to be filesystem-safe
            safe_name = "".join(c if c.isalnum() or c in (' ', '-', '_', 'ا', 'ب', 'ت', 'ث', 'ج', 'ح', 'خ', 'د', 'ذ', 'ر', 'ز', 'س', 'ش', 'ص', 'ض', 'ط', 'ظ', 'ع', 'غ', 'ف', 'ق', 'ك', 'ل', 'م', 'ن', 'ه', 'و', 'ي', 'ى', 'أ', 'إ', 'آ', 'ة', 'ئ', 'ء', 'ؤ') else '_' for c in tender_name)
            safe_name = safe_name.strip()[:100]  # Limit length to 100 chars
            folder_name = f"{safe_name}_{reference_number}"
        else:
            folder_name = tender_id
        
        # Create downloads folder if it doesn't exist
        root_dir = Path(__file__).parent.parent
        downloads_folder = os.path.join(str(root_dir), 'downloads', folder_name)
        os.makedirs(downloads_folder, exist_ok=True)
        print(f"📁 Created folder: {downloads_folder}")
        
        try:
            # Fetch attachments page
            attachments_url = f"{self.base_url}/Tender/GetAttachmentsViewComponenet"
            params = {'tenderIdStr': tender_id}
            
            print(f"🌐 Fetching attachments from: {attachments_url}")
            print(f"   Parameters: {params}")
            
            response = requests.get(
                attachments_url,
                params=params,
                cookies=self.cookies,
                headers=self.headers,
                timeout=30
            )
            
            if response.status_code != 200:
                raise Exception(f"Failed to fetch attachments. Status: {response.status_code}")
            
            print(f"✅ Received attachments page ({len(response.text)} chars)")
            
            # Parse HTML to extract download links
            soup = BeautifulSoup(response.text, 'html.parser')
            
            download_links = []
            
            # 1. Find the main conditions booklet form (كراسة الشروط والمواصفات)
            from urllib.parse import quote
            form = soup.find('form', action='PrintConditionsTemplateRfp')
            if form:
                tender_id_input = form.find('input', {'name': 'STenderId'})
                if tender_id_input:
                    tender_id_value = tender_id_input.get('value', '')
                    # URL encode the tender ID for the query parameter
                    encoded_id = quote(tender_id_value)
                    download_links.append({
                        'url': f'/Tender/PrintConditionsTemplateRfp?STenderId={encoded_id}',
                        'text': 'كراسة_الشروط_والمواصفات.pdf',
                        'type': 'form',
                        'post_data': {'STenderId': tender_id_value}  # Keep original for POST
                    })
            
            # 2. Find all supporting files with onclick="RedirectURL(...)"
            for link in soup.find_all('a', onclick=True):
                onclick = link.get('onclick', '')
                # Extract fileId and fileName from: RedirectURL('idd_XXX','filename.pdf')
                match = re.search(r"RedirectURL\('([^']+)','([^']+)'\)", onclick)
                if match:
                    file_id = match.group(1)
                    file_name = match.group(2)
                    download_links.append({
                        'url': f'/Upload/getfile/{file_id}:{file_name}',
                        'text': file_name,
                        'type': 'redirect'
                    })
            
            print(f"🔗 Found {len(download_links)} potential download links")
            
            if not download_links:
                print("⚠️  No download links found in attachments page")
                # Save the HTML for debugging
                debug_path = os.path.join(downloads_folder, 'attachments_page_debug.html')
                with open(debug_path, 'w', encoding='utf-8') as f:
                    f.write(response.text)
                print(f"   Saved debug HTML to: {debug_path}")
            
            # Download each file
            downloaded_files = []
            for idx, link_info in enumerate(download_links, 1):
                try:
                    file_url = link_info['url']
                    file_text = link_info['text']
                    link_type = link_info.get('type', 'unknown')
                    
                    # Make URL absolute if it's relative
                    if not file_url.startswith('http'):
                        file_url = self.base_url + file_url
                    
                    print(f"\n📄 [{idx}/{len(download_links)}] Downloading: {file_text}")
                    print(f"   URL: {file_url}")
                    
                    # For form submissions, use POST
                    if link_type == 'form':
                        post_data = link_info.get('post_data', {})
                        file_response = requests.post(
                            file_url.split('?')[0] if '?' in file_url else file_url,  # Remove query string for POST
                            data=post_data,
                            cookies=self.cookies,
                            headers=self.headers,
                            timeout=60,
                            stream=True
                        )
                    else:
                        # For direct links, use GET
                        file_response = requests.get(
                            file_url,
                            cookies=self.cookies,
                            headers=self.headers,
                            timeout=60,
                            stream=True
                        )
                    
                    if file_response.status_code != 200:
                        print(f"   ❌ Failed: Status {file_response.status_code}")
                        continue
                    
                    # Use the filename from link_info (already extracted from HTML)
                    filename = file_text
                    
                    # If filename doesn't have extension, try to get from Content-Disposition
                    if '.' not in filename:
                        if 'content-disposition' in file_response.headers:
                            cd = file_response.headers['content-disposition']
                            filenames = re.findall(r'filename[*]?=([^;]+)', cd)
                            if filenames:
                                extracted = filenames[0].strip('"\'')
                                if '.' in extracted:
                                    filename = extracted
                        
                        # If still no extension, guess from content-type
                        if '.' not in filename:
                            content_type = file_response.headers.get('content-type', '')
                            ext = '.pdf' if 'pdf' in content_type else \
                                  '.doc' if 'word' in content_type else \
                                  '.xls' if 'excel' in content_type else '.pdf'
                            filename = filename + ext
                    
                    # Save the file
                    file_path = os.path.join(downloads_folder, filename)
                    
                    # Write file in chunks
                    with open(file_path, 'wb') as f:
                        for chunk in file_response.iter_content(chunk_size=8192):
                            f.write(chunk)
                    
                    file_size = os.path.getsize(file_path)
                    print(f"   ✅ Saved: {filename} ({file_size:,} bytes)")
                    downloaded_files.append(filename)
                    
                except Exception as e:
                    print(f"   ❌ Error downloading file: {e}")
                    continue
            
            print(f"\n✅ Download complete! {len(downloaded_files)} files saved to: {downloads_folder}")
            return downloads_folder
            
        except Exception as e:
            print(f"❌ Error in download_tender_documents: {e}")
            import traceback
            traceback.print_exc()
            raise Exception(f"فشل تحميل المستندات: {str(e)}")

