"""PyInstaller entry point for the vcf2pdf CLI."""

from __future__ import annotations

import sys

from vcf2pdf.cli import main

if __name__ == "__main__":
    sys.exit(main())