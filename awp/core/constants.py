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

SYMLINK_MAP = {
    "folder.png": [
        "athena.png", "file-manager.png", "gtk-directory.png", "inode-directory.png",
        "kfm.png", "nautilus-actions-config-tool.png", "nautilus.png", "nemo.png",
        "org.xfce.filemanager.png", "org.xfce.panel.directorymenu.png",
        "org.xfce.thunar.png", "redhat-filemanager.png", "stock_folder.png",
        "system-file-manager.png", "thunar.png", "Thunar.png", "xfce-filemanager.png"
    ],
    "user-desktop.png": ["desktop.png", "gnome-fs-desktop.png", "org.xfce.panel.showdesktop.png", "org.xfce.xfdesktop.png"],
    "user-home.png": ["folder_home.png", "gnome-fs-home.png"],
    "folder-drag-accept.png": ["folder-open.png"],
    "gtk-network.png": ["folder-remote.png", "org.xfce.gigolo.png"],
    "folder-music.png": ["library-music.png"],
    "network-workgroup.png": ["network-server.png"],
    "user-bookmarks.png": ["xapp-user-favorites.png"],
    "text-x-python.png": [
        "application-x-python.png",
        "application-x-python-bytecode.png",
        "text-x-python3.png",
        "text-x-script.python.png",
        "application-x-executable-python.png"
    ],
    "text-x-script.png": [
        "application-x-shellscript.png",
        "application-x-sh.png",
        "text-x-sh.png",
        "shellscript.png"
    ],
    "text-x-generic.png": [
        "text-plain.png",
        "text-log.png",
        "txt.png",
        "text-x-preview.png"
    ],
    "audio-mpeg.png": ["audio-mp3.png", "mpeg.png"],
    "audio-flac.png": ["flac.png", "audio-x-flac.png"],
    "audio-x-wav.png": ["audio-wav.png", "audio-vnd.wave.png", "x-wav.png", "wav.png"],
    "audio-midi.png": [
        "audio-mid.png", "audio-x-midi.png", "audio-sp-midi.png",
        "audio-smf.png", "midi.png", "mid.png"
    ],

    # --- SVG SYMLINKS ---
    "folder.svg": [
        "athena.svg", "file-manager.svg", "gtk-directory.svg", "inode-directory.svg",
        "kfm.svg", "nautilus-actions-config-tool.svg", "nautilus.svg", "nemo.svg",
        "org.xfce.filemanager.svg", "org.xfce.panel.directorymenu.svg",
        "org.xfce.thunar.svg", "redhat-filemanager.svg", "stock_folder.svg",
        "system-file-manager.svg", "thunar.svg", "Thunar.svg", "xfce-filemanager.svg"
    ],
    "user-desktop.svg": ["desktop.svg", "gnome-fs-desktop.svg", "org.xfce.panel.showdesktop.svg", "org.xfce.xfdesktop.svg"],
    "user-home.svg": ["folder_home.svg", "gnome-fs-home.svg"],
    "folder-drag-accept.svg": ["folder-open.svg"],
    "gtk-network.svg": ["folder-remote.svg", "org.xfce.gigolo.svg"],
    "folder-music.svg": ["library-music.svg"],
    "network-workgroup.svg": ["network-server.svg"],
    "user-bookmarks.svg": ["xapp-user-favorites.svg"],
    "text-x-python.svg": [
        "application-x-python.svg",
        "application-x-python-bytecode.svg",
        "text-x-python3.svg",
        "text-x-script.python.svg",
        "application-x-executable-python.svg"
    ],
    "text-x-script.svg": [
        "application-x-shellscript.svg",
        "application-x-sh.svg",
        "text-x-sh.svg",
        "shellscript.svg"
    ],
    "text-x-generic.svg": [
        "text-plain.svg",
        "text-log.svg",
        "txt.svg",
        "text-x-preview.svg"
    ],
}

