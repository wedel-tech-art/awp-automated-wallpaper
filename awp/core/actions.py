#!/usr/bin/env python3
"""
AWP - Automated Wallpaper Program
Core Actions Module

Shared business logic
"""
import os
import json
import random
import subprocess
from pathlib import Path
from typing import List, Tuple, Optional

from .constants import AWP_DIR, STATE_PATH, RUNTIME_STATE_PATH
from .config import AWPConfig
from backends import get_backend

def load_images(folder_path: str) -> List[Path]:
    """Load all supported images (JPG, PNG, WebP, AVIF)."""
    p = Path(folder_path)
    if not p.is_dir():
        return []
    
    # Define the formats you want to support
    extensions = ['*.jpg', '*.jpeg', '*.png', '*.webp', '*.avif']
    
    images = []
    for ext in extensions:
        # This catches both .jpg and .JPG because glob is case-insensitive 
        # on some systems, but to be safe on Linux, we can do this:
        images.extend(p.glob(ext.lower()))
        images.extend(p.glob(ext.upper()))
        
    return images

def sort_images(images: List[Path], order_key: str) -> List[Path]:
    """Sort images based on specified order preference."""
    if order_key == 'name_az':
        return sorted(images, key=lambda f: f.name.lower())
    elif order_key == 'name_za':
        return sorted(images, key=lambda f: f.name.lower(), reverse=True)
    elif order_key == 'name_new':
        return sorted(images, key=lambda f: f.stat().st_mtime, reverse=True)
    elif order_key == 'name_old':
        return sorted(images, key=lambda f: f.stat().st_mtime)
    return images

def load_state() -> dict:
    """Load workspace state from JSON file."""
    if not os.path.isfile(STATE_PATH):
        return {}
    try:
        with open(STATE_PATH, "r") as f:
            return json.load(f)
    except Exception:
        return {}

def save_state(state: dict):
    """Save workspace state to JSON file."""
    tmp = STATE_PATH + ".tmp"
    with open(tmp, "w") as f:
        json.dump(state, f)
    os.replace(tmp, STATE_PATH)

def get_ws_key(ws_num: int) -> str:
    """Get workspace key for state storage."""
    return f"ws{ws_num+1}"

def get_current_workspace() -> int:
    """Get current workspace number using xprop."""
    try:
        ws_num = subprocess.check_output(
            ["xprop", "-root", "_NET_CURRENT_DESKTOP"], 
            text=True
        ).strip().split()[-1]
        return int(ws_num)
    except Exception as e:
        print(f"Error getting workspace: {e}")
        return 0

def parse_timing(timing_str: str) -> int:
    """Convert timing string (e.g., 30s, 7m, 2h) to seconds."""
    units = {'s': 1, 'm': 60, 'h': 3600}
    try:
        unit = timing_str[-1].lower()
        number = int(timing_str[:-1])
        return number * units.get(unit, 60)
    except Exception:
        return 60  # Default to 60 seconds

_DE = None

def set_backend(desktop_env: str):
    """Set the global desktop environment backend."""
    global _DE
    _DE = desktop_env

def get_backend_func(func_name: str):
    """Get a backend function for current DE."""
    backend = get_backend(_DE)
    if backend:
        return backend.get(func_name)
    return None

def set_wallpaper(ws_num: int, image_path: str, scaling: str):
    """Set wallpaper for specified workspace with given scaling."""
    func = get_backend_func("wallpaper")
    if func:
        func(ws_num, image_path, scaling)

def force_single_workspace_off():
    """Disable single workspace mode for current desktop environment."""
    func = get_backend_func("workspace_off")
    if func:
        func()

def refresh_current_workspace():
    """Apply current workspace configuration immediately.
    Used by dashboard after saving changes."""
    from core.runtime import update_runtime_state    
    ws_num = get_current_workspace()
    config = AWPConfig()
    set_backend(config.de)
    
    ws_config = config.get_workspace_config(ws_num)
    images, _ = get_workspace_images(ws_config)
    
    if not images:
        return False
    
    idx = get_workspace_index(ws_num, images)
    wallpaper_path = str(images[idx])
    
    # Apply wallpaper
    set_wallpaper(ws_num, wallpaper_path, ws_config['scaling'])
    
    # Apply themes NOW (this is what you want!)
    set_themes(ws_num, config.config)
    
    # Update panel icon if changed
    icon_path = ws_config.get('icon') or DEFAULT_ICON
    set_panel_icon(icon_path)
       
    # Update runtime state
    full_info = config.generate_runtime_state(f"ws{ws_num+1}", wallpaper_path)
    update_runtime_state(full_info)
    
    return True
    
    # This one is needed by Dab
def get_workspace_images(ws_config: dict) -> tuple:
    """Load and sort images for a workspace based on its config."""
    folder = ws_config['folder']
    mode = ws_config['mode']
    order = ws_config['order']
    
    images = load_images(folder)
    if mode == 'sequential':
        images = sort_images(images, order)
    else:
        images = sort_images(images, 'name_az')
    
    return images, mode

    # This one is needed by Dab
def get_workspace_index(ws_num: int, images: list) -> int:
    """Get current index for workspace from state."""
    state = load_state()
    ws_key = get_ws_key(ws_num)
    idx = int(state.get(ws_key, 0) or 0)
    if idx >= len(images):
        idx = 0
    return idx

    # This one is needed by Dab
def set_themes(ws_num: int, config=None):
    """Apply theme settings for specified workspace."""
    func = get_backend_func("themes")
    if func:
        func(ws_num, config)

    # This one is needed by Dab
def set_panel_icon(icon_path: str):
    """Set panel/menu icon for current desktop environment."""
    func = get_backend_func("icon")
    if func:
        func(icon_path)
        
def show_hud():
    """
    Launches the fading info HUD.
    The HUD script handles its own delay and cleanup.
    """
    try:
        hud_script = os.path.expanduser("~/awp/hud_ws_info.py")
        # Popen is non-blocking; the daemon continues immediately
        subprocess.Popen(["python3", hud_script], 
                         stdout=subprocess.DEVNULL, 
                         stderr=subprocess.DEVNULL)
    except Exception as e:
        print(f"HUD Error: {e}")
