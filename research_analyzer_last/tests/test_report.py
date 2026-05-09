import pytest
import os
from src.utils.report_generator import ResearchReport, generate_report

def test_report_generator_initialization():
    generator = ResearchReport()
    assert hasattr(generator, 'set_auto_page_break')
    assert hasattr(generator, 'add_page')

def test_report_generation():
    # Sample test data
    test_papers = [
        {
            'title': 'Novel Treatment for Chronic Pain Using AI-guided Drug Delivery',
            'abstract': 'This study presents a breakthrough in chronic pain management using AI-controlled drug delivery systems. The system adapts medication dosage based on real-time patient data, resulting in better pain control and fewer side effects.',
            'authors': 'John Smith, Maria Garcia, Robert Johnson',
            'year': '2024',
            'source': 'PubMed',
            'summary_gpt4': 'The research introduces an innovative AI-powered drug delivery system for chronic pain management. The system uses machine learning to optimize medication dosage based on patient vital signs and reported pain levels. Clinical trials showed a 45% improvement in pain control compared to traditional methods.',
            'summary_claude': 'A novel approach to pain management utilizing artificial intelligence to control drug delivery. The system continuously monitors patient data and adjusts medication levels accordingly. Results demonstrate significant improvements in pain control while reducing adverse effects.'
        }
    ]
    
    report_file = generate_report(test_papers, 'test_medical_report.pdf')
    assert report_file is not None
    assert os.path.exists(report_file)
    
    # Clean up
    if os.path.exists(report_file):
        os.remove(report_file)

if __name__ == "__main__":
    print("Running tests...")
    pytest.main([__file__])
