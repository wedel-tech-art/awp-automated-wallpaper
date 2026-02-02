#!/usr/bin/env python3
"""
GNOME Desktop Backend for AWP
Contains all GNOME-specific wallpaper and theme management functions.
"""

import os
import subprocess

# ANSI Color Codes for clean terminal output (matching xfce.py)
CLR_RED    = "\033[91m"
CLR_GREEN  = "\033[92m"
CLR_YELLOW = "\033[93m"
CLR_CYAN   = "\033[96m"
CLR_RESET  = "\033[0m"
CLR_BOLD   = "\033[1m"

SCALING_GNOME = {'centered': 'centered', 'scaled': 'scaled', 'zoomed': 'zoom'}

def gnome_lean_mode():
    """
    GNOME already uses native wallpaper methods.
    This is a compatibility placeholder.
    """
    print(f"{CLR_CYAN}[AWP-GNOME]{CLR_RESET} {CLR_YELLOW}Note: GNOME uses native wallpaper methods{CLR_RESET}")

def gnome_force_single_workspace_off():
    """GNOME doesn't have single workspace mode to disable."""
    print(f"{CLR_CYAN}[AWP-GNOME]{CLR_RESET} {CLR_YELLOW}Note: GNOME doesn't have single workspace mode{CLR_RESET}")

def gnome_set_wallpaper_native(ws_num: int, image_path: str, scaling: str):
    """
    Alias for gnome_set_wallpaper since GNOME is already native.
    Uses gsettings to set wallpaper with visual feedback.
    """
    return gnome_set_wallpaper(ws_num, image_path, scaling)

def gnome_set_wallpaper(ws_num: int, image_path: str, scaling: str):
    """Set wallpaper for GNOME with specified scaling."""
    try:
        uri = f"file://{os.path.abspath(image_path)}"
        style_val = SCALING_GNOME.get(scaling, 'zoom')
        wp_name = os.path.basename(image_path)
        
        # Set wallpaper properties (both light and dark mode)
        subprocess.run(["gsettings", "set", "org.gnome.desktop.background", "picture-uri", uri], check=True)
        subprocess.run(["gsettings", "set", "org.gnome.desktop.background", "picture-uri-dark", uri], check=True)
        subprocess.run(["gsettings", "set", "org.gnome.desktop.background", "picture-options", style_val], check=True)
        
        # Visual feedback
        print(f"{CLR_CYAN}[AWP]{CLR_RESET} Workspace {ws_num + 1} -> {CLR_GREEN}{CLR_BOLD}{wp_name}{CLR_RESET}")
        
    except subprocess.CalledProcessError as e:
        print(f"{CLR_RED}[AWP-GNOME] Failed to set wallpaper via gsettings: {e}{CLR_RESET}")
    except Exception as e:
        print(f"{CLR_RED}[AWP-GNOME] Unexpected error: {e}{CLR_RESET}")

def gnome_set_icon(icon_path: str):
    """
    GNOME doesn't have a simple panel icon like XFCE/Cinnamon.
    This is a placeholder for API compatibility.
    
    Args:
        icon_path (str): Full path to icon image file (ignored)
    """
    icon_name = os.path.basename(icon_path)
    print(f"{CLR_YELLOW}[AWP-GNOME]{CLR_RESET} Panel icon setting not available in GNOME (would set: {CLR_CYAN}{icon_name}{CLR_RESET})")

def gnome_set_themes(ws_num: int, config):
    """Set GNOME theme parameters from configuration."""
    section = f"ws{ws_num + 1}"
    
    if not config.has_section(section):
        print(f"{CLR_YELLOW}[AWP-GNOME] No theme config found for {section}{CLR_RESET}")
        return
    
    icon_theme = config.get(section, 'icon_theme', fallback=None)
    gtk_theme = config.get(section, 'gtk_theme', fallback=None)
    cursor_theme = config.get(section, 'cursor_theme', fallback=None)
    
    try:
        if icon_theme:
            subprocess.run(["gsettings", "set", "org.gnome.desktop.interface", "icon-theme", icon_theme], check=False)
            print(f"{CLR_GREEN}✓{CLR_RESET} GNOME icon theme: {CLR_CYAN}{icon_theme}{CLR_RESET}")
        
        if gtk_theme:
            subprocess.run(["gsettings", "set", "org.gnome.desktop.interface", "gtk-theme", gtk_theme], check=False)
            print(f"{CLR_GREEN}✓{CLR_RESET} GNOME GTK theme: {CLR_CYAN}{gtk_theme}{CLR_RESET}")
        
        if cursor_theme:
            subprocess.run(["gsettings", "set", "org.gnome.desktop.interface", "cursor-theme", cursor_theme], check=False)
            print(f"{CLR_GREEN}✓{CLR_RESET} GNOME cursor theme: {CLR_CYAN}{cursor_theme}{CLR_RESET}")
        
        print(f"{CLR_CYAN}[AWP]{CLR_RESET} Themes Applied for {CLR_BOLD}WS{ws_num + 1}{CLR_RESET}")
        
    except Exception as e:
        print(f"{CLR_RED}Error applying GNOME themes: {e}{CLR_RESET}")
