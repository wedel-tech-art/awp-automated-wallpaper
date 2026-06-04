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
    "user-trash": {
        "context": "places",
        "png_action": {"original": ["slot-multicolor", "sweet-svg", "mint", "yaru"]},
        "svg_action": {"svg_original": ["slot-multicolor", "sweet-svg", "mint", "yaru"]},
        "symlinks": []
    },
    "user-trash-full": {
        "context": "places",
        "png_action": {"original": ["slot-multicolor", "sweet-svg", "mint", "yaru"]},
        "svg_action": {"svg_original": ["slot-multicolor", "sweet-svg", "mint", "yaru"]},
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
        "png_action": {"original": ["slot-multicolor", "sweet-svg", "breeze-svg", "mint", "yaru"]},
        "svg_action": {"svg_original": ["slot-multicolor", "sweet-svg", "breeze-svg", "mint", "yaru"]},
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
        "png_action": {"original": ["slot-multicolor", "sweet-svg", "breeze-svg", "mint", "yaru", "adwaitaru", "rami"]},
        "svg_action": {"svg_original": ["slot-multicolor", "sweet-svg", "breeze-svg", "mint", "yaru", "adwaitaru", "rami"]},
        "symlinks": ["text-x-markdown", "markdown", "text-x-readme", "readme"]
    },
    "audio-mpeg": {
        "context": "mimetypes",
        "png_action": {"original": ["slot-multicolor", "sweet-svg", "breeze-svg", "mint", "yaru", "adwaitaru", "rami"]},
        "svg_action": {"svg_original": ["slot-multicolor", "sweet-svg", "breeze-svg", "mint", "yaru", "adwaitaru", "rami"]},
        "symlinks": ["audio-mp3", "mpeg"]
    },
    "audio-flac": {
        "context": "mimetypes",
        "png_action": {"original": ["slot-multicolor", "sweet-svg", "breeze-svg", "mint", "yaru", "adwaitaru", "rami"]},
        "svg_action": {"svg_original": ["slot-multicolor", "sweet-svg", "breeze-svg", "mint", "yaru", "adwaitaru", "rami"]},
        "symlinks": ["flac", "audio-x-flac"]
    },
    "audio-x-wav": {
        "context": "mimetypes",
        "png_action": {"original": ["slot-multicolor", "sweet-svg", "breeze-svg", "mint", "yaru", "adwaitaru", "rami"]},
        "svg_action": {"svg_original": ["slot-multicolor", "sweet-svg", "breeze-svg", "mint", "yaru", "adwaitaru", "rami"]},
        "symlinks": ["audio-wav", "audio-vnd.wave", "x-wav", "wav"]
    },
    "audio-midi": {
        "context": "mimetypes",
        "png_action": {"original": ["slot-multicolor", "sweet-svg", "breeze-svg", "mint", "yaru", "adwaitaru", "rami"]},
        "svg_action": {"svg_original": ["slot-multicolor", "sweet-svg", "breeze-svg", "mint", "yaru", "adwaitaru", "rami"]},
        "symlinks": [
            "audio-mid", "audio-x-midi", "audio-sp-midi",
            "audio-smf", "midi", "mid"
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

_PURPLE = {
    'colors': [
        ('a27ae4', 'hex'),
        ('7155a0', 'dark_shade'),
        ('cbb1f0', 'lighter'),
        ('dbcbfa', 'lightest'),
    ],
    'family_ratios': {
        'dark_shade': (1.01, 0.70),
        'lighter':    (0.56, 1.05),
        'lightest':   (0.40, 1.15),
    },
}

ICON_PRESETS = {
    'slot-multicolor': {'path': 'template-icon-presets/slot-multicolor', **_PURPLE},
    'sweet-svg':       {'path': 'template-icon-presets/sweet-svg',       **_PURPLE},
    'breeze-svg':      {'path': 'template-icon-presets/breeze-svg',      **_PURPLE},
    'mint':            {'path': 'template-icon-presets/mint',            **_PURPLE},
    'yaru':            {'path': 'template-icon-presets/yaru',            **_PURPLE},
    'adwaitaru':       {'path': 'template-icon-presets/adwaitaru',       **_PURPLE},
    'neon':            {'path': 'template-icon-presets/neon',            **_PURPLE},
    'rami':            {'path': 'template-icon-presets/rami',            **_PURPLE},
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
            ('254, 128, 25', 'rgb'),
            
            ('d65d0e', 'dark_shade'),
            ('214, 93, 14', 'dark_shade_rgb'),
            
            ('fe9137', 'shade'),
            ('254, 145, 55', 'shade_rgb'),
            ('fda24d', 'lighter'),
            ('253, 162, 77', 'lighter_rgb'),
        ],
        'family_ratios': {
            'dark_shade':     (1.0, 0.78),
            'dark_shade_rgb': (1.0, 0.78),
            'shade':          (1.0, 0.93),
            'shade_rgb':      (1.0, 0.93),
            'lighter':        (0.85, 1.10),
            'lighter_rgb':    (0.85, 1.10),
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
        ],
        'family_ratios': {
            'dark_shade':     (1.0, 0.78),
            'dark_shade_rgb': (1.0, 0.78),
            'shade':          (1.0, 0.93),
            'shade_rgb':      (1.0, 0.93),
            'lighter':        (0.85, 1.10),
            'lighter_rgb':    (0.85, 1.10),
        },
        'assets': GTK2_ASSETS,
    },
    'flat-remix': {
        'path':    'template-theme-presets/flat-remix',
        'rebrand': ['Flat-Remix-GTK-Blue-Darkest-Solid'],
        'colors':  [
            # === MAIN ACCENT ===
            ('2777ff', 'hex'), ('3b84ff', 'hex'), ('317dff', 'hex'), ('1d71ff', 'hex'),
            ('2165d9', 'hex'), ('2262cf', 'hex'), ('377cf1', 'hex'), ('3b83fd', 'hex'),
            ('468aff', 'hex'),

            # === DARK BORDERS ===
            ('00348d', 'dark_border'), ('00215a', 'dark_border'), ('0047c0', 'dark_border'),
            ('0052df', 'dark_border'), ('0056e9', 'dark_border'), ('004fd4', 'dark_border'),
            ('1d59be', 'dark_border'),

            # === BRIGT LIGHTS / HOVERS ===
            ('6ea4ff', 'hover_light'), ('74a7ff', 'hover_light'), ('8db7ff', 'hover_light'),
            ('5a97ff', 'hover_light'), ('4187ff', 'hover_light'), ('5594ff', 'hover_light'),
            ('4b8dff', 'hover_light'), ('83b6ec', 'hover_light'), ('337fdc', 'hover_light'),
        ],
        'family_ratios': {
            'dark_border': (1.00, 0.45),
            'hover_light': (0.50, 1.00),
        },
        'assets': FLAT_REMIX_ASSETS,
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
