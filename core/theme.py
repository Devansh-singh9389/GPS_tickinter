import os

C_BG        = "#0D1B2A"
C_PANEL     = "#112236"
C_BORDER    = "#1E3A5F"
C_ACCENT    = "#00D4FF"
C_ACCENT2   = "#0099BB"
C_TEXT      = "#D0E8F2"
C_MUTED     = "#6B8FA8"
C_SUCCESS   = "#00E57A"
C_ERROR     = "#FF4D6D"
C_WARNING   = "#FFB740"
C_ENTRY_BG  = "#0A1520"
C_TAB_BG    = "#0F2035"

OPTIMIZATION_OPTIONS = {
    "No Optimization": "-O0",
    "Basic Optimization": "-O1",
    "Recommended Standard": "-O2",
    "Aggressive Optimization": "-O3",
}

FONT_MONO   = ("Courier New", 10)
FONT_BODY   = ("Segoe UI", 10) if os.name == "nt" else ("DejaVu Sans", 10)
FONT_LABEL  = ("Segoe UI", 10, "bold") if os.name == "nt" else ("DejaVu Sans", 10, "bold")
FONT_TITLE  = ("Segoe UI", 13, "bold") if os.name == "nt" else ("DejaVu Sans", 13, "bold")
FONT_HEADER = ("Segoe UI", 16, "bold") if os.name == "nt" else ("DejaVu Sans", 16, "bold")
FONT_CLOCK  = ("Courier New", 13, "bold")