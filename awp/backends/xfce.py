#!/usr/bin/env python3
"""
XFCE Desktop Backend for AWP
Simple orchestrator - applies theme components only if they differ from config
"""

import os
import subprocess
import configparser

from core.constants import SCALING_FEH
from core.printer import get_printer

# Get printer instance
_printer = get_printer()
# No set_backend here - we'll pass it explicitly in each function

def _get_current_value(channel, property):
    """Get current XFCE setting value."""
    try:
        result = subprocess.run(
            ["xfconf-query", "-c", channel, "-p", property],
            capture_output=True, text=True, check=True
        )
        return result.stdout.strip()
    except:
        return None

def xfce_set_themes(ws_num: int, config):
    """
    Simple orchestrator - applies theme components only if they differ from current.
    Handles: gtk_theme, icon_theme, cursor_theme, wm_theme
    Panel icon is handled separately by xfce_set_icon()
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
    
    # Check Window Manager theme
    if should_wm:
        current = _get_current_value("xfwm4", "/general/theme")
        if current != should_wm:
            subprocess.run([
                "xfconf-query", "-c", "xfwm4", "-p", "/general/theme", 
                "-s", should_wm, "--create"
            ], check=False)
            changes.append("wm")
    
    # Use printer with explicit backend
    _printer.themes(ws_num, changes, backend="xfce")

def xfce_lean_mode():
    """Kills xfdesktop and prevents XFCE from restarting it."""
    try:
        subprocess.run([
            "xfconf-query", "-c", "xfce4-session", 
            "-p", "/sessions/Failsafe/Client3_Command", 
            "-t", "string", "-s", "true", "--create"
        ], stderr=subprocess.DEVNULL)
        subprocess.run(["xfdesktop", "--quit"], stderr=subprocess.DEVNULL)
        _printer.lean_mode("Activated", backend="xfce")
    except Exception as e:
        _printer.error(str(e), backend="xfce")

def xfce_force_single_workspace_off():
    """Disable single workspace mode in XFCE."""
    subprocess.run([
        "xfconf-query", "-c", "xfce4-desktop",
        "-p", "/backdrop/single-workspace-mode",
        "--set", "false", "--create"
    ])

def xfce_get_monitors_for_workspace(ws_num: int):
    """Get list of monitors for specified XFCE workspace."""
    props = subprocess.check_output(
        ["xfconf-query", "-c", "xfce4-desktop", "-l"], text=True
    ).splitlines()
    monitors = []
    for p in props:
        if f"/workspace{ws_num}/last-image" in p:
            parts = p.split("/")
            if len(parts) >= 6 and parts[3].startswith("monitor"):
                monitors.append(parts[3])
    return sorted(set(monitors))

def xfce_set_wallpaper_native(ws_num: int, image_path: str, scaling: str):
    """LEGACY: Set wallpaper using XFCE's native desktop manager."""
    # XFCE-specific scaling (stays here, not in constants)
    SCALING_XFCE = {'centered': 1, 'scaled': 4, 'zoomed': 5}
    style_code = SCALING_XFCE.get(scaling, 5)
    for mon in xfce_get_monitors_for_workspace(ws_num):
        subprocess.run([
            "xfconf-query", "--channel", "xfce4-desktop",
            "--property", f"/backdrop/screen0/{mon}/workspace{ws_num}/last-image",
            "--set", image_path, "--create"
        ])
        subprocess.run([
            "xfconf-query", "--channel", "xfce4-desktop", 
            "--property", f"/backdrop/screen0/{mon}/workspace{ws_num}/image-style",
            "--set", str(style_code), "--create"
        ])
    subprocess.run(["xfdesktop", "--reload"])

def xfce_set_wallpaper(ws_num: int, image_path: str, scaling: str):
    """Set wallpaper using feh (Lean Mode compatible)."""
    style_flag = SCALING_FEH.get(scaling, '--bg-fill')
    wp_name = os.path.basename(image_path)
    
    try:
        subprocess.run(["feh", style_flag, image_path], check=True)
        _printer.wallpaper(ws_num, wp_name, backend="xfce")
    except Exception as e:
        _printer.warning(f"feh failed, falling back to native: {e}", backend="xfce")
        xfce_set_wallpaper_native(ws_num, image_path, scaling)

def xfce_set_icon(icon_path: str):
    """Set panel/whiskermenu icon."""
    try:
        from core.constants import DEFAULT_ICON
        subprocess.run(
            ["xfconf-query", "-c", "xfce4-panel", "-p", "/plugins/plugin-1/button-icon", 
             "-s", DEFAULT_ICON, "--create", "-t", "string"],
            capture_output=True, check=True
        )
        subprocess.run(
            ["xfconf-query", "-c", "xfce4-panel", "-p", "/plugins/plugin-1/button-icon", 
             "-s", icon_path, "--create", "-t", "string"],
            capture_output=True, check=True
        )
        icon_name = os.path.basename(icon_path)
        _printer.icon(icon_name, backend="xfce")
        return True
    except subprocess.CalledProcessError as e:
        _printer.error(f"Failed to set icon: {e.stderr}", backend="xfce")
        return False
