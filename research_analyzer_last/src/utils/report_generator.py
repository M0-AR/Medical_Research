from fpdf import FPDF
import os
from datetime import datetime
import matplotlib.pyplot as plt
from collections import Counter
import textwrap
import re

def clean_text(text):
    """Clean text to remove unsupported characters"""
    if not isinstance(text, str):
        return str(text)
    # Replace special characters with closest ASCII equivalent
    text = text.encode('ascii', 'replace').decode()
    # Remove any remaining non-printable characters
    text = ''.join(char if ord(char) < 128 else '?' for char in text)
    return text

def categorize_paper(title, abstract):
    """Categorize paper based on title and abstract"""
    text = (title + " " + abstract).lower()
    categories = []
    
    if any(term in text for term in ['treatment', 'therapy', 'therapeutic', 'drug', 'medication']):
        categories.append('Treatment & Therapeutics')
    if any(term in text for term in ['diagnostic', 'diagnosis', 'detection', 'screening', 'imaging']):
        categories.append('Diagnostics & Detection')
    if any(term in text for term in ['device', 'technology', 'equipment', 'instrument']):
        categories.append('Medical Devices')
    if any(term in text for term in ['public health', 'population', 'epidemiology', 'prevention']):
        categories.append('Public Health')
    if any(term in text for term in ['clinical trial', 'phase', 'randomized']):
        categories.append('Clinical Trials')
    
    return categories or ['Other Research']

class ResearchReport(FPDF):
    def __init__(self):
        super().__init__()
        self.set_auto_page_break(auto=True, margin=15)
        self.add_page()
        self.set_font('Helvetica', 'B', 24)
        
    def header(self):
        if self.page_no() == 1:  # Only on first page
            return
        self.set_font('Helvetica', 'I', 10)
        self.cell(0, 10, f'Medical Research Daily Update - {datetime.now().strftime("%Y-%m-%d")}', 0, 1, 'R')
        self.ln(10)

    def footer(self):
        self.set_y(-15)
        self.set_font('Helvetica', 'I', 8)
        self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')

    def chapter_title(self, title):
        self.set_font('Helvetica', 'B', 16)
        self.ln(10)
        self.cell(0, 10, clean_text(title), 0, 1, 'L')
        self.ln(5)

    def chapter_body(self, text):
        self.set_font('Helvetica', '', 11)
        # Split text into lines that fit the page width
        lines = textwrap.wrap(clean_text(text), width=90)
        for line in lines:
            self.cell(0, 5, line, 0, 1, 'L')
        self.ln(5)

    def add_source_statistics(self, papers):
        self.chapter_title("Research Overview")
        
        # Count papers by source
        source_counts = Counter(paper['source'] for paper in papers)
        
        # Count papers by category
        category_counts = Counter()
        for paper in papers:
            categories = categorize_paper(paper['title'], paper.get('abstract', ''))
            for category in categories:
                category_counts[category] += 1
        
        # Create source distribution pie chart
        plt.figure(figsize=(8, 6))
        plt.subplot(1, 2, 1)
        plt.pie(source_counts.values(), labels=source_counts.keys(), autopct='%1.1f%%')
        plt.title('Papers by Source')
        
        # Create category distribution pie chart
        plt.subplot(1, 2, 2)
        plt.pie(category_counts.values(), labels=category_counts.keys(), autopct='%1.1f%%')
        plt.title('Papers by Category')
        
        # Save the plot to a temporary file
        temp_plot = 'temp_plot.png'
        plt.savefig(temp_plot, bbox_inches='tight')
        plt.close()
        
        # Add the plot to the PDF
        self.image(temp_plot, x=10, w=190)
        self.ln(10)
        
        # Clean up
        os.remove(temp_plot)

