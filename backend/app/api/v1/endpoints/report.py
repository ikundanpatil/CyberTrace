"""
Report Generation Endpoint

Generates court-ready PDF reports for domain analysis.
"""
from fastapi import APIRouter, HTTPException, Request, Depends
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from app.models.domain import DomainAnalysisRequest
from app.api.v1.endpoints.domain import analyze_domain
from app.reports.pdf_generator import PDFReportGenerator
from app.db.base import get_db
import logging
import os

logger = logging.getLogger(__name__)
router = APIRouter()

pdf_generator = PDFReportGenerator()


@router.post("/generate")
async def generate_report(
    request: Request,
    payload: DomainAnalysisRequest,
    db: Session = Depends(get_db)
):
    """
    Generate PDF report for domain analysis
    
    This endpoint:
    1. Performs domain analysis
    2. Generates court-ready PDF
    3. Returns download link
    """
    try:
        # Call analyze_domain with correct argument order (request, payload, db)
        analysis_result = await analyze_domain(request=request, payload=payload, db=db)
        
        # Extract data correctly
        if hasattr(analysis_result, 'data'):
            data = analysis_result.data
        else:
            data = analysis_result
        
        # Generate PDF
        pdf_path = pdf_generator.generate_report(data)
        
        filename = os.path.basename(pdf_path)
        return {
            "status": "success",
            "data": {
                "report_path": pdf_path,
                "filename": filename,
                "download_url": f"/api/v1/report/download/{filename}"
            }
        }
        
    except Exception as e:
        logger.error(f"Report generation failed: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Report generation failed: {str(e)}"
        )


@router.get("/download/{filename}")
async def download_report(filename: str):
    """Download generated PDF report"""
    try:
        base_dir = os.getcwd()
        filepath = os.path.join(base_dir, "reports", filename)
        
        if not os.path.exists(filepath):
            filepath = f"./reports/{filename}"
        
        return FileResponse(
            filepath,
            media_type='application/pdf',
            filename=filename
        )
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Report not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Download failed: {str(e)}")