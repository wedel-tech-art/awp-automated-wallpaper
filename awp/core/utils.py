#!/usr/bin/env python3
"""
AWP Core Utilities
Shared helper functions used by multiple AWP modules.
"""

import os
import subprocess
import colorsys
from PIL import Image


# Terminal Colors for Status Output
CLR_CYAN = "\033[96m"
CLR_GREEN = "\033[92m"
CLR_RED = "\033[91m"
CLR_YELLOW = "\033[93m"
CLR_RESET = "\033[0m"

def x11_blanking(timeout_seconds: int):
    """Universal X11 screen blanking control via xset."""
    try:
        if timeout_seconds == 0:
            subprocess.run(["xset", "s", "off", "-dpms"], check=False)
            print(f"{CLR_CYAN}[AWP]{CLR_RESET} Screen blanking: {CLR_RED}DISABLED{CLR_RESET}")
        else:
            subprocess.run(["xset", "s", str(timeout_seconds)], check=False)
            subprocess.run(["xset", "+dpms", "dpms", str(timeout_seconds), str(timeout_seconds), str(timeout_seconds)], check=False)
            print(f"{CLR_CYAN}[AWP]{CLR_RESET} Screen blanking: {CLR_GREEN}{timeout_seconds}s{CLR_RESET}")
    except Exception as e:
        print(f"{CLR_RED}[AWP-UTILS] Blanking Error: {e}{CLR_RESET}")

def get_icon_color(image_path: str) -> str:
    """Extract dominant color from the first non-transparent pixel."""
    try:
        with Image.open(image_path) as img:
            rgba = img.convert("RGBA")
            pixels = list(rgba.getdata())
            for r, g, b, a in pixels:
                if a > 0:
                    return f'#{r:02x}{g:02x}{b:02x}'
            return ""
    except Exception:
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
