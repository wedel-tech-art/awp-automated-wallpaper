#!/usr/bin/env python3
"""
Openbox + XFCE Hybrid Backend for AWP
For Openbox window manager with XFCE theming components.
Uses feh for wallpapers, xfsettingsd for theming, Openbox for WM.
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

def openbox_xfce_lean_mode():
    """
    Kills xfdesktop and prevents XFCE from restarting it.
    Similar to xfce_lean_mode() but for Openbox environment.
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
        
        print(f"{CLR_CYAN}[AWP-Openbox+XFCE]{CLR_RESET} {CLR_GREEN}Lean Mode: xfdesktop terminated{CLR_RESET}")
        
    except Exception as e:
        print(f"{CLR_RED}[AWP-Openbox+XFCE] Lean Mode Error: {e}{CLR_RESET}")

def openbox_xfce_force_single_workspace_off():
    """
    Disable single workspace mode in XFCE (if xfdesktop was running).
    Similar to xfce_force_single_workspace_off().
    """
    try:
        subprocess.run([
            "xfconf-query", "-c", "xfce4-desktop",
            "-p", "/backdrop/single-workspace-mode",
            "--set", "false", "--create"
        ], stderr=subprocess.DEVNULL)
    except Exception:
        pass  # Silently fail if not using xfdesktop

def openbox_xfce_set_wallpaper(ws_num: int, image_path: str, scaling: str):
    """
    Set wallpaper using feh (Openbox compatible).
    Similar to xfce_set_wallpaper() but always uses feh.
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
        print(f"{CLR_RED}[AWP-Openbox+XFCE] feh failed: {e}{CLR_RESET}")
        # No fallback to native since Openbox doesn't have native wallpaper

def openbox_xfce_set_icon(icon_path: str):
    """
    Openbox + XFCE Hybrid Icon Management.
    Silent version: No terminal noise, no tint2 sabotage.
    """
    # 1. We completely ignore tint2 (The source of the flicker and path corruption)
    
    # 2. Only attempt XFCE panel update if it's actually running
    # (Since you use xfce4-panel in your Openbox session for audio/system trays)
    try:
        # Check if panel exists without printing to terminal
        if subprocess.run(["pgrep", "-x", "xfce4-panel"], capture_output=True).returncode == 0:
            subprocess.run([
                "xfconf-query", "-c", "xfce4-panel",
                "-p", "/plugins/plugin-1/button-icon",
                "-s", icon_path, "--create", "-t", "string"
            ], check=False) # check=False to fail silently
    except Exception:
        pass

    return True

def openbox_xfce_set_themes(ws_num: int, config):
    """
    Apply GTK/Icons/Cursors via xfsettingsd.
    Silent and accurate version for the Beast.
    """
    section = f"ws{ws_num + 1}"
    if not config.has_section(section): 
        return
    
    gtk_theme = config.get(section, 'gtk_theme', fallback=None)
    icon_theme = config.get(section, 'icon_theme', fallback=None)
    cursor_theme = config.get(section, 'cursor_theme', fallback=None)
    
    try:
        # 1. Apply visual themes (shared with XFCE engine)
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
        
        # 2. Reload Openbox (In case you changed things manually in rc.xml)
        subprocess.run(["openbox", "--reconfigure"], stderr=subprocess.DEVNULL)
        
        # 3. Honest, single-line feedback
        print(f"{CLR_CYAN}[AWP]{CLR_RESET} WS{ws_num + 1} Applied: GTK={gtk_theme}, Icons={icon_theme}")
        
    except Exception as e:
        # Only print if something actually fails
        pass
        
def openbox_xfce_wallpaper_native(ws_num: int, image_path: str, scaling: str):
    """
    Openbox doesn't have native wallpaper - falls back to feh.
    Similar to xfce_set_wallpaper_native() but just uses feh.
    """
    print(f"{CLR_YELLOW}[AWP-Openbox+XFCE] No native wallpaper, using feh{CLR_RESET}")
    openbox_xfce_set_wallpaper(ws_num, image_path, scaling)
