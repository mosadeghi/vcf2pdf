"""Modal dialog for creating or editing a Contact."""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from ..models import Contact


class ContactEditor(tk.Toplevel):
    """A modal editor. After ``wait_window``, read :attr:`result`.

    ``result`` is ``None`` if the user cancelled, otherwise a new
    :class:`Contact` built from the form values.
    """

    def __init__(self, parent: tk.Misc, contact: Contact | None = None) -> None:
        super().__init__(parent)
        self.title("Edit Contact" if contact else "Add Contact")
        self.resizable(True, True)
        self.result: Contact | None = None
        self._build_ui(contact)
        self.transient(parent)
        self.grab_set()
        self._center_on(parent)
        self.bind("<Escape>", lambda _e: self._cancel())
        self.name_entry.focus_set()

    # ------------------------------------------------------------------ UI

    def _build_ui(self, contact: Contact | None) -> None:
        body = ttk.Frame(self, padding=12)
        body.pack(fill="both", expand=True)
        body.columnconfigure(1, weight=1)
        body.rowconfigure(5, weight=1)

        ttk.Label(body, text="Name:").grid(row=0, column=0, sticky="w", pady=(0, 6))
        self.name_entry = ttk.Entry(body)
        self.name_entry.grid(row=0, column=1, sticky="ew", pady=(0, 6))

        ttk.Label(body, text="Organization:").grid(row=1, column=0, sticky="w", pady=(0, 6))
        self.org_entry = ttk.Entry(body)
        self.org_entry.grid(row=1, column=1, sticky="ew", pady=(0, 6))

        ttk.Label(body, text="Phones:").grid(row=2, column=0, sticky="nw", pady=(0, 6))
        self.phones_text = self._multiline(body)
        self.phones_text.grid(row=2, column=1, sticky="nsew", pady=(0, 6))

        ttk.Label(body, text="Emails:").grid(row=3, column=0, sticky="nw", pady=(0, 6))
        self.emails_text = self._multiline(body)
        self.emails_text.grid(row=3, column=1, sticky="nsew", pady=(0, 6))

        ttk.Label(body, text="Addresses:").grid(row=4, column=0, sticky="nw", pady=(0, 6))
        self.addresses_text = self._multiline(body)
        self.addresses_text.grid(row=4, column=1, sticky="nsew", pady=(0, 6))

        hint = ttk.Label(
            body,
            text="One item per line.",
            foreground="#718096",
        )
        hint.grid(row=5, column=1, sticky="nw")

        buttons = ttk.Frame(self, padding=(12, 0, 12, 12))
        buttons.pack(fill="x")
        ttk.Button(buttons, text="Cancel", command=self._cancel).pack(side="right")
        ttk.Button(buttons, text="OK", command=self._ok).pack(
            side="right", padx=(0, 8)
        )

        # Populate
        if contact is not None:
            self.name_entry.insert(0, contact.name)
            self.org_entry.insert(0, contact.organization)
            self._fill(self.phones_text, contact.phones)
            self._fill(self.emails_text, contact.emails)
            self._fill(self.addresses_text, contact.addresses)

        self.minsize(420, 420)

    @staticmethod
    def _multiline(parent: tk.Misc) -> tk.Text:
        frame = ttk.Frame(parent)
        text = tk.Text(frame, height=3, wrap="word", undo=True)
        scroll = ttk.Scrollbar(frame, orient="vertical", command=text.yview)
        text.configure(yscrollcommand=scroll.set)
        text.pack(side="left", fill="both", expand=True)
        scroll.pack(side="right", fill="y")
        # Keep a reference so .grid() works on the outer frame, not inner.
        text.frame = frame  # type: ignore[attr-defined]
        return _TextProxy(frame, text)

    @staticmethod
    def _fill(proxy: "_TextProxy", values: tuple[str, ...]) -> None:
        proxy.text.insert("1.0", "\n".join(values))

    # --------------------------------------------------------------- result

    def _ok(self) -> None:
        name = self.name_entry.get().strip()
        if not name:
            from tkinter import messagebox

            messagebox.showwarning(
                "Missing name", "A contact must have a name.", parent=self
            )
            self.name_entry.focus_set()
            return
        self.result = Contact(
            name=name,
            organization=self.org_entry.get().strip(),
            phones=self._lines(self.phones_text),
            emails=self._lines(self.emails_text),
            addresses=self._lines(self.addresses_text),
        )
        self.destroy()

    def _cancel(self) -> None:
        self.result = None
        self.destroy()

    @staticmethod
    def _lines(proxy: "_TextProxy") -> tuple[str, ...]:
        raw = proxy.text.get("1.0", "end").splitlines()
        return tuple(line.strip() for line in raw if line.strip())

    def _center_on(self, parent: tk.Misc) -> None:
        self.update_idletasks()
        px, py = parent.winfo_rootx(), parent.winfo_rooty()
        pw, ph = parent.winfo_width(), parent.winfo_height()
        w, h = self.winfo_width(), self.winfo_height()
        self.geometry(f"+{px + (pw - w) // 2}+{py + (ph - h) // 2}")


class _TextProxy:
    """Let a ``tk.Text`` sit inside a ``ttk.Frame`` so ``.grid`` works on the frame."""

    def __init__(self, frame: ttk.Frame, text: tk.Text) -> None:
        self.frame = frame
        self.text = text

    def grid(self, **kwargs) -> None:  # type: ignore[override]
        self.frame.grid(**kwargs)