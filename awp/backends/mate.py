#!/usr/bin/env python3
"""
MATE Desktop Backend for AWP - DUAL MODE VERSION
Supports both native MATE wallpaper and feh-based lean mode.
Now includes Qt6 accent color support via /dev/shm (RAM)
"""

import os
import subprocess
import time
import configparser

from core.constants import SCALING_FEH, QT6_ACCENT_SHM, QT6CT_CONF_PATH, QT6CT_COLORS_DIR
from core.printer import get_printer

# Get printer instance
_printer = get_printer()

# MATE native scaling
SCALING_MATE = {'centered': 'centered', 'scaled': 'scaled', 'zoomed': 'zoom'}

# Simple state tracking
_lean_mode_active = False


# =============================================================================
# QT6 COLOR SCHEME SETUP (RAM-based, zero disk writes)
# =============================================================================

def _ensure_qt6_symlink():
    """
    Ensure qt6ct points to /dev/shm for zero-disk-write theming.
    Creates symlink: ~/.config/qt6ct/colors/awp.conf -> /dev/shm/awp-qt-color.conf
    """
    # Use centralized constants instead of hardcoded strings
    target_link = os.path.join(QT6CT_COLORS_DIR, "awp.conf")
    shm_file = QT6_ACCENT_SHM
    
    # Create directory if needed
    os.makedirs(QT6CT_COLORS_DIR, exist_ok=True)
    
    # Check if symlink already exists and points to the right place
    if os.path.islink(target_link):
        if os.readlink(target_link) == shm_file:
            return
    
    # Remove existing file/symlink if it exists
    if os.path.exists(target_link) or os.path.islink(target_link):
        os.remove(target_link)
    
    # Create the symlink
    os.symlink(shm_file, target_link)
    
    # Also ensure qt6ct.conf uses this symlink
    if os.path.exists(QT6CT_CONF_PATH):
        cfg = configparser.ConfigParser()
        cfg.read(QT6CT_CONF_PATH)
        if cfg.has_section('Appearance'):
            current_path = cfg.get('Appearance', 'color_scheme_path', fallback='')
            if current_path != target_link:
                cfg.set('Appearance', 'color_scheme_path', target_link)
                with open(QT6CT_CONF_PATH, 'w') as f:
                    cfg.write(f)
                _printer.info("Updated qt6ct.conf to use symlink", backend="mate")
    
    _printer.info(f"Qt6 symlink created: {target_link} -> {shm_file}", backend="mate")


def _write_qt6_accent(accent_color: str) -> None:
    """
    Write Qt6 color scheme with accent color directly to /dev/shm (RAM).
    No disk writes - everything stays in memory.
    """
    accent = accent_color.lstrip('#').lower()
    shm_file = QT6_ACCENT_SHM # Constant used here for zero-latency sync
    
    # Your scheme_content logic remains the same...
    scheme_content = f'''[ColorScheme]
active_colors=#ffffff, #ff2e2e2e, #ff4e4e4e, #ff3a3a3a, #ff1a1a1a, #ff2a2a2a, #ffffffff, #ffffffff, #ffffffff, #ff242424, #ff2e2e2e, #ffffffff, #{accent}, #ffffffff, #ffff6a00, #ffa70b06, #ff2e2e2e, #ffffffff, #ff3f3f36, #ffffffff, #80ffffff, #ff12608a
inactive_colors=#ffffffff, #ff2e2e2e, #ff4e4e4e, #ff3a3a3a, #ff1a1a1a, #ff2a2a2a, #ffffffff, #ffffffff, #ffffffff, #ff242424, #ff2e2e2e, #ffffffff, #{accent}, #ffffffff, #ffff6a00, #ffa70b06, #ff2e2e2e, #ffffffff, #ff3f3f36, #ffffffff, #80ffffff, #ff12608a
disabled_colors=#ff808080, #ff2e2e2e, #ff4e4e4e, #ff3a3a3a, #ff1a1a1a, #ff2a2a2a, #ff808080, #ffffffff, #ff808080, #ff242424, #ff2e2e2e, #ffffffff, #{accent}, #ff808080, #ffff6a00, #ffa70b06, #ff2e2e2e, #ffffffff, #ff3f3f36, #ffffffff, #80ffffff, #ff12608a'''
    
    with open(shm_file, 'w') as f:
        f.write(scheme_content)
    
    _printer.info(f"Qt6 accent written to RAM: {accent_color}", backend="mate")

# Run symlink setup when module loads
_ensure_qt6_symlink()


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
    Handles: gtk_theme, icon_theme, cursor_theme, wm_theme, qt6_accent
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
    should_wm = config.get(section, 'wm_theme', fallback=None)
    should_accent = config.get(section, 'icon_color', fallback=None)
    
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
            cursor_changed = True
    
    # Force cursor refresh if it changed (fixes stubborn apps)
    if cursor_changed:
        time.sleep(0.5)
        subprocess.run(["xsetroot", "-cursor_name", "left_ptr"], check=False)
        subprocess.run([
            "xprop", "-root", "-f", "_XSETTINGS_SETTINGS", "8s",
            "-set", "_XSETTINGS_SETTINGS", ""
        ], check=False)
        _printer.info("Cursor refresh triggered", backend="mate")
    
    # Check Window Manager theme (Marco)
    if should_wm:
        current = _get_current_gsetting("org.mate.Marco.general", "theme")
        if current != should_wm:
            subprocess.run([
                "gsettings", "set", "org.mate.Marco.general", 
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
