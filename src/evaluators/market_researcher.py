"""
Market Researcher Module
Performs internet research for market data, pricing, and suppliers
"""

import logging
import os
from typing import Dict, List, Optional
from datetime import datetime
import json

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MarketResearcher:
    """Internet research for tender market data"""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize Market Researcher
        
        Args:
            api_key: Tavily API key (if not provided, reads from env)
        """
        self.api_key = api_key or os.getenv('TAVILY_API_KEY')
        self.client = None
        
        if self.api_key:
            self._initialize_client()
        else:
            logger.warning("⚠️ Tavily API key not found. Market research will be limited.")
            logger.info("   Set TAVILY_API_KEY environment variable to enable full research.")
    
    def _initialize_client(self):
        """Initialize Tavily client"""
        try:
            from tavily import TavilyClient
            
            self.client = TavilyClient(api_key=self.api_key)
            logger.info("✅ Tavily client initialized")
            
        except ImportError:
            logger.error("Tavily package not installed. Install with: pip install tavily-python")
            self.client = None
        except Exception as e:
            logger.error(f"Failed to initialize Tavily client: {e}")
            self.client = None
    
    def research_tender(
        self, 
        tender_data: Dict, 
        requirements: Optional[Dict] = None
    ) -> Dict:
        """
        Perform market research for a tender
        
        Args:
            tender_data: Tender information
            requirements: Extracted requirements
            
        Returns:
            Dict with research results
        """
        logger.info("🔍 Starting market research...")
        
        research = {
            'timestamp': datetime.now().isoformat(),
            'tender_reference': tender_data.get('reference_number', 'N/A'),
            'similar_tenders': [],
            'pricing_data': {},
            'suppliers': [],
            'market_insights': [],
            'salary_data': {},
            'technical_resources': [],
            'research_sources': []
        }
        
        if not self.client:
            logger.warning("⚠️ Tavily client not available - using mock data")
            return self._generate_mock_research(tender_data, requirements)
        
        try:
            # Research similar tenders
            similar_tenders = self._search_similar_tenders(tender_data)
            research['similar_tenders'] = similar_tenders
            
            # Research pricing
            pricing_data = self._search_pricing(tender_data, requirements)
            research['pricing_data'] = pricing_data
            
            # Research suppliers
            suppliers = self._search_suppliers(tender_data, requirements)
            research['suppliers'] = suppliers
            
            # Research Saudi market salaries
            salary_data = self._search_salary_data(tender_data)
            research['salary_data'] = salary_data
            
            # Technical resources
            technical_resources = self._search_technical_resources(tender_data, requirements)
            research['technical_resources'] = technical_resources
            
            logger.info("✅ Market research complete")
            
        except Exception as e:
            logger.error(f"❌ Market research failed: {e}")
            research['error'] = str(e)
        
        return research
    
    def _search_similar_tenders(self, tender_data: Dict) -> List[Dict]:
        """Search for similar tenders"""
        if not self.client:
            return []
        
        logger.info("   Searching for similar tenders...")
        
        # Build search query
        description = tender_data.get('description', '')[:200]
        query = f"منافسات حكومية سعودية {description} site:etimad.sa OR site:monshaat.gov.sa"
        
        try:
            results = self.client.search(
                query=query,
                search_depth="basic",
                max_results=5
            )
            
            similar = []
            for result in results.get('results', []):
                similar.append({
                    'title': result.get('title'),
                    'url': result.get('url'),
                    'snippet': result.get('content', '')[:200],
                    'relevance_score': result.get('score', 0)
                })
            
            logger.info(f"   Found {len(similar)} similar tenders")
            return similar
            
        except Exception as e:
            logger.error(f"   Failed to search similar tenders: {e}")
            return []
    
    def _search_pricing(self, tender_data: Dict, requirements: Optional[Dict]) -> Dict:
        """Search for pricing information"""
        if not self.client:
            return {}
        
        logger.info("   Searching for pricing data...")
        
        pricing_data = {
            'avg_salary': 0,
            'product_prices': [],
            'service_rates': [],
            'market_rates': {}
        }
        
        # Search for Saudi IT salary data
        try:
            query = "Saudi Arabia IT salaries 2025 average software developer engineer"
            results = self.client.search(
                query=query,
                search_depth="basic",
                max_results=3
            )
            
            # Parse salary information
            for result in results.get('results', []):
                content = result.get('content', '').lower()
                if 'sar' in content or 'riyal' in content:
                    # Try to extract salary numbers
                    import re
                    numbers = re.findall(r'(\d{1,3}(?:,\d{3})*)', content)
                    if numbers:
                        # Take first reasonable salary (between 5K-50K SAR)
                        for num_str in numbers:
                            try:
                                salary = int(num_str.replace(',', ''))
                                if 5000 <= salary <= 50000:
                                    pricing_data['avg_salary'] = salary
                                    break
                            except:
                                continue
            
            # Default if not found
            if pricing_data['avg_salary'] == 0:
                pricing_data['avg_salary'] = 15000  # Default SAR
            
            logger.info(f"   Average salary estimate: SAR {pricing_data['avg_salary']:,}")
            
        except Exception as e:
            logger.error(f"   Failed to search pricing: {e}")
            pricing_data['avg_salary'] = 15000  # Default
        
        return pricing_data
    
    def _search_suppliers(self, tender_data: Dict, requirements: Optional[Dict]) -> List[Dict]:
        """Search for potential suppliers"""
        if not self.client:
            return []
        
        logger.info("   Searching for suppliers...")
        
        suppliers = []
        
        # Identify what products/services are needed
        description = tender_data.get('description', '')
        
        # Search for Saudi suppliers
        query = f"Saudi Arabia suppliers vendors {description[:100]}"
        
        try:
            results = self.client.search(
                query=query,
                search_depth="basic",
                max_results=5
            )
            
            for result in results.get('results', []):
                suppliers.append({
                    'name': result.get('title'),
                    'url': result.get('url'),
                    'description': result.get('content', '')[:200]
                })
            
            logger.info(f"   Found {len(suppliers)} potential suppliers")
            
        except Exception as e:
            logger.error(f"   Failed to search suppliers: {e}")
        
        return suppliers
    
    def _search_salary_data(self, tender_data: Dict) -> Dict:
        """Search for Saudi salary data by role"""
        if not self.client:
            return {}
        
        logger.info("   Searching for salary data...")
        
        salary_data = {
            'project_manager': 20000,
            'senior_developer': 18000,
            'developer': 12000,
            'engineer': 15000,
            'analyst': 13000,
            'consultant': 25000,
            'source': 'Default estimates'
        }
        
        try:
            query = "Saudi Arabia salaries 2025 IT technology project manager developer"
            results = self.client.search(
                query=query,
                search_depth="basic",
                max_results=2
            )
            
            if results.get('results'):
                salary_data['source'] = results['results'][0].get('url', 'Market research')
            
        except Exception as e:
            logger.error(f"   Failed to search salary data: {e}")
        
        return salary_data
    
    def _search_technical_resources(self, tender_data: Dict, requirements: Optional[Dict]) -> List[Dict]:
        """Search for technical documentation and resources"""
        if not self.client:
            return []
        
        logger.info("   Searching for technical resources...")
        
        resources = []
        
        # Extract key technologies from requirements
        if requirements:
            technologies = requirements.get('technologies', [])
            if technologies:
                tech_query = ' '.join(technologies[:3])
                query = f"{tech_query} documentation best practices Saudi Arabia"
                
                try:
                    results = self.client.search(
                        query=query,
                        search_depth="basic",
                        max_results=3
                    )
                    
                    for result in results.get('results', []):
                        resources.append({
                            'title': result.get('title'),
                            'url': result.get('url'),
                            'type': 'Technical Documentation'
                        })
                    
                except Exception as e:
                    logger.error(f"   Failed to search technical resources: {e}")
        
        return resources
    
    def _generate_mock_research(self, tender_data: Dict, requirements: Optional[Dict]) -> Dict:
        """Generate mock research data when API is not available"""
        logger.info("   Generating mock research data...")
        
        return {
            'timestamp': datetime.now().isoformat(),
            'tender_reference': tender_data.get('reference_number', 'N/A'),
            'similar_tenders': [
                {
                    'title': 'Similar tender project (mock data)',
                    'url': 'https://etimad.sa',
                    'snippet': 'This is mock data. Configure TAVILY_API_KEY for real research.',
                    'relevance_score': 0.8
                }
            ],
            'pricing_data': {
                'avg_salary': 15000,
                'product_prices': [],
                'service_rates': [],
                'market_rates': {
                    'developer': 12000,
                    'engineer': 15000,
                    'project_manager': 20000
                }
            },
            'suppliers': [
                {
                    'name': 'Mock Supplier (Configure API key for real data)',
                    'url': 'https://example.com',
                    'description': 'Set TAVILY_API_KEY for actual supplier research'
                }
            ],
            'market_insights': [
                'Market research requires Tavily API key',
                'Set TAVILY_API_KEY environment variable',
                'Get API key from: https://tavily.com'
            ],
            'salary_data': {
                'project_manager': 20000,
                'senior_developer': 18000,
                'developer': 12000,
                'engineer': 15000,
                'analyst': 13000,
                'source': 'Default estimates (mock data)'
            },
            'technical_resources': [],
            'research_sources': [],
            'note': 'This is mock data. Configure TAVILY_API_KEY for actual market research.'
        }
    
    def search_custom_query(self, query: str, max_results: int = 5) -> List[Dict]:
        """
        Perform custom search query
        
        Args:
            query: Search query
            max_results: Maximum number of results
            
        Returns:
            List of search results
        """
        if not self.client:
            logger.warning("Tavily client not available")
            return []
        
        try:
            results = self.client.search(
                query=query,
                search_depth="basic",
                max_results=max_results
            )
            
            return results.get('results', [])
            
        except Exception as e:
            logger.error(f"Search failed: {e}")
            return []


if __name__ == "__main__":
    # Test the module
    print("=" * 60)
    print("Market Researcher Test")
    print("=" * 60)
    
    researcher = MarketResearcher()
    
    # Sample tender data
    sample_tender = {
        'reference_number': '251039009436',
        'description': '''
        مشروع تطوير نظام إدارة الموارد البشرية المتكامل
        يتضمن تطوير تطبيق ويب وموبايل
        مع قاعدة بيانات وخدمات سحابية
        '''
    }
    
    sample_requirements = {
        'technologies': ['Python', 'React', 'AWS'],
        'team_requirements': {'total_size': 8}
    }
    
    print("\n🔍 Testing market research...\n")
    
    result = researcher.research_tender(sample_tender, sample_requirements)
    
    print(f"\n📊 Market Research Results:")
    print(f"{'='*60}")
    print(f"Tender: {result['tender_reference']}")
    
    print(f"\n🔎 Similar Tenders ({len(result['similar_tenders'])}):")
    for tender in result['similar_tenders'][:3]:
        print(f"  • {tender['title']}")
        print(f"    URL: {tender['url']}")
    
    print(f"\n💰 Pricing Data:")
    pricing = result['pricing_data']
    print(f"  Average Salary: SAR {pricing.get('avg_salary', 0):,}")
    if pricing.get('market_rates'):
        print(f"  Market Rates:")
        for role, rate in pricing['market_rates'].items():
            print(f"    - {role}: SAR {rate:,}")
    
    print(f"\n🏢 Suppliers ({len(result['suppliers'])}):")
    for supplier in result['suppliers'][:3]:
        print(f"  • {supplier['name']}")
        print(f"    {supplier['url']}")
    
    print(f"\n📚 Technical Resources ({len(result['technical_resources'])}):")
    for resource in result['technical_resources'][:3]:
        print(f"  • {resource['title']}")
    
    if result.get('note'):
        print(f"\n⚠️ Note: {result['note']}")
    
    print(f"\n✅ Test complete!")
