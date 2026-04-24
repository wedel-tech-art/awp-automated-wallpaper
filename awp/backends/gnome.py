#!/usr/bin/env python3
"""
GNOME Desktop Backend for AWP
Contains all GNOME-specific wallpaper and theme management functions.
Now includes Qt6 accent color support via /dev/shm (RAM)
"""

import os
import subprocess
import configparser  # ADDED for Qt6

from core.constants import SCALING_FEH
from core.printer import get_printer

# Get printer instance
_printer = get_printer()

# GNOME-specific scaling mapping
SCALING_GNOME = {'centered': 'centered', 'scaled': 'scaled', 'zoomed': 'zoom'}


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
                _printer.info("Updated qt6ct.conf to use symlink", backend="gnome")
    
    _printer.info(f"Qt6 symlink created: {target_link} -> {shm_file}", backend="gnome")


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
    
    _printer.info(f"Qt6 accent written to RAM: {accent_color}", backend="gnome")


# Run symlink setup when module loads
_ensure_qt6_symlink()


# =============================================================================
# WORKSPACE DETECTION
# =============================================================================

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


# =============================================================================
# GNOME SETTINGS HELPERS
# =============================================================================

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


# =============================================================================
# THEME ORCHESTRATOR (GTK, Icons, Cursor, Qt6)
# =============================================================================

def gnome_set_themes(ws_num: int, config):
    """
    Simple orchestrator - applies theme components only if they differ from current.
    Handles: gtk_theme, icon_theme, cursor_theme, qt6_accent
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
    should_accent = config.get(section, 'icon_color', fallback=None)
    
    # ========================================================================
    # GTK Theme
    # ========================================================================
    if should_gtk:
        current = _get_current_gsetting("org.gnome.desktop.interface", "gtk-theme")
        if current != should_gtk:
            subprocess.run([
                "gsettings", "set", "org.gnome.desktop.interface", 
                "gtk-theme", should_gtk
            ], check=False)
            changes.append("gtk")
    
    # ========================================================================
    # Icon Theme
    # ========================================================================
    if should_icon:
        current = _get_current_gsetting("org.gnome.desktop.interface", "icon-theme")
        if current != should_icon:
            subprocess.run([
                "gsettings", "set", "org.gnome.desktop.interface", 
                "icon-theme", should_icon
            ], check=False)
            changes.append("icons")
    
    # ========================================================================
    # Cursor Theme
    # ========================================================================
    if should_cursor:
        current = _get_current_gsetting("org.gnome.desktop.interface", "cursor-theme")
        if current != should_cursor:
            subprocess.run([
                "gsettings", "set", "org.gnome.desktop.interface", 
                "cursor-theme", should_cursor
            ], check=False)
            changes.append("cursor")
    
    # ========================================================================
    # Qt6 Accent Color (via /dev/shm - RAM, no disk writes!)
    # ========================================================================
    if should_accent:
        _write_qt6_accent(should_accent)
        changes.append(f"qt6:{should_accent}")
    
    # ========================================================================
    # Report changes
    # ========================================================================
    _printer.themes(ws_num, changes, backend="gnome")


# =============================================================================
# LEAN MODE
# =============================================================================

def gnome_lean_mode():
    """
    GNOME already uses native wallpaper methods.
    This is a compatibility placeholder.
    """
    _printer.info("GNOME uses native wallpaper methods", backend="gnome")


# =============================================================================
# WALLPAPER FUNCTIONS
# =============================================================================

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


# =============================================================================
# ICON FUNCTIONS
# =============================================================================

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


# =============================================================================
# MONITOR FUNCTIONS (for API compatibility)
# =============================================================================

def gnome_get_monitors_for_workspace(ws_num: int):
    """Get list of monitors (placeholder for API compatibility)."""
    return []  # GNOME handles multi-monitor automatically
