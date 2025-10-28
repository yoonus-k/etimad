"""
AI Analyzer Module
Orchestrates AI-powered tender analysis using Anthropic Claude
"""

import os
import json
from pathlib import Path
from typing import Dict, Optional
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

class AIAnalyzer:
    """AI-powered tender analysis orchestrator using Claude"""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize AI Analyzer
        
        Args:
            api_key: Anthropic API key (if not provided, reads from env)
        """
        self.api_key = api_key or os.getenv('ANTHROPIC_API_KEY')
        self.client = None
        self.model = "claude-sonnet-4-20250514"  # Claude Sonnet 4
        self.max_tokens = 200000  # Claude's large context window
        
        if self.api_key:
            self._initialize_client()
        else:
            logger.warning("⚠️ Anthropic API key not found. Set ANTHROPIC_API_KEY environment variable.")
    
    def _initialize_client(self):
        """Initialize Anthropic client"""
        try:
            from anthropic import Anthropic
            
            self.client = Anthropic(api_key=self.api_key)
            logger.info("✅ Anthropic Claude client initialized")
            
            # Test connection
            self._test_connection()
        
        except ImportError:
            logger.error("Anthropic package not installed. Install with: pip install anthropic")
        except Exception as e:
            logger.error(f"Failed to initialize Anthropic client: {e}")
    
    def _test_connection(self):
        """Test Anthropic API connection"""
        try:
            # Simple test request
            response = self.client.messages.create(
                model="claude-3-haiku-20240307",  # Use cheaper model for testing
                max_tokens=10,
                messages=[{"role": "user", "content": "Test"}]
            )
            logger.info("✅ Anthropic API connection successful")
        except Exception as e:
            logger.warning(f"⚠️ Anthropic API test failed: {e}")
    
    def analyze_tender_summary(self, tender_text: str, company_context: str) -> Dict:
        """
        Get initial tender summary and basic analysis
        
        Args:
            tender_text: Combined text from all tender documents
            company_context: Company profile summary
            
        Returns:
            Dict with summary and initial analysis
        """
        if not self.client:
            logger.error("Anthropic client not initialized")
            return {"error": "Anthropic client not initialized"}
        
        logger.info("🤖 Generating tender summary...")
        
        # Truncate text if too long
        max_text_length = 50000  # Approximately 12-13k tokens
        if len(tender_text) > max_text_length:
            logger.warning(f"Tender text too long ({len(tender_text)} chars), truncating to {max_text_length}")
            tender_text = tender_text[:max_text_length] + "\n\n[...text truncated...]"
        
        prompt = f"""
You are an expert tender analyst helping a Saudi Arabian company evaluate government tenders.

COMPANY PROFILE:
{company_context}

TENDER DOCUMENTS:
{tender_text}

Analyze this tender and provide your response in STRICT JSON format (no markdown, no code blocks, just pure JSON):

{{
  "recommendation": "PROCEED|CONSIDER|SKIP",
  "confidence": "High|Medium|Low",
  "priority": "High|Medium|Low",
  "executive_summary": {{
    "ar": "ملخص باللغة العربية",
    "en": "Summary in English"
  }},
  "key_strengths": [
    "Strength 1",
    "Strength 2"
  ],
  "key_concerns": [
    "Concern 1",
    "Concern 2"
  ],
  "technical_requirements": [
    "Requirement 1",
    "Requirement 2"
  ],
  "financial_insights": {{
    "estimated_value_sar": 0,
    "complexity": "Low|Medium|High",
    "resource_needs": "Description"
  }},
  "analysis_summary": "Brief summary of the analysis"
}}

