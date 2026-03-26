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
from core.utils import load_images, sort_images
from core.runtime import load_index_state, save_index_state

def get_ws_key(ws_num: int) -> str:
    """Get workspace key for state storage."""
    return f"ws{ws_num+1}"

def get_current_workspace() -> int:
    """
    The Universal Passport: Asks the active backend for the workspace number.
    This replaces the hardcoded xprop call.
    """
    func = get_backend_func("current_ws")
    if func:
        try:
            return func()
        except Exception as e:
            print(f"Backend workspace detection failed: {e}")
            return 0
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

def get_workspace_index(ws_num: int, images: list) -> int:
    """Get current index for workspace from state."""
    state = load_index_state()
    ws_key = get_ws_key(ws_num)
    idx = int(state.get(ws_key, 0) or 0)
    if idx >= len(images):
        idx = 0
    return idx

def set_themes(ws_num: int, config=None):
    """Apply theme settings for specified workspace."""
    func = get_backend_func("themes")
    if func:
        func(ws_num, config)

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
