#!/usr/bin/env python3
"""
Constants for AWP (Automated Wallpaper Program)
Centralized paths and configuration constants.
Keep it simple, no fancy stuff.
"""

#!/usr/bin/env python3
import os
from pathlib import Path

# Base Paths
AWP_DIR = Path(__file__).resolve().parent.parent
CONFIG_PATH = str(AWP_DIR / "awp_config.ini")
STATE_PATH = str(AWP_DIR / "indexes.json")
ICON_DIR = str(AWP_DIR / "logos")
DEFAULT_ICON = str(AWP_DIR / "debian.png")

# RAM-Bridge Paths (Zero-Disk-Write Architecture)
RUNTIME_STATE_PATH = "/dev/shm/awp_full_state.json"
AWP_CONFIG_RAM = "/dev/shm/awp_config_ram.json"
QT6_ACCENT_SHM = "/dev/shm/awp-qt-color.conf"
KDE_ACCENT_SHM = "/dev/shm/awp-kde-color.colors"

# System Config Paths (for Symlinking)
QT6CT_COLORS_DIR = os.path.expanduser("~/.config/qt6ct/colors/")
QT6CT_CONF_PATH = os.path.expanduser("~/.config/qt6ct/qt6ct.conf")
KDE_COLORS_DIR = os.path.expanduser("~/.local/share/color-schemes")

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
        'has_wm_theme': True,
        'has_desktop_theme': False,
        'has_gtk': True,
        'has_icons': True,
        'has_cursor': True,
        'has_qt_accent': True,
        'notes': 'Window manager: XFWM'
    },
    'qtile_xfce': {
        'has_wm_theme': False,
        'has_desktop_theme': False,
        'has_gtk': True,
        'has_icons': True,
        'has_cursor': True,
        'has_qt_accent': True,
        'notes': 'Hybrid: Qtile + xfsettingsd'
    },
    'qtile_gnome': {
        'has_wm_theme': False,
        'has_desktop_theme': False,
        'has_gtk': True,
        'has_icons': True,
        'has_cursor': True,
        'has_qt_accent': True,
        'notes': 'Hybrid: Qtile + gnome-settings-daemon'
    },
    'qtile_wayland': {
        'has_wm_theme': False,        # Qtile draws its own borders
        'has_desktop_theme': False,   # No desktop shell
        'has_gtk': True,              # Via gsd-xsettings (works in Wayland)
        'has_icons': True,
        'has_cursor': True,           # Wayland handles cursors differently but still works
        'has_qt_accent': True,        # Same Qt6 accent file works
        'notes': 'Qtile Wayland + gnome-settings-daemon (no systray, no picom)'
    },
    'cinnamon': {
        'has_wm_theme': True,
        'has_desktop_theme': True,
        'has_gtk': True,
        'has_icons': True,
        'has_cursor': True,
        'has_qt_accent': True,
        'notes': 'Has separate desktop theme'
    },
    'gnome': {
        'has_wm_theme': False,
        'has_desktop_theme': False,
        'has_gtk': True,
        'has_icons': True,
        'has_cursor': True,
        'has_qt_accent': True,
        'notes': 'WM theme follows GTK'
    },
    'mate': {
        'has_wm_theme': True,
        'has_desktop_theme': False,
        'has_gtk': True,
        'has_icons': True,
        'has_cursor': True,
        'has_qt_accent': True,
        'notes': 'Window manager: Marco'
    },
    'generic': {
        'has_wm_theme': False,
        'has_desktop_theme': False,
        'has_gtk': True,
        'has_icons': True,
        'has_cursor': True,
        'has_qt_accent': True,
        'notes': 'Basic theme support via gsettings'
    }
}
