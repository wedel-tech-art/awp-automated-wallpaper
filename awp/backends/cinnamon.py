#!/usr/bin/env python3
"""
Cinnamon Desktop Backend for AWP
Contains all Cinnamon-specific wallpaper and theme management functions.
Now includes Qt6 accent color support via /dev/shm (RAM)
"""

import os
import subprocess
import json
import configparser

from core.constants import SCALING_FEH
from core.printer import get_printer

# Get printer instance
_printer = get_printer()

# Cinnamon-specific scaling mapping
SCALING_CINNAMON = {'centered': 'centered', 'scaled': 'scaled', 'zoomed': 'zoom'}


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
                _printer.info("Updated qt6ct.conf to use symlink", backend="cinnamon")
    
    _printer.info(f"Qt6 symlink created: {target_link} -> {shm_file}", backend="cinnamon")


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
    
    _printer.info(f"Qt6 accent written to RAM: {accent_color}", backend="cinnamon")


# Run symlink setup when module loads
_ensure_qt6_symlink()


def cinnamon_current_ws():
    """
    Cinnamon Workspace Detection via D-Bus.
    Works on X11 and is the 'Passport' for Cinnamon's Wayland future.
    """
    try:
        import subprocess
        # We ask Cinnamon directly for the active workspace index
        cmd = [
            "dbus-send", "--print-reply", "--dest=org.Cinnamon",
            "/org/Cinnamon", "org.freedesktop.DBus.Properties.Get",
            "string:org.Cinnamon", "string:active-workspace-index"
        ]
        
        result = subprocess.check_output(cmd, text=True)
        
        # Extract the integer from the reply (e.g., variant int32 1)
        ws_num = result.split()[-1]
        return int(ws_num)
        
    except Exception as e:
        # Fallback to xprop if D-Bus is stubborn on older Mint versions
        try:
            ws_num = subprocess.check_output(
                ["xprop", "-root", "_NET_CURRENT_DESKTOP"], 
                text=True).strip().split()[-1]
            return int(ws_num)
        except:
            _printer.error(f"Cinnamon detection failed: {e}", backend="cinnamon")
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


def cinnamon_set_themes(ws_num: int, config):
    """
    Simple orchestrator - applies theme components only if they differ from current.
    Handles: gtk_theme, icon_theme, cursor_theme, desktop_theme, wm_theme, qt6_accent
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
    should_desktop = config.get(section, 'desktop_theme', fallback=None)
    should_wm = config.get(section, 'wm_theme', fallback=None)
    should_accent = config.get(section, 'icon_color', fallback=None)
    
    # Check GTK theme
    if should_gtk:
        current = _get_current_gsetting("org.cinnamon.desktop.interface", "gtk-theme")
        if current != should_gtk:
            subprocess.run([
                "gsettings", "set", "org.cinnamon.desktop.interface", 
                "gtk-theme", should_gtk
            ], check=False)
            changes.append("gtk")
    
    # Check Icon theme
    if should_icon:
        current = _get_current_gsetting("org.cinnamon.desktop.interface", "icon-theme")
        if current != should_icon:
            subprocess.run([
                "gsettings", "set", "org.cinnamon.desktop.interface", 
                "icon-theme", should_icon
            ], check=False)
            changes.append("icons")
    
    # Check Cursor theme
    if should_cursor:
        current = _get_current_gsetting("org.cinnamon.desktop.interface", "cursor-theme")
        if current != should_cursor:
            subprocess.run([
                "gsettings", "set", "org.cinnamon.desktop.interface", 
                "cursor-theme", should_cursor
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
        _printer.info("Cursor refresh triggered", backend="cinnamon")
    
    # Check Desktop theme (Cinnamon shell theme)
    if should_desktop:
        current = _get_current_gsetting("org.cinnamon.theme", "name")
        if current != should_desktop:
            subprocess.run([
                "gsettings", "set", "org.cinnamon.theme", 
                "name", should_desktop
            ], check=False)
            changes.append("desktop")
    
    # Check Window Manager theme
    if should_wm:
        current = _get_current_gsetting("org.cinnamon.desktop.wm.preferences", "theme")
        if current != should_wm:
            subprocess.run([
                "gsettings", "set", "org.cinnamon.desktop.wm.preferences", 
                "theme", should_wm
            ], check=False)
            changes.append("wm")
    
    # ========================================================================
    # Qt6 Accent Color (via /dev/shm - RAM, no disk writes!)
    # ========================================================================
    if should_accent:
        _write_qt6_accent(should_accent)
        changes.append(f"qt6:{should_accent}")
    
    # Use printer with explicit backend
    _printer.themes(ws_num, changes, backend="cinnamon")


def cinnamon_lean_mode():
    """
    Cinnamon already uses native wallpaper methods.
    This is a compatibility placeholder.
    """
    _printer.info("Cinnamon uses native wallpaper methods", backend="cinnamon")


def cinnamon_set_wallpaper_native(ws_num: int, image_path: str, scaling: str):
    """
    Alias for cinnamon_set_wallpaper since Cinnamon is already native.
    """
    return cinnamon_set_wallpaper(ws_num, image_path, scaling)


def cinnamon_set_wallpaper(ws_num: int, image_path: str, scaling: str):
    """Set wallpaper for Cinnamon with specified scaling."""
    try:
        uri = f"file://{os.path.abspath(image_path)}"
        style_val = SCALING_CINNAMON.get(scaling, 'zoom')
        wp_name = os.path.basename(image_path)
        
        # Set wallpaper properties
        subprocess.run([
            "gsettings", "set", "org.cinnamon.desktop.background", 
            "picture-uri", uri
        ], check=True)
        subprocess.run([
            "gsettings", "set", "org.cinnamon.desktop.background", 
            "picture-options", style_val
        ], check=True)
        
        # Use printer for feedback
        _printer.wallpaper(ws_num, wp_name, backend="cinnamon")
        
    except subprocess.CalledProcessError as e:
        _printer.error(f"Failed to set wallpaper via gsettings: {e}", backend="cinnamon")
    except Exception as e:
        _printer.error(f"Unexpected error: {e}", backend="cinnamon")


def cinnamon_set_icon(icon_path: str):
    """
    Set the Cinnamon Menu icon.
    
    Args:
        icon_path (str): Full path to icon image file
    """
    config_file = os.path.expanduser("~/.config/cinnamon/spices/menu@cinnamon.org/0.json")
    
    try:
        if not os.path.exists(config_file):
            _printer.warning(f"Menu config not found at {config_file}", backend="cinnamon")
            return False
        
        with open(config_file, "r") as f:
            data = json.load(f)
        
        data["menu-icon"]["value"] = icon_path
        
        with open(config_file, "w") as f:
            json.dump(data, f, indent=4)
        
        icon_name = os.path.basename(icon_path)
        _printer.icon(icon_name, backend="cinnamon")
        return True
        
    except json.JSONDecodeError as e:
        _printer.error(f"Failed to parse menu config: {e}", backend="cinnamon")
        return False
    except Exception as e:
        _printer.error(f"Error setting Cinnamon menu icon: {e}", backend="cinnamon")
        return False


# Optional: Add helper function to get monitors if needed for multi-monitor setups
def cinnamon_get_monitors_for_workspace(ws_num: int):
    """Get list of monitors (placeholder for API compatibility)."""
    return []  # Cinnamon handles multi-monitor automatically
