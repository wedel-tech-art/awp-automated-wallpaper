#!/usr/bin/env python3
"""
AWP Backends Package
Dynamic loader for Desktop Environment backends.
"""
import importlib
import logging

logger = logging.getLogger("AWP.Backends")

# Map of internal keys to their module names and pretty names
BACKEND_MAP = {
    "xfce": ("xfce", "XFCE"),
    "gnome": ("gnome", "GNOME"),
    "cinnamon": ("cinnamon", "Cinnamon"),
    "mate": ("mate", "MATE"),
    "generic": ("generic", "Generic")
}

BACKENDS = {}

for key, (mod_name, pretty_name) in BACKEND_MAP.items():
    try:
        # Dynamically import the module
        module = importlib.import_module(f".{mod_name}", package=__package__)
        
        # Map the specific functions to the standard AWP interface
        BACKENDS[key] = {
            "wallpaper": getattr(module, f"{mod_name}_set_wallpaper"),
            "icon": getattr(module, f"{mod_name}_set_icon"),
            "themes": getattr(module, f"{mod_name}_set_themes"),
            "workspace_off": getattr(module, f"{mod_name}_force_single_workspace_off"),
            "configure_blanking": getattr(module, f"{mod_name}_configure_screen_blanking")
        }
        logger.info(f"{pretty_name} backend loaded successfully.")
    except (ImportError, AttributeError) as e:
        if key == "xfce":
            logger.critical(f"Core backend XFCE failed to load: {e}")
        else:
            logger.debug(f"{pretty_name} backend not available: {e}")

def get_backend(de_name):
    """Returns the function dictionary for the requested DE."""
    return BACKENDS.get(de_name)

def list_available_backends():
    """Returns list of loaded backend keys."""
    return list(BACKENDS.keys())
