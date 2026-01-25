#!/usr/bin/env python3
"""
Cinnamon Desktop Backend for AWP
"""
import os
import subprocess
import json

SCALING_CINNAMON = {'centered': 'centered', 'scaled': 'scaled', 'zoomed': 'zoom'}

def cinnamon_force_single_workspace_off():
    """Cinnamon doesn't have single workspace mode to disable."""
    pass

def cinnamon_set_wallpaper(ws_num: int, image_path: str, scaling: str):
    """Set wallpaper for Cinnamon with specified scaling."""
    uri = f"file://{image_path}"
    style_val = SCALING_CINNAMON.get(scaling, 'zoom')
    subprocess.run(["gsettings", "set", "org.cinnamon.desktop.background", "picture-uri", uri])
    subprocess.run(["gsettings", "set", "org.cinnamon.desktop.background", "picture-options", style_val])

def cinnamon_set_icon(icon_path: str):
    """
    Set the Cinnamon Menu icon.
    
    Args:
        icon_path (str): Full path to icon image file
    """
    config_file = os.path.expanduser("~/.config/cinnamon/spices/menu@cinnamon.org/0.json")
    
    try:
        with open(config_file, "r") as f:
            data = json.load(f)
        
        data["menu-icon"]["value"] = icon_path
        
        with open(config_file, "w") as f:
            json.dump(data, f, indent=4)
        
        print(f"Set Cinnamon menu icon to: {icon_path}")
        
    except Exception as e:
        print(f"Error setting Cinnamon menu icon: {e}")

def cinnamon_set_themes(ws_num: int, config):
    """Set Cinnamon theme parameters from configuration."""
    section = f"ws{ws_num + 1}"
    
    if not config.has_section(section):
        print(f"No theme config found for {section}")
        return
    
    icon_theme = config.get(section, 'icon_theme', fallback=None)
    gtk_theme = config.get(section, 'gtk_theme', fallback=None)
    cursor_theme = config.get(section, 'cursor_theme', fallback=None)
    desktop_theme = config.get(section, 'desktop_theme', fallback=None)
    wm_theme = config.get(section, 'wm_theme', fallback=None)
    
    if icon_theme:
        subprocess.run(["gsettings", "set", "org.cinnamon.desktop.interface", "icon-theme", icon_theme])
        print(f"✓ Cinnamon icon theme: {icon_theme}")
    
    if gtk_theme:
        subprocess.run(["gsettings", "set", "org.cinnamon.desktop.interface", "gtk-theme", gtk_theme])
        print(f"✓ Cinnamon GTK theme: {gtk_theme}")
    
    if cursor_theme:
        subprocess.run(["gsettings", "set", "org.cinnamon.desktop.interface", "cursor-theme", cursor_theme])
        print(f"✓ Cinnamon cursor theme: {cursor_theme}")
    
    if desktop_theme:
        subprocess.run(["gsettings", "set", "org.cinnamon.theme", "name", desktop_theme])
        print(f"✓ Cinnamon desktop theme: {desktop_theme}")
    
    if wm_theme:
        subprocess.run(["gsettings", "set", "org.cinnamon.desktop.wm.preferences", "theme", wm_theme])
        print(f"✓ Cinnamon window theme: {wm_theme}")
    
    print(f"Applied Cinnamon themes for workspace {ws_num + 1}")

