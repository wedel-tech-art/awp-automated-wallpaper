#!/usr/bin/env python3
"""
AWP Core Utilities
Shared helper functions used by multiple AWP modules.
"""

import os
import re
import shutil
import subprocess
import colorsys
from PIL import Image
from pathlib import Path
from typing import List, Tuple, Optional
from collections import Counter
from core.constants import SVG_TEMPLATES

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


def get_icon_color(image_path: str) -> str:
    try:
        with Image.open(image_path) as img:
            # 1. Ensure we have an alpha channel to work with
            img = img.convert("RGBA")
            
            # 2. Get the raw data
            data = img.getdata()
            
            # 3. Filter: Keep only pixels that are not fully transparent
            # We check if alpha (data[3]) > 0
            visible_pixels = [pix[:3] for pix in data if pix[3] > 0]
            
            if not visible_pixels:
                return "" # Icon is entirely transparent
            
            # 4. Find the most common among visible pixels
            most_common = Counter(visible_pixels).most_common(1)[0][0]
            
            return f'#{most_common[0]:02x}{most_common[1]:02x}{most_common[2]:02x}'
    except Exception:
        return ""


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


# =============================================================================
# COLOR SPACE CONVERSIONS - HLS (Hue, Lightness, Saturation)
# =============================================================================

def hex_to_hls(hex_color: str) -> tuple:
    """
    Convert hex color (without #) to normalized HLS tuple.
    
    Args:
        hex_color: 6-character hex string (e.g., 'a27ae4')
    
    Returns:
        tuple: (hue 0-1, lightness 0-1, saturation 0-1)
    """
    r = int(hex_color[0:2], 16) / 255.0
    g = int(hex_color[2:4], 16) / 255.0
    b = int(hex_color[4:6], 16) / 255.0
    return colorsys.rgb_to_hls(r, g, b)


def hls_to_hex(h: float, l: float, s: float) -> str:
    """
    Convert normalized HLS tuple to hex color (without #).
    
    Args:
        h: Hue (0-1)
        l: Lightness (0-1)
        s: Saturation (0-1)
    
    Returns:
        str: 6-character hex string (e.g., 'a27ae4')
    """
    r, g, b = colorsys.hls_to_rgb(h, l, s)
    r_final = max(0, min(255, int(round(r * 255))))
    g_final = max(0, min(255, int(round(g * 255))))
    b_final = max(0, min(255, int(round(b * 255))))
    return f"{r_final:02x}{g_final:02x}{b_final:02x}"


# =============================================================================
# ANGLE & MATH UTILITIES
# =============================================================================

def signed_hue_diff(deg1: float, deg2: float) -> float:
    """
    Calculate the shortest signed difference between two angles in degrees.
    Pure mathematics - no theming logic.
    
    Args:
        deg1: First angle in degrees
        deg2: Second angle in degrees
    
    Returns:
        float: Signed difference in degrees (-180 to 180)
    """
    return (deg1 - deg2 + 180.0) % 360.0 - 180.0


def clamp(value: float, min_val: float = 0.0, max_val: float = 400.0) -> float:
    """
    Clamp a value between min and max.
    Pure mathematics - no theming logic.
    
    Args:
        value: Value to clamp
        min_val: Minimum allowed value (default: 0.0)
        max_val: Maximum allowed value (default: 400.0)
    
    Returns:
        float: Clamped value
    """
    return max(min_val, min(max_val, value))


# =============================================================================
# CONFIG HELPERS
# =============================================================================

def get_source_hex_from_config(config: dict) -> str:
    """
    Get the source hex color from a preset config.
    Looks for explicit 'source_hex' field first, then falls back to first 'hex'.
    
    Args:
        config: Preset configuration dict (from THEME_PRESETS or ICON_PRESETS)
    
    Returns:
        str: Hex color without #, or None if not found
    """
    # First: check for explicit source_hex field
    if 'source_hex' in config:
        return config['source_hex']
    
    # Fallback: first 'hex' color (for backward compatibility)
    for color, kind in config.get('colors', []):
        if kind == 'hex':
            return color
    
    return None


# =============================================================================
# IMAGE COLOR DETECTION (Optional - useful for auto-detection)
# =============================================================================

def get_dominant_color(image_path: str) -> str:
    """
    Get the dominant color from a PNG image.
    Returns hex color without #.
    
    Args:
        image_path: Path to the PNG file
    
    Returns:
        str: Hex color (e.g., '3daee9') or None if failed
    """
    try:
        with Image.open(image_path) as img:
            img = img.convert("RGBA")
            data = img.getdata()
            visible = [pix[:3] for pix in data if pix[3] > 0]
            
            if not visible:
                return None
            
            most_common = Counter(visible).most_common(1)[0][0]
            return f"{most_common[0]:02x}{most_common[1]:02x}{most_common[2]:02x}"
            
    except Exception:
        return None

