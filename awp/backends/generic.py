#!/usr/bin/env python3
"""
Hybrid Generic Backend for AWP
Optimized for Openbox sessions running on an XFCE-based system.
Uses XFCE's logic for themes/icons but universal tools for the rest.
"""

import os
import subprocess

# Standard owstudios Status Colors
CLR_RED    = "\033[91m"
CLR_GREEN  = "\033[92m"
CLR_YELLOW = "\033[93m"
CLR_CYAN   = "\033[96m"
CLR_RESET  = "\033[0m"
CLR_BOLD   = "\033[1m"

def generic_lean_mode():
    """Ensures xfdesktop is terminated for the Openbox session."""
    try:
        subprocess.run(["xfdesktop", "--quit"], stderr=subprocess.DEVNULL)
        print(f"{CLR_CYAN}[AWP-GENERIC]{CLR_RESET} {CLR_GREEN}Lean Mode: Active (Environment Cleaned){CLR_RESET}")
    except Exception:
        pass

def generic_force_single_workspace_off():
    """No-op for Openbox."""
    pass

def generic_configure_screen_blanking(timeout_seconds: int):
    """Universal X11 screen blanking control."""
    try:
        if timeout_seconds == 0:
            subprocess.run(["xset", "s", "off", "-dpms"], check=False)
            print(f"{CLR_CYAN}[AWP]{CLR_RESET} Screen blanking: {CLR_RED}DISABLED{CLR_RESET}")
        else:
            subprocess.run(["xset", "s", str(timeout_seconds)], check=False)
            subprocess.run(["xset", "+dpms", "dpms", str(timeout_seconds), str(timeout_seconds), str(timeout_seconds)], check=False)
            print(f"{CLR_CYAN}[AWP]{CLR_RESET} Screen blanking: {CLR_GREEN}{timeout_seconds}s{CLR_RESET}")
    except Exception as e:
        print(f"{CLR_RED}[AWP-GENERIC] Blanking Error: {e}{CLR_RESET}")

def generic_set_wallpaper(ws_num: int, image_path: str, scaling: str):
    """Set wallpaper using feh for Openbox compatibility."""
    scaling_map = {'centered': '--bg-center', 'scaled': '--bg-scale', 'zoomed': '--bg-fill'}
    style_flag = scaling_map.get(scaling, '--bg-fill')
    wp_name = os.path.basename(image_path)
    
    try:
        subprocess.run(["feh", style_flag, image_path], check=True)
        print(f"{CLR_CYAN}[AWP]{CLR_RESET} Workspace {ws_num + 1} -> {CLR_GREEN}{CLR_BOLD}{wp_name}{CLR_RESET}")
    except Exception as e:
        print(f"{CLR_RED}[AWP-GENERIC] feh failed: {e}{CLR_RESET}")

def generic_set_icon(icon_path: str):
    """Smart icon switcher for tint2 or xfce4-panel in Openbox."""
    icon_name = os.path.basename(icon_path)
    
    # Check for xfce4-panel
    if subprocess.run(["pgrep", "xfce4-panel"], capture_output=True).returncode == 0:
        subprocess.run(["xfconf-query", "-c", "xfce4-panel", "-p", "/plugins/plugin-1/button-icon", "-s", icon_path], check=False)
        print(f"{CLR_GREEN}✓{CLR_RESET} XFCE Panel Icon: {CLR_CYAN}{icon_name}{CLR_RESET}")
        return

    # Check for tint2
    tint2_conf = os.path.expanduser("~/.config/tint2/tint2rc")
    if os.path.exists(tint2_conf):
        subprocess.run(["sed", "-i", f"s|launcher_item_app = .*|launcher_item_app = {icon_path}|", tint2_conf])
        subprocess.run(["killall", "-SIGUSR1", "tint2"], stderr=subprocess.DEVNULL)
        print(f"{CLR_GREEN}✓{CLR_RESET} tint2 Panel Icon: {CLR_CYAN}{icon_name}{CLR_RESET}")

def generic_set_themes(ws_num: int, config):
    """Hybrid Theme Applier (xfconf + Openbox Refresh)."""
    section = f"ws{ws_num + 1}"
    if not config.has_section(section): return

    gtk = config.get(section, 'gtk_theme', fallback=None)
    icons = config.get(section, 'icon_theme', fallback=None)

    try:
        if gtk:
            subprocess.run(["xfconf-query", "-c", "xsettings", "-p", "/Net/ThemeName", "-s", gtk], check=False)
        if icons:
            subprocess.run(["xfconf-query", "-c", "xsettings", "-p", "/Net/IconThemeName", "-s", icons], check=False)

        # Signal Openbox to update borders
        subprocess.run(["openbox", "--reconfigure"], stderr=subprocess.DEVNULL)
        print(f"{CLR_CYAN}[AWP]{CLR_RESET} Generic Themes applied for {CLR_BOLD}WS{ws_num + 1}{CLR_RESET}")
    except Exception as e:
        print(f"{CLR_RED}Error applying Generic themes: {e}{CLR_RESET}")
