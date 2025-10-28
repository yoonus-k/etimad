"""
Financial Evaluator Module
Performs financial analysis and cost estimation for tenders
"""

import logging
from typing import Dict, List, Optional
from datetime import datetime
import json

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class FinancialEvaluator:
    """Financial evaluation and cost estimation for tenders"""
    
    def __init__(self, company_context: Optional[Dict] = None):
        """
        Initialize Financial Evaluator
        
        Args:
            company_context: Company profile with pricing strategy (CompanyContext object or dict)
        """
        # Handle both CompanyContext object and dict
        if company_context:
            if hasattr(company_context, 'profile'):
                # It's a CompanyContext object - use the profile attribute
                profile = company_context.profile
                self.company_context = profile
                self.pricing_strategy = profile.get('pricing_strategy', {})
            else:
                # It's already a dict
                self.company_context = company_context
                self.pricing_strategy = company_context.get('pricing_strategy', {})
        else:
            self.company_context = {}
            self.pricing_strategy = {}
        
        # Default pricing strategy if not provided
        self.profit_margin_min = self.pricing_strategy.get('profit_margin_min', 0.10)
        self.profit_margin_target = self.pricing_strategy.get('profit_margin_target', 0.20)
        self.profit_margin_max = self.pricing_strategy.get('profit_margin_max', 0.30)
        self.overhead_percentage = self.pricing_strategy.get('overhead_percentage', 0.15)
        self.contingency_percentage = self.pricing_strategy.get('contingency_percentage', 0.08)
        
        logger.info("✅ Financial Evaluator initialized")
    
    def evaluate_tender(self, tender_data: Dict, market_research: Optional[Dict] = None) -> Dict:
        """
        Perform complete financial evaluation of a tender
        
        Args:
            tender_data: Extracted tender information
            market_research: Optional market research data with prices
            
        Returns:
            Dict with financial evaluation results
        """
        logger.info("💰 Starting financial evaluation...")
        
        evaluation = {
            'timestamp': datetime.now().isoformat(),
            'tender_reference': tender_data.get('reference_number', 'N/A'),
            'cost_breakdown': {},
            'pricing_analysis': {},
            'profitability': {},
            'recommendations': []
        }
        
        # Extract budget information from tender
        tender_budget = self._extract_budget_info(tender_data)
        evaluation['tender_budget'] = tender_budget
        
        # Calculate estimated costs
        cost_breakdown = self._calculate_cost_breakdown(tender_data, market_research)
        evaluation['cost_breakdown'] = cost_breakdown
        
        # Calculate pricing options
        pricing = self._calculate_pricing(cost_breakdown, tender_budget)
        evaluation['pricing_analysis'] = pricing
        
        # Calculate profitability metrics
        profitability = self._calculate_profitability(cost_breakdown, pricing)
        evaluation['profitability'] = profitability
        
        # Generate recommendations
        recommendations = self._generate_financial_recommendations(
            tender_budget, cost_breakdown, pricing, profitability
        )
        evaluation['recommendations'] = recommendations
        
        logger.info(f"✅ Financial evaluation complete")
        logger.info(f"   Estimated cost: SAR {cost_breakdown.get('total_cost', 0):,.2f}")
        logger.info(f"   Recommended bid: SAR {pricing.get('recommended_bid', 0):,.2f}")
        
        return evaluation
    
    def _extract_budget_info(self, tender_data: Dict) -> Dict:
        """Extract budget information from tender data"""
        budget_info = {
            'mentioned_budget': None,
            'estimated_range_min': None,
            'estimated_range_max': None,
            'currency': 'SAR'
        }
        
        # Try to find budget in tender data
        if 'budget' in tender_data:
            budget_info['mentioned_budget'] = tender_data['budget']
        
        if 'estimated_value' in tender_data:
            budget_info['mentioned_budget'] = tender_data['estimated_value']
        
        # Try to extract from description
        description = tender_data.get('description', '')
        requirements = tender_data.get('requirements', '')
        
        # If requirements is a dict, convert to string
        if isinstance(requirements, dict):
            requirements = str(requirements)
        
        combined_text = description + ' ' + requirements
        
        # Look for Saudi Riyal amounts (simple pattern matching)
        import re
        patterns = [
            r'(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)\s*(?:ريال|SAR)',
            r'(?:ريال|SAR)\s*(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)',
            r'(\d{1,3}(?:,\d{3})*)\s*(?:مليون|million)',
        ]
        
        amounts = []
        for pattern in patterns:
            matches = re.findall(pattern, combined_text, re.IGNORECASE)
            for match in matches:
                try:
                    amount = float(match.replace(',', ''))
                    if 'مليون' in combined_text or 'million' in combined_text.lower():
                        amount *= 1_000_000
                    amounts.append(amount)
                except ValueError:
                    continue
        
        if amounts:
            amounts.sort()
            budget_info['estimated_range_min'] = amounts[0]
            budget_info['estimated_range_max'] = amounts[-1]
            if not budget_info['mentioned_budget']:
                budget_info['mentioned_budget'] = amounts[-1] if len(amounts) == 1 else None
        
        return budget_info
    
    def _calculate_cost_breakdown(self, tender_data: Dict, market_research: Optional[Dict]) -> Dict:
        """
        Calculate detailed cost breakdown
        
        This is a simplified estimation. In production, this would use:
        - BOQ (Bill of Quantities) from Excel files
        - Market prices from research
        - Historical project data
        - Detailed resource allocation
        """
        breakdown = {
            'labor_costs': 0.0,
            'materials_costs': 0.0,
            'equipment_costs': 0.0,
            'subcontractor_costs': 0.0,
            'licensing_costs': 0.0,
            'overhead': 0.0,
            'contingency': 0.0,
            'subtotal': 0.0,
            'total_cost': 0.0,
            'breakdown_items': []
        }
        
        # Estimate based on project duration and type
        duration_months = self._estimate_duration(tender_data)
        project_type = self._identify_project_type(tender_data)
        
        # Use market research for pricing if available
        market_prices = market_research.get('pricing_data', {}) if market_research else {}
        
        # Labor costs estimation
        team_size = self._estimate_team_size(tender_data)
        avg_monthly_salary = market_prices.get('avg_salary', 15000)  # SAR per person
        breakdown['labor_costs'] = team_size * avg_monthly_salary * duration_months
        breakdown['breakdown_items'].append({
            'category': 'Labor',
            'description': f'{team_size} team members for {duration_months} months',
            'quantity': team_size * duration_months,
            'unit_cost': avg_monthly_salary,
            'total': breakdown['labor_costs']
        })
        
        # Materials/Equipment estimation
        if project_type in ['it', 'software', 'technology']:
            # Software licenses, cloud services, hardware
            breakdown['materials_costs'] = breakdown['labor_costs'] * 0.3
            breakdown['breakdown_items'].append({
                'category': 'Materials',
                'description': 'Software licenses, cloud services, development tools',
                'total': breakdown['materials_costs']
            })
        elif project_type in ['construction', 'infrastructure']:
            # Construction materials
            breakdown['materials_costs'] = breakdown['labor_costs'] * 0.5
            breakdown['equipment_costs'] = breakdown['labor_costs'] * 0.2
            breakdown['breakdown_items'].append({
                'category': 'Materials',
                'description': 'Construction materials',
                'total': breakdown['materials_costs']
            })
            breakdown['breakdown_items'].append({
                'category': 'Equipment',
                'description': 'Construction equipment rental',
                'total': breakdown['equipment_costs']
            })
        else:
            # General services
            breakdown['materials_costs'] = breakdown['labor_costs'] * 0.2
            breakdown['breakdown_items'].append({
                'category': 'Materials',
                'description': 'General materials and supplies',
                'total': breakdown['materials_costs']
            })
        
        # Subcontractor costs (if needed)
        if self._requires_subcontractors(tender_data):
            breakdown['subcontractor_costs'] = breakdown['labor_costs'] * 0.3
            breakdown['breakdown_items'].append({
                'category': 'Subcontractors',
                'description': 'Specialized subcontractor services',
                'total': breakdown['subcontractor_costs']
            })
        
        # Licensing and certifications
        if self._requires_licenses(tender_data):
            breakdown['licensing_costs'] = 50000  # Estimated
            breakdown['breakdown_items'].append({
                'category': 'Licensing',
                'description': 'Required licenses and certifications',
                'total': breakdown['licensing_costs']
            })
        
        # Calculate subtotal
        breakdown['subtotal'] = (
            breakdown['labor_costs'] +
            breakdown['materials_costs'] +
            breakdown['equipment_costs'] +
            breakdown['subcontractor_costs'] +
            breakdown['licensing_costs']
        )
        
        # Add overhead
        breakdown['overhead'] = breakdown['subtotal'] * self.overhead_percentage
        breakdown['breakdown_items'].append({
            'category': 'Overhead',
            'description': f'Overhead ({self.overhead_percentage*100:.0f}%)',
            'total': breakdown['overhead']
        })
        
        # Add contingency
        breakdown['contingency'] = breakdown['subtotal'] * self.contingency_percentage
        breakdown['breakdown_items'].append({
            'category': 'Contingency',
            'description': f'Contingency reserve ({self.contingency_percentage*100:.0f}%)',
            'total': breakdown['contingency']
        })
        
        # Total cost
        breakdown['total_cost'] = (
            breakdown['subtotal'] +
            breakdown['overhead'] +
            breakdown['contingency']
        )
        
        return breakdown
    
    def _calculate_pricing(self, cost_breakdown: Dict, tender_budget: Dict) -> Dict:
        """Calculate pricing options"""
        total_cost = cost_breakdown['total_cost']
        
        pricing = {
            'minimum_price': total_cost * (1 + self.profit_margin_min),
            'target_price': total_cost * (1 + self.profit_margin_target),
            'maximum_price': total_cost * (1 + self.profit_margin_max),
            'recommended_bid': 0.0,
            'strategy': ''
        }
        
        # Determine recommended bid based on tender budget
        tender_max = tender_budget.get('mentioned_budget') or tender_budget.get('estimated_range_max')
        
        if tender_max:
            # If tender has budget, bid competitively
            if tender_max >= pricing['target_price']:
                # Can bid target price
                pricing['recommended_bid'] = pricing['target_price']
                pricing['strategy'] = 'Competitive - Target margin achievable'
            elif tender_max >= pricing['minimum_price']:
                # Need to bid lower margin
                pricing['recommended_bid'] = tender_max * 0.95  # Bid 95% of max
                pricing['strategy'] = 'Aggressive - Lower margin for competitiveness'
            else:
                # Budget too low
                pricing['recommended_bid'] = pricing['minimum_price']
                pricing['strategy'] = 'Minimum viable - Budget may be insufficient'
        else:
            # No budget info, bid target
            pricing['recommended_bid'] = pricing['target_price']
            pricing['strategy'] = 'Standard - Target margin'
        
        return pricing
    
    def _calculate_profitability(self, cost_breakdown: Dict, pricing: Dict) -> Dict:
        """Calculate profitability metrics"""
        total_cost = cost_breakdown['total_cost']
        recommended_bid = pricing['recommended_bid']
        
        profit = recommended_bid - total_cost
        profit_margin = (profit / recommended_bid * 100) if recommended_bid > 0 else 0
        roi = (profit / total_cost * 100) if total_cost > 0 else 0
        
        return {
            'expected_profit': profit,
            'profit_margin_percentage': profit_margin,
            'roi_percentage': roi,
            'break_even_price': total_cost,
            'risk_adjusted_profit': profit * 0.8  # 80% confidence
        }
    
    def _generate_financial_recommendations(
        self, 
        tender_budget: Dict, 
        cost_breakdown: Dict, 
        pricing: Dict,
        profitability: Dict
    ) -> List[str]:
        """Generate financial recommendations"""
        recommendations = []
        
        # Check if profitable
        if profitability['profit_margin_percentage'] < 10:
            recommendations.append('⚠️ Low profit margin - Consider carefully before bidding')
        elif profitability['profit_margin_percentage'] >= 20:
            recommendations.append('✅ Healthy profit margin - Good opportunity')
        
        # Check cost vs budget
        tender_max = tender_budget.get('mentioned_budget')
        if tender_max:
            if pricing['recommended_bid'] > tender_max * 1.1:
                recommendations.append('❌ Our costs exceed tender budget significantly')
            elif pricing['recommended_bid'] <= tender_max:
                recommendations.append('✅ Bid is within tender budget')
        
        # Risk assessment
        if cost_breakdown['contingency'] < cost_breakdown['subtotal'] * 0.1:
            recommendations.append('⚠️ Increase contingency reserve for risk mitigation')
        
        # Optimization suggestions
        if cost_breakdown['labor_costs'] > cost_breakdown['subtotal'] * 0.6:
            recommendations.append('💡 Consider optimizing team size to reduce labor costs')
        
        if cost_breakdown['subcontractor_costs'] > 0:
            recommendations.append('💡 Negotiate with subcontractors for better rates')
        
        return recommendations
    
    def _estimate_duration(self, tender_data: Dict) -> int:
        """Estimate project duration in months"""
        # Try to extract from tender data
        duration = tender_data.get('duration_months')
        if duration:
            return duration
        
        # Look in description
        description = str(tender_data.get('description', ''))
        import re
        
        # Look for duration patterns
        patterns = [
            r'(\d+)\s*(?:شهر|شهور|months?)',
            r'(\d+)\s*(?:سنة|سنوات|years?)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, description, re.IGNORECASE)
            if match:
                value = int(match.group(1))
                if 'سنة' in match.group(0) or 'year' in match.group(0).lower():
                    return value * 12
                return value
        
        # Default estimate
        return 12
    
    def _identify_project_type(self, tender_data: Dict) -> str:
        """Identify project type from tender data"""
        description = str(tender_data.get('description', '')).lower()
        
        keywords = {
            'it': ['تقنية', 'برمجة', 'نظام', 'software', 'it', 'system', 'application'],
            'construction': ['بناء', 'تشييد', 'إنشاء', 'construction', 'building'],
            'consulting': ['استشار', 'دراسة', 'consulting', 'advisory'],
            'maintenance': ['صيانة', 'دعم', 'maintenance', 'support']
        }
        
        for proj_type, words in keywords.items():
            if any(word in description for word in words):
                return proj_type
        
        return 'general'
    
    def _estimate_team_size(self, tender_data: Dict) -> int:
        """Estimate required team size"""
        # This would analyze requirements to determine team size
        # For now, use simple heuristics
        
        duration = self._estimate_duration(tender_data)
        project_type = self._identify_project_type(tender_data)
        
        base_team = {
            'it': 8,
            'construction': 15,
            'consulting': 5,
            'maintenance': 4,
            'general': 6
        }
        
        team_size = base_team.get(project_type, 6)
        
        # Adjust based on complexity keywords
        description = str(tender_data.get('description', '')).lower()
        if any(word in description for word in ['كبير', 'شامل', 'large', 'comprehensive']):
            team_size = int(team_size * 1.5)
        
        return team_size
    
    def _requires_subcontractors(self, tender_data: Dict) -> bool:
        """Check if project requires subcontractors"""
        description = str(tender_data.get('description', '')).lower()
        keywords = ['متخصص', 'specialized', 'expert', 'استشاري']
        return any(word in description for word in keywords)
    
    def _requires_licenses(self, tender_data: Dict) -> bool:
        """Check if project requires special licenses"""
        description = str(tender_data.get('description', '')).lower()
        keywords = ['رخصة', 'ترخيص', 'license', 'certification', 'شهادة']
        return any(word in description for word in keywords)


if __name__ == "__main__":
    # Test the module
    print("=" * 60)
    print("Financial Evaluator Test")
    print("=" * 60)
    
    # Sample company context
    from company_context import get_company_context
    context = get_company_context()
    
    evaluator = FinancialEvaluator(context.profile)
    
    # Sample tender data
    sample_tender = {
        'reference_number': '251039009436',
        'description': '''
        مشروع تطوير نظام إدارة الموارد البشرية المتكامل
        المدة: 12 شهراً
        القيمة التقديرية: 5,000,000 ريال سعودي
        
        المتطلبات:
        - تطوير نظام متكامل
        - قاعدة بيانات آمنة
        - دعم فني لمدة سنة
        - تدريب الموظفين
        ''',
        'requirements': 'خبرة 5 سنوات، شهادة ISO 27001',
        'duration_months': 12
    }
    
    print("\n📊 Testing financial evaluation...\n")
    
    result = evaluator.evaluate_tender(sample_tender)
    
    print(f"\n💰 Financial Evaluation Results:")
    print(f"{'='*60}")
    print(f"Tender: {result['tender_reference']}")
    print(f"\n📋 Cost Breakdown:")
    print(f"  Total Cost: SAR {result['cost_breakdown']['total_cost']:,.2f}")
    print(f"  - Labor: SAR {result['cost_breakdown']['labor_costs']:,.2f}")
    print(f"  - Materials: SAR {result['cost_breakdown']['materials_costs']:,.2f}")
    print(f"  - Overhead: SAR {result['cost_breakdown']['overhead']:,.2f}")
    print(f"  - Contingency: SAR {result['cost_breakdown']['contingency']:,.2f}")
    
    print(f"\n💵 Pricing Analysis:")
    print(f"  Minimum Price: SAR {result['pricing_analysis']['minimum_price']:,.2f}")
    print(f"  Target Price: SAR {result['pricing_analysis']['target_price']:,.2f}")
    print(f"  Recommended Bid: SAR {result['pricing_analysis']['recommended_bid']:,.2f}")
    print(f"  Strategy: {result['pricing_analysis']['strategy']}")
    
    print(f"\n📈 Profitability:")
    print(f"  Expected Profit: SAR {result['profitability']['expected_profit']:,.2f}")
    print(f"  Profit Margin: {result['profitability']['profit_margin_percentage']:.1f}%")
    print(f"  ROI: {result['profitability']['roi_percentage']:.1f}%")
    
    print(f"\n💡 Recommendations:")
    for rec in result['recommendations']:
        print(f"  {rec}")
    
    print(f"\n✅ Test complete!")