IMPORTANT: Return ONLY the JSON object, no other text."""
        
        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=4000,
                system="You are an expert Saudi Arabian government tender analyst specializing in IT and technology procurement. You always respond in valid JSON format without markdown code blocks.",
                messages=[
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1  # Very low temperature for structured output
            )
            
            result = response.content[0].text
            
            # Strip markdown code blocks if present
            result = result.strip()
            if result.startswith('```json'):
                result = result[7:]  # Remove ```json
            if result.startswith('```'):
                result = result[3:]  # Remove ```
            if result.endswith('```'):
                result = result[:-3]  # Remove closing ```
            result = result.strip()
            
            # Try to parse as JSON
            try:
                analysis = json.loads(result)
            except json.JSONDecodeError as e:
                logger.warning(f"Failed to parse JSON: {e}")
                # If not JSON, extract key information from text
                analysis = {
                    "raw_analysis": result,
                    "recommendation": self._extract_recommendation(result),
                    "confidence": self._extract_confidence(result),
                    "priority": self._extract_priority(result),
                    "key_strengths": self._extract_list(result, ["strong", "strength", "advantage", "قوة", "مميز"]),
                    "key_concerns": self._extract_list(result, ["risk", "concern", "challenge", "مخاطر", "تحدي"]),
                    "analysis_summary": result[:500] + "..." if len(result) > 500 else result
                }
            
            # Add metadata
            analysis['_metadata'] = {
                'model': self.model,
                'timestamp': datetime.now().isoformat(),
                'tokens_used': response.usage.input_tokens + response.usage.output_tokens,
                'cost_estimate_usd': self._estimate_cost(response.usage.input_tokens, response.usage.output_tokens)
            }
            
            # Add usage for cost tracking
            analysis['usage'] = {
                'input_tokens': response.usage.input_tokens,
                'output_tokens': response.usage.output_tokens
            }
            
            logger.info(f"✅ Analysis complete ({response.usage.input_tokens + response.usage.output_tokens} tokens)")
            return analysis
        
        except Exception as e:
            logger.error(f"❌ Analysis failed: {e}")
            return {"error": str(e)}
    
    def extract_requirements(self, tender_text: str) -> Dict:
        """
        Extract structured requirements from tender
        
        Args:
            tender_text: Tender document text
            
        Returns:
            Dict with extracted requirements
        """
        if not self.client:
            return {"error": "Anthropic client not initialized"}
        
        logger.info("🔍 Extracting requirements...")
        
        # Truncate if needed
        max_text_length = 50000
        if len(tender_text) > max_text_length:
            tender_text = tender_text[:max_text_length]
        
        prompt = f"""
Extract and structure all requirements from this Saudi government tender document.

TENDER TEXT:
{tender_text}

Please extract and return in JSON format:

{{
  "technical_requirements": [
    "requirement 1",
    "requirement 2"
  ],
  "certifications_required": [
    "certification 1"
  ],
  "classifications_required": [
    {{"code": "XXX", "description": "..."}}
  ],
  "budget_info": {{
    "mentioned_budget": "...",
    "estimated_range": "..."
  }},
  "timeline": {{
    "project_duration": "...",
    "submission_deadline": "...",
    "start_date": "...",
    "end_date": "..."
  }},
  "deliverables": [
    "deliverable 1"
  ],
  "evaluation_criteria": {{
    "financial_weight": "...",
    "technical_weight": "...",
    "other_criteria": []
  }},
  "team_requirements": {{
    "required_roles": [],
    "minimum_experience": "...",
    "team_size_estimate": "..."
  }}
}}

