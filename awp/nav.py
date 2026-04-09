#!/usr/bin/env python3
"""
AWP - Automated Wallpaper Program
Navigation Controller - OPTIMIZED FOR RAM CONFIG

Changes:
- v2.0: Added RAM-first config loading (fallback to HDD INI)
- Reads from /dev/shm/awp_config_ram.json for faster access on HDD systems
- Falls back to traditional INI file if RAM config is unavailable
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
from core.constants import AWP_DIR, STATE_PATH, RUNTIME_STATE_PATH, AWP_CONFIG_RAM
from core.config import AWPConfig
from core.runtime import update_runtime_state, load_index_state, save_index_state
from core.utils import load_images, sort_images
from core.actions import (
    get_ws_key,
    get_current_workspace,
    set_backend,
    set_wallpaper,
    show_hud
)
from backends import get_backend
from core.printer import get_printer

# Initialize printer
_printer = get_printer()

DE = None


# =============================================================================
# CONFIGURATION LOADING (RAM-first with HDD fallback)
# =============================================================================

def get_config():
    """
    Load configuration from RAM disk first, fallback to HDD INI.
    
    Returns:
        configparser.ConfigParser: Configuration object with all sections
    
    Performance:
        RAM disk: ~0.1ms (no disk seek)
        HDD INI: ~10-20ms (fallback, disk seek)
    """
    # Attempt to load from RAM disk (fast path)
    try:
        with open(AWP_CONFIG_RAM, "r") as f:
            config_dict = json.load(f)
        
        # Convert JSON dict to ConfigParser object
        from configparser import ConfigParser
        config = ConfigParser()
        for section, values in config_dict.items():
            config[section] = values
        
        _printer.info(f"Config loaded from RAM ({len(config_dict)} sections)", backend="nav")
        return config
        
    except FileNotFoundError:
        _printer.warning("RAM config not found (/dev/shm/awp_config_ram.json)", backend="nav")
    except json.JSONDecodeError as e:
        _printer.warning(f"RAM config JSON decode error: {e}", backend="nav")
    except Exception as e:
        _printer.warning(f"RAM config error: {e}, falling back to INI", backend="nav")
    
    # Fallback to traditional HDD INI file (slow path)
    try:
        from core.config import AWPConfig
        awp = AWPConfig()
        _printer.info("Config loaded from INI (HDD fallback)", backend="nav")
        return awp.config
    except Exception as e:
        _printer.error(f"Failed to load config from INI: {e}", backend="nav")
        raise


def get_awpconfig_instance():
    """
    Create AWPConfig instance with RAM-loaded config.
    Used for methods that need the full AWPConfig object.
    
    Returns:
        AWPConfig: Configured AWPConfig instance
    """
    awp = AWPConfig()
    awp.config = get_config()  # Override with RAM-loaded config
    return awp


# =============================================================================
# WALLPAPER DELETION FUNCTIONALITY
# =============================================================================

def universal_confirm_deletion(wallpaper_name: str) -> bool:
    """
    Display confirmation dialog for wallpaper deletion.
    
    Args:
        wallpaper_name: Path to wallpaper file
    
    Returns:
        bool: True if user confirmed deletion, False otherwise
    """
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
            _printer.error(f"Qt confirmation dialog failed: {e}", backend="nav")

    # Fallback to terminal confirmation
    _printer.warning(f"About to delete: {os.path.basename(wallpaper_name)}", backend="nav")
    response = input("Type 'DELETE' to confirm, or anything else to cancel: ")
    return response.strip().upper() == "DELETE"


def delete_current_wallpaper_and_advance() -> bool:
    """
    Delete current wallpaper and advance to next one.
    
    Returns:
        bool: True if successful, False otherwise
    """
    ws_num = get_current_workspace()
    ws_key = get_ws_key(ws_num)
    
    # Use RAM-loaded config
    config_parser = get_config()
    global DE
    DE = config_parser.get('general', 'os_detected', fallback='qtile_xfce')
    set_backend(DE)
    
    state = load_index_state()
    
    # Get workspace configuration
    section = f"ws{ws_num + 1}"
    if not config_parser.has_section(section):
        _printer.error(f"Section {section} not found in config", backend="nav")
        return False
    
    folder = config_parser.get(section, 'folder')
    mode = config_parser.get(section, 'mode', fallback='sequential')
    order = config_parser.get(section, 'order', fallback='name_az')
    scaling = config_parser.get(section, 'scaling', fallback='zoomed')
    
    # Load and sort images
    imgs = load_images(folder)
    if not imgs:
        _printer.error(f"No images in {folder}", backend="nav")
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
        _printer.info("Deletion cancelled", backend="nav")
        return False
    
    # Delete the file
    try:
        os.remove(current_wallpaper)
        _printer.info(f"Deleted: {os.path.basename(current_wallpaper)}", backend="nav")
    except Exception as e:
        _printer.error(f"Failed to delete {current_wallpaper}: {e}", backend="nav")
        return False
    
    # Reload images after deletion
    imgs = load_images(folder)
    if not imgs:
        _printer.warning("No wallpapers left after deletion", backend="nav")
        return True
    
    if mode == 'sequential':
        imgs = sort_images(imgs, order)
    else:
        imgs = sort_images(imgs, 'name_az')
    
    # Calculate new index based on mode
    if mode == 'random':
        if len(imgs) == 1:
            new_idx = 0
        else:
            new_idx = current_idx
            while new_idx == current_idx and len(imgs) > 1:
                new_idx = random.randint(0, len(imgs) - 1)
    else:  # sequential
        new_idx = current_idx % len(imgs)
    
    # Update state
    state[ws_key + '_last'] = current_idx
    state[ws_key] = new_idx
    save_index_state(state)
    
    # Set new wallpaper
    wallpaper_path = str(imgs[new_idx])
    set_wallpaper(ws_num, wallpaper_path, scaling)
    
    # Update runtime state for HUDs
    awp = get_awpconfig_instance()
    full_info = awp.generate_runtime_state(f"ws{ws_num + 1}", wallpaper_path)
    update_runtime_state(full_info)
    
    # Trigger HUD
    show_hud()
    
    _printer.info(f"WS{ws_num + 1}: After deletion -> index {new_idx}", backend="nav")
    return True


# =============================================================================
# EFFECT PREVIEW
# =============================================================================

def apply_effect_preview(effect: str = "sharpen"):
    """
    Apply a temporary effect to the current wallpaper.
    
    Args:
        effect: Effect type ('sharpen', 'black', 'color')
    """
    # Use RAM-loaded config
    config_parser = get_config()
    global DE
    DE = config_parser.get('general', 'os_detected', fallback='qtile_xfce')
    set_backend(DE)

    ws_num = get_current_workspace()
    ws_key = get_ws_key(ws_num)
    section = f"ws{ws_num + 1}"

    if not config_parser.has_section(section):
        _printer.error(f"Section {section} not found", backend="nav")
        return

    state = load_index_state()
    idx = int(state.get(ws_key, 0) or 0)

    folder = config_parser.get(section, 'folder')
    mode = config_parser.get(section, 'mode', fallback='sequential')
    order = config_parser.get(section, 'order', fallback='name_az')
    scaling = config_parser.get(section, 'scaling', fallback='zoomed')

    imgs = load_images(folder)
    if not imgs:
        _printer.error(f"No images in {folder}", backend="nav")
        return

    if mode == 'sequential':
        imgs = sort_images(imgs, order)
    else:
        imgs = sort_images(imgs, 'name_az')

    if idx >= len(imgs):
        idx = 0

    wallpaper_path = str(imgs[idx])

    if not os.path.isfile(wallpaper_path):
        _printer.error("Cannot determine current wallpaper path.", backend="nav")
        return

    # Create temporary file for effect
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
        _printer.error(f"Unknown effect: {effect}", backend="nav")
        return

    cmd.append(temp_file)

    try:
        subprocess.run(cmd, check=True)
        set_wallpaper(ws_num, temp_file, scaling)
        _printer.info(f"Applied temporary effect '{effect}' to wallpaper", backend="nav")
    except Exception as e:
        _printer.error(f"Failed to apply effect '{effect}': {e}", backend="nav")


def park_current():
    """
    Park at current indexed wallpaper (no rotation, just apply).
    Used when switching workspaces to restore the correct wallpaper.
    """
    # Use RAM-loaded config
    config_parser = get_config()
    global DE
    DE = config_parser.get('general', 'os_detected', fallback='qtile_xfce')
    set_backend(DE)
    
    ws_num = get_current_workspace()
    ws_key = get_ws_key(ws_num)
    section = f"ws{ws_num + 1}"

    if not config_parser.has_section(section):
        _printer.error(f"Section {section} not found", backend="nav")
        return
    
    folder = config_parser.get(section, 'folder')
    mode = config_parser.get(section, 'mode', fallback='sequential')
    order = config_parser.get(section, 'order', fallback='name_az')
    scaling = config_parser.get(section, 'scaling', fallback='zoomed')
    
    imgs = load_images(folder)
    if not imgs:
        _printer.error(f"No images in {folder}", backend="nav")
        return
    
    if mode == 'sequential':
        imgs = sort_images(imgs, order)
    else:
        imgs = sort_images(imgs, 'name_az')
    
    state = load_index_state()
    idx = int(state.get(ws_key, 0) or 0)
    
    if idx >= len(imgs):
        idx = 0
    
    # === FIX: Save the index to initialize workspace in indexes.json ===
    state[ws_key] = idx
    save_index_state(state)
    # === END FIX ===
    
    # Apply the wallpaper (no rotation, just park)
    wallpaper_path = str(imgs[idx])
    set_wallpaper(ws_num, wallpaper_path, scaling)
    
    # Update runtime state for HUDs
    awp = get_awpconfig_instance()
    full_info = awp.generate_runtime_state(f"ws{ws_num + 1}", wallpaper_path)
    update_runtime_state(full_info)
    
    # Trigger HUD (commented for faster workspace switching)
    # show_hud()
    
    _printer.info(f"WS{ws_num + 1}: Parked at index {idx}", backend="nav")


def main():
    """Main navigation controller entry point."""
    allowed = ("next", "prev", "delete", "sharpen", "black", "color", "park")
    if len(sys.argv) != 2 or sys.argv[1] not in allowed:
        _printer.error(f"Usage: {sys.argv[0]} " + " | ".join(allowed), backend="nav")
        sys.exit(1)

    command = sys.argv[1]

    # --- 1. INITIALIZE CONFIG & BACKEND (RAM-first) ---
    # Load configuration from RAM disk (fast) or HDD fallback
    config_parser = get_config()
    global DE
    DE = config_parser.get('general', 'os_detected', fallback='qtile_xfce')
    set_backend(DE)

    # --- 2. TEMPORAL EFFECTS ---
    if command in ("sharpen", "black", "color"):
        os.makedirs(AWP_DIR, exist_ok=True)
        _printer.info(f"Applying effect: {command}", backend="nav")
        apply_effect_preview(command)
        return
    
    # --- 3. PARK (Restore current wallpaper) ---
    if command == "park":
        os.makedirs(AWP_DIR, exist_ok=True)
        _printer.info("Parking wallpaper...", backend="nav")
        park_current()
        return
    
    # --- 4. DELETION ---
    if command == "delete":
        os.makedirs(AWP_DIR, exist_ok=True)
        _printer.info("Deleting current wallpaper...", backend="nav")
        success = delete_current_wallpaper_and_advance()
        sys.exit(0 if success else 1)
    
    # --- 5. NAVIGATION (NEXT/PREV) ---
    direction = command
    os.makedirs(AWP_DIR, exist_ok=True)

    ws_num = get_current_workspace()
    ws_key = get_ws_key(ws_num)
    section = f"ws{ws_num + 1}"

    if not config_parser.has_section(section):
        _printer.error(f"Section {section} not found in config", backend="nav")
        sys.exit(1)

    folder = config_parser.get(section, 'folder')
    mode = config_parser.get(section, 'mode', fallback='sequential')
    order = config_parser.get(section, 'order', fallback='name_az')
    scaling = config_parser.get(section, 'scaling', fallback='zoomed')

    # Load and sort images
    imgs = load_images(folder)
    if not imgs:
        _printer.error(f"No images in {folder}", backend="nav")
        sys.exit(1)

    if mode == 'sequential':
        imgs = sort_images(imgs, order)
    else:
        imgs = sort_images(imgs, 'name_az')

    # Get current index from state
    state = load_index_state()
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
                    new_idx = random.randint(0, len(imgs) - 1)
        else:
            new_idx = (idx + 1) % len(imgs)
    else:  # prev
        if mode == 'random':
            new_idx = last_idx if 0 <= last_idx < len(imgs) else idx
        else:
            new_idx = (idx - 1) % len(imgs)

    # Update state (indexes.json)
    state[ws_key + '_last'] = idx
    state[ws_key] = new_idx
    save_index_state(state)

    # Apply the wallpaper via backend
    wallpaper_path = str(imgs[new_idx])
    set_wallpaper(ws_num, wallpaper_path, scaling)
    
    # Update runtime state for HUDs
    awp = get_awpconfig_instance()
    full_info = awp.generate_runtime_state(f"ws{ws_num + 1}", wallpaper_path)
    update_runtime_state(full_info)
    
    # Trigger HUD (commented for faster response)
    # show_hud()
    
    _printer.info(f"WS{ws_num + 1}: {direction} wallpaper changed", backend="nav")


if __name__ == "__main__":
    main()
