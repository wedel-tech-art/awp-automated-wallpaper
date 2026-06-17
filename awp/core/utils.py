#!/usr/bin/env python3
"""
AWP Core Utilities
Shared helper functions used by multiple AWP modules.
"""

import os
import subprocess
import colorsys
from PIL import Image
from pathlib import Path
from typing import List, Tuple, Optional

from core.printer import get_printer

VALID_EXTENSIONS = (".jpg", ".jpeg", ".png", ".webp", ".avif")

_printer = get_printer()


def hex_to_hsv(hex_color: str):
    """
    Convert hex color (without #) to normalized HSV tuple.
    
    Args:
        hex_color: 6-character hex string (e.g., 'a27ae4')
    
    Returns:
        tuple: (hue 0-1, saturation 0-1, value 0-1)
    """
    r = int(hex_color[0:2], 16) / 255.0
    g = int(hex_color[2:4], 16) / 255.0
    b = int(hex_color[4:6], 16) / 255.0
    return colorsys.rgb_to_hsv(r, g, b)


def hsv_to_hex(h: float, s: float, v: float) -> str:
    """
    Convert normalized HSV tuple to hex color (without #).
    
    Args:
        h: Hue (0-1)
        s: Saturation (0-1)
        v: Value (0-1)
    
    Returns:
        str: 6-character hex string (e.g., 'a27ae4')
    """
    r, g, b = colorsys.hsv_to_rgb(h, s, v)
    r_final = max(0, min(255, int(round(r * 255))))
    g_final = max(0, min(255, int(round(g * 255))))
    b_final = max(0, min(255, int(round(b * 255))))
    return f"{r_final:02x}{g_final:02x}{b_final:02x}"


def apply_hue_shift(h: float, shift_deg: float) -> float:
    """
    Apply hue shift in degrees, wrap around 0-1 range.
    
    Args:
        h: Normalized hue (0-1)
        shift_deg: Degrees to shift (positive or negative)
    
    Returns:
        float: New normalized hue
    """
    return (h + (shift_deg / 360.0)) % 1.0


def apply_sat_val(s: float, v: float, sat_ratio: float, val_ratio: float):
    """
    Apply saturation and value multipliers with clamping to 0-1.
    
    Args:
        s: Saturation (0-1)
        v: Value (0-1)
        sat_ratio: Multiplier for saturation
        val_ratio: Multiplier for value
    
    Returns:
        tuple: (new_saturation, new_value)
    """
    ns = min(1.0, max(0.0, s * sat_ratio))
    nv = min(1.0, max(0.0, v * val_ratio))
    return ns, nv


def calculate_family_color(base_hex: str, sat_ratio: float, val_ratio: float, hue_shift_deg: float = 0) -> str:
    """
    Pure calculation: base_hex + ratios -> new hex.
    
    Args:
        base_hex: Base hex color without # (e.g., 'a27ae4')
        sat_ratio: Saturation multiplier
        val_ratio: Value multiplier
        hue_shift_deg: Degrees to shift hue (default 0)
    
    Returns:
        str: New hex color without #
    """
    h, s, v = hex_to_hsv(base_hex)
    h = apply_hue_shift(h, hue_shift_deg)
    s, v = apply_sat_val(s, v, sat_ratio, val_ratio)
    return hsv_to_hex(h, s, v)


def hex_to_rgb(hex_color: str) -> tuple:
    """
    Convert hex color to RGB tuple.
    
    Args:
        hex_color: 6-character hex string (e.g., 'a27ae4')
    
    Returns:
        tuple: (r, g, b) as integers 0-255
    """
    r = int(hex_color[0:2], 16)
    g = int(hex_color[2:4], 16)
    b = int(hex_color[4:6], 16)
    return (r, g, b)


def rgb_to_hex(r: int, g: int, b: int) -> str:
    """
    Convert RGB tuple to hex string.
    
    Args:
        r: Red (0-255)
        g: Green (0-255)
        b: Blue (0-255)
    
    Returns:
        str: 6-character hex string
    """
    return f"{r:02x}{g:02x}{b:02x}"



def x11_blanking(timeout_seconds: int):
    """Universal X11 screen blanking control via xset."""
    try:
        if timeout_seconds == 0:
            subprocess.run(["xset", "s", "off", "-dpms"], check=False)
            _printer.info(f"Screen blanking: DISABLED", backend="utils")
        else:
            subprocess.run(["xset", "s", str(timeout_seconds)], check=False)
            subprocess.run(["xset", "+dpms", "dpms", str(timeout_seconds), str(timeout_seconds), str(timeout_seconds)], check=False)
            _printer.info(f"Screen blanking: {timeout_seconds}s", backend="utils")
    except Exception as e:
        _printer.error(f"Blanking Error: {e}", backend="utils")

def get_icon_color(image_path: str) -> str:
    """Extract dominant color by sampling multiple pixels."""
    try:
        with Image.open(image_path) as img:
            rgba = img.convert("RGBA")
            
            # Sample 100 pixels across the image (10x10 grid)
            width, height = rgba.size
            samples = []
            
            for i in range(10):
                for j in range(10):
                    x = int(width * i / 10)
                    y = int(height * j / 10)
                    if x < width and y < height:
                        r, g, b, a = rgba.getpixel((x, y))
                        if a > 0:  # Only use non-transparent pixels
                            samples.append((r, g, b))
            
            if not samples:
                return ""
            
            # Average the samples
            avg_r = sum(c[0] for c in samples) // len(samples)
            avg_g = sum(c[1] for c in samples) // len(samples)
            avg_b = sum(c[2] for c in samples) // len(samples)
            
            return f'#{avg_r:02x}{avg_g:02x}{avg_b:02x}'
            
    except Exception as e:
        return ""

