#!/usr/bin/env python3
"""
MATE Desktop Backend for AWP - DUAL MODE VERSION
Supports both native MATE wallpaper and feh-based lean mode.
"""

import os
import subprocess
import time

# ANSI Color Codes
CLR_RED    = "\033[91m"
CLR_GREEN  = "\033[92m"
CLR_YELLOW = "\033[93m"
CLR_CYAN   = "\033[96m"
CLR_RESET  = "\033[0m"
CLR_BOLD   = "\033[1m"

# MATE native scaling
SCALING_MATE = {'centered': 'centered', 'scaled': 'scaled', 'zoomed': 'zoom'}

# feh scaling (same as XFCE)
SCALING_FEH = {
    'centered': '--bg-center',
    'scaled': '--bg-scale',
    'zoomed': '--bg-fill'
}

# Simple state tracking
_lean_mode_active = False

def mate_lean_mode():
    """
    Kills MATE desktop components to enable feh-based wallpaper.
    Similar to xfce_lean_mode() - kills desktop manager for low-latency audio.
    """
    global _lean_mode_active
    
    try:
        print(f"{CLR_CYAN}[AWP-MATE]{CLR_RESET} {CLR_YELLOW}Activating Lean Mode...{CLR_RESET}")
        
        # Kill caja-desktop (MATE's desktop manager)
        subprocess.run(["pkill", "-f", "caja-desktop"], stderr=subprocess.DEVNULL)
        time.sleep(0.3)  # Brief pause
        
        # Kill cairo-dock if present (common MATE dock)
        subprocess.run(["pkill", "-f", "cairo-dock"], stderr=subprocess.DEVNULL)
        
        # Optional: Try to prevent auto-restart (not always possible in MATE)
        # MATE sessions are usually less aggressive about restarting than GNOME
        
        _lean_mode_active = True
        print(f"{CLR_CYAN}[AWP-MATE]{CLR_RESET} {CLR_GREEN}Lean Mode Activated: caja-desktop terminated{CLR_RESET}")
        return True
        
    except Exception as e:
        print(f"{CLR_RED}[AWP-MATE] Lean Mode Error: {e}{CLR_RESET}")
        _lean_mode_active = False
        return False

def mate_force_single_workspace_off():
    """MATE doesn't have single workspace mode to disable."""
    print(f"{CLR_CYAN}[AWP-MATE]{CLR_RESET} {CLR_YELLOW}Note: MATE doesn't have single workspace mode{CLR_RESET}")

def mate_set_wallpaper_native(ws_num: int, image_path: str, scaling: str):
    """
    LEGACY: Set wallpaper using MATE's native desktop manager.
    Keeps desktop icons and right-click menu.
    """
    try:
        style_val = SCALING_MATE.get(scaling, 'zoom')
        wp_name = os.path.basename(image_path)
        
        # Set wallpaper using MATE's gsettings
        subprocess.run(["gsettings", "set", "org.mate.background", "picture-filename", image_path], check=True)
        subprocess.run(["gsettings", "set", "org.mate.background", "picture-options", style_val], check=True)
        
        print(f"{CLR_CYAN}[AWP]{CLR_RESET} Workspace {ws_num + 1} -> {CLR_GREEN}{CLR_BOLD}{wp_name}{CLR_RESET} (MATE native)")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"{CLR_RED}[AWP-MATE] Native wallpaper failed: {e}{CLR_RESET}")
        return False
    except Exception as e:
        print(f"{CLR_RED}[AWP-MATE] Unexpected error: {e}{CLR_RESET}")
        return False

def mate_set_wallpaper(ws_num: int, image_path: str, scaling: str):
    """Try feh first, fallback to native MATE."""
    wp_name = os.path.basename(image_path)
    
    # Always try feh if available
    style_flag = SCALING_FEH.get(scaling, '--bg-fill')
    
    try:
        subprocess.run(["feh", style_flag, image_path], check=True)
        print(f"{CLR_CYAN}[AWP]{CLR_RESET} Workspace {ws_num + 1} -> {CLR_GREEN}{CLR_BOLD}{wp_name}{CLR_RESET} (feh)")
        return True
    except Exception as e:
        print(f"{CLR_YELLOW}[AWP-MATE] feh failed, falling back to native: {e}{CLR_RESET}")
        return mate_set_wallpaper_native(ws_num, image_path, scaling)  # Fallback to native

def mate_set_icon(icon_path: str):
    """MATE icon setting placeholder."""
    icon_name = os.path.basename(icon_path)
    print(f"{CLR_YELLOW}[AWP-MATE]{CLR_RESET} Panel icon setting not available in MATE (would set: {CLR_CYAN}{icon_name}{CLR_RESET})")

def mate_set_themes(ws_num: int, config):
    """Set MATE theme parameters from configuration."""
    section = f"ws{ws_num + 1}"
    
    if not config.has_section(section):
        print(f"{CLR_YELLOW}[AWP-MATE] No theme config found for {section}{CLR_RESET}")
        return
    
    icon_theme = config.get(section, 'icon_theme', fallback=None)
    gtk_theme = config.get(section, 'gtk_theme', fallback=None)
    cursor_theme = config.get(section, 'cursor_theme', fallback=None)
    wm_theme = config.get(section, 'wm_theme', fallback=None)
    
    try:
        if icon_theme:
            subprocess.run(["gsettings", "set", "org.mate.interface", "icon-theme", icon_theme], check=False)
            print(f"{CLR_GREEN}✓{CLR_RESET} MATE icon theme: {CLR_CYAN}{icon_theme}{CLR_RESET}")
        
        if gtk_theme:
            subprocess.run(["gsettings", "set", "org.mate.interface", "gtk-theme", gtk_theme], check=False)
            print(f"{CLR_GREEN}✓{CLR_RESET} MATE GTK theme: {CLR_CYAN}{gtk_theme}{CLR_RESET}")
        
        if cursor_theme:
            subprocess.run(["gsettings", "set", "org.mate.peripherals-mouse", "cursor-theme", cursor_theme], check=False)
            print(f"{CLR_GREEN}✓{CLR_RESET} MATE cursor theme: {CLR_CYAN}{cursor_theme}{CLR_RESET}")
        
        if wm_theme:
            subprocess.run(["gsettings", "set", "org.mate.Marco.general", "theme", wm_theme], check=False)
            print(f"{CLR_GREEN}✓{CLR_RESET} MATE window theme: {CLR_CYAN}{wm_theme}{CLR_RESET}")
        
        print(f"{CLR_CYAN}[AWP]{CLR_RESET} Themes Applied for {CLR_BOLD}WS{ws_num + 1}{CLR_RESET}")
        
    except Exception as e:
        print(f"{CLR_RED}Error applying MATE themes: {e}{CLR_RESET}")
