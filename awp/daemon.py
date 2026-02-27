#!/usr/bin/env python3
"""
AWP - Automated Wallpaper Program
Main Daemon Process - NOW USING CORE ACTIONS FOR HELPERS
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
from core.constants import AWP_DIR, STATE_PATH, RUNTIME_STATE_PATH
from core.config import AWPConfig, ConfigError
from core.utils import x11_blanking
from core.runtime import update_runtime_state
from core.actions import (
    load_images,
    sort_images,
    load_state,
    save_state,
    get_ws_key,
    get_current_workspace,
    parse_timing,
    set_backend,
    force_single_workspace_off,
    set_wallpaper,
    set_panel_icon,
    show_hud
)

def optimize_desktop_environment():
    """Universal optimization: Disables heavy desktop managers."""
    backend = get_backend(DE)
    if backend:
        func = backend.get("lean_mode")
        if func:
            print(f"[AWP] Initializing Lean Mode for {DE}...")
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
# WORKSPACE MODEL
# =============================================================================

class Workspace:
    """Represents a workspace with its wallpaper configuration and state."""
    
    def __init__(self, num: int, config: AWPConfig):
        self.num = num
        self.key = get_ws_key(num)
        self.config = config
        self.reload_images_and_index()
        self.next_switch_time = time.time() + self.timing

    def reload_images_and_index(self):
        """Reload images and configuration from cached config."""
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

    def apply_index(self, new_index: int):
        """Apply new wallpaper index and update runtime state."""
        state = load_state()
        self.index = new_index
        state[self.key] = self.index
        save_state(state)

        current_wallpaper_path = str(self.images[self.index])
        set_wallpaper(self.num, current_wallpaper_path, self.scaling)  # Now using imported function

        full_info = self.config.generate_runtime_state(
            f"ws{self.num+1}",
            current_wallpaper_path
        )
        update_runtime_state(full_info)

# =============================================================================
# MAIN LOOP
# =============================================================================

def main_loop(workspaces: dict, config: AWPConfig):
    """Refactored daemon: Logic first, Execution last."""
    last_ws = None
    while True:
        now = time.time()
        ws_num = get_current_workspace()
        ws = workspaces.get(ws_num)
        change_required = False

        if ws:
            force_single_workspace_off()

            # 1. Workspace Changed
            if ws_num != last_ws:
                ws.reload_images_and_index()
                ws.apply_index(ws.index)
                
                ws_config = config.get_workspace_config(ws_num)
                if ws_config['icon']:
                    set_panel_icon(ws_config['icon'])

                config.reload()
                set_themes(ws_num, config.config)
                
                ws.next_switch_time = now + ws.timing
                last_ws = ws_num
                change_required = True

            # 2. LOGIC: Timer Expired (Auto-Rotate)
            elif now >= ws.next_switch_time:
                # IMPORTANT: We reload FIRST to see if nav.py changed anything
                ws.reload_images_and_index()
                
                if ws.images:
                    ws.index = ws.pick_next_index()
                    
                    # SYNC: We must save like nav.py does!
                    from core.actions import load_state, save_state
                    state = load_state()
                    state[f"ws{ws.num+1}"] = ws.index
                    save_state(state)
                    
                    ws.apply_index(ws.index)
                    change_required = True # This triggers the HUD below
                
                ws.next_switch_time = now + ws.timing

            # 3. Execution
            #if change_required:
                #show_hud()

        time.sleep(2)

def main():
    """Main daemon entry point."""
    os.makedirs(AWP_DIR, exist_ok=True)
    config = AWPConfig()

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
    force_single_workspace_off()
    
    n_ws = config.workspaces_count
    workspaces = {}
    for i in range(n_ws):
        try:
            ws = Workspace(i, config)
            workspaces[ws.num] = ws
        except Exception as e:
            print(f"Warning: failed to load ws{i+1}: {e}")

    print(f"Loaded {len(workspaces)} workspaces. State: {STATE_PATH}")
    main_loop(workspaces, config)

if __name__ == "__main__":
    main()
