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
# ICON AND GTK THEME TEMPLATE PRESETS AND DICTIONARIES
# ============================================================================
ICON_SIZES = ["16", "22", "24", "32", "48", "64", "96"]


# ============================================================================
# SELECTION BRIGHTNESS - Central control for all themes
# ============================================================================
# 0.70 = 70% brightness (safe, works with ALL colors including extreme yellow)
# 0.75 = 75% brightness (balanced, works with most colors)
# 0.80 = 80% brightness (vibrant, works with dark/medium colors only)
SELECTION_BRIGHTNESS = 0.75  # Default: 70% - maximum readability


ICON_REGISTRY = {
    # --- PLACES ---
    "folder": {
        "context": "places",
        "symlinks": [
            "athena", "file-manager", "gtk-directory", "inode-directory",
            "kfm", "nautilus-actions-config-tool", "nautilus", "nemo",
            "org.xfce.filemanager", "org.xfce.panel.directorymenu",
            "org.xfce.thunar", "redhat-filemanager", "stock_folder",
            "system-file-manager", "thunar", "Thunar", "xfce-filemanager"
        ]
    },
    "folder-documents": {
        "context": "places",
        "symlinks": []
    },
    "folder-download": {
        "context": "places",
        "symlinks": []
    },
    "folder-drag-accept": {
        "context": "places",
        "symlinks": ["folder-open"]
    },
    "folder-music": {
        "context": "places",
        "symlinks": ["library-music"]
    },
    "folder-pictures": {
        "context": "places",
        "symlinks": []
    },
    "folder-publicshare": {
        "context": "places",
        "symlinks": []
    },
    "folder-recent": {
        "context": "places",
        "symlinks": []
    },
    "folder-saved-search": {
        "context": "places",
        "symlinks": []
    },
    "folder-templates": {
        "context": "places",
        "symlinks": []
    },
    "folder-videos": {
        "context": "places",
        "symlinks": []
    },
    "gtk-network": {
        "context": "places",
        "symlinks": ["folder-remote", "org.xfce.gigolo"]
    },
    "network-workgroup": {
        "context": "places",
        "symlinks": ["network-server"]
    },
    "user-bookmarks": {
        "context": "places",
        "symlinks": ["xapp-user-favorites"]
    },
    "user-desktop": {
        "context": "places",
        "symlinks": ["desktop", "gnome-fs-desktop", "org.xfce.panel.showdesktop", "org.xfce.xfdesktop"]
    },
    "user-home": {
        "context": "places",
        "symlinks": ["folder_home", "gnome-fs-home"]
    },
    
    # --- TRASH ---
    "user-trash": {
        "context": "places",
        "png_action": {"original": ["sweet-hollow", "sweet"]},
        "svg_action": {"svg_original": ["sweet-hollow", "sweet"]},
        "symlinks": []
    },
    "user-trash-full": {
        "context": "places",
        "png_action": {"original": ["sweet-hollow", "sweet"]},
        "svg_action": {"svg_original": ["sweet-hollow", "sweet"]},
        "symlinks": []
    },

    # --- DEVICES ---
    "computer": {
        "context": "devices",
        "symlinks": []
    },
    "drive-harddisk": {
        "context": "devices",
        "symlinks": []
    },

    # --- LEGACY ---
    "go-home": {
        "context": "legacy",
        "symlinks": []
    },
    "emblem-symbolic-link": {
        "context": "legacy",
        "png_action": {"original": ["besgnulinux", "slot-multicolor", "sweet"]},
        "svg_action": {"svg_original": ["besgnulinux", "slot-multicolor", "sweet"]},
        "symlinks": []
    },

    # --- MIMETYPES ---
    "text-x-python": {
        "context": "mimetypes",
        "png_action": {"original": ["adwaitaru", "rami"]},
        "svg_action": {"svg_original": ["adwaitaru", "rami"]},
        "symlinks": [
            "application-x-python", "application-x-python-bytecode",
            "text-x-python3", "text-x-script.python",
            "application-x-executable-python"
        ]
    },
    "text-x-script": {
        "context": "mimetypes",
        "png_action": {"original": ["adwaitaru", "rami"]},
        "svg_action": {"svg_original": ["adwaitaru", "rami"]},        
        "symlinks": [
            "application-x-shellscript", "application-x-sh",
            "text-x-sh", "shellscript"
        ]
    },
    "text-x-generic": {
        "context": "mimetypes",
        "symlinks": ["text-plain", "text-log", "txt", "text-x-preview"]
    },
    "package-x-generic": {
        "context": "mimetypes",
        "symlinks": [
            "package",
            "application-x-gzip", "application-gzip", "gz",
            "application-x-tar", "tar", "application-x-bzip", "application-x-compressed-tar",
            "application-zip", "zip", "application-x-zip-compressed",
            "application-x-7z-compressed", "7z", "application-x-7z",
            "application-x-rar", "rar", "application-rar"
        ]
    },
    "application-json": {
        "context": "mimetypes",
        "symlinks": ["json", "text-x-json"]
    },
    "text-markdown": {
        "context": "mimetypes",
        "png_action": {"original": ["mint", "slot-multicolor", "sweet", "breeze", "adwaitaru", "rami"]},
        "svg_action": {"svg_original": ["mint", "slot-multicolor", "sweet", "breeze", "adwaitaru", "rami"]},
        "symlinks": ["text-x-markdown", "markdown", "text-x-readme", "readme"]
    },
    
    # --- AUDIO ---
    "audio-mpeg": {
        "context": "mimetypes",
        "png_action": {"original": ["besgnulinux", "sweet-hollow", "slot-multicolor", "sweet", "breeze", "adwaitaru", "rami"]},
        "svg_action": {"svg_original": ["besgnulinux", "sweet-hollow", "slot-multicolor", "sweet", "breeze", "adwaitaru", "rami"]},
        "symlinks": ["audio-mp3", "mpeg"]
    },
    "audio-flac": {
        "context": "mimetypes",
        "png_action": {"original": ["besgnulinux", "sweet-hollow", "slot-multicolor", "sweet", "breeze", "adwaitaru", "rami"]},
        "svg_action": {"svg_original": ["besgnulinux", "sweet-hollow", "slot-multicolor", "sweet", "breeze", "adwaitaru", "rami"]},
        "symlinks": ["flac", "audio-x-flac"]
    },
    "audio-x-wav": {
        "context": "mimetypes",
        "png_action": {"original": ["besgnulinux", "sweet-hollow", "slot-multicolor", "sweet", "breeze", "adwaitaru", "rami"]},
        "svg_action": {"svg_original": ["besgnulinux", "sweet-hollow", "slot-multicolor", "sweet", "breeze", "adwaitaru", "rami"]},
        "symlinks": ["audio-wav", "audio-vnd.wave", "x-wav", "wav"]
    },
    "audio-midi": {
        "context": "mimetypes",
        "png_action": {"original": ["besgnulinux", "sweet-hollow", "slot-multicolor", "sweet", "breeze", "adwaitaru", "rami"]},
        "svg_action": {"svg_original": ["besgnulinux", "sweet-hollow", "slot-multicolor", "sweet", "breeze", "adwaitaru", "rami"]},
        "symlinks": [
            "audio-mid", "audio-x-midi", "audio-sp-midi",
            "audio-smf", "midi", "mid"
        ]
    },
    # --- (DEBIAN SPECIFIC) ---
    "application-vnd.debian.binary-package": {
        "context": "mimetypes",
        "png_action": {"original": ["mint", "slot-multicolor", "adwaitaru", "rami", "breeze", "sweet"]},
        "svg_action": {"svg_original": ["mint", "slot-multicolor", "adwaitaru", "rami", "breeze", "sweet"]},
        "symlinks": [
            "gnome-mime-application-x-deb", "application-x-deb"
        ]
    },

    # --- (WORD / WRITER) ---
    "x-office-document": {
        "context": "mimetypes",
        "png_action": {"original": ["besgnulinux", "mint", "sweet-hollow", "slot-multicolor", "adwaitaru", "rami", "breeze", "sweet"]},
        "svg_action": {"svg_original": ["besgnulinux", "mint", "sweet-hollow", "slot-multicolor", "adwaitaru", "rami", "breeze", "sweet"]},
        "symlinks": [
            "application-msword", "application-vnd.openxmlformats-officedocument.wordprocessingml.document",
            "application-vnd.oasis.opendocument.text", "application-vnd.oasis.opendocument.text-rtl",
            "application-vnd.sun.xml.writer", "application-vnd.sun.xml.writer-rtl",
            "application-vnd.wordperfect", "application-vnd.wordperfect-rtl",
            "ms-word", "abiword", "document", "document-rtl", "wordprocessing", "wordprocessing-rtl"
        ]
    },

    # --- (EXCEL / CALC) ---
    "x-office-spreadsheet": {
        "context": "mimetypes",
        "png_action": {"original": ["besgnulinux", "mint", "sweet-hollow", "slot-multicolor", "adwaitaru", "rami", "breeze", "sweet"]},
        "svg_action": {"svg_original": ["besgnulinux", "mint", "sweet-hollow", "slot-multicolor", "adwaitaru", "rami", "breeze", "sweet"]},
        "symlinks": [
            "application-vnd.ms-excel", "application-vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            "application-vnd.oasis.opendocument.spreadsheet", "application-vnd.sun.xml.calc",
            "ms-excel", "text-spreadsheet", "office-spreadsheet"
        ]
    },

    # --- (POWERPOINT / IMPRESS) ---
    "x-office-presentation": {
        "context": "mimetypes",
        "png_action": {"original": ["besgnulinux", "mint", "sweet-hollow", "slot-multicolor", "adwaitaru", "rami", "breeze", "sweet"]},
        "svg_action": {"svg_original": ["besgnulinux", "mint", "sweet-hollow", "slot-multicolor", "adwaitaru", "rami", "breeze", "sweet"]},
        "symlinks": [
            "application-vnd.ms-powerpoint", "application-vnd.openxmlformats-officedocument.presentationml.presentation",
            "application-vnd.openxmlformats-officedocument.presentationml.slideshow", "application-vnd.ms-powerpoint.presentation.macroEnabled.12",
            "application-vnd.oasis.opendocument.presentation", "ms-powerpoint", "ooo-impress"
        ]
    },
}


