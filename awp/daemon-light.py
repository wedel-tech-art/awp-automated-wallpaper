#!/usr/bin/env python3
"""
AWP - Automated Wallpaper Program
Main Daemon Process - NO ROTATION VERSION
- Sets wallpaper on workspace switch
- Does NOT rotate automatically over time
- Preserves all other functionality (themes, icons, config reload, etc.)
"""

import json
import os
import sys
import time
import random
import subprocess
from pathlib import Path
from datetime import datetime

os.environ['NO_AT_BRIDGE'] = '1'

from backends import get_backend
from core.constants import AWP_DIR, STATE_PATH, RUNTIME_STATE_PATH, AWP_CONFIG_RAM
from core.config import AWPConfig, ConfigError
from core.utils import x11_blanking, load_images, sort_images
from core.runtime import update_runtime_state, load_index_state, save_index_state, update_ram_config
from core.actions import (
    get_ws_key,
    get_current_workspace,
    parse_timing,
    set_backend,
    set_wallpaper,
    set_panel_icon,
    show_hud
)
from core.printer import get_printer

# Get printer instance
_printer = get_printer()
_printer.set_backend("daemon")

def optimize_desktop_environment():
    """Universal optimization: Disables heavy desktop managers."""
    backend = get_backend(DE)
    if backend:
        func = backend.get("lean_mode")
        if func:
            _printer.info(f"Initializing Lean Mode for {DE}...", backend="daemon")
            func()

def set_themes(ws_num: int, config=None):
    """Apply theme settings for specified workspace."""
    backend = get_backend(DE)
    if backend:
        func = backend.get("themes")
        if func:
            func(ws_num, config)

def configure_screen_blanking(config):
    """Standard AWP Blanking configuration."""
    x11_blanking(config.blanking_timeout)

# =============================================================================
# WORKSPACE MODEL (Modified - No Rotation Timer)
# =============================================================================

class Workspace:
    """Represents a workspace with its wallpaper configuration - NO ROTATION."""
    
    def __init__(self, num: int, config: AWPConfig):
        self.num = num
        self.key = get_ws_key(num)
        self.config = config

        self.reload_images_and_index()

    def reload_images_and_index(self):
        """Reload images and configuration from cached config."""
        ws_config = self.config.get_workspace_config(self.num)
    
        self.folder = ws_config['folder']
        self.timing_str = ws_config['timing']
        self.timing = parse_timing(self.timing_str) or 60
        self.mode = ws_config['mode']
        self.order = ws_config['order']
        self.scaling = ws_config['scaling']

        # Load & sort images
        self.images = load_images(self.folder)
        if self.mode == 'sequential':
            self.images = sort_images(self.images, self.order)
        else:
            self.images = sort_images(self.images, 'name_az')

        # Load index
        state = load_index_state()
        self.index = int(state.get(self.key, 0) or 0)

        if not self.images or self.index >= len(self.images):
            self.index = 0

        # Track folder mtime (for change detection)
        try:
            self._last_folder_mtime = os.path.getmtime(self.folder)
        except Exception:
            self._last_folder_mtime = 0

    def folder_changed(self) -> bool:
        """Detect if folder contents changed."""
        try:
            current_mtime = os.path.getmtime(self.folder)
        except Exception:
            return False

        if current_mtime != self._last_folder_mtime:
            self._last_folder_mtime = current_mtime
            return True

        return False

    def apply_current_wallpaper(self):
        """Apply the current wallpaper (no rotation, just set it)."""
        if not self.images:
            return
        
        if self.index >= len(self.images):
            self.index = 0
        
        current_wallpaper_path = str(self.images[self.index])
        set_wallpaper(self.num, current_wallpaper_path, self.scaling)

        full_info = self.config.generate_runtime_state(
            f"ws{self.num+1}",
            current_wallpaper_path
        )
        update_runtime_state(full_info)

# =============================================================================
# MAIN LOOP (Modified - No Rotation Timer)
# =============================================================================

