import tkinter as tk
from tkinter import ttk, scrolledtext
from core.theme import *
from views.components import StyledFrame, SectionLabel, FieldLabel, StyledEntry, PrimaryButton, GhostButton, Divider
from core.config import load_settings

class BRDCDownloaderView(tk.Frame):
    def __init__(self, master, controller):
        super().__init__(master, bg=C_BG)
        self.ctrl = controller
        self._build_ui()

    def _build_ui(self):
        self.columnconfigure(0, weight=1)
        self.rowconfigure(4, weight=1)

        hdr = tk.Frame(self, bg=C_BG, padx=24, pady=14)
        hdr.grid(row=0, column=0, sticky="ew")
        tk.Label(hdr, text="Broadcast Ephemeris Downloader", font=FONT_TITLE, fg=C_TEXT, bg=C_BG).pack(side=tk.LEFT)
        tk.Label(hdr, text="Source: NASA CDDIS  •  RINEX 2 (.yyN)", font=FONT_BODY, fg=C_MUTED, bg=C_BG).pack(side=tk.RIGHT)
        Divider(self).grid(row=1, column=0, sticky="ew", padx=24)

        config_row = tk.Frame(self, bg=C_BG)
        config_row.grid(row=2, column=0, sticky="ew", padx=24, pady=12)
        config_row.columnconfigure(0, weight=1)
        config_row.columnconfigure(1, weight=1)

        self._build_credentials_panel(config_row)
        self._build_date_panel(config_row)

        # --- FIXED ACTION ROW ---
        action_row = tk.Frame(self, bg=C_BG, padx=24, pady=10)
        action_row.grid(row=3, column=0, sticky="ew")
        action_row.columnconfigure(2, weight=1) 

        self.download_btn = PrimaryButton(action_row, text="⬇  Download BRDC File", command=self.ctrl.start_download)
        self.download_btn.grid(row=0, column=0, sticky="w")
        
        self.clear_btn = GhostButton(action_row, text="🗑 Clear BRDCs", command=self.ctrl.clear_brdc_files)
        self.clear_btn.grid(row=0, column=1, sticky="w", padx=(12, 0))

        pb_frame = tk.Frame(action_row, bg=C_BG)
        pb_frame.grid(row=0, column=2, sticky="ew", padx=(16, 0))
        pb_frame.columnconfigure(0, weight=1)

        self.progress_var = tk.DoubleVar(value=0.0)
        self.progress_bar = ttk.Progressbar(pb_frame, variable=self.progress_var, maximum=1.0, style="Accent.Horizontal.TProgressbar", length=200)
        self.progress_bar.grid(row=0, column=0, sticky="ew")
        self.progress_label = tk.Label(pb_frame, text="Idle", fg=C_MUTED, bg=C_BG, font=("Courier New", 9))
        self.progress_label.grid(row=1, column=0, sticky="w", pady=(2, 0))
        # ------------------------

        log_frame = tk.Frame(self, bg=C_BG, padx=24)
        log_frame.grid(row=4, column=0, sticky="nsew", pady=(0, 16))
        log_frame.rowconfigure(1, weight=1)
        log_frame.columnconfigure(0, weight=1)

        header = tk.Frame(log_frame, bg=C_BG)
        header.grid(row=0, column=0, sticky="ew", pady=(0, 6))
        SectionLabel(header, "Activity Log", bg=C_BG).pack(side=tk.LEFT)
        GhostButton(header, text="Clear", command=self.clear_log, bg=C_BG).pack(side=tk.RIGHT)

        self.log = scrolledtext.ScrolledText(log_frame, height=10, bg=C_ENTRY_BG, fg=C_TEXT, font=FONT_MONO, relief=tk.FLAT, state=tk.DISABLED)
        self.log.grid(row=1, column=0, sticky="nsew")
        self.log.tag_config("success", foreground=C_SUCCESS)
        self.log.tag_config("error", foreground=C_ERROR)
        self.log.tag_config("warn", foreground=C_WARNING)
        self.log.tag_config("info", foreground=C_TEXT)
        self.log.tag_config("muted", foreground=C_MUTED)

    def _build_credentials_panel(self, parent):
        panel = StyledFrame(parent, padx=18, pady=16)
        panel.grid(row=0, column=0, sticky="nsew", padx=(0, 8))
        panel.columnconfigure(1, weight=1)

        settings = load_settings()

        SectionLabel(panel, "NASA Earthdata Credentials").grid(row=0, column=0, columnspan=3, sticky="w", pady=(0, 10))
        
        FieldLabel(panel, "Username", "Earthdata Account", "Required to access NASA CDDIS archives.\nYou can register for free at: urs.earthdata.nasa.gov").grid(row=1, column=0, sticky="w", pady=4)
        self.username_var = tk.StringVar(value=settings.get("nasa_username", ""))
        StyledEntry(panel, textvariable=self.username_var, width=26).grid(row=1, column=1, columnspan=2, sticky="ew", pady=4, padx=(8, 0))

        FieldLabel(panel, "Password").grid(row=2, column=0, sticky="w", pady=4)
        self.password_var = tk.StringVar(value=settings.get("nasa_password", ""))
        self.pw_entry = StyledEntry(panel, textvariable=self.password_var, show="●", width=26)
        self.pw_entry.grid(row=2, column=1, sticky="ew", pady=4, padx=(8, 4))

        self.show_pw_var = tk.BooleanVar(value=False)
        tk.Checkbutton(panel, text="Show", variable=self.show_pw_var, command=lambda: self.pw_entry.config(show="" if self.show_pw_var.get() else "●"), bg=C_PANEL, fg=C_MUTED, activebackground=C_PANEL, activeforeground=C_ACCENT, selectcolor=C_ENTRY_BG, font=("Courier New", 9), relief=tk.FLAT, cursor="hand2").grid(row=2, column=2, pady=4)


    def _build_date_panel(self, parent):
        panel = StyledFrame(parent, padx=18, pady=16)
        panel.grid(row=0, column=1, sticky="nsew", padx=(8, 0))
        panel.columnconfigure(1, weight=1)

        SectionLabel(panel, "Ephemeris Date").grid(row=0, column=0, columnspan=3, sticky="w", pady=(0, 10))
        self.date_mode = tk.StringVar(value="today")
        tk.Radiobutton(panel, text="Today's BRDC  (UTC)", variable=self.date_mode, value="today", command=self._on_date_mode_change, bg=C_PANEL, fg=C_TEXT, activebackground=C_PANEL, activeforeground=C_ACCENT, selectcolor=C_ENTRY_BG, font=FONT_BODY, cursor="hand2").grid(row=1, column=0, columnspan=3, sticky="w", pady=3)
        tk.Radiobutton(panel, text="Select date:", variable=self.date_mode, value="custom", command=self._on_date_mode_change, bg=C_PANEL, fg=C_TEXT, activebackground=C_PANEL, activeforeground=C_ACCENT, selectcolor=C_ENTRY_BG, font=FONT_BODY, cursor="hand2").grid(row=2, column=0, sticky="w", pady=3)

        import datetime
        now = datetime.datetime.now(datetime.UTC)
        spin_kw = dict(bg=C_ENTRY_BG, fg=C_TEXT, buttonbackground=C_BORDER, relief=tk.FLAT, font=FONT_BODY, state="disabled")
        date_frame = tk.Frame(panel, bg=C_PANEL)
        date_frame.grid(row=2, column=1, columnspan=2, sticky="w", padx=(8, 0))

        self.year_var, self.month_var, self.day_var = tk.StringVar(value=str(now.year)), tk.StringVar(value=str(now.month).zfill(2)), tk.StringVar(value=str(now.day).zfill(2))
        self.year_spin = tk.Spinbox(date_frame, from_=2000, to=2099, textvariable=self.year_var, width=5, **spin_kw)
        self.month_spin = tk.Spinbox(date_frame, from_=1, to=12, textvariable=self.month_var, width=3, **spin_kw)
        self.day_spin = tk.Spinbox(date_frame, from_=1, to=31, textvariable=self.day_var, width=3, **spin_kw)

        self.year_spin.pack(side=tk.LEFT, padx=(0, 2))
        tk.Label(date_frame, text="-", fg=C_MUTED, bg=C_PANEL).pack(side=tk.LEFT)
        self.month_spin.pack(side=tk.LEFT, padx=2)
        tk.Label(date_frame, text="-", fg=C_MUTED, bg=C_PANEL).pack(side=tk.LEFT)
        self.day_spin.pack(side=tk.LEFT, padx=(2, 0))

        self.date_widgets = [self.year_spin, self.month_spin, self.day_spin]
        tk.Label(panel, text=f"Current UTC date: {now.strftime('%Y-%m-%d')}", fg=C_SUCCESS, bg=C_PANEL, font=("Courier New", 9)).grid(row=3, column=0, columnspan=3, sticky="w", pady=(8, 0))

    def _on_date_mode_change(self):
        state = "normal" if self.date_mode.get() == "custom" else "disabled"
        for w in self.date_widgets: w.config(state=state)

    def log_line(self, msg: str, tag: str = "info"):
        import datetime
        ts = datetime.datetime.now(datetime.UTC).strftime("%H:%M:%S")
        self.log.config(state=tk.NORMAL)
        self.log.insert(tk.END, f"[{ts}]  {msg}\n", tag)
        self.log.see(tk.END)
        self.log.config(state=tk.DISABLED)

    def clear_log(self):
        self.log.config(state=tk.NORMAL)
        self.log.delete("1.0", tk.END)
        self.log.config(state=tk.DISABLED)