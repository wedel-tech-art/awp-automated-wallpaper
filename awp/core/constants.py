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
# ICON TEMPLATE PRESETS
# ============================================================================
# Maps preset names to their template folder
# Used by bake_awp_icon() and dashboard preset selection

# The master list of assets to be re-hued during the bake process
TARGET_ASSETS = [
    "arrow-down-active.png", "arrow-down-hover.png",
    "arrow-left-active.png", "arrow-left-hover.png",
    "arrow-right-active.png", "arrow-right-hover.png",
    "arrow-small-down-active.png", "arrow-small-down-hover.png",
    "arrow-small-left-active.png", "arrow-small-left-hover.png",
    "arrow-small-right-active.png", "arrow-small-right-hover.png",
    "arrow-small-up-active.png", "arrow-small-up-hover.png",
    "arrow-up-active.png", "arrow-up-hover.png",
    "button-active.png", "button-hover.png",
    "check-checked-active@2.png", "check-checked-active.png",
    "check-checked-hover@2.png", "check-checked-hover.png",
    "check-mixed-active@2.png", "check-mixed-active.png",
    "check-mixed-hover@2.png", "check-mixed-hover.png",
    "check-selectionmode-checked-active@2.png", "check-selectionmode-checked-active.png",
    "check-selectionmode-checked-hover@2.png", "check-selectionmode-checked-hover.png",
    "check-selectionmode-unchecked-active@2.png", "check-selectionmode-unchecked-active.png",
    "check-selectionmode-unchecked-hover@2.png", "check-selectionmode-unchecked-hover.png",
    "check-unchecked-active@2.png", "check-unchecked-active.png",
    "check-unchecked-hover@2.png", "check-unchecked-hover.png",
    "combo-entry-active.png", "combo-entry-button-active.png",
    "entry-active.png", "menubar-button.png", "progressbar-bar.png",
    "radio-checked-active@2.png", "radio-checked-active.png",
    "radio-checked-hover@2.png", "radio-checked-hover.png",
    "radio-mixed-active@2.png", "radio-mixed-active.png",
    "radio-mixed-hover@2.png", "radio-mixed-hover.png",
    "radio-unchecked-active@2.png", "radio-unchecked-active.png",
    "radio-unchecked-hover@2.png", "radio-unchecked-hover.png",
    "scale-slider-active.png", "scale-slider-hover.png",
    "scrollbar-slider-horizontal-active@2.png", "scrollbar-slider-horizontal-active.png",
    "scrollbar-slider-horizontal-hover@2.png", "scrollbar-slider-horizontal-hover.png",
    "scrollbar-slider-vertical-active@2.png", "scrollbar-slider-vertical-active.png",
    "scrollbar-slider-vertical-hover@2.png", "scrollbar-slider-vertical-hover.png",
    "togglebutton-active.png", "togglebutton-hover.png",
    "toolbutton-active.png", "toolbutton-hover.png"
]

ICON_PRESETS = {
    'mint': 'template-icon-presets/mint',
    'yaru': 'template-icon-presets/yaru',
    'souza': 'template-icon-presets/souza',
    'jojo': 'template-icon-presets/jojo',
    'paomedia': 'template-icon-presets/paomedia'
}

THEME_PRESETS = {
    'breeze': {
        'path':    'template-theme-presets/breeze',
        'rebrand': ['Breeze-Dark', 'Breeze'],
        'colors':  [
            ('3daee9', 'hex'),
            ('61, 174, 233', 'rgb'),
            ('37, 164, 230', 'rgb'),
        ],
        'family_ratios': None,
        'assets':  TARGET_ASSETS,
    },
    'colloid': {
        'path':    'template-theme-presets/colloid',
        'rebrand': ['Colloid-Orange-Dark-Gruvbox'],
        'colors':  [
            ('fe8019', 'hex'),
            ('253, 128, 25', 'rgb'),
            ('fe9137', 'shade'),
            ('253, 145, 55', 'shade_rgb'),
            ('fda24d', 'lighter'),
            ('253, 162, 77', 'lighter_rgb'),
        ],
        'family_ratios': {
            'shade':   (0.869, 1.000),
            'lighter': (0.772, 0.996),
        },
        'assets': [],
    },
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
