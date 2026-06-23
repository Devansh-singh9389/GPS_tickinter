import tkinter as tk
from tkinter import ttk
from core.theme import *
from core.config import load_settings, save_settings
from views.components import StyledFrame, SectionLabel, FieldLabel, StyledEntry, PrimaryButton, GhostButton, Divider

class SettingsDialog(tk.Toplevel):
    def __init__(self, parent, app_state):
        super().__init__(parent)
        self.title("Preferences")
        self.geometry("1920x1080")
        self.configure(bg=C_BG)
        self.transient(parent)
        self.grab_set() # Blocks the main window while settings are open
        
        self.app_state = app_state
        self.current_settings = load_settings()
        
        # Center the window
        self.update_idletasks()
        x = parent.winfo_rootx() + (parent.winfo_width() // 2) - (1080 // 2)
        y = parent.winfo_rooty() + (parent.winfo_height() // 2) - (720 // 2)
        self.geometry(f"+{x}+{y}")

        self._build_ui()

    def _build_ui(self):
        # --- Main Layout Layout ---
        sidebar = tk.Frame(self, bg=C_PANEL, width=360)
        sidebar.pack(side=tk.LEFT, fill=tk.Y)
        sidebar.pack_propagate(False)

        self.content_area = tk.Frame(self, bg=C_BG, padx=24, pady=24)
        self.content_area.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # --- Sidebar Buttons ---
        SectionLabel(sidebar, "Categories").pack(anchor="w", padx=16, pady=(20, 10))
        
        self.btn_gen = GhostButton(sidebar, text="⚙  General", command=lambda: self.show_page(self.page_general))
        self.btn_gen.pack(fill=tk.X, padx=8, pady=2)
        
        self.btn_perf = GhostButton(sidebar, text="🚀  Performance", command=lambda: self.show_page(self.page_performance))
        self.btn_perf.pack(fill=tk.X, padx=8, pady=2)
        
        self.btn_app = GhostButton(sidebar, text="🎨  Appearance", command=lambda: self.show_page(self.page_appearance))
        self.btn_app.pack(fill=tk.X, padx=8, pady=2)

        # --- Pages ---
        self.page_general = tk.Frame(self.content_area, bg=C_BG)
        self.page_performance = tk.Frame(self.content_area, bg=C_BG)
        self.page_appearance = tk.Frame(self.content_area, bg=C_BG)

        self._build_general_page()
        self._build_performance_page()
        self._build_appearance_page()

        # Bottom Action Bar
        action_bar = tk.Frame(self, bg=C_PANEL, pady=12, padx=24)
        action_bar.pack(side=tk.BOTTOM, fill=tk.X)
        Divider(self).pack(side=tk.BOTTOM, fill=tk.X)
        
        PrimaryButton(action_bar, text="Save Preferences", command=self.save_and_close).pack(side=tk.RIGHT)
        GhostButton(action_bar, text="Cancel", command=self.destroy).pack(side=tk.RIGHT, padx=8)

        reset_btn = ttk.Button(action_bar, text="↺ Reset to Defaults", command=self.reset_to_defaults)
        reset_btn.pack(side=tk.LEFT)

        # Start on General tab
        self.show_page(self.page_general)

    def show_page(self, page):
        for p in (self.page_general, self.page_performance, self.page_appearance):
            p.pack_forget()
        page.pack(fill=tk.BOTH, expand=True)

    def _build_general_page(self):
        from tkinter import ttk  # Needed for the Optimization Combobox

        tk.Label(self.page_general, text="General Settings", font=FONT_TITLE, fg=C_TEXT, bg=C_BG).pack(anchor="w",
                                                                                                       pady=(0, 16))

        f1 = StyledFrame(self.page_general, padx=16, pady=16)
        f1.pack(fill=tk.X, pady=(0, 12))

        # UI Toggles
        self.var_metadata = tk.BooleanVar(value=self.current_settings.get("auto_save_metadata", True))
        tk.Checkbutton(f1, text="Auto-Save JSON Metadata Sidecars", variable=self.var_metadata, bg=C_PANEL, fg=C_TEXT,
                       selectcolor=C_ENTRY_BG, activebackground=C_PANEL, activeforeground=C_TEXT, cursor="hand2").pack(
            anchor="w", pady=4)

        self.var_smartname = tk.BooleanVar(value=self.current_settings.get("smart_auto_naming", True))
        tk.Checkbutton(f1, text="Enable Smart Auto-Naming for BIN Files", variable=self.var_smartname, bg=C_PANEL,
                       fg=C_TEXT, selectcolor=C_ENTRY_BG, activebackground=C_PANEL, activeforeground=C_TEXT,
                       cursor="hand2").pack(anchor="w", pady=4)

        f2 = StyledFrame(self.page_general, padx=16, pady=16)
        f2.pack(fill=tk.X, pady=(0, 12))

        # NASA Credentials
        SectionLabel(f2, "Global Earthdata Credentials").pack(anchor="w", pady=(0, 8))
        self.var_user = tk.StringVar(value=self.current_settings.get("nasa_username", ""))
        self.var_pass = tk.StringVar(value=self.current_settings.get("nasa_password", ""))

        row1 = tk.Frame(f2, bg=C_PANEL)
        row1.pack(fill=tk.X, pady=2)
        FieldLabel(row1, "Username").pack(side=tk.LEFT)
        StyledEntry(row1, textvariable=self.var_user, width=30).pack(side=tk.RIGHT)

        row2 = tk.Frame(f2, bg=C_PANEL)
        row2.pack(fill=tk.X, pady=2)
        FieldLabel(row2, "Password").pack(side=tk.LEFT)
        StyledEntry(row2, textvariable=self.var_pass, show="●", width=30).pack(side=tk.RIGHT)

        # --- NEW: Compilation Attributes ---
        f3 = StyledFrame(self.page_general, padx=16, pady=16)
        f3.pack(fill=tk.X, pady=2)
        SectionLabel(f3, "Default Compilation Attributes").pack(anchor="w", pady=(0, 8))

        # Grid for Number/Text inputs
        grid_frame = tk.Frame(f3, bg=C_PANEL)
        grid_frame.pack(fill=tk.X, pady=4)

        # Row 0: User Motion & Max Satellites
        self.var_ums = tk.StringVar(value=str(self.current_settings.get("user_motion_size", 3000)))
        FieldLabel(grid_frame, "User Motion Size (s)").grid(row=0, column=0, sticky="w", pady=4)
        tk.Spinbox(grid_frame, from_=1, to=86400, textvariable=self.var_ums, bg=C_ENTRY_BG, fg=C_TEXT,
                   buttonbackground=C_BORDER, relief=tk.FLAT, width=8).grid(row=0, column=1, sticky="w", padx=(8, 20),
                                                                            pady=4)

        self.var_max_sat = tk.StringVar(value=str(self.current_settings.get("max_satellites", 32)))
        FieldLabel(grid_frame, "Max Satellites").grid(row=0, column=2, sticky="w", pady=4)
        tk.Spinbox(grid_frame, from_=8, to=40, textvariable=self.var_max_sat, bg=C_ENTRY_BG, fg=C_TEXT,
                   buttonbackground=C_BORDER, relief=tk.FLAT, width=8).grid(row=0, column=3, sticky="w", padx=(8, 0),
                                                                            pady=4)

        # Row 1: Max Channels & Default Optimization
        self.var_max_chan = tk.StringVar(value=str(self.current_settings.get("max_channels", 16)))
        FieldLabel(grid_frame, "Max Channels").grid(row=1, column=0, sticky="w", pady=4)
        tk.Spinbox(grid_frame, from_=4, to=32, textvariable=self.var_max_chan, bg=C_ENTRY_BG, fg=C_TEXT,
                   buttonbackground=C_BORDER, relief=tk.FLAT, width=8).grid(row=1, column=1, sticky="w", padx=(8, 20),
                                                                            pady=4)

        self.var_opt = tk.StringVar(value=self.current_settings.get("default_optimization", "Aggressive Optimization"))
        FieldLabel(grid_frame, "Optimization").grid(row=1, column=2, sticky="w", pady=4)
        ttk.Combobox(grid_frame, textvariable=self.var_opt,
                     values=["No Optimization", "Basic Optimization", "Recommended Standard",
                             "Aggressive Optimization"], state="readonly", width=18).grid(row=1, column=3, sticky="w",
                                                                                          padx=(8, 0), pady=4)

        # Checkboxes for Official Features
        chk_frame = tk.Frame(f3, bg=C_PANEL)
        chk_frame.pack(fill=tk.X, pady=(12, 0))

        def add_check(parent, text, key, default):
            var = tk.BooleanVar(value=self.current_settings.get(key, default))
            tk.Checkbutton(parent, text=text, variable=var, bg=C_PANEL, fg=C_TEXT, selectcolor=C_ENTRY_BG,
                           activebackground=C_PANEL, activeforeground=C_TEXT, cursor="hand2").pack(anchor="w", pady=2)
            return var

        self.var_large_file = add_check(chk_frame, "Large File Support (>2GB I/Q)", "large_file", True)
        self.var_multithread = add_check(chk_frame, "Multi-Threading (Real-time SDR)", "multithread", False)
        self.var_native_cpu = add_check(chk_frame, "Native CPU Architecture Optimizations", "native_cpu_arch", True)
        self.var_extreme_math = add_check(chk_frame, "Extreme Speed Math (-ffast-math)", "extreme_speed_math", False)
        self.var_high_prec = add_check(chk_frame, "Enable High-Precision Carrier Phase", "enable_high_precision", False)

    def _build_performance_page(self):
        tk.Label(self.page_performance, text="Performance Settings", font=FONT_TITLE, fg=C_TEXT, bg=C_BG).pack(anchor="w", pady=(0, 16))
        
        f1 = StyledFrame(self.page_performance, padx=16, pady=16)
        f1.pack(fill=tk.X)

        row1 = tk.Frame(f1, bg=C_PANEL)
        row1.pack(fill=tk.X, pady=6)
        FieldLabel(row1, "Default Compiler Opt.").pack(side=tk.LEFT)
        self.var_opt = tk.StringVar(value=self.current_settings.get("default_optimization", "Recommended Standard"))
        ttk.Combobox(row1, textvariable=self.var_opt, values=list(OPTIMIZATION_OPTIONS.keys()), state="readonly", width=22).pack(side=tk.RIGHT)

        row2 = tk.Frame(f1, bg=C_PANEL)
        row2.pack(fill=tk.X, pady=6)
        FieldLabel(row2, "Hardware Polling Rate (ms)").pack(side=tk.LEFT)
        self.var_poll = tk.StringVar(value=str(self.current_settings.get("hardware_poll_rate_ms", 3000)))
        tk.Spinbox(row2, from_=500, to=10000, increment=500, textvariable=self.var_poll, width=10, bg=C_ENTRY_BG, fg=C_TEXT, buttonbackground=C_BORDER, relief=tk.FLAT).pack(side=tk.RIGHT)

        self.var_verbose = tk.BooleanVar(value=self.current_settings.get("verbose_logging", False))
        tk.Checkbutton(f1, text="Force Verbose Logging globally (-v)", variable=self.var_verbose, bg=C_PANEL, fg=C_TEXT, selectcolor=C_ENTRY_BG, activebackground=C_PANEL, activeforeground=C_TEXT, cursor="hand2").pack(anchor="w", pady=(12, 0))

    def _build_appearance_page(self):
        tk.Label(self.page_appearance, text="Appearance", font=FONT_TITLE, fg=C_TEXT, bg=C_BG).pack(anchor="w", pady=(0, 16))
        
        f1 = StyledFrame(self.page_appearance, padx=16, pady=16)
        f1.pack(fill=tk.X)

        row1 = tk.Frame(f1, bg=C_PANEL)
        row1.pack(fill=tk.X, pady=6)
        FieldLabel(row1, "Theme Mode").pack(side=tk.LEFT)
        self.var_theme = tk.StringVar(value=self.current_settings.get("theme_mode", "Dark"))
        ttk.Combobox(row1, textvariable=self.var_theme, values=["Dark", "Light"], state="readonly", width=22).pack(side=tk.RIGHT)
        
        tk.Label(f1, text="Note: Light mode requires app restart.", font=FONT_HINT, fg=C_MUTED, bg=C_PANEL).pack(anchor="w", pady=(8, 0))

    def reset_to_defaults(self):
        from tkinter import messagebox
        from core.config import reset_settings

        if messagebox.askyesno("Reset Settings",
                               "Are you sure you want to restore all settings to their system defaults? This cannot be undone."):
            defaults = reset_settings()
            self.app_state.settings = defaults
            self.destroy()
            messagebox.showinfo("Reset Complete",
                                "Settings restored to defaults. Please reopen the settings window to view them.")

    def save_and_close(self):
        from core.config import save_settings

        # Ensure we catch empty inputs for the number fields to prevent crashes!
        try:
            ums_val = int(self.var_ums.get())
            sat_val = int(self.var_max_sat.get())
            chan_val = int(self.var_max_chan.get())
        except ValueError:
            import tkinter.messagebox as mb
            mb.showerror("Invalid Input", "User Motion, Max Satellites, and Max Channels must be valid numbers.")
            return

        updates = {
            "auto_save_metadata": self.var_metadata.get(),
            "smart_auto_naming": self.var_smartname.get(),
            "nasa_username": self.var_user.get().strip(),
            "nasa_password": self.var_pass.get().strip(),

            # --- New Compilation Attributes ---
            "user_motion_size": ums_val,
            "max_satellites": sat_val,
            "max_channels": chan_val,
            "default_optimization": self.var_opt.get(),

            "large_file": self.var_large_file.get(),
            "multithread": self.var_multithread.get(),
            "native_cpu_arch": self.var_native_cpu.get(),
            "extreme_speed": self.var_extreme_math.get(),
            "enable_high_precision": self.var_high_prec.get(),

            "theme_mode": self.var_theme.get()
        }

        self.app_state.update_settings(updates)
        save_settings(updates)
        self.destroy()