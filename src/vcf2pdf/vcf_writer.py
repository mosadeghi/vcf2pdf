"""Write display-ready Contact objects back to a .vcf file.

Note: ``ADR`` is written as a single string (what our parser produces), not
the full structured ``street;city;region;code;country`` form. This round-trips
through :func:`vcf2pdf.vcf_parser.parse_vcf` but may not import cleanly into
other vCard tools that expect structured addresses.
"""

from __future__ import annotations

from pathlib import Path

from .models import Contact


def _escape(value: str) -> str:
    """Escape a vCard 3.0 text value."""
    return (
        value.replace("\\", "\\\\")
        .replace("\r\n", "\\n")
        .replace("\n", "\\n")
        .replace(",", "\\,")
        .replace(";", "\\;")
    )


def _write_card(lines: list[str], c: Contact) -> None:
    lines.append("BEGIN:VCARD")
    lines.append("VERSION:3.0")
    lines.append(f"N:{_escape(c.name)};;;;")
    lines.append(f"FN:{_escape(c.name)}")
    if c.organization:
        lines.append(f"ORG:{_escape(c.organization)}")
    for phone in c.phones:
        lines.append(f"TEL:{_escape(phone)}")
    for email in c.emails:
        lines.append(f"EMAIL:{_escape(email)}")
    for address in c.addresses:
        lines.append(f"ADR:{_escape(address)}")
    lines.append("END:VCARD")


def write_vcf(contacts: list[Contact], path: Path) -> None:
    """Serialize *contacts* to *path* as a single .vcf file."""
    lines: list[str] = []
    for contact in contacts:
        _write_card(lines, contact)
    path.write_text("\r\n".join(lines) + "\r\n", encoding="utf-8")