# The master list of assets to be re-hued during the bake GTK THEME process
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

# ==============================================================================
# TARGET ASSETS FOR FLAT REMIX THEME
# ==============================================================================
FLAT_REMIX_ASSETS = [
    # --- GTK 2.0 (Legacy Interface Controls) ---
    'checkbox-checked.png',
    'checkbox-checked-hover.png',
    'checkbox-mixed.png',
    'checkbox-mixed-hover.png',
    'combo-entry-ltr-entry-active.png',
    'combo-entry-rtl-entry-active.png',
    'entry-active.png',
    'menubar-item-active.png',
    'notebook-combo-entry-ltr-entry-active.png',
    'notebook-combo-entry-rtl-entry-active.png',
    'notebook-entry-active.png',
    'progressbar-horz.png',
    'progressbar-vert.png',
    'radio-checked.png',
    'radio-checked-hover.png',
    'radio-mixed.png',
    'radio-mixed-hover.png',
    'scale-horz-trough-active.png',
    'scale-slider-active.png',
    'scale-slider-hover.png',
    'scale-vert-trough-active.png',
    'scrollbar-horz-slider-active.png',
    'scrollbar-vert-slider-active.png',
    'scrollbar-vert-slider-active-rtl.png',

    # --- GTK 3.0 (Scale Sliders with Marks & Text Selection Anchors) ---
    'slider-horz-scale-has-marks-above-active.png',
    'slider-horz-scale-has-marks-above-active@2.png',
    'slider-horz-scale-has-marks-above-active-dark.png',
    'slider-horz-scale-has-marks-above-active-dark@2.png',
    'slider-horz-scale-has-marks-above-active-darkest.png',
    'slider-horz-scale-has-marks-above-active-darkest@2.png',
    'slider-horz-scale-has-marks-above-hover.png',
    'slider-horz-scale-has-marks-above-hover@2.png',
    'slider-horz-scale-has-marks-above-hover-dark.png',
    'slider-horz-scale-has-marks-above-hover-dark@2.png',
    'slider-horz-scale-has-marks-above-hover-darkest.png',
    'slider-horz-scale-has-marks-above-hover-darkest@2.png',
    
    'slider-horz-scale-has-marks-below-active.png',
    'slider-horz-scale-has-marks-below-active@2.png',
    'slider-horz-scale-has-marks-below-active-dark.png',
    'slider-horz-scale-has-marks-below-active-dark@2.png',
    'slider-horz-scale-has-marks-below-active-darkest.png',
    'slider-horz-scale-has-marks-below-active-darkest@2.png',
    'slider-horz-scale-has-marks-below-hover.png',
    'slider-horz-scale-has-marks-below-hover@2.png',
    'slider-horz-scale-has-marks-below-hover-dark.png',
    'slider-horz-scale-has-marks-below-hover-dark@2.png',
    'slider-horz-scale-has-marks-below-hover-darkest.png',
    'slider-horz-scale-has-marks-below-hover-darkest@2.png',
    
    'slider-vert-scale-has-marks-above-active.png',
    'slider-vert-scale-has-marks-above-active@2.png',
    'slider-vert-scale-has-marks-above-active-dark.png',
    'slider-vert-scale-has-marks-above-active-dark@2.png',
    'slider-vert-scale-has-marks-above-active-darkest.png',
    'slider-vert-scale-has-marks-above-active-darkest@2.png',
    'slider-vert-scale-has-marks-above-hover.png',
    'slider-vert-scale-has-marks-above-hover@2.png',
    'slider-vert-scale-has-marks-above-hover-dark.png',
    'slider-vert-scale-has-marks-above-hover-dark@2.png',
    'slider-vert-scale-has-marks-above-hover-darkest.png',
    'slider-vert-scale-has-marks-above-hover-darkest@2.png',
    
    'slider-vert-scale-has-marks-below-active.png',
    'slider-vert-scale-has-marks-below-active@2.png',
    'slider-vert-scale-has-marks-below-active-dark.png',
    'slider-vert-scale-has-marks-below-active-dark@2.png',
    'slider-vert-scale-has-marks-below-active-darkest.png',
    'slider-vert-scale-has-marks-below-active-darkest@2.png',
    'slider-vert-scale-has-marks-below-hover.png',
    'slider-vert-scale-has-marks-below-hover@2.png',
    'slider-vert-scale-has-marks-below-hover-dark.png',
    'slider-vert-scale-has-marks-below-hover-dark@2.png',
    'slider-vert-scale-has-marks-below-hover-darkest.png',
    'slider-vert-scale-has-marks-below-hover-darkest@2.png',
    
    'text-select-end-active.png',
    'text-select-end-active@2.png',
    'text-select-end-active-dark.png',
    'text-select-end-active-dark@2.png',
    'text-select-end-active-darkest.png',
    'text-select-end-active-darkest@2.png',
    'text-select-end-hover.png',
    'text-select-end-hover@2.png',
    'text-select-end-hover-dark.png',
    'text-select-end-hover-dark@2.png',
    'text-select-end-hover-darkest.png',
    'text-select-end-hover-darkest@2.png',
    
    'text-select-start-active.png',
    'text-select-start-active@2.png',
    'text-select-start-active-dark.png',
    'text-select-start-active-dark@2.png',
    'text-select-start-active-darkest.png',
    'text-select-start-active-darkest@2.png',
    'text-select-start-hover.png',
    'text-select-start-hover@2.png',
    'text-select-start-hover-dark.png',
    'text-select-start-hover-dark@2.png',
    'text-select-start-hover-darkest.png',
    'text-select-start-hover-darkest@2.png'
]

