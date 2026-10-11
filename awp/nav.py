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
import numpy as np
from PIL import Image
from pathlib import Path
from configparser import ConfigParser

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
from core.utils import load_images, sort_images, hex_to_hls
from core.actions import (
    get_ws_key,
    get_current_workspace,
    get_workspace_images,
    get_workspace_index,
    set_backend,
    set_wallpaper,
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

def load_current_workspace_context():
    """
    Load everything needed to operate on the current workspace.

    Returns a dict with:
        awp:      AWPConfig instance (RAM-loaded)
        de:       detected desktop environment
        ws_num:   current workspace index (0-based)
        ws_key:   e.g. "ws1"
        section:  e.g. "ws1"
        config:   workspace config dict (folder, mode, order, scaling, icon_color, ...)
        imgs:     list of sorted image Paths
        idx:      current index into imgs
    Or None on error.
    """
    awp = get_awpconfig_instance()

    # Detect desktop environment and set the backend
    global DE
    DE = awp.de
    set_backend(DE)

    ws_num = get_current_workspace()
    ws_key = get_ws_key(ws_num)
    section = f"ws{ws_num + 1}"

    # Workspace config from AWPConfig (has its own fallbacks)
    ws_config = awp.get_workspace_config(ws_num)
    
    imgs, mode = get_workspace_images(ws_config)
    if not imgs:
        _printer.error(f"No images in {ws_config['folder']}", backend="nav")
        return None

    idx = get_workspace_index(ws_num, imgs)

    return {
        "awp": awp,
        "de": DE,
        "ws_num": ws_num,
        "ws_key": ws_key,
        "section": section,
        "config": ws_config,
        "imgs": imgs,
        "idx": idx,
    }

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
    ctx = load_current_workspace_context()
    if not ctx:
        return False

    ws_num = ctx["ws_num"]
    ws_key = ctx["ws_key"]
    mode = ctx["config"]["mode"]
    scaling = ctx["config"]["scaling"]
    imgs = ctx["imgs"]
    current_idx = ctx["idx"]

    current_wallpaper = imgs[current_idx]

    if not universal_confirm_deletion(str(current_wallpaper)):
        _printer.info("Deletion cancelled", backend="nav")
        return False

    try:
        os.remove(current_wallpaper)
        _printer.info(f"Deleted: {os.path.basename(current_wallpaper)}", backend="nav")
    except Exception as e:
        _printer.error(f"Failed to delete {current_wallpaper}: {e}", backend="nav")
        return False

    # Reload images after deletion
    imgs, _ = get_workspace_images(ctx["config"])
    if not imgs:
        _printer.warning("No wallpapers left after deletion", backend="nav")
        return True

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

    state = load_index_state()
    state[ws_key + '_last'] = current_idx
    state[ws_key] = new_idx
    save_index_state(state)

    wallpaper_path = str(imgs[new_idx])
    set_wallpaper(ws_num, wallpaper_path, scaling)

    full_info = ctx["awp"].generate_runtime_state(f"ws{ws_num + 1}", wallpaper_path)
    update_runtime_state(full_info)

    _printer.info(f"WS{ws_num + 1}: After deletion -> index {new_idx}", backend="nav")
    return True


# =============================================================================
# EFFECT PREVIEW
# =============================================================================

def _apply_tint_pil(image_path, target_hex, output_path, target_saturation=None):
    """
    Mimic GIMP's Colorize: replace every pixel's hue and saturation
    with the target's, keeping the original luminance.

    target_saturation: 0-1. If None, uses the target color's own saturation.
    """
    clean = target_hex.lstrip("#")
    target_h, target_l, target_s = hex_to_hls(clean)

    if target_saturation is None:
        target_saturation = target_s * 0.6

    # Load image, convert to grayscale to get luminance
    img = Image.open(image_path).convert("L")
    luminance = np.array(img, dtype=np.float32) / 255.0  # 0-1

    # Build HSL arrays: H and S constant, L from luminance
    # Convert to RGB using PIL's HSV or manual math
    # (colorsys per-pixel would be slow; use vectorized conversion)

    # Simplest: convert each pixel via HSV
    # H = target_h, S = target_saturation, V = luminance
    # Then HSV → RGB

    # Vectorized HSV → RGB for constant H, S:
    h = target_h * 6.0                    # 0-6
    i = int(h)                            # sector 0-5
    f = h - i                             # fractional part
    p = luminance * (1 - target_saturation)
    q = luminance * (1 - target_saturation * f)
    t = luminance * (1 - target_saturation * (1 - f))
    v = luminance

    # Select RGB based on sector
    r = np.zeros_like(luminance)
    g = np.zeros_like(luminance)
    b = np.zeros_like(luminance)

    if i == 0:
        r, g, b = v, t, p
    elif i == 1:
        r, g, b = q, v, p
    elif i == 2:
        r, g, b = p, v, t
    elif i == 3:
        r, g, b = p, q, v
    elif i == 4:
        r, g, b = t, p, v
    else:
        r, g, b = v, p, q

    rgb = np.stack([r, g, b], axis=-1)
    result = Image.fromarray((rgb * 255).astype(np.uint8), mode="RGB")
    result.save(output_path)
    return True

def apply_effect_preview(effect: str = "sharpen"):
    """
    Apply a temporary effect to the current wallpaper.

    Args:
        effect: Effect type ('sharpen', 'black', 'color', 'tint')
    """
    ctx = load_current_workspace_context()
    if not ctx:
        return

    ws_num = ctx["ws_num"]
    scaling = ctx["config"]["scaling"]
    wallpaper_path = str(ctx["imgs"][ctx["idx"]])

    if not os.path.isfile(wallpaper_path):
        _printer.error("Cannot determine current wallpaper path.", backend="nav")
        return

    filename = os.path.basename(wallpaper_path)
    temp_file = os.path.join(AWP_DIR, filename)
    os.makedirs(os.path.dirname(temp_file), exist_ok=True)

    # ─── Tint: uses PIL, returns early ───
    if effect == "tint":
        accent_hex = ctx["config"].get('icon_color', None)
        if not accent_hex:
            _printer.error("No icon_color for this workspace", backend="nav")
            return
        if not accent_hex.startswith("#"):
            accent_hex = f"#{accent_hex}"

        try:
            ok = _apply_tint_pil(wallpaper_path, accent_hex, temp_file)
            if not ok:
                _printer.error("Tint failed", backend="nav")
                return
            set_wallpaper(ws_num, temp_file, scaling)
            _printer.info(f"Applied temporary effect '{effect}' to wallpaper", backend="nav")
        except Exception as e:
            _printer.error(f"Failed to apply tint: {e}", backend="nav")
        return

    # ─── ImageMagick effects ───
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
    ctx = load_current_workspace_context()
    if not ctx:
        return

    ws_num = ctx["ws_num"]
    ws_key = ctx["ws_key"]
    idx = ctx["idx"]
    scaling = ctx["config"]["scaling"]
    imgs = ctx["imgs"]

    state = load_index_state()
    state[ws_key] = idx
    save_index_state(state)

    wallpaper_path = str(imgs[idx])
    set_wallpaper(ws_num, wallpaper_path, scaling)

    full_info = ctx["awp"].generate_runtime_state(f"ws{ws_num + 1}", wallpaper_path)
    update_runtime_state(full_info)

    _printer.info(f"WS{ws_num + 1}: Parked at index {idx}", backend="nav")


def main():
    """Main navigation controller entry point."""
    allowed = ("next", "prev", "delete", "sharpen", "black", "color", "tint", "park")
    if len(sys.argv) != 2 or sys.argv[1] not in allowed:
        _printer.error(f"Usage: {sys.argv[0]} " + " | ".join(allowed), backend="nav")
        sys.exit(1)

    command = sys.argv[1]
    os.makedirs(AWP_DIR, exist_ok=True)

    # --- EFFECTS ---
    if command in ("sharpen", "black", "color", "tint"):
        _printer.info(f"Applying effect: {command}", backend="nav")
        apply_effect_preview(command)
        return

    # --- PARK ---
    if command == "park":
        _printer.info("Parking wallpaper...", backend="nav")
        park_current()
        return

    # --- DELETION ---
    if command == "delete":
        _printer.info("Deleting current wallpaper...", backend="nav")
        success = delete_current_wallpaper_and_advance()
        sys.exit(0 if success else 1)

    # --- NAVIGATION (NEXT/PREV) ---
    direction = command
    ctx = load_current_workspace_context()
    if not ctx:
        sys.exit(1)

    ws_num = ctx["ws_num"]
    ws_key = ctx["ws_key"]
    mode = ctx["config"]["mode"]
    scaling = ctx["config"]["scaling"]
    imgs = ctx["imgs"]
    idx = ctx["idx"]

    state = load_index_state()
    last_idx = int(state.get(ws_key + '_last', -1) or -1)

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

    state[ws_key + '_last'] = idx
    state[ws_key] = new_idx
    save_index_state(state)

    wallpaper_path = str(imgs[new_idx])
    set_wallpaper(ws_num, wallpaper_path, scaling)

    full_info = ctx["awp"].generate_runtime_state(f"ws{ws_num + 1}", wallpaper_path)
    update_runtime_state(full_info)

    _printer.info(f"WS{ws_num + 1}: {direction} wallpaper changed", backend="nav")


if __name__ == "__main__":
    main()