Be thorough and extract all relevant information. Use "N/A" if information not found.
"""
        
        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=3000,
                messages=[
                    {"role": "user", "content": f"You are an expert at extracting structured information from tender documents.\n\n{prompt}"}
                ],
                temperature=0.1  # Very low for factual extraction
            )
            
            result = response.content[0].text
            
            # Strip markdown code blocks if present
            result = result.strip()
            if result.startswith('```json'):
                result = result[7:]  # Remove ```json
            if result.startswith('```'):
                result = result[3:]  # Remove ```
            if result.endswith('```'):
                result = result[:-3]  # Remove closing ```
            result = result.strip()
            
            # Parse JSON
            try:
                requirements = json.loads(result)
            except json.JSONDecodeError as e:
                logger.warning(f"Failed to parse requirements JSON: {e}")
                requirements = {"raw_extraction": result}
            
            logger.info(f"✅ Requirements extracted ({response.usage.input_tokens + response.usage.output_tokens} tokens)")
            return requirements
        
        except Exception as e:
            logger.error(f"❌ Requirement extraction failed: {e}")
            return {"error": str(e)}
    
    def _estimate_cost(self, input_tokens: int, output_tokens: int) -> float:
        """
        Estimate API call cost in USD
        
        Args:
            input_tokens: Input tokens used
            output_tokens: Output tokens generated
            
        Returns:
            Estimated cost in USD
        """
        # Claude Sonnet 4 pricing (as of 2025):
        # Input: $3.00 per 1M tokens
        # Output: $15.00 per 1M tokens
        
        cost = (input_tokens / 1_000_000 * 3.00) + (output_tokens / 1_000_000 * 15.00)
        return round(cost, 4)
    
    def _extract_recommendation(self, text: str) -> str:
        """Extract recommendation from text"""
        text_lower = text.lower()
        if any(word in text_lower for word in ['proceed', 'yes', 'recommended', 'يُنصح', 'نعم', 'مناسب']):
            return 'PROCEED'
        elif any(word in text_lower for word in ['consider', 'maybe', 'possible', 'محتمل', 'ربما']):
            return 'CONSIDER'
        else:
            return 'SKIP'
    
    def _extract_confidence(self, text: str) -> str:
        """Extract confidence level from text"""
        text_lower = text.lower()
        if any(word in text_lower for word in ['high confidence', 'very confident', 'عالية', 'كبيرة']):
            return 'High'
        elif any(word in text_lower for word in ['medium', 'moderate', 'متوسطة']):
            return 'Medium'
        else:
            return 'Low'
    
    def _extract_priority(self, text: str) -> str:
        """Extract priority from text"""
        text_lower = text.lower()
        if any(word in text_lower for word in ['high priority', 'urgent', 'عالية', 'عاجل']):
            return 'High'
        elif any(word in text_lower for word in ['medium priority', 'moderate', 'متوسطة']):
            return 'Medium'
        else:
            return 'Low'
    
    def _extract_list(self, text: str, keywords: list) -> list:
        """Extract list items containing keywords"""
        items = []
        for line in text.split('\n'):
            line = line.strip()
            if any(keyword in line.lower() for keyword in keywords):
                # Clean the line
                line = line.lstrip('- *•').strip()
                if line and len(line) > 10:  # Meaningful line
                    items.append(line[:200])  # Limit length
                    if len(items) >= 5:  # Max 5 items
                        break
        return items if items else ["Analysis available in full report"]
    
    def get_usage_stats(self) -> Dict:
        """Get API usage statistics (if available)"""
        # This would need to track usage across sessions
        # For now, return empty stats
        return {
            "total_requests": 0,
            "total_tokens": 0,
            "estimated_cost": 0.0
        }


if __name__ == "__main__":
    # Test the module
    print("=" * 60)
    print("AI Analyzer Test")
    print("=" * 60)
    
    # Check for API key
    api_key = os.getenv('ANTHROPIC_API_KEY')
    
    if not api_key:
        print("\n⚠️ ANTHROPIC_API_KEY not found in environment variables")
        print("\nTo use this module:")
        print("1. Get an API key from: https://console.anthropic.com/settings/keys")
        print("2. Create a .env file with: ANTHROPIC_API_KEY=your-key-here")
        print("3. Or set environment variable: set ANTHROPIC_API_KEY=your-key-here")
    else:
        print("\n✅ API key found!")
        
        analyzer = AIAnalyzer(api_key)
        
        if analyzer.client:
            print("\n🤖 Testing with sample tender text...\n")
            
            sample_text = """
مشروع تطوير نظام إدارة الموارد البشرية
رقم المنافسة: 1234567890

الجهة المشترية: وزارة الموارد البشرية والتنمية الاجتماعية

المتطلبات الفنية:
- تطوير نظام متكامل لإدارة الموارد البشرية
- يدعم اللغتين العربية والإنجليزية
- قاعدة بيانات آمنة ومشفرة
- واجهة مستخدم سهلة وحديثة
- تكامل مع أنظمة الحكومة الإلكترونية

المتطلبات القانونية:
- التصنيف المطلوب: 701 (خدمات تقنية المعلومات)
- شهادة ISO 27001
- خبرة لا تقل عن 5 سنوات

القيمة التقديرية: 5,000,000 ريال سعودي
مدة التنفيذ: 12 شهراً
آخر موعد للتقديم: 2025-11-30
"""
            
            # Test summary
            from company_context import get_company_context
            context = get_company_context()
            company_summary = context.get_summary_for_ai()
            
            result = analyzer.analyze_tender_summary(sample_text, company_summary)
            
            # save the json result to a file
            output_path = Path(__file__).parent / 'sample_tender_analysis.json'
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(result, f, ensure_ascii=False, indent=2)
            
            print("📊 Analysis Result:")
            print(json.dumps(result, ensure_ascii=False, indent=2))
            
            if '_metadata' in result:
                print(f"\n💰 Cost: ${result['_metadata']['cost_estimate_usd']:.4f}")
                print(f"🎯 Tokens: {result['_metadata']['tokens_used']}")
