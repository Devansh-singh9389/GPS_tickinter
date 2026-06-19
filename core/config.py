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

# --- Local Memory / Cache Functions ---
def load_settings() -> dict:
    """Load settings from the local JSON file. Return defaults if missing."""
    if SETTINGS_FILE.exists():
        try:
            with open(SETTINGS_FILE, "r") as f:
                return json.load(f)
        except json.JSONDecodeError:
            pass # Fallback to defaults if file is corrupted
            
    # Default fallback values
    return {
        "nasa_username": "Devanshearthdata",
        "nasa_password": "Devanshsingh@9389"
    }

def save_settings(username: str, password: str):
    """Save the credentials back to the local JSON file."""
    settings = load_settings()
    settings["nasa_username"] = username
    settings["nasa_password"] = password
    
    with open(SETTINGS_FILE, "w") as f:
        json.dump(settings, f, indent=4)