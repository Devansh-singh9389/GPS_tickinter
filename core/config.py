import os
import json
from pathlib import Path

# --- Directory Configuration ---
PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR_BRDCS  = PROJECT_ROOT / "data" / "BRDCs"
DATA_DIR_COMPILED = PROJECT_ROOT / "data" / "Compiled"
DATA_DIR_BINARY = PROJECT_ROOT / "data" / "BIN"
ASSETS_DIR = PROJECT_ROOT / "assets"

# File to store user preferences locally
SETTINGS_FILE = PROJECT_ROOT / "settings.json"

# Ensure directories exist
for directory in [DATA_DIR_BRDCS , DATA_DIR_COMPILED, DATA_DIR_BINARY, ASSETS_DIR]:
    directory.mkdir(parents=True, exist_ok=True)


#------Default Settings------
Default_Settings = {

    #general settings
    "nasa_username": "Devanshearthdata",
    "nasa_password": "Devanshsingh@9389",
    "auto_save_metadata": True,
    "smart_auto_naming": True,

    #professional settings
    "default_optimization_level": "Recommended Standard",
    "hardware_poll_rate_ms": 3000,
    "verbose_logging": False,

    #apperance settings
    "theme_mode" : "Dark"
}

# --- Local Memory / Cache Functions ---
def load_settings() -> dict:
    if not SETTINGS_FILE.exists() : 
        return Default_Settings
    
    try:
        with open(SETTINGS_FILE, "r") as f:
            user_settings = json.load(f)
        
        merged_settings = Default_Settings.copy()
        merged_settings.update(user_settings)
        return merged_settings
    except Exception as e:
        return Default_Settings.copy()
    
def save_settings(settings: dict):
    try:
        with open(SETTINGS_FILE, "w") as f:
            json.dump(settings, f, indent=4)
    except Exception as e:
        print(f"CRITICAL ERROR: Could not save settings: {e}")