"""
Cost Tracking Module
Tracks API usage and costs for tender analysis
"""

import json
import os
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CostTracker:
    """Tracks API usage costs and provides budget warnings"""
    
    def __init__(self, data_dir: str = "data"):
        """
        Initialize cost tracker
        
        Args:
            data_dir: Directory to store cost data
        """
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        self.cost_file = self.data_dir / "api_costs.json"
        self.costs = self._load_costs()
        
        # API pricing (as of 2025)
        self.pricing = {
            'anthropic_claude_sonnet_4': {
                'input_per_1m': 3.00,
                'output_per_1m': 15.00
            },
            'anthropic_claude_haiku': {
                'input_per_1m': 0.25,
                'output_per_1m': 1.25
            },
            'tavily_search': {
                'per_search': 0.005
            },
            'openai_gpt4': {
                'input_per_1m': 5.00,
                'output_per_1m': 15.00
            }
        }
        
        # Budget limits (can be configured)
        self.monthly_budget_limit = float(os.getenv('API_BUDGET_LIMIT', '100.0'))  # Default $100/month
        self.warning_threshold = 0.80  # Warn at 80% of budget
        
        logger.info(f"✅ Cost Tracker initialized (Budget: ${self.monthly_budget_limit}/month)")
    
    def _load_costs(self) -> Dict:
        """Load cost history from file"""
        if self.cost_file.exists():
            try:
                with open(self.cost_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Failed to load costs: {e}")
        
        return {
            'total_cost': 0.0,
            'monthly_costs': {},
            'analyses': []
        }
    
    def _save_costs(self):
        """Save cost history to file"""
        try:
            with open(self.cost_file, 'w', encoding='utf-8') as f:
                json.dump(self.costs, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"Failed to save costs: {e}")
    
    def calculate_anthropic_cost(self, input_tokens: int, output_tokens: int, model: str = 'sonnet_4') -> float:
        """
        Calculate Anthropic API cost
        
        Args:
            input_tokens: Input tokens used
            output_tokens: Output tokens generated
            model: Model name ('sonnet_4' or 'haiku')
            
        Returns:
            Cost in USD
        """
        model_key = f'anthropic_claude_{model}'
        if model_key not in self.pricing:
            logger.warning(f"Unknown model {model}, using sonnet_4 pricing")
            model_key = 'anthropic_claude_sonnet_4'
        
        pricing = self.pricing[model_key]
        cost = (input_tokens / 1_000_000 * pricing['input_per_1m']) + \
               (output_tokens / 1_000_000 * pricing['output_per_1m'])
        
        return round(cost, 4)
    
    def calculate_tavily_cost(self, num_searches: int) -> float:
        """
        Calculate Tavily search API cost
        
        Args:
            num_searches: Number of searches performed
            
        Returns:
            Cost in USD
        """
        cost = num_searches * self.pricing['tavily_search']['per_search']
        return round(cost, 4)
    
    def track_analysis(self, tender_id: str, costs_breakdown: Dict) -> Dict:
        """
        Track costs for a tender analysis
        
        Args:
            tender_id: Tender ID
            costs_breakdown: Dictionary with cost breakdown
                {
                    'anthropic': {'input_tokens': X, 'output_tokens': Y, 'cost': Z},
                    'tavily': {'num_searches': X, 'cost': Y},
                    'total': Z
                }
        
        Returns:
            Cost summary with warnings
        """
        current_month = datetime.now().strftime('%Y-%m')
        
        # Add to total costs
        self.costs['total_cost'] += costs_breakdown['total']
        
        # Add to monthly costs
        if current_month not in self.costs['monthly_costs']:
            self.costs['monthly_costs'][current_month] = 0.0
        
        self.costs['monthly_costs'][current_month] += costs_breakdown['total']
        
        # Record analysis
        analysis_record = {
            'tender_id': tender_id,
            'timestamp': datetime.now().isoformat(),
            'costs': costs_breakdown,
            'month': current_month
        }
        
        self.costs['analyses'].append(analysis_record)
        
        # Save to file
        self._save_costs()
        
        # Check budget and generate warnings
        monthly_cost = self.costs['monthly_costs'][current_month]
        percentage_used = (monthly_cost / self.monthly_budget_limit) * 100
        
        warning = None
        if percentage_used >= 100:
            warning = {
                'level': 'critical',
                'message': f'⛔ BUDGET EXCEEDED! Used ${monthly_cost:.2f} of ${self.monthly_budget_limit:.2f} ({percentage_used:.1f}%)',
                'action': 'Consider increasing budget or pausing analyses'
            }
            logger.error(warning['message'])
        elif percentage_used >= self.warning_threshold * 100:
            warning = {
                'level': 'warning',
                'message': f'⚠️ Budget warning: Used ${monthly_cost:.2f} of ${self.monthly_budget_limit:.2f} ({percentage_used:.1f}%)',
                'action': 'Monitor spending closely'
            }
            logger.warning(warning['message'])
        else:
            logger.info(f"💰 Cost tracked: ${costs_breakdown['total']:.4f} (Monthly total: ${monthly_cost:.2f}/{self.monthly_budget_limit:.2f})")
        
        return {
            'tender_id': tender_id,
            'analysis_cost': costs_breakdown['total'],
            'monthly_total': monthly_cost,
            'monthly_budget': self.monthly_budget_limit,
            'percentage_used': round(percentage_used, 1),
            'warning': warning
        }
    
    def get_monthly_summary(self, month: Optional[str] = None) -> Dict:
        """
        Get cost summary for a month
        
        Args:
            month: Month in format 'YYYY-MM' (defaults to current month)
            
        Returns:
            Dictionary with monthly summary
        """
        if month is None:
            month = datetime.now().strftime('%Y-%m')
        
        monthly_cost = self.costs['monthly_costs'].get(month, 0.0)
        
        # Get analyses for this month
        monthly_analyses = [
            a for a in self.costs['analyses']
            if a.get('month') == month
        ]
        
        # Calculate breakdown
        anthropic_cost = sum(a['costs'].get('anthropic', {}).get('cost', 0) for a in monthly_analyses)
        tavily_cost = sum(a['costs'].get('tavily', {}).get('cost', 0) for a in monthly_analyses)
        
        percentage_used = (monthly_cost / self.monthly_budget_limit) * 100 if self.monthly_budget_limit > 0 else 0
        
        return {
            'month': month,
            'total_cost': round(monthly_cost, 2),
            'budget_limit': self.monthly_budget_limit,
            'percentage_used': round(percentage_used, 1),
            'num_analyses': len(monthly_analyses),
            'avg_cost_per_analysis': round(monthly_cost / len(monthly_analyses), 4) if monthly_analyses else 0,
            'breakdown': {
                'anthropic': round(anthropic_cost, 2),
                'tavily': round(tavily_cost, 2)
            },
            'budget_remaining': round(self.monthly_budget_limit - monthly_cost, 2),
            'status': 'OK' if percentage_used < 80 else ('WARNING' if percentage_used < 100 else 'EXCEEDED')
        }
    
    def get_total_summary(self) -> Dict:
        """
        Get total cost summary across all time
        
        Returns:
            Dictionary with total summary
        """
        num_analyses = len(self.costs['analyses'])
        
        # Calculate total breakdown
        total_anthropic = sum(
            a['costs'].get('anthropic', {}).get('cost', 0)
            for a in self.costs['analyses']
        )
        total_tavily = sum(
            a['costs'].get('tavily', {}).get('cost', 0)
            for a in self.costs['analyses']
        )
        
        return {
            'total_cost': round(self.costs['total_cost'], 2),
            'num_analyses': num_analyses,
            'avg_cost_per_analysis': round(self.costs['total_cost'] / num_analyses, 4) if num_analyses else 0,
            'breakdown': {
                'anthropic': round(total_anthropic, 2),
                'tavily': round(total_tavily, 2)
            },
            'months_tracked': len(self.costs['monthly_costs']),
            'current_month': self.get_monthly_summary()
        }
    
    def get_recent_analyses(self, limit: int = 10) -> List[Dict]:
        """
        Get recent analyses with costs
        
        Args:
            limit: Maximum number of analyses to return
            
        Returns:
            List of recent analyses
        """
        return sorted(
            self.costs['analyses'],
            key=lambda x: x['timestamp'],
            reverse=True
        )[:limit]
    
    def set_budget_limit(self, limit: float) -> bool:
        """
        Set monthly budget limit
        
        Args:
            limit: Monthly budget limit in USD
            
        Returns:
            True if successful
        """
        try:
            self.monthly_budget_limit = float(limit)
            logger.info(f"✅ Budget limit set to ${limit:.2f}/month")
            return True
        except Exception as e:
            logger.error(f"Failed to set budget limit: {e}")
            return False


if __name__ == "__main__":
    # Test cost tracker
    print("=" * 60)
    print("Cost Tracker Test")
    print("=" * 60)
    
    tracker = CostTracker()
    
    # Simulate an analysis
    print("\n💰 Simulating analysis cost tracking...")
    
    costs = {
        'anthropic': {
            'input_tokens': 10000,
            'output_tokens': 3000,
            'cost': tracker.calculate_anthropic_cost(10000, 3000, 'sonnet_4')
        },
        'tavily': {
            'num_searches': 5,
            'cost': tracker.calculate_tavily_cost(5)
        },
        'total': 0
    }
    costs['total'] = costs['anthropic']['cost'] + costs['tavily']['cost']
    
    result = tracker.track_analysis('TEST_123', costs)
    
    print(f"\n📊 Analysis tracked:")
    print(f"  Cost: ${result['analysis_cost']:.4f}")
    print(f"  Monthly total: ${result['monthly_total']:.2f}")
    print(f"  Budget used: {result['percentage_used']}%")
    if result['warning']:
        print(f"  Warning: {result['warning']['message']}")
    
    # Get summary
    print("\n📈 Monthly Summary:")
    summary = tracker.get_monthly_summary()
    for key, value in summary.items():
        print(f"  {key}: {value}")
    
    print("\n✅ Cost tracking working!")
