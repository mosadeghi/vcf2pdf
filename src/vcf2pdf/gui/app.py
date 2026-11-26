"""Main application window."""

from __future__ import annotations

import sys
import tkinter as tk
import tkinter.font as tkfont
from pathlib import Path
from tkinter import filedialog, messagebox, simpledialog, ttk

from ..fonts import FontSet, find_font_set, register_fonts
from ..models import Contact
from ..pdf_builder import build_pdf
from ..vcf_parser import parse_vcf
from ..vcf_writer import write_vcf
from .contact_editor import ContactEditor


class App(tk.Tk):
    """Address-book editor with PDF export."""

    TITLE = "vcf2pdf — Address Book"

    def __init__(self) -> None:
        super().__init__()
        self.title(self.TITLE)
        self.geometry("1000x680")
        self.minsize(720, 480)

        self.contacts: list[Contact] = []
        self.vcf_path: Path | None = None
        self.custom_font: FontSet | None = None

        self._apply_system_fonts()
        self._build_menu()
        self._build_toolbar()
        self._build_panes()
        self._build_status()

        self.bind("<Control-o>", lambda _e: self._open_vcf())
        self.bind("<Control-s>", lambda _e: self._save_vcf())
        self.bind("<Control-p>", lambda _e: self._export_pdf())
        self.bind("<Control-n>", lambda _e: self._add_contact())
        self.bind("<Delete>", lambda _e: self._delete_selected())
        self.bind("<F2>", lambda _e: self._edit_selected())

        self._update_status("Ready")

    # ------------------------------------------------------------------ UI

    def _apply_system_fonts(self) -> None:
        if sys.platform != "win32":
            return
        for name in ("TkDefaultFont", "TkTextFont", "TkMenuFont", "TkHeadingFont"):
            try:
                tkfont.nametofont(name).configure(family="Segoe UI", size=10)
            except tk.TclError:
                pass

    def _build_menu(self) -> None:
        menubar = tk.Menu(self)

        file_menu = tk.Menu(menubar, tearoff=False)
        file_menu.add_command(
            label="Open VCF…", accelerator="Ctrl+O", command=self._open_vcf
        )
        file_menu.add_command(
            label="Save VCF", accelerator="Ctrl+S", command=self._save_vcf
        )
        file_menu.add_command(
            label="Save VCF As…", command=self._save_vcf_as
        )
        file_menu.add_separator()
        file_menu.add_command(
            label="Export PDF…", accelerator="Ctrl+P", command=self._export_pdf
        )
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.destroy)
        menubar.add_cascade(label="File", menu=file_menu)

        edit_menu = tk.Menu(menubar, tearoff=False)
        edit_menu.add_command(
            label="Add Contact", accelerator="Ctrl+N", command=self._add_contact
        )
        edit_menu.add_command(
            label="Edit Selected", accelerator="F2", command=self._edit_selected
        )
        edit_menu.add_command(
            label="Delete Selected", accelerator="Del", command=self._delete_selected
        )
        menubar.add_cascade(label="Edit", menu=edit_menu)

        settings_menu = tk.Menu(menubar, tearoff=False)
        settings_menu.add_command(
            label="Choose PDF Font…", command=self._choose_font
        )
        settings_menu.add_command(
            label="Reset PDF Font", command=self._reset_font
        )
        menubar.add_cascade(label="Settings", menu=settings_menu)

        help_menu = tk.Menu(menubar, tearoff=False)
        help_menu.add_command(label="About", command=self._show_about)
        menubar.add_cascade(label="Help", menu=help_menu)

        self.config(menu=menubar)

    def _build_toolbar(self) -> None:
        bar = ttk.Frame(self, padding=(8, 6))
        bar.pack(fill="x")

        ttk.Button(bar, text="Open VCF", command=self._open_vcf).pack(
            side="left", padx=(0, 4)
        )
        ttk.Button(bar, text="Save VCF", command=self._save_vcf).pack(
            side="left", padx=(0, 12)
        )

        ttk.Separator(bar, orient="vertical").pack(
            side="left", fill="y", padx=(0, 12)
        )

        ttk.Button(bar, text="Add", command=self._add_contact).pack(
            side="left", padx=(0, 4)
        )
        ttk.Button(bar, text="Edit", command=self._edit_selected).pack(
            side="left", padx=(0, 4)
        )
        ttk.Button(bar, text="Delete", command=self._delete_selected).pack(
            side="left", padx=(0, 12)
        )

        ttk.Separator(bar, orient="vertical").pack(
            side="left", fill="y", padx=(0, 12)
        )

        ttk.Button(bar, text="Export PDF…", command=self._export_pdf).pack(
            side="left"
        )

    def _build_panes(self) -> None:
        panes = ttk.Panedwindow(self, orient="vertical")
        panes.pack(fill="both", expand=True, padx=8, pady=(0, 6))

        # ---- Top: tree --------------------------------------------------
        top = ttk.Frame(panes)
        top.columnconfigure(0, weight=1)
        top.rowconfigure(0, weight=1)

        cols = ("name", "organization", "phone", "email")
        self.tree = ttk.Treeview(
            top, columns=cols, show="headings", selectmode="extended"
        )
        self.tree.heading("name", text="Name", command=self._sort_by_name)
        self.tree.heading("organization", text="Organization")
        self.tree.heading("phone", text="Phone")
        self.tree.heading("email", text="Email")
        self.tree.column("name", width=260, stretch=True)
        self.tree.column("organization", width=220, stretch=True)
        self.tree.column("phone", width=160, stretch=False)
        self.tree.column("email", width=260, stretch=True)
        self.tree.grid(row=0, column=0, sticky="nsew")

        yscroll = ttk.Scrollbar(top, orient="vertical", command=self.tree.yview)
        yscroll.grid(row=0, column=1, sticky="ns")
        self.tree.configure(yscrollcommand=yscroll.set)
        self.tree.bind("<<TreeviewSelect>>", self._on_select)
        self.tree.bind("<Double-1>", lambda _e: self._edit_selected())

        panes.add(top, weight=3)

        # ---- Bottom: detail --------------------------------------------
        bottom = ttk.LabelFrame(panes, text="Contact Details", padding=8)
        bottom.columnconfigure(0, weight=1)
        bottom.rowconfigure(0, weight=1)

        self.detail = tk.Text(
            bottom,
            height=8,
            wrap="word",
            state="disabled",
            borderwidth=0,
            padx=6,
            pady=4,
        )
        self.detail.grid(row=0, column=0, sticky="nsew")
        dscroll = ttk.Scrollbar(bottom, orient="vertical", command=self.detail.yview)
        dscroll.grid(row=0, column=1, sticky="ns")
        self.detail.configure(yscrollcommand=dscroll.set)

        panes.add(bottom, weight=1)

    def _build_status(self) -> None:
        self.status_var = tk.StringVar()
        bar = ttk.Frame(self, padding=(8, 4))
        bar.pack(fill="x", side="bottom")
        ttk.Label(bar, textvariable=self.status_var, anchor="w").pack(
            side="left", fill="x", expand=True
        )

    # ------------------------------------------------------------- actions

    def _open_vcf(self) -> None:
        path = filedialog.askopenfilename(
            parent=self,
            title="Open VCF",
            filetypes=[("vCard files", "*.vcf *.vcard"), ("All files", "*.*")],
        )
        if not path:
            return
        try:
            contacts, skipped = parse_vcf(Path(path))
        except Exception as exc:  # noqa: BLE001
            messagebox.showerror("Parse error", str(exc), parent=self)
            return
        self.contacts = contacts
        self.contacts.sort(key=lambda c: c.name.casefold())
        self.vcf_path = Path(path)
        self._refresh_tree()
        msg = f"Loaded {len(contacts)} contacts from {path}"
        if skipped:
            msg += f" ({skipped} skipped)"
        self._update_status(msg)

    def _save_vcf(self) -> None:
        if not self.contacts:
            messagebox.showinfo("Nothing to save", "Load a VCF first.", parent=self)
            return
        if self.vcf_path is None:
            self._save_vcf_as()
            return
        self._write_vcf(self.vcf_path)

    def _save_vcf_as(self) -> None:
        if not self.contacts:
            messagebox.showinfo("Nothing to save", "Load a VCF first.", parent=self)
            return
        path = filedialog.asksaveasfilename(
            parent=self,
            title="Save VCF As",
            defaultextension=".vcf",
            filetypes=[("vCard files", "*.vcf"), ("All files", "*.*")],
            initialfile=self.vcf_path.name if self.vcf_path else "contacts.vcf",
        )
        if path:
            self._write_vcf(Path(path))

    def _write_vcf(self, path: Path) -> None:
        try:
            write_vcf(self.contacts, path)
        except Exception as exc:  # noqa: BLE001
            messagebox.showerror("Save failed", str(exc), parent=self)
            return
        self.vcf_path = path
        self._update_status(f"Saved {len(self.contacts)} contacts to {path}")

    def _add_contact(self) -> None:
        dlg = ContactEditor(self, contact=None)
        self.wait_window(dlg)
        if dlg.result is not None:
            self.contacts.append(dlg.result)
            self.contacts.sort(key=lambda c: c.name.casefold())
            idx = self.contacts.index(dlg.result)
            self._refresh_tree(select=idx)
            self._update_status(f"Added “{dlg.result.name}”")

    def _edit_selected(self) -> None:
        idx = self._selected_index()
        if idx is None:
            return
        current = self.contacts[idx]
        dlg = ContactEditor(self, contact=current)
        self.wait_window(dlg)
        if dlg.result is None:
            return
        self.contacts[idx] = dlg.result
        self.contacts.sort(key=lambda c: c.name.casefold())
        new_idx = self.contacts.index(dlg.result)
        self._refresh_tree(select=new_idx)
        self._update_status(f"Updated “{dlg.result.name}”")

    def _delete_selected(self) -> None:
        indices = self._selected_indices()
        if not indices:
            return
        n = len(indices)
        if not messagebox.askyesno(
            "Delete",
            f"Delete {n} contact{'s' if n != 1 else ''}?",
            parent=self,
        ):
            return
        for idx in sorted(indices, reverse=True):
            del self.contacts[idx]
        self._refresh_tree()
        self._update_status(f"Deleted {n} contact{'s' if n != 1 else ''}")

    def _export_pdf(self) -> None:
        if not self.contacts:
            messagebox.showinfo(
                "Nothing to export", "Load or add contacts first.", parent=self
            )
            return

        title = simpledialog.askstring(
            "PDF Title",
            "Title on the cover page:",
            initialvalue="Address Book",
            parent=self,
        )
        if title is None:  # user cancelled
            return

        path = filedialog.asksaveasfilename(
            parent=self,
            title="Export PDF",
            defaultextension=".pdf",
            filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")],
            initialfile="address-book.pdf",
        )
        if not path:
            return

        font_set = self.custom_font or find_font_set()
        if font_set is None:
            messagebox.showerror(
                "No font found",
                "No Unicode TTF was found on this system.\n\n"
                "Use Settings → Choose PDF Font… to point at one.",
                parent=self,
            )
            return
        try:
            family = register_fonts(font_set)
            ordered = sorted(self.contacts, key=lambda c: c.name.casefold())
            build_pdf(ordered, Path(path), family, title=title or "Contacts")
        except Exception as exc:  # noqa: BLE001
            messagebox.showerror("Export failed", str(exc), parent=self)
            return

        messagebox.showinfo("Export complete", f"PDF written to:\n{path}", parent=self)
        self._update_status(f"Exported {len(self.contacts)} contacts to {path}")

    def _choose_font(self) -> None:
        path = filedialog.askopenfilename(
            parent=self,
            title="Choose Unicode TTF font",
            filetypes=[("TrueType fonts", "*.ttf"), ("All files", "*.*")],
        )
        if not path:
            return
        p = Path(path)
        self.custom_font = FontSet(p, None)
        self._update_status(f"PDF font: {p.name}")

    def _reset_font(self) -> None:
        self.custom_font = None
        self._update_status("PDF font: auto-detect")

    def _show_about(self) -> None:
        messagebox.showinfo(
            "About vcf2pdf",
            "vcf2pdf — render vCard address books as PDF directories.\n\n"
            "CLI: vcf2pdf contacts.vcf -o out.pdf\n"
            "GUI: vcf2pdf-gui",
            parent=self,
        )

    # ------------------------------------------------------------- helpers

    def _refresh_tree(self, select: int | None = None) -> None:
        self.tree.delete(*self.tree.get_children())
        for i, c in enumerate(self.contacts):
            self.tree.insert(
                "",
                "end",
                iid=str(i),
                values=(
                    c.name,
                    c.organization,
                    c.phones[0] if c.phones else "",
                    c.emails[0] if c.emails else "",
                ),
            )
        if select is not None and 0 <= select < len(self.contacts):
            self.tree.selection_set(str(select))
            self.tree.focus(str(select))
            self.tree.see(str(select))
        else:
            self._clear_detail()
        self._update_count()

    def _sort_by_name(self) -> None:
        self.contacts.sort(key=lambda c: c.name.casefold())
        self._refresh_tree()

    def _selected_indices(self) -> list[int]:
        return [int(iid) for iid in self.tree.selection()]

    def _selected_index(self) -> int | None:
        sel = self.tree.selection()
        return int(sel[0]) if sel else None

    def _on_select(self, _event: tk.Event) -> None:
        idx = self._selected_index()
        if idx is None or not (0 <= idx < len(self.contacts)):
            self._clear_detail()
            return
        self._show_detail(self.contacts[idx])

    def _show_detail(self, c: Contact) -> None:
        lines = [f"Name:        {c.name}"]
        if c.organization:
            lines.append(f"Organization: {c.organization}")
        for p in c.phones:
            lines.append(f"Phone:       {p}")
        for e in c.emails:
            lines.append(f"Email:       {e}")
        for a in c.addresses:
            lines.append(f"Address:     {a}")
        self.detail.configure(state="normal")
        self.detail.delete("1.0", "end")
        self.detail.insert("1.0", "\n".join(lines))
        self.detail.configure(state="disabled")

    def _clear_detail(self) -> None:
        self.detail.configure(state="normal")
        self.detail.delete("1.0", "end")
        self.detail.configure(state="disabled")

    def _update_status(self, message: str) -> None:
        self.status_var.set(message)

    def _update_count(self) -> None:
        total = len(self.contacts)
        source = f" — {self.vcf_path.name}" if self.vcf_path else ""
        self._update_status(f"{total} contact{'s' if total != 1 else ''}{source}")


def main() -> int:
    # Crisper text on Windows high-DPI displays.
    if sys.platform == "win32":
        try:
            from ctypes import windll

            windll.shcore.SetProcessDpiAwareness(1)
        except Exception:  # noqa: BLE001
            pass

    App().mainloop()
    return 0


if __name__ == "__main__":
    sys.exit(main())