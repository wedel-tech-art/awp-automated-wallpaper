#!/usr/bin/env python3
"""
AWP - Automated Wallpaper Program
Main Daemon Process

Background service that manages wallpaper rotation, theme switching, 
and workspace-aware desktop customization.
Part of the AWP wallpaper automation system.
"""

import json
import os
import sys
import time
import random
import subprocess
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any, Union

# Set environment variables to prevent accessibility bus warnings
os.environ['NO_AT_BRIDGE'] = '1'

# CORE IMPORTS
from core.constants import AWP_DIR, STATE_PATH, CONKY_STATE_PATH
from core.config import AWPConfig, ConfigError
from backends import get_backend

# =============================================================================
# LOGGING CONFIGURATION
# =============================================================================

def setup_logging() -> logging.Logger:
    """Configures logging to output to both the terminal and a log file."""
    logger = logging.getLogger("AWP")
    logger.setLevel(logging.INFO)

    # Console Handler (Visual feedback for your terminal)
    c_handler = logging.StreamHandler()
    c_handler.setFormatter(logging.Formatter('[AWP] %(message)s'))
    
    # File Handler (Professional background record)
    log_file = os.path.join(AWP_DIR, "awp_daemon.log")
    f_handler = logging.FileHandler(log_file)
    f_handler.setFormatter(logging.Formatter(
        '%(asctime)s [%(levelname)s] %(message)s', '%H:%M:%S'
    ))

    logger.addHandler(c_handler)
    logger.addHandler(f_handler)
    return logger

logger = setup_logging()

# =============================================================================
# CONKY INTEGRATION (OPTIONAL)
# 
# To enable Conky integration:
# 1. Ensure the CONKY_STATE_PATH below matches your Conky configuration.
# 2. Your Conky/Lua script can read from this file for real-time wallpaper info.
#
# AWP is designed to be "Conky-agnostic"—the daemon will update the state file
# if possible, but the core engine does not require Conky to function.
#
# AVAILABLE VARIABLES for your Conky/Lua script:
# - wallpaper_path: Current wallpaper image path
# - workspace_name: Current workspace (e.g., 'ws1')  
# - logo_path: Workspace icon path
# - icon_color: Dominant color from workspace icon (hex)
# - intv: Wallpaper rotation interval (e.g., '5m', '30s')
# - flow: Rotation mode ('random' or 'sequential')
# - sort: Sort order ('name_az', 'name_za', 'name_old', 'name_new')
# - view: Scaling mode ('centered', 'scaled', 'zoomed')
# - blanking_timeout: Screen blanking timeout ('off', '30s', '5m', etc.)
# - blanking_paused: Whether blanking is paused ('True' or 'False')
# =============================================================================

# =============================================================================
# UNIVERSAL DESKTOP FUNCTIONS
# =============================================================================

def force_single_workspace_off() -> None:
    """Disable single workspace mode for current desktop environment."""
    backend = get_backend(DE)
    if backend:
        func = backend.get("workspace_off")
        if func:
            func()

def set_wallpaper(ws_num: int, image_path: str, scaling: str) -> None:
    """Set wallpaper for specified workspace with given scaling."""
    backend = get_backend(DE)
    if backend:
        func = backend.get("wallpaper")
        if func:
            func(ws_num, image_path, scaling)

def set_panel_icon(icon_path: str) -> None:
    """Set panel/menu icon for current desktop environment."""
    backend = get_backend(DE)
    if backend:
        func = backend.get("icon")
        if func:
            func(icon_path)

def set_themes(ws_num: int, config: Any = None) -> None:
    """Apply theme settings for specified workspace."""
    backend = get_backend(DE)
    if backend:
        func = backend.get("themes")
        if func:
            func(ws_num, config)

def configure_screen_blanking(config: AWPConfig) -> None:
    """Read blanking settings from config and apply via backend."""
    try:
        timeout = int(config.get('general', 'blanking_timeout', 0))
        de = config.get('general', 'os_detected', 'generic')
        backend = get_backend(de)
        if backend and 'configure_blanking' in backend:
            backend['configure_blanking'](timeout)
            logger.info(f"Blanking set to {timeout}s")
    except Exception as e:
        logger.error(f"Failed to configure screen blanking: {e}")

def update_conky_state(workspace_name: str, wallpaper_path: str, config: AWPConfig) -> None:
    """
    Update Conky state file for Lua-HUD integration.
    This is an optional bridge; failures here do not affect the main daemon.
    """
    try:
        state_dict = config.get_conky_state(workspace_name, wallpaper_path)
        with open(CONKY_STATE_PATH, 'w') as f:
            for key, value in state_dict.items():
                f.write(f"{key}={value}\n")
    except Exception as e:
        # We log this as debug so it doesn't clutter the terminal for users not using Conky
        logger.debug(f"Conky bridge update skipped (Optional): {e}")

# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def parse_timing(timing_str: str) -> Optional[int]:
    """Convert timing string (e.g., 30s, 7m, 2h) to seconds."""
    units = {'s': 1, 'm': 60, 'h': 3600}
    try:
        unit = timing_str[-1].lower()
        number = int(timing_str[:-1])
        return number * units.get(unit, 60)
    except Exception:
        return None

def get_current_workspace() -> int:
    """Get current workspace number using xprop."""
    ws_num = subprocess.check_output(
        ["xprop", "-root", "_NET_CURRENT_DESKTOP"], text=True
    ).strip().split()[-1]
    return int(ws_num)

def ensure_awp_dir() -> None:
    """Ensure AWP directory structure exists."""
    if not os.path.isdir(AWP_DIR):
        os.makedirs(AWP_DIR, exist_ok=True)

