#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Quick test for API with cookies"""

from tender_scraper import TenderScraper
import config

try:
    print("Testing Etimad API with authentication cookies...")
    print("Fetching first 3 pages only for testing...\n")
    
    scraper = TenderScraper(cookies=config.COOKIES, use_api=config.USE_API)
    tenders = scraper.fetch_all_tenders(max_pages=3)
    
    print(f"\n{'='*60}")
    print(f"✓ SUCCESS! Fetched {len(tenders)} tenders from API")
    print(f"{'='*60}\n")
    
    if tenders:
        print("First 3 tenders:")
        for i, tender in enumerate(tenders[:3], 1):
            print(f"\n{i}. {tender.get('tenderName', 'N/A')}")
            print(f"   Agency: {tender.get('agencyName', 'N/A')}")
            print(f"   Reference: {tender.get('referenceNumber', 'N/A')}")
    
except Exception as e:
    print(f"\n✗ Error: {e}")
    import traceback
    traceback.print_exc()