def generate_report(papers, output_file='medical_research_report.pdf'):
    """Generate a PDF report from the analyzed papers."""
    
    pdf = ResearchReport()
    
    # Title Page
    pdf.set_font('Helvetica', 'B', 24)
    pdf.cell(0, 60, 'Medical Research', 0, 1, 'C')
    pdf.set_font('Helvetica', 'B', 16)
    pdf.cell(0, 10, 'Daily Update Report', 0, 1, 'C')
    pdf.set_font('Helvetica', '', 12)
    pdf.cell(0, 10, datetime.now().strftime("%Y-%m-%d"), 0, 1, 'C')
    
    # Add source and category statistics
    pdf.add_source_statistics(papers)
    
    # Executive Summary
    pdf.add_page()
    pdf.chapter_title("Executive Summary")
    
    # Categorize papers
    papers_by_category = {}
    for paper in papers:
        categories = categorize_paper(paper['title'], paper.get('abstract', ''))
        for category in categories:
            if category not in papers_by_category:
                papers_by_category[category] = []
            papers_by_category[category].append(paper)
    
    summary_text = f"""This report summarizes {len(papers)} recent medical research papers across various categories:

    Key Highlights:
    - Treatment & Therapeutics: {len(papers_by_category.get('Treatment & Therapeutics', []))} papers on new treatments and therapeutic approaches
    - Diagnostics & Detection: {len(papers_by_category.get('Diagnostics & Detection', []))} papers on diagnostic methods and disease detection
    - Medical Devices: {len(papers_by_category.get('Medical Devices', []))} papers on medical technology and devices
    - Public Health: {len(papers_by_category.get('Public Health', []))} papers on public health and prevention
    - Clinical Trials: {len(papers_by_category.get('Clinical Trials', []))} papers on ongoing clinical trials
    - Other Research: {len(papers_by_category.get('Other Research', []))} papers on various other topics
    """
    pdf.chapter_body(summary_text)
    
    # Detailed Findings by Category
    pdf.add_page()
    pdf.chapter_title("Detailed Findings")
    
    for category, category_papers in papers_by_category.items():
        if category_papers:
            pdf.set_font('Helvetica', 'B', 14)
            pdf.ln(5)
            pdf.cell(0, 10, clean_text(category), 0, 1, 'L')
            pdf.ln(5)
            
            for i, paper in enumerate(category_papers, 1):
                # Paper title
                pdf.set_font('Helvetica', 'B', 12)
                pdf.cell(0, 10, clean_text(f"{i}. {paper['title']}"), 0, 1, 'L')
                
                # Paper details
                pdf.set_font('Helvetica', '', 10)
                pdf.cell(0, 5, clean_text(f"Source: {paper['source']}"), 0, 1, 'L')
                pdf.cell(0, 5, clean_text(f"Authors: {paper.get('authors', 'N/A')}"), 0, 1, 'L')
                pdf.cell(0, 5, clean_text(f"Year: {paper.get('year', 'N/A')}"), 0, 1, 'L')
                
                # Abstract
                if paper.get('abstract'):
                    pdf.ln(5)
                    pdf.set_font('Helvetica', 'I', 10)
                    abstract_text = paper['abstract'][:500] + '...' if len(paper['abstract']) > 500 else paper['abstract']
                    pdf.multi_cell(0, 5, clean_text(abstract_text))
                
                # Add summaries if available
                for model_name, summary in paper.items():
                    if model_name.startswith('summary_'):
                        pdf.ln(5)
                        pdf.set_font('Helvetica', 'B', 10)
                        pdf.cell(0, 5, f"{model_name.replace('summary_', '').title()} Summary:", 0, 1, 'L')
                        pdf.set_font('Helvetica', '', 10)
                        summary_text = summary[:300] + '...' if len(summary) > 300 else summary
                        pdf.multi_cell(0, 5, clean_text(summary_text))
                
                pdf.ln(10)
    
    # Recommendations
    pdf.add_page()
    pdf.chapter_title("Key Takeaways & Recommendations")
    recommendations = f"""Based on today's research findings:

    1. Treatment Advances:
       - {len(papers_by_category.get('Treatment & Therapeutics', []))} new studies on treatments
       - Focus on personalized medicine and targeted therapies
       
    2. Diagnostic Improvements:
       - {len(papers_by_category.get('Diagnostics & Detection', []))} new diagnostic approaches
       - Emphasis on early detection and precision diagnostics
       
    3. Technology Integration:
       - {len(papers_by_category.get('Medical Devices', []))} new medical devices and technologies
       - Trend towards AI-enabled and smart medical devices
       
    4. Public Health Implications:
       - {len(papers_by_category.get('Public Health', []))} public health studies
       - Important findings for population health management
       
    Recommended Actions:
    1. Review promising treatments in clinical trials for potential fast-track approval
    2. Evaluate new diagnostic tools for integration into healthcare systems
    3. Consider pilot programs for innovative medical devices
    4. Update public health guidelines based on new findings"""
    
    pdf.chapter_body(recommendations)
    
    # Save the report
    try:
        pdf.output(output_file)
        print(f"\nReport generated successfully: {output_file}")
    except Exception as e:
        print(f"Error generating report: {str(e)}")
        return None
    
    return output_file
