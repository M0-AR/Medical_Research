from fpdf import FPDF
import os
from datetime import datetime
import matplotlib.pyplot as plt
from collections import Counter
import textwrap
import re
from ..core.paper_analyzer import ResearchPaperAnalyzer
from ..core.config import settings

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
        self.add_font('Arial', '', 'arial.ttf', uni=True)
        self.add_font('Arial', 'B', 'arialbd.ttf', uni=True)
        self.add_page()
        
    def header(self):
        if self.page_no() == 1:  # Only on first page
            return
        self.set_font('Arial', '', 10)
        self.cell(0, 10, f'تحديث الأبحاث الطبية اليومي - {datetime.now().strftime("%Y-%m-%d")}', 0, 1, 'R')
        self.ln(10)

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', '', 8)
        self.cell(0, 10, f'الصفحة {self.page_no()}', 0, 0, 'C')

    def chapter_title(self, title):
        self.set_font('Arial', 'B', 16)
        self.cell(0, 10, title, 0, 1, 'R')
        self.ln(10)

    def chapter_body(self, body):
        self.set_font('Arial', '', 12)
        self.multi_cell(0, 10, body)
        self.ln()

async def generate_daily_report():
    """Generate a new daily research report."""
    # Initialize analyzer and get papers
    analyzer = ResearchPaperAnalyzer()
    papers = await analyzer.run_analysis()
    
    if not papers:
        raise Exception("No papers found for analysis")

    # Create PDF
    pdf = ResearchReport()
    
    # Title Page
    pdf.set_font('Arial', 'B', 24)
    pdf.cell(0, 20, 'تقرير الأبحاث الطبية اليومي', 0, 1, 'C')
    pdf.set_font('Arial', '', 14)
    pdf.cell(0, 10, f'تاريخ التقرير: {datetime.now().strftime("%Y-%m-%d")}', 0, 1, 'C')
    
    # Summary Statistics
    categories = []
    for paper in papers:
        cats = categorize_paper(paper['title'], paper['abstract'])
        categories.extend(cats)
    
    category_counts = Counter(categories)
    
    # Create pie chart of categories
    plt.figure(figsize=(10, 8))
    plt.pie(category_counts.values(), labels=category_counts.keys(), autopct='%1.1f%%')
    plt.title('توزيع فئات الأبحاث')
    
    # Save plot to file
    plot_path = settings.REPORTS_DIR / 'categories_plot.png'
    plt.savefig(plot_path)
    plt.close()
    
    # Add plot to PDF
    pdf.add_page()
    pdf.chapter_title('تحليل فئات الأبحاث')
    pdf.image(str(plot_path), x=30, w=150)
    
    # Papers Section
    pdf.add_page()
    pdf.chapter_title('ملخصات الأبحاث')
    
    for paper in papers:
        pdf.set_font('Arial', 'B', 14)
        pdf.multi_cell(0, 10, clean_text(paper['title']))
        
        pdf.set_font('Arial', '', 12)
        pdf.cell(0, 10, f"المصدر: {paper['source']}", 0, 1, 'R')
        
        if paper.get('authors'):
            pdf.cell(0, 10, f"المؤلفون: {', '.join(paper['authors'])}", 0, 1, 'R')
        
        pdf.ln(5)
        pdf.multi_cell(0, 10, clean_text(paper['abstract']))
        
        # Add model summaries if available
        for key, value in paper.items():
            if key.startswith('summary_') and value:
                model_name = key.replace('summary_', '')
                pdf.set_font('Arial', 'B', 12)
                pdf.cell(0, 10, f"ملخص {model_name}:", 0, 1, 'R')
                pdf.set_font('Arial', '', 12)
                pdf.multi_cell(0, 10, clean_text(value))
        
        pdf.ln(10)
    
    # Save the PDF
    today = datetime.now().strftime("%Y-%m-%d")
    report_path = settings.REPORTS_DIR / f"medical_report_{today}.pdf"
    pdf.output(str(report_path))
    
    # Save metadata
    metadata = {
        "generated_at": datetime.now().isoformat(),
        "paper_count": len(papers),
        "categories": dict(category_counts)
    }
    metadata_path = settings.REPORTS_DIR / "latest_report_metadata.json"
    with open(metadata_path, "w", encoding="utf-8") as f:
        json.dump(metadata, f)
    
    # Clean up plot file
    if plot_path.exists():
        os.remove(plot_path)
    
    return report_path

def get_latest_report_path():
    """Get the path to the latest report, generating one if needed."""
    today = datetime.now().strftime("%Y-%m-%d")
    report_path = settings.REPORTS_DIR / f"medical_report_{today}.pdf"
    
    if not report_path.exists():
        report_path = asyncio.run(generate_daily_report())
    
    return report_path
