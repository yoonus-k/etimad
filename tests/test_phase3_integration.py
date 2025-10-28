"""
Phase 3 Integration Test - Report Generation
Tests the complete report generation pipeline with all Phase 1 & 2 modules
"""

import os
import sys
from pathlib import Path

# Fix Unicode encoding for Windows console
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from company_context import CompanyContext
from document_processor import DocumentProcessor
from financial_evaluator import FinancialEvaluator
from technical_evaluator import TechnicalEvaluator
from market_researcher import MarketResearcher
from report_generator import ReportGenerator


def test_full_analysis_pipeline():
    """Test complete analysis pipeline from tender to report"""
    
    print("=" * 80)
    print("PHASE 3 INTEGRATION TEST - COMPLETE PIPELINE")
    print("=" * 80)
    
    # Sample tender data
    tender_data = {
        'tender_id': '251039009436',
        'title': 'تجديد رخص نظام إدارة المحتوى وتقديم خدمات الدعم الفني',
        'title_en': 'Content Management System License Renewal and Technical Support',
        'description': 'تجديد رخص نظام إدارة المحتوى ليزرفيش لمدة سنة وتقديم خدمات الدعم الفني والصيانة',
        'description_en': 'Renewal of Laser Fish CMS licenses for one year with technical support and maintenance',
        'category': 'Information Technology',
        'budget': 500000,
        'duration_months': 12,
        'requirements': {
            'technical': [
                'خبرة 5 سنوات في إدارة أنظمة المحتوى',
                'شهادات فنية في تقنية المعلومات',
                'فريق دعم فني متفرغ'
            ],
            'certifications': [
                'ISO 27001',
                'ISO 9001'
            ],
            'resources': {
                'team_size': 5,
                'positions': [
                    'مدير مشروع',
                    'مهندس نظم',
                    'فني دعم فني'
                ]
            }
        }
    }
    
    print(f"\n📋 Tender: {tender_data['title_en']}")
    print(f"💰 Budget: SAR {tender_data['budget']:,.0f}")
    print(f"⏱️  Duration: {tender_data['duration_months']} months")
    
    # Initialize all modules
    print("\n" + "=" * 80)
    print("PHASE 1: Initializing Foundation Modules")
    print("=" * 80)
    
    company = CompanyContext()
    print("✅ Company Context loaded")
    
    doc_processor = DocumentProcessor()
    print("✅ Document Processor ready")
    
    # Phase 2: Analysis modules
    print("\n" + "=" * 80)
    print("PHASE 2: Running Analysis Modules")
    print("=" * 80)
    
    financial = FinancialEvaluator(company)
    print("\n💰 Financial Analysis:")
    
    # Use the main evaluation method
    financial_eval = financial.evaluate_tender(tender_data)
    print(f"   Total Cost: SAR {financial_eval['cost_breakdown']['total_cost']:,.2f}")
    print(f"   Recommended Bid: SAR {financial_eval['pricing_analysis']['recommended_bid']:,.2f}")
    print(f"   Profit Margin: {financial_eval['profitability']['profit_margin_percentage']:.1f}%")
    
    technical = TechnicalEvaluator(company)
    print("\n🔧 Technical Assessment:")
    
    # Use the main evaluation method
    technical_eval = technical.evaluate_tender(tender_data)
    print(f"   Feasibility: {technical_eval['feasibility']['level']} ({technical_eval['feasibility']['score']:.1f}%)")
    print(f"   Capability Match: {technical_eval['capability_match']['overall_score']:.1f}%")
    
    market = MarketResearcher()
    print("\n📊 Market Research:")
    market_data = market.research_tender(tender_data)
    print(f"   Similar Tenders: {len(market_data['similar_tenders'])}")
    print(f"   Suppliers Found: {len(market_data['suppliers'])}")
    
    # Phase 3: Report Generation
    print("\n" + "=" * 80)
    print("PHASE 3: Generating Reports")
    print("=" * 80)
    
    report_gen = ReportGenerator()
    
    # Prepare complete analysis data
    analysis_data = {
        'tender': tender_data,
        'financial': financial_eval,
        'technical': technical_eval,
        'market': market_data,
        'company': company.profile,
        'recommendation': {
            'should_bid': (
                technical_eval['feasibility']['score'] >= 70 and 
                financial_eval['profitability']['profit_margin_percentage'] >= 10
            ),
            'confidence': 'High' if technical_eval['feasibility']['score'] >= 80 else 'Medium',
            'key_strengths': [
                'قدرة فنية عالية',
                'خبرة سابقة في مشاريع مماثلة',
                'فريق فني مؤهل'
            ],
            'key_concerns': technical_eval.get('risks', [])[:3]
        }
    }
    
    # Generate Arabic report
    print("\n📄 Generating Arabic Report...")
    ar_report = report_gen.generate_report(
        analysis_data,
        language='ar',
        format='html'
    )
    print(f"✅ Arabic Report: {ar_report}")
    
    # Generate English report
    print("\n📄 Generating English Report...")
    en_report = report_gen.generate_report(
        analysis_data,
        language='en',
        format='html'
    )
    print(f"✅ English Report: {en_report}")
    
    # Summary
    print("\n" + "=" * 80)
    print("TEST COMPLETE - SUMMARY")
    print("=" * 80)
    
    print("\n✅ All Phases Working:")
    print("   • Phase 1: Foundation modules operational")
    print("   • Phase 2: Analysis complete")
    print("   • Phase 3: Reports generated")
    
    print("\n📊 Analysis Results:")
    print(f"   • Cost Estimate: SAR {financial_eval['cost_breakdown']['total_cost']:,.0f}")
    print(f"   • Recommended Bid: SAR {financial_eval['pricing_analysis']['recommended_bid']:,.0f}")
    print(f"   • Expected Profit: SAR {financial_eval['profitability']['expected_profit']:,.0f}")
    print(f"   • Technical Score: {technical_eval['feasibility']['score']:.1f}%")
    print(f"   • Recommendation: {'✅ BID' if analysis_data['recommendation']['should_bid'] else '❌ SKIP'}")
    
    print("\n📁 Reports Generated:")
    print(f"   • Arabic: {ar_report}")
    print(f"   • English: {en_report}")
    
    return True


if __name__ == '__main__':
    try:
        success = test_full_analysis_pipeline()
        if success:
            print("\n" + "=" * 80)
            print("✅ PHASE 3 INTEGRATION TEST PASSED")
            print("=" * 80)
    except Exception as e:
        print(f"\n❌ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()
