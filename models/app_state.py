import tkinter as tk
from core.config import load_settings

class AppState:
    def __init__(self):
        # Shared File Paths
        self.latest_brdc_path = tk.StringVar()
        self.compiled_exe_path = tk.StringVar()
        self.latest_bin_path = tk.StringVar()
        
        # --- NEW: Live Settings Memory ---
        self.settings = load_settings()

    def get_setting(self, key: str, default=None):
        """Safely fetch a setting from live memory."""
        return self.settings.get(key, default)

    def update_settings(self, new_settings: dict):
        """Updates live memory immediately when the user clicks 'Save'."""
        self.settings.update(new_settings)