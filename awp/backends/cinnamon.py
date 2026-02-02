#!/usr/bin/env python3
"""
Cinnamon Desktop Backend for AWP
Contains all Cinnamon-specific wallpaper and theme management functions.
"""

import os
import subprocess
import json

# ANSI Color Codes for clean terminal output (matching xfce.py)
CLR_RED    = "\033[91m"
CLR_GREEN  = "\033[92m"
CLR_YELLOW = "\033[93m"
CLR_CYAN   = "\033[96m"
CLR_RESET  = "\033[0m"
CLR_BOLD   = "\033[1m"

SCALING_CINNAMON = {'centered': 'centered', 'scaled': 'scaled', 'zoomed': 'zoom'}

def cinnamon_lean_mode():
    """
    Cinnamon already uses native wallpaper methods.
    This is a compatibility placeholder with optional optimizations.
    """
    try:
        # Optional: Disable some visual effects for better performance
        # subprocess.run(["gsettings", "set", "org.cinnamon", "desktop-effects", "false"], check=False)
        # subprocess.run(["gsettings", "set", "org.cinnamon", "effects-desktop", "false"], check=False)
        
        print(f"{CLR_CYAN}[AWP-Cinnamon]{CLR_RESET} {CLR_YELLOW}Note: Cinnamon uses native wallpaper methods{CLR_RESET}")
    except Exception as e:
        print(f"{CLR_RED}[AWP-Cinnamon] Lean Mode Error: {e}{CLR_RESET}")

def cinnamon_force_single_workspace_off():
    """Cinnamon doesn't have single workspace mode to disable."""
    print(f"{CLR_CYAN}[AWP-Cinnamon]{CLR_RESET} {CLR_YELLOW}Note: Cinnamon doesn't have single workspace mode{CLR_RESET}")

def cinnamon_set_wallpaper_native(ws_num: int, image_path: str, scaling: str):
    """
    Alias for cinnamon_set_wallpaper since Cinnamon is already native.
    Uses gsettings to set wallpaper with visual feedback.
    """
    return cinnamon_set_wallpaper(ws_num, image_path, scaling)

def cinnamon_set_wallpaper(ws_num: int, image_path: str, scaling: str):
    """Set wallpaper for Cinnamon with specified scaling."""
    try:
        uri = f"file://{os.path.abspath(image_path)}"
        style_val = SCALING_CINNAMON.get(scaling, 'zoom')
        wp_name = os.path.basename(image_path)
        
        # Set wallpaper properties
        subprocess.run(["gsettings", "set", "org.cinnamon.desktop.background", "picture-uri", uri], check=True)
        subprocess.run(["gsettings", "set", "org.cinnamon.desktop.background", "picture-options", style_val], check=True)
        
        # Visual feedback
        print(f"{CLR_CYAN}[AWP]{CLR_RESET} Workspace {ws_num + 1} -> {CLR_GREEN}{CLR_BOLD}{wp_name}{CLR_RESET}")
        
    except subprocess.CalledProcessError as e:
        print(f"{CLR_RED}[AWP-Cinnamon] Failed to set wallpaper via gsettings: {e}{CLR_RESET}")
    except Exception as e:
        print(f"{CLR_RED}[AWP-Cinnamon] Unexpected error: {e}{CLR_RESET}")

def cinnamon_set_icon(icon_path: str):
    """
    Set the Cinnamon Menu icon.
    
    Args:
        icon_path (str): Full path to icon image file
    """
    config_file = os.path.expanduser("~/.config/cinnamon/spices/menu@cinnamon.org/0.json")
    
    try:
        if not os.path.exists(config_file):
            print(f"{CLR_YELLOW}[AWP-Cinnamon] Menu config not found at {config_file}{CLR_RESET}")
            return False
        
        with open(config_file, "r") as f:
            data = json.load(f)
        
        data["menu-icon"]["value"] = icon_path
        
        with open(config_file, "w") as f:
            json.dump(data, f, indent=4)
        
        icon_name = os.path.basename(icon_path)
        print(f"{CLR_GREEN}✓{CLR_RESET} Cinnamon menu icon: {CLR_CYAN}{icon_name}{CLR_RESET}")
        return True
        
    except json.JSONDecodeError as e:
        print(f"{CLR_RED}✗ Failed to parse menu config: {e}{CLR_RESET}")
        return False
    except Exception as e:
        print(f"{CLR_RED}✗ Error setting Cinnamon menu icon: {e}{CLR_RESET}")
        return False

def cinnamon_set_themes(ws_num: int, config):
    """Set Cinnamon theme parameters from configuration."""
    section = f"ws{ws_num + 1}"
    
    if not config.has_section(section):
        print(f"{CLR_YELLOW}[AWP-Cinnamon] No theme config found for {section}{CLR_RESET}")
        return
    
    icon_theme = config.get(section, 'icon_theme', fallback=None)
    gtk_theme = config.get(section, 'gtk_theme', fallback=None)
    cursor_theme = config.get(section, 'cursor_theme', fallback=None)
    desktop_theme = config.get(section, 'desktop_theme', fallback=None)
    wm_theme = config.get(section, 'wm_theme', fallback=None)
    
    try:
        if icon_theme:
            subprocess.run(["gsettings", "set", "org.cinnamon.desktop.interface", "icon-theme", icon_theme], check=False)
            print(f"{CLR_GREEN}✓{CLR_RESET} Cinnamon icon theme: {CLR_CYAN}{icon_theme}{CLR_RESET}")
        
        if gtk_theme:
            subprocess.run(["gsettings", "set", "org.cinnamon.desktop.interface", "gtk-theme", gtk_theme], check=False)
            print(f"{CLR_GREEN}✓{CLR_RESET} Cinnamon GTK theme: {CLR_CYAN}{gtk_theme}{CLR_RESET}")
        
        if cursor_theme:
            subprocess.run(["gsettings", "set", "org.cinnamon.desktop.interface", "cursor-theme", cursor_theme], check=False)
            print(f"{CLR_GREEN}✓{CLR_RESET} Cinnamon cursor theme: {CLR_CYAN}{cursor_theme}{CLR_RESET}")
        
        if desktop_theme:
            subprocess.run(["gsettings", "set", "org.cinnamon.theme", "name", desktop_theme], check=False)
            print(f"{CLR_GREEN}✓{CLR_RESET} Cinnamon desktop theme: {CLR_CYAN}{desktop_theme}{CLR_RESET}")
        
        if wm_theme:
            subprocess.run(["gsettings", "set", "org.cinnamon.desktop.wm.preferences", "theme", wm_theme], check=False)
            print(f"{CLR_GREEN}✓{CLR_RESET} Cinnamon window theme: {CLR_CYAN}{wm_theme}{CLR_RESET}")
        
        print(f"{CLR_CYAN}[AWP]{CLR_RESET} Themes Applied for {CLR_BOLD}WS{ws_num + 1}{CLR_RESET}")
        
    except Exception as e:
        print(f"{CLR_RED}Error applying Cinnamon themes: {e}{CLR_RESET}")
