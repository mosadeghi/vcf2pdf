# -*- mode: python ; coding: utf-8 -*-
"""PyInstaller spec: builds `vcf2pdf-gui.exe` (windowed) and `vcf2pdf.exe` (console).

Build with:
    pyinstaller --clean --noconfirm vcf2pdf.spec
"""

from PyInstaller.utils.hooks import collect_data_files

# reportlab ships some non-code files at runtime; pull them in.
reportlab_datas = collect_data_files("reportlab")

hidden_imports = [
    "vcf2pdf.gui",
    "vcf2pdf.gui.app",
    "vcf2pdf.gui.contact_editor",
    "vcf2pdf.vcf_writer",
    "tkinter",
    "tkinter.ttk",
    "tkinter.filedialog",
    "tkinter.messagebox",
    "tkinter.simpledialog",
    "tkinter.font",
]

common_excludes = [
    "PyQt5", "PyQt6", "PySide2", "PySide6",
    "matplotlib", "numpy", "scipy", "pandas", "IPython", "pytest",
]


# --- GUI ------------------------------------------------------------------

a_gui = Analysis(
    ["gui_launcher.py"],
    pathex=["src"],
    binaries=[],
    datas=reportlab_datas,
    hiddenimports=hidden_imports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=common_excludes,
    noarchive=False,
)
pyz_gui = PYZ(a_gui.pure, a_gui.zipped_data)
exe_gui = EXE(
    pyz_gui,
    a_gui.scripts,
    a_gui.binaries,
    a_gui.datas,
    [],
    name="vcf2pdf-gui",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    runtime_tmpdir=None,
    console=False,                  # no console window
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)


# --- CLI ------------------------------------------------------------------

a_cli = Analysis(
    ["cli_launcher.py"],
    pathex=["src"],
    binaries=[],
    datas=reportlab_datas,
    hiddenimports=hidden_imports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=common_excludes,
    noarchive=False,
)
pyz_cli = PYZ(a_cli.pure, a_cli.zipped_data)
exe_cli = EXE(
    pyz_cli,
    a_cli.scripts,
    a_cli.binaries,
    a_cli.datas,
    [],
    name="vcf2pdf",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)