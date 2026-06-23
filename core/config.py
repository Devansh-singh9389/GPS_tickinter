import os
import json
from pathlib import Path

# --- Directory Configuration ---
PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR_BRDCS = PROJECT_ROOT / "data" / "BRDCs"
DATA_DIR_COMPILED = PROJECT_ROOT / "data" / "Compiled"
DATA_DIR_BINARY = PROJECT_ROOT / "data" / "BIN"
ASSETS_DIR = PROJECT_ROOT / "assets" #this is for future use. currently it is empty

SETTINGS_FILE = PROJECT_ROOT / "settings.json"

for directory in [DATA_DIR_BRDCS, DATA_DIR_COMPILED, DATA_DIR_BINARY, ASSETS_DIR]:
    directory.mkdir(parents=True, exist_ok=True)

# --- SYSTEM DEFAULTS ---
DEFAULT_SETTINGS = {
    "nasa_username": "",
    "nasa_password": "",
    "auto_save_metadata": True,
    "smart_auto_naming": True,
    "hardware_poll_rate_ms": 3000,
    "verbose_logging": False,
    "theme_mode": "Dark",
    "hackrf_freq_offset": "-10",

    # --- NEW: MEMORY FOR FILE PATHS ---
    "last_compiler_src": str(Path.home() / "Code" / "TRY 1" / "gps-sdr-sim"),
    "last_brdc_file": "",
    "last_bin_file": "",

    #Compilation
    "default_optimization": "Aggressive Optimization",
    "user_motion_size": 3000,
    #----official Compilare feature----
    "large_file": True,
    "multithread": True,
    "Native Cpu Arch": True,
    "Extreme speed Math":False,
    #---Advance header----
    "Enable High-Precision" : False,
    "max_satterlite" : 32,
    "max_channels" : 16

}


def load_settings() -> dict:
    current = DEFAULT_SETTINGS.copy()
    if SETTINGS_FILE.exists():
        try:
            with open(SETTINGS_FILE, "r") as f:
                disk_data = json.load(f)
                if isinstance(disk_data, dict):
                    current.update(disk_data)
        except Exception:
            pass
    return current


def save_settings(updates: dict) -> None:
    # BULLETPROOF SAVE: Always load defaults first, then disk, then updates.
    # This guarantees no keys are ever lost, even if the file gets corrupted.
    current = load_settings()
    current.update(updates)

    try:
        with open(SETTINGS_FILE, "w") as f:
            json.dump(current, f, indent=4)
    except Exception as e:
        print(f"CRITICAL ERROR: Could not save settings: {e}")


def reset_settings() -> dict:
    """Restores the system to factory defaults."""
    try:
        with open(SETTINGS_FILE, "w") as f:
            json.dump(DEFAULT_SETTINGS, f, indent=4)
    except Exception:
        pass
    return DEFAULT_SETTINGS.copy()