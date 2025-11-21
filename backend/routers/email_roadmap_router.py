from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import os
import smtplib
from email.message import EmailMessage
from fpdf import FPDF
import tempfile

router = APIRouter()

class EmailRequest(BaseModel):
    to_email: str
    user_id: str
    roadmap_text: str
    plan_type: str

TEMPLATE_PDF = "TaxNerdGPT - CONSUMER PDF SHEET.pdf"

def generate_roadmap_pdf(text: str, user_id: str, plan_type: str) -> str:
    pdf = FPDF()
    pdf.add_page()

    # Use the template as a base image
    template_path = os.path.join(os.getcwd(), TEMPLATE_PDF)
    if os.path.exists(template_path):
        pdf.image(template_path, x=0, y=0, w=210, h=297)

    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.set_font("Arial", size=12)
    pdf.set_text_color(40, 40, 40)
    pdf.set_xy(10, 80)
    for line in text.split("\n"):
        pdf.multi_cell(0, 10, line)

    out_path = os.path.join(tempfile.gettempdir(), f"{user_id}_{plan_type}_roadmap.pdf")
    pdf.output(out_path)
    return out_path

@router.post("/email/roadmap")
def email_roadmap(data: EmailRequest):
    smtp_server = os.getenv("SMTP_SERVER")
    smtp_port = int(os.getenv("SMTP_PORT", 587))
    smtp_user = os.getenv("SMTP_USER")
    smtp_password = os.getenv("SMTP_PASSWORD")

    if not all([smtp_server, smtp_user, smtp_password]):
        raise HTTPException(status_code=500, detail="Email server not configured")

    try:
        # Generate roadmap PDF
        pdf_path = generate_roadmap_pdf(data.roadmap_text, data.user_id, data.plan_type)

        msg = EmailMessage()
        msg["Subject"] = f"Your {data.plan_type} Roadmap from TaxNerdGPT"
        msg["From"] = smtp_user
        msg["To"] = data.to_email
        msg.set_content(f"Hi {data.user_id},\n\nPlease find attached your personalized roadmap.")

        with open(pdf_path, "rb") as f:
            msg.add_attachment(f.read(), maintype="application", subtype="pdf", filename=os.path.basename(pdf_path))

        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(smtp_user, smtp_password)
            server.send_message(msg)

        return {"message": "Roadmap emailed with PDF attachment"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
