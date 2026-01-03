#!/usr/bin/env python3
"""
AWP - Automated Wallpaper Program
Navigation Controller (awp_nav.py)

Provides manual wallpaper navigation with five commands:
  - next: Switch to next wallpaper
  - prev: Switch to previous wallpaper  
  - delete: Delete current wallpaper and advance to next
  - sharpen: Apply sharpen effect temporarily
  - black: Apply black & white effect temporarily
  - color: Apply color boost effect temporarily

Can be bound to keyboard shortcuts for quick wallpaper control.
Part of the AWP wallpaper automation system.
"""
import os
import sys
import random
import json
import subprocess
from pathlib import Path
import logging

try:
    from PyQt5.QtWidgets import QApplication, QMessageBox
    from PyQt5.QtCore import Qt
    HAS_QT = True
except ImportError:
    HAS_QT = False

# =============================================================================
# CONFIGURATION
# =============================================================================
logging.basicConfig(level=logging.ERROR, format="%(asctime)s - %(levelname)s - %(message)s")

# =============================================================================
# CORE IMPORTS
# =============================================================================
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from core.constants import AWP_DIR, STATE_PATH, CONKY_STATE_PATH
from core.config import AWPConfig
from backends import get_backend

DE = None

# =============================================================================
# UNIVERSAL DESKTOP FUNCTIONS
# =============================================================================

def force_single_workspace_off():
    """Disable single workspace mode for current desktop environment."""
    global DE
    backend = get_backend(DE)
    if backend:
        func = backend.get("workspace_off")
        if func:
            func()

def set_wallpaper(ws_num: int, image_path: str, scaling: str):
    """Set wallpaper for specified workspace with given scaling."""
    global DE
    backend = get_backend(DE)
    if backend:
        func = backend.get("wallpaper")
        if func:
            func(ws_num, image_path, scaling)

# =============================================================================
# CONKY INTEGRATION
# =============================================================================

def update_conky_state(workspace_name: str, wallpaper_path: str, config: AWPConfig):
    """
    Update Conky state file with current workspace and wallpaper information.
    """
    state_dict = config.get_conky_state(workspace_name, wallpaper_path)
    try:
        with open(CONKY_STATE_PATH, 'w') as f:
            for key, value in state_dict.items():
                f.write(f"{key}={value}\n")
    except OSError as e:
        logging.error(f"Failed to write Conky state file {CONKY_STATE_PATH}: {e}")

# =============================================================================
# WALLPAPER DELETION FUNCTIONALITY
# =============================================================================

def universal_confirm_deletion(wallpaper_name: str) -> bool:
    """
    Display confirmation dialog for wallpaper deletion.
    """
    if HAS_QT:
        try:
            app = QApplication.instance()
            if app is None:
                app = QApplication([])
            
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Question)
            msg.setWindowTitle("Delete Wallpaper")
            msg.setText(f"Are you sure you want to delete this wallpaper?")
            msg.setInformativeText(os.path.basename(wallpaper_name))
            msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
            msg.setDefaultButton(QMessageBox.No)
            msg.setWindowFlags(msg.windowFlags() | Qt.WindowStaysOnTopHint)
            
            result = msg.exec_()
            return result == QMessageBox.Yes
            
        except Exception as e:
            logging.error(f"Qt confirmation dialog failed: {e}")
    
    # Fallback to terminal
    print(f"\n🚨 WARNING: About to delete: {os.path.basename(wallpaper_name)}")
    response = input("Type 'DELETE' to confirm, or anything else to cancel: ")
    return response.strip().upper() == "DELETE"

