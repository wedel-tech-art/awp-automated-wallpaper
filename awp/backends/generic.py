#!/usr/bin/env python3
"""
Generic Backend for AWP
For pure window managers without desktop environment dependencies.
Provides minimal functionality: wallpapers via feh, theme hints only.
Now includes Qt6 accent color support via /dev/shm (RAM)
"""

import os
import subprocess
import configparser
import time

from core.constants import SCALING_FEH
from core.printer import get_printer
from backends import ensure_qt6_kde_symlinks, write_qt6_kde_accent

ensure_qt6_kde_symlinks()

# Get printer instance
_printer = get_printer()


def generic_current_ws():
    """
    Standard X11 Workspace Detection.
    Provides safety and logging for the GENERIC backend.
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
        _printer.error(f"X11 xprop failed: {e}", backend="generic")
        return 0


def generic_lean_mode():
    """
    Generic lean mode - nothing to kill, already using feh.
    """
    _printer.info("Already lean (feh only)", backend="generic")


def generic_set_wallpaper(ws_num: int, image_path: str, scaling: str):
    """
    Set wallpaper using feh (works with any WM).
    """
    style_flag = SCALING_FEH.get(scaling, '--bg-fill')
    wp_name = os.path.basename(image_path)
    
    try:
        subprocess.run(["feh", style_flag, image_path], check=True)
        _printer.wallpaper(ws_num, wp_name, backend="generic")
    except Exception as e:
        _printer.error(f"feh failed: {e}", backend="generic")


def generic_set_wallpaper_native(ws_num: int, image_path: str, scaling: str):
    """
    No native method - always uses feh.
    """
    generic_set_wallpaper(ws_num, image_path, scaling)


def generic_set_icon(icon_path: str):
    """
    Generic icon setter - just logs the request.
    Panel/dock icons are WM/panel specific.
    """
    icon_name = os.path.basename(icon_path)
    _printer.info(f"Icon request: {icon_name} (install panel-specific backend)", backend="generic")
    return False


def generic_set_themes(ws_num: int, config):
    """
    Minimal theme support - attempts gsettings, but doesn't pretend to be comprehensive.
    For real theme management, use a DE-specific backend.
    Handles: gtk_theme, icon_theme, cursor_theme, qt6_accent
    """
    section = f"ws{ws_num + 1}"
    if not config.has_section(section):
        return
    
    changes = []
    cursor_changed = False
    
    # Get what SHOULD be from config
    should_gtk = config.get(section, 'gtk_theme', fallback=None)
    should_icon = config.get(section, 'icon_theme', fallback=None)
    should_cursor = config.get(section, 'cursor_theme', fallback=None)
    should_accent = config.get(section, 'icon_color', fallback=None)
    
    # Try gsettings for GTK theme (works on most GTK systems)
    if should_gtk:
        try:
            # Check current value first
            result = subprocess.run(
                ["gsettings", "get", "org.gnome.desktop.interface", "gtk-theme"],
                capture_output=True, text=True, check=True
            )
            current = result.stdout.strip().strip("'")
            
            if current != should_gtk:
                subprocess.run([
                    "gsettings", "set", "org.gnome.desktop.interface", 
                    "gtk-theme", should_gtk
                ], check=True)
                changes.append("gtk")
        except:
            _printer.debug("gsettings not available for GTK theme", backend="generic")
    
    # Try gsettings for icon theme
    if should_icon:
        try:
            result = subprocess.run(
                ["gsettings", "get", "org.gnome.desktop.interface", "icon-theme"],
                capture_output=True, text=True, check=True
            )
            current = result.stdout.strip().strip("'")
            
            if current != should_icon:
                subprocess.run([
                    "gsettings", "set", "org.gnome.desktop.interface", 
                    "icon-theme", should_icon
                ], check=True)
                changes.append("icons")
        except:
            _printer.debug("gsettings not available for icon theme", backend="generic")
    
    # Try gsettings for cursor theme
    if should_cursor:
        try:
            result = subprocess.run(
                ["gsettings", "get", "org.gnome.desktop.interface", "cursor-theme"],
                capture_output=True, text=True, check=True
            )
            current = result.stdout.strip().strip("'")
            
            if current != should_cursor:
                subprocess.run([
                    "gsettings", "set", "org.gnome.desktop.interface", 
                    "cursor-theme", should_cursor
                ], check=True)
                changes.append("cursor")
                cursor_changed = True
        except:
            _printer.debug("gsettings not available for cursor theme", backend="generic")
    
    # Force cursor refresh if it changed (fixes stubborn apps)
    if cursor_changed:
        time.sleep(0.5)
        subprocess.run(["xsetroot", "-cursor_name", "left_ptr"], check=False)
        subprocess.run([
            "xprop", "-root", "-f", "_XSETTINGS_SETTINGS", "8s",
            "-set", "_XSETTINGS_SETTINGS", ""
        ], check=False)
        _printer.info("Cursor refresh triggered", backend="generic")
    
    # ========================================================================
    # Qt6 Accent Color (via /dev/shm - RAM, no disk writes!)
    # ========================================================================
    if should_accent:
        write_qt6_kde_accent(should_accent)
        changes.append(f"qt6:{should_accent}")
    
    # Report what was applied (if anything)
    if changes:
        _printer.themes(ws_num, changes, backend="generic")
    else:
        _printer.info(f"No theme changes (WM may need manual theme tools)", backend="generic")
