import datetime
import sys
import os
import platform
import shutil
import tkinter as tk
from tkinter import ttk, messagebox

# Ensure the root is on path for absolute imports
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from core.theme import C_BG, C_TAB_BG, C_MUTED, C_PANEL, C_ACCENT, FONT_BODY, C_BORDER, C_TEXT, FONT_HEADER, FONT_CLOCK
from models.app_state import AppState
from controllers.brdc_controller import BRDCController
from controllers.compiler_controller import CompilerController
from controllers.generator_controller import GeneratorController
from controllers.hackrf_controller import HackRFController

def run_preflight_check():
    """Checks if the required OS tools are installed before launching the app."""
    missing_tools = []
    
    # shutil.which() silently checks if a command exists in the system PATH
    if shutil.which("gcc") is None:
        missing_tools.append("GCC Compiler (gcc)")
    if shutil.which("hackrf_info") is None:
        missing_tools.append("HackRF Tools (hackrf_info)")

    if not missing_tools:
        return True # Everything is perfect!

    # If tools are missing, determine the OS to give precise instructions
    os_name = platform.system()
    instructions = ""
    
    if os_name == "Linux":
        instructions = "Run this in your terminal:\nsudo apt install build-essential hackrf"
    elif os_name == "Darwin": # macOS
        instructions = "Run this in your terminal:\nxcode-select --install\nbrew install hackrf"
    elif os_name == "Windows":
        instructions = ("1. Install MSYS2/MinGW and add gcc to your PATH.\n"
                        "2. Download HackRF Windows binaries and add to PATH.\n"
                        "3. Use Zadig to install the WinUSB driver for the HackRF.")

    root = tk.Tk()
    root.withdraw() # Hide the main window
    messagebox.showerror(
        "Missing Dependencies", 
        f"Your system is missing the following required tools:\n\n"
        f"{', '.join(missing_tools)}\n\n"
        f"How to fix this on {os_name}:\n{instructions}"
    )
    root.destroy()
    return False


class Application(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("509 Army WSP")
        self.geometry("1050x720")
        self.configure(bg=C_BG)
        
        # 1. Initialize Shared App State
        self.app_state = AppState()
        
        # 2. Configure global Tkinter styles
        self._configure_styles()
        
        # 3. Build Layout
        self._build_header()
        self._start_clock()
        self._build_layout()

    def _build_header(self) -> None:
        hdr = tk.Frame(self, bg=C_BG, pady=12, padx=20)
        hdr.pack(fill=tk.X, side=tk.TOP)

        # Left: app icon area + title
        left = tk.Frame(hdr, bg=C_BG)
        left.pack(side=tk.LEFT)

        # Antenna SVG rendered as Unicode stand-in (no asset required)
        icon_lbl = tk.Label(
            left, text="📡", font=("", 26), bg=C_BG, fg=C_ACCENT
        )
        icon_lbl.pack(side=tk.LEFT, padx=(0, 10))

        titles = tk.Frame(left, bg=C_BG)
        titles.pack(side=tk.LEFT)
        tk.Label(
            titles,
            text="509 Army Base WKSP",
            font=FONT_HEADER,
            fg=C_TEXT,
            bg=C_BG,
        ).pack(anchor=tk.W)
        tk.Label(
            titles,
            text="GNSS SPOOFER",
            font=FONT_BODY,
            fg=C_MUTED,
            bg=C_BG,
        ).pack(anchor=tk.W)

        # Right: live UTC clock
        right = tk.Frame(hdr, bg=C_BG)
        right.pack(side=tk.RIGHT)
        tk.Label(right, text="UTC", font=("Courier New", 9), fg=C_MUTED, bg=C_BG).pack()
        self._clock_var = tk.StringVar(value="--:--:--")
        tk.Label(
            right,
            textvariable=self._clock_var,
            font=FONT_CLOCK,
            fg=C_ACCENT,
            bg=C_BG,
        ).pack()

        # Separator below header
        tk.Frame(self, height=1, bg=C_BORDER).pack(fill=tk.X)

    def _start_clock(self) -> None:
        def tick():
            now = datetime.datetime.now(datetime.UTC)
            self._clock_var.set(now.strftime("%H:%M:%S"))
            self.after(1000, tick)
        tick()

    def _configure_styles(self):
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("App.TNotebook", background=C_TAB_BG, borderwidth=0)
        style.configure("App.TNotebook.Tab", background=C_TAB_BG, foreground=C_MUTED, font=FONT_BODY, padding=[18, 8], borderwidth=0)
        style.map("App.TNotebook.Tab", background=[("selected", C_PANEL)], foreground=[("selected", C_ACCENT)])
        style.configure("Accent.Horizontal.TProgressbar", troughcolor=C_BORDER, background=C_ACCENT, borderwidth=0, thickness=10)

    def _build_layout(self):
        notebook = ttk.Notebook(self, style="App.TNotebook")
        notebook.pack(fill=tk.BOTH, expand=True)

        # Tab 1: BRDC Downloader
        t1 = tk.Frame(notebook, bg=C_BG)
        notebook.add(t1, text="  BRDC Downloader  ")
        self.brdc_ctrl = BRDCController(t1, self.app_state)

        # Tab 2: GPS-SDR-SIM Compiler
        t2 = tk.Frame(notebook, bg=C_BG)
        notebook.add(t2, text="  GPS-SDR-SIM (Compiler)  ")
        self.compiler_ctrl = CompilerController(t2, self.app_state)

        # Tab 3: GPS-SDR-SIM Bin Convertor
        t3 = tk.Frame(notebook, bg=C_BG)
        notebook.add(t3, text="  GPS-SDR-SIM (Bin Convertor)  ")
        self.generator_ctrl = GeneratorController(t3, self.app_state)

        # Tab 4: HackRF Transmitter
        t4 = tk.Frame(notebook, bg=C_BG)
        notebook.add(t4, text="  HackRF Transfer  ")
        self.hackrf_ctrl = HackRFController(t4, self.app_state)

# --- EXECUTION BLOCK MUST ALWAYS BE AT THE VERY BOTTOM ---
if __name__ == "__main__":
    # Only launch the massive Tkinter UI if the computer has the required SDR tools
    if run_preflight_check():
        app = Application()
        app.mainloop()