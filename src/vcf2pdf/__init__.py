"""vcf2pdf — render a vCard (.vcf) address book as a printable PDF directory."""

from __future__ import annotations

from .cli import main
from .models import Contact
from .pdf_builder import build_pdf
from .vcf_parser import parse_vcf

__version__ = "0.1.0"

__all__ = ["Contact", "build_pdf", "main", "parse_vcf", "__version__"]