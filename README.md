# vcf2pdf

Turn a vCard (`.vcf`) address book into a clean, printable PDF directory.

`vcf2pdf` parses one or more vCards, groups contacts alphabetically, and
renders them as a two-column tabular listing with alternating row shading —
one page per letter, plus a cover page. Persian/Arabic text is reshaped and
bidirectionally reordered, so the PDF looks correct in any viewer.

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

---

## Installation

### From a clone

```bash
git clone https://github.com/mosadeghi/vcf2pdf
cd vcf2pdf
pip install .
```

### Editable install (for development)

```bash
pip install -e ".[dev]"
```

### Verification

```bash
vcf2pdf --help
# or
python -m vcf2pdf --help
```

---

## Usage

### CLI

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

### Library usage

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

### As a module

```bash
python -m vcf2pdf contacts.vcf -o address-book.pdf
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

---

## Project structure

```
vcf2pdf/
├── pyproject.toml
├── README.md
└── src/
    └── vcf2pdf/
        ├── __init__.py       # public API
        ├── __main__.py       # `python -m vcf2pdf`
        ├── cli.py            # argument parsing and orchestration
        ├── models.py         # Contact dataclass
        ├── theme.py          # palette and layout constants
        ├── rtl.py            # Arabic shaping + bidi reorder
        ├── grouping.py       # alphabetical bucketing
        ├── fonts.py          # font discovery and registration
        ├── vcf_parser.py     # robust VCF decoding and parsing
        ├── styles.py         # ReportLab ParagraphStyles
        ├── layout.py         # contact cells, section headers, tables
        └── pdf_builder.py    # assemble the final document
```

Dependency direction is strictly:

```
models  →  rtl / theme  →  grouping / vcf_parser  →  styles / layout  →  pdf_builder  →  cli
```

---

## Development

```bash
git clone <repo-url> vcf2pdf
cd vcf2pdf
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -e ".[dev]"
```

Lint (catches undefined-name bugs like missing imports):

```bash
ruff check src/
```

Run the CLI against a small fixture:

```bash
vcf2pdf tests/fixtures/sample.vcf -o /tmp/sample.pdf
```

---

## Troubleshooting

**`No Unicode font found`**  
Install a Unicode font, or pass `--font` explicitly. On Linux you may need
`fonts-noto` / `fonts-dejavu`; on minimal Docker images, copy a TTF into the
image and point `--font` at it.

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
`0`, and the count of skipped cards is printed at the end.

**Output PDF has a blank page at the end**  
This is a ReportLab quirk with trailing `PageBreak`s. It shouldn't happen with
the current builder; if it does, please open an issue with a minimal
reproducing `.vcf`.

---

