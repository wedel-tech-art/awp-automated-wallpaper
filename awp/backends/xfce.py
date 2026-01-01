#!/usr/bin/env python3
"""
XFCE Desktop Backend for AWP
Optimized for XFCE 4.16+ and X11 sessions.
"""

import subprocess
import logging

logger = logging.getLogger("AWP.XFCE")

SCALING_XFCE = {'centered': 1, 'scaled': 4, 'zoomed': 5}

def _xfconf_set(channel: str, prop: str, value: str, prop_type: str = "string"):
    """Internal helper to set xfconf properties safely."""
    try:
        # Use --create as a default to ensure the property exists
        subprocess.run([
            "xfconf-query", "-c", channel, "-p", prop, 
            "--set", str(value), "--create"
        ], check=True, capture_output=True)
    except subprocess.CalledProcessError as e:
        logger.error(f"Xfconf error on {prop}: {e}")

def xfce_force_single_workspace_off():
    """Disable single workspace mode to allow unique wallpapers per desktop."""
    _xfconf_set("xfce4-desktop", "/backdrop/single-workspace-mode", "false", "bool")

def xfce_configure_screen_blanking(timeout_seconds: int):
    """Manages DPMS and X11 screen blanking."""
    try:
        if timeout_seconds == 0:
            subprocess.run(["xset", "s", "off"], check=False)
            subprocess.run(["xset", "-dpms"], check=False)
            logger.info("Screen blanking disabled via xset.")
        else:
            subprocess.run(["xset", "s", str(timeout_seconds)], check=False)
            subprocess.run(["xset", "+dpms"], check=False)
            subprocess.run([
                "xset", "dpms", str(timeout_seconds), 
                str(timeout_seconds), str(timeout_seconds)
            ], check=False)
            logger.info(f"Screen blanking set to {timeout_seconds}s")
    except Exception as e:
        logger.error(f"Failed to set xset blanking: {e}")

def xfce_get_monitors(ws_num: int):
    """Finds all monitor properties for a specific workspace."""
    try:
        props = subprocess.check_output(
            ["xfconf-query", "-c", "xfce4-desktop", "-l"], text=True
        ).splitlines()
        
        monitors = []
        target = f"/workspace{ws_num}/last-image"
        for p in props:
            if target in p:
                parts = p.split("/")
                # Pattern matches /backdrop/screen0/monitorHDMI-1/...
                if len(parts) >= 4 and "monitor" in parts[3]:
                    monitors.append(parts[3])
        return sorted(set(monitors))
    except Exception:
        return ["monitor0"] # Fallback

def xfce_set_wallpaper(ws_num: int, image_path: str, scaling: str):
    """Applies wallpaper and scaling style to all monitors on a workspace."""
    style_code = SCALING_XFCE.get(scaling, 5)
    monitors = xfce_get_monitors(ws_num)
    
    for mon in monitors:
        base_path = f"/backdrop/screen0/{mon}/workspace{ws_num}"
        _xfconf_set("xfce4-desktop", f"{base_path}/last-image", image_path)
        _xfconf_set("xfce4-desktop", f"{base_path}/image-style", style_code)
    
    # Force XFCE to repaint the desktop
    subprocess.run(["xfdesktop", "--reload"], check=False)

def xfce_set_icon(icon_path: str):
    """Whisker Menu icon updates are currently disabled for stability."""
    logger.debug(f"XFCE Icon update requested but skipped: {icon_path}")
    pass

def xfce_set_themes(ws_num: int, config):
    """Dynamically switch GTK, Icon, and Window themes per workspace."""
    section = f"ws{ws_num + 1}"
    
    # Map config keys to XFCE Xfconf properties
    theme_map = {
        'icon_theme': ("xsettings", "/Net/IconThemeName"),
        'gtk_theme': ("xsettings", "/Net/ThemeName"),
        'cursor_theme': ("xsettings", "/Gtk/CursorThemeName"),
        'wm_theme': ("xfwm4", "/general/theme")
    }

    for cfg_key, (channel, prop) in theme_map.items():
        val = config.get(section, cfg_key, fallback=None)
        if val:
            _xfconf_set(channel, prop, val)
            logger.info(f"Applied {cfg_key}: {val}")
