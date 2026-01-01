#!/usr/bin/env python3
"""
Generic/WM Backend for AWP
For Window Managers: Openbox, Fluxbox, i3, bspwm, awesome, etc.
Minimalist implementation - only what actually works.
"""

import os
import subprocess

def generic_force_single_workspace_off():
    """
    WM doesn't have single workspace mode to disable.
    This is a no-op for generic backends.
    """
    pass

def generic_configure_screen_blanking(timeout_seconds: int):
    """
    Configure screen blanking for X11 WM sessions.
    
    Args:
        timeout_seconds (int): Time in seconds before screen blanks (0 = disable)
    """
    if timeout_seconds == 0:
        subprocess.run(["xset", "s", "off"], check=False)
        subprocess.run(["xset", "-dpms"], check=False)
        print(f"[Generic] Screen blanking: OFF")
    else:
        subprocess.run(["xset", "s", str(timeout_seconds)], check=False)
        subprocess.run(["xset", "+dpms"], check=False)
        print(f"[Generic] Screen blanking: {timeout_seconds}s")

def generic_set_wallpaper(ws_num: int, image_path: str, scaling: str):
    """
    Set wallpaper for WM using feh.
    
    Args:
        ws_num (int): Workspace number (0-based)
        image_path (str): Path to wallpaper image
        scaling (str): Scaling mode ('centered', 'scaled', 'zoomed', 'fill')
    """
    # Simple mapping
    scaling_options = {
        'centered': '--bg-center',
        'scaled': '--bg-scale', 
        'zoomed': '--bg-fill',
        'fill': '--bg-fill'
    }
    
    style_val = scaling_options.get(scaling, '--bg-fill')
    
    try:
        subprocess.run(["feh", style_val, image_path], check=True)
        print(f"[Generic] WS{ws_num}: {os.path.basename(image_path)}")
    except (subprocess.CalledProcessError, FileNotFoundError):
        print(f"[Generic] Error: Install 'feh' for wallpaper support")

def generic_set_icon(icon_path: str):
    """
    WM panel icon - NOT IMPLEMENTED.
    
    Args:
        icon_path (str): Path to icon image (not used in WM)
    """
    if icon_path:
        print(f"[Generic] Note: WM panels need manual icon configuration")

def generic_set_themes(ws_num: int, config):
    """
    Set WM theme parameters from configuration.
    
    Args:
        ws_num (int): Workspace number (0-based)
        config: Configuration parser object
    """
    section = f"ws{ws_num + 1}"
    
    if not config.has_section(section):
        print(f"[Generic] No theme config for {section}")
        return
    
    # Get theme settings
    gtk_theme = config.get(section, 'theme', fallback='')
    cursor_theme = config.get(section, 'cursor_theme', fallback='')
    icon_theme = config.get(section, 'icon_theme', fallback='')
    
    # Apply GTK themes via gsettings (works for GTK apps in WM)
    try:
        if gtk_theme:
            subprocess.run([
                "gsettings", "set", "org.gnome.desktop.interface",
                "gtk-theme", gtk_theme
            ], capture_output=True)
            print(f"[Generic] GTK theme: {gtk_theme}")
        
        if cursor_theme:
            subprocess.run([
                "gsettings", "set", "org.gnome.desktop.interface",
                "cursor-theme", cursor_theme
            ], capture_output=True)
            print(f"[Generic] Cursor theme: {cursor_theme}")
        
        if icon_theme:
            subprocess.run([
                "gsettings", "set", "org.gnome.desktop.interface",
                "icon-theme", icon_theme
            ], capture_output=True)
            print(f"[Generic] Icon theme: {icon_theme}")
        
        print(f"[Generic] Applied themes for workspace {ws_num + 1}")
        
    except subprocess.CalledProcessError as e:
        print(f"[Generic] Error applying themes: {e}")
