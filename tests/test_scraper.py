#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Test script to debug the tender scraper"""

from tender_scraper import TenderScraper

try:
    # Test with local JSON (default)
    scraper = TenderScraper(use_api=False)
    print("Testing with local JSON file...\n")
    
    tenders = scraper.fetch_all_tenders(max_pages=3)
    print(f"\n✓ Loaded {len(tenders)} tenders")
    
    print("\nTesting filter...")
    filtered = scraper.filter_tenders(tenders)
    print(f"✓ Filtered to {len(filtered)} tenders")
    
    if filtered:
        print("\nFirst tender:")
        print(f"  Name: {filtered[0]['tenderName']}")
        print(f"  Agency: {filtered[0]['agencyName']}")
        print(f"  Reference: {filtered[0]['referenceNumber']}")
        print(f"  Remaining: {filtered[0]['remainingTime']}")
    
    print("\n✓ All tests passed!")
    
except Exception as e:
    print(f"\n✗ Error: {e}")
    import traceback
    traceback.print_exc()
