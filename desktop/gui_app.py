"""Native Windows GUI desktop application for Baloide Clinical Redactor.

Runs completely in-process: NO browser, NO web server, 100% offline and native.
"""

import sys
import time
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

ROOT = Path(__file__).resolve().parent
if not getattr(sys, "frozen", False):
    sys.path.insert(0, str(ROOT.parent / "backend"))

from app.schemas.redact import MaskMode, RedactOptions  # noqa: E402
from app.services.languages import SAMPLES  # noqa: E402
from app.services.redaction_engine import RedactionEngine  # noqa: E402
from app.services.text_ingestion import IngestionError, extract_text  # noqa: E402

LANGUAGE_NAMES = {
    "it": "Italiano",
    "en": "English",
    "es": "Español",
    "de": "Deutsch",
    "fr": "Français",
    "pt": "Português",
    "nl": "Nederlands",
    "pl": "Polski",
    "tr": "Türkçe",
    "ru": "Русский",
}

MASK_MODES = [
    ("TAG", "Placeholder [TAG]"),
    ("PSEUDONYM", "Pseudonimi Coerenti (Paziente_A)"),
    ("BLOCK", "Blackout (████)"),
    ("ASTERISK", "Asterischi (****)"),
]


class ClinicalRedactorApp:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Velide · Clinical Redactor")
        self.root.geometry("1280x820")
        self.root.minsize(980, 650)
        self.root.configure(bg="#0f172a")  # Slate 900 dark theme

        self.engine = RedactionEngine()
        self.current_entities = []
        self._debounce_job = None

        # Setup icon if present
        for icon_name in ("velide.ico", "baloide.ico"):
            icon_path = ROOT / "assets" / icon_name
            if icon_path.exists():
                try:
                    self.root.iconbitmap(str(icon_path))
                    break
                except Exception:
                    pass

        self._apply_styles()
        self._build_ui()

        # Load initial Italian sample
        self.load_sample("it")

    def _apply_styles(self):
        style = ttk.Style()
        style.theme_use("clam")

        # Dark theme colors
        bg_dark = "#0f172a"  # slate 900
        bg_panel = "#1e293b"  # slate 800
        fg_text = "#f8fafc"  # slate 50
        accent = "#0284c7"  # sky 600
        accent_hover = "#0369a1"  # sky 700

        style.configure(".", background=bg_dark, foreground=fg_text, font=("Segoe UI", 10))
        style.configure("TFrame", background=bg_dark)
        style.configure("Panel.TFrame", background=bg_panel)

        style.configure("TLabel", background=bg_dark, foreground=fg_text)
        style.configure("Panel.TLabel", background=bg_panel, foreground=fg_text)
        style.configure(
            "Muted.TLabel", background=bg_dark, foreground="#94a3b8", font=("Segoe UI", 9)
        )
        style.configure(
            "PanelMuted.TLabel", background=bg_panel, foreground="#94a3b8", font=("Segoe UI", 9)
        )

        style.configure("Title.TLabel", font=("Segoe UI", 14, "bold"), foreground="#38bdf8")
        style.configure(
            "Badge.TLabel",
            font=("Segoe UI", 9, "bold"),
            foreground="#34d399",
            background="#064e3b",
            padding=4,
        )

        style.configure(
            "TCheckbutton", background=bg_dark, foreground=fg_text, font=("Segoe UI", 9)
        )
        style.map("TCheckbutton", background=[("active", bg_dark)])

        style.configure(
            "TCombobox", fieldbackground=bg_panel, background=bg_panel, foreground=fg_text
        )
        style.map(
            "TCombobox",
            fieldbackground=[("readonly", bg_panel)],
            foreground=[("readonly", fg_text)],
        )

        # Buttons
        style.configure(
            "Primary.TButton",
            background=accent,
            foreground="#ffffff",
            font=("Segoe UI", 10, "bold"),
            padding=6,
        )
        style.map("Primary.TButton", background=[("active", accent_hover)])

        style.configure(
            "Secondary.TButton",
            background="#334155",
            foreground=fg_text,
            font=("Segoe UI", 9),
            padding=5,
        )
        style.map("Secondary.TButton", background=[("active", "#475569")])

        # Treeview (Detections table)
        style.configure(
            "Treeview",
            background="#1e293b",
            foreground="#f8fafc",
            fieldbackground="#1e293b",
            rowheight=24,
            font=("Segoe UI", 9),
        )
        style.configure(
            "Treeview.Heading",
            background="#334155",
            foreground="#f8fafc",
            font=("Segoe UI", 9, "bold"),
        )
        style.map("Treeview", background=[("selected", "#0369a1")])

    def _build_ui(self):
        # 1. Top Bar
        top_bar = ttk.Frame(self.root, padding="16 12 16 12")
        top_bar.pack(fill="x")

        title_box = ttk.Frame(top_bar)
        title_box.pack(side="left")

        title_lbl = ttk.Label(title_box, text="Baloide Clinical Redactor 🛡️", style="Title.TLabel")
        title_lbl.pack(anchor="w")

        sub_lbl = ttk.Label(
            title_box,
            text="Anonimizzazione & De-identificazione Dati Clinici • 100% Offline Locale • GDPR Compliant",
            style="Muted.TLabel",
        )
        sub_lbl.pack(anchor="w")

        # Top Bar Controls (Language & Mask Mode)
        controls_box = ttk.Frame(top_bar)
        controls_box.pack(side="right")

        ttk.Label(controls_box, text="Lingua:", style="Muted.TLabel").pack(
            side="left", padx=(10, 4)
        )
        self.lang_var = tk.StringVar(value="it")
        lang_cb = ttk.Combobox(
            controls_box,
            textvariable=self.lang_var,
            values=[f"{k} - {v}" for k, v in LANGUAGE_NAMES.items()],
            state="readonly",
            width=16,
        )
        lang_cb.current(0)
        lang_cb.bind("<<ComboboxSelected>>", self._on_language_changed)
        lang_cb.pack(side="left", padx=(0, 15))

        ttk.Label(controls_box, text="Modalità Maschera:", style="Muted.TLabel").pack(
            side="left", padx=(5, 4)
        )
        self.mode_var = tk.StringVar(value="TAG")
        mode_cb = ttk.Combobox(
            controls_box,
            textvariable=self.mode_var,
            values=[label for code, label in MASK_MODES],
            state="readonly",
            width=28,
        )
        mode_cb.current(0)
        mode_cb.bind("<<ComboboxSelected>>", lambda e: self.trigger_redaction())
        mode_cb.pack(side="left")

        # 2. Filter Checkboxes Bar
        filters_bar = ttk.Frame(self.root, padding="16 4 16 8")
        filters_bar.pack(fill="x")

        ttk.Label(
            filters_bar, text="Elementi da de-identificare:", font=("Segoe UI", 9, "bold")
        ).pack(side="left", padx=(0, 10))

        self.chk_names = tk.BooleanVar(value=True)
        self.chk_tax = tk.BooleanVar(value=True)
        self.chk_dates = tk.BooleanVar(value=True)
        self.chk_contacts = tk.BooleanVar(value=True)
        self.chk_locations = tk.BooleanVar(value=True)
        self.chk_ids = tk.BooleanVar(value=True)

        cb_specs = [
            ("Nomi", self.chk_names),
            ("Codici Fiscali / Tax ID", self.chk_tax),
            ("Date", self.chk_dates),
            ("Telefoni & Email", self.chk_contacts),
            ("Indirizzi & Ospedali", self.chk_locations),
            ("ID Cartella / Fascicoli", self.chk_ids),
        ]

        for text, var in cb_specs:
            cb = ttk.Checkbutton(
                filters_bar, text=text, variable=var, command=self.trigger_redaction
            )
            cb.pack(side="left", padx=8)

        # 3. Main Split Area (Left: Original, Right: Redacted)
        main_paned = tk.PanedWindow(self.root, orient="horizontal", bg="#0f172a", sashwidth=6, bd=0)
        main_paned.pack(fill="both", expand=True, padx=16, pady=6)

        # Left Panel (Input)
        left_panel = ttk.Frame(main_paned, style="Panel.TFrame", padding=10)
        main_paned.add(left_panel, minsize=420)

        left_header = ttk.Frame(left_panel, style="Panel.TFrame")
        left_header.pack(fill="x", pady=(0, 8))

        ttk.Label(
            left_header,
            text="TESTO CLINICO ORIGINALE",
            font=("Segoe UI", 10, "bold"),
            foreground="#fb7185",
            style="Panel.TLabel",
        ).pack(side="left")
        self.lbl_char_count = ttk.Label(left_header, text="0 caratteri", style="PanelMuted.TLabel")
        self.lbl_char_count.pack(side="right")

        # Toolbar on Left
        left_toolbar = ttk.Frame(left_panel, style="Panel.TFrame")
        left_toolbar.pack(fill="x", pady=(0, 8))

        ttk.Button(
            left_toolbar,
            text="📂 Apri Documento (PDF / DOCX / TXT)",
            style="Secondary.TButton",
            command=self.open_file_dialog,
        ).pack(side="left", padx=(0, 6))
        ttk.Button(
            left_toolbar,
            text="📋 Esempio",
            style="Secondary.TButton",
            command=lambda: self.load_sample(),
        ).pack(side="left", padx=(0, 6))
        ttk.Button(
            left_toolbar, text="🗑️ Pulisci", style="Secondary.TButton", command=self.clear_all
        ).pack(side="left")

        # Text input
        self.txt_input = tk.Text(
            left_panel,
            bg="#0b0f19",
            fg="#f8fafc",
            insertbackground="#38bdf8",
            selectbackground="#0369a1",
            relief="flat",
            wrap="word",
            font=("Consolas", 10),
            padx=8,
            pady=8,
        )
        scroll_input = ttk.Scrollbar(left_panel, command=self.txt_input.yview)
        self.txt_input.configure(yscrollcommand=scroll_input.set)
        scroll_input.pack(side="right", fill="y")
        self.txt_input.pack(side="left", fill="both", expand=True)
        self.txt_input.bind("<KeyRelease>", lambda e: self.schedule_redaction())

        # Right Panel (Output)
        right_panel = ttk.Frame(main_paned, style="Panel.TFrame", padding=10)
        main_paned.add(right_panel, minsize=420)

        right_header = ttk.Frame(right_panel, style="Panel.TFrame")
        right_header.pack(fill="x", pady=(0, 8))

        ttk.Label(
            right_header,
            text="TESTO DE-IDENTIFICATO (SICURO)",
            font=("Segoe UI", 10, "bold"),
            foreground="#34d399",
            style="Panel.TLabel",
        ).pack(side="left")

        self.lbl_stats = ttk.Label(right_header, text="0 rimossi • 0 ms", style="PanelMuted.TLabel")
        self.lbl_stats.pack(side="right")

        # Text output
        self.txt_output = tk.Text(
            right_panel,
            bg="#06201b",
            fg="#6ee7b7",
            insertbackground="#34d399",
            selectbackground="#047857",
            relief="flat",
            wrap="word",
            font=("Consolas", 10),
            padx=8,
            pady=8,
        )
        scroll_output = ttk.Scrollbar(right_panel, command=self.txt_output.yview)
        self.txt_output.configure(yscrollcommand=scroll_output.set)
        scroll_output.pack(side="right", fill="y")
        self.txt_output.pack(side="left", fill="both", expand=True)

        # 4. Action Bar (Bottom export buttons)
        action_bar = ttk.Frame(self.root, padding="16 10 16 10")
        action_bar.pack(fill="x")

        ttk.Button(
            action_bar,
            text="📋 Copia Testo Anonimizzato",
            style="Primary.TButton",
            command=self.copy_output,
        ).pack(side="left", padx=(0, 10))
        ttk.Button(
            action_bar,
            text="🤖 Copia per ChatGPT / Claude",
            style="Secondary.TButton",
            command=self.copy_for_ai,
        ).pack(side="left", padx=(0, 10))
        ttk.Button(
            action_bar,
            text="💾 Salva su File .TXT",
            style="Secondary.TButton",
            command=self.save_to_file,
        ).pack(side="left", padx=(0, 10))

        self.lbl_status_msg = ttk.Label(action_bar, text="Pronto.", style="Muted.TLabel")
        self.lbl_status_msg.pack(side="right")

        # 5. Bottom Table: Detections List
        table_frame = ttk.Frame(self.root, padding="16 0 16 12")
        table_frame.pack(fill="x")

        table_label_box = ttk.Frame(table_frame)
        table_label_box.pack(fill="x", pady=(0, 4))
        ttk.Label(
            table_label_box,
            text="Dati Sensibili Rilevati ed Espunti:",
            font=("Segoe UI", 9, "bold"),
        ).pack(side="left")
        self.lbl_table_count = ttk.Label(table_label_box, text="0 elementi", style="Muted.TLabel")
        self.lbl_table_count.pack(side="right")

        self.tree = ttk.Treeview(
            table_frame, columns=("type", "original", "replacement"), show="headings", height=4
        )
        self.tree.heading("type", text="Tipo Entità")
        self.tree.heading("original", text="Dato Originale (Sensibile)")
        self.tree.heading("replacement", text="Sostituzione Protetta")

        self.tree.column("type", width=140, minwidth=100)
        self.tree.column("original", width=360, minwidth=200)
        self.tree.column("replacement", width=360, minwidth=200)

        tree_scroll = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=tree_scroll.set)
        tree_scroll.pack(side="right", fill="y")
        self.tree.pack(side="left", fill="x", expand=True)

    def _get_selected_language(self) -> str:
        val = self.lang_var.get()
        return val.split(" - ")[0] if " - " in val else "it"

    def _get_mask_mode(self) -> MaskMode:
        label = self.mode_var.get()
        for code, mode_label in MASK_MODES:
            if mode_label == label:
                return MaskMode(code)
        return MaskMode.TAG

    def _on_language_changed(self, event=None):
        lang = self._get_selected_language()
        self.load_sample(lang)

    def load_sample(self, lang: str = None):
        if not lang:
            lang = self._get_selected_language()
        sample_text = SAMPLES.get(lang, SAMPLES.get("it", ""))
        self.txt_input.delete("1.0", tk.END)
        self.txt_input.insert("1.0", sample_text)
        self.trigger_redaction()

    def clear_all(self):
        self.txt_input.delete("1.0", tk.END)
        self.txt_output.delete("1.0", tk.END)
        self.current_entities = []
        for item in self.tree.get_children():
            self.tree.delete(item)
        self.lbl_char_count.configure(text="0 caratteri")
        self.lbl_stats.configure(text="0 rimossi • 0 ms")
        self.lbl_table_count.configure(text="0 elementi")
        self.lbl_status_msg.configure(text="Editor pulito.")

    def open_file_dialog(self):
        filetypes = [
            ("Tutti i documenti supportati", "*.pdf;*.docx;*.txt;*.md"),
            ("Documenti PDF (*.pdf)", "*.pdf"),
            ("Documenti Word (*.docx)", "*.docx"),
            ("File di Testo (*.txt;*.md)", "*.txt;*.md"),
        ]
        filepath = filedialog.askopenfilename(
            title="Seleziona documento clinico", filetypes=filetypes
        )
        if not filepath:
            return

        ext = Path(filepath).suffix.lower().lstrip(".")
        if ext not in ("pdf", "docx", "txt", "md"):
            messagebox.showerror("Formato non supportato", f"Il formato .{ext} non è supportato.")
            return

        try:
            with open(filepath, "rb") as f:
                data = f.read()

            self.lbl_status_msg.configure(text=f"Estrazione testo da {Path(filepath).name}...")
            self.root.update_idletasks()

            res = extract_text(data, ext)
            self.txt_input.delete("1.0", tk.END)
            self.txt_input.insert("1.0", res.text)
            self.trigger_redaction()
            self.lbl_status_msg.configure(
                text=f"Documento caricato: {Path(filepath).name} ({res.characters} caratteri)"
            )
        except IngestionError as e:
            messagebox.showerror(
                "Errore lettura file", f"Impossibile leggere il documento: codice errore '{e.code}'"
            )
            self.lbl_status_msg.configure(text="Errore importazione.")
        except Exception as e:
            messagebox.showerror("Errore", f"Errore durante l'apertura del file:\n{str(e)}")
            self.lbl_status_msg.configure(text="Errore importazione.")

    def schedule_redaction(self):
        if self._debounce_job:
            self.root.after_cancel(self._debounce_job)
        self._debounce_job = self.root.after(200, self.trigger_redaction)

    def trigger_redaction(self):
        text = self.txt_input.get("1.0", tk.END).strip()
        self.lbl_char_count.configure(text=f"{len(text):,} caratteri".replace(",", "."))

        if not text:
            self.txt_output.delete("1.0", tk.END)
            self.lbl_stats.configure(text="0 rimossi • 0 ms")
            self.lbl_table_count.configure(text="0 elementi")
            for item in self.tree.get_children():
                self.tree.delete(item)
            return

        options = RedactOptions(
            language=self._get_selected_language(),
            mask_mode=self._get_mask_mode(),
            redact_names=self.chk_names.get(),
            redact_tax_codes=self.chk_tax.get(),
            redact_dates=self.chk_dates.get(),
            redact_contacts=self.chk_contacts.get(),
            redact_locations=self.chk_locations.get(),
            redact_ids=self.chk_ids.get(),
            custom_keywords=[],
        )

        try:
            res = self.engine.redact(text, options)
            self.current_entities = res.entities

            # Update output box
            self.txt_output.delete("1.0", tk.END)
            self.txt_output.insert("1.0", res.redacted_text)

            # Update stats
            self.lbl_stats.configure(text=f"{res.entities_found} rimossi • {res.execution_ms} ms")
            self.lbl_table_count.configure(text=f"{res.entities_found} elementi rimossi")

            # Update Treeview
            for item in self.tree.get_children():
                self.tree.delete(item)
            for e in res.entities:
                self.tree.insert("", "end", values=(e.entity_type, e.original, e.replacement))

            self.lbl_status_msg.configure(text="De-identificazione completata con successo.")
        except Exception as e:
            self.lbl_status_msg.configure(text=f"Errore: {str(e)}")

    def copy_output(self):
        text = self.txt_output.get("1.0", tk.END).strip()
        if not text:
            return
        self.root.clipboard_clear()
        self.root.clipboard_append(text)
        self.lbl_status_msg.configure(text="✓ Testo anonimizzato copiato negli appunti!")

    def copy_for_ai(self):
        text = self.txt_output.get("1.0", tk.END).strip()
        if not text:
            return
        prompt = (
            "Sei un assistente medico clinico esperto. Il seguente referto è stato integralmente "
            "de-identificato e anonimizzato secondo le norme vigenti di privacy (GDPR / HIPAA). "
            "Nessun dato personale o identificativo è presente. Analizza il quadro clinico e fornisci "
            "una sintesi chiara del decorso, delle diagnosi e delle indicazioni terapeutiche:\n\n"
            f"---\n{text}\n---"
        )
        self.root.clipboard_clear()
        self.root.clipboard_append(prompt)
        self.lbl_status_msg.configure(text="✓ Prompt per ChatGPT / Claude copiato negli appunti!")

    def save_to_file(self):
        text = self.txt_output.get("1.0", tk.END).strip()
        if not text:
            return
        filepath = filedialog.asksaveasfilename(
            title="Salva referto de-identificato",
            defaultextension=".txt",
            filetypes=[("File di Testo (*.txt)", "*.txt"), ("Tutti i file", "*.*")],
            initialfile=f"referto_anonimizzato_{int(time.time())}.txt",
        )
        if filepath:
            try:
                with open(filepath, "w", encoding="utf-8") as f:
                    f.write(text)
                self.lbl_status_msg.configure(
                    text=f"✓ File salvato con successo: {Path(filepath).name}"
                )
            except Exception as e:
                messagebox.showerror(
                    "Errore salvataggio", f"Impossibile salvare il file:\n{str(e)}"
                )


def main():
    root = tk.Tk()
    ClinicalRedactorApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
