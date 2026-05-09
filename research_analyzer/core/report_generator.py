from fpdf import FPDF
import os
from datetime import datetime
import matplotlib.pyplot as plt
from collections import Counter
import textwrap
import logging
from typing import List, Dict
from ..utils.error_handler import handle_error

logger = logging.getLogger(__name__)

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
        self.set_font('Helvetica', 'B', 20)
        self.cell(0, 10, title, 0, 1, 'L')
        self.ln(10)

    def chapter_body(self, body):
        self.set_font('Helvetica', '', 12)
        lines = textwrap.wrap(body, width=90)
        for line in lines:
            self.cell(0, 10, line, 0, 1)
        self.ln()

def generate_report(papers: List[Dict], model_results: Dict[str, str], output_dir: str = 'results') -> str:
    """Generate a PDF report from analyzed papers and model results."""
    try:
        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
        
        # Initialize report
        pdf = ResearchReport()
        
        # Title
        pdf.cell(0, 10, 'Medical Research Daily Update', 0, 1, 'C')
        pdf.cell(0, 10, datetime.now().strftime("%Y-%m-%d"), 0, 1, 'C')
        pdf.ln(20)
        
        # Summary of findings
        pdf.chapter_title('Key Findings')
        
        # Only include successful model results
        successful_analyses = {
            model: result for model, result in model_results.items()
            if not result.startswith('Error:')
        }
        
        if successful_analyses:
            for model, analysis in successful_analyses.items():
                pdf.set_font('Helvetica', 'B', 14)
                pdf.cell(0, 10, f'Analysis by {model}:', 0, 1)
                pdf.chapter_body(analysis)
                pdf.ln(10)
        else:
            pdf.chapter_body("No successful model analyses available for today's papers.")
        
        # Papers section
        if papers:
            pdf.add_page()
            pdf.chapter_title('Analyzed Papers')
            
            for paper in papers:
                pdf.set_font('Helvetica', 'B', 14)
                pdf.cell(0, 10, paper.get('title', 'Untitled'), 0, 1)
                
                pdf.set_font('Helvetica', 'I', 12)
                authors = paper.get('authors', [])
                if authors:
                    pdf.cell(0, 10, f"Authors: {', '.join(authors)}", 0, 1)
                
                pdf.set_font('Helvetica', '', 12)
                abstract = paper.get('abstract', 'No abstract available')
                pdf.multi_cell(0, 10, abstract)
                pdf.ln(10)
        
        # Generate output filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d")
        output_file = os.path.join(output_dir, f'medical_research_report_{timestamp}.pdf')
        
        # Save PDF
        pdf.output(output_file)
        logger.info(f"Report generated successfully: {output_file}")
        
        return output_file
        
    except Exception as e:
        error_msg = f"Error generating report: {str(e)}"
        logger.error(error_msg)
        handle_error(error_msg)
        return None
