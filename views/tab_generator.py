import tkinter as tk
from tkinter import ttk, scrolledtext
from core.theme import *
from views.components import StyledFrame, SectionLabel, FieldLabel, StyledEntry, PrimaryButton, GhostButton, Divider, attach_advanced_tooltip, ScrollableFrame
from pathlib import Path

class GeneratorView(tk.Frame):
    def __init__(self, master, controller, app_state):
        super().__init__(master, bg=C_BG)
        self.ctrl = controller
        self.app_state = app_state
        
        # Wrapped in our robust ScrollableFrame!
        self.scroll = ScrollableFrame(self)
        self.scroll.pack(fill=tk.BOTH, expand=True)
        self._build_ui(self.scroll.content)

    def _build_ui(self, container):
        container.columnconfigure(0, weight=1)

        hdr = tk.Frame(container, bg=C_BG, padx=24, pady=14)
        hdr.grid(row=0, column=0, sticky="ew")
        tk.Label(hdr, text="GPS Baseband Generator", font=FONT_TITLE, fg=C_TEXT, bg=C_BG).pack(side=tk.LEFT)
        tk.Label(hdr, text="Generate .bin file for RF Testing", font=FONT_BODY, fg=C_MUTED, bg=C_BG).pack(side=tk.RIGHT)
        Divider(container).grid(row=1, column=0, sticky="ew", padx=24)

        panel = StyledFrame(container, padx=16, pady=14)
        panel.grid(row=2, column=0, sticky="nsew", padx=24, pady=12)
        panel.columnconfigure(1, weight=1)

        # --- 1. REQUIRED FILES SECTION ---
        SectionLabel(panel, "1. Required Files").grid(row=0, column=0, columnspan=3, sticky="w", pady=(0, 8))

        default_out = str(Path(__file__).resolve().parents[2] / "data" / "BIN" / "gpssim.bin")
        self.exe_var = self.app_state.compiled_exe_path
        self.nav_file_var = self.app_state.latest_brdc_path
        self.output_file_var = tk.StringVar(value=default_out)

        self._path_row(panel, 1, "Executable Path", "Compiler Output", "The gps-sdr-sim executable from the Compiler Tab.", self.exe_var, self.ctrl.browse_exe)
        self._path_row(panel, 2, "Navigation File (-e)", "Required Ephemeris", "Specifies the path to your RINEX navigation file.", self.nav_file_var, self.ctrl.browse_nav)

        # --- AUTO-NAMING OUTPUT FILE ROW ---
        FieldLabel(panel, "Output File (-o)", "Smart Output Name", "Auto-generates based on parameters. Click Auto-Name to reset.").grid(row=3, column=0, sticky="w", pady=5, padx=(0, 8))
        f_out = tk.Frame(panel, bg=C_PANEL)
        f_out.grid(row=3, column=1, sticky="ew", pady=5, padx=(8, 6))
        f_out.columnconfigure(0, weight=1)
        
        StyledEntry(f_out, textvariable=self.output_file_var).grid(row=0, column=0, sticky="ew")
        
        btn_frame = tk.Frame(f_out, bg=C_PANEL)
        btn_frame.grid(row=0, column=1, sticky="e", padx=(8, 0))
        GhostButton(btn_frame, text="Auto-Name", command=self.ctrl.force_auto_name).pack(side=tk.LEFT, padx=(0, 4))
        GhostButton(btn_frame, text="Browse", command=self.ctrl.browse_output).pack(side=tk.LEFT)

        # --- 2. TRAJECTORY & MOTION SECTION ---
        SectionLabel(panel, "2. Location and Movement").grid(row=4, column=0, columnspan=3, sticky="w", pady=(16, 8))
        
        mode_box = ttk.Notebook(panel)
        mode_box.grid(row=5, column=0, columnspan=3, sticky="ew", pady=(0, 12))
        self.motion_mode_var = tk.StringVar(value="static")
        
        self.static_coord_var = tk.StringVar(value="llh")
        self.llh_lat_var, self.llh_lon_var, self.llh_hgt_var = tk.StringVar(value="35.681236"), tk.StringVar(value="139.767125"), tk.StringVar(value="40")
        self.ecef_x_var, self.ecef_y_var, self.ecef_z_var = tk.StringVar(), tk.StringVar(), tk.StringVar()
        self.traj_format_var = tk.StringVar(value="ecef")
        self.csv_file_var, self.nmea_file_var = tk.StringVar(), tk.StringVar()

        self._build_static_tab(mode_box)
        self._build_csv_tab(mode_box)
        self._build_nmea_tab(mode_box)
        mode_box.bind("<<NotebookTabChanged>>", lambda e: self.motion_mode_var.set(["static", "csv", "nmea"][mode_box.index(mode_box.select())]))

        # --- 3. SIGNAL & TIME PARAMETERS SECTION ---
        sig_box = tk.LabelFrame(panel, text="3. Hardware & Time Adjustments", bg=C_PANEL, fg=C_ACCENT, font=("Courier New", 9, "bold"), padx=10, pady=8, highlightbackground=C_BORDER)
        sig_box.grid(row=6, column=0, columnspan=3, sticky="ew", pady=(8, 12))
        
        self.duration_var = tk.StringVar(value="300")
        self.sample_rate_var = tk.StringVar(value="2600000")
        self.iq_bits_var = tk.StringVar(value="16")
        self.start_time_var = tk.StringVar(value="")
        self.toc_time_var = tk.StringVar(value="")
        self.leap_sec_var = tk.StringVar(value="")

        FieldLabel(sig_box, "Duration (-d)", "Simulation Length", "Length in seconds. Max static is 86,400s (24h), dynamic is 300s (5m).").grid(row=0, column=0, sticky="w", pady=4)
        tk.Spinbox(sig_box, from_=1, to=86400, textvariable=self.duration_var, bg=C_ENTRY_BG, fg=C_TEXT, buttonbackground=C_BORDER, relief=tk.FLAT, width=12).grid(row=0, column=1, sticky="w", pady=4, padx=(8, 20))

        FieldLabel(sig_box, "Sample Rate (-s)", "Hardware Frequency", "Base sample rate in Hz. HackRF defaults to 2600000. BladeRF/LimeSDR often need 5000000+.").grid(row=0, column=2, sticky="w", pady=4)
        StyledEntry(sig_box, textvariable=self.sample_rate_var, width=14).grid(row=0, column=3, sticky="w", pady=4, padx=(8, 20))

        FieldLabel(sig_box, "I/Q Bits (-b)", "Bit Depth", "1, 8, or 16 bits.\nHackRF = 8\nBladeRF/USRP = 16").grid(row=0, column=4, sticky="w", pady=4)
        ttk.Combobox(sig_box, textvariable=self.iq_bits_var, values=["1", "8", "16"], state="readonly", width=5).grid(row=0, column=5, sticky="w", pady=4, padx=(8, 0))

        FieldLabel(sig_box, "Start Time (-t)", "Override Start", "Format: YYYY/MM/DD,hh:mm:ss\nOverrides the exact day and clock time the simulation begins.").grid(row=1, column=0, sticky="w", pady=4)
        StyledEntry(sig_box, textvariable=self.start_time_var, width=18).grid(row=1, column=1, sticky="w", pady=4, padx=(8, 20))

        FieldLabel(sig_box, "TOC/TOE Override (-T)", "Override TOC/TOE", "Format: YYYY/MM/DD,hh:mm:ss\nOverwrites the internal Time of Clock (TOC) and Time of Ephemeris (TOE).").grid(row=1, column=2, sticky="w", pady=4)
        StyledEntry(sig_box, textvariable=self.toc_time_var, width=18).grid(row=1, column=3, sticky="w", pady=4, padx=(8, 20))

        FieldLabel(sig_box, "Leap Second (-L)", "Future Leap Second", "Format: wnslf,dn,dtslf\nManually pushes a future leap-second event into the stream.").grid(row=1, column=4, sticky="w", pady=4)
        StyledEntry(sig_box, textvariable=self.leap_sec_var, width=14).grid(row=1, column=5, sticky="w", pady=4, padx=(8, 0))

        # --- 4. ADVANCED PHYSICS SECTION ---
        phys_box = tk.LabelFrame(panel, text="4. Advanced Physics & Debugging", bg=C_PANEL, fg=C_ACCENT, font=("Courier New", 9, "bold"), padx=10, pady=8, highlightbackground=C_BORDER)
        phys_box.grid(row=7, column=0, columnspan=3, sticky="ew", pady=(0, 16))
        
        self.disable_iono_var = tk.BooleanVar(value=False)
        self.disable_pathloss_var = tk.BooleanVar(value=False)
        self.verbose_var = tk.BooleanVar(value=False)

        c1 = tk.Checkbutton(phys_box, text="Disable Ionospheric Math (-i)", variable=self.disable_iono_var, bg=C_PANEL, fg=C_TEXT, selectcolor=C_ENTRY_BG, activebackground=C_PANEL, activeforeground=C_TEXT, cursor="hand2")
        c1.grid(row=0, column=0, sticky="w", padx=(0, 20))
        attach_advanced_tooltip(c1, "Disable Ionosphere (-i)", "Disables ionospheric delay math. Useful for advanced troubleshooting or spacecraft simulation outside Earth's atmosphere.")

        c2 = tk.Checkbutton(phys_box, text="Flat Power Levels (-p)", variable=self.disable_pathloss_var, bg=C_PANEL, fg=C_TEXT, selectcolor=C_ENTRY_BG, activebackground=C_PANEL, activeforeground=C_TEXT, cursor="hand2")
        c2.grid(row=0, column=1, sticky="w", padx=(0, 20))
        attach_advanced_tooltip(c2, "Disable Path Loss (-p)", "Disables natural signal loss math over long distances. Keeps transmission power perfectly flat and solid.")

        c3 = tk.Checkbutton(phys_box, text="Verbose Mode (-v)", variable=self.verbose_var, bg=C_PANEL, fg=C_TEXT, selectcolor=C_ENTRY_BG, activebackground=C_PANEL, activeforeground=C_TEXT, cursor="hand2")
        c3.grid(row=0, column=2, sticky="w", padx=(0, 0))
        attach_advanced_tooltip(c3, "Verbose Mode (-v)", "Prints a real-time breakdown of every single tracking channel on your command screen while the data is generating.")

        # --- ACTION BUTTONS ---
        action = tk.Frame(panel, bg=C_PANEL)
        action.grid(row=8, column=0, columnspan=3, sticky="ew", pady=(10, 0))
        
        self.generate_btn = PrimaryButton(action, text="Generate .bin", command=self.ctrl.start_generate)
        self.generate_btn.pack(side=tk.LEFT)
        
        self.stop_btn = GhostButton(action, text="Stop", command=self.ctrl.stop_generate, state=tk.DISABLED)
        self.stop_btn.pack(side=tk.LEFT, padx=(8, 0))
        
        # CLEAR BINS BUTTON
        self.clear_btn = GhostButton(action, text="Clear BINs", command=self.ctrl.clear_bins)
        self.clear_btn.pack(side=tk.LEFT, padx=(8, 0))
        
        # --- FIXED: LIVE PERCENTAGE READOUT WITH DOUBLEVAR ---
        pb_frame = tk.Frame(action, bg=C_PANEL)
        pb_frame.pack(side=tk.RIGHT, padx=(8, 0), fill=tk.X, expand=True)
        
        self.progress_label = tk.Label(pb_frame, text="Idle", fg=C_MUTED, bg=C_PANEL, font=("Courier New", 9, "bold"))
        self.progress_label.pack(side=tk.TOP, anchor="e", pady=(0, 2))
        
        # We now attach a tk.DoubleVar() to force the UI to render updates immediately
        self.progress_var = tk.DoubleVar(value=0.0)
        self.process_progress = ttk.Progressbar(pb_frame, variable=self.progress_var, mode="determinate", maximum=100.0, style="Accent.Horizontal.TProgressbar")
        self.process_progress.pack(side=tk.BOTTOM, fill=tk.X)
        # -----------------------------------------------------

        # Log
        log_frame = tk.Frame(container, bg=C_BG, padx=24)
        log_frame.grid(row=3, column=0, sticky="nsew", pady=(0, 16))
        log_frame.rowconfigure(1, weight=1)
        log_frame.columnconfigure(0, weight=1)

        SectionLabel(log_frame, "Generation Log", bg=C_BG).grid(row=0, column=0, sticky="w")
        self.log = scrolledtext.ScrolledText(log_frame, height=9, bg=C_ENTRY_BG, fg=C_TEXT, font=FONT_MONO, relief=tk.FLAT, state=tk.DISABLED)
        self.log.grid(row=1, column=0, sticky="nsew", pady=(6,0))
        self.log.tag_config("success", foreground=C_SUCCESS)
        self.log.tag_config("error", foreground=C_ERROR)
        self.log.tag_config("muted", foreground=C_MUTED)

    def _path_row(self, parent, row, label, tt_title, tt_desc, var, command):
        FieldLabel(parent, label, tt_title, tt_desc).grid(row=row, column=0, sticky="w", pady=5, padx=(0, 8))
        StyledEntry(parent, textvariable=var).grid(row=row, column=1, sticky="ew", pady=5, padx=(8, 6))
        GhostButton(parent, text="Browse", command=command).grid(row=row, column=2, sticky="e", pady=5)

    def _build_static_tab(self, nb):
        t = StyledFrame(nb, padx=10, pady=8)
        nb.add(t, text="Static location (-l / -c)")
        tk.Radiobutton(t, text="Lat/Lon/Height (-l)", value="llh", variable=self.static_coord_var, bg=C_PANEL, fg=C_TEXT, selectcolor=C_ENTRY_BG).grid(row=0, column=0, sticky="w")
        tk.Radiobutton(t, text="ECEF X/Y/Z (-c)", value="ecef", variable=self.static_coord_var, bg=C_PANEL, fg=C_TEXT, selectcolor=C_ENTRY_BG).grid(row=0, column=1, sticky="w")
        StyledEntry(t, textvariable=self.llh_lat_var, width=14).grid(row=1, column=0, padx=4, pady=2)
        StyledEntry(t, textvariable=self.llh_lon_var, width=14).grid(row=2, column=0, padx=4, pady=2)
        StyledEntry(t, textvariable=self.llh_hgt_var, width=14).grid(row=3, column=0, padx=4, pady=2)

    def _build_csv_tab(self, nb):
        t = StyledFrame(nb, padx=10, pady=8)
        nb.add(t, text="Dynamic CSV (-u / -x)")
        tk.Radiobutton(t, text="ECEF Format (-u)", value="ecef", variable=self.traj_format_var, bg=C_PANEL, fg=C_TEXT, selectcolor=C_ENTRY_BG).grid(row=0, column=0, sticky="w", pady=(0, 6))
        tk.Radiobutton(t, text="LLH Format (-x)", value="llh", variable=self.traj_format_var, bg=C_PANEL, fg=C_TEXT, selectcolor=C_ENTRY_BG).grid(row=0, column=1, sticky="w", pady=(0, 6))
        self._path_row(t, 1, "CSV file", "User Motion CSV", "A file containing ECEF or Lat/Lon trajectory data over time.", self.csv_file_var, self.ctrl.browse_csv)

    def _build_nmea_tab(self, nb):
        t = StyledFrame(nb, padx=10, pady=8)
        nb.add(t, text="NMEA GGA (-g)")
        self._path_row(t, 0, "GGA file", "NMEA Trajectory", "Standard NMEA GGA formatted log file for dynamic routing.", self.nmea_file_var, self.ctrl.browse_nmea)

    def log_line(self, msg: str, tag: str = "info"):
        import datetime
        ts = datetime.datetime.now(datetime.UTC).strftime("%H:%M:%S")
        self.log.config(state=tk.NORMAL)
        self.log.insert(tk.END, f"[{ts}]  {msg}\n", tag)
        self.log.see(tk.END)
        self.log.config(state=tk.DISABLED)

