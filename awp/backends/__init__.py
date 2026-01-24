#!/usr/bin/env python3
"""
AWP Backends Package - COMPLETE VERSION
Exports all desktop environment backend functions.
"""
import sys

# Try to import all backends with error handling
BACKENDS = {}

# XFCE (core backend, should always be available)
try:
    from .xfce import (
        xfce_force_single_workspace_off,
        xfce_configure_screen_blanking,
        xfce_set_wallpaper,
        xfce_set_wallpaper_native,  # <--- Added this
        xfce_lean_mode,             # <--- Added this
        xfce_set_icon,
        xfce_set_themes
    )
    BACKENDS["xfce"] = {
        "wallpaper": xfce_set_wallpaper,
        "wallpaper_native": xfce_set_wallpaper_native, # <--- Added this
        "lean_mode": xfce_lean_mode,                   # <--- Added this
        "icon": xfce_set_icon,
        "themes": xfce_set_themes,
        "workspace_off": xfce_force_single_workspace_off,
        "configure_blanking": xfce_configure_screen_blanking
    }
    print(f"[AWP Backends] XFCE backend loaded (Lean Mode enabled)")
except ImportError as e:
    print(f"[AWP Backends] ERROR: Could not load XFCE backend: {e}")
    sys.exit(1)

# GNOME
try:
    from .gnome import (
        gnome_force_single_workspace_off,
        gnome_set_wallpaper,
        gnome_set_icon,
        gnome_set_themes,
        gnome_configure_screen_blanking
    )
    BACKENDS["gnome"] = {
        "wallpaper": gnome_set_wallpaper,
        "icon": gnome_set_icon,
        "themes": gnome_set_themes,
        "workspace_off": gnome_force_single_workspace_off,
        "configure_blanking": gnome_configure_screen_blanking
    }
    print(f"[AWP Backends] GNOME backend loaded")
except ImportError as e:
    print(f"[AWP Backends] WARNING: GNOME backend not available: {e}")

# Cinnamon
try:
    from .cinnamon import (
        cinnamon_force_single_workspace_off,
        cinnamon_set_wallpaper,
        cinnamon_set_icon,
        cinnamon_set_themes,
        cinnamon_configure_screen_blanking
    )
    BACKENDS["cinnamon"] = {
        "wallpaper": cinnamon_set_wallpaper,
        "icon": cinnamon_set_icon,
        "themes": cinnamon_set_themes,
        "workspace_off": cinnamon_force_single_workspace_off,
        "configure_blanking": cinnamon_configure_screen_blanking
    }
    print(f"[AWP Backends] Cinnamon backend loaded")
except ImportError as e:
    print(f"[AWP Backends] WARNING: Cinnamon backend not available: {e}")

# MATE
try:
    from .mate import (
        mate_force_single_workspace_off,
        mate_set_wallpaper,
        mate_set_icon,
        mate_set_themes,
        mate_configure_screen_blanking
    )
    BACKENDS["mate"] = {
        "wallpaper": mate_set_wallpaper,
        "icon": mate_set_icon,
        "themes": mate_set_themes,
        "workspace_off": mate_force_single_workspace_off,
        "configure_blanking": mate_configure_screen_blanking
    }
    print(f"[AWP Backends] MATE backend loaded")
except ImportError as e:
    print(f"[AWP Backends] WARNING: MATE backend not available: {e}")

# Generic
try:
    from .generic import (
        generic_force_single_workspace_off,
        generic_set_wallpaper,
        generic_set_icon,
        generic_set_themes,
        generic_configure_screen_blanking
    )
    BACKENDS["generic"] = {
        "wallpaper": generic_set_wallpaper,
        "icon": generic_set_icon,
        "themes": generic_set_themes,
        "workspace_off": generic_force_single_workspace_off,
        "configure_blanking": generic_configure_screen_blanking
    }
    print(f"[AWP Backends] Generic backend loaded")
except ImportError as e:
    print(f"[AWP Backends] WARNING: Generic backend not available: {e}")

# Export the main dictionary
backend_funcs = BACKENDS

def get_backend(de_name):
    """
    Get backend functions for a specific desktop environment.
    
    Args:
        de_name (str): Desktop environment name ('xfce', 'gnome', etc.)
    
    Returns:
        dict: Backend functions dictionary or None if not found
    """
    return BACKENDS.get(de_name)

def list_available_backends():
    """Return list of available backend names."""
    return list(BACKENDS.keys())

def is_backend_available(de_name):
    """Check if a specific backend is available."""
    return de_name in BACKENDS

# Print summary
print(f"[AWP Backends] Available backends: {list(BACKENDS.keys())}")
