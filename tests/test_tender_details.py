"""
Test script to fetch tender details which should contain attachment links
"""
import requests
import json
from config import COOKIES

def test_tender_details_api():
    """Test the tender details API to find attachment structure"""
    
    # Test tender ID
    tender_id = "geHwdTka43XRq5Z20a43QA=="
    
    # Try different possible endpoints for tender details
    possible_endpoints = [
        f"https://tenders.etimad.sa/Tender/Details?STenderId={tender_id}",
        f"https://tenders.etimad.sa/Tender/DetailsForSupplier?STenderId={tender_id}",
        f"https://tenders.etimad.sa/Tender/GetTenderDetails?tenderIdStr={tender_id}",
        f"https://tenders.etimad.sa/api/Tender/GetTenderData?tenderIdStr={tender_id}",
    ]
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'Accept-Language': 'ar,en-US;q=0.7,en;q=0.3',
        'X-Requested-With': 'XMLHttpRequest',
        'Referer': 'https://tenders.etimad.sa/',
        'Connection': 'keep-alive',
    }
    
    print(f"🔍 Testing tender ID: {tender_id}\n")
    print("=" * 70)
    
    for url in possible_endpoints:
        print(f"\n📡 Testing: {url}")
        
        try:
            response = requests.get(url, cookies=COOKIES, headers=headers, timeout=10)
            
            print(f"   Status: {response.status_code}")
            print(f"   Content-Type: {response.headers.get('Content-Type', 'N/A')}")
            
            if response.status_code == 200:
                try:
                    # Try JSON
                    data = response.json()
                    print(f"   ✅ JSON Response!")
                    
                    # Look for attachment-related fields
                    if isinstance(data, dict):
                        attachment_keys = [k for k in data.keys() if 'attach' in k.lower() or 'file' in k.lower() or 'document' in k.lower()]
                        if attachment_keys:
                            print(f"   📎 Attachment fields found: {attachment_keys}")
                            for key in attachment_keys:
                                print(f"      {key}: {data[key]}")
                        
                        # Print first level keys
                        print(f"   📋 Top-level keys: {list(data.keys())[:20]}")
                        
                        # Save full response
                        filename = f"tender_details_{url.split('/')[-1].split('?')[0]}.json"
                        with open(filename, 'w', encoding='utf-8') as f:
                            json.dump(data, f, indent=2, ensure_ascii=False)
                        print(f"   💾 Saved to {filename}")
                        
                except:
                    # HTML response
                    print(f"   📄 HTML Response ({len(response.text)} bytes)")
                    if 'attachment' in response.text.lower() or 'مرفق' in response.text:
                        print(f"   ✅ Found attachment-related content!")
                    
            elif response.status_code == 302:
                print(f"   ↪️  Redirect to: {response.headers.get('Location', 'N/A')}")
            else:
                print(f"   ❌ Error response")
                
        except Exception as e:
            print(f"   ❌ Exception: {str(e)}")
        
        print("-" * 70)

if __name__ == "__main__":
    test_tender_details_api()
