#!/usr/bin/env python3
"""
GNOME Desktop Backend for AWP
Contains all GNOME-specific wallpaper and theme management functions.
Targets GNOME on X11 (Xorg session).

Workspace detection:
  1. xprop -root _NET_CURRENT_DESKTOP  (preferred — x11-utils, installed everywhere)
  2. wmctrl -d                          (fallback — reads the same EWMH property)
  3. Fallback: 0

GNOME Wayland is intentionally not supported: modern GNOME Shell does not
expose workspace state to external processes, and workspace-reactive theming
would require a custom shell extension. Use an Xorg session for full AWP
behavior on GNOME.
"""

import os
import subprocess

from core.printer import get_printer

# Get printer instance
_printer = get_printer()

# GNOME-specific scaling mapping
SCALING_GNOME = {'centered': 'centered', 'scaled': 'scaled', 'zoomed': 'zoom'}

# Cache: once we know no detection method works, stop retrying every poll
_WS_METHOD_AVAILABLE = None   # None = unknown, True/False = cached
_WS_WARNED = False            # Only warn once


# =============================================================================
# SESSION DETECTION
# =============================================================================

def _is_x11() -> bool:
    """Detect if running under real X11 (strict — not XWayland)."""
    session = os.environ.get("XDG_SESSION_TYPE", "").lower()
    if session == "x11":
        return True
    if session == "wayland":
        return False
    # Unset — trust DISPLAY only if Wayland is not present
    return bool(os.environ.get("DISPLAY")) and not os.environ.get("WAYLAND_DISPLAY")


# =============================================================================
# WORKSPACE DETECTION
# =============================================================================

def gnome_current_ws():
    """
    GNOME X11 Workspace Detection.
    Returns workspace index (0-based).
    Caches the "nothing works" state so we don't spam logs.
    """
    global _WS_METHOD_AVAILABLE, _WS_WARNED

    if _WS_METHOD_AVAILABLE is False:
        return 0

    # Only attempt detection under real X11
    if _is_x11():
        ws = _gnome_ws_via_xprop()
        if ws is not None:
            _WS_METHOD_AVAILABLE = True
            return ws

        ws = _gnome_ws_via_wmctrl()
        if ws is not None:
            _WS_METHOD_AVAILABLE = True
            return ws

    # Nothing worked — cache and warn once
    _WS_METHOD_AVAILABLE = False
    if not _WS_WARNED:
        _WS_WARNED = True
        _printer.info(
            "GNOME workspace detection unavailable on this session. "
            "Defaulting to workspace 0. AWP requires an Xorg session "
            "on GNOME for workspace-reactive theming.",
            backend="gnome"
        )
    return 0


def _gnome_ws_via_xprop():
    """
    Read _NET_CURRENT_DESKTOP via xprop.
    Output format: _NET_CURRENT_DESKTOP(CARDINAL) = 5
    Returns int or None.
    """
    try:
        result = subprocess.run(
            ["xprop", "-root", "_NET_CURRENT_DESKTOP"],
            capture_output=True, text=True, timeout=2
        )
        if result.returncode != 0:
            return None
        value = result.stdout.strip().split()[-1]
        if value.isdigit():
            return int(value)
    except Exception:
        return None
    return None


def _gnome_ws_via_wmctrl():
    """
    Read _NET_CURRENT_DESKTOP via wmctrl.
    Returns int or None.
    """
    try:
        result = subprocess.run(
            ["wmctrl", "-d"], capture_output=True, text=True, timeout=2
        )
        if result.returncode != 0:
            return None
        for line in result.stdout.splitlines():
            if "*" in line:
                return int(line.split()[0])
    except Exception:
        return None
    return None


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
        return result.stdout.strip().strip("'")
    except Exception:
        return None


# =============================================================================
# THEME ORCHESTRATOR (GTK, Icons, Cursor, Qt6)
# =============================================================================

