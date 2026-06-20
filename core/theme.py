import os

# ── Core Palette ───────────────────────────────────────────────────────────────
C_BG        = "#0D1B2A"     # App background
C_PANEL     = "#112236"     # Card / panel surface
C_BORDER    = "#1E3A5F"     # Dividers and borders
C_ACCENT    = "#00D4FF"     # Primary interactive colour
C_ACCENT2   = "#0099BB"     # Hover / pressed accent
C_TEXT      = "#D0E8F2"     # Primary text
C_MUTED     = "#6B8FA8"     # Hints, labels, secondary text
C_SUCCESS   = "#00E57A"     # Positive state
C_ERROR     = "#FF4D6D"     # Error / danger
C_WARNING   = "#FFB740"     # Warnings and caution
C_ENTRY_BG  = "#0A1520"     # Text input background
C_TAB_BG    = "#0F2035"     # Notebook tab strip

# ── Semantic extras ────────────────────────────────────────────────────────────
C_BADGE_FG  = "#0D1B2A"     # Text on accent-coloured step badges
C_PRESET_BG = "#162D46"     # Preset / quick-action button background
C_HINT      = "#4D7A96"     # Inline hint text (dimmer than C_MUTED)
C_DIVIDER   = C_BORDER      # Alias — use this for horizontal rules

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