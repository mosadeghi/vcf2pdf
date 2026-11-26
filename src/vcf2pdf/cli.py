"""Command-line interface for vcf2pdf."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .fonts import FontSet, find_font_set, register_fonts
from .pdf_builder import build_pdf
from .rtl import HAS_BIDI, contains_rtl
from .vcf_parser import parse_vcf


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="vcf2pdf",
        description="Generate a PDF address book from a vCard (.vcf) file.",
    )
    parser.add_argument("vcf", type=Path, help="input .vcf file")
    parser.add_argument(
        "-o", "--output", type=Path, default=Path("contacts.pdf"),
        help="output PDF path (default: contacts.pdf)",
    )
    parser.add_argument("--title", default="Contacts", help="title on the cover")
    parser.add_argument(
        "--sort", action="store_true",
        help="(always applied; kept for backward compatibility)",
    )
    parser.add_argument(
        "--font", type=Path, default=None,
        help="path to a Unicode TTF font (auto-detected if omitted)",
    )
    parser.add_argument(
        "--font-bold", type=Path, default=None,
        help="path to a bold variant of --font",
    )
    args = parser.parse_args(argv)

    if not args.vcf.is_file():
        parser.error(f"VCF file not found: {args.vcf}")

    contacts, skipped = parse_vcf(args.vcf)
    # Alphabetisation is required for the section headers to be meaningful.
    contacts.sort(key=lambda c: c.name.casefold())

    if args.font:
        if not args.font.is_file():
            parser.error(f"Font file not found: {args.font}")
        bold = args.font_bold if args.font_bold and args.font_bold.is_file() else None
        font_set: FontSet | None = FontSet(args.font, bold)
    else:
        font_set = find_font_set()

    if font_set is None:
        parser.error(
            "No Unicode font found. Pass --font /path/to/font.ttf."
        )

    has_rtl = any(
        contains_rtl(field)
        for c in contacts
        for field in (c.name, c.organization, *c.phones, *c.emails, *c.addresses)
    )
    if has_rtl and not HAS_BIDI:
        parser.error(
            "Persian/Arabic text detected but arabic-reshaper / python-bidi "
            "are not installed.\n    pip install arabic-reshaper python-bidi"
        )

    font_family = register_fonts(font_set)
    build_pdf(contacts, args.output, font_family, title=args.title)

    suffix = f" ({skipped} skipped)" if skipped else ""
    print(f"Wrote {len(contacts)} contact(s) to {args.output}{suffix}")
    return 0