def load_state() -> dict:
    """Load workspace state from JSON file."""
    if not os.path.isfile(STATE_PATH):
        return {}
    try:
        with open(STATE_PATH, "r") as f:
            return json.load(f)
    except Exception:
        return {}

def save_state(state: dict) -> None:
    """Save workspace state to JSON file using atomic replacement."""
    tmp = STATE_PATH + ".tmp"
    with open(tmp, "w") as f:
        json.dump(state, f)
    os.replace(tmp, STATE_PATH)

def get_ws_key(ws_num: int) -> str:
    """Get workspace key for state storage (e.g., ws1, ws2)."""
    return f"ws{ws_num+1}"

def load_images(folder_path: str) -> List[Path]:
    """Load all JPEG and PNG images from specified folder."""
    p = Path(folder_path)
    if not p.is_dir():
        return []
    return list(p.glob("*.[jJ][pP][gG]")) + list(p.glob("*.[pP][nN][gG]"))

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

# =============================================================================
# WORKSPACE MODEL
# =============================================================================

class Workspace:
    """
    Represents a workspace with its wallpaper configuration and state.
    """
    
    def __init__(self, num: int, config: AWPConfig):
        self.num = num
        self.key = get_ws_key(num)
        self.config = config
        self.reload_images_and_index()
        self.next_switch_time = time.time() + self.timing

    def reload_images_and_index(self) -> None:
        """Reload images and configuration from cached config object."""
        ws_config = self.config.get_workspace_config(self.num)
    
        self.folder = ws_config['folder']
        self.timing_str = ws_config['timing']
        self.timing = parse_timing(self.timing_str) or 60
        self.mode = ws_config['mode']
        self.order = ws_config['order']
        self.scaling = ws_config['scaling']

        # Reload images and index
        self.images = load_images(self.folder)
        if self.mode == 'sequential':
            self.images = sort_images(self.images, self.order)
        else:
            self.images = sort_images(self.images, 'name_az')

        state = load_state()
        self.index = int(state.get(self.key, 0) or 0)
        if not self.images or self.index >= len(self.images):
            self.index = 0

    def pick_next_index(self) -> int:
        """Determine next wallpaper index based on rotation mode."""
        if not self.images:
            return 0
        if self.mode == 'random':
            if len(self.images) == 1:
                return 0
            new_idx = self.index
            while new_idx == self.index:
                new_idx = random.randint(0, len(self.images)-1)
            return new_idx
        return (self.index + 1) % len(self.images)

    def apply_index(self, new_index: int) -> None:
        """Apply new wallpaper index, update state, and optional Conky bridge."""
        state = load_state()
        self.index = new_index
        state[self.key] = self.index
        save_state(state)

        if self.images:
            current_wallpaper_path = str(self.images[self.index])
            set_wallpaper(self.num, current_wallpaper_path, self.scaling)
            
            # =========================================================================
            # CONKY INTEGRATION (OPTIONAL)
            # The daemon updates the state file for the HUD if present.
            # =========================================================================
            update_conky_state(f"ws{self.num+1}", current_wallpaper_path, self.config)

# =============================================================================
# MAIN LOOP
# =============================================================================

def main_loop(workspaces: Dict[int, Workspace], config: AWPConfig):
    """Main daemon loop managing workspace wallpaper rotation."""
    last_ws: Optional[int] = None
    
    while True:
        try:
            now = time.time()
            ws_num = get_current_workspace()
            ws = workspaces.get(ws_num)
            
            if not ws:
                time.sleep(0.5)
                continue

            force_single_workspace_off()

            # Handle Workspace Switch
            if ws_num != last_ws:
                logger.info(f"Switched to Workspace {ws_num+1}")
                ws.reload_images_and_index()
                ws.apply_index(ws.index)
                ws.next_switch_time = now + ws.timing
                
                ws_config = config.get_workspace_config(ws_num)
                if ws_config.get('icon'):
                    set_panel_icon(ws_config['icon'])

                # Apply theme changes on workspace switch
                config.reload()
                set_themes(ws_num, config.config)
                
                last_ws = ws_num

            # Handle Scheduled Rotation
            if now >= ws.next_switch_time:
                ws.reload_images_and_index()
                if ws.images:
                    new_idx = ws.pick_next_index()
                    ws.apply_index(new_idx)
                    logger.info(f"[{datetime.now().strftime('%H:%M:%S')}] WS{ws.num+1}: index -> {ws.index}")
                ws.next_switch_time = now + ws.timing

        except Exception as e:
            logger.error(f"Error in main loop: {e}")
            time.sleep(1)

        time.sleep(0.5)

def main():
    """Main daemon entry point."""
    ensure_awp_dir()
    config = AWPConfig()

    # Set globals for universal desktop functions
    global DE, SESSION_TYPE, BLANKING_PAUSE, BLANKING_TIMEOUT, BLANKING_FORMATTED
    DE = config.de
    SESSION_TYPE = config.session_type
    BLANKING_PAUSE = config.blanking_pause
    BLANKING_TIMEOUT = config.blanking_timeout
    BLANKING_FORMATTED = config.blanking_formatted

    # Initial Setup
    configure_screen_blanking(config)
    force_single_workspace_off()
    
    # Load workspace configurations
    n_ws = config.workspaces_count
    workspaces = {}
    for i in range(n_ws):
        try:
            ws = Workspace(i, config)
            workspaces[ws.num] = ws
        except Exception as e:
            logger.warning(f"Failed to load WS{i+1}: {e}")

    logger.info(f"Loaded {len(workspaces)} workspaces on {DE}. Monitoring...")
    main_loop(workspaces, config)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logger.info("Daemon stopped by user.")
        sys.exit(0)