def delete_current_wallpaper_and_advance() -> bool:
    """
    Delete current wallpaper and advance to next one.
    """
    ws_num = get_current_workspace()
    ws_key = get_ws_key(ws_num)
    
    # Load config and state
    config = AWPConfig()
    global DE
    DE = config.de
    
    state = load_state()
    ws_config = config.get_workspace_config(ws_num)
    
    folder = ws_config['folder']
    mode = ws_config['mode']
    order = ws_config['order']
    scaling = ws_config['scaling']
    
    # Get current images and index
    imgs = load_images(folder)
    if not imgs:
        logging.error(f"No images in {folder}")
        return False
    
    if mode == 'sequential':
        imgs = sort_images(imgs, order)
    else:
        imgs = sort_images(imgs, 'name_az')
    
    current_idx = int(state.get(ws_key, 0) or 0)
    if current_idx >= len(imgs):
        current_idx = 0
    
    current_wallpaper = imgs[current_idx]
    
    # Confirm deletion
    if not universal_confirm_deletion(str(current_wallpaper)):
        print("Deletion cancelled")
        return False
    
    # Delete the file
    try:
        os.remove(current_wallpaper)
        print(f"Deleted: {current_wallpaper}")
    except Exception as e:
        logging.error(f"Failed to delete {current_wallpaper}: {e}")
        return False
    
    # Reload images and re-sort
    imgs = load_images(folder)
    if not imgs:
        logging.error("No wallpapers left after deletion")
        return True
    
    if mode == 'sequential':
        imgs = sort_images(imgs, order)
    else:
        imgs = sort_images(imgs, 'name_az')
    
    # Calculate new index
    if mode == 'random':
        if len(imgs) == 1:
            new_idx = 0
        else:
            new_idx = current_idx
            while new_idx == current_idx and len(imgs) > 1:
                new_idx = random.randint(0, len(imgs)-1)
    else:  # sequential
        new_idx = current_idx % len(imgs)
    
    # Update state
    state[ws_key + '_last'] = current_idx
    state[ws_key] = new_idx
    save_state(state)
    
    # Set new wallpaper
    wallpaper_path = str(imgs[new_idx])
    set_wallpaper(ws_num, wallpaper_path, scaling)
    update_conky_state(f"ws{ws_num+1}", wallpaper_path, config)
    
    print(f"WS{ws_num+1}: After deletion -> index {new_idx}, wallpaper '{wallpaper_path}'")
    return True

# =============================================================================
# EFFECT PREVIEW
# =============================================================================

def apply_effect_preview(effect: str = "sharpen"):
    """
    Apply a temporary effect to the current wallpaper.
    """
    config = AWPConfig()
    global DE
    DE = config.de
    
    ws_num = get_current_workspace()

    # Read current wallpaper from Conky state
    wallpaper_path = None
    if os.path.isfile(CONKY_STATE_PATH):
        try:
            with open(CONKY_STATE_PATH, "r") as f:
                for line in f:
                    if line.startswith("wallpaper_path="):
                        wallpaper_path = line.strip().split("=", 1)[1]
                        break
        except Exception as e:
            logging.error(f"Failed to read Conky state: {e}")

    if not wallpaper_path or not os.path.isfile(wallpaper_path):
        logging.error("Cannot determine current wallpaper path.")
        return

    # Temporary file
    filename = os.path.basename(wallpaper_path)
    temp_file = os.path.join(AWP_DIR, filename)
    os.makedirs(os.path.dirname(temp_file), exist_ok=True)

    # Build ImageMagick command
    cmd = ["convert", wallpaper_path]
    if effect == "sharpen":
        cmd += ["-unsharp", "0x2+0.8+0"]
    elif effect == "black":
        cmd += ["-modulate", "100,0,100"]
    elif effect == "color":
        cmd += ["-modulate", "100,130,100"]
    else:
        logging.error(f"Unknown effect: {effect}")
        return

    cmd.append(temp_file)

    # Apply effect
    try:
        subprocess.run(cmd, check=True)
        ws_config = config.get_workspace_config(ws_num)
        set_wallpaper(ws_num, temp_file, ws_config['scaling'])
        print(f"Applied temporary effect '{effect}' to wallpaper: {temp_file}")
    except Exception as e:
        logging.error(f"Failed to apply effect '{effect}': {e}")

# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def get_current_workspace() -> int:
    """Get current workspace number using xprop."""
    try:
        ws_num = subprocess.check_output(
            ["xprop", "-root", "_NET_CURRENT_DESKTOP"], text=True
        ).strip().split()[-1]
        return int(ws_num)
    except Exception as e:
        logging.error(f"Could not determine current workspace: {e}")
        sys.exit(1)

def get_ws_key(ws_num: int) -> str:
    """Get workspace key for state storage."""
    return f"ws{ws_num+1}"