GTK2_ASSETS = [
    "checkbox-checked.png", "checkbox-checked-active.png", "checkbox-checked-disabled.png",
    "checkbox-checked-hover.png", "checkbox-mixed.png", "checkbox-mixed-active.png", "checkbox-mixed-disabled.png",
    "checkbox-mixed-hover.png", "combo-left-entry-active.png", "combo-right-entry-active.png",
    "entry-active.png", "menu-checkbox-checked.png", "menu-checkbox-checked-disabled.png",
    "menu-checkbox-mixed.png", "menu-checkbox-mixed-disabled.png", "menu-radio-checked.png", "menu-radio-checked-disabled.png",
    "menu-radio-mixed.png", "menu-radio-mixed-disabled.png", "progressbar-progress.png",
    "radio-checked.png", "radio-checked-active.png", "radio-checked-disabled.png",
    "radio-checked-hover.png", "radio-mixed.png", "radio-mixed-active.png",
    "radio-mixed-disabled.png", "radio-mixed-hover.png", "scale-horz-trough-active.png",
    "scale-slider.png", "scale-slider-active.png", "scale-slider-hover.png",
    "scale-vert-trough-active.png", "spin-ltr-down-active.png", "spin-ltr-up-active.png",
    "spin-rtl-down-active.png", "spin-rtl-up-active.png", "tab.png", "treeview-ltr-button-active.png", "treeview-rtl-button-active.png"
]


ICON_PRESETS = {
    'mint': {
        'path': 'template-icon-presets/mint',
        'colors': [
            ('a27ae4', 'hex'),
            ('7240c3', 'mid_dark'),
            ('7155a0', 'dark_shade'),
            ('4a2e85', 'darkest'),
            ('2c1e44', 'deepest'),
            ('cbb1f0', 'lighter'),
            
            ('6c763f', 'trash_dark_base'),
            ('adbc6a', 'trash_light_leaf'),
            ('86a10c', 'trash_mid_dark'),
            ('98b710', 'trash_mid_bright'),
            ('9aab4d', 'trash_muted_mid'),
            ('839341', 'trash_olive_shade'),
            ('b2d226', 'trash_bright_pop'),
        ],
        'family_ratios': {
            # Stability-First: Minimal hue shifts, rich saturation/value depth
            # Pure: (0.0, 1.01, 0.85)  → 266°, 67%, 76%
            'mid_dark':   (0.0, 1.15, 0.78),   # Pure hue, rich & darker
            
            # Pure: (-5.0, 0.71, 0.71)  → 261°, 47%, 63%
            'dark_shade': (-1.0, 0.85, 0.62),  # Minimal cool, richer
            
            # Pure: (-6.0, 0.98, 0.58)  → 260°, 65%, 52%
            'darkest':    (1.0, 1.10, 0.45),   # Minimal warm, very rich
            
            # Pure: (-4.0, 0.85, 0.30)  → 262°, 56%, 27%
            'deepest':    (-1.0, 0.95, 0.20),  # Minimal cool, deepest
            
            # Pure: (0.0, 0.39, 1.06)  → 266°, 26%, 94%
            'lighter':    (0.0, 0.30, 1.12),   # Pure hue, bright & pure
            
            'trash_dark_base':   (0, 0.47, 0.46),
            'trash_light_leaf':  (0, 0.44, 0.74),
            'trash_mid_dark':    (0, 0.93, 0.63),
            'trash_mid_bright':  (0, 0.91, 0.72),
            'trash_muted_mid':   (0, 0.55, 0.67),
            'trash_olive_shade': (0, 0.56, 0.58),
            'trash_bright_pop':  (0, 0.82, 0.82),
        },
    },
    'rami': {
        'path': 'template-icon-presets/rami',
        'colors': [
            ('a27ae4', 'hex'),
            ('7155a0', 'dark_shade'),
            ('dbcbfa', 'lightest'),
            ('cbb1f0', 'lighter'),
            ('b897e6', 'led_glow'),      # LED glow color
            ('585858', 'body_dark'),
            ('7e7e7e', 'body_light'),
        ],
        'family_ratios': {
            # Pure: (-5.0, 0.71, 0.71)  → 261°, 47%, 63%
            'dark_shade': (-1.0, 0.90, 0.58),  # Minimal cool, richer shadow
            
            # Pure: (0.0, 0.29, 1.10)  → 266°, 19%, 98%
            'lightest':   (0.0, 0.20, 1.18),   # Pure hue, very bright
            
            # Pure: (0.0, 0.39, 1.06)  → 266°, 26%, 94%
            'lighter':    (0.0, 0.35, 1.10),   # Pure hue, bright
            
            # LED Glow: (0.0, 0.50, 1.01)  → 266°, 33%, 90%
            'led_glow':   (0.0, 0.50, 1.01),   # Rich purple glow
            
            # Dark background
            'body_dark':  (0.0, 0.05, 0.40),   # 40% value (medium dark)
            'body_light': (0.0, 0.05, 0.55),   # 55% value (medium)
        },
    },
    'adwaitaru': {
        'path': 'template-icon-presets/adwaitaru',
        'colors': [
            ('a27ae4', 'hex'),
            ('dbcbfa', 'lightest'),
            ('7155a0', 'dark_shade'),
        ],
        'family_ratios': {
            # Pure: (0.0, 0.29, 1.10)  → 266°, 19%, 98%
            'lightest':   (2.0, 0.20, 1.25),   # 268°, 13%, 111% (warm, bright emblem)
            
            # Pure: (-5.0, 0.71, 0.71)  → 261°, 47%, 63%
            'dark_shade': (-2.0, 0.95, 0.65),  # 264°, 63%, 58% (richer shadow)
        },
    },
    'slot-multicolor': {
        'path': 'template-icon-presets/slot-multicolor',
        'colors': [
            ('7155a0', 'dark_shade'),
            ('a27ae4', 'hex'),
            ('cbb1f0', 'lighter'),
            ('6c763f', 'trash_dark_base'),
            ('adbc6a', 'trash_light_leaf'),
            ('86a10c', 'trash_mid_dark'),
            ('98b710', 'trash_mid_bright'),
            ('9aab4d', 'trash_muted_mid'),
            ('839341', 'trash_olive_shade'),
            ('b2d226', 'trash_bright_pop'),
        ],
        'family_ratios': {
            # Pure: (-5.0, 0.71, 0.71)  → 261°, 47%, 63%
            'dark_shade': (2, 0.85, 0.61),  # Minimal warm, richer, darker
            
            # Pure: (0.0, 0.39, 1.06)  → 266°, 26%, 94%
            'lighter':    (0.0, 0.30, 1.12),   # Pure hue, bright pop

            'trash_dark_base':   (0, 0.47, 0.46),
            'trash_light_leaf':  (0, 0.44, 0.74),
            'trash_mid_dark':    (0, 0.93, 0.63),
            'trash_mid_bright':  (0, 0.91, 0.72),
            'trash_muted_mid':   (0, 0.55, 0.67),
            'trash_olive_shade': (0, 0.56, 0.58),
            'trash_bright_pop':  (0, 0.82, 0.82),
        },
    },
    'sweet': {
        'path': 'template-icon-presets/sweet',
        'colors': [
            ('a27ae4', 'hex'),
            ('7155a0', 'sweet_deep'),
        ],
        'family_ratios': {
            # Pure: (-5.0, 0.71, 0.71)  → 261°, 47%, 63%
            'sweet_deep': (-1.0, 0.90, 0.55),  # Minimal cool, rich shadow
        },
    },
    'sweet-hollow': {
        'path': 'template-icon-presets/sweet-hollow',
        'colors': [
            ('a27ae4', 'hex'),
            ('7155a0', 'dark_shade'),
        ],
        'family_ratios': {
            # Pure: (-5.0, 0.71, 0.71)  → 261°, 47%, 63%
            # Unchanged - the hollow design is stable by nature
            'dark_shade': (-5.0, 0.71, 0.71),
        },
    },
    'breeze': {
        'path': 'template-icon-presets/breeze',
        'colors': [
            ('a27ae4', 'hex'),
            ('7240c3', 'breeze_grad'),
            ('7155a0', 'breeze_edge'),
            ('dbcbfa', 'breeze_lite'),
            ('CBB1F0', 'breeze_sol'),
            ('6c763f', 'trash_dark_base'),
            ('adbc6a', 'trash_light_leaf'),
            ('86a10c', 'trash_mid_dark'),
            ('98b710', 'trash_mid_bright'),
            ('9aab4d', 'trash_muted_mid'),
            ('839341', 'trash_olive_shade'),
            ('b2d226', 'trash_bright_pop'),
        ],
        'family_ratios': {
            # Pure: (0.0, 1.01, 0.85)  → 266°, 67%, 76%
            'breeze_grad': (0.0, 1.15, 0.78),  # Pure hue, rich & darker
            
            # Pure: (-5.0, 0.71, 0.71)  → 261°, 47%, 63%
            'breeze_edge': (-1.0, 0.90, 0.55), # Minimal cool, richer
            
            # Pure: (0.0, 0.29, 1.10)  → 266°, 19%, 98%
            'breeze_lite': (0.0, 0.20, 1.18),  # Pure hue, very bright
            
            # Pure: (0.0, 0.39, 1.06)  → 266°, 26%, 94%
            'breeze_sol':  (0.0, 0.35, 1.10),  # Pure hue, bright

            'trash_dark_base':   (0, 0.47, 0.46),
            'trash_light_leaf':  (0, 0.44, 0.74),
            'trash_mid_dark':    (0, 0.93, 0.63),
            'trash_mid_bright':  (0, 0.91, 0.72),
            'trash_muted_mid':   (0, 0.55, 0.67),
            'trash_olive_shade': (0, 0.56, 0.58),
            'trash_bright_pop':  (0, 0.82, 0.82),
        },
    },
    'neon': {
        'path': 'template-icon-presets/neon',
        'colors': [
            ('a27ae4', 'hex'),
        ],
        'family_ratios': {},
    },
    'besgnulinux': {
        'path': 'template-icon-presets/besgnulinux',
        'colors': [
            ('5989b6', 'hex'),
            ('355878', 'bes_deep'),
        ],
        'family_ratios': {
            # Pure: (0.0, 0.84, 0.66)  → 208°, 43%, 47%
            'bes_deep': (0.0, 0.95, 0.52),   # Pure hue, richer & darker
        },
    },
}


