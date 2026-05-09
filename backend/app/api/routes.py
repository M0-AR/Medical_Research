from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from datetime import datetime
from app.core.config import settings
from app.utils.pdf_generator import generate_daily_report, get_latest_report_path
import json

router = APIRouter()

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
    metadata_path = settings.REPORTS_DIR / "latest_report_metadata.json"
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
