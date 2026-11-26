"""RTL shaping and reordering for Persian/Arabic text."""

from __future__ import annotations

from xml.sax.saxutils import escape

try:
    import arabic_reshaper
    from bidi.algorithm import get_display

    HAS_BIDI = True
except ImportError:  # pragma: no cover - optional dependency
    HAS_BIDI = False


def contains_rtl(text: str) -> bool:
    """Return True if *text* contains any Arabic-script code point."""
    for ch in text:
        cp = ord(ch)
        if (
            0x0600 <= cp <= 0x06FF
            or 0x0750 <= cp <= 0x077F
            or 0xFB50 <= cp <= 0xFDFF
            or 0xFE70 <= cp <= 0xFEFF
        ):
            return True
    return False


def shape(text: str) -> str:
    """Reshape Arabic-script, reorder bidirectionally, HTML-escape."""
    if not text:
        return ""
    if HAS_BIDI:
        text = arabic_reshaper.reshape(text)
        text = get_display(text)
    return escape(text)