def gnome_set_themes(ws_num: int, config):
    """
    Applies theme components only if they differ from current.
    Handles: gtk_theme, icon_theme, cursor_theme.
    GNOME doesn't have a separate WM theme (uses GTK theme).
    """
    section = f"ws{ws_num + 1}"
    if not config.has_section(section):
        return

    changes = []

    should_gtk = config.get(section, 'gtk_theme', fallback=None)
    should_icon = config.get(section, 'icon_theme', fallback=None)
    should_cursor = config.get(section, 'cursor_theme', fallback=None)

    # GTK Theme
    if should_gtk:
        current = _get_current_gsetting("org.gnome.desktop.interface", "gtk-theme")
        if current != should_gtk:
            subprocess.run([
                "gsettings", "set", "org.gnome.desktop.interface",
                "gtk-theme", should_gtk
            ], check=False)
            changes.append("gtk")

    # Icon Theme
    if should_icon:
        current = _get_current_gsetting("org.gnome.desktop.interface", "icon-theme")
        if current != should_icon:
            subprocess.run([
                "gsettings", "set", "org.gnome.desktop.interface",
                "icon-theme", should_icon
            ], check=False)
            changes.append("icons")

    # Cursor Theme
    if should_cursor:
        current = _get_current_gsetting("org.gnome.desktop.interface", "cursor-theme")
        if current != should_cursor:
            subprocess.run([
                "gsettings", "set", "org.gnome.desktop.interface",
                "cursor-theme", should_cursor
            ], check=False)
            changes.append("cursor")

    _printer.themes(ws_num, changes, backend="gnome")


# =============================================================================
# LEAN MODE
# =============================================================================

def gnome_lean_mode():
    """
    GNOME has no competing desktop manager — wallpaper is handled
    natively via gsettings. Nothing to disable for feh or other wp setter.
    """
    _printer.info("GNOME has no competing wallpaper daemon; lean mode is a no-op", backend="gnome")
    return True

# =============================================================================
# WALLPAPER FUNCTIONS
# =============================================================================

def gnome_set_wallpaper_native(ws_num: int, image_path: str, scaling: str):
    """Alias for gnome_set_wallpaper since GNOME is already native."""
    return gnome_set_wallpaper(ws_num, image_path, scaling)


def gnome_set_wallpaper(ws_num: int, image_path: str, scaling: str):
    """Set wallpaper for GNOME via gsettings."""
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
    GNOME Shell has no panel icon concept like XFCE/Cinnamon.
    Placeholder for API compatibility.
    """
    icon_name = os.path.basename(icon_path)
    _printer.info(
        f"Panel icon setting not available in GNOME (would set: {icon_name})",
        backend="gnome"
    )
    return False


# =============================================================================
# MONITOR FUNCTIONS (for API compatibility)
# =============================================================================

def gnome_get_monitors_for_workspace(ws_num: int):
    """
    GNOME handles multi-monitor wallpaper automatically.
    Placeholder for API compatibility — returns empty list.
    """
    return []


def gnome_get_current_themes():
    """Get current theme settings from GNOME via gsettings."""
    current = {
        'gtk': None,
        'icon': None,
        'cursor': None,
        'wm': None,
        'desktop': None
    }

    try:
        result = subprocess.run(
            ["gsettings", "get", "org.gnome.desktop.interface", "gtk-theme"],
            capture_output=True, text=True
        )
        if result.returncode == 0:
            current['gtk'] = result.stdout.strip().strip("'")
    except Exception:
        pass

    try:
        result = subprocess.run(
            ["gsettings", "get", "org.gnome.desktop.interface", "icon-theme"],
            capture_output=True, text=True
        )
        if result.returncode == 0:
            current['icon'] = result.stdout.strip().strip("'")
    except Exception:
        pass

    try:
        result = subprocess.run(
            ["gsettings", "get", "org.gnome.desktop.interface", "cursor-theme"],
            capture_output=True, text=True
        )
        if result.returncode == 0:
            current['cursor'] = result.stdout.strip().strip("'")
    except Exception:
        pass

    _printer.info(
        f"Current themes: GTK={current['gtk']}, Icons={current['icon']}, "
        f"Cursor={current['cursor']}",
        backend="gnome"
    )

    return current
