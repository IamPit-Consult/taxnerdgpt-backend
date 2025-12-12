# backend/utils/pdf_letterhead.py
from __future__ import annotations

import io
import os
import textwrap
from datetime import datetime
from typing import Optional

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter

from pypdf import PdfReader, PdfWriter


def _wrap_lines(text: str, width_chars: int = 95) -> list[str]:
    lines: list[str] = []
    for raw in (text or "").replace("\r\n", "\n").split("\n"):
        raw = raw.strip()
        if not raw:
            lines.append("")
            continue
        lines.extend(textwrap.wrap(raw, width=width_chars))
    return lines


def generate_roadmap_pdf_with_letterhead(
    roadmap_text: str,
    *,
    output_title: str = "Perpetual Life Planner Roadmap",
    client_name: Optional[str] = None,
    template_path: str = "backend/assets/TaxNerdGPT - CONSUMER PDF SHEET.pdf",
) -> bytes:
    """
    Creates a PDF where each page uses the provided letterhead PDF as a background,
    and the roadmap text is drawn on top of it.

    Returns: PDF bytes
    """
    if not os.path.exists(template_path):
        raise FileNotFoundError(f"Letterhead template not found: {template_path}")

    # Read the single-page template (letterhead)
    template_reader = PdfReader(template_path)
    if len(template_reader.pages) < 1:
        raise ValueError("Letterhead template PDF has no pages.")
    template_page = template_reader.pages[0]

    # Page size (we assume letter; matches your template in most cases)
    page_w, page_h = letter

    # Layout: keep content away from header/footer printed on the letterhead
    left_margin = 54
    right_margin = 54
    top_margin = 140   # push content below the letterhead header
    bottom_margin = 110  # keep above footer legal text

    usable_width = page_w - left_margin - right_margin
    line_height = 14

    # Turn roadmap into wrapped lines
    lines = _wrap_lines(roadmap_text, width_chars=95)

    # We'll paginate lines based on vertical space
    max_lines_per_page = int((page_h - top_margin - bottom_margin) / line_height)
    if max_lines_per_page <= 0:
        raise ValueError("Margins are too large; no space to write content.")

    # PDF writer
    writer = PdfWriter()

    # Metadata header lines (optional)
    header_block = [
        output_title,
        f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
    ]
    if client_name:
        header_block.insert(1, f"Client: {client_name}")

    # Prepend a blank line after metadata
    all_lines = header_block + [""] + lines

    # Create each page overlay and merge onto the template background
    for page_start in range(0, len(all_lines), max_lines_per_page):
        chunk = all_lines[page_start: page_start + max_lines_per_page]

        # Create overlay PDF in memory
        overlay_buf = io.BytesIO()
        c = canvas.Canvas(overlay_buf, pagesize=letter)

        # Typography
        c.setFont("Helvetica", 11)

        # Starting cursor
        y = page_h - top_margin

        # Draw text
        for ln in chunk:
            if ln == "":
                y -= line_height  # blank line
                continue

            # If it's a heading-like line, bold it a bit
            if ln.lower().startswith("day ") or ln.startswith("#") or ln.endswith(":"):
                c.setFont("Helvetica-Bold", 12)
                c.drawString(left_margin, y, ln.replace("#", "").strip())
                c.setFont("Helvetica", 11)
            else:
                c.drawString(left_margin, y, ln)

            y -= line_height

        c.showPage()
        c.save()
        overlay_buf.seek(0)

        overlay_reader = PdfReader(overlay_buf)
        overlay_page = overlay_reader.pages[0]

        # Merge overlay text onto the letterhead background
        base = template_page  # same background each page
        merged = base  # pypdf merges in-place
        merged.merge_page(overlay_page)

        writer.add_page(merged)

    out = io.BytesIO()
    writer.write(out)
    return out.getvalue()