def get_dynamic_mount_labels(target_mounts=None):
    """
    Dynamically map mount paths to device labels.
    
    Args:
        target_mounts: List of mount paths to map (e.g., ["/", "/mnt/internal1500"])
                      If None, returns all mounts.
    
    Returns:
        Dictionary: {mount_path: device_label} (e.g., {"/": "SDA2", "/mnt/internal1500": "SDB1"})
    """
    import subprocess
    
    mount_labels = {}
    
    try:
        # Use -l flag for list format (no tree characters like ├─ └─)
        # Use -o for specific columns: NAME (device name) and MOUNTPOINT
        lsblk_output = subprocess.check_output(
            ["lsblk", "-l", "-o", "NAME,MOUNTPOINT"], 
            encoding='utf-8'
        )
        
        mount_to_dev = {}
        for line in lsblk_output.splitlines():
            # Skip the header line
            if line.startswith('NAME'):
                continue
                
            parts = line.split(maxsplit=1)
            if len(parts) == 2:
                dev_name, mountpoint = parts
                if mountpoint and mountpoint.strip():
                    # Clean the device name (remove any remaining special chars just in case)
                    dev_name = dev_name.strip()
                    mountpoint = mountpoint.strip()
                    mount_to_dev[mountpoint] = dev_name
        
        # If no specific targets requested, return all mounts
        if target_mounts is None:
            target_mounts = list(mount_to_dev.keys())
        
        # Build labels for requested mount points
        for mount in target_mounts:
            if mount in mount_to_dev:
                dev = mount_to_dev[mount]
                # Create label like "SDA2" (strip any numbers to keep just base name if preferred)
                # Remove partition numbers if you want just sda/sdb/sdc:
                # import re
                # dev = re.sub(r'\d+$', '', dev)
                label = dev.upper()
                mount_labels[mount] = label
            else:
                # Provide fallback label if mount point not found
                mount_labels[mount] = "???"
                
    except Exception as e:
        # Fallback to generic labels if detection fails
        print(f"Warning: Could not detect mount labels dynamically: {e}")
        if target_mounts:
            for mount in target_mounts:
                if mount == "/":
                    mount_labels[mount] = "ROOT"
                else:
                    import os
                    mount_labels[mount] = os.path.basename(mount).upper()[:8]
    
    return mount_labels

def get_ram_info():
    """
    Returns RAM information in unified format: 'used|free|totalG'
    """
    try:
        with open('/proc/meminfo', 'r') as f:
            mem = {line.split()[0].rstrip(':'): int(line.split()[1]) for line in f}
        
        total = mem['MemTotal'] / 1024 / 1024
        free = mem['MemAvailable'] / 1024 / 1024
        used = total - free
        
        return f"{used:.1f}|{free:.1f}|{total:.1f}G"
    
    except Exception:
        return "??|??|??G"

def get_swap_info():
    """
    Returns SWAP information in unified format: 'used|free|totalG'
    Returns '0.0|0.0|0.0G' if no swap is present.
    """
    try:
        with open('/proc/meminfo', 'r') as f:
            mem = {line.split()[0].rstrip(':'): int(line.split()[1]) for line in f}
        
        total = mem.get('SwapTotal', 0) / 1024 / 1024
        free = mem.get('SwapFree', 0) / 1024 / 1024
        used = total - free
        
        if total == 0:
            return "0.0|0.0|0.0G"
        
        return f"{used:.1f}|{free:.1f}|{total:.1f}G"
    
    except Exception:
        return "??|??|??G"

def get_mounts_info(paths):
    """
    Returns filesystem information for multiple paths.
    Returns dict: {path: 'used|free|totalG'}
    """
    result = {}
    for path in paths:
        try:
            st = os.statvfs(path)
            used = (st.f_blocks - st.f_bfree) * st.f_frsize / (1024**3)
            free = st.f_bavail * st.f_frsize / (1024**3)
            total = st.f_blocks * st.f_frsize / (1024**3)
            result[path] = f"{used:.1f}|{free:.1f}|{total:.1f}G"
        except Exception:
            result[path] = "N/A|N/A|N/A"
    return result

def load_images(folder_path: str) -> List[Path]:
    """Fast image loader using single-pass scandir."""
    images = []
    
    try:
        for entry in os.scandir(folder_path):
            if entry.is_file():
                name = entry.name.lower()
                if name.endswith(VALID_EXTENSIONS):
                    images.append(Path(entry.path))
    except Exception:
        return []
    
    return images

def sort_images(images: List[Path], order_key: str) -> List[Path]:
    """Sort images based on specified order preference."""
    
    if order_key in ('name_new', 'name_old'):
        images_with_stat = [(f, f.stat().st_mtime) for f in images]
        
        reverse = order_key == 'name_new'
        images_with_stat.sort(key=lambda x: x[1], reverse=reverse)
        
        return [f for f, _ in images_with_stat]

    elif order_key == 'name_az':
        return sorted(images, key=lambda f: f.name.lower())

    elif order_key == 'name_za':
        return sorted(images, key=lambda f: f.name.lower(), reverse=True)

    return images
