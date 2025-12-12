from fastapi import APIRouter
from fastapi.responses import Response

from utils.pdf_letterhead import generate_roadmap_pdf_with_letterhead

router = APIRouter(
    prefix="/planner",
    tags=["PDF"]
)

@router.post("/roadmap/pdf")
def download_roadmap_pdf(payload: dict):
    """
    Generates a roadmap PDF using the TaxNerdGPT letterhead.
    """
    roadmap_text = payload.get("roadmap", "")
    client_name = payload.get("name", None)

    pdf_bytes = generate_roadmap_pdf_with_letterhead(
        roadmap_text=roadmap_text,
        output_title="TaxNerdGPT – Perpetual Life Planner",
        client_name=client_name,
        template_path="backend/asset/TaxNerdGPT - CONSUMER PDF SHEET.pdf"
    )

    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={
            "Content-Disposition": "attachment; filename=TaxNerdGPT_Roadmap.pdf"
        }
    )


