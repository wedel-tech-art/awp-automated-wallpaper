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
