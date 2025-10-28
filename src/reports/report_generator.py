"""
Report Generator Module
Generates professional PDF reports for tender analysis
"""

import logging
import os
from pathlib import Path
from typing import Dict, Optional
from datetime import datetime
import json

from jinja2 import Environment, FileSystemLoader, select_autoescape
from weasyprint import HTML, CSS
from weasyprint.text.fonts import FontConfiguration

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ReportGenerator:
    """Generate professional PDF reports from analysis data"""
    
    def __init__(self, template_dir: Optional[str] = None):
        """
        Initialize Report Generator
        
        Args:
            template_dir: Directory containing Jinja2 templates
        """
        if template_dir is None:
            # Default to data/analysis_templates
            project_root = Path(__file__).parent.parent
            template_dir = project_root / 'data' / 'analysis_templates'
        
        self.template_dir = Path(template_dir)
        self.template_dir.mkdir(parents=True, exist_ok=True)
        
        # Setup Jinja2 environment
        self.jinja_env = Environment(
            loader=FileSystemLoader(str(self.template_dir)),
            autoescape=select_autoescape(['html', 'xml'])
        )
        
        # Font configuration for Arabic support
        self.font_config = FontConfiguration()
        
        logger.info("✅ Report Generator initialized")
    
    def generate_report(
        self, 
        analysis_data: Dict,
        output_path: Optional[Path] = None,
        language: str = 'ar',
        format: str = 'pdf'
    ) -> Path:
        """
        Generate analysis report
        
        Args:
            analysis_data: Complete analysis results
            output_path: Where to save the report (optional)
            language: Report language ('ar' or 'en')
            format: Output format ('pdf' or 'html')
            
        Returns:
            Path to generated report
        """
        logger.info(f"📄 Generating {language.upper()} report...")
        
        # Prepare data for template
        template_data = self._prepare_template_data(analysis_data, language)
        
        # Render HTML from template
        html_content = self._render_template(template_data, language)
        
        # Determine output path
        if output_path is None:
            tender_ref = analysis_data.get('tender_reference', 'unknown')
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"analysis_{tender_ref}_{language}_{timestamp}.{format}"
            
            project_root = Path(__file__).parent.parent
            output_dir = project_root / 'data' / 'tender_analyses'
            output_dir.mkdir(parents=True, exist_ok=True)
            output_path = output_dir / filename
        
        output_path = Path(output_path)
        
        # Generate output
        if format == 'pdf':
            self._generate_pdf(html_content, output_path)
        else:
            # Save as HTML
            output_path.write_text(html_content, encoding='utf-8')
        
        logger.info(f"✅ Report saved: {output_path}")
        return output_path
    
    def _prepare_template_data(self, analysis_data: Dict, language: str) -> Dict:
        """Prepare and enrich data for template"""
        
        # Add language-specific labels
        labels = self._get_labels(language)
        
        # Calculate summary metrics
        summary = self._calculate_summary_metrics(analysis_data)
        
        # Format numbers for display
        formatted_data = self._format_numbers(analysis_data)
        
        return {
            'labels': labels,
            'language': language,
            'direction': 'rtl' if language == 'ar' else 'ltr',
            'analysis': formatted_data,
            'summary': summary,
            'generated_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'generated_date': datetime.now().strftime('%Y-%m-%d')
        }
    
    def _get_labels(self, language: str) -> Dict:
        """Get localized labels"""
        
        if language == 'ar':
            return {
                'title': 'تقرير تحليل المنافسة',
                'executive_summary': 'الملخص التنفيذي',
                'tender_details': 'تفاصيل المنافسة',
                'financial_evaluation': 'التقييم المالي',
                'technical_evaluation': 'التقييم الفني',
                'risk_assessment': 'تقييم المخاطر',
                'market_research': 'البحث السوقي',
                'recommendations': 'التوصيات',
                'tender_reference': 'رقم المنافسة',
                'priority': 'الأولوية',
                'fit_score': 'نسبة الملاءمة',
                'suggested_bid': 'السعر المقترح',
                'expected_profit': 'الربح المتوقع',
                'win_probability': 'احتمالية الفوز',
                'total_cost': 'التكلفة الإجمالية',
                'profit_margin': 'هامش الربح',
                'roi': 'العائد على الاستثمار',
                'high': 'عالي',
                'medium': 'متوسط',
                'low': 'منخفض',
                'yes': 'نعم',
                'no': 'لا',
                'sar': 'ريال',
                'cost_breakdown': 'تفصيل التكاليف',
                'labor_costs': 'تكاليف العمالة',
                'materials_costs': 'تكاليف المواد',
                'equipment_costs': 'تكاليف المعدات',
                'overhead': 'المصاريف الإدارية',
                'contingency': 'احتياطي الطوارئ',
                'risks': 'المخاطر',
                'similar_tenders': 'منافسات مشابهة',
                'suppliers': 'الموردون',
                'certifications_match': 'الشهادات المتوفرة',
                'certifications_missing': 'الشهادات المطلوبة',
                'capability_score': 'درجة القدرات',
                'feasibility': 'الجدوى',
                'page': 'صفحة',
                'generated_on': 'تاريخ الإنشاء'
            }
        else:  # English
            return {
                'title': 'Tender Analysis Report',
                'executive_summary': 'Executive Summary',
                'tender_details': 'Tender Details',
                'financial_evaluation': 'Financial Evaluation',
                'technical_evaluation': 'Technical Evaluation',
                'risk_assessment': 'Risk Assessment',
                'market_research': 'Market Research',
                'recommendations': 'Recommendations',
                'tender_reference': 'Tender Reference',
                'priority': 'Priority',
                'fit_score': 'Fit Score',
                'suggested_bid': 'Suggested Bid',
                'expected_profit': 'Expected Profit',
                'win_probability': 'Win Probability',
                'total_cost': 'Total Cost',
                'profit_margin': 'Profit Margin',
                'roi': 'Return on Investment',
                'high': 'High',
                'medium': 'Medium',
                'low': 'Low',
                'yes': 'Yes',
                'no': 'No',
                'sar': 'SAR',
                'cost_breakdown': 'Cost Breakdown',
                'labor_costs': 'Labor Costs',
                'materials_costs': 'Materials Costs',
                'equipment_costs': 'Equipment Costs',
                'overhead': 'Overhead',
                'contingency': 'Contingency',
                'risks': 'Risks',
                'similar_tenders': 'Similar Tenders',
                'suppliers': 'Suppliers',
                'certifications_match': 'Certifications Available',
                'certifications_missing': 'Certifications Required',
                'capability_score': 'Capability Score',
                'feasibility': 'Feasibility',
                'page': 'Page',
                'generated_on': 'Generated on'
            }
    
    def _calculate_summary_metrics(self, analysis_data: Dict) -> Dict:
        """Calculate summary metrics for dashboard"""
        
        summary = {
            'priority': 'MEDIUM',
            'priority_color': 'orange',
            'decision': 'CONSIDER',
            'decision_icon': '⚠️'
        }
        
        # Get scores from different evaluations
        tech_eval = analysis_data.get('technical_evaluation', {})
        fin_eval = analysis_data.get('financial_evaluation', {})
        
        capability_score = tech_eval.get('capability_match', {}).get('overall_score', 0)
        profit_margin = fin_eval.get('profitability', {}).get('profit_margin_percentage', 0)
        can_deliver = tech_eval.get('feasibility', {}).get('can_deliver', False)
        
        # Determine priority
        if capability_score >= 70 and profit_margin >= 15 and can_deliver:
            summary['priority'] = 'HIGH'
            summary['priority_color'] = 'green'
            summary['decision'] = 'PROCEED'
            summary['decision_icon'] = '✅'
        elif capability_score >= 60 and profit_margin >= 10 and can_deliver:
            summary['priority'] = 'MEDIUM'
            summary['priority_color'] = 'orange'
            summary['decision'] = 'CONSIDER'
            summary['decision_icon'] = '⚠️'
        elif capability_score < 40 or profit_margin < 5:
            summary['priority'] = 'LOW'
            summary['priority_color'] = 'red'
            summary['decision'] = 'SKIP'
            summary['decision_icon'] = '❌'
        
        return summary
    
    def _format_numbers(self, data: Dict) -> Dict:
        """Format numbers for display"""
        # This is a deep copy to avoid modifying original data
        import copy
        formatted = copy.deepcopy(data)
        
        # Format financial numbers
        if 'financial_evaluation' in formatted:
            fin = formatted['financial_evaluation']
            
            # Format cost breakdown
            if 'cost_breakdown' in fin:
                for key in fin['cost_breakdown']:
                    if isinstance(fin['cost_breakdown'][key], (int, float)):
                        fin['cost_breakdown'][key] = f"{fin['cost_breakdown'][key]:,.2f}"
            
            # Format pricing
            if 'pricing_analysis' in fin:
                for key in fin['pricing_analysis']:
                    if isinstance(fin['pricing_analysis'][key], (int, float)):
                        fin['pricing_analysis'][key] = f"{fin['pricing_analysis'][key]:,.2f}"
            
            # Format profitability
            if 'profitability' in fin:
                for key in fin['profitability']:
                    if isinstance(fin['profitability'][key], (int, float)):
                        if 'percentage' in key:
                            fin['profitability'][key] = f"{fin['profitability'][key]:.1f}%"
                        else:
                            fin['profitability'][key] = f"{fin['profitability'][key]:,.2f}"
        
        # Format technical scores
        if 'technical_evaluation' in formatted:
            tech = formatted['technical_evaluation']
            
            if 'capability_match' in tech and 'overall_score' in tech['capability_match']:
                tech['capability_match']['overall_score'] = f"{tech['capability_match']['overall_score']:.1f}%"
            
            if 'feasibility' in tech and 'score' in tech['feasibility']:
                tech['feasibility']['score'] = f"{tech['feasibility']['score']:.1f}%"
        
        return formatted
    
    def _render_template(self, data: Dict, language: str) -> str:
        """Render HTML template with data"""
        
        template_name = f'report_template_{language}.html'
        
        # Check if template exists, if not create default
        template_path = self.template_dir / template_name
        if not template_path.exists():
            logger.warning(f"Template {template_name} not found, creating default template")
            self._create_default_template(language)
        
        try:
            template = self.jinja_env.get_template(template_name)
            html = template.render(**data)
            return html
        except Exception as e:
            logger.error(f"Template rendering failed: {e}")
            # Return simple HTML as fallback
            return self._generate_simple_html(data)
    
    def _generate_pdf(self, html_content: str, output_path: Path):
        """Convert HTML to PDF using WeasyPrint"""
        
        try:
            # Add CSS for better PDF rendering
            css = CSS(string=self._get_pdf_css(), font_config=self.font_config)
            
            # Generate PDF
            HTML(string=html_content).write_pdf(
                output_path,
                stylesheets=[css],
                font_config=self.font_config
            )
            
        except Exception as e:
            logger.error(f"PDF generation failed: {e}")
            # Save as HTML instead
            html_path = output_path.with_suffix('.html')
            html_path.write_text(html_content, encoding='utf-8')
            logger.info(f"Saved as HTML instead: {html_path}")
            raise
    
    def _get_pdf_css(self) -> str:
        """Get CSS for PDF rendering"""
        return """
        @page {
            size: A4;
            margin: 2cm;
        }
        
        body {
            font-family: 'Arial', 'Tahoma', sans-serif;
            line-height: 1.6;
            color: #333;
        }
        
        h1, h2, h3 {
            color: #2c3e50;
            page-break-after: avoid;
        }
        
        table {
            width: 100%;
            border-collapse: collapse;
            margin: 1em 0;
            page-break-inside: avoid;
        }
        
        th, td {
            border: 1px solid #ddd;
            padding: 8px;
            text-align: left;
        }
        
        th {
            background-color: #f2f2f2;
        }
        
        .page-break {
            page-break-after: always;
        }
        
        .metric-box {
            border: 2px solid #3498db;
            padding: 15px;
            margin: 10px 0;
            border-radius: 5px;
            page-break-inside: avoid;
        }
        
        .high-priority { color: #27ae60; font-weight: bold; }
        .medium-priority { color: #f39c12; font-weight: bold; }
        .low-priority { color: #e74c3c; font-weight: bold; }
        """
    
    def _create_default_template(self, language: str):
        """Create a default template if none exists"""
        
        template_content = self._get_default_template(language)
        template_name = f'report_template_{language}.html'
        template_path = self.template_dir / template_name
        
        template_path.write_text(template_content, encoding='utf-8')
        logger.info(f"Created default template: {template_path}")
    
    def _get_default_template(self, language: str) -> str:
        """Get default template content"""
        
        if language == 'ar':
            return '''<!DOCTYPE html>
<html dir="rtl" lang="ar">
<head>
    <meta charset="UTF-8">
    <title>{{ labels.title }}</title>
    <style>
        body { font-family: 'Arial', 'Tahoma', sans-serif; direction: rtl; }
        .header { background: #2c3e50; color: white; padding: 20px; text-align: center; }
        .section { margin: 20px 0; padding: 15px; border: 1px solid #ddd; }
        .metric { display: inline-block; margin: 10px; padding: 15px; background: #ecf0f1; border-radius: 5px; }
        table { width: 100%; border-collapse: collapse; margin: 15px 0; }
        th, td { border: 1px solid #ddd; padding: 8px; text-align: right; }
        th { background: #34495e; color: white; }
        .high { color: green; font-weight: bold; }
        .medium { color: orange; font-weight: bold; }
        .low { color: red; font-weight: bold; }
    </style>
</head>
<body>
    <div class="header">
        <h1>{{ labels.title }}</h1>
        <p>{{ labels.tender_reference }}: {{ analysis.tender_reference }}</p>
        <p>{{ labels.generated_on }}: {{ generated_at }}</p>
    </div>
    
    <div class="section">
        <h2>{{ labels.executive_summary }}</h2>
        <div class="metric">
            <strong>{{ labels.priority }}:</strong> 
            <span class="{{ summary.priority|lower }}">{{ summary.priority }}</span>
        </div>
        <div class="metric">
            <strong>{{ labels.fit_score }}:</strong> 
            {{ analysis.technical_evaluation.capability_match.overall_score }}
        </div>
        <div class="metric">
            <strong>{{ labels.suggested_bid }}:</strong> 
            {{ analysis.financial_evaluation.pricing_analysis.recommended_bid }} {{ labels.sar }}
        </div>
    </div>
    
    <div class="section">
        <h2>{{ labels.financial_evaluation }}</h2>
        <h3>{{ labels.cost_breakdown }}</h3>
        <table>
            <tr>
                <th>البند</th>
                <th>المبلغ ({{ labels.sar }})</th>
            </tr>
            <tr>
                <td>{{ labels.labor_costs }}</td>
                <td>{{ analysis.financial_evaluation.cost_breakdown.labor_costs }}</td>
            </tr>
            <tr>
                <td>{{ labels.materials_costs }}</td>
                <td>{{ analysis.financial_evaluation.cost_breakdown.materials_costs }}</td>
            </tr>
            <tr>
                <td>{{ labels.overhead }}</td>
                <td>{{ analysis.financial_evaluation.cost_breakdown.overhead }}</td>
            </tr>
            <tr>
                <td>{{ labels.contingency }}</td>
                <td>{{ analysis.financial_evaluation.cost_breakdown.contingency }}</td>
            </tr>
            <tr>
                <th>{{ labels.total_cost }}</th>
                <th>{{ analysis.financial_evaluation.cost_breakdown.total_cost }}</th>
            </tr>
        </table>
    </div>
    
    <div class="section">
        <h2>{{ labels.technical_evaluation }}</h2>
        <p><strong>{{ labels.capability_score }}:</strong> {{ analysis.technical_evaluation.capability_match.overall_score }}</p>
        <p><strong>{{ labels.feasibility }}:</strong> {{ analysis.technical_evaluation.feasibility.level }}</p>
        
        <h3>{{ labels.risks }}</h3>
        <ul>
        {% for risk in analysis.technical_evaluation.risks %}
            <li><strong>[{{ risk.severity }}]</strong> {{ risk.description }}</li>
        {% endfor %}
        </ul>
    </div>
    
    <div class="section">
        <h2>{{ labels.recommendations }}</h2>
        <ul>
        {% for rec in analysis.financial_evaluation.recommendations %}
            <li>{{ rec }}</li>
        {% endfor %}
        {% for rec in analysis.technical_evaluation.recommendations %}
            <li>{{ rec }}</li>
        {% endfor %}
        </ul>
    </div>
</body>
</html>'''
        else:  # English
            return '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>{{ labels.title }}</title>
    <style>
        body { font-family: Arial, sans-serif; }
        .header { background: #2c3e50; color: white; padding: 20px; text-align: center; }
        .section { margin: 20px 0; padding: 15px; border: 1px solid #ddd; }
        .metric { display: inline-block; margin: 10px; padding: 15px; background: #ecf0f1; border-radius: 5px; }
        table { width: 100%; border-collapse: collapse; margin: 15px 0; }
        th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
        th { background: #34495e; color: white; }
        .high { color: green; font-weight: bold; }
        .medium { color: orange; font-weight: bold; }
        .low { color: red; font-weight: bold; }
    </style>
</head>
<body>
    <div class="header">
        <h1>{{ labels.title }}</h1>
        <p>{{ labels.tender_reference }}: {{ analysis.tender_reference }}</p>
        <p>{{ labels.generated_on }}: {{ generated_at }}</p>
    </div>
    
    <div class="section">
        <h2>{{ labels.executive_summary }}</h2>
        <div class="metric">
            <strong>{{ labels.priority }}:</strong> 
            <span class="{{ summary.priority|lower }}">{{ summary.priority }}</span>
        </div>
        <div class="metric">
            <strong>{{ labels.fit_score }}:</strong> 
            {{ analysis.technical_evaluation.capability_match.overall_score }}
        </div>
        <div class="metric">
            <strong>{{ labels.suggested_bid }}:</strong> 
            {{ labels.sar }} {{ analysis.financial_evaluation.pricing_analysis.recommended_bid }}
        </div>
    </div>
    
    <div class="section">
        <h2>{{ labels.financial_evaluation }}</h2>
        <h3>{{ labels.cost_breakdown }}</h3>
        <table>
            <tr>
                <th>Item</th>
                <th>Amount ({{ labels.sar }})</th>
            </tr>
            <tr>
                <td>{{ labels.labor_costs }}</td>
                <td>{{ analysis.financial_evaluation.cost_breakdown.labor_costs }}</td>
            </tr>
            <tr>
                <td>{{ labels.materials_costs }}</td>
                <td>{{ analysis.financial_evaluation.cost_breakdown.materials_costs }}</td>
            </tr>
            <tr>
                <td>{{ labels.overhead }}</td>
                <td>{{ analysis.financial_evaluation.cost_breakdown.overhead }}</td>
            </tr>
            <tr>
                <td>{{ labels.contingency }}</td>
                <td>{{ analysis.financial_evaluation.cost_breakdown.contingency }}</td>
            </tr>
            <tr>
                <th>{{ labels.total_cost }}</th>
                <th>{{ analysis.financial_evaluation.cost_breakdown.total_cost }}</th>
            </tr>
        </table>
    </div>
    
    <div class="section">
        <h2>{{ labels.technical_evaluation }}</h2>
        <p><strong>{{ labels.capability_score }}:</strong> {{ analysis.technical_evaluation.capability_match.overall_score }}</p>
        <p><strong>{{ labels.feasibility }}:</strong> {{ analysis.technical_evaluation.feasibility.level }}</p>
        
        <h3>{{ labels.risks }}</h3>
        <ul>
        {% for risk in analysis.technical_evaluation.risks %}
            <li><strong>[{{ risk.severity }}]</strong> {{ risk.description }}</li>
        {% endfor %}
        </ul>
    </div>
    
    <div class="section">
        <h2>{{ labels.recommendations }}</h2>
        <ul>
        {% for rec in analysis.financial_evaluation.recommendations %}
            <li>{{ rec }}</li>
        {% endfor %}
        {% for rec in analysis.technical_evaluation.recommendations %}
            <li>{{ rec }}</li>
        {% endfor %}
        </ul>
    </div>
</body>
</html>'''
    
    def _generate_simple_html(self, data: Dict) -> str:
        """Generate simple HTML fallback"""
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>Tender Analysis Report</title>
        </head>
        <body>
            <h1>Tender Analysis Report</h1>
            <pre>{json.dumps(data, ensure_ascii=False, indent=2)}</pre>
        </body>
        </html>
        """


if __name__ == "__main__":
    # Test the module
    print("=" * 60)
    print("Report Generator Test")
    print("=" * 60)
    
    # Create sample analysis data
    sample_analysis = {
        'tender_reference': '251039009436',
        'financial_evaluation': {
            'cost_breakdown': {
                'labor_costs': 540000.00,
                'materials_costs': 162000.00,
                'equipment_costs': 0.00,
                'subcontractor_costs': 0.00,
                'licensing_costs': 0.00,
                'subtotal': 702000.00,
                'overhead': 105300.00,
                'contingency': 56160.00,
                'total_cost': 863460.00
            },
            'pricing_analysis': {
                'minimum_price': 949806.00,
                'target_price': 1036152.00,
                'maximum_price': 1122498.00,
                'recommended_bid': 1036152.00,
                'strategy': 'Standard - Target margin'
            },
            'profitability': {
                'expected_profit': 172692.00,
                'profit_margin_percentage': 16.67,
                'roi_percentage': 20.00,
                'break_even_price': 863460.00
            },
            'recommendations': [
                '✅ Healthy profit margin - Good opportunity',
                '💡 Consider optimizing team size to reduce labor costs'
            ]
        },
        'technical_evaluation': {
            'capability_match': {
                'overall_score': 75.5,
                'certifications_match': ['ISO 9001'],
                'certifications_missing': ['ISO 27001'],
                'experience_adequate': True,
                'team_adequate': True
            },
            'feasibility': {
                'level': 'High',
                'score': 75.5,
                'description': 'Strong capability match - Highly feasible',
                'can_deliver': True
            },
            'risks': [
                {
                    'type': 'Certification',
                    'severity': 'High',
                    'description': 'Missing certifications: ISO 27001',
                    'mitigation': 'Obtain required certifications before bidding'
                },
                {
                    'type': 'Technical Capability',
                    'severity': 'Medium',
                    'description': 'Capability gaps in: React Native',
                    'mitigation': 'Hire experts or provide training'
                }
            ],
            'recommendations': [
                '✅ Strong technical fit - Proceed with confidence',
                '📜 Obtain certifications: ISO 27001',
                '🎓 Build capabilities in: React Native'
            ]
        },
        'market_research': {
            'similar_tenders': [
                {'title': 'Similar Project', 'url': 'https://example.com'}
            ],
            'pricing_data': {
                'avg_salary': 15000
            }
        }
    }
    
    print("\n📄 Testing report generation...\n")
    
    generator = ReportGenerator()
    
    # Generate Arabic report
    print("Generating Arabic report...")
    ar_report = generator.generate_report(sample_analysis, language='ar', format='html')
    print(f"✅ Arabic report: {ar_report}")
    
    # Generate English report
    print("\nGenerating English report...")
    en_report = generator.generate_report(sample_analysis, language='en', format='html')
    print(f"✅ English report: {en_report}")
    
    print("\n✅ Report generation test complete!")
    print(f"\nReports saved in: {ar_report.parent}")
