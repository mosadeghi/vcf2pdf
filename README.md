# vcf2pdf

Turn a vCard (`.vcf`) address book into a clean, printable PDF directory.

`vcf2pdf` parses one or more vCards, groups contacts alphabetically, and
renders them as a two-column tabular listing with alternating row shading —
one page per letter, plus a cover page. Persian/Arabic text is reshaped and
bidirectionally reordered, so the PDF looks correct in any viewer.

Ships with both a **command-line interface** and a **tkinter GUI**, and can be
built into a **standalone Windows executable**.

---

## Features

- **One command, one PDF** — point it at a `.vcf` file and get a printable
  address book.
- **Alphabetical sections** — contacts are grouped by their first letter;
  each section starts on its own page.
- **Two-column grid** — compact layout with zebra-striped rows and thin
  dividers, sized for A4.
- **RTL-aware** — Persian/Arabic names, organizations, and addresses are
  reshaped (via `arabic-reshaper`) and reordered (via `python-bidi`) before
  rendering.
- **Robust VCF decoding** — handles `UTF-8`, `windows-1252`, `iso-8859-1`,
  BOMs, `QUOTED-PRINTABLE` continuations, and mislabelled
  `CHARSET=UTF-8` properties.
- **Font auto-detection** — picks a Unicode TTF already present on Windows,
  macOS, or Linux; you can override with `--font`.
- **Skips bad cards, keeps going** — malformed vCards are reported to
  `stderr` and counted, but never abort the run.
- **GUI editor** — open/save VCF, list and edit contacts, delete, and export
  PDF with a chosen title and output path.
- **Standalone build** — PyInstaller spec and `build.ps1` produce
  `vcf2pdf-gui.exe` and `vcf2pdf.exe` for Windows.

---

## Requirements

- Python **3.10** or newer
- A Unicode TTF font installed on the system (auto-detected) — or pass
  `--font /path/to/font.ttf`.

Python dependencies (installed automatically):

| Package | Purpose |
| --- | --- |
| `vobject` | vCard parsing |
| `reportlab` | PDF generation |
| `arabic-reshaper` | Arabic/Persian glyph shaping |
| `python-bidi` | Bidirectional text reordering |

`tkinter` is part of the Python standard library and requires no extra
install. On Linux you may need the system package (`sudo apt install
python3-tk`); on Windows and macOS it is bundled with the official Python
installer.

---

## Installation

### From a clone

```bash
git clone https://github.com/mosadeghi/vcf2pdf
cd vcf2pdf
pip install .
```

### Editable install (for development, includes PyInstaller)

```bash
pip install -e ".[dev,build]"
```

### Verification

```bash
vcf2pdf --help
vcf2pdf-gui --help          # opens the GUI; Ctrl+C / close to exit
python -m vcf2pdf --help
python -m vcf2pdf.gui       # launches the GUI
```

---

## Usage — CLI

### Basic

```bash
vcf2pdf contacts.vcf -o address-book.pdf
```

With a custom title and an explicit font:

```bash
vcf2pdf contacts.vcf -o address-book.pdf \
    --title "Team Directory" \
    --font "C:/Windows/Fonts/tahoma.ttf" \
    --font-bold "C:/Windows/Fonts/tahomabd.ttf"
```

### Options

| Flag | Default | Description |
| --- | --- | --- |
| `vcf` (positional) | — | Input `.vcf` file (required). |
| `-o`, `--output` | `contacts.pdf` | Output PDF path. |
| `--title` | `Contacts` | Title shown on the cover page. |
| `--font` | auto-detected | Path to a Unicode TTF for body text. |
| `--font-bold` | auto-detected | Optional bold variant of `--font`. |
| `--sort` | off | No-op; kept for backward compatibility. Sorting is always applied. |
| `-h`, `--help` | — | Show usage and exit. |

---

## Usage — GUI

Launch the graphical editor:

```bash
vcf2pdf-gui
# or
python -m vcf2pdf.gui
```

The GUI shares the same parser, writer, and PDF builder as the CLI, so the
exported PDF is identical to what `vcf2pdf` produces.

### Features

- **Open / Save VCF** — load an address book, edit it, save it back to
  `.vcf` (Save or Save As).
- **Contact list** — sortable table (Name / Organization / Phone / Email);
  multi-select supported.
