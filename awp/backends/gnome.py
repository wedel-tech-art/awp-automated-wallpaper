#!/usr/bin/env python3
"""
GNOME Desktop Backend for AWP
Contains all GNOME-specific wallpaper and theme management functions.
"""

import os
import subprocess

from core.constants import SCALING_FEH
from core.printer import get_printer

# Get printer instance
_printer = get_printer()

# GNOME-specific scaling mapping
SCALING_GNOME = {'centered': 'centered', 'scaled': 'scaled', 'zoomed': 'zoom'}

def gnome_current_ws():
    """
    GNOME Workspace Detection via D-Bus.
    Works on both X11 and Wayland.
    """
    try:
        import subprocess
        # This sends a message to the GNOME Shell to ask for the active workspace index
        cmd = [
            "dbus-send", "--print-reply", "--dest=org.gnome.Shell",
            "/org/gnome/Shell", "org.freedesktop.DBus.Properties.Get",
            "string:org.gnome.Shell", "string:active-workspace-index"
        ]
        
        result = subprocess.check_output(cmd, text=True)
        
        # D-Bus replies are wordy, so we find the integer value in the output
        # Example reply: variant int32 2
        ws_num = result.split()[-1]
        return int(ws_num)
        
    except Exception as e:
        _printer.error(f"GNOME D-Bus detection failed: {e}", backend="gnome")
        return 0

def _get_current_gsetting(schema, key):
    """Get current gsettings value."""
    try:
        result = subprocess.run(
            ["gsettings", "get", schema, key],
            capture_output=True, text=True, check=True
        )
        # Remove quotes from string output
        return result.stdout.strip().strip("'")
    except:
        return None

def gnome_set_themes(ws_num: int, config):
    """
    Simple orchestrator - applies theme components only if they differ from current.
    Handles: gtk_theme, icon_theme, cursor_theme
    GNOME doesn't have separate WM theme (uses GTK theme).
    """
    section = f"ws{ws_num + 1}"
    if not config.has_section(section):
        return
    
    changes = []
    
    # Get what SHOULD be from config
    should_gtk = config.get(section, 'gtk_theme', fallback=None)
    should_icon = config.get(section, 'icon_theme', fallback=None)
    should_cursor = config.get(section, 'cursor_theme', fallback=None)
    # wm_theme is ignored - GNOME uses GTK theme for window decorations
    
    # Check GTK theme
    if should_gtk:
        current = _get_current_gsetting("org.gnome.desktop.interface", "gtk-theme")
        if current != should_gtk:
            subprocess.run([
                "gsettings", "set", "org.gnome.desktop.interface", 
                "gtk-theme", should_gtk
            ], check=False)
            changes.append("gtk")
    
    # Check Icon theme
    if should_icon:
        current = _get_current_gsetting("org.gnome.desktop.interface", "icon-theme")
        if current != should_icon:
            subprocess.run([
                "gsettings", "set", "org.gnome.desktop.interface", 
                "icon-theme", should_icon
            ], check=False)
            changes.append("icons")
    
    # Check Cursor theme
    if should_cursor:
        current = _get_current_gsetting("org.gnome.desktop.interface", "cursor-theme")
        if current != should_cursor:
            subprocess.run([
                "gsettings", "set", "org.gnome.desktop.interface", 
                "cursor-theme", should_cursor
            ], check=False)
            changes.append("cursor")
    
    # Use printer with explicit backend
    _printer.themes(ws_num, changes, backend="gnome")

def gnome_lean_mode():
    """
    GNOME already uses native wallpaper methods.
    This is a compatibility placeholder.
    """
    _printer.info("GNOME uses native wallpaper methods", backend="gnome")

def gnome_set_wallpaper_native(ws_num: int, image_path: str, scaling: str):
    """
    Alias for gnome_set_wallpaper since GNOME is already native.
    """
    return gnome_set_wallpaper(ws_num, image_path, scaling)

def gnome_set_wallpaper(ws_num: int, image_path: str, scaling: str):
    """Set wallpaper for GNOME with specified scaling."""
    try:
        uri = f"file://{os.path.abspath(image_path)}"
        style_val = SCALING_GNOME.get(scaling, 'zoom')
        wp_name = os.path.basename(image_path)
        
        # Set wallpaper properties (both light and dark mode)
        subprocess.run([
            "gsettings", "set", "org.gnome.desktop.background", 
            "picture-uri", uri
        ], check=True)
        subprocess.run([
            "gsettings", "set", "org.gnome.desktop.background", 
            "picture-uri-dark", uri
        ], check=True)
        subprocess.run([
            "gsettings", "set", "org.gnome.desktop.background", 
            "picture-options", style_val
        ], check=True)
        
        # Use printer for feedback
        _printer.wallpaper(ws_num, wp_name, backend="gnome")
        
    except subprocess.CalledProcessError as e:
        _printer.error(f"Failed to set wallpaper via gsettings: {e}", backend="gnome")
    except Exception as e:
        _printer.error(f"Unexpected error: {e}", backend="gnome")

def gnome_set_icon(icon_path: str):
    """
    GNOME doesn't have a simple panel icon like XFCE/Cinnamon.
    This is a placeholder for API compatibility.
    
    Args:
        icon_path (str): Full path to icon image file (ignored)
    """
    icon_name = os.path.basename(icon_path)
    _printer.info(f"Panel icon setting not available in GNOME (would set: {icon_name})", backend="gnome")
    return False

# Optional: Add helper function for API consistency
def gnome_get_monitors_for_workspace(ws_num: int):
    """Get list of monitors (placeholder for API compatibility)."""
    return []  # GNOME handles multi-monitor automatically
