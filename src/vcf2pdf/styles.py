"""ReportLab paragraph styles."""

from __future__ import annotations

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet

from .theme import MUTED, TEXT


def build_styles(font_family: str) -> dict[str, ParagraphStyle]:
    base = getSampleStyleSheet()
    return {
        "cover_title": ParagraphStyle(
            "CoverTitle", parent=base["Title"], fontName=font_family,
            fontSize=44, leading=52, textColor=TEXT,
            alignment=TA_CENTER, spaceAfter=12,
        ),
        "cover_subtitle": ParagraphStyle(
            "CoverSubtitle", parent=base["BodyText"], fontName=font_family,
            fontSize=13, leading=18, textColor=MUTED, alignment=TA_CENTER,
        ),
        "letter": ParagraphStyle(
            "Letter", parent=base["Heading1"], fontName=font_family,
            fontSize=22, leading=26, textColor=colors.white,
            alignment=TA_CENTER,
        ),
        "letter_count": ParagraphStyle(
            "LetterCount", parent=base["BodyText"], fontName=font_family,
            fontSize=10, leading=13, textColor=MUTED, alignment=TA_LEFT,
        ),
        "name": ParagraphStyle(
            "Name", parent=base["Heading2"], fontName=font_family,
            fontSize=11, leading=14, textColor=TEXT, spaceAfter=2,
        ),
        "org": ParagraphStyle(
            "Org", parent=base["Italic"], fontName=font_family,
            fontSize=9, leading=12, textColor=MUTED, spaceAfter=4,
        ),
        "field": ParagraphStyle(
            "Field", parent=base["BodyText"], fontName=font_family,
            fontSize=8.5, leading=11, textColor=TEXT,
            alignment=TA_LEFT, spaceAfter=1,
        ),
        "empty": ParagraphStyle(
            "Empty", parent=base["BodyText"], fontName=font_family,
            fontSize=11, leading=14, textColor=MUTED, alignment=TA_CENTER,
        ),
    }