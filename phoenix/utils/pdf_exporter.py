from __future__ import annotations

from pathlib import Path

from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas


def export_text_report(title: str, lines: list[str], destination: Path) -> Path:
    pdf = canvas.Canvas(str(destination), pagesize=A4)
    pdf.setTitle(title)
    y = 800
    pdf.setFont("Helvetica-Bold", 16)
    pdf.drawString(50, y, title)
    y -= 40
    pdf.setFont("Helvetica", 11)
    for line in lines:
        pdf.drawString(50, y, line)
        y -= 18
        if y < 60:
            pdf.showPage()
            y = 800
    pdf.save()
    return destination
