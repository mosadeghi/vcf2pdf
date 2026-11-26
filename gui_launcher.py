"""PyInstaller entry point for the vcf2pdf GUI."""

from __future__ import annotations

import sys

from vcf2pdf.gui.app import main

if __name__ == "__main__":
    sys.exit(main())