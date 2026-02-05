#!/usr/bin/env python3
"""
Constants for AWP (Automated Wallpaper Program)
Centralized paths and configuration constants.
Keep it simple, no fancy stuff.
"""

import os
from pathlib import Path

AWP_DIR = Path(__file__).resolve().parent.parent

CONFIG_PATH = str(AWP_DIR / "awp_config.ini")
STATE_PATH = str(AWP_DIR / "indexes.json")
ICON_DIR = str(AWP_DIR / "logos")
CONKY_STATE_PATH = str(AWP_DIR / "conky" / ".awp_conky_state.txt")
