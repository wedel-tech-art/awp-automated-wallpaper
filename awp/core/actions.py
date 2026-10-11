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
import configparser
from pathlib import Path
from typing import List, Tuple, Optional
from .constants import AWP_DIR, STATE_PATH, RUNTIME_STATE_PATH
from .config import AWPConfig
from backends import get_backend, write_qt6_kde_accent
from core.utils import load_images, sort_images
from core.runtime import load_index_state, save_index_state
from core.themes import extract_preset_from_theme
from core.printer import get_printer

_printer = get_printer()

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
            _printer.warning(f"Backend workspace detection failed: {e}")
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


def _get_config_parser(config):
    """
    Ensure we have a ConfigParser object.

    Handles:
    - ConfigParser object → return as-is
    - AWPConfig object → return config.config
    - SimpleConfig (duck-typed ConfigParser-like) → return as-is
    - Anything else → create new AWPConfig and return its config
    """
    # 1. Real ConfigParser
    if isinstance(config, configparser.ConfigParser):
        return config

    # 2. AWPConfig wrapper — unwrap to its inner ConfigParser
    if hasattr(config, 'config') and isinstance(config.config, configparser.ConfigParser):
        return config.config

    # 3. Duck-typed ConfigParser-like (e.g. Bath's SimpleConfig)
    if hasattr(config, 'sections') and hasattr(config, 'has_section') and hasattr(config, 'get'):
        return config

    # 4. Fallback
    return AWPConfig().config


def set_themes(ws_num: int, config):
    """
    Unified theme application for ALL backends.
    Handles: GTK, Icons, Cursor, WM, Desktop, AND Qt/KDE.
    """
    
    # 1. Get ConfigParser object
    awp_config = _get_config_parser(config)
    
    # 2. Get the current backend
    backend_name = awp_config.get('general', 'os_detected', fallback='xfce')
    
    # 3. Apply GTK/Icons/Cursor/WM via backend
    backend = get_backend(backend_name)
    if backend:
        func = backend.get("themes")
        if func:
            func(ws_num, awp_config)
    
    # 4. Apply Qt/KDE accent (UNIFIED for ALL backends)
    section = f"ws{ws_num + 1}"
    if awp_config.has_section(section):
        accent_color = awp_config.get(section, 'icon_color', fallback=None)
        if accent_color:
            gtk_theme = awp_config.get(section, 'gtk_theme', fallback='awp-gtk-breeze-000000')
            theme_name = extract_preset_from_theme(gtk_theme, 'awp-gtk-')
            if not theme_name:
                theme_name = 'breeze'
            write_qt6_kde_accent(accent_color, theme_name)

def set_panel_icon(icon_path: str):
    """Set panel/menu icon for current desktop environment."""
    func = get_backend_func("icon")
    if func:
        func(icon_path)
        

def run_awp_start(preset_name: str, awp_dir: str = None) -> bool:
    """
    Run awp_start.sh to recreate symlinks (non-blocking).
    
    Args:
        preset_name: The preset to apply (e.g., 'qtile_xfce-debian')
        awp_dir: Path to AWP directory (default: ~/awp)
    
    Returns:
        True if started successfully, False otherwise
    """

    if awp_dir is None:
        awp_dir = os.path.expanduser("~/awp")
    
    awp_start = os.path.join(awp_dir, "awp_start.sh")
    
    if not os.path.exists(awp_start):
        _printer.warning(f"awp_start.sh not found at {awp_start}", backend="actions")
        return False
    
    try:
        # Start process without waiting
        cmd = [awp_start, preset_name]
        subprocess.Popen(
            cmd,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            stdin=subprocess.DEVNULL,
            start_new_session=True
        )
        
        _printer.info(f"Symlinks recreated for {preset_name}", backend="actions")
        return True
                
    except Exception as e:
        _printer.error(f"Failed to run awp_start.sh: {e}", backend="actions")
        return False
