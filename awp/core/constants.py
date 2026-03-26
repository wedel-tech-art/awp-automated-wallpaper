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
RUNTIME_STATE_PATH = "/dev/shm/awp_full_state.json"
AWP_CONFIG_RAM = "/dev/shm/awp_config_ram.json"
DEFAULT_ICON = str(AWP_DIR / "debian.png")

# ============================================================================
# ANSI COLOR CODES - for consistent terminal output
# ============================================================================
CLR_RED     = "\033[91m"
CLR_GREEN   = "\033[92m"
CLR_YELLOW  = "\033[93m"
CLR_BLUE    = "\033[94m"
CLR_MAGENTA = "\033[95m"
CLR_CYAN    = "\033[96m"
CLR_WHITE   = "\033[97m"
CLR_RESET   = "\033[0m"
CLR_BOLD    = "\033[1m"

# ============================================================================
# SHARED MAPPINGS
# ============================================================================
SCALING_FEH = {
    'centered': '--bg-center',
    'scaled': '--bg-scale',
    'zoomed': '--bg-fill'
}

# ============================================================================
# THEME CAPABILITY MATRIX - for UI enabling/disabling
# ============================================================================
# Defines what theme controls are available for each desktop environment
THEME_CAPABILITIES = {
    'xfce': {
        'has_wm_theme': True,      # XFWM themes
        'has_desktop_theme': False, # No separate desktop theme
        'has_gtk': True,
        'has_icons': True,
        'has_cursor': True,
        'notes': 'Window manager: XFWM'
    },
    'qtile_xfce': {
        'has_wm_theme': False,      # Qtile is WM, no separate theme
        'has_desktop_theme': False,
        'has_gtk': True,             # Uses xfsettingsd for GTK
        'has_icons': True,
        'has_cursor': True,
        'notes': 'Hybrid: Qtile + xfsettingsd'
    },
    'cinnamon': {
        'has_wm_theme': True,        # Muffin/Marco themes
        'has_desktop_theme': True,   # Cinnamon shell theme!
        'has_gtk': True,
        'has_icons': True,
        'has_cursor': True,
        'notes': 'Has separate desktop theme'
    },
    'gnome': {
        'has_wm_theme': False,       # Mutter integrated with GTK
        'has_desktop_theme': False,  # GNOME Shell theme (complex)
        'has_gtk': True,
        'has_icons': True,
        'has_cursor': True,
        'notes': 'WM theme follows GTK'
    },
    'mate': {
        'has_wm_theme': True,        # Marco themes
        'has_desktop_theme': False,
        'has_gtk': True,
        'has_icons': True,
        'has_cursor': True,
        'notes': 'Window manager: Marco'
    },
    'generic': {
        'has_wm_theme': False,       # Depends on WM
        'has_desktop_theme': False,
        'has_gtk': True,             # Maybe, if gsettings works
        'has_icons': True,
        'has_cursor': True,
        'notes': 'Basic theme support via gsettings'
    }
}
