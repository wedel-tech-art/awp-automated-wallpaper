#!/usr/bin/env python3
"""
Qtile + XFCE Hybrid Backend for AWP
For Qtile window manager with XFCE theming components.
Uses feh for wallpapers, xfsettingsd for theming.
"""
import os
import subprocess

# ANSI Color Codes
CLR_RED    = "\033[91m"
CLR_GREEN  = "\033[92m"
CLR_YELLOW = "\033[93m"
CLR_CYAN   = "\033[96m"
CLR_RESET  = "\033[0m"
CLR_BOLD   = "\033[1m"

def qtile_xfce_lean_mode():
    """
    Kills xfdesktop and prevents XFCE from restarting it.
    """
    try:
        # 1. Stop XFCE session manager from restarting xfdesktop
        subprocess.run([
            "xfconf-query", "-c", "xfce4-session", 
            "-p", "/sessions/Failsafe/Client3_Command", 
            "-t", "string", "-s", "true", "--create"
        ], stderr=subprocess.DEVNULL)
        
        # 2. Gracefully kill current xfdesktop
        subprocess.run(["xfdesktop", "--quit"], stderr=subprocess.DEVNULL)
        
        print(f"{CLR_CYAN}[AWP-Qtile+XFCE]{CLR_RESET} {CLR_GREEN}Lean Mode: xfdesktop terminated{CLR_RESET}")
        
    except Exception as e:
        print(f"{CLR_RED}[AWP-Qtile+XFCE] Lean Mode Error: {e}{CLR_RESET}")

def qtile_xfce_force_single_workspace_off():
    """
    Disable single workspace mode in XFCE.
    """
    try:
        subprocess.run([
            "xfconf-query", "-c", "xfce4-desktop",
            "-p", "/backdrop/single-workspace-mode",
            "--set", "false", "--create"
        ], stderr=subprocess.DEVNULL)
    except Exception:
        pass 

def qtile_xfce_set_wallpaper(ws_num: int, image_path: str, scaling: str):
    """
    Set wallpaper using feh.
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
        print(f"{CLR_CYAN}[AWP]{CLR_RESET} Workspace {ws_num + 1} → "
              f"{CLR_GREEN}{CLR_BOLD}{wp_name}{CLR_RESET}")
        
    except Exception as e:
        print(f"{CLR_RED}[AWP-Qtile+XFCE] feh failed: {e}{CLR_RESET}")

def qtile_xfce_set_icon(icon_path: str):
    """
    Qtile + XFCE Hybrid Icon Management.
    Silent version: No tint2 sabotage.
    """
    try:
        if subprocess.run(["pgrep", "-x", "xfce4-panel"], capture_output=True).returncode == 0:
            subprocess.run([
                "xfconf-query", "-c", "xfce4-panel",
                "-p", "/plugins/plugin-1/button-icon",
                "-s", icon_path, "--create", "-t", "string"
            ], check=False)
    except Exception:
        pass

    return True

def qtile_xfce_set_themes(ws_num: int, config):
    """
    Apply GTK/Icons/Cursors via xfsettingsd.
    """
    section = f"ws{ws_num + 1}"
    if not config.has_section(section): 
        return
    
    gtk_theme = config.get(section, 'gtk_theme', fallback=None)
    icon_theme = config.get(section, 'icon_theme', fallback=None)
    cursor_theme = config.get(section, 'cursor_theme', fallback=None)
    
    try:
        if gtk_theme:
            subprocess.run([
                "xfconf-query", "-c", "xsettings", "-p", "/Net/ThemeName",
                "-s", gtk_theme, "--create"
            ], stderr=subprocess.DEVNULL, check=False)
        
        if icon_theme:
            subprocess.run([
                "xfconf-query", "-c", "xsettings", "-p", "/Net/IconThemeName",
                "-s", icon_theme, "--create"
            ], stderr=subprocess.DEVNULL, check=False)
        
        if cursor_theme:
            subprocess.run([
                "xfconf-query", "-c", "xsettings", "-p", "/Gtk/CursorThemeName",
                "-s", cursor_theme, "--create"
            ], stderr=subprocess.DEVNULL, check=False)
        
        # Qtile doesn't typically need a 'reconfigure' for GTK themes, 
        # but we could trigger a cmd-obj call here if you used Qtile-specific themes.
        
        print(f"{CLR_CYAN}[AWP]{CLR_RESET} WS{ws_num + 1} Applied: GTK={gtk_theme}, Icons={icon_theme}")
        
    except Exception as e:
        pass
        
def qtile_xfce_wallpaper_native(ws_num: int, image_path: str, scaling: str):
    """
    Qtile fallback to feh.
    """
    qtile_xfce_set_wallpaper(ws_num, image_path, scaling)
