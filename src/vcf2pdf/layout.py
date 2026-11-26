"""Reusable layout primitives: contact cells, section headers, tables."""

from __future__ import annotations

from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import Paragraph, Spacer, Table, TableStyle

from .models import Contact
from .rtl import shape
from .theme import ACCENT, BORDER, COL_WIDTH, MUTED_HEX, SURFACE


def contact_cell(
    contact: Contact, styles: dict[str, ParagraphStyle]
) -> list:
    """Return the stack of Paragraphs that make up one contact cell."""
    parts = [Paragraph(shape(contact.name), styles["name"])]
    if contact.organization:
        parts.append(Paragraph(shape(contact.organization), styles["org"]))
    if contact.phones:
        parts.append(
            Paragraph(
                f"<font color='{MUTED_HEX}'>Tel</font> "
                f"{shape(', '.join(contact.phones))}",
                styles["field"],
            )
        )
    if contact.emails:
        parts.append(
            Paragraph(
                f"<font color='{MUTED_HEX}'>Email</font> "
                f"{shape(', '.join(contact.emails))}",
                styles["field"],
            )
        )
    if contact.addresses:
        parts.append(
            Paragraph(
                f"<font color='{MUTED_HEX}'>Address</font> "
                f"{shape('; '.join(contact.addresses))}",
                styles["field"],
            )
        )
    return parts


def letter_header(
    letter: str, count: int, styles: dict[str, ParagraphStyle]
) -> Table:
    """Big colored letter badge + contact count + 2pt underline."""
    letter_para = Paragraph(shape(letter), styles["letter"])
    count_para = Paragraph(
        f"{count} contact{'s' if count != 1 else ''}",
        styles["letter_count"],
    )

    header = Table(
        [[letter_para, count_para]],
        colWidths=[1.4 * cm, None],
        rowHeights=[1.4 * cm],
    )
    header.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (0, 0), ACCENT),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("ALIGN", (0, 0), (0, 0), "CENTER"),
                ("ALIGN", (1, 0), (1, 0), "LEFT"),
                ("LEFTPADDING", (0, 0), (0, 0), 0),
                ("RIGHTPADDING", (0, 0), (0, 0), 0),
                ("LEFTPADDING", (1, 0), (1, 0), 14),
                ("RIGHTPADDING", (1, 0), (1, 0), 0),
                ("TOPPADDING", (0, 0), (-1, -1), 0),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
                ("LINEBELOW", (0, 0), (-1, -1), 2, ACCENT),
            ]
        )
    )
    return header


def contact_table(
    contacts: list[Contact], styles: dict[str, ParagraphStyle]
) -> Table:
    """Two-column table with zebra rows and thin dividers."""
    rows: list[list[list]] = []
    for i in range(0, len(contacts), 2):
        left = contact_cell(contacts[i], styles)
        right = (
            contact_cell(contacts[i + 1], styles)
            if i + 1 < len(contacts)
            else [Spacer(1, 1)]
        )
        rows.append([left, right])

    table = Table(rows, colWidths=[COL_WIDTH, COL_WIDTH])

    commands: list[tuple] = [
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 12),
        ("RIGHTPADDING", (0, 0), (-1, -1), 12),
        ("TOPPADDING", (0, 0), (-1, -1), 14),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 14),
    ]
    for row_idx in range(len(rows)):
        bg = colors.white if row_idx % 2 == 0 else SURFACE
        commands.append(("BACKGROUND", (0, row_idx), (-1, row_idx), bg))
    if len(rows) > 1:
        commands.append(("LINEBELOW", (0, 0), (-1, -2), 0.5, BORDER))

    table.setStyle(TableStyle(commands))
    return table