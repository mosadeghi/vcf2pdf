"""Robust vCard (.vcf) decoding and parsing."""

from __future__ import annotations

import re
import sys
from pathlib import Path
from quopri import decodestring

import vobject

from .models import Contact

_QP_UTF8_RE = re.compile(r"CHARSET=UTF-8", re.IGNORECASE)


def _decode_bytes(raw: bytes) -> str:
    for encoding in ("utf-8-sig", "utf-8", "windows-1252", "iso-8859-1"):
        try:
            return raw.decode(encoding)
        except UnicodeDecodeError:
            continue
    return raw.decode("latin-1")


def _join_qp_continuations(text: str) -> str:
    """Glue every ``ENCODING=QUOTED-PRINTABLE`` property into one logical line."""
    lines = text.splitlines(keepends=True)
    out: list[str] = []
    i = 0
    while i < len(lines):
        line = lines[i]
        stripped = line.rstrip("\r\n")
        ending = line[len(stripped):]
        if "ENCODING=QUOTED-PRINTABLE" in stripped.upper():
            while stripped.endswith("=") and i + 1 < len(lines):
                stripped = stripped[:-1]
                i += 1
                next_line = lines[i]
                next_stripped = next_line.rstrip("\r\n")
                ending = next_line[len(next_stripped):]
                stripped += next_stripped
        out.append(stripped + ending)
        i += 1
    return "".join(out)


def _fix_charset_declarations(text: str) -> str:
    """Rewrite ``CHARSET=UTF-8`` when the QP payload cannot be decoded as UTF-8."""
    out: list[str] = []
    for line in text.splitlines(keepends=True):
        stripped = line.rstrip("\r\n")
        ending = line[len(stripped):]
        upper = stripped.upper()
        if (
            "ENCODING=QUOTED-PRINTABLE" in upper
            and "CHARSET=UTF-8" in upper
            and ":" in stripped
        ):
            header, _, value = stripped.partition(":")
            try:
                raw = decodestring(value.encode("ascii"))
            except Exception:  # noqa: BLE001
                raw = None
            if raw is not None:
                chosen = None
                for enc in ("utf-8", "windows-1252", "iso-8859-1"):
                    try:
                        raw.decode(enc)
                    except UnicodeDecodeError:
                        continue
                    else:
                        chosen = enc
                        break
                if chosen and chosen != "utf-8":
                    header = _QP_UTF8_RE.sub(f"CHARSET={chosen.upper()}", header)
                    stripped = header + ":" + value
        out.append(stripped + ending)
    return "".join(out)


def _split_cards(text: str) -> list[str]:
    cards: list[str] = []
    current: list[str] = []
    in_card = False
    for line in text.splitlines(keepends=True):
        marker = line.strip().upper()
        if marker == "BEGIN:VCARD":
            current = [line]
            in_card = True
        elif in_card:
            current.append(line)
            if marker == "END:VCARD":
                cards.append("".join(current))
                current = []
                in_card = False
    return cards


def _card_field(card, attr: str) -> str:
    obj = getattr(card, attr, None)
    if obj is None:
        return ""
    value = obj.value
    if isinstance(value, (list, tuple)):
        return ", ".join(str(v) for v in value if v)
    return str(value).strip()


def _format_address(value: object) -> str:
    if hasattr(value, "street"):
        parts = [
            getattr(value, "street", ""),
            getattr(value, "city", ""),
            getattr(value, "region", ""),
            getattr(value, "code", ""),
            getattr(value, "country", ""),
        ]
        return ", ".join(p for p in parts if p)
    return str(value).replace("\n", ", ").strip()


def _contact_from_card(card) -> Contact:
    name = _card_field(card, "fn") or _card_field(card, "n") or "(unnamed)"
    return Contact(
        name=name,
        organization=_card_field(card, "org"),
        phones=tuple(str(t.value) for t in card.contents.get("tel", [])),
        emails=tuple(str(e.value) for e in card.contents.get("email", [])),
        addresses=tuple(
            _format_address(a.value) for a in card.contents.get("adr", [])
        ),
    )


def parse_vcf(path: Path) -> tuple[list[Contact], int]:
    """Parse *path* and return ``(contacts, skipped_count)``."""
    raw = path.read_bytes()
    text = _decode_bytes(raw)
    text = _join_qp_continuations(text)
    text = _fix_charset_declarations(text)
    cards = _split_cards(text) or [text]

    contacts: list[Contact] = []
    skipped = 0

    for index, card_text in enumerate(cards, start=1):
        try:
            for card in vobject.readComponents(card_text):
                contacts.append(_contact_from_card(card))
        except Exception as exc:  # noqa: BLE001
            skipped += 1
            print(
                f"Warning: skipped vCard #{index} ({type(exc).__name__}: {exc})",
                file=sys.stderr,
            )

    return contacts, skipped