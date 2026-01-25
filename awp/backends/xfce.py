#!/usr/bin/env python3
"""
XFCE Desktop Backend for AWP
Contains all XFCE-specific wallpaper and theme management functions.
"""

import os
import subprocess

# ANSI Color Codes for clean terminal output
CLR_RED    = "\033[91m"
CLR_GREEN  = "\033[92m"
CLR_YELLOW = "\033[93m"
CLR_CYAN   = "\033[96m"
CLR_RESET  = "\033[0m"
CLR_BOLD   = "\033[1m"

# XFCE specific mapping
SCALING_XFCE = {'centered': 1, 'scaled': 4, 'zoomed': 5}

# feh specific mapping
SCALING_FEH = {
    'centered': '--bg-center',
    'scaled': '--bg-scale',
    'zoomed': '--bg-fill'
}

def xfce_lean_mode():
    """
    Kills xfdesktop and prevents XFCE from restarting it.
    This creates the 'Lean Mode' for low-latency audio work.
    """
    try:
        # 1. Tell XFCE Session Manager to stop restarting xfdesktop
        subprocess.run([
            "xfconf-query", "-c", "xfce4-session", 
            "-p", "/sessions/Failsafe/Client3_Command", 
            "-t", "string", "-s", "true", "--create"
        ], stderr=subprocess.DEVNULL)
        
        # 2. Gracefully kill the current xfdesktop process
        subprocess.run(["xfdesktop", "--quit"], stderr=subprocess.DEVNULL)
        print(f"{CLR_CYAN}[AWP-XFCE]{CLR_RESET} {CLR_YELLOW}Lean Mode Activated: xfdesktop terminated.{CLR_RESET}")
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
    """
    LEGACY: Set wallpaper using XFCE's native desktop manager.
    Keeps desktop icons and right-click menu.
    """
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
    """
    NEW DEFAULT: Set wallpaper using feh (Lean Mode compatible).
    Includes terminal status feedback.
    """
    style_flag = SCALING_FEH.get(scaling, '--bg-fill')
    wp_name = os.path.basename(image_path)
    
    try:
        # The actual work
        subprocess.run(["feh", style_flag, image_path], check=True)
        
        # The Status Print
        print(f"{CLR_CYAN}[AWP]{CLR_RESET} Workspace {ws_num + 1} -> {CLR_GREEN}{CLR_BOLD}{wp_name}{CLR_RESET}")
        
    except Exception as e:
        print(f"{CLR_YELLOW}[AWP-XFCE] feh failed, falling back to native: {e}{CLR_RESET}")
        xfce_set_wallpaper_native(ws_num, image_path, scaling)

def xfce_set_icon(icon_path: str):
    try:
        subprocess.run(
            ["xfconf-query", "-c", "xfce4-panel", "-p", "/plugins/plugin-1/button-icon", "-s", icon_path, "--create", "-t", "string"],
            capture_output=True, text=True, check=True
        )
        print(f"{CLR_GREEN}✓{CLR_RESET} XFCE whiskermenu icon: {CLR_CYAN}{os.path.basename(icon_path)}{CLR_RESET}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"{CLR_RED}✗ Failed to set icon: {e.stderr}{CLR_RESET}")
        return False

def xfce_set_themes(ws_num: int, config):
    section = f"ws{ws_num + 1}"
    if not config.has_section(section):
        return
    
    icon_theme = config.get(section, 'icon_theme', fallback=None)
    gtk_theme = config.get(section, 'gtk_theme', fallback=None)
    cursor_theme = config.get(section, 'cursor_theme', fallback=None)
    wm_theme = config.get(section, 'wm_theme', fallback=None)
    
    try:
        if icon_theme:
            subprocess.run(["xfconf-query", "-c", "xsettings", "-p", "/Net/IconThemeName", "-s", icon_theme, "--create"], check=False)
        if gtk_theme:
            subprocess.run(["xfconf-query", "-c", "xsettings", "-p", "/Net/ThemeName", "-s", gtk_theme, "--create"], check=False)
        if cursor_theme:
            subprocess.run(["xfconf-query", "-c", "xsettings", "-p", "/Gtk/CursorThemeName", "-s", cursor_theme, "--create"], check=False)
        if wm_theme:
            subprocess.run(["xfconf-query", "-c", "xfwm4", "-p", "/general/theme", "-s", wm_theme, "--create"], check=False)
        
        print(f"{CLR_CYAN}[AWP]{CLR_RESET} Themes Applied for {CLR_BOLD}WS{ws_num + 1}{CLR_RESET}")
    except Exception as e:
        print(f"{CLR_RED}Error applying XFCE themes: {e}{CLR_RESET}")
