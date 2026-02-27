#!/usr/bin/env python3
"""
Hybrid Qtile/XFCE Backend for AWP
Uses Qtile as WM with xfsettingsd for theme management.
Simple orchestrator - applies theme components only if they differ from config.
Qtile is already lean, so no desktop environment to optimize.
All functions maintained for backend API consistency.
"""

import os
import subprocess
import configparser

# ANSI Color Codes
CLR_RED    = "\033[91m"
CLR_GREEN  = "\033[92m"
CLR_YELLOW = "\033[93m"
CLR_CYAN   = "\033[96m"
CLR_RESET  = "\033[0m"
CLR_BOLD   = "\033[1m"

# Wallpaper scaling for feh (works with any WM)
SCALING_FEH = {
    'centered': '--bg-center',
    'scaled': '--bg-scale',
    'zoomed': '--bg-fill'
}

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
    
    # Simple feedback if anything changed
    if changes:
        print(f"{CLR_CYAN}[AWP-Qtile]{CLR_RESET} WS{ws_num + 1} themes: {CLR_GREEN}{', '.join(changes)}{CLR_RESET}")


# =============================================================================
# LEAN MODE - Qtile is already lean
# =============================================================================

def qtile_xfce_lean_mode():
    """Qtile is already lean - just ensure xfsettingsd is running for themes."""
    try:
        # Check if xfsettingsd is running, start if not
        subprocess.run(["pgrep", "xfsettingsd"], check=True)
    except:
        subprocess.Popen(["xfsettingsd"])
        print(f"{CLR_CYAN}[AWP-Qtile]{CLR_RESET} {CLR_GREEN}Started xfsettingsd for themes{CLR_RESET}")


# =============================================================================
# FORCE SINGLE WORKSPACE - Not needed for Qtile, kept for API
# =============================================================================

def qtile_xfce_force_single_workspace_off():
    """Not needed for Qtile - workspaces are handled by the WM."""
    pass


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
        print(f"{CLR_CYAN}[AWP-Qtile]{CLR_RESET} Workspace {ws_num + 1} -> {CLR_GREEN}{CLR_BOLD}{wp_name}{CLR_RESET}")
    except Exception as e:
        print(f"{CLR_RED}[AWP-Qtile] feh failed: {e}{CLR_RESET}")
        # Fallback to something? Maybe just warn


# =============================================================================
# ICON FUNCTIONS - Not needed for Qtile bar, kept for API
# =============================================================================

def qtile_xfce_set_icon(icon_path: str):
    """Panel icon not used with Qtile - just returns False for API."""
    # Optional: If you ever use xfce4-panel with Qtile, you could enable this
    return False
