import tkinter as tk
from core.config import load_settings, save_settings, DATA_DIR_BRDCS, DATA_DIR_BINARY , DATA_DIR_COMPILED


class AppState:
    def __init__(self):
        self.settings = load_settings()

        saved_BRDCS = self.settings.get("latest BRDCs file" , "")
        saved_exe = self.settings.get("latest_compiled_file" , "")
        saved_bin = self.settings.get("latest binary file" , "")

        actual_brdc = self._verify_or_fallback(saved_BRDCS,DATA_DIR_BRDCS,"*.*n*")
        actual_compiled = self._verify_or_fallback(saved_exe, DATA_DIR_COMPILED, "*")
        actual_bin = self._verify_or_fallback(saved_bin,DATA_DIR_BINARY,"*.bin")

        # Shared File Paths (Initialize them with saved settings)
        self.latest_brdc_path = tk.StringVar(value=actual_brdc)
        self.compiled_exe_path = tk.StringVar(value=actual_compiled)
        self.latest_bin_path = tk.StringVar(value=actual_bin)

    def _verify_or_fallback(self, saved_path_str, directory: Path, search_pattern: str) -> str:
        """Checks if a saved file exists. If deleted, auto-selects the newest valid file."""
        # 1. If we have a saved path and it physically exists, use it!
        if saved_path_str and Path(saved_path_str).exists():
            return saved_path_str

        # 2. If it was manually deleted (or missing), scan the folder for the newest file
        if directory.exists():
            files = list(directory.glob(search_pattern))
            if files:
                # Sort the files by creation/modification time, and grab the newest one
                newest_file = max(files, key=lambda f: f.stat().st_mtime)
                return str(newest_file)

        # 3. If the folder is completely empty, safely return blank
        return ""

    def get_setting(self, key: str, default=None):
        return self.settings.get(key, default)

    def update_settings(self, new_settings: dict):
        self.settings.update(new_settings)

    def save_path(self, key: str, path: str):
        """Immediately saves a path to memory and disk."""
        self.settings[key] = path
        save_settings({key: path})