THEME_PRESETS = {
    'breeze': {
        'path':    'template-theme-presets/breeze',
        'rebrand': ['Breeze-Dark', 'Breeze'],
        'colors':  [
            ('3daee9', 'hex'),           # Main accent
            ('61, 174, 233', 'rgb'),     # RGB version
            ('37, 164, 230', 'rgb'),     # RGB alt
            ('cc241d', 'hex'),           # Close button
            ('d79921', 'hide_gold'),     # Hide button
            ('98971a', 'maximize_blue'), # Maximize button
            ('2673a8', 'selection_bg'),
        ],
        'family_ratios': {
            'maximize_blue':  (-25, 1.00, 1.00),
            'hide_gold':      (-50, 1.00, 1.00),
            'selection_bg':   (0, 1.0, SELECTION_BRIGHTNESS),
        },
        'assets':  TARGET_ASSETS,
    },
    'colloid': {
        'path':    'template-theme-presets/colloid',
        'rebrand': ['Colloid-Orange-Dark-Gruvbox'],
        'colors':  [
            ('fe8019', 'hex'),
            ('254, 128, 25', 'rgb'),
            ('d65d0e', 'dark_shade'),
            ('214, 93, 14', 'dark_shade_rgb'),
            ('fe9137', 'shade'),
            ('254, 145, 55', 'shade_rgb'),
            ('fda24d', 'lighter'),
            ('253, 162, 77', 'lighter_rgb'),
            ('cc241d', 'hex'),
            ('d79921', 'hide_gold'),
            ('98971a', 'maximize_blue'),
            ('b35a12', 'selection_bg'),
        ],
        'family_ratios': {
            'dark_shade':     (0, 1.0, 0.78),
            'dark_shade_rgb': (0, 1.0, 0.78),
            'shade':          (0, 1.0, 0.93),
            'shade_rgb':      (0, 1.0, 0.93),
            'lighter':        (0, 0.85, 1.10),
            'lighter_rgb':    (0, 0.85, 1.10),
            'maximize_blue':  (-25, 1.00, 1.00),
            'hide_gold':      (-50, 1.00, 1.00),
            'selection_bg':   (0, 1.00, SELECTION_BRIGHTNESS),
        },
        'assets': GTK2_ASSETS,
    },
    'graphite': {
        'path':    'template-theme-presets/graphite',
        'rebrand': ['Graphite-blue-Dark', 'Graphite-blue'],
        'colors':  [
            ('fe8019', 'hex'),
            ('254, 128, 25', 'rgb'),
            ('d65d0e', 'dark_shade'),
            ('214, 93, 14', 'dark_shade_rgb'),
            ('fe9137', 'shade'),
            ('254, 145, 55', 'shade_rgb'),
            ('fda24d', 'lighter'),
            ('253, 162, 77', 'lighter_rgb'),
            ('b35a12', 'selection_bg'),
        ],
        'family_ratios': {
            'dark_shade':     (0, 1.0, 0.78),
            'dark_shade_rgb': (0, 1.0, 0.78),
            'shade':          (0, 1.0, 0.93),
            'shade_rgb':      (0, 1.0, 0.93),
            'lighter':        (0, 0.85, 1.10),
            'lighter_rgb':    (0, 0.85, 1.10),
            'selection_bg':   (0, 1.00, SELECTION_BRIGHTNESS),
        },
        'assets': GTK2_ASSETS,
    },
    'flat-remix': {
        'path':    'template-theme-presets/flat-remix',
        'rebrand': ['Flat-Remix-GTK-Blue-Darkest-Solid'],
        'colors':  [
            ('2777ff', 'hex'), ('3b84ff', 'hex'), ('317dff', 'hex'), ('1d71ff', 'hex'),
            ('2165d9', 'hex'), ('2262cf', 'hex'), ('377cf1', 'hex'), ('3b83fd', 'hex'),
            ('468aff', 'hex'),
            ('00348d', 'dark_border'), ('00215a', 'dark_border'), ('0047c0', 'dark_border'),
            ('0052df', 'dark_border'), ('0056e9', 'dark_border'), ('004fd4', 'dark_border'),
            ('1d59be', 'dark_border'),
            ('6ea4ff', 'hover_light'), ('74a7ff', 'hover_light'), ('8db7ff', 'hover_light'),
            ('5a97ff', 'hover_light'), ('4187ff', 'hover_light'), ('5594ff', 'hover_light'),
            ('4b8dff', 'hover_light'), ('83b6ec', 'hover_light'), ('337fdc', 'hover_light'),
            ('999911', 'hide_gold'),
            ('999922', 'maximize_blue'),
            ('1a5599', 'selection_bg'),
        ],
        'family_ratios': {
            'dark_border':   (0, 1.00, 0.45),
            'hover_light':   (0, 0.50, 1.00),
            'hide_gold':     (-50, 1.00, 1.00),
            'maximize_blue': (-25, 1.00, 1.00),
            'selection_bg':  (0, 1.00, SELECTION_BRIGHTNESS),
        },
        'assets': FLAT_REMIX_ASSETS,
    },
}

