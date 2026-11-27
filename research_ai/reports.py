from __future__ import annotations

from io import BytesIO
from html import escape

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer


def generate_report(title: str, analysis: dict[str, str], viva: dict[str, list[dict[str, str]]] | None, insights: dict[str, list[str]] | None) -> bytes:
    output = BytesIO()
    styles = getSampleStyleSheet()
    story = [Paragraph("Research Analysis Report", styles["Title"]), Paragraph(title, styles["Heading2"]), Spacer(1, 12)]
    for label, value in analysis.items():
        story.extend([Paragraph(label.replace("_", " ").title(), styles["Heading3"]), Paragraph(escape(value), styles["BodyText"]), Spacer(1, 8)])
    if viva:
        story.append(Paragraph("Viva Preparation", styles["Heading2"]))
        for category, entries in viva.items():
            story.append(Paragraph(category, styles["Heading3"]))
            for entry in entries:
                story.append(Paragraph(f"Q. {escape(entry['question'])}", styles["BodyText"]))
                story.append(Paragraph(f"A. {escape(entry['answer'])}", styles["BodyText"]))
    if insights:
        story.append(Paragraph("AI-assisted Research Observations", styles["Heading2"]))
        for section, entries in insights.items():
            story.append(Paragraph(section.replace("_", " ").title(), styles["Heading3"]))
            for entry in entries:
                story.append(Paragraph(f"• {escape(entry)}", styles["BodyText"]))
        story.append(Paragraph("These observations are not guaranteed novel research gaps and require broader literature review.", styles["Italic"]))
    SimpleDocTemplate(output, pagesize=A4, title=title).build(story)
    return output.getvalue()
