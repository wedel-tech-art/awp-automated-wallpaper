#!/usr/bin/env python3
"""
Hybrid Qtile/XFCE Backend for AWP
Uses Qtile as WM with xfsettingsd for theme management.
Simple orchestrator - applies theme components only if they differ from config.
Qtile is already lean, so no desktop environment to optimize.
All functions maintained for backend API consistency.
"""

import os
import json
import subprocess
import configparser
import time
from core.constants import SCALING_FEH
from core.printer import get_printer

# Get printer instance
_printer = get_printer()
# No set_backend here - we'll pass it explicitly in each function

def qtile_xfce_current_ws():
    """
    Read current workspace from /dev/shm (written by Qtile).
    Used by subprocesses (nav.py) to get current workspace.
    """
    try:
        workspace_file = "/dev/shm/qtile_current_ws"
        if os.path.exists(workspace_file):
            with open(workspace_file, 'r') as f:
                state = json.load(f)
                return state.get('workspace_num', 0)
    except Exception as e:
        print(f"Failed to read workspace from /dev/shm: {e}")
    
    # Fallback to xprop
    try:
        import subprocess
        ws_num = subprocess.check_output(
            ["xprop", "-root", "_NET_CURRENT_DESKTOP"], 
            text=True
        ).strip().split()[-1]
        return int(ws_num)
    except:
        return 0

def _get_current_value(channel, property):
    """Get current XFCE setting value via xfsettingsd."""
    try:
        result = subprocess.run(
            ["xfconf-query", "-c", channel, "-p", property],
            capture_output=True, text=True, check=True
        )
        return result.stdout.strip()
    except:
        return None

def qtile_xfce_set_themes(ws_num: int, config):
    """
    Simple orchestrator - applies theme components only if they differ from current.
    Uses xfsettingsd for: gtk_theme, icon_theme, cursor_theme
    Qtile handles WM itself, so wm_theme is not applicable.
    """
    section = f"ws{ws_num + 1}"
    if not config.has_section(section):
        return
    
    changes = []
    cursor_changed = False  # Track cursor changes
    
    # Get what SHOULD be from config
    should_gtk = config.get(section, 'gtk_theme', fallback=None)
    should_icon = config.get(section, 'icon_theme', fallback=None)
    should_cursor = config.get(section, 'cursor_theme', fallback=None)
    # wm_theme is ignored - Qtile doesn't use XFWM
    
    # Check GTK theme
    if should_gtk:
        current = _get_current_value("xsettings", "/Net/ThemeName")
        if current != should_gtk:
            subprocess.run([
                "xfconf-query", "-c", "xsettings", "-p", "/Net/ThemeName", 
                "-s", should_gtk, "--create"
            ], check=False)
            changes.append("gtk")
    
    # Check Icon theme
    if should_icon:
        current = _get_current_value("xsettings", "/Net/IconThemeName")
        if current != should_icon:
            subprocess.run([
                "xfconf-query", "-c", "xsettings", "-p", "/Net/IconThemeName", 
                "-s", should_icon, "--create"
            ], check=False)
            changes.append("icons")
    
    # Check Cursor theme
    if should_cursor:
        current = _get_current_value("xsettings", "/Gtk/CursorThemeName")
        if current != should_cursor:
            subprocess.run([
                "xfconf-query", "-c", "xsettings", "-p", "/Gtk/CursorThemeName", 
                "-s", should_cursor, "--create"
            ], check=False)
            changes.append("cursor")
            cursor_changed = True
    
    # Force cursor refresh if it changed (fixes stubborn apps)
    if cursor_changed:
        time.sleep(0.5)
        subprocess.run(["xsetroot", "-cursor_name", "left_ptr"], check=False)
        subprocess.run([
            "xprop", "-root", "-f", "_XSETTINGS_SETTINGS", "8s",
            "-set", "_XSETTINGS_SETTINGS", ""
        ], check=False)
        _printer.info("Cursor refresh triggered", backend="qtile_xfce")
    
    # Use printer with explicit backend
    _printer.themes(ws_num, changes, backend="qtile_xfce")


# =============================================================================
# LEAN MODE - Qtile is already lean
# =============================================================================

def qtile_xfce_lean_mode():
    """
    Generic lean mode - nothing to kill, already using feh.
    """
    _printer.info("Started xfsettingsd for themes", backend="qtile_xfce")


# =============================================================================
# MONITOR FUNCTIONS - Not needed with feh, kept for API
# =============================================================================

def qtile_xfce_get_monitors_for_workspace(ws_num: int):
    """Not needed with feh - returns empty list for API compatibility."""
    return []


# =============================================================================
# WALLPAPER FUNCTIONS
# =============================================================================

def qtile_xfce_set_wallpaper_native(ws_num: int, image_path: str, scaling: str):
    """Native wallpaper not used with Qtile - falls back to feh."""
    qtile_xfce_set_wallpaper(ws_num, image_path, scaling)

def qtile_xfce_set_wallpaper(ws_num: int, image_path: str, scaling: str):
    """Set wallpaper using feh (works with any WM)."""
    style_flag = SCALING_FEH.get(scaling, '--bg-fill')
    wp_name = os.path.basename(image_path)
    
    try:
        subprocess.run(["feh", style_flag, image_path], check=True)
        _printer.wallpaper(ws_num, wp_name, backend="qtile_xfce")
    except Exception as e:
        _printer.error(f"feh failed: {e}", backend="qtile_xfce")


# =============================================================================
# ICON FUNCTIONS - Not needed for Qtile bar, kept for API
# =============================================================================

def qtile_xfce_set_icon(icon_path: str):
    """Panel icon not used with Qtile - just returns False for API."""
    # Optional: If you ever use xfce4-panel with Qtile:
    # from backends.xfce import xfce_set_icon
    # return xfce_set_icon(icon_path)
    return False
