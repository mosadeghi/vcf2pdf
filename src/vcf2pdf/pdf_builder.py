"""Assemble the final PDF document."""

from __future__ import annotations

from pathlib import Path

from reportlab.lib.units import cm
from reportlab.platypus import (
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
)

from .grouping import group_by_letter
from .layout import contact_table, letter_header
from .models import Contact
from .rtl import shape
from .styles import build_styles
from .theme import MARGIN_H, MARGIN_V, MUTED, PAGE_SIZE


def make_footer(font_family: str):
    def _footer(canvas, _doc):
        canvas.saveState()
        canvas.setFont(font_family, 8)
        canvas.setFillColor(MUTED)
        canvas.drawCentredString(
            PAGE_SIZE[0] / 2, 1.1 * cm, str(canvas.getPageNumber())
        )
        canvas.restoreState()

    return _footer


def build_pdf(
    contacts: list[Contact],
    output: Path,
    font_family: str,
    title: str = "Contacts",
) -> None:
    doc = SimpleDocTemplate(
        str(output),
        pagesize=PAGE_SIZE,
        leftMargin=MARGIN_H,
        rightMargin=MARGIN_H,
        topMargin=MARGIN_V,
        bottomMargin=MARGIN_V,
        title=title,
        author="vcf2pdf",
    )
    styles = build_styles(font_family)

    story: list = []

    # ---- Cover page ------------------------------------------------------
    story.append(Spacer(1, 7 * cm))
    story.append(Paragraph(shape(title), styles["cover_title"]))
    story.append(
        Paragraph(
            f"{len(contacts)} contact{'s' if len(contacts) != 1 else ''}",
            styles["cover_subtitle"],
        )
    )
    story.append(PageBreak())

    # ---- One page per alphabetical section -------------------------------
    groups = group_by_letter(contacts)
    if not groups:
        story.append(Paragraph("No contacts found.", styles["empty"]))
    else:
        for idx, (letter, bucket) in enumerate(groups):
            if idx > 0:
                story.append(PageBreak())
            story.append(letter_header(letter, len(bucket), styles))
            story.append(Spacer(1, 0.4 * cm))
            story.append(contact_table(bucket, styles))

    footer = make_footer(font_family)
    doc.build(story, onFirstPage=footer, onLaterPages=footer)