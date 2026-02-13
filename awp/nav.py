#!/usr/bin/env python3
"""
AWP - Automated Wallpaper Program
Navigation Controller - NOW USING CORE ACTIONS FOR HELPERS
"""
import os
import sys
import random
import json
import subprocess
from pathlib import Path

# Optional Qt6 support
try:
    from PyQt6.QtWidgets import QApplication, QMessageBox
    from PyQt6.QtCore import Qt
    HAS_QT = True
except ImportError:
    HAS_QT = False

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from core.constants import AWP_DIR, STATE_PATH, RUNTIME_STATE_PATH
from core.config import AWPConfig
from core.runtime import update_runtime_state
from core.actions import (
    load_images,
    sort_images,
    load_state,
    save_state,
    get_ws_key,
    get_current_workspace,
    set_backend,
    force_single_workspace_off,
    set_wallpaper
)
from backends import get_backend

# =============================================================================
# REMOVED ALL DUPLICATE FUNCTIONS:
# - load_images (now from core.actions)
# - sort_images (now from core.actions)
# - load_state (now from core.actions)
# - save_state (now from core.actions)
# - get_ws_key (now from core.actions)
# - get_current_workspace (now from core.actions)
# - set_wallpaper (now from core.actions)
# - force_single_workspace_off (now from core.actions)
# =============================================================================

DE = None

# =============================================================================
# WALLPAPER DELETION FUNCTIONALITY
# =============================================================================

def universal_confirm_deletion(wallpaper_name: str) -> bool:
    """Display confirmation dialog for wallpaper deletion."""
    if HAS_QT:
        try:
            created_app = False
            app = QApplication.instance()
            if app is None:
                app = QApplication([])
                created_app = True

            msg = QMessageBox()
            msg.setStyleSheet("""
QMessageBox {
    background-color: #2e2e2e;
}
QLabel {
    color: white;
}
QPushButton {
    background-color: #3a3a3a;
    color: white;
    border: 1px solid #555;
    padding: 5px 12px;
}
QPushButton:hover {
    background-color: #4a4a4a;
}
""")
            msg.setIcon(QMessageBox.Icon.Question)
            msg.setWindowTitle("Delete Wallpaper")
            msg.setText("Are you sure you want to delete this wallpaper?")
            msg.setInformativeText(os.path.basename(wallpaper_name))
            msg.setStandardButtons(
                QMessageBox.StandardButton.Yes |
                QMessageBox.StandardButton.No
            )
            msg.setDefaultButton(QMessageBox.StandardButton.No)
            msg.setWindowFlags(
                msg.windowFlags() | Qt.WindowType.WindowStaysOnTopHint
            )

            result = msg.exec()

            if created_app:
                app.quit()

            return result == QMessageBox.StandardButton.Yes

        except Exception as e:
            logging.error(f"Qt confirmation dialog failed: {e}")

    # Fallback to terminal
    print(f"\n🚨 WARNING: About to delete: {os.path.basename(wallpaper_name)}")
    response = input("Type 'DELETE' to confirm, or anything else to cancel: ")
    return response.strip().upper() == "DELETE"

def delete_current_wallpaper_and_advance() -> bool:
    """Delete current wallpaper and advance to next one."""
    ws_num = get_current_workspace()
    ws_key = get_ws_key(ws_num)
    
    config = AWPConfig()
    global DE
    DE = config.de
    set_backend(DE)
    
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
    
    full_info = config.generate_runtime_state(f"ws{ws_num+1}", wallpaper_path)
    update_runtime_state(full_info)
    
    print(f"WS{ws_num+1}: After deletion -> index {new_idx}, wallpaper '{wallpaper_path}'")
    return True

# =============================================================================
# EFFECT PREVIEW
# =============================================================================

def apply_effect_preview(effect: str = "sharpen"):
    """Apply a temporary effect to the current wallpaper."""
    config = AWPConfig()
    global DE
    DE = config.de
    set_backend(DE)

    ws_num = get_current_workspace()
    ws_key = get_ws_key(ws_num)

    state = load_state()
    idx = int(state.get(ws_key, 0) or 0)

    ws_config = config.get_workspace_config(ws_num)
    folder = ws_config['folder']
    mode = ws_config['mode']
    order = ws_config['order']
    scaling = ws_config['scaling']

    imgs = load_images(folder)
    if not imgs:
        logging.error(f"No images in {folder}")
        return

    if mode == 'sequential':
        imgs = sort_images(imgs, order)
    else:
        imgs = sort_images(imgs, 'name_az')

    if idx >= len(imgs):
        idx = 0

    wallpaper_path = str(imgs[idx])

    if not os.path.isfile(wallpaper_path):
        logging.error("Cannot determine current wallpaper path.")
        return

    # Temporary file inside AWP_DIR
    filename = os.path.basename(wallpaper_path)
    temp_file = os.path.join(AWP_DIR, filename)
    os.makedirs(os.path.dirname(temp_file), exist_ok=True)

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

    try:
        subprocess.run(cmd, check=True)
        set_wallpaper(ws_num, temp_file, scaling)
        print(f"Applied temporary effect '{effect}' to wallpaper: {temp_file}")
    except Exception as e:
        logging.error(f"Failed to apply effect '{effect}': {e}")

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
    
    if command in ("sharpen", "black", "color"):
        os.makedirs(AWP_DIR, exist_ok=True)
        apply_effect_preview(command)
        return
    
    if command == "delete":
        os.makedirs(AWP_DIR, exist_ok=True)
        force_single_workspace_off()
        success = delete_current_wallpaper_and_advance()
        sys.exit(0 if success else 1)
    
    direction = command
    os.makedirs(AWP_DIR, exist_ok=True)
    force_single_workspace_off()

    ws_num = get_current_workspace()
    ws_key = get_ws_key(ws_num)

    config = AWPConfig()
    global DE
    DE = config.de
    set_backend(DE)
    
    ws_config = config.get_workspace_config(ws_num)
    folder = ws_config['folder']
    mode = ws_config['mode']
    order = ws_config['order']
    scaling = ws_config['scaling']

    imgs = load_images(folder)
    if not imgs:
        logging.error(f"No images in {folder}")
        sys.exit(1)

    if mode == 'sequential':
        imgs = sort_images(imgs, order)
    else:
        imgs = sort_images(imgs, 'name_az')

    state = load_state()
    idx = int(state.get(ws_key, 0) or 0)
    last_idx = int(state.get(ws_key + '_last', -1) or -1)
    if idx >= len(imgs):
        idx = 0

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

    state[ws_key + '_last'] = idx
    state[ws_key] = new_idx
    save_state(state)

    wallpaper_path = str(imgs[new_idx])
    set_wallpaper(ws_num, wallpaper_path, scaling)
    
    full_info = config.generate_runtime_state(f"ws{ws_num+1}", wallpaper_path)
    update_runtime_state(full_info)
    
    print(f"WS{ws_num+1}: {direction} -> index {new_idx}, scaling '{scaling}', wallpaper '{wallpaper_path}'")

if __name__ == "__main__":
    main()
