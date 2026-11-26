"""Core data model for a display-ready contact."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Contact:
    """A single, display-ready contact."""

    name: str
    organization: str = ""
    phones: tuple[str, ...] = ()
    emails: tuple[str, ...] = ()
    addresses: tuple[str, ...] = ()