CURSOR_PRESETS = {
    'oxy': {
        'path': 'template-cursor-presets/oxy',
        'description': 'Oxygen cursor theme (binary modulation)',
    },
    # Future presets here
}


# =============================================================================
# SVG ICON TEMPLATES
# These templates use simplified, transformed versions of various
# distro logos for personal theming purposes. All trademarks belong
# to their respective owners. For personal use only.
# =============================================================================

SVG_TEMPLATES = {
    'awp': '''<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<svg xmlns="http://www.w3.org/2000/svg" viewBox="15 15 70 70" width="512" height="512">
  <defs>
    <mask id="f"><rect x="15" y="15" width="70" height="70" rx="15" ry="15" fill="white"/><path d="M 23 68 L 32 36 C 33 32 35 32 36 36 L 41 58 C 42 62 44 62 45 58 L 49 41 C 50 37 52 37 53 41 L 58 58 C 59 62 61 62 62 58 L 65 39 C 66 32 79 32 79 44 C 79 49 76 51 73 51" fill="none" stroke="black" stroke-width="6.5" stroke-linecap="round" stroke-linejoin="round"/></mask>
  </defs>
  <rect x="15" y="15" width="70" height="70" rx="15" ry="15" fill="{{COLOR}}" mask="url(#f)"/>
</svg>''',
    
    'debian': '''<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<svg xmlns="http://www.w3.org/2000/svg" viewBox="15 15 70 70" width="512" height="512">
  <defs>
    <mask id="debianMask">
      <rect x="15" y="15" width="70" height="70" rx="15" ry="15" fill="white"/>
      <g transform="translate(61,55) scale(0.50) translate(-64,-64)" fill="black">
        <path d="M51.986,57.297c-1.797,0.025,0.34,0.926,2.686,1.287c0.648-0.506,1.236-1.018,1.76-1.516C54.971,57.426,53.484,57.434,51.986,57.297"/>
        <path d="M61.631,54.893c1.07-1.477,1.85-3.094,2.125-4.766c-0.24,1.192-0.887,2.221-1.496,3.307c-3.359,2.115-0.316-1.256-0.002-2.537C58.646,55.443,61.762,53.623,61.631,54.893"/>
        <path d="M65.191,45.629c0.217-3.236-0.637-2.213-0.924-0.978C64.602,44.825,64.867,46.932,65.191,45.629"/>
        <path d="M45.172,1.399c0.959,0.172,2.072,0.304,1.916,0.533C48.137,1.702,48.375,1.49,45.172,1.399"/>
        <path d="M47.088,1.932l-0.678,0.14l0.631-0.056L47.088,1.932"/>
        <path d="M76.992,46.856c0.107,2.906-0.85,4.316-1.713,6.812l-1.553,0.776c-1.271,2.468,0.123,1.567-0.787,3.53c-1.984,1.764-6.021,5.52-7.313,5.863c-0.943-0.021,0.639-1.113,0.846-1.541c-2.656,1.824-2.131,2.738-6.193,3.846l-0.119-0.264c-10.018,4.713-23.934-4.627-23.751-17.371c-0.107,0.809-0.304,0.607-0.526,0.934c-0.517-6.557,3.028-13.143,9.007-15.832c5.848-2.895,12.704-1.707,16.893,2.197c-2.301-3.014-6.881-6.209-12.309-5.91c-5.317,0.084-10.291,3.463-11.951,7.131c-2.724,1.715-3.04,6.611-4.227,7.507C31.699,56.271,36.3,61.342,44.083,67.307c1.225,0.826,0.345,0.951,0.511,1.58c-2.586-1.211-4.954-3.039-6.901-5.277c1.033,1.512,2.148,2.982,3.589,4.137c-2.438-0.826-5.695-5.908-6.646-6.115c4.203,7.525,17.052,13.197,23.78,10.383c-3.113,0.115-7.068,0.064-10.566-1.229c-1.469-0.756-3.467-2.322-3.11-2.615c9.182,3.43,18.667,2.598,26.612-3.771c2.021-1.574,4.229-4.252,4.867-4.289c-0.961,1.445,0.164,0.695-0.574,1.971c2.014-3.248-0.875-1.322,2.082-5.609l1.092,1.504c-0.406-2.696,3.348-5.97,2.967-10.234c0.861-1.304,0.961,1.403,0.047,4.403c1.268-3.328,0.334-3.863,0.66-6.609c0.352,0.923,0.814,1.904,1.051,2.878c-0.826-3.216,0.848-5.416,1.262-7.285c-0.408-0.181-1.275,1.422-1.473-2.377c0.029-1.65,0.459-0.865,0.625-1.271c-0.324-0.186-1.174-1.451-1.691-3.877c0.375-0.57,1.002,1.478,1.512,1.562c-0.328-1.929-0.893-3.4-0.916-4.88c-1.49-3.114-0.527,0.415-1.736-1.337c-1.586-4.947,1.316-1.148,1.512-3.396c2.404,3.483,3.775,8.881,4.404,11.117c-0.48-2.726-1.256-5.367-2.203-7.922c0.73,0.307-1.176-5.609,0.949-1.691c-2.27-8.352-9.715-16.156-16.564-19.818c0.838,0.767,1.896,1.73,1.516,1.881c-3.406-2.028-2.807-2.186-3.295-3.043c-2.775-1.129-2.957,0.091-4.795,0.002c-5.23-2.774-6.238-2.479-11.051-4.217l0.219,1.023c-3.465-1.154-4.037,0.438-7.782,0.004c-0.228-0.178,1.2-0.644,2.375-0.815c-3.35,0.442-3.193-0.66-6.471,0.122c0.808-0.567,1.662-0.942,2.524-1.424c-2.732,0.166-6.522,1.59-5.352,0.295c-4.456,1.988-12.37,4.779-16.811,8.943l-0.14-0.933c-2.035,2.443-8.874,7.296-9.419,10.46l-0.544,0.127c-1.059,1.793-1.744,3.825-2.584,5.67c-1.385,2.36-2.03,0.908-1.833,1.278c-2.724,5.523-4.077,10.164-5.246,13.97c0.833,1.245,0.02,7.495,0.335,12.497c-1.368,24.704,17.338,48.69,37.785,54.228c2.997,1.072,7.454,1.031,11.245,1.141c-4.473-1.279-5.051-0.678-9.408-2.197c-3.143-1.48-3.832-3.17-6.058-5.102l0.881,1.557c-4.366-1.545-2.539-1.912-6.091-3.037l0.941-1.229c-1.415-0.107-3.748-2.385-4.386-3.646l-1.548,0.061c-1.86-2.295-2.851-3.949-2.779-5.23l-0.5,0.891c-0.567-0.973-6.843-8.607-3.587-6.83c-0.605-0.553-1.409-0.9-2.281-2.484l0.663-0.758c-1.567-2.016-2.884-4.6-2.784-5.461c0.836,1.129,1.416,1.34,1.99,1.533c-3.957-9.818-4.179-0.541-7.176-9.994l0.634-0.051c-0.486-0.732-0.781-1.527-1.172-2.307l0.276-2.75C4.667,58.121,6.719,47.409,7.13,41.534c0.285-2.389,2.378-4.932,3.97-8.92l-0.97-0.167c1.854-3.234,10.586-12.988,14.63-12.486c1.959-2.461-0.389-0.009-0.772-0.629c4.303-4.453,5.656-3.146,8.56-3.947c3.132-1.859-2.688,0.725-1.203-0.709c5.414-1.383,3.837-3.144,10.9-3.846c0.745,0.424-1.729,0.655-2.35,1.205c4.511-2.207,14.275-1.705,20.617,1.225c7.359,3.439,15.627,13.605,15.953,23.17l0.371,0.1c-0.188,3.802,0.582,8.199-0.752,12.238L76.992,46.856"/>
        <path d="M32.372,59.764l-0.252,1.26c1.181,1.604,2.118,3.342,3.626,4.596C34.661,63.502,33.855,62.627,32.372,59.764"/>
        <path d="M35.164,59.654c-0.625-0.691-0.995-1.523-1.409-2.352c0.396,1.457,1.207,2.709,1.962,3.982L35.164,59.654"/>
        <path d="M84.568,48.916l-0.264,0.662c-0.484,3.438-1.529,6.84-3.131,9.994C82.943,56.244,84.088,52.604,84.568,48.916"/>
        <path d="M45.527,0.537C46.742,0.092,48.514,0.293,49.803,0c-1.68,0.141-3.352,0.225-5.003,0.438L45.527,0.537"/>
        <path d="M2.872,23.219c0.28,2.592-1.95,3.598,0.494,1.889C4.676,22.157,2.854,24.293,2.872,23.219"/>
        <path d="M0,35.215c0.563-1.728,0.665-2.766,0.88-3.766C-0.676,33.438,0.164,33.862,0,35.215"/>
      </g>
    </mask>
  </defs>
  <rect x="15" y="15" width="70" height="70" rx="15" ry="15" fill="{{COLOR}}" mask="url(#debianMask)"/>
</svg>''',

    'swirldeb': '''<svg xmlns="http://www.w3.org/2000/svg" height="512" width="512" viewBox="0 0 128 128">
<path fill-rule="evenodd" fill="{{COLOR}}" d="M20,0 H108 A20,20 0 0 1 128,20 V108 A20,20 0 0 1 108,128 H20 A20,20 0 0 1 0,108 V20 A20,20 0 0 1 20,0 Z M71.439 47.961c.464-.362.88-.726 1.254-1.08-1.04.255-2.1.26-3.168.163-1.281.018.242.659 1.914.917zM76.398 45.331c.765-1.055 1.322-2.206 1.518-3.397-.172.848-.632 1.58-1.066 2.355-2.395 1.509-.227-.895-.002-1.811-2.574 3.245-.356 1.946-.45 2.853zM78.939 38.725c.155-2.307-.454-1.575-.659-.697.239.124.428 1.626.659.697zM64.666 7.194c.684.122 1.479.216 1.364.38.75-.166.92-.315-1.364-.38zM65.999 7.632l.031-.058-.48.101zM64.334 54.868l.019-.06-.019.06zM64.255 55.306c-1.844-.862-3.531-2.166-4.92-3.761.738 1.076 1.533 2.124 2.561 2.947-1.74-.587-4.062-4.212-4.739-4.359 2.997 5.365 12.155 9.409 16.954 7.402-2.221.083-5.04.046-7.533-.877-.963-.494-2.234-1.47-2.244-1.79-.047.125-.128.25-.079.438zM91.872 33.822c.021-1.178.328-.617.445-.906-.229-.134-.836-1.035-1.203-2.765.265-.407.713 1.054 1.076 1.112-.234-1.374-.636-2.422-.653-3.479-1.063-2.22-.376.297-1.237-.953-1.132-3.526.938-.818 1.079-2.42 1.712 2.481 2.688 6.331 3.14 7.926-.344-1.943-.896-3.827-1.573-5.65.522.222-.839-3.996.678-1.204-1.619-5.954-6.925-11.518-11.808-14.127.597.546 1.35 1.231 1.081 1.34-2.429-1.445-2.003-1.559-2.351-2.169-1.977-.806-2.108.065-3.416.002-3.729-1.979-4.448-1.77-7.88-3.007l.156.73c-2.47-.822-2.877.31-5.546.001-.163-.126.855-.459 1.694-.579-2.389.314-2.277-.473-4.614.086.575-.404 1.186-.673 1.798-1.016-1.946.118-4.649 1.134-3.815.209-3.176 1.419-8.817 3.408-11.984 6.377l-.1-.665c-1.45 1.741-6.326 5.201-6.715 7.458l-.388.09c-.753 1.278-1.242 2.727-1.841 4.041-.988 1.683-1.448.648-1.307.912-1.942 3.937-2.908 7.244-3.739 9.959.592.887.013 5.342.237 8.907-.974 17.613 12.361 34.713 26.937 38.66 2.137.766 5.313.738 8.015.813-3.188-.912-3.599-.482-6.706-1.565-2.24-1.056-2.731-2.261-4.318-3.639l.629 1.11c-3.111-1.102-1.81-1.363-4.343-2.165l.671-.874c-1.009-.077-2.672-1.7-3.127-2.601l-1.104.044c-1.325-1.635-2.033-2.815-1.98-3.729l-.356.636c-.403-.693-4.879-6.137-2.558-4.87-.431-.393-1.004-.641-1.626-1.771l.473-.539c-1.115-1.438-2.056-3.28-1.983-3.895.595.804 1.008.955 1.418 1.094-2.822-7-2.979-.386-5.116-7.126l.452-.035c-.346-.523-.558-1.089-.836-1.646l.198-1.959c-2.03-2.346-.567-9.983-.273-14.171.201-1.703 1.695-3.517 2.829-6.359l-.691-.119c1.322-2.304 7.546-9.258 10.43-8.901 1.396-1.754-.278-.008-.551-.447 3.068-3.175 4.033-2.243 6.103-2.815 2.232-1.324-1.916.519-.858-.504 3.861-.985 2.735-2.242 7.771-2.742.532.302-1.232.467-1.675.859 3.215-1.574 10.176-1.215 14.7.873 5.244 2.452 11.139 9.699 11.373 16.518l.265.07c-.133 2.711.415 5.847-.538 8.726l.644-1.364c.077 2.071-.604 3.078-1.22 4.857l-1.108.552c-.906 1.761.09 1.118-.559 2.518-1.416 1.258-4.292 3.935-5.213 4.18-.672-.014.456-.793.604-1.098-1.894 1.3-1.52 1.951-4.417 2.742l-.084-.19c-7.142 3.362-17.062-3.297-16.933-12.382-.075.576-.216.433-.374.664-.368-4.673 2.158-9.367 6.422-11.287 4.169-2.063 9.056-1.218 12.041 1.569-1.639-2.149-4.905-4.427-8.773-4.216-3.79.062-7.336 2.469-8.519 5.085-1.942 1.222-2.167 4.712-3.013 5.352-1.14 8.367 2.141 11.981 7.691 16.234.448.303.499.474.459.629l.007-.012c6.546 2.443 13.307 1.85 18.971-2.69 1.441-1.122 3.016-3.032 3.471-3.059-.685 1.032.118.496-.409 1.406 1.435-2.316-.624-.943 1.484-3.999l.779 1.071c-.292-1.924 2.387-4.257 2.115-7.298.614-.929.685 1.002.033 3.14.905-2.372.24-2.753.471-4.712.249.659.581 1.357.75 2.053-.589-2.293.603-3.86.899-5.193-.3-.128-.916 1.014-1.058-1.693zM55.361 49.699c.842 1.145 1.511 2.384 2.585 3.275-.773-1.507-1.347-2.131-2.404-4.173l-.181.898zM57.531 48.725c-.445-.493-.708-1.088-1.005-1.678.284 1.038.862 1.931 1.4 2.84l-.395-1.162zM90.333 48.666c1.262-2.372 2.076-4.968 2.42-7.598l-.188.473c-.343 2.451-1.09 4.876-2.232 7.125zM67.969 6.196c-1.199.101-2.391.16-3.568.312l.519.071c.866-.316 2.128-.174 3.049-.383zM34.518 22.84l-.007-.091.007.091zM34.861 24.095c.891-2.006-.246-.715-.344-1.255.14 1.779-1.367 2.454.344 1.255zM32.463 31.301c.402-1.231.474-1.972.627-2.685-1.108 1.418-.51 1.721-.627 2.685z M33.145 89.352c-1.429.677-2.662 1.113-5.363 1.352 1.072 1.151 1.072 1.748 1.072 6.99-.753-.237-1.708-.516-3.337-.516-7.111 0-8.263 6.197-8.263 10.808 0 11.202 5.959 11.202 6.833 11.202 2.463 0 4.053-1.352 4.728-3.694l.08 3.535c.755-.041 1.509-.12 2.741-.12.437 0 .793 0 1.112.041.318 0 .635.038.994.079-.636-1.271-1.113-4.131-1.113-10.33 0-6.039 0-16.248.516-19.347zm-4.489 22.049c-.078 1.349-.198 4.249-3.058 4.249-2.94 0-3.656-3.377-3.893-4.846-.278-1.628-.278-2.98-.278-3.575 0-1.906.119-7.231 4.608-7.231 1.352 0 2.106.398 2.701.715l.04 2.583c-.041.041-.041 6.435-.12 8.105zM42.732 97.138c-8.104 0-8.104 8.98-8.104 10.886 0 8.063 3.615 11.241 9.693 11.241 2.7 0 4.012-.395 4.728-.595-.04-1.43.158-2.344.398-3.575-.836.518-1.908 1.093-4.292 1.093-6.197 0-6.278-5.688-6.278-7.688h10.569l.077-2.243c.001-4.648-.912-9.119-6.791-9.119zm2.86 9.362h-6.793c.041-3 .717-6.237 3.536-6.237 3.1 0 3.335 3.237 3.257 6.237zM60.544 97.178c-3.814 0-4.926 3.179-5.521 4.808 0-2.026.039-9.098.355-12.713-2.581 1.192-4.196 1.39-5.902 1.549 1.548.634 1.524 3.258 1.524 11.8v9.878h.048c0 3 0 4.555-.476 5.826 1.628.635 3.653.966 6.078.966 1.549 0 6.038-.014 8.461-4.979 1.152-2.305 1.549-5.41 1.549-7.754 0-1.431-.159-4.572-1.311-6.558-1.111-1.866-2.899-2.823-4.805-2.823zm-3.378 19.546c-.636 0-1.43-.12-1.945-.239-.08-1.43-.08-3.894-.08-6.753 0-3.418.357-5.202.636-6.078.833-2.82 2.701-2.858 3.058-2.858 3.02 0 3.615 4.171 3.615 7.269-.001 3.693-.676 8.659-5.284 8.659zM73.541 102.223c0-2.66.042-3.537.358-5.284-1.509.716-2.422.954-5.679 1.271.556.397.913.634 1.111 2.146.278 1.986.237 11.441.079 14.978-.119 2.581-.278 2.94-.675 3.695.913-.119 1.789-.2 3.058-.2 1.152 0 1.709.08 2.505.2-.876-1.631-.837-3.098-.757-16.806zM90.872 111.28l.041-8.104c0-3.021-.796-5.999-6.755-5.999-3.932 0-6.236 1.191-7.388 1.788.478.874.875 1.626 1.232 3.338 1.55-1.351 3.576-2.066 5.64-2.066 3.3 0 3.3 2.185 3.3 5.282-.755-.039-1.392-.118-2.465-.118-5.047.002-8.384 1.945-8.384 7.271 0 2.504.755 5.005 2.981 6.078.993.438 1.985.438 2.304.438 3.655 0 4.886-2.703 5.642-4.371-.04 1.748 0 2.819.119 4.212.715-.041 1.43-.12 2.624-.12.675 0 1.31.079 1.985.12-.437-.675-.675-1.074-.795-2.623-.081-1.51-.081-3.019-.081-5.126zm-4.649 2.003c-.834 1.788-2.225 2.376-3.257 2.376-2.386 0-2.9-2.093-2.9-4.039 0-3.734 3.338-4.121 4.846-4.121h2.107c-.079 3.001-.12 4.394-.796 5.784zM110 115.095v-11.961c0-2.382-.335-5.997-5.302-5.997-3.974 0-4.698 2.74-5.698 3.974v-4.21c-1 .516-1.819 1.032-5.037 1.192.435.396.936.753 1.134 2.304.36 2.541.253 13.268.172 15.453-.079 2.224-.212 2.542-.49 3.179.793-.12 1.441-.158 2.396-.158 1.192 0 2.032.079 2.706.158-.396-1.393-.394-1.867-.432-6.952 0-5.88.001-7.39.318-8.78.278-1.351 1.034-3.019 3.298-3.019 2.307 0 2.62 1.828 2.698 2.501.122.953.237 3.656.237 5.523v4.289c0 1.073-.195 4.134-.315 5.045-.078.677-.218.877-.376 1.393.757-.118 1.244-.199 2.198-.199 1.626 0 2.178.12 3.053.199-.555-1.153-.56-2.583-.56-3.934zM71.342 94.6l-3.289-3.289 3.29-3.289 3.289 3.289z"/>
</svg>''',

    'ubuntu': '''<svg xmlns="http://www.w3.org/2000/svg" aria-label="Ubuntu" role="img" viewBox="0 0 512 512">
    <defs>
        <mask id="hole-puncher">
            <rect width="512" height="512" rx="110" ry="110" fill="white"/>

            <g fill="black">
                <circle cx="265" cy="256" r="150"/>
                <circle cx="90" cy="257" r="41"/>
                <circle cx="353" cy="409" r="41"/>
                <circle cx="353" cy="104" r="41"/>
            </g>
        </mask>
    </defs>

    <rect width="512" height="512" rx="110" ry="110" fill="{{COLOR}}" mask="url(#hole-puncher)"/>

    <g stroke="{{COLOR}}" stroke-width="10" fill="none">
        <circle cx="90" cy="257" r="41"/>
        <circle cx="353" cy="409" r="41"/>
        <circle cx="353" cy="104" r="41"/>
    </g>

    <g fill="{{COLOR}}">
        <circle cx="265" cy="256" r="99"/>
        <path d="m420 266v-19h-60v19zm-241 119 17 10 31-53-17-9zm17-268-17 10 31 52 17-9z"/>
    </g>
</svg>''',

    'mint': '''<svg xmlns="http://www.w3.org/2000/svg" width="512" height="512" viewBox="0 0 512 512">
  <defs>
    <mask id="stencil">
      <rect width="512" height="512" rx="110" ry="110" fill="white"/>

      <path fill="black"
            transform="translate(2 2) scale(20)"
            d="M 4.62,5.2 L 6.93,5.2 L 6.93,15.59 C 6.93,16.88 7.95,17.9 9.24,17.9 L 16.16,17.9 C 17.45,17.9 18.47,16.88 18.47,15.59 L 18.47,9.81 C 18.47,9.16 17.97,8.66 17.32,8.66 C 16.67,8.66 16.16,9.16 16.16,9.81 L 16.16,15.59 L 13.85,15.59 L 13.85,9.81 C 13.85,9.16 13.35,8.66 12.7,8.66 C 12.05,8.66 11.55,9.16 11.55,9.81 L 11.55,15.59 L 9.24,15.59 L 9.24,9.81 C 9.24,7.91 10.8,6.35 12.7,6.35 C 13.59,6.35 14.39,6.7 15.01,7.26 C 15.63,6.7 16.43,6.35 17.32,6.35 C 19.22,6.35 20.78,7.91 20.78,9.81 L 20.78,15.59 C 20.78,18.12 18.7,20.2 16.16,20.2 L 9.24,20.2 C 6.7,20.2 4.62,18.12 4.62,15.59 L 4.62,5.2"/>
      </mask>
    </defs>

    <rect width="512" height="512" rx="110" ry="110" fill="{{COLOR}}" mask="url(#stencil)"/>
  </svg>''',
  
    'kde': '''<svg xmlns="http://www.w3.org/2000/svg" width="512" height="512" viewBox="0 0 512 512">
  <defs>
    <mask id="stencil">
      <rect width="512" height="512" rx="110" ry="110" fill="white"/>

      <path fill="black"
            transform="scale(1.15) translate(-38.4 -38.4)"
            d="m 281.20611,104 -53.34272,5.29507 0,218.79542 52.75638,-7.64604 0,-93.51753 70.34227,103.51816 L 406.06338,312.798 333.96265,213.39952 406.64956,119.29269 350.37602,106.35107 280.61985,200.4579 281.20786,104 Z m -120.16743,53.5207 c -0.59631,0 -1.30917,0.33662 -1.75893,0.60675 l -20.5164,21.17363 c -0.87376,0.91014 -1.2286,2.45903 -0.58809,3.53029 l 24.03363,39.99643 c -4.31459,7.27928 -7.49407,15.24894 -9.96531,23.52158 l -44.55001,9.41487 c -1.24208,0.33663 -2.34313,1.07771 -2.34313,2.35783 l 0,29.40959 c 0,1.24634 1.1478,2.62733 2.34313,2.93061 l 43.37766,10.58692 c 2.30961,9.58982 5.81721,18.70475 10.55116,27.05178 l -25.20567,38.23818 c -0.69922,1.07771 -0.33553,2.62744 0.5881,3.53008 l 20.5167,20.58102 c 0.87377,0.8426 2.45058,1.28 3.51684,0.60675 l 39.27456,-24.11119 c 7.7223,4.46992 15.81737,8.19855 24.61989,10.58358 l 9.37872,44.11272 C 234.58061,422.9221 235.38983,424 236.6549,424 l 29.30893,0 c 1.2353,0 2.63526,-1.14452 2.93058,-2.35788 l 10.55124,-44.11272 c 9.07344,-2.45901 17.88186,-6.49766 25.79217,-11.17299 l 38.68806,25.87941 c 1.06474,0.67325 2.61181,0.33662 3.51716,-0.60675 l 20.51623,-20.58757 c 0.87895,-0.91013 1.23211,-2.45901 0.5881,-3.52675 l -14.0684,-23.5217 -4.68945,1.75148 c -0.66915,0.33663 -1.36621,0 -1.75894,-0.60675 0,0 -8.86626,-13.4771 -20.51647,-30.58862 -13.92737,27.35153 -42.31004,45.88122 -75.03131,45.88122 -46.48901,0 -84.41043,-37.46011 -84.41043,-84.10922 0,-34.31411 20.54119,-63.82834 49.82563,-77.04924 l 0,-21.76335 c -5.3301,1.88634 -10.34701,3.79294 -15.24108,6.47409 0,0 -0.5735,0 -0.58801,0 l -39.27416,-25.88285 c -0.53401,-0.33766 -1.16135,-0.63999 -1.75918,-0.57247 z"/>
      </mask>
    </defs>

    <rect width="512" height="512" rx="110" ry="110" fill="{{COLOR}}" mask="url(#stencil)"/>
  </svg>''',
  
    'gnome': '''<svg xmlns="http://www.w3.org/2000/svg" width="512" height="512" viewBox="0 0 512 512">
    <defs>
        <mask id="stencil">
            <rect width="512" height="512" rx="110" ry="110" fill="white"/>

            <g fill="black" fill-rule="nonzero" transform="translate(51 51) scale(0.8)">
                <path d="M417.717 4.08c-104.53 0-124.138 148.883-65.334 148.883 58.795 0 169.868-148.883 65.334-148.883z"/>
                <path d="M244.148 134.515c31.31 1.912 65.661-119.486 6.815-111.851-58.825 7.635-38.138 109.939-6.815 111.85z"/>
                <path d="M100.656 209.949c22.268-9.802 2.868-105.678-34.998-79.53-37.848 26.151 12.73 89.327 34.998 79.53z"/>
                <path d="M163.398 159.766c26.509-5.405 27.962-114.141-19.31-94.635-47.282 19.51-7.177 100.048 19.31 94.635z"/>
                <path d="M301.821 403.1c4.704 35.92-26.35 53.66-56.764 30.503-96.818-73.713 160.304-110.487 143.356-211.193-14.068-83.591-270.55-57.856-299.756 72.94-19.77 88.465 81.378 211.197 186.92 211.197 51.92 0 111.808-46.881 123.012-106.272 8.557-45.288-100.693-27.141-96.768 2.826z"/>
            </g>
        </mask>
    </defs>

    <rect width="512" height="512" rx="110" ry="110" fill="{{COLOR}}" mask="url(#stencil)"/>
</svg>''',

    'plasma': '''<svg xmlns="http://www.w3.org/2000/svg" width="512" height="512" viewBox="0 0 512 512">
  <defs>
    <mask id="stencil">
      <rect width="512" height="512" rx="110" ry="110" fill="white"/>

      <path fill="black"
            transform="translate(45 45) scale(20)"
            d="M 7 3 C 6.446 3 6 3.446 6 4 C 6 4.554 6.446 5 7 5 C 7.554 5 8 4.554 8 4 C 8 3.446 7.554 3 7 3 z M 14 3 L 12 5 L 15 8 L 12 11 L 14 13 L 17 10 L 19 8 L 14 3 z M 4.5 9 C 3.669 9 3 9.669 3 10.5 C 3 11.331 3.669 12 4.5 12 C 5.331 12 6 11.331 6 10.5 C 6 9.669 5.331 9 4.5 9 z M 9 15 C 7.892 15 7 15.892 7 17 C 7 18.108 7.892 19 9 19 C 10.108 19 11 18.108 11 17 C 11 15.892 10.108 15 9 15 z " />
    </mask>
  </defs>

  <rect width="512" height="512" rx="110" ry="110" fill="{{COLOR}}" mask="url(#stencil)"/>
</svg>'''
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
