import os
import tkinter as tk
from tkinter import ttk, scrolledtext
from core.theme import *
from views.components import StyledFrame, SectionLabel, FieldLabel, StyledEntry, PrimaryButton, GhostButton, Divider, attach_advanced_tooltip, ScrollableFrame
from pathlib import Path
from core.config import DATA_DIR_COMPILED

class CompilerView(tk.Frame):
    def __init__(self, master, controller):
        super().__init__(master, bg=C_BG)
        self.ctrl = controller
        
        self.scroll = ScrollableFrame(self)
        self.scroll.pack(fill=tk.BOTH, expand=True)
        self._build_ui(self.scroll.content)

    def _build_ui(self, container):
        container.columnconfigure(0, weight=1)
        container.rowconfigure(2, weight=1)

        hdr = tk.Frame(container, bg=C_BG, padx=24, pady=14)
        hdr.grid(row=0, column=0, sticky="ew")
        tk.Label(hdr, text="GPS-SDR-SIM Compiler", font=FONT_TITLE, fg=C_TEXT, bg=C_BG).pack(side=tk.LEFT)
        tk.Label(hdr, text="Compile source code for simulation", font=FONT_BODY, fg=C_MUTED, bg=C_BG).pack(side=tk.RIGHT)
        Divider(container).grid(row=1, column=0, sticky="ew", padx=24)

        panel = StyledFrame(container, padx=16, pady=14)
        panel.grid(row=2, column=0, sticky="nsew", padx=24, pady=12)
        panel.columnconfigure(1, weight=1)

        SectionLabel(panel, "Compiler Configuration").grid(row=0, column=0, columnspan=3, sticky="w", pady=(0, 8))

        # Core Variables
        self.src_dir_var = tk.StringVar(value=str(Path.home() / "Code" / "TRY 1" / "gps-sdr-sim"))
        self.user_motion_size_var = tk.StringVar(value="3000")
        self.float_carr_phase_var = tk.BooleanVar(value=False)
        self.max_sat_var = tk.StringVar(value="32")
        self.max_chan_var = tk.StringVar(value="16")
        self.optimization_var = tk.StringVar(value="Recommended Standard")
        
        # New Official Feature Variables
        self.large_file_var = tk.BooleanVar(value=True)
        self.multithread_var = tk.BooleanVar(value=False)
        self.arch_native_var = tk.BooleanVar(value=False)
        self.fast_math_var = tk.BooleanVar(value=False)

        self.output_exe_var = tk.StringVar(value="gps-sdr-sim")
        self.output_dir_var = tk.StringVar(value=str(DATA_DIR_COMPILED))
        self.clean_before_build_var = tk.BooleanVar(value=False)
        self.build_mode_var = tk.StringVar(value="auto")

        self._path_row(panel, 1, "Source directory", "Source Code", "The folder containing gpssim.c and gpssim.h.", self.src_dir_var, self.ctrl.browse_source)
        
        FieldLabel(panel, "User Motion Size (s)", "Simulation Duration", "Maximum simulation duration in seconds (default: 3000).").grid(row=2, column=0, sticky="w", pady=5)
        spin = tk.Spinbox(panel, from_=1, to=86400, increment=100, textvariable=self.user_motion_size_var, bg=C_ENTRY_BG, fg=C_TEXT, buttonbackground=C_BORDER, relief=tk.FLAT, width=10, font=FONT_BODY)
        spin.grid(row=2, column=1, sticky="w", pady=5, padx=(8, 0))

        FieldLabel(panel, "Optimization", "Compiler Optimization", "-O0 to -O3 flag. Higher means faster simulation but longer compile time.").grid(row=3, column=0, sticky="w", pady=5)
        ttk.Combobox(panel, textvariable=self.optimization_var, values=list(OPTIMIZATION_OPTIONS.keys()), state="readonly", width=20).grid(row=3, column=1, sticky="w", pady=5, padx=(8, 0))

        # --- NEW: OFFICIAL COMPILER FEATURES SECTION ---
        feat_box = tk.LabelFrame(panel, text="Official Compiler Features", bg=C_PANEL, fg=C_ACCENT, font=("Courier New", 9, "bold"), padx=10, pady=8, highlightbackground=C_BORDER)
        feat_box.grid(row=4, column=0, columnspan=3, sticky="ew", pady=(12, 8))

        c1 = tk.Checkbutton(feat_box, text="Large File Support (>2GB I/Q)", variable=self.large_file_var, bg=C_PANEL, fg=C_TEXT, selectcolor=C_ENTRY_BG, activebackground=C_PANEL, activeforeground=C_TEXT, cursor="hand2")
        c1.grid(row=0, column=0, sticky="w", padx=(0, 20), pady=4)
        attach_advanced_tooltip(c1, "Large File Support (-D_FILE_OFFSET_BITS=64)", "Generating GPS I/Q files creates massive binary data files (often multiple gigabytes). This ensures older or 32-bit systems won't crash.")

        c2 = tk.Checkbutton(feat_box, text="Multi-Threading (Real-time SDR)", variable=self.multithread_var, bg=C_PANEL, fg=C_TEXT, selectcolor=C_ENTRY_BG, activebackground=C_PANEL, activeforeground=C_TEXT, cursor="hand2")
        c2.grid(row=0, column=1, sticky="w", padx=(0, 20), pady=4)
        attach_advanced_tooltip(c2, "Multi-Threading Flag (-lpthread)", "If using a fork designed for real-time streaming, this links the POSIX threads library so it can calculate and stream simultaneously.")

        c3 = tk.Checkbutton(feat_box, text="Native CPU Architecture", variable=self.arch_native_var, bg=C_PANEL, fg=C_TEXT, selectcolor=C_ENTRY_BG, activebackground=C_PANEL, activeforeground=C_TEXT, cursor="hand2")
        c3.grid(row=1, column=0, sticky="w", padx=(0, 20), pady=4)
        attach_advanced_tooltip(c3, "CPU Architecture Optimizations (-march=native)", "Tells the compiler to use every advanced instruction your exact computer CPU supports (like AVX or SSE) for much faster math rendering.")

        c4 = tk.Checkbutton(feat_box, text="Extreme Speed Math", variable=self.fast_math_var, bg=C_PANEL, fg=C_TEXT, selectcolor=C_ENTRY_BG, activebackground=C_PANEL, activeforeground=C_TEXT, cursor="hand2")
        c4.grid(row=1, column=1, sticky="w", padx=(0, 20), pady=4)
        attach_advanced_tooltip(c4, "Fast Math (-ffast-math)", "Breaks strict IEEE floating-point math rules for extreme speeds. Note: can occasionally cause minor math rounding errors.")
        # -----------------------------------------------

        # --- DYNAMIC EXTRA CFLAGS LIST ---
        FieldLabel(panel, "Extra CFLAGS", "Custom Build Flags", "Enable specific C compiler flags to modify how the executable is built.").grid(row=5, column=0, sticky="nw", pady=5)
        
        self.flags_main_frame = tk.Frame(panel, bg=C_PANEL)
        self.flags_main_frame.grid(row=5, column=1, columnspan=2, sticky="ew", pady=5, padx=(8, 0))
        
        self.flags_list_frame = tk.Frame(self.flags_main_frame, bg=C_PANEL)
        self.flags_list_frame.pack(fill=tk.X)
        self.flag_vars = [] 
        
        # Pre-load only Debugging/Quality flags here now!
        default_flags = [
            ("-Wall", True, "Code Quality", 'Turns on "all warnings". Tells the compiler to warn you of potential bugs before building.'),
            ("-g", False, "Debugging", "Adds debugging information. Use this to find out why the program is crashing.")
        ]
        
        for flag_text, start_checked, t_title, t_desc in default_flags:
            self._add_flag_row(default_text=flag_text, is_default=True, start_checked=start_checked, tooltip_title=t_title, tooltip_desc=t_desc)
        
        self.add_flag_btn = GhostButton(self.flags_main_frame, text="+ Add Custom Flag", command=lambda: self._add_flag_row(""))
        self.add_flag_btn.pack(anchor="w", pady=(4, 0))
        # ----------------------------------------

        FieldLabel(panel, "Output executable", "Binary Name", "The name of the resulting compiled program.").grid(row=6, column=0, sticky="w", pady=5)
        StyledEntry(panel, textvariable=self.output_exe_var).grid(row=6, column=1, columnspan=2, sticky="ew", pady=5, padx=(8, 0))

        self._path_row(panel, 7, "Output directory", "Build Destination", "Where the compiled executable will be saved.", self.output_dir_var, self.ctrl.browse_output_dir)

        self._build_header_config(panel, 8)

        tk.Checkbutton(panel, text="Clean before build", variable=self.clean_before_build_var, bg=C_PANEL, fg=C_TEXT, activebackground=C_PANEL, activeforeground=C_ACCENT, selectcolor=C_ENTRY_BG, font=FONT_BODY, cursor="hand2").grid(row=9, column=0, columnspan=3, sticky="w", pady=(6, 2))

        mode_row = tk.Frame(panel, bg=C_PANEL)
        mode_row.grid(row=10, column=0, columnspan=3, sticky="w", pady=4)
        for text, value in [("Auto (prefer Makefile)", "auto"), ("Force make", "force_make"), ("Force gcc", "force_gcc")]:
            tk.Radiobutton(mode_row, text=text, value=value, variable=self.build_mode_var, bg=C_PANEL, fg=C_TEXT, activebackground=C_PANEL, activeforeground=C_ACCENT, selectcolor=C_ENTRY_BG, font=FONT_BODY, cursor="hand2").pack(side=tk.LEFT, padx=(0, 12))

        action = tk.Frame(panel, bg=C_PANEL)
        action.grid(row=11, column=0, columnspan=3, sticky="ew", pady=(10, 0))
        self.compile_btn = PrimaryButton(action, text="Compile", command=self.ctrl.start_compile)
        self.compile_btn.pack(side=tk.LEFT)
        self.clear_btn = GhostButton(action, text="Clear Compilation", command=self.ctrl.clear_compilation)
        self.clear_btn.pack(side=tk.LEFT, padx=(8, 0))
        
        self.exe_status_var = tk.StringVar(value="No executable compiled yet")
        tk.Label(action, textvariable=self.exe_status_var, fg=C_MUTED, bg=C_PANEL, font=("Courier New", 9)).pack(side=tk.LEFT, padx=(12, 0))

        self.process_progress = ttk.Progressbar(action, mode="indeterminate", style="Accent.Horizontal.TProgressbar", length=170)
        self.process_progress.pack(side=tk.RIGHT, padx=(8, 0))

        # Log
        log_frame = tk.Frame(container, bg=C_BG, padx=24)
        log_frame.grid(row=3, column=0, sticky="nsew", pady=(0, 16))
        log_frame.rowconfigure(1, weight=1)
        log_frame.columnconfigure(0, weight=1)

        SectionLabel(log_frame, "Compiler Log", bg=C_BG).grid(row=0, column=0, sticky="w")
        self.log = scrolledtext.ScrolledText(log_frame, height=11, bg=C_ENTRY_BG, fg=C_TEXT, font=FONT_MONO, relief=tk.FLAT, state=tk.DISABLED)
        self.log.grid(row=1, column=0, sticky="nsew", pady=(6,0))
        self.log.tag_config("success", foreground=C_SUCCESS)
        self.log.tag_config("error", foreground=C_ERROR)
        self.log.tag_config("warn", foreground=C_WARNING)
        self.log.tag_config("muted", foreground=C_MUTED)

    def _path_row(self, parent, row, label, tt_title, tt_desc, var, command):
        FieldLabel(parent, label, tt_title, tt_desc).grid(row=row, column=0, sticky="w", pady=5, padx=(0, 8))
        StyledEntry(parent, textvariable=var, width=120).grid(row=row, column=1, sticky="ew", pady=5, padx=(8, 6))
        GhostButton(parent, text="Browse", command=command).grid(row=row, column=2, sticky="e", pady=5)

    def _build_header_config(self, parent, row):
        box = tk.LabelFrame(parent, text="Advanced Header Configuration (gpssim.h)", bg=C_PANEL, fg=C_ACCENT, font=("Courier New", 9, "bold"), padx=10, pady=8, highlightbackground=C_BORDER)
        box.grid(row=row, column=0, columnspan=3, sticky="ew", pady=(8, 4))
        box.columnconfigure(1, weight=1)
        box.columnconfigure(3, weight=1)

        phase = tk.Checkbutton(box, text="Enable high-precision carrier phase", variable=self.float_carr_phase_var, bg=C_PANEL, fg=C_TEXT, selectcolor=C_ENTRY_BG)
        phase.grid(row=0, column=0, columnspan=4, sticky="w", pady=(0, 6))

        FieldLabel(box, "User Motion").grid(row=1, column=0, sticky="w")
        tk.Spinbox(box, from_=1, to=86400, textvariable=self.user_motion_size_var, width=10, bg=C_ENTRY_BG, fg=C_TEXT, buttonbackground=C_BORDER, relief=tk.FLAT).grid(row=1, column=1, sticky="w", padx=(8, 14))

        FieldLabel(box, "Max satellites").grid(row=1, column=2, sticky="w")
        tk.Spinbox(box, from_=8, to=40, textvariable=self.max_sat_var, width=7, bg=C_ENTRY_BG, fg=C_TEXT, buttonbackground=C_BORDER, relief=tk.FLAT).grid(row=1, column=3, sticky="w", padx=(8, 0))

        FieldLabel(box, "Max channels").grid(row=2, column=0, sticky="w")
        tk.Spinbox(box, from_=4, to=32, textvariable=self.max_chan_var, width=10, bg=C_ENTRY_BG, fg=C_TEXT, buttonbackground=C_BORDER, relief=tk.FLAT).grid(row=2, column=1, sticky="w", padx=(8, 14), pady=4)

        GhostButton(box, text="Restore Header Backup", command=self.ctrl.restore_header).grid(row=2, column=2, columnspan=2, sticky="e", pady=4)

    def log_line(self, msg: str, tag: str = "info"):
        import datetime
        ts = datetime.datetime.now(datetime.UTC).strftime("%H:%M:%S")
        self.log.config(state=tk.NORMAL)
        self.log.insert(tk.END, f"[{ts}]  {msg}\n", tag)
        self.log.see(tk.END)
        self.log.config(state=tk.DISABLED)

    def _add_flag_row(self, default_text="", is_default=False, start_checked=True, tooltip_title="", tooltip_desc=""):
        row_frame = tk.Frame(self.flags_list_frame, bg=C_PANEL)
        row_frame.pack(fill=tk.X, pady=2)
        
        toggle_var = tk.BooleanVar(self, value=start_checked)
        text_var = tk.StringVar(self, value=default_text)
        
        chk = tk.Checkbutton(
            row_frame, 
            variable=toggle_var, 
            bg=C_PANEL, 
            fg=C_TEXT, 
            selectcolor=C_ENTRY_BG, 
            activebackground=C_PANEL, 
            activeforeground=C_TEXT
        )
        chk.pack(side=tk.LEFT)
        
        ent = StyledEntry(row_frame, textvariable=text_var)
        ent.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=4)
        
        if tooltip_title and tooltip_desc:
            attach_advanced_tooltip(ent, tooltip_title, tooltip_desc)
        
        if not is_default:
            del_btn = tk.Button(row_frame, text="✖", bg=C_PANEL, fg=C_ERROR, activebackground=C_PANEL, activeforeground=C_ERROR, relief=tk.FLAT, cursor="hand2", command=lambda f=row_frame, tv=toggle_var, sv=text_var: self._remove_flag_row(f, tv, sv))
            del_btn.pack(side=tk.LEFT, padx=(4, 0))
            
        self.flag_vars.append((toggle_var, text_var))

    def _remove_flag_row(self, frame, toggle_var, text_var):
        frame.destroy() 
        if (toggle_var, text_var) in self.flag_vars:
            self.flag_vars.remove((toggle_var, text_var)) 

    # --- THIS METHOD GRABS BOTH THE OFFICIAL AND CUSTOM FLAGS ---
    def get_active_cflags(self) -> str:
        active_flags = []
        
        # 1. Grab the Official Feature Checkboxes
        if self.large_file_var.get(): 
            active_flags.append("-D_FILE_OFFSET_BITS=64")
        if self.multithread_var.get(): 
            active_flags.append("-lpthread")
        if self.arch_native_var.get(): 
            active_flags.append("-march=native")
        if self.fast_math_var.get(): 
            active_flags.append("-ffast-math")
        
        # 2. Grab the Custom Dynamic Flags
        for toggle_var, text_var in self.flag_vars:
            if toggle_var.get() and text_var.get().strip():
                active_flags.append(text_var.get().strip())
                
        return " ".join(active_flags)