ICON_MANIFEST = {
    "modulate": {
        "places": [
            "folder.png", "folder-documents.png", "folder-download.png", 
            "folder-drag-accept.png", "folder-music.png", "folder-pictures.png", 
            "folder-publicshare.png", "folder-recent.png", "folder-saved-search.png", 
            "folder-templates.png", "folder-videos.png", "gtk-network.png", 
            "network-workgroup.png", "user-bookmarks.png", "user-desktop.png", "user-home.png"
        ],
        "devices": ["computer.png", "drive-harddisk.png"],
        "legacy": ["go-home.png"],
        "mimetypes": ["text-x-python.png", "text-x-script.png", "text-x-generic.png"]
    },
    "original": {
        "places": ["user-trash.png", "user-trash-full.png"],
        "legacy": ["emblem-symbolic-link.png"],
        "mimetypes": ["audio-mpeg.png", "audio-flac.png", "audio-x-wav.png", "audio-midi.png"]
    }
}

ICON_MANIFEST_SVG = {
    "svg_recolor": {
        "places": [
            "folder.svg", "folder-documents.svg", "folder-download.svg",
            "folder-drag-accept.svg", "folder-music.svg", "folder-pictures.svg",
            "folder-publicshare.svg", "folder-recent.svg", "folder-saved-search.svg",
            "folder-templates.svg", "folder-videos.svg", "gtk-network.svg",
            "network-workgroup.svg", "user-bookmarks.svg", "user-desktop.svg", "user-home.svg"
        ],
        "devices": ["computer.svg", "drive-harddisk.svg"],
        "legacy": ["go-home.svg"],
        "mimetypes": ["text-x-python.svg", "text-x-script.svg", "text-x-generic.svg"]
    },
    "svg_original": {
        "places": ["user-trash.svg", "user-trash-full.svg"],
        "legacy": ["emblem-symbolic-link.svg"],
        "mimetypes": ["audio-mpeg.svg", "audio-flac.svg", "audio-x-wav.svg", "audio-midi.svg"]
    }
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
    'mint':     'template-icon-presets/mint',
    'yaru':     'template-icon-presets/yaru',
    'jojo':     'template-icon-presets/jojo',
    'paomedia': 'template-icon-presets/paomedia',
    'sweet-svg': {
        'path': 'template-icon-presets/sweet-svg',
        'colors': [
            ('a27ae4', 'hex'),        # purple base
            ('7155a0', 'dark_shade'), # same hue, -30% value
            ('cbb1f0', 'lighter'),    # same hue, -44% sat, +5% value
        ],
        'family_ratios': {
            'dark_shade': (1.01, 0.70),
            'lighter':    (0.56, 1.05),
        },
    },
    'breeze-svg': {
        'path': 'template-icon-presets/breeze-svg',
        'colors': [
            ('a27ae4', 'hex'),        # purple base
            ('7155a0', 'dark_shade'), # same hue, -30% value
            ('cbb1f0', 'lighter'),    # same hue, -44% sat, +5% value
        ],
        'family_ratios': {
            'dark_shade': (1.01, 0.70),
            'lighter':    (0.56, 1.05),
        },
    }
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

FOLDER_BADGES = {
    "folder-documents": '''<path d="M 32.794 26.478 C 33.202 26.478 33.533 26.147 33.533 25.739 C 33.533 25.331 33.202 25 32.794 25 L 26.848 25 C 25.828 25 25 25.828 25 26.848 L 25 40.152 C 25 41.172 25.828 42 26.848 42 L 40.152 42 C 41.172 42 42 41.172 42 40.152 L 42 32.794 C 42 32.386 41.669 32.055 41.261 32.055 L 36.423 32.055 C 36.219 32.055 36.054 31.889 36.054 31.685 L 36.054 28.385 C 36.054 28.181 36.183 28.119 36.342 28.246 L 40.06 31.22 C 40.378 31.475 40.843 31.423 41.098 31.105 C 41.353 30.787 41.302 30.322 40.984 30.067 L 35.441 25.633 C 34.963 25.251 34.575 25.438 34.575 26.05 L 34.575 32.425 C 34.575 33.036 35.072 33.533 35.684 33.533 L 39.783 33.533 C 40.191 33.533 40.522 33.864 40.522 34.272 L 40.522 39.413 C 40.522 40.025 40.025 40.522 39.413 40.522 L 27.587 40.522 C 26.975 40.522 26.478 40.025 26.478 39.413 L 26.478 27.587 C 26.478 26.975 26.975 26.478 27.587 26.478 Z
        M 28.442 37 L 38.352 37 C 38.71 37 39 37.29 39 37.648 L 39 37.852 C 39 38.21 38.71 38.5 38.352 38.5 L 28.442 38.5 C 28.085 38.5 27.794 38.21 27.794 37.852 L 27.794 37.648 C 27.794 37.29 28.085 37 28.442 37 Z
        M 28.417 34 L 33.247 34 C 33.591 34 33.87 34.279 33.87 34.623 L 33.87 34.877 C 33.87 35.221 33.591 35.5 33.247 35.5 L 28.417 35.5 C 28.073 35.5 27.794 35.221 27.794 34.877 L 27.794 34.623 C 27.794 34.279 28.073 34 28.417 34 Z
        M 28.417 30.932 L 33.247 30.932 C 33.591 30.932 33.87 31.211 33.87 31.554 L 33.87 31.809 C 33.87 32.153 33.591 32.432 33.247 32.432 L 28.417 32.432 C 28.073 32.432 27.794 32.153 27.794 31.809 L 27.794 31.554 C 27.794 31.211 28.073 30.932 28.417 30.932 Z"
        fill="#ffffff" fill-rule="evenodd"/>''',
    "folder-download": '''<path d="M 34.155 31.088 C 34.155 30.608 34.545 30.218 35.024 30.218 C 35.504 30.218 35.894 30.608 35.894 31.088 L 35.894 34.679 L 38.711 32.802 C 39.71 32.136 40.945 32.473 41.467 33.553 L 41.765 34.17 C 42.288 35.25 41.908 36.677 40.918 37.355 L 34.721 41.594 C 33.928 42.135 32.642 42.135 31.85 41.594 L 25.653 37.355 C 24.662 36.677 24.282 35.25 24.805 34.17 L 25.103 33.553 C 25.626 32.473 26.86 32.136 27.859 32.802 L 30.676 34.679 L 30.676 25.87 C 30.676 25.39 31.066 25 31.546 25 C 32.026 25 32.416 25.39 32.416 25.87 L 32.416 37.062 C 32.416 37.542 32.091 37.715 31.692 37.449 L 27.33 34.54 C 26.931 34.274 26.513 34.406 26.398 34.836 C 26.282 35.265 26.51 35.834 26.907 36.105 L 32.568 39.98 C 32.964 40.251 33.607 40.251 34.003 39.98 L 39.664 36.105 C 40.06 35.834 40.288 35.265 40.173 34.836 C 40.058 34.406 39.64 34.274 39.241 34.54 L 34.878 37.449 C 34.479 37.715 34.155 37.542 34.155 37.062 Z
        M 34.155 27.174 C 34.155 26.694 34.545 26.304 35.024 26.304 C 35.504 26.304 35.894 26.694 35.894 27.174 C 35.894 27.654 35.504 28.044 35.024 28.044 C 34.545 28.044 34.155 27.654 34.155 27.174 Z"
        fill="#ffffff" fill-rule="evenodd"/>''',
    "folder-music": '''<path d="M 41.266 25.948 C 40.799 25.568 40.193 25.42 39.602 25.542 L 31.834 27.174 C 30.914 27.364 30.246 28.185 30.246 29.125 L 30.246 36.575 C 29.699 36.167 29.021 35.926 28.287 35.926 C 26.475 35.926 25 37.4 25 39.213 C 25 41.025 26.475 42.5 28.287 42.5 C 30.095 42.5 31.566 41.033 31.574 39.228 C 31.574 39.227 31.574 39.225 31.574 39.224 L 31.574 31.751 L 40.672 29.816 L 40.672 34.45 C 40.124 34.042 39.446 33.801 38.713 33.801 C 36.9 33.801 35.426 35.275 35.426 37.088 C 35.426 38.9 36.9 40.375 38.713 40.375 C 39.068 40.375 39.418 40.318 39.753 40.207 C 40.101 40.091 40.289 39.715 40.173 39.367 C 40.057 39.019 39.681 38.831 39.333 38.947 C 39.134 39.013 38.925 39.047 38.713 39.047 C 37.633 39.047 36.754 38.168 36.754 37.088 C 36.754 36.008 37.633 35.129 38.713 35.129 C 39.793 35.129 40.672 36.008 40.672 37.088 L 40.672 37.092 C 40.672 37.459 40.969 37.756 41.336 37.756 C 41.703 37.756 42 37.459 42 37.092 L 42 27.492 C 42 26.891 41.732 26.328 41.266 25.948 Z
        M 28.287 41.172 C 27.207 41.172 26.328 40.293 26.328 39.213 C 26.328 38.133 27.207 37.254 28.287 37.254 C 29.367 37.254 30.246 38.133 30.246 39.213 C 30.246 40.293 29.367 41.172 28.287 41.172 Z
        M 31.574 29.125 C 31.574 28.811 31.797 28.538 32.106 28.474 L 39.873 26.842 C 39.918 26.833 39.964 26.828 40.009 26.828 C 40.16 26.828 40.307 26.88 40.427 26.977 C 40.583 27.104 40.672 27.292 40.672 27.492 L 40.672 28.458 L 31.574 30.393 L 31.574 29.125 Z"
        fill="#ffffff" fill-rule="evenodd"/>''',
    "folder-pictures": '''<path d="M 24.507 39.194 C 24.558 39.697 24.983 40.09 25.5 40.09 L 39 40.09 C 39.552 40.09 40 39.642 40 39.09 L 40 34.573 L 35.458 37.683 C 34.775 38.15 33.745 38.055 33.159 37.469 L 30.604 34.914 C 30.408 34.718 30.077 34.702 29.863 34.876 L 24.78 39.03 L 24.78 39.03 C 24.701 39.109 24.608 39.167 24.507 39.194 L 24.507 39.194 Z M 24.5 37.309 L 24.5 31 C 24.5 30.448 24.948 30 25.5 30 L 28.275 30 L 28.275 30 C 28.827 30 29.275 29.552 29.275 29 L 29.275 29 C 29.275 28.448 28.827 28 28.275 28 L 28.275 28 L 24 28 C 23.172 28 22.5 28.672 22.5 29.5 L 22.5 40.59 C 22.5 41.418 23.172 42.09 24 42.09 L 40.5 42.09 C 41.328 42.09 42 41.418 42 40.59 L 42 29.5 C 42 28.672 41.328 28 40.5 28 L 32.455 28 L 32.455 28 C 31.903 28 31.455 28.448 31.455 29 L 31.455 29 C 31.455 29.552 31.903 30 32.455 30 L 32.455 30 L 39 30 C 39.552 30 40 30.448 40 31 L 40 32.792 C 39.91 32.824 39.825 32.873 39.75 32.94 L 39.75 32.94 L 34.7 36.199 C 34.468 36.349 34.122 36.312 33.926 36.116 L 31.311 33.501 C 30.725 32.915 29.737 32.874 29.105 33.409 L 24.5 37.309 L 24.5 37.309 Z M 35.25 32.333 C 35.25 31.643 35.81 31.083 36.5 31.083 C 37.19 31.083 37.75 31.643 37.75 32.333 C 37.75 33.023 37.19 33.583 36.5 33.583 C 35.81 33.583 35.25 33.023 35.25 32.333 Z" fill="#ffffff" fill-rule="evenodd"/>''',
    "folder-videos": '''<path d="M 30.671 40.724 C 30.863 40.724 31.048 40.791 31.185 40.912 C 31.319 41.03 31.395 41.193 31.395 41.362 C 31.395 41.531 31.319 41.694 31.185 41.812 C 31.048 41.933 30.863 42 30.671 42 L 27.377 42 C 26.065 42 25 40.935 25 39.623 L 25 29.388 C 25 28.076 26.065 27.011 27.377 27.011 L 39.623 27.011 C 40.935 27.011 42 28.076 42 29.388 L 42 39.623 C 42 40.935 40.935 42 39.623 42 L 36.329 42 C 36.137 42 35.952 41.933 35.815 41.812 C 35.681 41.694 35.605 41.531 35.605 41.362 C 35.605 41.193 35.681 41.03 35.815 40.912 C 35.952 40.791 36.137 40.724 36.329 40.724 L 38.855 40.724 C 39.792 40.724 40.553 39.963 40.553 39.026 L 40.553 29.985 C 40.553 29.047 39.792 28.286 38.855 28.286 L 28.145 28.286 C 27.208 28.286 26.447 29.047 26.447 29.985 L 26.447 39.026 C 26.447 39.963 27.208 40.724 28.145 40.724 L 30.671 40.724 Z M 34.162 35.361 L 33.47 35.727 C 32.579 36.199 31.855 35.763 31.855 34.754 L 31.855 34.257 C 31.855 33.248 32.579 32.812 33.47 33.284 L 34.162 33.65 C 35.054 34.122 35.054 34.889 34.162 35.361 L 34.162 35.361 Z M 36.638 35.703 L 32.008 38.154 C 31.116 38.626 30.392 38.19 30.392 37.182 L 30.392 31.829 C 30.392 30.82 31.116 30.385 32.008 30.857 L 36.638 33.308 C 37.886 33.969 37.886 35.042 36.638 35.703 L 36.638 35.703 Z" fill="#ffffff" fill-rule="evenodd"/>''',
    "folder-publicshare": '''<path d="m 29.759769,31.656983 -0.01,0.015 0.63,0.444 8.103,5.731 c 0.174,0.123 0.316,0.396 0.316,0.609 v 1.144 c 0,0.213 -0.174,0.386 -0.387,0.386 h -13.136 c -0.213,0 -0.387,-0.173 -0.387,-0.386 v -1.117 c 0,-0.213 0.147,-0.478 0.327,-0.592 l 4.229,-2.661 v 0 c 0.36,-0.226 0.469,-0.703 0.243,-1.064 v 0 c -0.226,-0.362 -0.704,-0.47 -1.066,-0.242 v 0 l -4.296,2.699 c -0.542,0.34 -0.982,1.136 -0.982,1.775 v 1.975 c 0,0.639 0.519,1.159 1.159,1.159 h 14.682 c 0.64,0 1.159,-0.52 1.159,-1.159 v -1.948 c 0,-0.639 -0.424,-1.459 -0.947,-1.828 l -6.406,-4.526 c 0.639,-0.191 1.227,-0.537 1.703,-1.013 0.76,-0.76 1.18,-1.79 1.18,-2.86 0,-1.07 -0.42,-2.09 -1.18,-2.85 -0.75,-0.75 -1.78,-1.18 -2.85,-1.18 -1.07,0 -2.1,0.43 -2.85,1.18 -0.76,0.76 -1.18,1.78 -1.18,2.85 v 0 c 0,1.07 0.42,2.1 1.18,2.86 0.231,0.231 0.489,0.432 0.766,0.599 z m 0.866,-1.231 0.013,-0.018 0.119,0.085 c 0.337,0.159 0.708,0.245 1.086,0.245 0.67,0 1.32,-0.27 1.79,-0.74 0.48,-0.48 0.74,-1.12 0.74,-1.8 0,-0.67 -0.26,-1.31 -0.74,-1.79 -0.47,-0.47 -1.12,-0.74 -1.79,-0.74 -0.67,0 -1.32,0.27 -1.79,0.74 -0.48,0.48 -0.74,1.12 -0.74,1.79 v 0 c 0,0.68 0.26,1.32 0.74,1.8 0.17,0.17 0.363,0.313 0.572,0.428 z" fill="#ffffff" fill-rule="evenodd"/>''',
    "folder-recent": '''<path d="M 28.266 25.89 L 28.266 25.89 C 28.018 26.042 27.691 25.964 27.536 25.716 L 27.536 25.716 C 27.382 25.468 27.458 25.141 27.706 24.987 L 27.706 24.987 C 29.212 24.062 30.94 23.57 32.706 23.57 C 35.227 23.57 37.648 24.574 39.434 26.356 C 41.216 28.142 42.22 30.563 42.22 33.084 C 42.22 35.606 41.216 38.026 39.434 39.813 C 37.648 41.594 35.227 42.598 32.706 42.598 C 30.877 42.598 29.085 42.07 27.547 41.076 C 26.009 40.082 24.788 38.666 24.032 37.001 L 24.032 37.001 C 23.912 36.735 24.031 36.422 24.296 36.301 L 24.296 36.301 C 24.562 36.18 24.877 36.297 24.999 36.562 L 24.999 36.562 C 25.665 38.047 26.749 39.305 28.118 40.188 C 29.487 41.071 31.078 41.541 32.706 41.541 C 34.947 41.541 37.098 40.648 38.684 39.062 C 40.27 37.477 41.163 35.325 41.163 33.084 C 41.163 30.843 40.27 28.692 38.684 27.106 C 37.098 25.52 34.947 24.627 32.706 24.627 C 31.136 24.627 29.598 25.061 28.266 25.89 L 28.266 25.89 L 28.266 25.89 Z M 24.328 34.263 L 24.328 34.263 C 24.36 34.552 24.15 34.812 23.86 34.844 L 23.86 34.844 C 23.57 34.876 23.308 34.666 23.276 34.374 L 23.276 34.374 L 23.223 33.845 L 23.223 33.845 C 23.191 33.557 23.401 33.296 23.691 33.264 L 23.691 33.264 C 23.981 33.232 24.243 33.443 24.275 33.734 L 24.275 33.734 L 24.328 34.263 L 24.328 34.263 L 24.328 34.263 Z M 24.333 31.879 L 24.333 31.879 C 24.284 32.165 24.01 32.358 23.723 32.31 L 23.723 32.31 C 23.435 32.262 23.242 31.988 23.292 31.699 L 23.292 31.699 L 23.361 31.277 L 23.361 31.277 C 23.41 30.991 23.684 30.798 23.971 30.846 L 23.971 30.846 C 24.259 30.894 24.454 31.167 24.407 31.456 L 24.407 31.456 L 24.333 31.879 L 24.333 31.879 Z M 36.591 34.353 L 36.591 34.353 C 36.865 34.455 37.005 34.759 36.903 35.032 L 36.903 35.032 C 36.8 35.305 36.495 35.443 36.221 35.341 L 36.221 35.341 L 31.649 33.629 L 31.649 28.507 L 31.649 28.507 C 31.649 28.215 31.885 27.978 32.177 27.978 L 32.177 27.978 C 32.469 27.978 32.706 28.215 32.706 28.507 L 32.706 28.507 L 32.706 32.894 L 36.591 34.353 Z" fill="#ffffff" fill-rule="evenodd"/>''',
    "folder-templates": '''<path d="M 32.794 26.478 L 32.794 26.478 C 33.202 26.478 33.533 26.147 33.533 25.739 L 33.533 25.739 C 33.533 25.331 33.202 25 32.794 25 L 32.794 25 L 26.848 25 C 25.828 25 25 25.828 25 26.848 L 25 40.152 C 25 41.172 25.828 42 26.848 42 L 40.152 42 C 41.172 42 42 41.172 42 40.152 L 42 32.794 C 42 32.386 41.669 32.055 41.261 32.055 L 36.423 32.055 C 36.219 32.055 36.054 31.889 36.054 31.685 L 36.054 28.385 C 36.054 28.181 36.183 28.119 36.342 28.246 L 40.06 31.22 L 40.06 31.22 C 40.378 31.475 40.843 31.423 41.098 31.105 L 41.098 31.105 C 41.353 30.787 41.302 30.322 40.984 30.067 L 40.984 30.067 L 35.441 25.633 C 34.963 25.251 34.575 25.438 34.575 26.05 L 34.575 32.425 C 34.575 33.036 35.072 33.533 35.684 33.533 L 39.783 33.533 C 40.191 33.533 40.522 33.864 40.522 34.272 L 40.522 39.413 C 40.522 40.025 40.025 40.522 39.413 40.522 L 27.587 40.522 C 26.975 40.522 26.478 40.025 26.478 39.413 L 26.478 27.587 C 26.478 26.975 26.975 26.478 27.587 26.478 L 32.794 26.478 Z M 32.162 38.12 L 28.88 38.12 L 28.88 34.838 L 32.162 38.12 L 32.162 38.12 Z M 34.468 39.228 L 28.141 39.228 C 27.937 39.228 27.772 39.063 27.772 38.859 L 27.772 32.532 C 27.772 32.328 27.889 32.279 28.033 32.423 L 34.577 38.967 C 34.721 39.111 34.672 39.228 34.468 39.228 L 34.468 39.228 Z" fill="#ffffff" fill-rule="evenodd"/>''',
    "gtk-network": '''<path d="M 24 14.5 A 2.5 2.5 0 1 0 24 19.5 A 2.5 2.5 0 1 0 24 14.5 Z M 19.5 18 A 0.625 0.625 0 1 0 19.5 19.25 A 0.625 0.625 0 1 0 19.5 18 Z M 15.75 20.5 A 0.625 0.625 0 1 0 15.75 21.75 A 0.625 0.625 0 1 0 15.75 20.5 Z M 12 23 A 0.625 0.625 0 1 0 12 24.25 A 0.625 0.625 0 1 0 12 23 Z M 6.375 24.25 A 2.5 2.5 0 1 0 6.375 29.25 A 2.5 2.5 0 1 0 6.375 24.25 Z M 12 29.25 A 0.625 0.625 0 1 0 12 30.5 A 0.625 0.625 0 1 0 12 29.25 Z M 15.75 31.75 A 0.625 0.625 0 1 0 15.75 33 A 0.625 0.625 0 1 0 15.75 31.75 Z M 19.5 34.25 A 0.625 0.625 0 1 0 19.5 35.5 A 0.625 0.625 0 1 0 19.5 34.25 Z M 24 34.25 A 2.5 2.5 0 1 0 24 39.25 A 2.5 2.5 0 1 0 24 34.25 Z M 30.75 38.75 A 2.5 2.5 0 1 0 30.75 43.75 A 2.5 2.5 0 1 0 30.75 38.75 Z" fill="#ffffff" fill-rule="evenodd"/>''',
    "network-workgroup": '''<path d="M 41.424947 31.214005 H 26.340031 C 25.811984 31.214005 25.382489 30.777372 25.382489 30.240658 V 27.251095 C 25.382489 26.714256 25.811984 26.27765 26.340031 26.27765 H 41.424947 C 41.952994 26.27765 42.382498 26.714256 42.382498 27.250979 V 30.240658 C 42.382498 30.777372 41.952994 31.214005 41.424947 31.214005 Z M 26.340031 26.993271 C 26.206668 26.993271 26.098101 27.108985 26.098101 27.251095 V 30.240658 C 26.098101 30.382795 26.206668 30.49842 26.340031 30.49842 H 41.424947 C 41.558265 30.49842 41.666868 30.382795 41.666868 30.240658 V 27.250979 C 41.666868 27.108833 41.558265 26.993271 41.424947 26.993271 Z M 41.424947 42.46024 H 26.340031 C 25.811984 42.46024 25.382489 42.023499 25.382489 41.486642 V 38.497232 C 25.382489 37.960536 25.811984 37.523903 26.340031 37.523903 H 41.424947 C 41.952994 37.523903 42.382498 37.960536 42.382498 38.497232 V 41.486642 C 42.382498 42.023508 41.952994 42.46024 41.424947 42.46024 Z M 26.340031 38.23947 C 26.206668 38.23947 26.098101 38.355095 26.098101 38.497232 V 41.486642 C 26.098101 41.628904 26.206668 41.744628 26.340031 41.744628 H 41.424947 C 41.558265 41.744628 41.666868 41.628904 41.666868 41.486642 V 38.497232 C 41.666868 38.355095 41.558265 38.23947 41.424947 38.23947 Z M 41.424947 36.837069 H 26.340031 C 25.811984 36.837069 25.382489 36.400417 25.382489 35.86374 V 32.874141 C 25.382489 32.337472 25.811984 31.90083 26.340031 31.90083 H 41.424947 C 41.952994 31.90083 42.382498 32.337472 42.382498 32.874141 V 35.86374 C 42.382498 36.400417 41.952994 36.837069 41.424947 36.837069 Z M 26.340031 32.616442 C 26.206668 32.616442 26.098101 32.73204 26.098101 32.874141 V 35.86374 C 26.098101 36.005868 26.206668 36.121457 26.340031 36.121457 H 41.424947 C 41.558265 36.121457 41.666868 36.005868 41.666868 35.86374 V 32.874141 C 41.666868 32.73204 41.558265 32.616442 41.424947 32.616442 Z" fill="#ffffff" fill-rule="evenodd"/>
        <ellipse cx="39.960217" cy="28.74604" rx="0.746246" ry="0.745168" fill="#ffffff"/>
        <ellipse cx="39.960217" cy="39.991905" rx="0.746246" ry="0.745169" fill="#ffffff"/>
        <ellipse cx="39.960217" cy="34.368946" rx="0.746246" ry="0.745168" fill="#ffffff"/>''',
    "user-bookmarks": '''<g transform="matrix(0.94972067,0,0,0.94972067,-374.63443,-463.22075)" fill="#ffffff" fill-opacity="1">
        <g transform="matrix(0.63928509,0,0,0.63928509,423.03572,513.51943)">
        <path d="M 14,25.229 7.581,29.814 C 7.276,30.031 6.875,30.061 6.542,29.889 6.209,29.718 6,29.375 6,29 V 5 C 6,3.344 7.344,2 9,2 h 10 c 1.656,0 3,1.344 3,3 V 6 C 22,6.552 21.552,7 21,7 20.448,7 20,6.552 20,6 20,6 20,5 20,5 20,4.448 19.552,4 19,4 19,4 9,4 9,4 8.448,4 8,4.448 8,5 v 22.057 l 5.419,-3.871 c 0.347,-0.248 0.815,-0.248 1.162,0 L 20,27.057 V 24 c 0,-0.552 0.448,-1 1,-1 0.552,0 1,0.448 1,1 v 5 c 0,0.375 -0.209,0.718 -0.542,0.889 -0.333,0.172 -0.734,0.142 -1.039,-0.075 z" fill="#ffffff"/> </g> <path d="m 434.56642,519.43537 c -1.21924,0 -2.21448,1.01735 -2.21448,2.27751 0,0.65577 0.26692,1.25388 0.69552,1.67015 l 3.40394,3.34026 3.40391,-3.34026 c 0.42867,-0.41619 0.69554,-1.01432 0.69554,-1.67015 0,-1.26016 -0.99525,-2.27751 -2.21448,-2.27751 -0.80302,0 -1.49884,0.43808 -1.88503,1.10078 -0.38612,-0.66267 -1.08189,-1.10078 -1.88501,-1.10078 z" fill="#ffffff"/> </g>''',
    "user-home": '''<path d="m 36.924507,34.433024 h -0.40553 v 3.155828 H 35.098385 V 35.22334 h -2.616438 v 2.365512 h -1.388485 v -3.155828 h -0.58187 l 3.273388,-3.070375 z m 0.250431,5.271404 v 0 c 0.47419,-0.30279 1.106442,-0.164485 1.411207,0.309704 v 0 c 0.304766,0.473696 0.166954,1.103972 -0.307235,1.406762 v 0 c -0.784882,0.509259 -1.653241,0.878238 -2.558152,1.101502 -2.185222,0.540378 -4.506279,0.189675 -6.433167,-0.97357 -1.926887,-1.162751 -3.31883,-3.053581 -3.859208,-5.238803 -0.539884,-2.185222 -0.189182,-4.506773 0.974063,-6.43366 1.162752,-1.926394 3.053581,-3.318831 5.238803,-3.858715 2.185222,-0.540378 4.506773,-0.189676 6.433167,0.97357 1.926889,1.162751 3.318832,3.053581 3.85921,5.238802 0.158063,0.64065 0.24401,1.298587 0.246974,1.96344 v 0 c 0.0079,0.562606 -0.443071,1.023952 -1.006171,1.02988 v 0 c -0.563099,0.0059 -1.026422,-0.446034 -1.034325,-1.00864 v 0 c -0.0049,-0.503332 -0.06619,-1.006664 -0.187206,-1.495178 -0.410964,-1.663614 -1.46653,-3.098036 -2.932071,-3.982695 -1.465541,-0.88466 -3.226462,-1.149909 -4.890076,-0.738945 -1.663614,0.411458 -3.098036,1.466529 -3.982696,2.93207 -0.884659,1.466035 -1.150402,3.226956 -0.738944,4.89057 0.411458,1.663614 1.466529,3.098036 2.932069,3.982695 1.465541,0.884659 3.226463,1.149909 4.890077,0.738945 0.686586,-0.169918 1.345511,-0.451962 1.943681,-0.837734 z m -7.14939,-4.20349 h -2.215846 l 5.98565,-5.61766 5.756461,5.61766 H 37.58689 v 3.155828 h -3.556419 v -2.365513 h -0.48061 v 2.365513 h -3.524313 z m 9.428464,1.399352 v 0 c 0.233143,-0.510247 0.839216,-0.73203 1.351933,-0.495429 v 0 c 0.512717,0.236601 0.736475,0.843662 0.49938,1.354403 v 0 c -0.150654,0.324523 -0.318102,0.639168 -0.510247,0.938993 v 0 C 40.49624,39.17788 39.86547,39.324582 39.387327,39.02525 v 0 c -0.47814,-0.299332 -0.622867,-0.929114 -0.323041,-1.405279 v 0 C 39.21,37.387816 39.340896,37.152203 39.454012,36.90029 Z" fill="#ffffff" fill-rule="evenodd"/>''',
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
