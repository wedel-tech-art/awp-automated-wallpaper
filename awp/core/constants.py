#!/usr/bin/env python3
"""
Constants for AWP (Automated Wallpaper Program)
Centralized paths and configuration constants.
Keep it simple, no fancy stuff.
"""

import os
from pathlib import Path

# Base directory relative to this file (Project Root)
AWP_DIR = Path(__file__).resolve().parent.parent

# File Paths
CONFIG_PATH = str(AWP_DIR / "awp_config.ini")
STATE_PATH = str(AWP_DIR / "indexes.json")
ICON_DIR = str(AWP_DIR / "logos")
CONKY_STATE_PATH = str(AWP_DIR / "conky" / ".awp_conky_state.txt")

# Ensure required directories exist
# This prevents 'File Not Found' errors during the first Save
os.makedirs(ICON_DIR, exist_ok=True)
os.makedirs(str(AWP_DIR / "conky"), exist_ok=True)

# System Constants
VALID_DES = ["xfce", "gnome", "cinnamon", "mate", "generic"]

# Timing mapping for the Dashboard dropdowns
# Maps UI text to the shorthand codes used by the Daemon
TIMING_OPTIONS = {
    "1 Minute": "1m",
    "5 Minutes": "5m",
    "15 Minutes": "15m",
    "30 Minutes": "30m",
    "1 Hour": "1h",
    "Daily": "24h"
}
