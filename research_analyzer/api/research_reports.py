from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from datetime import datetime
import os
from pathlib import Path
from ..paper_analyzer import analyze_papers
from fpdf2 import FPDF
import json

router = APIRouter()

# Get the base directory for storing reports
REPORTS_DIR = Path(__file__).parent.parent.parent / "results" / "reports"
REPORTS_DIR.mkdir(parents=True, exist_ok=True)

def generate_daily_report():
    """Generate a new daily research report."""
    # Analyze papers and get results
    analysis_results = analyze_papers()
    
    # Create PDF
    pdf = FPDF()
    pdf.add_page()
    
    # Add Arabic support
    pdf.add_font('Arial', '', 'arial.ttf', uni=True)
    pdf.set_font('Arial', '', 14)
    
    # Add title
    pdf.set_font('Arial', 'B', 24)
    pdf.cell(0, 10, 'تقرير الأبحاث الطبية اليومي', align='C', ln=True)
    pdf.ln(10)
    
    # Add date
    pdf.set_font('Arial', '', 12)
    today = datetime.now().strftime("%Y-%m-%d")
    pdf.cell(0, 10, f'تاريخ التقرير: {today}', align='R', ln=True)
    pdf.ln(10)
    
    # Add content
    pdf.set_font('Arial', '', 14)
    for paper in analysis_results:
        pdf.cell(0, 10, f"عنوان البحث: {paper['title']}", ln=True)
        pdf.cell(0, 10, f"المؤلفون: {', '.join(paper['authors'])}", ln=True)
        pdf.multi_cell(0, 10, f"ملخص: {paper['summary']}")
        pdf.ln(10)
    
    # Save the PDF
    report_path = REPORTS_DIR / f"medical_report_{today}.pdf"
    pdf.output(str(report_path))
    
    # Save metadata
    metadata = {
        "generated_at": datetime.now().isoformat(),
        "paper_count": len(analysis_results)
    }
    metadata_path = REPORTS_DIR / "latest_report_metadata.json"
    with open(metadata_path, "w", encoding="utf-8") as f:
        json.dump(metadata, f)
    
    return report_path

def get_latest_report_path():
    """Get the path to the latest report, generating one if needed."""
    today = datetime.now().strftime("%Y-%m-%d")
    report_path = REPORTS_DIR / f"medical_report_{today}.pdf"
    
    if not report_path.exists():
        report_path = generate_daily_report()
    
    return report_path

@router.get("/latest-report")
async def get_latest_report():
    """Endpoint to get the latest PDF report."""
    try:
        report_path = get_latest_report_path()
        return FileResponse(
            path=report_path,
            filename=f"medical_report_{datetime.now().strftime('%Y-%m-%d')}.pdf",
            media_type="application/pdf"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/last-update")
async def get_last_update():
    """Endpoint to get the timestamp of the last report update."""
    metadata_path = REPORTS_DIR / "latest_report_metadata.json"
    try:
        if metadata_path.exists():
            with open(metadata_path, "r", encoding="utf-8") as f:
                metadata = json.load(f)
            return {"lastUpdate": metadata["generated_at"]}
        else:
            # If no metadata exists, return the current time
            return {"lastUpdate": datetime.now().isoformat()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
