#!/usr/bin/env python3
"""
XFCE Desktop Backend for AWP
Contains all XFCE-specific wallpaper and theme management functions.
"""

import os
import subprocess

SCALING_XFCE = {'centered': 1, 'scaled': 4, 'zoomed': 5}

def xfce_force_single_workspace_off():
    """Disable single workspace mode in XFCE."""
    subprocess.run([
        "xfconf-query", "-c", "xfce4-desktop",
        "-p", "/backdrop/single-workspace-mode",
        "--set", "false", "--create"
    ])

def xfce_configure_screen_blanking(timeout_seconds: int):
    """
    Configure screen blanking for XFCE/X11 sessions.
    
    Args:
        timeout_seconds (int): Time in seconds before screen blanks (0 = disable)
    """
    if timeout_seconds == 0:
        # Explicitly disable all blanking
        subprocess.run(["xset", "s", "off"], check=False)
        subprocess.run(["xset", "-dpms"], check=False)
        print(f"[AWP] Screen blanking explicitly disabled")
    else:
        # Enable and configure blanking
        subprocess.run(["xset", "s", str(timeout_seconds)], check=False)
        subprocess.run(["xset", "+dpms"], check=False)
        subprocess.run(["xset", "dpms", str(timeout_seconds), str(timeout_seconds), str(timeout_seconds)], check=False)
        print(f"[AWP] Screen blanking set to {timeout_seconds}s")

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

def xfce_set_wallpaper(ws_num: int, image_path: str, scaling: str):
    """Set wallpaper for XFCE workspace with specified scaling."""
    style_code = SCALING_XFCE.get(scaling, 5)
    for mon in xfce_get_monitors_for_workspace(ws_num):
        subprocess.run([
            "xfconf-query",
            "--channel", "xfce4-desktop",
            "--property", f"/backdrop/screen0/{mon}/workspace{ws_num}/last-image",
            "--set", image_path,
            "--create"
        ])
        subprocess.run([
            "xfconf-query",
            "--channel", "xfce4-desktop", 
            "--property", f"/backdrop/screen0/{mon}/workspace{ws_num}/image-style",
            "--set", str(style_code),
            "--create"
        ])
    subprocess.run(["xfdesktop", "--reload"])


def xfce_set_icon(icon_path: str):
    try:
        result = subprocess.run(
            ["xfconf-query", "-c", "xfce4-panel", "-p", "/plugins/plugin-1/button-icon", "-s", icon_path, "--create", "-t", "string"],
            capture_output=True,
            text=True,
            check=True
        )
        print(f"✓ XFCE whiskermenu icon set to: {icon_path}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ Failed to set icon: {e.stderr}")
        return False


def xfce_set_themes(ws_num: int, config):

    section = f"ws{ws_num + 1}"
    
    if not config.has_section(section):
        print(f"No theme config found for {section}")
        return
    
    # Get theme settings with fallbacks
    icon_theme = config.get(section, 'icon_theme', fallback=None)
    gtk_theme = config.get(section, 'gtk_theme', fallback=None)
    cursor_theme = config.get(section, 'cursor_theme', fallback=None)
    wm_theme = config.get(section, 'wm_theme', fallback=None)
    
    # Apply themes if they exist in config
    try:
        if icon_theme:
            # Check if property exists
            result = subprocess.run(
                ["xfconf-query", "-c", "xsettings", "-p", "/Net/IconThemeName"],
                capture_output=True, text=True
            )
            if result.returncode == 0:
                # Property exists - set without --create
                subprocess.run(
                    ["xfconf-query", "-c", "xsettings", "-p", "/Net/IconThemeName", "--set", icon_theme],
                    check=True
                )
            else:
                # Property doesn't exist - create it
                subprocess.run(
                    ["xfconf-query", "-c", "xsettings", "-p", "/Net/IconThemeName", "--set", icon_theme, "--create"],
                    check=True
                )
            print(f"✓ XFCE icon theme: {icon_theme}")
        
        # Repeat the same pattern for other themes...
        if gtk_theme:
            result = subprocess.run(
                ["xfconf-query", "-c", "xsettings", "-p", "/Net/ThemeName"],
                capture_output=True, text=True
            )
            if result.returncode == 0:
                subprocess.run(
                    ["xfconf-query", "-c", "xsettings", "-p", "/Net/ThemeName", "--set", gtk_theme],
                    check=True
                )
            else:
                subprocess.run(
                    ["xfconf-query", "-c", "xsettings", "-p", "/Net/ThemeName", "--set", gtk_theme, "--create"],
                    check=True
                )
            print(f"✓ XFCE GTK theme: {gtk_theme}")
        
        if cursor_theme:
            result = subprocess.run(
                ["xfconf-query", "-c", "xsettings", "-p", "/Gtk/CursorThemeName"],
                capture_output=True, text=True
            )
            if result.returncode == 0:
                subprocess.run(
                    ["xfconf-query", "-c", "xsettings", "-p", "/Gtk/CursorThemeName", "--set", cursor_theme],
                    check=True
                )
            else:
                subprocess.run(
                    ["xfconf-query", "-c", "xsettings", "-p", "/Gtk/CursorThemeName", "--set", cursor_theme, "--create"],
                    check=True
                )
            print(f"✓ XFCE cursor theme: {cursor_theme}")
        
        if wm_theme:
            result = subprocess.run(
                ["xfconf-query", "-c", "xfwm4", "-p", "/general/theme"],
                capture_output=True, text=True
            )
            if result.returncode == 0:
                subprocess.run(
                    ["xfconf-query", "-c", "xfwm4", "-p", "/general/theme", "--set", wm_theme],
                    check=True
                )
            else:
                subprocess.run(
                    ["xfconf-query", "-c", "xfwm4", "-p", "/general/theme", "--set", wm_theme, "--create"],
                    check=True
                )
            print(f"✓ XFCE window theme: {wm_theme}")
        
        print(f"Applied XFCE themes for workspace {ws_num + 1}")
        
    except subprocess.CalledProcessError as e:
        print(f"Error applying XFCE themes: {e}")
