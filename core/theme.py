import os
import json
from pathlib import Path

# ── Theme Bootloader ───────────────────────────────────────────────────────────
# We read the settings file directly here to determine which theme to load.
# This happens before any UI is drawn.
_PROJECT_ROOT = Path(__file__).resolve().parents[2] # Assumes app/core/theme.py
_SETTINGS_FILE = _PROJECT_ROOT / "settings.json"

_active_mode = "Dark"
if _SETTINGS_FILE.exists():
    try:
        with open(_SETTINGS_FILE, "r") as f:
            _active_mode = json.load(f).get("theme_mode", "Dark")
    except Exception:
        pass

# ── Color Palettes ─────────────────────────────────────────────────────────────
_DARK_PALETTE = {
    "C_BG":        "#0D1B2A",     # App background
    "C_PANEL":     "#112236",     # Card / panel surface
    "C_BORDER":    "#1E3A5F",     # Dividers and borders
    "C_ACCENT":    "#00D4FF",     # Primary interactive colour
    "C_ACCENT2":   "#0099BB",     # Hover / pressed accent
    "C_TEXT":      "#D0E8F2",     # Primary text
    "C_MUTED":     "#6B8FA8",     # Hints, labels, secondary text
    "C_SUCCESS":   "#00E57A",     # Positive state
    "C_ERROR":     "#FF4D6D",     # Error / danger
    "C_WARNING":   "#FFB740",     # Warnings and caution
    "C_ENTRY_BG":  "#0A1520",     # Text input background
    "C_TAB_BG":    "#0F2035",     # Notebook tab strip
    "C_BADGE_FG":  "#0D1B2A",     # Text on accent-coloured step badges
    "C_PRESET_BG": "#162D46",     # Preset / quick-action button background
    "C_HINT":      "#4D7A96",     # Inline hint text
}

_LIGHT_PALETTE = {
    "C_BG":        "#F0F4F8",     # Light grey-blue app background
    "C_PANEL":     "#FFFFFF",     # Pure white cards / panels
    "C_BORDER":    "#D9E2EC",     # Soft grey dividers
    "C_ACCENT":    "#007AA5",     # Deeper cyan/blue for contrast on white
    "C_ACCENT2":   "#005C7A",     # Darker hover state
    "C_TEXT":      "#102A43",     # Deep navy/almost black for primary text
    "C_MUTED":     "#627D98",     # Medium grey for secondary text
    "C_SUCCESS":   "#00965E",     # Darker green for legibility
    "C_ERROR":     "#E12D39",     # Darker red
    "C_WARNING":   "#D97706",     # Darker amber
    "C_ENTRY_BG":  "#E4EBF1",     # Slightly darker than white for inputs
    "C_TAB_BG":    "#E4EBF1",     # Tab strip background
    "C_BADGE_FG":  "#FFFFFF",     # White text on accent-coloured badges
    "C_PRESET_BG": "#F0F4F8",     # Preset / quick-action button background
    "C_HINT":      "#829AB1",     # Inline hint text
}

# Select the correct dictionary based on user settings
_PALETTE = _LIGHT_PALETTE if _active_mode == "Light" else _DARK_PALETTE

# ── Exported Variables ─────────────────────────────────────────────────────────
# The rest of the app imports these directly.
C_BG        = _PALETTE["C_BG"]
C_PANEL     = _PALETTE["C_PANEL"]
C_BORDER    = _PALETTE["C_BORDER"]
C_ACCENT    = _PALETTE["C_ACCENT"]
C_ACCENT2   = _PALETTE["C_ACCENT2"]
C_TEXT      = _PALETTE["C_TEXT"]
C_MUTED     = _PALETTE["C_MUTED"]
C_SUCCESS   = _PALETTE["C_SUCCESS"]
C_ERROR     = _PALETTE["C_ERROR"]
C_WARNING   = _PALETTE["C_WARNING"]
C_ENTRY_BG  = _PALETTE["C_ENTRY_BG"]
C_TAB_BG    = _PALETTE["C_TAB_BG"]
C_BADGE_FG  = _PALETTE["C_BADGE_FG"]
C_PRESET_BG = _PALETTE["C_PRESET_BG"]
C_HINT      = _PALETTE["C_HINT"]
C_DIVIDER   = C_BORDER  # Alias

# ── Optimisation options (used by compiler tab) ────────────────────────────────
OPTIMIZATION_OPTIONS = {
    "No Optimization":       "-O0",
    "Basic Optimization":    "-O1",
    "Recommended Standard":  "-O2",
    "Aggressive Optimization": "-O3",
}

# ── Typography ─────────────────────────────────────────────────────────────────
# Windows uses Segoe UI; Linux falls back to DejaVu Sans.
_UI   = "Segoe UI"   if os.name == "nt" else "DejaVu Sans"
_MONO = "Courier New"

FONT_MONO    = (_MONO, 10)
FONT_BODY    = (_UI,   10)
FONT_LABEL   = (_UI,   10, "bold")
FONT_TITLE   = (_UI,   13, "bold")
FONT_HEADER  = (_UI,   16, "bold")
FONT_CLOCK   = (_MONO, 13, "bold")
FONT_HINT    = (_UI,    9)          # Inline hint / helper text
FONT_BADGE   = (_UI,    9, "bold")  # Step-number badges