def main_loop(workspaces: dict, config: AWPConfig):
    """Refactored daemon: NO rotation timer, only workspace switch handling."""
    global DE, BLANKING_PAUSE, BLANKING_TIMEOUT
    last_ws = None
    
    # Track config file changes
    last_config_mtime = os.path.getmtime(config.path)

    while True:
        now = time.time()
        
        # -------------------------------------------------
        # 1. CONFIG CHANGE DETECTION
        # -------------------------------------------------
        current_mtime = os.path.getmtime(config.path)
        if current_mtime > last_config_mtime:
            _printer.info("Config change detected! Re-Syncing ...", backend="daemon")
            config.reload()
            try:
                full_data = {s: dict(config.config.items(s)) for s in config.config.sections()}
                update_ram_config(full_data)
                _printer.info("RAM Config updated successfully.", backend="daemon")
            except Exception as e:
                _printer.error(f"Failed to sync RAM Config: {e}")
            last_config_mtime = current_mtime
            
            # Backend change
            if config.de != DE:
                _printer.warning(f"Backend switch: {DE} -> {config.de}", backend="daemon")
                DE = config.de
                set_backend(DE)
                optimize_desktop_environment()
            
            # Screen blanking
            configure_screen_blanking(config)
            
            # Reload all workspace internal state
            for ws in workspaces.values():
                ws.reload_images_and_index()

            # Apply current workspace immediately
            ws_num = get_current_workspace()
            ws = workspaces.get(ws_num)

            if ws:
                _printer.info(f"Re-applying current workspace WS{ws_num+1}", backend="daemon")
                ws.reload_images_and_index()
                ws.apply_current_wallpaper()

                ws_config = config.get_workspace_config(ws_num)
                if ws_config['icon']:
                    set_panel_icon(ws_config['icon'])

                set_themes(ws_num, config.config)

        # -------------------------------------------------
        # 2. WORKSPACE SWITCH HANDLING (NO ROTATION TIMER)
        # -------------------------------------------------
        ws_num = get_current_workspace()
        ws = workspaces.get(ws_num)

        if ws and ws_num != last_ws:
            _printer.info(f"Workspace changed to WS{ws_num+1}", backend="daemon")
            
            # Check if folder changed
            if ws.folder_changed():
                _printer.info(f"Folder change detected in WS{ws_num+1}", backend="daemon")
                ws.reload_images_and_index()
            
            # Apply current wallpaper for this workspace
            ws.apply_current_wallpaper()
            
            # Update panel icon
            ws_config = config.get_workspace_config(ws_num)
            if ws_config['icon']:
                set_panel_icon(ws_config['icon'])

            # Apply themes (GTK, icons, cursor, Qt6)
            set_themes(ws_num, config.config)
            
            last_ws = ws_num

        # -------------------------------------------------
        # 3. SLEEP (Simple poll, no rotation timer)
        # -------------------------------------------------
        time.sleep(1)

def main():
    """Main daemon entry point."""
    os.makedirs(AWP_DIR, exist_ok=True)
    config = AWPConfig()
    try:
        full_data = {s: dict(config.config.items(s)) for s in config.config.sections()}
        update_ram_config(full_data)
        _printer.info("RAM Config initialized.", backend="daemon")
    except Exception as e:
        _printer.error(f"Startup RAM Config failed: {e}")

    # Set globals
    global DE, SESSION_TYPE, BLANKING_PAUSE, BLANKING_TIMEOUT, BLANKING_FORMATTED
    DE = config.de
    SESSION_TYPE = config.session_type
    BLANKING_PAUSE = config.blanking_pause
    BLANKING_TIMEOUT = config.blanking_timeout
    BLANKING_FORMATTED = config.blanking_formatted

    set_backend(DE)

    optimize_desktop_environment()
    configure_screen_blanking(config)
    
    n_ws = config.workspaces_count
    workspaces = {}
    for i in range(n_ws):
        try:
            ws = Workspace(i, config)
            workspaces[ws.num] = ws
        except Exception as e:
            print(f"Warning: failed to load ws{i+1}: {e}")

    _printer.info(f"Loaded {len(workspaces)} workspaces. NO ROTATION MODE.", backend="daemon")
    main_loop(workspaces, config)

if __name__ == "__main__":
    main()
