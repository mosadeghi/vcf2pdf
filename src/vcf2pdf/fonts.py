"""Unicode font discovery and registration with ReportLab."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.pdfmetrics import registerFontFamily
from reportlab.pdfbase.ttfonts import TTFont


@dataclass(frozen=True)
class FontSet:
    regular: Path
    bold: Path | None = None


FONT_CANDIDATES: tuple[tuple[str, str | None], ...] = (
    ("C:/Windows/Fonts/tahoma.ttf", "C:/Windows/Fonts/tahomabd.ttf"),
    ("C:/Windows/Fonts/segoeui.ttf", "C:/Windows/Fonts/segoeuib.ttf"),
    ("C:/Windows/Fonts/arial.ttf", "C:/Windows/Fonts/arialbd.ttf"),
    (
        "/usr/share/fonts/truetype/noto/NotoNaskhArabic-Regular.ttf",
        "/usr/share/fonts/truetype/noto/NotoNaskhArabic-Bold.ttf",
    ),
    (
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    ),
    ("/System/Library/Fonts/Supplemental/Arial Unicode.ttf", None),
    ("/Library/Fonts/Arial Unicode.ttf", None),
)


def find_font_set() -> FontSet | None:
    """Return the first available font set from ``FONT_CANDIDATES``."""
    for regular, bold in FONT_CANDIDATES:
        rp = Path(regular)
        if not rp.is_file():
            continue
        bp = Path(bold) if bold else None
        return FontSet(rp, bp if bp and bp.is_file() else None)
    return None


def register_fonts(font_set: FontSet) -> str:
    """Register the font with ReportLab and return the family name."""
    family = "BodyFont"
    pdfmetrics.registerFont(TTFont(family, str(font_set.regular)))
    bold = family
    if font_set.bold:
        bold = f"{family}-Bold"
        pdfmetrics.registerFont(TTFont(bold, str(font_set.bold)))
    registerFontFamily(
        family, normal=family, bold=bold, italic=family, boldItalic=bold
    )
    return family