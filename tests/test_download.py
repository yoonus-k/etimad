"""
Test the download functionality with a real tender
"""
import sys
sys.path.insert(0, 'D:\\Users\\yoonus\\Documents\\GitHub\\Etimad')

from tender_scraper import TenderScraper
from config import COOKIES

def test_download():
    print("="*60)
    print("Testing Tender Document Download")
    print("="*60)
    
    scraper = TenderScraper(cookies=COOKIES, use_api=True)
    
    # Use the tender ID from your example
    tender_id = "tvg6OqxBP7 mkfvdsxrNEw=="
    tender_name = "تجديد باقات شرائح"
    
    print(f"\n🎯 Testing download for tender: {tender_name}")
    print(f"   Tender ID: {tender_id}")
    
    try:
        result = scraper.download_tender_documents(tender_id)
        print(f"\n✅ SUCCESS! Files downloaded to: {result}")
        
        # List downloaded files
        import os
        if os.path.exists(result):
            files = os.listdir(result)
            print(f"\n📁 Downloaded files ({len(files)}):")
            for f in files:
                file_path = os.path.join(result, f)
                size = os.path.getsize(file_path)
                print(f"   - {f} ({size:,} bytes)")
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_download()