- **Detail pane** — click any row to see the full contact below the list.
- **Add / Edit / Delete** — a modal form; live edits are reflected in the
  list immediately.
- **Export PDF** — choose a title, choose an output path, get the same
  zebra-striped, letter-sectioned PDF the CLI produces.
- **Font override** — `Settings → Choose PDF Font…` for cases where the
  auto-detected font doesn't cover your script.

### Keyboard shortcuts

| Shortcut | Action |
| --- | --- |
| `Ctrl+O` | Open VCF |
| `Ctrl+S` | Save VCF |
| `Ctrl+P` | Export PDF |
| `Ctrl+N` | Add contact |
| `F2` | Edit selected |
| `Del` | Delete selected |
| `Esc` | Close dialog |

---

## Library usage

### Generate a PDF

```python
from pathlib import Path

from vcf2pdf import parse_vcf, build_pdf
from vcf2pdf.fonts import find_font_set, register_fonts

contacts, skipped = parse_vcf(Path("contacts.vcf"))
contacts.sort(key=lambda c: c.name.casefold())

font_set = find_font_set()
if font_set is None:
    raise SystemExit("No Unicode font found; install one or pass an explicit TTF.")

family = register_fonts(font_set)
build_pdf(contacts, Path("out.pdf"), family, title="My Address Book")

print(f"Wrote {len(contacts)} contacts ({skipped} skipped)")
```

### Read and write a VCF

```python
from pathlib import Path
from vcf2pdf import parse_vcf
from vcf2pdf.vcf_writer import write_vcf

contacts, _ = parse_vcf(Path("in.vcf"))
write_vcf(contacts, Path("out.vcf"))
```

---

## What the PDF looks like

1. **Cover page** — large title, total contact count.
2. **One page per alphabetical section** — a colored letter badge, a
   "*N* contacts" caption, then a two-column table with zebra rows.
3. **Page numbers** centered at the bottom of every page.

---

## How RTL text is handled

Every string that ends up in the PDF passes through `vcf2pdf.rtl.shape()`:

1. `arabic_reshaper.reshape()` — joins Arabic/Persian letters into their
   contextual presentation forms.
2. `bidi.algorithm.get_display()` — reorders the visual run so ReportLab
   (which is not bidi-aware) renders it left-to-right correctly.
3. `xml.sax.saxutils.escape()` — escapes `&`, `<`, `>` for ReportLab's
   Paragraph markup.

If `arabic-reshaper` or `python-bidi` are missing **and** the input contains
Arabic-script characters, the CLI exits with a clear message rather than
producing a PDF of disconnected, reversed letters.

---

## Font handling

On startup the CLI tries, in order:

1. `--font` / `--font-bold` if provided.
2. A set of well-known system fonts:

   - Windows: Tahoma, Segoe UI, Arial
   - Linux: Noto Naskh Arabic, DejaVu Sans
   - macOS: Arial Unicode

If none is found, the run aborts with:

```
No Unicode font found. Pass --font /path/to/font.ttf.
```

You need a font that covers the script you're rendering. For Persian, **Tahoma**
or **Vazirmatn** are good choices; for Arabic, **Noto Naskh Arabic** or
**Amiri** work well. Any Unicode TTF will do — ReportLab does not need a
separate "Arabic" font, just one with the glyphs.

The GUI can pick a font at runtime via `Settings → Choose PDF Font…`.

---

## Building a standalone Windows executable

Tested with Python 3.11+ and PyInstaller 6.x.

```powershell
# From a clean checkout:
python -m venv .venv
.venv\Scripts\activate
.\build.ps1
```

`build.ps1` will:

1. install the package with its `[build]` extra,
2. run `pyinstaller --clean --noconfirm vcf2pdf.spec`.

The result is:

| Artifact | Type | Notes |
| --- | --- | --- |
| `dist\vcf2pdf-gui.exe` | windowed | Double-click to run. No console. |
| `dist\vcf2pdf.exe` | console | The CLI. |

Both are self-contained single-file executables. Users need nothing more
than the `.exe` itself and a Unicode TTF font on their system (Windows always
has Tahoma / Segoe UI / Arial).

### Manual build

```powershell
pip install -e ".[build]"
pyinstaller --clean --noconfirm vcf2pdf.spec
```

### Notes on the build

- The spec uses `pathex=['src']` **and** assumes the package is installed via
  `pip install -e .`. Either alone is enough; together they make the build
  robust.
