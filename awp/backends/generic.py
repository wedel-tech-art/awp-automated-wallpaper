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

from core.constants import SCALING_FEH
from core.printer import get_printer

# Get printer instance
_printer = get_printer()


# =============================================================================
# QT6 COLOR SCHEME SETUP (RAM-based, zero disk writes)
# =============================================================================

def _ensure_qt6_symlink():
    """
    Ensure qt6ct points to /dev/shm for zero-disk-write theming.
    Creates symlink: ~/.config/qt6ct/colors/awp.conf -> /dev/shm/awp-qt-color.conf
    """
    target_link = os.path.expanduser("~/.config/qt6ct/colors/awp.conf")
    shm_file = "/dev/shm/awp-qt-color.conf"
    
    # Create directory if needed
    os.makedirs(os.path.dirname(target_link), exist_ok=True)
    
    # Check if symlink already exists and points to the right place
    if os.path.islink(target_link):
        current_target = os.readlink(target_link)
        if current_target == shm_file:
            return
    
    # Remove existing file/symlink if it exists
    if os.path.exists(target_link) or os.path.islink(target_link):
        os.remove(target_link)
    
    # Create the symlink
    os.symlink(shm_file, target_link)
    
    # Also ensure qt6ct.conf uses this symlink
    qt6ct_conf = os.path.expanduser("~/.config/qt6ct/qt6ct.conf")
    if os.path.exists(qt6ct_conf):
        cfg = configparser.ConfigParser()
        cfg.read(qt6ct_conf)
        if cfg.has_section('Appearance'):
            current_path = cfg.get('Appearance', 'color_scheme_path', fallback='')
            if current_path != target_link:
                cfg.set('Appearance', 'color_scheme_path', target_link)
                with open(qt6ct_conf, 'w') as f:
                    cfg.write(f)
                _printer.info("Updated qt6ct.conf to use symlink", backend="generic")
    
    _printer.info(f"Qt6 symlink created: {target_link} -> {shm_file}", backend="generic")


def _write_qt6_accent(accent_color: str) -> None:
    """
    Write Qt6 color scheme with accent color directly to /dev/shm (RAM).
    No disk writes - everything stays in memory.
    """
    accent = accent_color.lstrip('#').lower()
    shm_file = "/dev/shm/awp-qt-color.conf"
    
    scheme_content = f'''[ColorScheme]
active_colors=#ffffff, #ff2e2e2e, #ff4e4e4e, #ff3a3a3a, #ff1a1a1a, #ff2a2a2a, #ffffffff, #ffffffff, #ffffffff, #ff242424, #ff2e2e2e, #ffffffff, #{accent}, #ffffffff, #ffff6a00, #ffa70b06, #ff2e2e2e, #ffffffff, #ff3f3f36, #ffffffff, #80ffffff, #ff12608a
inactive_colors=#ffffffff, #ff2e2e2e, #ff4e4e4e, #ff3a3a3a, #ff1a1a1a, #ff2a2a2a, #ffffffff, #ffffffff, #ffffffff, #ff242424, #ff2e2e2e, #ffffffff, #{accent}, #ffffffff, #ffff6a00, #ffa70b06, #ff2e2e2e, #ffffffff, #ff3f3f36, #ffffffff, #80ffffff, #ff12608a
disabled_colors=#ff808080, #ff2e2e2e, #ff4e4e4e, #ff3a3a3a, #ff1a1a1a, #ff2a2a2a, #ff808080, #ffffffff, #ff808080, #ff242424, #ff2e2e2e, #ffffffff, #{accent}, #ff808080, #ffff6a00, #ffa70b06, #ff2e2e2e, #ffffffff, #ff3f3f36, #ffffffff, #80ffffff, #ff12608a'''
    
    with open(shm_file, 'w') as f:
        f.write(scheme_content)
    
    _printer.info(f"Qt6 accent written to RAM: {accent_color}", backend="generic")


# Run symlink setup when module loads
_ensure_qt6_symlink()


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
        _write_qt6_accent(should_accent)
        changes.append(f"qt6:{should_accent}")
    
    # Report what was applied (if anything)
    if changes:
        _printer.themes(ws_num, changes, backend="generic")
    else:
        _printer.info(f"No theme changes (WM may need manual theme tools)", backend="generic")
