#!/usr/bin/env python3
"""
XFCE Desktop Backend for AWP
Simple orchestrator - applies theme components only if they differ from config
"""

import os
import subprocess
import configparser

# ANSI Color Codes
CLR_RED    = "\033[91m"
CLR_GREEN  = "\033[92m"
CLR_YELLOW = "\033[93m"
CLR_CYAN   = "\033[96m"
CLR_RESET  = "\033[0m"
CLR_BOLD   = "\033[1m"

# XFCE specific mapping
SCALING_XFCE = {'centered': 1, 'scaled': 4, 'zoomed': 5}
SCALING_FEH = {
    'centered': '--bg-center',
    'scaled': '--bg-scale',
    'zoomed': '--bg-fill'
}

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

def xfce_set_themes(ws_num: int, config):
    """
    Simple orchestrator - applies theme components only if they differ from current.
    Handles: gtk_theme, icon_theme, cursor_theme, wm_theme
    Panel icon is handled separately by xfce_set_icon()
    """
    section = f"ws{ws_num + 1}"
    if not config.has_section(section):
        return
    
    changes = []
    
    # Get what SHOULD be from config
    should_gtk = config.get(section, 'gtk_theme', fallback=None)
    should_icon = config.get(section, 'icon_theme', fallback=None)
    should_cursor = config.get(section, 'cursor_theme', fallback=None)
    should_wm = config.get(section, 'wm_theme', fallback=None)
    
    # Check GTK theme
    if should_gtk:
        current = _get_current_value("xsettings", "/Net/ThemeName")
        if current != should_gtk:
            subprocess.run([
                "xfconf-query", "-c", "xsettings", "-p", "/Net/ThemeName", 
                "-s", should_gtk, "--create"
            ], check=False)
            changes.append("gtk")
    
    # Check Icon theme
    if should_icon:
        current = _get_current_value("xsettings", "/Net/IconThemeName")
        if current != should_icon:
            subprocess.run([
                "xfconf-query", "-c", "xsettings", "-p", "/Net/IconThemeName", 
                "-s", should_icon, "--create"
            ], check=False)
            changes.append("icons")
    
    # Check Cursor theme
    if should_cursor:
        current = _get_current_value("xsettings", "/Gtk/CursorThemeName")
        if current != should_cursor:
            subprocess.run([
                "xfconf-query", "-c", "xsettings", "-p", "/Gtk/CursorThemeName", 
                "-s", should_cursor, "--create"
            ], check=False)
            changes.append("cursor")
    
    # Check Window Manager theme
    if should_wm:
        current = _get_current_value("xfwm4", "/general/theme")
        if current != should_wm:
            subprocess.run([
                "xfconf-query", "-c", "xfwm4", "-p", "/general/theme", 
                "-s", should_wm, "--create"
            ], check=False)
            changes.append("wm")
    
    # Simple feedback if anything changed
    if changes:
        print(f"{CLR_CYAN}[AWP]{CLR_RESET} WS{ws_num + 1} themes: {CLR_GREEN}{', '.join(changes)}{CLR_RESET}")


# Keep all your existing functions exactly as they were...
def xfce_lean_mode():
    """Kills xfdesktop and prevents XFCE from restarting it."""
    try:
        subprocess.run([
            "xfconf-query", "-c", "xfce4-session", 
            "-p", "/sessions/Failsafe/Client3_Command", 
            "-t", "string", "-s", "true", "--create"
        ], stderr=subprocess.DEVNULL)
        subprocess.run(["xfdesktop", "--quit"], stderr=subprocess.DEVNULL)
        print(f"{CLR_CYAN}[AWP-XFCE]{CLR_RESET} {CLR_YELLOW}Lean Mode Activated{CLR_RESET}")
    except Exception as e:
        print(f"{CLR_RED}[AWP-XFCE] Lean Mode Error: {e}{CLR_RESET}")

def xfce_force_single_workspace_off():
    """Disable single workspace mode in XFCE."""
    subprocess.run([
        "xfconf-query", "-c", "xfce4-desktop",
        "-p", "/backdrop/single-workspace-mode",
        "--set", "false", "--create"
    ])

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

def xfce_set_wallpaper_native(ws_num: int, image_path: str, scaling: str):
    """LEGACY: Set wallpaper using XFCE's native desktop manager."""
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
        print(f"{CLR_CYAN}[AWP]{CLR_RESET} Workspace {ws_num + 1} -> {CLR_GREEN}{CLR_BOLD}{wp_name}{CLR_RESET}")
    except Exception as e:
        print(f"{CLR_YELLOW}[AWP-XFCE] feh failed, falling back to native: {e}{CLR_RESET}")
        xfce_set_wallpaper_native(ws_num, image_path, scaling)

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
        print(f"{CLR_GREEN}✓{CLR_RESET} XFCE whiskermenu icon refreshed: {CLR_CYAN}{os.path.basename(icon_path)}{CLR_RESET}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"{CLR_RED}✗ Failed to set icon: {e.stderr}{CLR_RESET}")
        return False
