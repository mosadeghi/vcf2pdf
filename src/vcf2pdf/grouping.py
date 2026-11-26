"""Alphabetical grouping of contacts for section headers."""

from __future__ import annotations

from typing import Iterable

from .models import Contact


def first_letter(name: str) -> str:
    """Return the grouping key for a contact name."""
    stripped = name.strip()
    if not stripped:
        return "#"
    first = stripped[0]
    if first.isalpha():
        return first.upper()  # no-op for Persian; uppercase for Latin
    return "#"


def group_by_letter(
    contacts: Iterable[Contact],
) -> list[tuple[str, list[Contact]]]:
    """Bucket contacts by their first letter and return sorted sections."""
    groups: dict[str, list[Contact]] = {}
    for c in contacts:
        groups.setdefault(first_letter(c.name), []).append(c)
    return sorted(groups.items(), key=lambda kv: kv[0])