# One-shot Windows build: installs the package in editable mode together with
# PyInstaller, then produces dist\vcf2pdf-gui.exe and dist\vcf2pdf.exe.
#
# Usage:
#   .\build.ps1

$ErrorActionPreference = "Stop"

Write-Host "→ Installing package in editable mode with [build] extra..."
python -m pip install --upgrade pip | Out-Null
python -m pip install -e ".[build]"

Write-Host "→ Running PyInstaller..."
python -m PyInstaller --clean --noconfirm vcf2pdf.spec

Write-Host ""
Write-Host "Build complete. Output:"
Write-Host "  dist\vcf2pdf-gui.exe   (double-click to launch the GUI)"
Write-Host "  dist\vcf2pdf.exe       (command-line interface)"