#!/usr/bin/env python3
"""
XFCE Desktop Backend for AWP
Simple orchestrator - applies theme components only if they differ from config
Now includes Qt6 accent color support via /dev/shm (RAM)
"""

import os
import subprocess
import configparser
import time

from core.constants import SCALING_FEH, QT6_ACCENT_SHM, QT6CT_CONF_PATH, QT6CT_COLORS_DIR
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
                _printer.info("Updated qt6ct.conf to use symlink", backend="xfce")
    
    _printer.info(f"Qt6 symlink created: {target_link} -> {shm_file}", backend="xfce")


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
    
    _printer.info(f"Qt6 accent written to RAM: {accent_color}", backend="xfce")

# Run symlink setup when module loads
_ensure_qt6_symlink()


# =============================================================================
# WORKSPACE DETECTION
# =============================================================================

def xfce_current_ws():
    """
    Standard X11 Workspace Detection.
    Provides safety and logging for the XFCE backend.
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
        _printer.error(f"X11 xprop failed: {e}", backend="xfce")
        return 0


# =============================================================================
# XFCE SETTINGS HELPERS
# =============================================================================

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


# =============================================================================
# THEME ORCHESTRATOR (GTK, Icons, Cursor, WM, Qt6)
# =============================================================================

def xfce_set_themes(ws_num: int, config):
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
    
    # ========================================================================
    # GTK Theme
    # ========================================================================
    if should_gtk:
        current = _get_current_value("xsettings", "/Net/ThemeName")
        if current != should_gtk:
            subprocess.run([
                "xfconf-query", "-c", "xsettings", "-p", "/Net/ThemeName", 
                "-s", should_gtk, "--create"
            ], check=False)
            changes.append("gtk")
    
    # ========================================================================
    # Icon Theme
    # ========================================================================
    if should_icon:
        current = _get_current_value("xsettings", "/Net/IconThemeName")
        if current != should_icon:
            subprocess.run([
                "xfconf-query", "-c", "xsettings", "-p", "/Net/IconThemeName", 
                "-s", should_icon, "--create"
            ], check=False)
            changes.append("icons")
    
    # ========================================================================
    # Cursor Theme
    # ========================================================================
    if should_cursor:
        current = _get_current_value("xsettings", "/Gtk/CursorThemeName")
        if current != should_cursor:
            subprocess.run([
                "xfconf-query", "-c", "xsettings", "-p", "/Gtk/CursorThemeName", 
                "-s", should_cursor, "--create"
            ], check=False)
            changes.append("cursor")
            cursor_changed = True
    
    # ========================================================================
    # Window Manager Theme (XFWM)
    # ========================================================================
    if should_wm:
        current = _get_current_value("xfwm4", "/general/theme")
        if current != should_wm:
            subprocess.run([
                "xfconf-query", "-c", "xfwm4", "-p", "/general/theme", 
                "-s", should_wm, "--create"
            ], check=False)
            changes.append("wm")
    
    # ========================================================================
    # Force cursor refresh if it changed (fixes stubborn apps)
    # ========================================================================
    if cursor_changed:
        # Small delay to let the setting propagate
        time.sleep(0.5)
        
        # Method 1: Tell X to reload the cursor
        subprocess.run(["xsetroot", "-cursor_name", "left_ptr"], check=False)
        
        # Method 2: Broadcast Xsettings change (more thorough)
        subprocess.run([
            "xprop", "-root", "-f", "_XSETTINGS_SETTINGS", "8s",
            "-set", "_XSETTINGS_SETTINGS", ""
        ], check=False)
        
        _printer.info("Cursor refresh triggered", backend="xfce")
    
    # ========================================================================
    # Qt6 Accent Color (via /dev/shm - RAM, no disk writes!)
    # ========================================================================
    if should_accent:
        _write_qt6_accent(should_accent)
        changes.append(f"qt6:{should_accent}")
    
    # ========================================================================
    # Report changes
    # ========================================================================
    _printer.themes(ws_num, changes, backend="xfce")


# =============================================================================
# LEAN MODE
# =============================================================================

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


# =============================================================================
# MONITOR FUNCTIONS
# =============================================================================

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


# =============================================================================
# WALLPAPER FUNCTIONS
# =============================================================================

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


# =============================================================================
# ICON FUNCTIONS
# =============================================================================

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
