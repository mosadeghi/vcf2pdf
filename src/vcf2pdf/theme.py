"""Shared palette and page-layout constants."""

from __future__ import annotations

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm

# --- Palette ----------------------------------------------------------------

ACCENT = colors.HexColor("#3b5bdb")   # indigo
TEXT = colors.HexColor("#1a202c")     # near-black
MUTED = colors.HexColor("#718096")    # slate
BORDER = colors.HexColor("#e2e8f0")   # pale border
SURFACE = colors.HexColor("#fafbfc")  # off-white for zebra rows

# Hex string form for use inside ReportLab Paragraph markup.
MUTED_HEX = "#718096"

# --- Layout -----------------------------------------------------------------

PAGE_SIZE = A4
MARGIN_H = 2 * cm
MARGIN_V = 2 * cm
GAP = 0.8 * cm
COL_WIDTH = (PAGE_SIZE[0] - 2 * MARGIN_H - GAP) / 2