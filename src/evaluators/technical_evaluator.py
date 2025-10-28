"""
Technical Evaluator Module
Performs technical analysis and capability matching for tenders
"""

import logging
from typing import Dict, List, Optional, Set
from datetime import datetime
import re

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TechnicalEvaluator:
    """Technical evaluation and requirements analysis for tenders"""
    
    def __init__(self, company_context: Optional[Dict] = None):
        """
        Initialize Technical Evaluator
        
        Args:
            company_context: Company profile with capabilities and certifications (CompanyContext object or dict)
        """
        # Handle both CompanyContext object and dict
        if company_context:
            if hasattr(company_context, 'profile'):
                # It's a CompanyContext object - use the profile attribute
                profile = company_context.profile
                self.company_context = profile
                self.capabilities = profile.get('capabilities', {})
                self.certifications = profile.get('certifications', [])
                self.classifications = profile.get('classifications', [])
                self.team = profile.get('team', {})
            else:
                # It's already a dict
                self.company_context = company_context
                self.capabilities = company_context.get('capabilities', {})
                self.certifications = company_context.get('certifications', [])
                self.classifications = company_context.get('classifications', [])
                self.team = company_context.get('team', {})
        else:
            self.company_context = {}
            self.capabilities = {}
            self.certifications = []
            self.classifications = []
            self.team = {}
        
        logger.info("✅ Technical Evaluator initialized")
    
    def evaluate_tender(self, tender_data: Dict, extracted_requirements: Optional[Dict] = None) -> Dict:
        """
        Perform complete technical evaluation of a tender
        
        Args:
            tender_data: Extracted tender information
            extracted_requirements: Pre-extracted requirements (from AI)
            
        Returns:
            Dict with technical evaluation results
        """
        logger.info("🔧 Starting technical evaluation...")
        
        evaluation = {
            'timestamp': datetime.now().isoformat(),
            'tender_reference': tender_data.get('reference_number', 'N/A'),
            'requirements': {},
            'capability_match': {},
            'feasibility': {},
            'risks': [],
            'recommendations': []
        }
        
        # Extract technical requirements
        requirements = self._extract_requirements(tender_data, extracted_requirements)
        evaluation['requirements'] = requirements
        
        # Match company capabilities
        capability_match = self._match_capabilities(requirements)
        evaluation['capability_match'] = capability_match
        
        # Assess feasibility
        feasibility = self._assess_feasibility(requirements, capability_match)
        evaluation['feasibility'] = feasibility
        
        # Identify risks
        risks = self._identify_risks(requirements, capability_match, feasibility)
        evaluation['risks'] = risks
        
        # Generate recommendations
        recommendations = self._generate_technical_recommendations(
            requirements, capability_match, feasibility, risks
        )
        evaluation['recommendations'] = recommendations
        
        logger.info(f"✅ Technical evaluation complete")
        logger.info(f"   Capability match: {capability_match.get('overall_score', 0):.1f}%")
        logger.info(f"   Feasibility: {feasibility.get('level', 'Unknown')}")
        
        return evaluation
    
    def _extract_requirements(self, tender_data: Dict, extracted_requirements: Optional[Dict]) -> Dict:
        """Extract technical requirements from tender data"""
        
        if extracted_requirements:
            # Use pre-extracted requirements if available
            return extracted_requirements
        
        # Otherwise, extract from tender data
        description = tender_data.get('description', '')
        requirements = tender_data.get('requirements', '')
        
        # If requirements is a dict, use it directly or convert to string
        if isinstance(requirements, dict):
            # If requirements is already structured, use it
            if any(key in requirements for key in ['certifications', 'technical', 'resources']):
                return requirements
            # Otherwise convert to string for text extraction
            requirements = str(requirements)
        
        combined_text = description + ' ' + requirements
        
        requirements_dict = {
            'certifications': self._extract_certifications(combined_text),
            'classifications': self._extract_classifications(combined_text),
            'experience_years': self._extract_experience(combined_text),
            'technical_specs': self._extract_technical_specs(combined_text),
            'team_requirements': self._extract_team_requirements(combined_text),
            'technologies': self._extract_technologies(combined_text),
            'deliverables': self._extract_deliverables(combined_text),
            'quality_standards': self._extract_quality_standards(combined_text)
        }
        
        return requirements_dict
    
    def _extract_certifications(self, text: str) -> List[str]:
        """Extract required certifications"""
        certifications = []
        
        # Common certification patterns
        cert_patterns = [
            r'ISO\s*\d+',
            r'CITC',
            r'PMP',
            r'CMMI',
            r'SADAIA',
            r'شهادة\s+[\w\s]+',
        ]
        
        for pattern in cert_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            certifications.extend(matches)
        
        return list(set(certifications))  # Remove duplicates
    
    def _extract_classifications(self, text: str) -> List[Dict]:
        """Extract required classifications"""
        classifications = []
        
        # Look for classification codes
        patterns = [
            r'تصنيف\s*(\d{3,4})',
            r'classification\s*(\d{3,4})',
            r'code\s*(\d{3,4})',
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for code in matches:
                classifications.append({'code': code, 'description': 'Required'})
        
        return classifications
    
    def _extract_experience(self, text: str) -> int:
        """Extract required years of experience"""
        patterns = [
            r'(\d+)\s*(?:سنوات?|years?)\s*(?:خبرة|experience)',
            r'(?:خبرة|experience)\s*(?:لا\s*تقل\s*عن|not less than|minimum)\s*(\d+)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return int(match.group(1))
        
        return 0
    
    def _extract_technical_specs(self, text: str) -> List[str]:
        """Extract technical specifications"""
        specs = []
        
        # Look for bullet points and numbered lists
        lines = text.split('\n')
        for line in lines:
            line = line.strip()
            if line.startswith(('-', '•', '*')) or re.match(r'^\d+[.)]', line):
                specs.append(line)
        
        return specs[:20]  # Limit to top 20
    
    def _extract_team_requirements(self, text: str) -> Dict:
        """Extract team size and composition requirements"""
        team_req = {
            'total_size': 0,
            'roles': []
        }
        
        # Look for team size
        patterns = [
            r'(\d+)\s*(?:موظف|موظفين|employees?|staff|persons?)',
            r'(?:فريق|team)\s*(?:من|of)\s*(\d+)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                team_req['total_size'] = int(match.group(1))
                break
        
        # Look for specific roles
        role_keywords = {
            'مدير مشروع': 'Project Manager',
            'مهندس': 'Engineer',
            'مطور': 'Developer',
            'مبرمج': 'Programmer',
            'محلل': 'Analyst',
            'مستشار': 'Consultant',
            'فني': 'Technician'
        }
        
        for ar_role, en_role in role_keywords.items():
            if ar_role in text or en_role.lower() in text.lower():
                team_req['roles'].append(en_role)
        
        return team_req
    
    def _extract_technologies(self, text: str) -> List[str]:
        """Extract required technologies"""
        technologies = []
        
        # Common technology keywords
        tech_keywords = [
            'Python', 'Java', 'JavaScript', 'React', 'Angular', 'Vue',
            'SQL', 'NoSQL', 'MongoDB', 'PostgreSQL', 'Oracle',
            'AWS', 'Azure', 'Google Cloud', 'Docker', 'Kubernetes',
            'AI', 'Machine Learning', 'Deep Learning',
            'Blockchain', 'IoT', 'Cloud', 'Mobile'
        ]
        
        text_lower = text.lower()
        for tech in tech_keywords:
            if tech.lower() in text_lower:
                technologies.append(tech)
        
        return technologies
    
    def _extract_deliverables(self, text: str) -> List[str]:
        """Extract project deliverables"""
        deliverables = []
        
        # Look for deliverable keywords
        deliverable_patterns = [
            r'تسليم\s+([\w\s]+)',
            r'deliver(?:able)?\s+([\w\s]+)',
            r'مخرجات\s+([\w\s]+)',
        ]
        
        for pattern in deliverable_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            deliverables.extend(matches[:10])
        
        return deliverables
    
    def _extract_quality_standards(self, text: str) -> List[str]:
        """Extract quality standards"""
        standards = []
        
        standard_keywords = [
            'ISO', 'CMMI', 'ITIL', 'COBIT', 'Prince2',
            'معايير الجودة', 'quality standards',
            'ضمان الجودة', 'quality assurance'
        ]
        
        for keyword in standard_keywords:
            if keyword.lower() in text.lower():
                standards.append(keyword)
        
        return list(set(standards))
    
    def _match_capabilities(self, requirements: Dict) -> Dict:
        """Match tender requirements to company capabilities"""
        
        match = {
            'overall_score': 0.0,
            'certifications_match': [],
            'certifications_missing': [],
            'classifications_match': [],
            'classifications_missing': [],
            'experience_adequate': False,
            'capabilities_match': [],
            'capabilities_gaps': [],
            'team_adequate': False
        }
        
        scores = []
        
        # Check certifications
        required_certs = requirements.get('certifications', [])
        for req_cert in required_certs:
            if any(req_cert.upper() in str(cert).upper() for cert in self.certifications):
                match['certifications_match'].append(req_cert)
                scores.append(100)
            else:
                match['certifications_missing'].append(req_cert)
                scores.append(0)
        
        # Check classifications
        required_classifications = requirements.get('classifications', [])
        for req_class in required_classifications:
            req_code = req_class.get('code', '')
            if any(req_code in str(cls.get('code', '')) for cls in self.classifications):
                match['classifications_match'].append(req_code)
                scores.append(100)
            else:
                match['classifications_missing'].append(req_code)
                scores.append(0)
        
        # Check experience
        required_exp = requirements.get('experience_years', 0)
        company_exp = max(
            [cap.get('experience_years', 0) for cap in self.capabilities.values()],
            default=0
        )
        if company_exp >= required_exp:
            match['experience_adequate'] = True
            scores.append(100)
        else:
            scores.append(50)
        
        # Check technologies
        required_techs = requirements.get('technologies', [])
        if required_techs:
            matched_techs = 0
            for req_tech in required_techs:
                # Check if technology is in any capability
                for cap_name, cap_data in self.capabilities.items():
                    cap_techs = cap_data.get('technologies', [])
                    cap_specs = cap_data.get('specializations', [])
                    if any(req_tech.lower() in str(t).lower() for t in cap_techs + cap_specs):
                        matched_techs += 1
                        match['capabilities_match'].append(req_tech)
                        break
                else:
                    match['capabilities_gaps'].append(req_tech)
            
            tech_score = (matched_techs / len(required_techs) * 100) if required_techs else 100
            scores.append(tech_score)
        
        # Check team capacity
        required_team = requirements.get('team_requirements', {}).get('total_size', 0)
        available_team = sum(self.team.values()) if self.team else 0
        if available_team >= required_team or required_team == 0:
            match['team_adequate'] = True
            scores.append(100)
        else:
            scores.append(50)
        
        # Calculate overall score
        match['overall_score'] = sum(scores) / len(scores) if scores else 0
        
        return match
    
    def _assess_feasibility(self, requirements: Dict, capability_match: Dict) -> Dict:
        """Assess technical feasibility"""
        
        overall_score = capability_match['overall_score']
        
        if overall_score >= 80:
            level = 'High'
            description = 'Strong capability match - Highly feasible'
        elif overall_score >= 60:
            level = 'Medium'
            description = 'Good capability match - Feasible with preparation'
        elif overall_score >= 40:
            level = 'Low'
            description = 'Partial capability match - Requires partnerships or training'
        else:
            level = 'Very Low'
            description = 'Poor capability match - High risk'
        
        feasibility = {
            'level': level,
            'score': overall_score,
            'description': description,
            'can_deliver': overall_score >= 50,
            'requires_partnerships': overall_score < 70,
            'requires_training': len(capability_match['capabilities_gaps']) > 0,
            'requires_certifications': len(capability_match['certifications_missing']) > 0
        }
        
        return feasibility
    
    def _identify_risks(self, requirements: Dict, capability_match: Dict, feasibility: Dict) -> List[Dict]:
        """Identify technical risks"""
        risks = []
        
        # Missing certifications
        if capability_match['certifications_missing']:
            risks.append({
                'type': 'Certification',
                'severity': 'High',
                'description': f"Missing certifications: {', '.join(capability_match['certifications_missing'])}",
                'mitigation': 'Obtain required certifications before bidding or partner with certified company'
            })
        
        # Missing classifications
        if capability_match['classifications_missing']:
            risks.append({
                'type': 'Classification',
                'severity': 'High',
                'description': f"Missing classifications: {', '.join(capability_match['classifications_missing'])}",
                'mitigation': 'Apply for required classifications or partner with classified company'
            })
        
        # Capability gaps
        if capability_match['capabilities_gaps']:
            risks.append({
                'type': 'Technical Capability',
                'severity': 'Medium',
                'description': f"Capability gaps in: {', '.join(capability_match['capabilities_gaps'][:5])}",
                'mitigation': 'Hire experts, provide training, or subcontract specialized work'
            })
        
        # Inadequate experience
        if not capability_match['experience_adequate']:
            risks.append({
                'type': 'Experience',
                'severity': 'Medium',
                'description': 'Required experience level not met',
                'mitigation': 'Partner with experienced company or highlight transferable experience'
            })
        
        # Team capacity
        if not capability_match['team_adequate']:
            risks.append({
                'type': 'Team Capacity',
                'severity': 'Medium',
                'description': 'Current team size may be insufficient',
                'mitigation': 'Plan for hiring or use subcontractors'
            })
        
        # Overall feasibility
        if feasibility['level'] in ['Low', 'Very Low']:
            risks.append({
                'type': 'Overall Feasibility',
                'severity': 'High',
                'description': 'Overall technical feasibility is low',
                'mitigation': 'Carefully evaluate if this tender is suitable for your company'
            })
        
        return risks
    
    def _generate_technical_recommendations(
        self,
        requirements: Dict,
        capability_match: Dict,
        feasibility: Dict,
        risks: List[Dict]
    ) -> List[str]:
        """Generate technical recommendations"""
        recommendations = []
        
        # Overall assessment
        if feasibility['score'] >= 80:
            recommendations.append('✅ Strong technical fit - Proceed with confidence')
        elif feasibility['score'] >= 60:
            recommendations.append('✅ Good technical fit - Address gaps before bidding')
        elif feasibility['score'] >= 40:
            recommendations.append('⚠️ Moderate technical fit - Consider partnerships')
        else:
            recommendations.append('❌ Weak technical fit - Reconsider bidding')
        
        # Specific actions
        if capability_match['certifications_missing']:
            certs = ', '.join(capability_match['certifications_missing'])
            recommendations.append(f'📜 Obtain certifications: {certs}')
        
        if capability_match['classifications_missing']:
            classes = ', '.join(capability_match['classifications_missing'])
            recommendations.append(f'📋 Apply for classifications: {classes}')
        
        if capability_match['capabilities_gaps']:
            gaps = ', '.join(capability_match['capabilities_gaps'][:3])
            recommendations.append(f'🎓 Build capabilities in: {gaps}')
        
        if not capability_match['team_adequate']:
            recommendations.append('👥 Expand team or plan for subcontractors')
        
        # Risk mitigation
        high_risks = [r for r in risks if r['severity'] == 'High']
        if high_risks:
            recommendations.append(f'⚠️ Address {len(high_risks)} high-severity risks before bidding')
        
        return recommendations


if __name__ == "__main__":
    # Test the module
    print("=" * 60)
    print("Technical Evaluator Test")
    print("=" * 60)
    
    # Sample company context
    from company_context import get_company_context
    context = get_company_context()
    
    evaluator = TechnicalEvaluator(context.profile)
    
    # Sample tender data
    sample_tender = {
        'reference_number': '251039009436',
        'description': '''
        مشروع تطوير نظام إدارة الموارد البشرية المتكامل
        
        المتطلبات الفنية:
        - خبرة لا تقل عن 5 سنوات في تطوير الأنظمة الحكومية
        - شهادة ISO 27001 للأمن السيبراني
        - التصنيف المطلوب: 701 (خدمات تقنية المعلومات)
        - فريق عمل لا يقل عن 8 موظفين
        - خبرة في Python و React و AWS
        
        المخرجات:
        - نظام متكامل لإدارة الموارد البشرية
        - قاعدة بيانات آمنة ومشفرة
        - واجهة مستخدم باللغتين العربية والإنجليزية
        - تطبيق موبايل (iOS و Android)
        - وثائق فنية شاملة
        - دعم فني لمدة سنة
        ''',
        'requirements': 'شهادة ISO 27001، خبرة 5 سنوات، التصنيف 701'
    }
    
    print("\n🔧 Testing technical evaluation...\n")
    
    result = evaluator.evaluate_tender(sample_tender)
    
    print(f"\n📋 Technical Evaluation Results:")
    print(f"{'='*60}")
    print(f"Tender: {result['tender_reference']}")
    
    print(f"\n✅ Requirements Extracted:")
    print(f"  Certifications: {', '.join(result['requirements']['certifications']) or 'None'}")
    print(f"  Classifications: {[c['code'] for c in result['requirements']['classifications']]}")
    print(f"  Experience Required: {result['requirements']['experience_years']} years")
    print(f"  Technologies: {', '.join(result['requirements']['technologies']) or 'None'}")
    
    print(f"\n🎯 Capability Match:")
    print(f"  Overall Score: {result['capability_match']['overall_score']:.1f}%")
    print(f"  Certifications Match: {result['capability_match']['certifications_match']}")
    print(f"  Certifications Missing: {result['capability_match']['certifications_missing']}")
    print(f"  Experience Adequate: {result['capability_match']['experience_adequate']}")
    print(f"  Team Adequate: {result['capability_match']['team_adequate']}")
    
    print(f"\n📊 Feasibility Assessment:")
    print(f"  Level: {result['feasibility']['level']}")
    print(f"  Score: {result['feasibility']['score']:.1f}%")
    print(f"  Can Deliver: {result['feasibility']['can_deliver']}")
    print(f"  Description: {result['feasibility']['description']}")
    
    print(f"\n⚠️ Risks Identified ({len(result['risks'])}):")
    for risk in result['risks']:
        print(f"  • [{risk['severity']}] {risk['type']}: {risk['description']}")
        print(f"    → Mitigation: {risk['mitigation']}")
    
    print(f"\n💡 Recommendations:")
    for rec in result['recommendations']:
        print(f"  {rec}")
    
    print(f"\n✅ Test complete!")
