"""
Company Context Module
Loads and manages company profile for AI tender analysis
"""

import json
from pathlib import Path
from typing import Dict, List, Optional


class CompanyContext:
    """Manages company profile and capabilities"""
    
    def __init__(self, profile_path: Optional[Path] = None):
        """
        Initialize company context
        
        Args:
            profile_path: Path to company_profile.json
        """
        if profile_path is None:
            # Go up from src/config/ to root, then to data/
            profile_path = Path(__file__).parent.parent.parent / 'data' / 'company_profile.json'
        
        self.profile_path = profile_path
        self.profile = self._load_profile()
    
    def _load_profile(self) -> Dict:
        """Load company profile from JSON file"""
        try:
            with open(self.profile_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"⚠️ Company profile not found at {self.profile_path}")
            return {}
        except json.JSONDecodeError as e:
            print(f"❌ Error parsing company profile: {e}")
            return {}
    
    def get_company_name(self, language: str = 'ar') -> str:
        """Get company name in specified language"""
        if language == 'ar':
            return self.profile.get('company_name_ar', 'شركتنا')
        return self.profile.get('company_name', 'Our Company')
    
    def get_capabilities(self) -> Dict:
        """Get all company capabilities"""
        return self.profile.get('capabilities', {})
    
    def get_certifications(self) -> List[Dict]:
        """Get company certifications"""
        return self.profile.get('certifications', [])
    
    def get_classifications(self) -> List[Dict]:
        """Get company classifications"""
        return self.profile.get('classifications', [])
    
    def get_past_projects(self) -> List[Dict]:
        """Get past project history"""
        return self.profile.get('past_projects', [])
    
    def get_team_composition(self) -> Dict:
        """Get team structure and size"""
        return self.profile.get('team', {})
    
    def get_pricing_strategy(self) -> Dict:
        """Get pricing margins and strategy"""
        return self.profile.get('pricing_strategy', {
            'profit_margin_min': 0.15,
            'profit_margin_target': 0.25,
            'profit_margin_max': 0.35,
            'overhead_percentage': 0.18,
            'contingency_percentage': 0.10
        })
    
    def get_preferences(self) -> Dict:
        """Get tender preferences (min/max values, sectors, etc.)"""
        return self.profile.get('preferences', {})
    
    def get_competitive_advantages(self) -> List[Dict]:
        """Get competitive advantages"""
        return self.profile.get('competitive_advantages', [])
    
    def matches_classification(self, required_code: str) -> bool:
        """
        Check if company has required classification
        
        Args:
            required_code: Classification code required by tender
            
        Returns:
            True if company has the classification
        """
        company_codes = [c.get('code', '') for c in self.get_classifications()]
        return required_code in company_codes
    
    def has_certification(self, cert_name: str) -> bool:
        """
        Check if company has specific certification
        
        Args:
            cert_name: Certification name to check
            
        Returns:
            True if company has the certification
        """
        company_certs = [c.get('name', '').lower() for c in self.get_certifications()]
        return cert_name.lower() in company_certs or any(cert_name.lower() in c for c in company_certs)
    
    def get_capability_by_sector(self, sector: str) -> Optional[Dict]:
        """
        Get company capability for specific sector
        
        Args:
            sector: Sector name (e.g., 'web_development', 'ai_and_ml')
            
        Returns:
            Capability dict or None
        """
        return self.get_capabilities().get(sector)
    
    def calculate_hourly_rate(self, level: str = 'mid') -> float:
        """
        Get hourly rate for team member level
        
        Args:
            level: 'junior', 'mid', 'senior', or 'expert'
            
        Returns:
            Hourly rate in SAR
        """
        rates = self.profile.get('cost_estimation_factors', {}).get('development_hourly_rate_range', {})
        return rates.get(level, 250)
    
    def get_technology_multiplier(self, tech_type: str) -> float:
        """
        Get cost multiplier for technology type
        
        Args:
            tech_type: Technology type (e.g., 'ai_ml', 'blockchain')
            
        Returns:
            Multiplier value
        """
        multipliers = self.profile.get('cost_estimation_factors', {}).get('technology_multipliers', {})
        return multipliers.get(tech_type, 1.0)
    
    def get_summary_for_ai(self) -> str:
        """
        Generate a text summary of company profile for AI context
        
        Returns:
            Formatted company summary
        """
        summary = f"""
Company Profile:
- Name: {self.get_company_name('en')} ({self.get_company_name('ar')})
- Commercial Registration: {self.profile.get('commercial_registration', 'N/A')}
- Location: {self.profile.get('location', {}).get('city', 'Saudi Arabia')}

Certifications:
{self._format_certifications()}

Classifications:
{self._format_classifications()}

Core Capabilities:
{self._format_capabilities()}

Team Composition:
{self._format_team()}

Past Projects:
{self._format_past_projects()}

Competitive Advantages:
{self._format_advantages()}

Pricing Strategy:
- Target Profit Margin: {self.get_pricing_strategy().get('profit_margin_target', 0.25) * 100}%
- Overhead: {self.get_pricing_strategy().get('overhead_percentage', 0.18) * 100}%
- Contingency: {self.get_pricing_strategy().get('contingency_percentage', 0.10) * 100}%
"""
        return summary.strip()
    
    def _format_certifications(self) -> str:
        """Format certifications for text summary"""
        certs = self.get_certifications()
        if not certs:
            return "- None listed"
        return "\n".join([f"- {c.get('name', 'Unknown')}" for c in certs[:5]])
    
    def _format_classifications(self) -> str:
        """Format classifications for text summary"""
        classifications = self.get_classifications()
        if not classifications:
            return "- None listed"
        return "\n".join([
            f"- {c.get('code', 'N/A')}: {c.get('description', 'N/A')} (Grade: {c.get('grade', 'N/A')})"
            for c in classifications[:5]
        ])
    
    def _format_capabilities(self) -> str:
        """Format capabilities for text summary"""
        caps = self.get_capabilities()
        if not caps:
            return "- None listed"
        
        result = []
        for sector, details in list(caps.items())[:6]:
            years = details.get('experience_years', 0)
            max_value = details.get('max_project_value', 0) / 1000000
            result.append(f"- {sector.replace('_', ' ').title()}: {years} years, up to SAR {max_value:.1f}M")
        
        return "\n".join(result)
    
    def _format_team(self) -> str:
        """Format team composition"""
        team = self.get_team_composition()
        if not team:
            return "- Not specified"
        
        total = team.get('total', sum(team.values()) if team else 0)
        return f"- Total: {total} professionals\n" + "\n".join([
            f"- {role.replace('_', ' ').title()}: {count}"
            for role, count in team.items() if role != 'total'
        ][:5])
    
    def _format_past_projects(self) -> str:
        """Format past projects"""
        projects = self.get_past_projects()
        if not projects:
            return "- None listed"
        
        return "\n".join([
            f"- {p.get('name', 'Unknown')} (SAR {p.get('value', 0)/1000000:.1f}M, {p.get('year', 'N/A')})"
            for p in projects[:5]
        ])
    
    def _format_advantages(self) -> str:
        """Format competitive advantages"""
        advantages = self.get_competitive_advantages()
        if not advantages:
            return "- None listed"
        
        return "\n".join([
            f"- {a.get('advantage', 'Unknown')}"
            for a in advantages[:5]
        ])


# Singleton instance
_company_context = None

def get_company_context() -> CompanyContext:
    """Get singleton instance of CompanyContext"""
    global _company_context
    if _company_context is None:
        _company_context = CompanyContext()
    return _company_context


if __name__ == "__main__":
    # Test the module
    context = get_company_context()
    print("=" * 60)
    print("Company Context Test")
    print("=" * 60)
    print(f"\n🏢 Company: {context.get_company_name('ar')}")
    print(f"📜 CR: {context.profile.get('commercial_registration', 'N/A')}")
    print(f"👥 Team Size: {context.get_team_composition().get('total', 'N/A')}")
    print(f"🎓 Certifications: {len(context.get_certifications())}")
    print(f"🏗️ Classifications: {len(context.get_classifications())}")
    print(f"💼 Past Projects: {len(context.get_past_projects())}")
    print("\n" + "=" * 60)
    print("Full Summary for AI:")
    print("=" * 60)
    print(context.get_summary_for_ai())
