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
import time
from backends import ensure_qt6_kde_symlinks, write_qt6_kde_accent
from core.printer import get_printer

ensure_qt6_kde_symlinks()

# Get printer instance
_printer = get_printer()

# Cinnamon-specific scaling mapping
SCALING_CINNAMON = {'centered': 'centered', 'scaled': 'scaled', 'zoomed': 'zoom'}


def cinnamon_current_ws():
    """
    Standard X11 Workspace Detection via xprop for Cinnamon.
    Clean, reliable, and avoids invalid D-Bus property errors.
    """
    try:
        ws_num = subprocess.check_output(
            ["xprop", "-root", "_NET_CURRENT_DESKTOP"], 
            text=True
        ).strip().split()[-1]
        
        return int(ws_num)
    except Exception as e:
        _printer.error(f"Cinnamon workspace detection failed: {e}", backend="cinnamon")
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
    
    # Check Cursor theme - IMPROVED with XFCE approach
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
        # Small delay to let the setting propagate
        time.sleep(0.5)
        
        # Method 1: Tell X to reload the cursor (same as XFCE)
        subprocess.run(["xsetroot", "-cursor_name", "left_ptr"], check=False)
        
        # Method 2: Broadcast Xsettings change (same as XFCE)
        subprocess.run([
            "xprop", "-root", "-f", "_XSETTINGS_SETTINGS", "8s",
            "-set", "_XSETTINGS_SETTINGS", ""
        ], check=False)
        
        # Method 3: Cinnamon-specific - restart cinnamon-settings-daemon
        #subprocess.run(["pkill", "-HUP", "cinnamon-settings-daemon"], check=False)
        
        # Method 4: Force GTK to reload via cursor size toggle
        current_size = subprocess.run(
            ["gsettings", "get", "org.cinnamon.desktop.interface", "cursor-size"],
            capture_output=True, text=True
        ).stdout.strip()
        
        if current_size:
            # Change size slightly to force reload
            new_size = int(current_size) + 1 if current_size.isdigit() else 25
            subprocess.run([
                "gsettings", "set", "org.cinnamon.desktop.interface", 
                "cursor-size", str(new_size)
            ], check=False)
            time.sleep(0.1)
            # Restore original size
            subprocess.run([
                "gsettings", "set", "org.cinnamon.desktop.interface", 
                "cursor-size", current_size
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
    
    # Qt6 Accent Color
    if should_accent:
        write_qt6_kde_accent(should_accent)
        changes.append(f"qt6:{should_accent}")
    
    # Report changes
    _printer.themes(ws_num, changes, backend="cinnamon")

def cinnamon_lean_mode():
    """
    Cinnamon uses native gsettings for wallpapers, 
    so lean mode acts as a clean bypass.
    """
    _printer.lean_mode("Bypassed (Native Engine Active)", backend="cinnamon")


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



def cinnamon_get_current_themes():
    """Get current theme settings from Cinnamon."""
    current = {
        'gtk': None,
        'icon': None,
        'cursor': None,
        'wm': None,
        'desktop': None
    }
    
    try:
        result = subprocess.run(
            ["gsettings", "get", "org.cinnamon.desktop.interface", "gtk-theme"],
            capture_output=True, text=True
        )
        if result.returncode == 0:
            current['gtk'] = result.stdout.strip().strip("'")
    except:
        pass
    
    try:
        result = subprocess.run(
            ["gsettings", "get", "org.cinnamon.desktop.interface", "icon-theme"],
            capture_output=True, text=True
        )
        if result.returncode == 0:
            current['icon'] = result.stdout.strip().strip("'")
    except:
        pass
    
    try:
        result = subprocess.run(
            ["gsettings", "get", "org.cinnamon.desktop.interface", "cursor-theme"],
            capture_output=True, text=True
        )
        if result.returncode == 0:
            current['cursor'] = result.stdout.strip().strip("'")
    except:
        pass
    
    try:
        result = subprocess.run(
            ["gsettings", "get", "org.cinnamon.desktop.wm.preferences", "theme"],
            capture_output=True, text=True
        )
        if result.returncode == 0:
            current['wm'] = result.stdout.strip().strip("'")
    except:
        pass
    
    try:
        result = subprocess.run(
            ["gsettings", "get", "org.cinnamon.theme", "name"],
            capture_output=True, text=True
        )
        if result.returncode == 0:
            current['desktop'] = result.stdout.strip().strip("'")
    except:
        pass
    
    _printer.info(f"Current themes: GTK={current['gtk']}, Icons={current['icon']}, Cursor={current['cursor']}", backend="cinnamon")
    
    return current
