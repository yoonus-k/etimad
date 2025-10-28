"""
Tender Attachment Downloader for Etimad
Downloads all tender attachments (كراسة، جدول الكميات، المرفقات) 
"""
import requests
import os
import sys
import json
import re
import shutil
import urllib.parse
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

# Import from root config.py (not src.config package)
from config import COOKIES

class TenderAttachmentDownloader:
    """Downloads tender attachments from Etimad"""
    
    def __init__(self, cookies=None):
        self.cookies = cookies or COOKIES
        self.base_url = "https://tenders.etimad.sa"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'ar,en-US;q=0.7,en;q=0.3',
            'Referer': 'https://tenders.etimad.sa/',
            'Connection': 'keep-alive',
        }
    
    def get_tender_attachments(self, tender_id_str):
        """
        Get list of attachments for a tender
        
        Etimad typically has these attachment types:
        - Booklet (كراسة الشروط والمواصفات)
        - BOQ (جدول الكميات)  
        - Other attachments (مرفقات أخرى)
        """
        
        print(f"\n🔍 Fetching attachments for tender: {tender_id_str}")
        
        # Common Etimad attachment endpoints
        endpoints_to_try = [
            # Attachments view component
            f"{self.base_url}/Tender/GetAttachmentsViewComponenet?tenderIdStr={tender_id_str}",
            
            # Tender details page (may have attachment links)
            f"{self.base_url}/Tender/DetailsForSupplier?STenderId={tender_id_str}",
            
            # Direct attachment download patterns (common in Etimad)
            f"{self.base_url}/Tender/DownloadTenderFiles?tenderIdStr={tender_id_str}",
            f"{self.base_url}/Attachment/GetAttachmentFile?tenderIdStr={tender_id_str}",
        ]
        
        attachments = []
        
        for endpoint in endpoints_to_try:
            try:
                response = requests.get(
                    endpoint, 
                    cookies=self.cookies, 
                    headers=self.headers,
                    timeout=15,
                    allow_redirects=True
                )
                
                if response.status_code == 200:
                    print(f"   ✅ {endpoint.split('/')[-1].split('?')[0]}: {response.status_code}")
                    
                    # Check content type
                    content_type = response.headers.get('Content-Type', '')
                    
                    # If it's a file download, save it
                    if 'application/' in content_type and 'html' not in content_type:
                        filename = self._extract_filename(response) or "attachment"
                        attachments.append({
                            'name': filename,
                            'url': endpoint,
                            'content': response.content,
                            'content_type': content_type
                        })
                        print(f"      📎 Found file: {filename} ({content_type})")
                    
                    # If HTML, parse for download links
                    elif 'html' in content_type:
                        from bs4 import BeautifulSoup
                        soup = BeautifulSoup(response.text, 'html.parser')
                        
                        # Debug: save HTML for inspection
                        debug_file = Path("downloads") / tender_id_str / f"{endpoint.split('/')[-1].split('?')[0]}_debug.html"
                        debug_file.parent.mkdir(parents=True, exist_ok=True)
                        with open(debug_file, 'w', encoding='utf-8') as f:
                            f.write(response.text)
                        print(f"      🐛 Saved debug HTML: {debug_file}")

                        # 1) Find download links (common patterns in Etimad)
                        download_links = soup.find_all('a', href=True)
                        for link in download_links:
                            href = link['href']
                            text = link.get_text(strip=True)

                            # Check if it's a download link
                            if any(keyword in href.lower() for keyword in ['download', 'attachment', 'file']):
                                full_url = href if href.startswith('http') else f"{self.base_url}{href}"
                                attachments.append({
                                    'name': text or 'Unnamed',
                                    'url': full_url,
                                    'content': None  # Will download later
                                })
                                print(f"      🔗 Found link: {text} → {href[:80]}")

                        # 2) Find forms that trigger print/view pages, e.g. PrintConditionsTemplateRfp
                        forms = soup.find_all('form', action=True)
                        for form in forms:
                            action = form.get('action', '')
                            if 'PrintConditionsTemplateRfp' in action:
                                # Usually the form has a hidden input STenderId
                                st_input = form.find('input', {'name': 'STenderId'})
                                if st_input and st_input.get('value'):
                                    st_val = st_input['value']
                                    # Build full URL (GET form)
                                    q = urllib.parse.quote_plus(st_val)
                                    full_url = f"{self.base_url}/Tender/PrintConditionsTemplateRfp?STenderId={q}"
                                    attachments.append({
                                        'name': 'print_conditions.html',
                                        'url': full_url,
                                        'content': None,
                                        'type': 'print_html'
                                    })
                                    print(f"      🖨️ Found printable HTML form -> {full_url}")

                        # 3) Find JS RedirectURL(...) calls which point to /Upload/getfile/{id}:{name}
                        onclick_links = soup.find_all(attrs={"onclick": True})
                        for el in onclick_links:
                            onclick = el.get('onclick', '')
                            m = re.search(r"RedirectURL\('\s*([^']+?)\s*','\s*([^']+?)\s*'\)", onclick)
                            if m:
                                file_id = m.group(1)
                                file_name = m.group(2)
                                # Encode file name safely
                                enc_name = urllib.parse.quote(file_name)
                                full_url = f"{self.base_url}/Upload/getfile/{file_id}:{enc_name}"
                                attachments.append({
                                    'name': file_name,
                                    'url': full_url,
                                    'content': None
                                })
                                print(f"      🔗 Found RedirectURL link: {file_name} -> {full_url}")
                    
            except Exception as e:
                print(f"   ❌ Error with {endpoint.split('/')[-1]}: {str(e)[:100]}")
        
        return attachments
    
    def _extract_filename(self, response):
        """Extract filename from response headers"""
        content_disp = response.headers.get('Content-Disposition', '')
        if 'filename=' in content_disp:
            import re
            match = re.search(r'filename[^;=\n]*=(([\'"]).*?\2|[^;\n]*)', content_disp)
            if match:
                return match.group(1).strip('\'"')
        return None
    
    def download_attachment(self, url, save_path):
        """Download a single attachment"""
        try:
            print(f"   ⬇️  Downloading: {os.path.basename(save_path)}")
            response = requests.get(
                url,
                cookies=self.cookies,
                headers=self.headers,
                timeout=30,
                stream=True
            )
            
            if response.status_code == 200:
                with open(save_path, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)
                
                file_size = os.path.getsize(save_path) / 1024  # KB
                print(f"      ✅ Downloaded: {file_size:.1f} KB")
                return True
            else:
                print(f"      ❌ Failed: Status {response.status_code}")
                return False
                
        except Exception as e:
            print(f"      ❌ Error: {str(e)[:100]}")
            return False
    
    def download_html_as_pdf(self, url, save_folder, base_name="print_conditions"):
        """
        Download HTML page and optionally convert to PDF
        
        Returns:
            (html_path, pdf_path) tuple. pdf_path will be None if conversion fails.
        """
        try:
            print(f"   🖨️  Downloading HTML from: {url[:80]}...")
            response = requests.get(
                url,
                cookies=self.cookies,
                headers=self.headers,
                timeout=30
            )
            
            if response.status_code != 200:
                print(f"      ❌ Failed to fetch HTML: Status {response.status_code}")
                return None, None
            
            # Save HTML
            html_path = save_folder / f"{base_name}.html"
            with open(html_path, 'w', encoding='utf-8') as f:
                f.write(response.text)
            
            html_size = os.path.getsize(html_path) / 1024
            print(f"      ✅ Saved HTML: {html_size:.1f} KB")
            
            # Try to convert to PDF using pdfkit (wkhtmltopdf)
            pdf_path = None
            try:
                import pdfkit
                pdf_path = save_folder / f"{base_name}.pdf"
                
                # Configure pdfkit options
                options = {
                    'enable-local-file-access': None,
                    'encoding': 'UTF-8',
                    'no-stop-slow-scripts': None,
                    'debug-javascript': None,
                }
                
                pdfkit.from_file(str(html_path), str(pdf_path), options=options)
                pdf_size = os.path.getsize(pdf_path) / 1024
                print(f"      ✅ Converted to PDF: {pdf_size:.1f} KB")
                
            except ImportError:
                print(f"      ⚠️  pdfkit not installed. Install with: pip install pdfkit")
                print(f"      ⚠️  Also requires wkhtmltopdf: https://wkhtmltopdf.org/downloads.html")
            except Exception as e:
                print(f"      ⚠️  PDF conversion failed: {str(e)[:100]}")
                print(f"      💡 HTML saved successfully, you can open it in browser")
            
            return html_path, pdf_path
            
        except Exception as e:
            print(f"      ❌ Error: {str(e)[:100]}")
            return None, None
    
    def download_tender_attachments(self, tender_id, tender_id_str, tender_name=""):
        """
        Download all attachments for a tender and save to folder
        
        Args:
            tender_id: Numeric tender ID
            tender_id_str: Encrypted tender ID string
            tender_name: Tender name for folder naming
        
        Returns:
            Path to download folder
        """
        # Create folder: downloads/tender_{id}_{name}
        safe_name = "".join(c for c in tender_name[:50] if c.isalnum() or c in (' ', '-', '_')).strip()
        folder_name = f"tender_{tender_id}_{safe_name}" if safe_name else f"tender_{tender_id}"
        download_folder = Path("downloads") / folder_name
        download_folder.mkdir(parents=True, exist_ok=True)
        
        print(f"\n📁 Download folder: {download_folder}")
        
        # Get attachments
        attachments = self.get_tender_attachments(tender_id_str)
        
        if not attachments:
            print("⚠️  No attachments found")
            return download_folder
        
        print(f"\n📥 Downloading {len(attachments)} attachment(s)...\n")
        
        # Download each attachment
        downloaded = 0
        for i, attachment in enumerate(attachments, 1):
            filename = attachment['name']
            url = attachment['url']
            att_type = attachment.get('type', '')
            
            # If content already downloaded, save it
            if attachment.get('content'):
                save_path = download_folder / filename
                with open(save_path, 'wb') as f:
                    f.write(attachment['content'])
                print(f"   ✅ Saved: {filename}")
                downloaded += 1
            
            # If it's a printable HTML page, download as HTML + PDF
            elif att_type == 'print_html':
                base_name = filename.replace('.html', '')
                html_path, pdf_path = self.download_html_as_pdf(url, download_folder, base_name)
                if html_path:
                    downloaded += 1
            
            # Otherwise download from URL
            else:
                # Generate filename if not provided
                if not filename or filename == 'Unnamed':
                    ext = self._guess_extension(url)
                    filename = f"attachment_{i}{ext}"
                
                save_path = download_folder / filename
                
                if self.download_attachment(url, save_path):
                    downloaded += 1
        
        print(f"\n✅ Downloaded {downloaded}/{len(attachments)} files to: {download_folder}")
        
        return download_folder
    
    def _guess_extension(self, url):
        """Guess file extension from URL"""
        if '.pdf' in url.lower():
            return '.pdf'
        elif '.doc' in url.lower():
            return '.doc'
        elif '.xls' in url.lower():
            return '.xls'
        elif '.zip' in url.lower():
            return '.zip'
        return '.file'


def test_download():
    """Test downloading attachments for a sample tender"""
    downloader = TenderAttachmentDownloader()
    
    # Test tender
    tender_id = 1006927
    tender_id_str = "geHwdTka43XRq5Z20a43QA=="
    tender_name = "تجديد باقات شرائح"
    
    folder = downloader.download_tender_attachments(
        tender_id=tender_id,
        tender_id_str=tender_id_str,
        tender_name=tender_name
    )
    
    print(f"\n📊 Summary:")
    print(f"   Folder: {folder}")
    print(f"   Files: {len(list(folder.glob('*')))} items")
    for file in folder.glob('*'):
        size = file.stat().st_size / 1024
        print(f"      - {file.name} ({size:.1f} KB)")


if __name__ == "__main__":
    test_download()
