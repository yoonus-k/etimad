"""
Test script to fetch and analyze tender attachments API
"""
import requests
import json
from bs4 import BeautifulSoup
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from config import COOKIES

def test_attachments_api():
    """Test the GetAttachmentsViewComponenet API"""
    
    # Example tender ID (encoded)
    tender_id = "tvg6OqxBP7 mkfvdsxrNEw=="
    
    # API endpoint
    url = f"https://tenders.etimad.sa/Tender/GetAttachmentsViewComponenet?tenderIdStr={tender_id}"
    
    print(f"🔍 Fetching attachments for tender: {tender_id}")
    print(f"📡 URL: {url}\n")
    
    # Headers to mimic browser request
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'ar,en-US;q=0.7,en;q=0.3',
        'Referer': 'https://tenders.etimad.sa/',
        'Connection': 'keep-alive',
    }
    
    try:
        # Make request with cookies
        response = requests.get(url, cookies=COOKIES, headers=headers)
        
        print(f"📊 Status Code: {response.status_code}")
        print(f"📄 Content-Type: {response.headers.get('Content-Type', 'N/A')}")
        print(f"📏 Content Length: {len(response.content)} bytes\n")
        
        if response.status_code == 200:
            # Try to parse as JSON
            try:
                data = response.json()
                print("✅ Response is JSON!")
                print(f"📦 JSON Structure:\n{json.dumps(data, indent=2, ensure_ascii=False)[:2000]}\n")
            except:
                # HTML response
                print("📄 Response is HTML")
                print(f"🔍 First 1000 characters:\n{response.text[:1000]}\n")
                
                # Save full HTML for inspection
                with open('attachments_response.html', 'w', encoding='utf-8') as f:
                    f.write(response.text)
                print("💾 Saved full HTML to attachments_response.html\n")
                
                # Look for download links
                if 'href=' in response.text:
                    print("🔗 Found href links in response!")
                    # Extract ALL hrefs
                    import re
                    from bs4 import BeautifulSoup
                    
                    soup = BeautifulSoup(response.text, 'html.parser')
                    
                    # Find all links
                    links = soup.find_all('a', href=True)
                    
                    print(f"\n📎 All Links Found ({len(links)} total):\n")
                    
                    download_links = []
                    for link in links:
                        href = link['href']
                        text = link.get_text(strip=True)
                        
                        # Check if it's a download link
                        if any(keyword in href.lower() for keyword in ['download', 'attachment', 'file', 'document', '.pdf', '.doc', '.xls']):
                            download_links.append({
                                'text': text,
                                'href': href,
                                'full_url': href if href.startswith('http') else f"https://tenders.etimad.sa{href}"
                            })
                            print(f"   📥 {text}")
                            print(f"      URL: {href}\n")
                    
                    if download_links:
                        print(f"\n✅ Found {len(download_links)} download links!")
                        print("\n📋 Summary:")
                        for i, link in enumerate(download_links, 1):
                            print(f"   {i}. {link['text']}")
                    else:
                        print("\n⚠️  No obvious download links found")
                        print("\n🔍 All links in page:")
                        for link in links[:20]:
                            print(f"   • {link.get_text(strip=True)[:50]} → {link['href'][:100]}")
                
        else:
            print(f"❌ Error: Status {response.status_code}")
            print(f"Response: {response.text[:500]}")
            
    except Exception as e:
        print(f"❌ Exception: {str(e)}")

if __name__ == "__main__":
    test_attachments_api()
