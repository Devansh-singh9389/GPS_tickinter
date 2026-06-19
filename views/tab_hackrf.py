import tkinter as tk
from tkinter import ttk, scrolledtext
from core.theme import *
from views.components import StyledFrame, SectionLabel, FieldLabel, StyledEntry, PrimaryButton, GhostButton, Divider, attach_advanced_tooltip, ScrollableFrame

class HackRFView(tk.Frame):
    def __init__(self, master, controller, app_state):
        super().__init__(master, bg=C_BG)
        self.ctrl = controller
        self.app_state = app_state
        
        self.scroll = ScrollableFrame(self)
        self.scroll.pack(fill=tk.BOTH, expand=True)
        self._build_ui(self.scroll.content)

    def _build_ui(self, container):
        container.columnconfigure(0, weight=1)

        hdr = tk.Frame(container, bg=C_BG, padx=24, pady=14)
        hdr.grid(row=0, column=0, sticky="ew")
        tk.Label(hdr, text="HackRF One Transmitter/Receiver", font=FONT_TITLE, fg=C_TEXT, bg=C_BG).pack(side=tk.LEFT)
        Divider(container).grid(row=1, column=0, sticky="ew", padx=24)

        panel = StyledFrame(container, padx=24, pady=16)
        panel.grid(row=2, column=0, sticky="ew", padx=24, pady=16)
        panel.columnconfigure(1, weight=1)

        # Variables
        self.mode_var = tk.StringVar(value="-t")
        self.file_var = self.app_state.latest_bin_path
        self.wav_var = tk.BooleanVar(value=False)

        self.freq_var = tk.StringVar(value="1575420000")
        self.sr_var = tk.StringVar(value="2600000")
        self.bw_var = tk.StringVar(value="")
        self.force_var = tk.BooleanVar(value=False)

        self.amp_var = tk.StringVar(value="0")
        self.ant_power_var = tk.StringVar(value="0")
        self.tx_vga_var = tk.StringVar(value="20")
        self.rx_lna_var = tk.StringVar(value="32")
        self.rx_vga_var = tk.StringVar(value="30")

        self.serial_var = tk.StringVar(value="")
        self.hw_trigger_var = tk.BooleanVar(value=False)
        self.repeat_var = tk.BooleanVar(value=False)
        self.cw_var = tk.StringVar(value="")
        self.num_samples_var = tk.StringVar(value="")

        # --- 1. CORE DATA DIRECTION ---
        SectionLabel(panel, "1. Core Data Direction").grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 8))
        
        mode_frame = tk.Frame(panel, bg=C_PANEL)
        mode_frame.grid(row=1, column=0, columnspan=2, sticky="w", pady=(0, 8))
        tk.Radiobutton(mode_frame, text="Transmit (-t)", value="-t", variable=self.mode_var, bg=C_PANEL, fg=C_TEXT, selectcolor=C_ENTRY_BG, activebackground=C_PANEL, activeforeground=C_ACCENT, cursor="hand2").pack(side=tk.LEFT, padx=(0, 16))
        tk.Radiobutton(mode_frame, text="Receive (-r)", value="-r", variable=self.mode_var, bg=C_PANEL, fg=C_TEXT, selectcolor=C_ENTRY_BG, activebackground=C_PANEL, activeforeground=C_ACCENT, cursor="hand2").pack(side=tk.LEFT)
        
        w_chk = tk.Checkbutton(mode_frame, text="Save as WAV (-w)", variable=self.wav_var, bg=C_PANEL, fg=C_TEXT, selectcolor=C_ENTRY_BG, activebackground=C_PANEL, activeforeground=C_TEXT)
        w_chk.pack(side=tk.LEFT, padx=(16, 0))
        attach_advanced_tooltip(w_chk, "WAV Format (-w)", "Receive mode only. Saves received data as a .wav file with audio-style header tags for retro-compatibility.")

        self._path_row(panel, 2, "Target File", "I/Q File", "The 8-bit signed I/Q file to broadcast or save to. Typing '-' redirects to stdout/stdin.", self.file_var, self.ctrl.browse_file)

        # --- 2. FREQUENCY & RADIO WAVES ---
        f_box = tk.LabelFrame(panel, text="2. Frequency and Radio Management", bg=C_PANEL, fg=C_ACCENT, font=("Courier New", 9, "bold"), padx=10, pady=8, highlightbackground=C_BORDER)
        f_box.grid(row=3, column=0, columnspan=2, sticky="ew", pady=(12, 8))

        FieldLabel(f_box, "Center Freq (-f)", "Target Frequency", "Sets the core center frequency in Hz. Standard GPS L1 is 1575420000.").grid(row=0, column=0, sticky="w", pady=4)
        StyledEntry(f_box, textvariable=self.freq_var, width=16).grid(row=0, column=1, sticky="w", padx=(8, 20), pady=4)

        FieldLabel(f_box, "Sample Rate (-s)", "USB Bus Speed", "Adjusts how fast data passes through USB (Hz). Must match simulation speed perfectly (e.g. 2600000).").grid(row=0, column=2, sticky="w", pady=4)
        StyledEntry(f_box, textvariable=self.sr_var, width=12).grid(row=0, column=3, sticky="w", padx=(8, 20), pady=4)

        FieldLabel(f_box, "Baseband BW (-b)", "Hardware Filter Width", "Sets internal hardware analog filter width (Hz). Leave blank for automatic optimization.").grid(row=1, column=0, sticky="w", pady=4)
        StyledEntry(f_box, textvariable=self.bw_var, width=16).grid(row=1, column=1, sticky="w", padx=(8, 20), pady=4)

        F_chk = tk.Checkbutton(f_box, text="Force Override (-F)", variable=self.force_var, bg=C_PANEL, fg=C_ERROR, selectcolor=C_ENTRY_BG, activebackground=C_PANEL, activeforeground=C_TEXT)
        F_chk.grid(row=1, column=2, columnspan=2, sticky="w")
        attach_advanced_tooltip(F_chk, "Force Override (-F)", "Bypasses built-in software safety limits, allowing custom hardware modifications outside the standard 1MHz-6GHz spectrum.")

        # --- 3. GAIN & POWER OPTIONS ---
        g_box = tk.LabelFrame(panel, text="3. Amplifiers and Power Options", bg=C_PANEL, fg=C_ACCENT, font=("Courier New", 9, "bold"), padx=10, pady=8, highlightbackground=C_BORDER)
        g_box.grid(row=4, column=0, columnspan=2, sticky="ew", pady=(8, 8))

        FieldLabel(g_box, "Amp Enable (-a)", "RF Amplifier", "0=Off (Nearby lab benches). 1=On (Max hardware range).").grid(row=0, column=0, sticky="w", pady=4)
        ttk.Combobox(g_box, textvariable=self.amp_var, values=["0", "1"], state="readonly", width=4).grid(row=0, column=1, sticky="w", padx=(8, 20))

        FieldLabel(g_box, "Antenna Power (-p)", "DC Bias Port", "0=Off. 1=Sends 3.3v down coax cable to power active external GPS patch antennas.").grid(row=0, column=2, sticky="w", pady=4)
        ttk.Combobox(g_box, textvariable=self.ant_power_var, values=["0", "1"], state="readonly", width=4).grid(row=0, column=3, sticky="w", padx=(8, 20))

        FieldLabel(g_box, "TX VGA Gain (-x)", "Transmit Volume", "0 to 47 dB in 1 dB steps. Keep around 20-30 for GPS simulation to prevent overpowering devices.").grid(row=1, column=0, sticky="w", pady=4)
        StyledEntry(g_box, textvariable=self.tx_vga_var, width=8).grid(row=1, column=1, sticky="w", padx=(8, 20))

        FieldLabel(g_box, "RX LNA Gain (-l)", "Receive Listening Vol", "0 to 40 dB in strict 8 dB increments.").grid(row=1, column=2, sticky="w", pady=4)
        StyledEntry(g_box, textvariable=self.rx_lna_var, width=8).grid(row=1, column=3, sticky="w", padx=(8, 20))

        FieldLabel(g_box, "RX VGA Gain (-g)", "Receive Baseband Vol", "0 to 62 dB in 2 dB increments.").grid(row=1, column=4, sticky="w", pady=4)
        StyledEntry(g_box, textvariable=self.rx_vga_var, width=8).grid(row=1, column=5, sticky="w", padx=(8, 0))

        # --- 4. ADVANCED SYNC ---
        s_box = tk.LabelFrame(panel, text="4. Advanced Synchronization", bg=C_PANEL, fg=C_ACCENT, font=("Courier New", 9, "bold"), padx=10, pady=8, highlightbackground=C_BORDER)
        s_box.grid(row=5, column=0, columnspan=2, sticky="ew", pady=(8, 8))

        FieldLabel(s_box, "Serial Num (-d)", "Target Specific HackRF", "Selects a specific board if multiple are plugged in.").grid(row=0, column=0, sticky="w", pady=4)
        StyledEntry(s_box, textvariable=self.serial_var, width=16).grid(row=0, column=1, sticky="w", padx=(8, 20), pady=4)

        H_chk = tk.Checkbutton(s_box, text="Hardware Trigger (-H)", variable=self.hw_trigger_var, bg=C_PANEL, fg=C_TEXT, selectcolor=C_ENTRY_BG)
        H_chk.grid(row=0, column=2, sticky="w", padx=(0, 20))
        attach_advanced_tooltip(H_chk, "Hardware Trigger (-H)", "Halts execution until it detects an electrical pulse on the physical pin header. Synchronizes multiple HackRFs.")

        R_chk = tk.Checkbutton(s_box, text="Infinite Loop (-R)", variable=self.repeat_var, bg=C_PANEL, fg=C_TEXT, selectcolor=C_ENTRY_BG)
        R_chk.grid(row=0, column=3, sticky="w")
        attach_advanced_tooltip(R_chk, "Repeat Transfer (-R)", "Instantly restarts from the beginning of the file when it hits the end.")

        FieldLabel(s_box, "CW Mode (-c)", "Continuous Wave", "Ignores files and blasts a single unmodulated carrier wave tone at a set power level. Used for calibration.").grid(row=1, column=0, sticky="w", pady=4)
        StyledEntry(s_box, textvariable=self.cw_var, width=16).grid(row=1, column=1, sticky="w", padx=(8, 20), pady=4)

        FieldLabel(s_box, "Sample Limit (-n)", "Block Execution Limit", "Stops operations automatically after a precise count of data blocks or raw signal samples have finished processing.").grid(row=1, column=2, sticky="w", pady=4)
        StyledEntry(s_box, textvariable=self.num_samples_var, width=16).grid(row=1, column=3, sticky="w", padx=(8, 0), pady=4)

        # --- ACTION BUTTONS ---
        btn_row = tk.Frame(panel, bg=C_PANEL)
        btn_row.grid(row=6, column=0, columnspan=2, sticky="w", pady=(16, 0))

        self.start_btn = PrimaryButton(btn_row, text="▶  Start Transfer", command=self.ctrl.start_tx)
        self.start_btn.pack(side=tk.LEFT, padx=(0, 8))

        self.stop_btn = GhostButton(btn_row, text="■  Stop", command=self.ctrl.stop_tx, state=tk.DISABLED)
        self.stop_btn.pack(side=tk.LEFT)

        # Log
        log_frame = tk.Frame(container, bg=C_BG, padx=24)
        log_frame.grid(row=3, column=0, sticky="nsew", pady=(0, 16))
        log_frame.rowconfigure(1, weight=1)
        log_frame.columnconfigure(0, weight=1)
        
        SectionLabel(log_frame, "Transmission Log", bg=C_BG).grid(row=0, column=0, sticky="w")
        self.log = scrolledtext.ScrolledText(log_frame, height=10, bg=C_ENTRY_BG, fg=C_TEXT, font=FONT_MONO, relief=tk.FLAT, state=tk.DISABLED)
        self.log.grid(row=1, column=0, sticky="nsew", pady=(6,0))
        self.log.tag_config("error", foreground=C_ERROR)
        self.log.tag_config("success", foreground=C_SUCCESS)
        self.log.tag_config("muted", foreground=C_MUTED)

    def _path_row(self, parent, row, label, tt_title, tt_desc, var, command):
        FieldLabel(parent, label, tt_title, tt_desc).grid(row=row, column=0, sticky="w", pady=5, padx=(0, 8))
        f = tk.Frame(parent, bg=C_PANEL)
        f.grid(row=row, column=1, sticky="ew", pady=5)
        f.columnconfigure(0, weight=1)
        StyledEntry(f, textvariable=var).grid(row=0, column=0, sticky="ew", padx=(8, 6))
        GhostButton(f, text="Browse", command=command).grid(row=0, column=1, sticky="e")

    def log_line(self, msg: str, tag: str = "info"):
        import datetime
        ts = datetime.datetime.now(datetime.UTC).strftime("%H:%M:%S")
        self.log.config(state=tk.NORMAL)
        self.log.insert(tk.END, f"[{ts}]  {msg}\n", tag)
        self.log.see(tk.END)
        self.log.config(state=tk.DISABLED)