"""
Phase 2 Integration Test
Tests the complete analysis pipeline with all Phase 2 modules
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.company_context import get_company_context
from src.financial_evaluator import FinancialEvaluator
from src.technical_evaluator import TechnicalEvaluator
from src.market_researcher import MarketResearcher


def test_complete_analysis_pipeline():
    """Test complete analysis with all Phase 2 modules"""
    
    print("=" * 70)
    print("PHASE 2 INTEGRATION TEST")
    print("Testing: Financial + Technical + Market Research")
    print("=" * 70)
    
    # Sample tender data
    tender_data = {
        'reference_number': '251039009436',
        'description': '''
        مشروع تطوير نظام إدارة الموارد البشرية المتكامل
        
        نطاق العمل:
        - تطوير نظام ويب متكامل لإدارة الموارد البشرية
        - تطبيق موبايل (iOS و Android)
        - قاعدة بيانات آمنة ومشفرة
        - لوحة تحكم إدارية
        - تقارير وتحليلات
        - تكامل مع أنظمة الحكومة الإلكترونية
        
        المتطلبات الفنية:
        - خبرة لا تقل عن 5 سنوات في تطوير الأنظمة الحكومية
        - شهادة ISO 27001 للأمن السيبراني
        - التصنيف المطلوب: 701 (خدمات تقنية المعلومات)
        - فريق عمل لا يقل عن 8 موظفين
        - خبرة في Python و React و AWS
        - خبرة في تطوير تطبيقات الموبايل
        
        المدة: 12 شهراً
        القيمة التقديرية: 5,000,000 ريال سعودي
        
        الشهادات المطلوبة:
        - ISO 27001
        - ISO 9001
        
        المخرجات:
        - نظام متكامل لإدارة الموارد البشرية
        - تطبيق موبايل (iOS و Android)
        - قاعدة بيانات آمنة
        - وثائق فنية شاملة
        - دعم فني لمدة سنة
        - تدريب للمستخدمين
        ''',
        'requirements': 'شهادة ISO 27001، خبرة 5 سنوات، التصنيف 701',
        'duration_months': 12
    }
    
    print(f"\n📋 Tender Reference: {tender_data['reference_number']}")
    print("=" * 70)
    
    # Step 1: Load company context
    print("\n[1/4] Loading company context...")
    context = get_company_context()
    print(f"✅ Company: {context.get_company_name('ar')}")
    print(f"   Team: {context.profile.get('team', {})}")
    
    # Step 2: Market Research
    print("\n[2/4] Performing market research...")
    researcher = MarketResearcher()
    market_data = researcher.research_tender(tender_data)
    print(f"✅ Market Research Complete")
    print(f"   Similar tenders found: {len(market_data['similar_tenders'])}")
    print(f"   Average salary: SAR {market_data['pricing_data'].get('avg_salary', 0):,}")
    print(f"   Suppliers found: {len(market_data['suppliers'])}")
    
    # Step 3: Technical Evaluation
    print("\n[3/4] Performing technical evaluation...")
    tech_evaluator = TechnicalEvaluator(context.profile)
    tech_result = tech_evaluator.evaluate_tender(tender_data)
    print(f"✅ Technical Evaluation Complete")
    print(f"   Capability match: {tech_result['capability_match']['overall_score']:.1f}%")
    print(f"   Feasibility: {tech_result['feasibility']['level']}")
    print(f"   Risks identified: {len(tech_result['risks'])}")
    
    # Step 4: Financial Evaluation
    print("\n[4/4] Performing financial evaluation...")
    fin_evaluator = FinancialEvaluator(context.profile)
    fin_result = fin_evaluator.evaluate_tender(tender_data, market_data)
    print(f"✅ Financial Evaluation Complete")
    print(f"   Total cost: SAR {fin_result['cost_breakdown']['total_cost']:,.2f}")
    print(f"   Recommended bid: SAR {fin_result['pricing_analysis']['recommended_bid']:,.2f}")
    print(f"   Expected profit: SAR {fin_result['profitability']['expected_profit']:,.2f}")
    print(f"   Profit margin: {fin_result['profitability']['profit_margin_percentage']:.1f}%")
    
    # Combined Summary
    print("\n" + "=" * 70)
    print("📊 COMBINED ANALYSIS SUMMARY")
    print("=" * 70)
    
    print(f"\n💰 FINANCIAL:")
    print(f"   Estimated Cost: SAR {fin_result['cost_breakdown']['total_cost']:,.2f}")
    print(f"   Recommended Bid: SAR {fin_result['pricing_analysis']['recommended_bid']:,.2f}")
    print(f"   Expected Profit: SAR {fin_result['profitability']['expected_profit']:,.2f} ({fin_result['profitability']['profit_margin_percentage']:.1f}%)")
    print(f"   ROI: {fin_result['profitability']['roi_percentage']:.1f}%")
    
    print(f"\n🔧 TECHNICAL:")
    print(f"   Capability Match: {tech_result['capability_match']['overall_score']:.1f}%")
    print(f"   Feasibility: {tech_result['feasibility']['level']} ({tech_result['feasibility']['score']:.1f}%)")
    print(f"   Can Deliver: {'Yes' if tech_result['feasibility']['can_deliver'] else 'No'}")
    print(f"   Certifications Match: {len(tech_result['capability_match']['certifications_match'])}")
    print(f"   Certifications Missing: {len(tech_result['capability_match']['certifications_missing'])}")
    
    print(f"\n🔍 MARKET RESEARCH:")
    print(f"   Similar Tenders: {len(market_data['similar_tenders'])}")
    print(f"   Market Salary Data: SAR {market_data['pricing_data'].get('avg_salary', 0):,}")
    print(f"   Suppliers Identified: {len(market_data['suppliers'])}")
    
    print(f"\n⚠️ KEY RISKS ({len(tech_result['risks'])}):")
    for risk in tech_result['risks'][:3]:
        print(f"   [{risk['severity']}] {risk['type']}: {risk['description'][:60]}...")
    
    print(f"\n💡 TOP RECOMMENDATIONS:")
    all_recommendations = (
        fin_result['recommendations'] + 
        tech_result['recommendations']
    )
    for rec in all_recommendations[:5]:
        print(f"   {rec}")
    
    # Final Decision
    print(f"\n" + "=" * 70)
    print("🎯 FINAL DECISION:")
    print("=" * 70)
    
    capability_score = tech_result['capability_match']['overall_score']
    profit_margin = fin_result['profitability']['profit_margin_percentage']
    can_deliver = tech_result['feasibility']['can_deliver']
    
    if capability_score >= 70 and profit_margin >= 15 and can_deliver:
        decision = "✅ HIGHLY RECOMMENDED - Proceed with bidding"
        priority = "HIGH"
    elif capability_score >= 60 and profit_margin >= 10 and can_deliver:
        decision = "✅ RECOMMENDED - Good opportunity with preparation"
        priority = "MEDIUM"
    elif capability_score >= 40 and profit_margin >= 5:
        decision = "⚠️ CONSIDER CAREFULLY - Requires significant preparation"
        priority = "LOW"
    else:
        decision = "❌ NOT RECOMMENDED - High risk / Low profitability"
        priority = "SKIP"
    
    print(f"\n{decision}")
    print(f"Priority: {priority}")
    print(f"")
    print(f"Technical Fit: {capability_score:.1f}%")
    print(f"Profit Margin: {profit_margin:.1f}%")
    print(f"Can Deliver: {'Yes' if can_deliver else 'No'}")
    
    print(f"\n" + "=" * 70)
    print("✅ PHASE 2 INTEGRATION TEST COMPLETE")
    print("=" * 70)
    
    return {
        'technical': tech_result,
        'financial': fin_result,
        'market': market_data,
        'decision': decision,
        'priority': priority
    }


if __name__ == "__main__":
    try:
        result = test_complete_analysis_pipeline()
        print("\n✅ All tests passed!")
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
