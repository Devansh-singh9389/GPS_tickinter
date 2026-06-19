import tkinter as tk
from pathlib import Path
from core.config import *

class AppState:
    """Shared application state accessible by all tabs."""
    def __init__(self):
        # We use tk.StringVar so the UI can reactively update when these change
        self.latest_brdc_path = tk.StringVar(value=self._find_latest_brdc_file())
        self.compiled_exe_path = tk.StringVar(value="")
        self.latest_bin_path = tk.StringVar(value="")

    @staticmethod
    def _find_latest_brdc_file() -> str:
        
        candidates = sorted(
            DATA_DIR_BRDCS.glob("brdc*.*n"),
            key=lambda p: p.stat().st_mtime if p.exists() else 0,
            reverse=True,
        )
        return str(candidates[0]) if candidates else ""