def load_state() -> dict:
    """Load workspace state from JSON file."""
    if not os.path.isfile(STATE_PATH):
        logging.error(f"State file {STATE_PATH} not found")
        return {}
    try:
        with open(STATE_PATH, "r") as f:
            return json.load(f)
    except Exception as e:
        logging.error(f"Failed to load state file {STATE_PATH}: {e}")
        return {}

def save_state(state: dict):
    """Save workspace state to JSON file."""
    tmp = STATE_PATH + ".tmp"
    try:
        with open(tmp, "w") as f:
            json.dump(state, f)
        os.replace(tmp, STATE_PATH)
    except Exception as e:
        logging.error(f"Failed to save state file {STATE_PATH}: {e}")

def load_images(folder_path: str) -> list:
    """Load all JPEG and PNG images from specified folder."""
    p = Path(folder_path)
    if not p.is_dir():
        logging.error(f"Folder {folder_path} is not a directory")
        return []
    return list(p.glob("*.[jJ][pP][gG]")) + list(p.glob("*.[pP][nN][gG]"))

def sort_images(images: list, order_key: str) -> list:
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
# MAIN EXECUTION
# =============================================================================

def main():
    """Main navigation controller entry point."""
    allowed = ("next", "prev", "delete", "sharpen", "black", "color")
    if len(sys.argv) != 2 or sys.argv[1] not in allowed:
        print(f"Usage: {sys.argv[0]} " + " | ".join(allowed))
        sys.exit(1)

    command = sys.argv[1]
    
    # Handle effect commands
    if command in ("sharpen", "black", "color"):
        os.makedirs(AWP_DIR, exist_ok=True)
        apply_effect_preview(command)
        return
    
    # Handle deletion command
    if command == "delete":
        os.makedirs(AWP_DIR, exist_ok=True)
        force_single_workspace_off()
        success = delete_current_wallpaper_and_advance()
        sys.exit(0 if success else 1)
    
    # Handle next/prev navigation commands
    direction = command
    os.makedirs(AWP_DIR, exist_ok=True)
    force_single_workspace_off()

    ws_num = get_current_workspace()
    ws_key = get_ws_key(ws_num)

    # Load configuration using AWPConfig
    config = AWPConfig()
    global DE
    DE = config.de
    
    ws_config = config.get_workspace_config(ws_num)
    folder = ws_config['folder']
    mode = ws_config['mode']
    order = ws_config['order']
    scaling = ws_config['scaling']

    # Load and sort images
    imgs = load_images(folder)
    if not imgs:
        logging.error(f"No images in {folder}")
        sys.exit(1)

    if mode == 'sequential':
        imgs = sort_images(imgs, order)
    else:
        imgs = sort_images(imgs, 'name_az')

    # Load state and calculate new index
    state = load_state()
    idx = int(state.get(ws_key, 0) or 0)
    last_idx = int(state.get(ws_key + '_last', -1) or -1)
    if idx >= len(imgs):
        idx = 0

    # Calculate new index based on direction and mode
    if direction == "next":
        if mode == 'random':
            if len(imgs) == 1:
                new_idx = 0
            else:
                new_idx = idx
                while new_idx == idx:
                    new_idx = random.randint(0, len(imgs)-1)
        else:
            new_idx = (idx + 1) % len(imgs)
    else:  # prev
        if mode == 'random':
            new_idx = last_idx if last_idx >= 0 and last_idx < len(imgs) else idx
        else:
            new_idx = (idx - 1) % len(imgs)

    # Update state and apply changes
    state[ws_key + '_last'] = idx
    state[ws_key] = new_idx
    save_state(state)

    # Apply new wallpaper and update Conky
    wallpaper_path = str(imgs[new_idx])
    set_wallpaper(ws_num, wallpaper_path, scaling)
    
    # CONKY INTEGRATION (OPTIONAL)
    # Uncomment the line below to enable real-time wallpaper info for Conky
    update_conky_state(f"ws{ws_num+1}", wallpaper_path, config)
    
    print(f"WS{ws_num+1}: {direction} -> index {new_idx}, scaling '{scaling}', wallpaper '{wallpaper_path}'")

if __name__ == "__main__":
    main()
