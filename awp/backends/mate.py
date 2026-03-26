#!/usr/bin/env python3
"""
MATE Desktop Backend for AWP - DUAL MODE VERSION
Supports both native MATE wallpaper and feh-based lean mode.
"""

import os
import subprocess
import time

from core.constants import SCALING_FEH
from core.printer import get_printer

# Get printer instance
_printer = get_printer()

# MATE native scaling
SCALING_MATE = {'centered': 'centered', 'scaled': 'scaled', 'zoomed': 'zoom'}

# Simple state tracking
_lean_mode_active = False

def mate_current_ws():
    """
    Standard X11 Workspace Detection.
    Provides safety and logging for the MATE backend.
    """
    try:
        import subprocess
        # Get the raw workspace index from the root window
        ws_num = subprocess.check_output(
            ["xprop", "-root", "_NET_CURRENT_DESKTOP"], 
            text=True
        ).strip().split()[-1]
        
        return int(ws_num)
    except Exception as e:
        # Using your existing printer logic
        _printer.error(f"X11 xprop failed: {e}", backend="mate")
        return 0

def _get_current_gsetting(schema, key):
    """Get current gsettings value."""
    try:
        result = subprocess.run(
            ["gsettings", "get", schema, key],
            capture_output=True, text=True, check=True
        )
        return result.stdout.strip().strip("'")
    except:
        return None

def mate_set_themes(ws_num: int, config):
    """
    Simple orchestrator - applies theme components only if they differ from current.
    Handles: gtk_theme, icon_theme, cursor_theme, wm_theme
    """
    section = f"ws{ws_num + 1}"
    if not config.has_section(section):
        return
    
    changes = []
    
    # Get what SHOULD be from config
    should_gtk = config.get(section, 'gtk_theme', fallback=None)
    should_icon = config.get(section, 'icon_theme', fallback=None)
    should_cursor = config.get(section, 'cursor_theme', fallback=None)
    should_wm = config.get(section, 'wm_theme', fallback=None)
    
    # Check GTK theme
    if should_gtk:
        current = _get_current_gsetting("org.mate.interface", "gtk-theme")
        if current != should_gtk:
            subprocess.run([
                "gsettings", "set", "org.mate.interface", 
                "gtk-theme", should_gtk
            ], check=False)
            changes.append("gtk")
    
    # Check Icon theme
    if should_icon:
        current = _get_current_gsetting("org.mate.interface", "icon-theme")
        if current != should_icon:
            subprocess.run([
                "gsettings", "set", "org.mate.interface", 
                "icon-theme", should_icon
            ], check=False)
            changes.append("icons")
    
    # Check Cursor theme
    if should_cursor:
        current = _get_current_gsetting("org.mate.peripherals-mouse", "cursor-theme")
        if current != should_cursor:
            subprocess.run([
                "gsettings", "set", "org.mate.peripherals-mouse", 
                "cursor-theme", should_cursor
            ], check=False)
            changes.append("cursor")
    
    # Check Window Manager theme (Marco)
    if should_wm:
        current = _get_current_gsetting("org.mate.Marco.general", "theme")
        if current != should_wm:
            subprocess.run([
                "gsettings", "set", "org.mate.Marco.general", 
                "theme", should_wm
            ], check=False)
            changes.append("wm")
    
    # Use printer with explicit backend
    _printer.themes(ws_num, changes, backend="mate")

def mate_lean_mode():
    """
    Kills MATE desktop components to enable feh-based wallpaper.
    Similar to xfce_lean_mode() - kills desktop manager for low-latency audio.
    """
    global _lean_mode_active
    
    try:
        _printer.info("Activating Lean Mode...", backend="mate")
        
        # Kill caja-desktop (MATE's desktop manager)
        subprocess.run(["pkill", "-f", "caja-desktop"], stderr=subprocess.DEVNULL)
        time.sleep(0.3)  # Brief pause
        
        # Kill cairo-dock if present (common MATE dock)
        subprocess.run(["pkill", "-f", "cairo-dock"], stderr=subprocess.DEVNULL)
        
        _lean_mode_active = True
        _printer.lean_mode("Activated - caja-desktop terminated", backend="mate")
        return True
        
    except Exception as e:
        _printer.error(f"Lean Mode Error: {e}", backend="mate")
        _lean_mode_active = False
        return False


def mate_set_wallpaper_native(ws_num: int, image_path: str, scaling: str):
    """
    LEGACY: Set wallpaper using MATE's native desktop manager.
    Keeps desktop icons and right-click menu.
    """
    try:
        style_val = SCALING_MATE.get(scaling, 'zoom')
        wp_name = os.path.basename(image_path)
        
        # Set wallpaper using MATE's gsettings
        subprocess.run([
            "gsettings", "set", "org.mate.background", 
            "picture-filename", image_path
        ], check=True)
        subprocess.run([
            "gsettings", "set", "org.mate.background", 
            "picture-options", style_val
        ], check=True)
        
        _printer.wallpaper(ws_num, wp_name, backend="mate")
        return True
        
    except subprocess.CalledProcessError as e:
        _printer.error(f"Native wallpaper failed: {e}", backend="mate")
        return False
    except Exception as e:
        _printer.error(f"Unexpected error: {e}", backend="mate")
        return False

def mate_set_wallpaper(ws_num: int, image_path: str, scaling: str):
    """Try feh first, fallback to native MATE."""
    wp_name = os.path.basename(image_path)
    
    # Always try feh if available
    style_flag = SCALING_FEH.get(scaling, '--bg-fill')
    
    try:
        subprocess.run(["feh", style_flag, image_path], check=True)
        _printer.wallpaper(ws_num, wp_name, backend="mate")
        return True
    except Exception as e:
        _printer.warning(f"feh failed, falling back to native: {e}", backend="mate")
        return mate_set_wallpaper_native(ws_num, image_path, scaling)

def mate_set_icon(icon_path: str):
    """MATE icon setting placeholder."""
    icon_name = os.path.basename(icon_path)
    _printer.info(f"Panel icon setting not available in MATE (would set: {icon_name})", backend="mate")
    return False

# Optional: Add helper function for API consistency
def mate_get_monitors_for_workspace(ws_num: int):
    """Get list of monitors (placeholder for API compatibility)."""
    return []  # MATE handles multi-monitor automatically
