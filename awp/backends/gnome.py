#!/usr/bin/env python3
"""
GNOME Desktop Backend for AWP
"""
import os
import subprocess

SCALING_GNOME = {'centered': 'centered', 'scaled': 'scaled', 'zoomed': 'zoom'}

def gnome_force_single_workspace_off():
    """GNOME doesn't have single workspace mode to disable."""
    pass

def gnome_set_wallpaper(ws_num: int, image_path: str, scaling: str):
    """Set wallpaper for GNOME with specified scaling."""
    uri = f"file://{image_path}"
    style_val = SCALING_GNOME.get(scaling, 'zoom')
    subprocess.run(["gsettings", "set", "org.gnome.desktop.background", "picture-uri", uri])
    subprocess.run(["gsettings", "set", "org.gnome.desktop.background", "picture-uri-dark", uri])
    subprocess.run(["gsettings", "set", "org.gnome.desktop.background", "picture-options", style_val])

def gnome_set_icon(icon_path: str):
    """
    Set icon for GNOME (not implemented yet).
    
    Args:
        icon_path (str): Full path to icon image file
    """
    print(f"[AWP] GNOME icon setting not implemented yet. Would set to: {icon_path}")

def gnome_set_themes(ws_num: int, config):
    """Set GNOME theme parameters from configuration."""
    section = f"ws{ws_num + 1}"
    if not config.has_section(section):
        return
    
    icon_theme = config.get(section, 'icon_theme', fallback=None)
    gtk_theme = config.get(section, 'gtk_theme', fallback=None)
    cursor_theme = config.get(section, 'cursor_theme', fallback=None)
    
    if icon_theme:
        subprocess.run(["gsettings", "set", "org.gnome.desktop.interface", "icon-theme", icon_theme])
        print(f"✓ GNOME icon theme: {icon_theme}")
    if gtk_theme:
        subprocess.run(["gsettings", "set", "org.gnome.desktop.interface", "gtk-theme", gtk_theme])
        print(f"✓ GNOME GTK theme: {gtk_theme}")
    if cursor_theme:
        subprocess.run(["gsettings", "set", "org.gnome.desktop.interface", "cursor-theme", cursor_theme])
        print(f"✓ GNOME cursor theme: {cursor_theme}")

