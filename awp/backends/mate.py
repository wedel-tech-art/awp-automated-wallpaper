#!/usr/bin/env python3
"""
MATE Desktop Backend for AWP
"""
import os
import subprocess

SCALING_MATE = {'centered': 'centered', 'scaled': 'scaled', 'zoomed': 'zoom'}

def mate_force_single_workspace_off():
    """MATE doesn't have single workspace mode to disable."""
    pass

def mate_set_wallpaper(ws_num: int, image_path: str, scaling: str):
    """Set wallpaper for MATE with specified scaling."""
    style_val = SCALING_MATE.get(scaling, 'zoom')
    subprocess.run(["gsettings", "set", "org.mate.background", "picture-filename", image_path])
    subprocess.run(["gsettings", "set", "org.mate.background", "picture-options", style_val])

def mate_set_icon(icon_path: str):
    """MATE icon setting not implemented."""
    print(f"[AWP] MATE icon setting not implemented yet. Would set to: {icon_path}")

def mate_set_themes(ws_num: int, config):
    """Set MATE theme parameters from configuration."""
    section = f"ws{ws_num + 1}"
    if not config.has_section(section):
        return
    
    icon_theme = config.get(section, 'icon_theme', fallback=None)
    gtk_theme = config.get(section, 'gtk_theme', fallback=None)
    cursor_theme = config.get(section, 'cursor_theme', fallback=None)
    wm_theme = config.get(section, 'wm_theme', fallback=None)
    
    if icon_theme:
        subprocess.run(["gsettings", "set", "org.mate.interface", "icon-theme", icon_theme])
    if gtk_theme:
        subprocess.run(["gsettings", "set", "org.mate.interface", "gtk-theme", gtk_theme])
    if cursor_theme:
        subprocess.run(["gsettings", "set", "org.mate.peripherals-mouse", "cursor-theme", cursor_theme])
    if wm_theme:
        subprocess.run(["gsettings", "set", "org.mate.Marco.general", "theme", wm_theme])