- `upx=False` to avoid known ReportLab/DLL issues.
- `reportlab` ships a few runtime data files; they are collected via
  `collect_data_files("reportlab")` in the spec.
- `tkinter` is bundled automatically by PyInstaller on Windows.
- Fonts are **not** bundled — the executable reads them from the system's
  font directory, same as the CLI.

---

## Project structure

```
vcf2pdf/
├── pyproject.toml
├── README.md
├── vcf2pdf.spec                # PyInstaller spec (GUI + CLI)
├── build.ps1                   # one-shot Windows build script
├── gui_launcher.py             # PyInstaller entry: GUI
├── cli_launcher.py             # PyInstaller entry: CLI
└── src/
    └── vcf2pdf/
        ├── __init__.py         # public API
        ├── __main__.py         # `python -m vcf2pdf`
        ├── cli.py              # argument parsing and orchestration
        ├── models.py           # Contact dataclass
        ├── theme.py            # palette and layout constants
        ├── rtl.py              # Arabic shaping + bidi reorder
        ├── grouping.py         # alphabetical bucketing
        ├── fonts.py            # font discovery and registration
        ├── vcf_parser.py       # robust VCF decoding and parsing
        ├── vcf_writer.py       # serialize contacts back to .vcf
        ├── styles.py           # ReportLab ParagraphStyles
        ├── layout.py           # contact cells, section headers, tables
        ├── pdf_builder.py      # assemble the final document
        └── gui/                # tkinter front-end
            ├── __init__.py
            ├── __main__.py     # `python -m vcf2pdf.gui`
            ├── app.py          # main window
            └── contact_editor.py  # add/edit dialog
```

Dependency direction is strictly:

```
models  →  rtl / theme  →  grouping / vcf_parser  →  styles / layout  →  pdf_builder  →  cli
                                                               ↘
                                                                gui
```

---

## Development

```bash
git clone <repo-url> vcf2pdf
cd vcf2pdf
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -e ".[dev,build]"
```

Lint (catches undefined-name bugs like missing imports):

```bash
ruff check src/
```

Run the CLI against a small fixture:

```bash
vcf2pdf tests/fixtures/sample.vcf -o /tmp/sample.pdf
```

Launch the GUI:

```bash
vcf2pdf-gui
```

---

## Troubleshooting

**`No Unicode font found`**  
Install a Unicode font, or pass `--font` explicitly. On Linux you may need
`fonts-noto` / `fonts-dejavu`; on minimal Docker images, copy a TTF into the
image and point `--font` at it. In the GUI, use `Settings → Choose PDF Font…`.

**`Persian/Arabic text detected but arabic-reshaper / python-bidi are not installed`**  
Run `pip install arabic-reshaper python-bidi` (or
`pip install "vcf2pdf[rtl]"` if the extra is defined in your environment).

**Letters appear disconnected or in the wrong order**  
The font you're using doesn't contain Arabic glyphs, or the shaping step was
skipped. Verify the font with `fc-list :lang=fa` (Linux) or by opening it in
a text editor and typing a Persian word.

**Some cards are silently dropped**  
Look at `stderr` — the parser prints `Warning: skipped vCard #N (…)` for
each failure, with the exception type and message. The exit code is still
`0`, and the count of skipped cards is printed at the end. The GUI shows the
skipped count in its status bar.

**`ModuleNotFoundError: No module named 'tkinter'` (Linux)**  
Install the system package: `sudo apt install python3-tk` (Debian/Ubuntu) or
`sudo dnf install python3-tkinter` (Fedora).

**PyInstaller build fails on ReportLab**  
Make sure `upx=False` in the spec (already the default here) and that
`reportlab` is installed in the same environment you run `pyinstaller` from.
Run `pyinstaller --clean` to purge the cache.

**`vcf2pdf-gui.exe` opens then closes immediately**  
Usually a missing font or a ReportLab data file. Run the console build
(`dist\vcf2pdf.exe`) to see the actual error, or temporarily set
`console=True` on `exe_gui` in `vcf2pdf.spec` and rebuild.

**Output PDF has a blank page at the end**  
This is a ReportLab quirk with trailing `PageBreak`s. It shouldn't happen with
the current builder; if it does, please open an issue with a minimal
reproducing `.vcf`.

---

