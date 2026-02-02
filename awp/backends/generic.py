#!/usr/bin/env python3
"""
Generic Backend for AWP
For any window manager without desktop environment dependencies.
Uses feh for wallpapers, minimal theme support.
"""

import os
import subprocess

# ANSI Colors
CLR_RED    = "\033[91m"
CLR_GREEN  = "\033[92m"
CLR_YELLOW = "\033[93m"
CLR_CYAN   = "\033[96m"
CLR_RESET  = "\033[0m"
CLR_BOLD   = "\033[1m"

def generic_lean_mode():
    """
    Generic lean mode - nothing to kill, already using feh.
    """
    print(f"{CLR_CYAN}[AWP-Generic]{CLR_RESET} {CLR_GREEN}Already lean (feh only){CLR_RESET}")

def generic_force_single_workspace_off():
    """
    No-op for generic WM - workspace handling is WM-specific.
    """
    pass

def generic_set_wallpaper(ws_num: int, image_path: str, scaling: str):
    """
    Set wallpaper using feh (works with any WM).
    """
    scaling_map = {
        'centered': '--bg-center',
        'scaled': '--bg-scale',
        'zoomed': '--bg-fill'
    }
    style_flag = scaling_map.get(scaling, '--bg-fill')
    wp_name = os.path.basename(image_path)
    
    try:
        subprocess.run(["feh", style_flag, image_path], check=True)
        print(f"{CLR_CYAN}[AWP-Generic]{CLR_RESET} WS{ws_num + 1} → "
              f"{CLR_GREEN}{CLR_BOLD}{wp_name}{CLR_RESET}")
    except Exception as e:
        print(f"{CLR_RED}[AWP-Generic] feh failed: {e}{CLR_RESET}")

def generic_set_icon(icon_path: str):
    """
    Minimal icon support - tries common panels.
    """
    icon_name = os.path.basename(icon_path)
    
    # Try tint2 (common with minimal WMs)
    tint2_conf = os.path.expanduser("~/.config/tint2/tint2rc")
    if os.path.exists(tint2_conf):
        try:
            subprocess.run([
                "sed", "-i",
                f"s|^launcher_item_app = .*|launcher_item_app = {icon_path}|",
                tint2_conf
            ], check=True)
            subprocess.run(["pkill", "-SIGUSR1", "tint2"], 
                         stderr=subprocess.DEVNULL, check=False)
            print(f"{CLR_GREEN}✓{CLR_RESET} tint2: {CLR_CYAN}{icon_name}{CLR_RESET}")
            return
        except:
            pass
    
    print(f"{CLR_YELLOW}[AWP-Generic] No panel found for icons{CLR_RESET}")

def generic_set_themes(ws_num: int, config):
    """
    Basic theme support using gsettings (GNOME/GTK) or lxappearance.
    """
    section = f"ws{ws_num + 1}"
    if not config.has_section(section):
        return
    
    gtk_theme = config.get(section, 'gtk_theme', fallback=None)
    icon_theme = config.get(section, 'icon_theme', fallback=None)
    
    applied = []
    
    # Try gsettings (works on most GTK systems)
    if gtk_theme:
        try:
            subprocess.run([
                "gsettings", "set",
                "org.gnome.desktop.interface", "gtk-theme",
                gtk_theme
            ], check=True)
            applied.append(f"GTK: {gtk_theme}")
        except:
            pass
    
    if icon_theme:
        try:
            subprocess.run([
                "gsettings", "set",
                "org.gnome.desktop.interface", "icon-theme",
                icon_theme
            ], check=True)
            applied.append(f"Icons: {icon_theme}")
        except:
            pass
    
    if applied:
        print(f"{CLR_CYAN}[AWP-Generic]{CLR_RESET} Themes: {', '.join(applied)}")
    else:
        print(f"{CLR_YELLOW}[AWP-Generic] No theme support (install lxappearance){CLR_RESET}")

def generic_wallpaper_native(ws_num: int, image_path: str, scaling: str):
    """
    No native method - always uses feh.
    """
    generic_set_wallpaper(ws_num, image_path, scaling)
