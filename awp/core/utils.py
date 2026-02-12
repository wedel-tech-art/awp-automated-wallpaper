#!/usr/bin/env python3
"""
AWP Core Utilities
Shared helper functions used by multiple AWP modules.
"""

import os
import shutil
import subprocess
import colorsys
import mimetypes
from PIL import Image

# Terminal Colors for Status Output
CLR_CYAN = "\033[96m"
CLR_GREEN = "\033[92m"
CLR_RED = "\033[91m"
CLR_YELLOW = "\033[93m"
CLR_RESET = "\033[0m"

# The master list of assets to be re-hued during the bake process
TARGET_ASSETS = [
    "arrow-down-active.png", "arrow-down-hover.png",
    "arrow-left-active.png", "arrow-left-hover.png",
    "arrow-right-active.png", "arrow-right-hover.png",
    "arrow-small-down-active.png", "arrow-small-down-hover.png",
    "arrow-small-left-active.png", "arrow-small-left-hover.png",
    "arrow-small-right-active.png", "arrow-small-right-hover.png",
    "arrow-small-up-active.png", "arrow-small-up-hover.png",
    "arrow-up-active.png", "arrow-up-hover.png",
    "button-active.png", "button-hover.png",
    "check-checked-active@2.png", "check-checked-active.png",
    "check-checked-hover@2.png", "check-checked-hover.png",
    "check-mixed-active@2.png", "check-mixed-active.png",
    "check-mixed-hover@2.png", "check-mixed-hover.png",
    "check-selectionmode-checked-active@2.png", "check-selectionmode-checked-active.png",
    "check-selectionmode-checked-hover@2.png", "check-selectionmode-checked-hover.png",
    "check-selectionmode-unchecked-active@2.png", "check-selectionmode-unchecked-active.png",
    "check-selectionmode-unchecked-hover@2.png", "check-selectionmode-unchecked-hover.png",
    "check-unchecked-active@2.png", "check-unchecked-active.png",
    "check-unchecked-hover@2.png", "check-unchecked-hover.png",
    "combo-entry-active.png", "combo-entry-button-active.png",
    "entry-active.png", "menubar-button.png", "progressbar-bar.png",
    "radio-checked-active@2.png", "radio-checked-active.png",
    "radio-checked-hover@2.png", "radio-checked-hover.png",
    "radio-mixed-active@2.png", "radio-mixed-active.png",
    "radio-mixed-hover@2.png", "radio-mixed-hover.png",
    "radio-unchecked-active@2.png", "radio-unchecked-active.png",
    "radio-unchecked-hover@2.png", "radio-unchecked-hover.png",
    "scale-slider-active.png", "scale-slider-hover.png",
    "scrollbar-slider-horizontal-active@2.png", "scrollbar-slider-horizontal-active.png",
    "scrollbar-slider-horizontal-hover@2.png", "scrollbar-slider-horizontal-hover.png",
    "scrollbar-slider-vertical-active@2.png", "scrollbar-slider-vertical-active.png",
    "scrollbar-slider-vertical-hover@2.png", "scrollbar-slider-vertical-hover.png",
    "togglebutton-active.png", "togglebutton-hover.png",
    "toolbutton-active.png", "toolbutton-hover.png"
]

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

def bake_awp_theme(hex_color: str, icon: str = None):
    """Dynamic Theme Synthesis Engine (AWP-G2) - List-Based Stable Edition"""
    if not hex_color or hex_color == "": return None
    clean_hex = hex_color.lstrip('#').lower()
    theme_name = f"awp-{clean_hex}"
    home = os.path.expanduser("~")
    template_path = os.path.join(home, "awp/template")
    target_path = os.path.join(home, ".themes", theme_name)

    if not os.path.exists(target_path):
        try:
            shutil.copytree(template_path, target_path)
            
            # --- 1. Icon Handling ---
            if icon and os.path.exists(icon):
                dest_icon = os.path.join(target_path, "folder.png")
                ext = os.path.splitext(icon)[1].lower()
                if ext == ".png":
                    shutil.copy2(icon, dest_icon)
                else:
                    subprocess.run(["convert", icon, dest_icon], check=True)

            # --- 2. Color Conversion ---
            r_int = int(clean_hex[0:2], 16)
            g_int = int(clean_hex[2:4], 16)
            b_int = int(clean_hex[4:6], 16)
            new_rgb = f"{r_int}, {g_int}, {b_int}"

            # --- 3. Surgical Replacements ---
            color_replacements = [
                ("3daee9", clean_hex), 
                ("61, 174, 233", new_rgb), 
                ("37, 164, 230", new_rgb)
            ]
            
            for old, new in color_replacements:
                subprocess.run(["find", target_path, "-type", "f", "(", 
                                "-name", "*.css", "-o", "-name", "*.svg", "-o", 
                                "-name", "*.rc", "-o", "-name", "index.theme", ")", 
                                "-exec", "sed", "-i", f"s/{old}/{new}/gI", "{}", "+"], check=True)

            index_file = os.path.join(target_path, "index.theme")
            if os.path.exists(index_file):
                subprocess.run(["sed", "-i", f"s/Breeze-Dark/{theme_name}/gI", index_file], check=True)
                subprocess.run(["sed", "-i", f"s/Breeze/{theme_name}/gI", index_file], check=True)

            # --- 4. PNG Graphics Surgery (The List-Based Engine) ---
            rgb_norm = (r_int/255.0, g_int/255.0, b_int/255.0)
            # Hue calculation logic
            im_hue = round(100 + ((colorsys.rgb_to_hls(*rgb_norm)[0] * 360 - 203) / 1.8))
            
            # Use the hardcoded list from utils.py
            # Note: Assuming TARGET_ASSETS is available in the scope
            assets_dir = os.path.join(target_path, "assets")

            for filename in TARGET_ASSETS:
                asset_file = os.path.join(assets_dir, filename)
                if os.path.exists(asset_file):
                    # Only mogrify the authorized genetic files
                    subprocess.run(["mogrify", "-modulate", f"100,100,{im_hue}", asset_file], check=True)

            # --- 5. Cleanup ---
            gres = os.path.join(target_path, "gtk-3.0/gtk.gresource")
            if os.path.exists(gres): os.remove(gres)
            
            # We no longer need to rmtree(target_assets_dir) because we stopped creating it!
            
            subprocess.run(["find", target_path, "-type", "f", "(", "-name", "*.css", "-o", "-name", "*.svg", ")", "-exec", "sed", "-i", "s/##/#/g", "{}", "+"])
            
        except Exception as e:
            print(f"System Error: {e}")
            return None
            
    return theme_name

def bake_awp_theme_legacy(hex_color: str, icon: str = None):
    """Genetic Theme Engine (Legacy) - Mint-Y Template Base"""
    if not hex_color or hex_color == "": return None
    clean_hex = hex_color.lstrip('#').lower()
    theme_name = f"awp-{clean_hex}"
    home = os.path.expanduser("~")
    template_path = os.path.join(home, "awp/template") # Should be Mint-Y for legacy
    target_path = os.path.join(home, ".themes", theme_name)

    if not os.path.exists(target_path):
        try:
            shutil.copytree(template_path, target_path)
            if icon and os.path.exists(icon): shutil.copy2(icon, os.path.join(target_path, "folder.png"))
            r, g, b = int(clean_hex[0:2], 16), int(clean_hex[2:4], 16), int(clean_hex[4:6], 16)
            faded_hex = f"{int(r*0.7):02x}{int(g*0.7):02x}{int(b*0.7):02x}"
            replacements = [("70737a", clean_hex), ("52545a", faded_hex), ("Mint-Y-Dark-Grey", theme_name)]
            for old, new in replacements:
                subprocess.run(["find", target_path, "-type", "f", "(", "-name", "*.css", "-o", "-name", "*.svg", "-o", "-name", "*.rc", "-o", "-name", "index.theme", ")", "-exec", "sed", "-i", f"s/{old}/{new}/gI", "{}", "+"], check=True)
            gres = os.path.join(target_path, "gtk-3.0/gtk.gresource")
            if os.path.exists(gres): os.remove(gres)
        except Exception as e:
            print(f"Legacy Error: {e}")
            return None
    return theme_name

def get_available_themes() -> dict:
    """Discover available themes and return categorised, sorted lists."""
    themes = {
        'icon_themes': [],
        'gtk_themes': [], 
        'cursor_themes': [],
        'desktop_themes': [],
        'wm_themes': []
    }
    
    icon_paths = [
        '/usr/share/icons', 
        '/usr/local/share/icons',
        os.path.expanduser('~/.icons'),
        os.path.expanduser('~/.local/share/icons')
    ]
    
    theme_paths = [
        '/usr/share/themes',
        '/usr/local/share/themes', 
        os.path.expanduser('~/.themes'),
        os.path.expanduser('~/.local/share/themes')
    ]

    # 1. Discover Icon and Cursor Themes
    for path in icon_paths:
        if os.path.exists(path):
            try:
                for item in os.listdir(path):
                    full_path = os.path.join(path, item)
                    if os.path.isdir(full_path):
                        # It's an icon theme
                        themes['icon_themes'].append(item)
                        # Check if it's specifically a cursor theme
                        if os.path.exists(os.path.join(full_path, 'cursors')):
                            themes['cursor_themes'].append(item)
            except (PermissionError, OSError):
                continue

    # 2. Discover GTK and Window Manager Themes
    all_raw_themes = []
    for path in theme_paths:
        if os.path.exists(path):
            try:
                for item in os.listdir(path):
                    full_path = os.path.join(path, item)
                    if os.path.isdir(full_path):
                        all_raw_themes.append(item)
                        
                        # Check for Window Manager components (XFWM, Openbox, Metacity)
                        # This solves your "Greyed out" issue for Openbox/Cinnamon
                        has_wm = any([
                            os.path.exists(os.path.join(full_path, 'xfwm4')),
                            os.path.exists(os.path.join(full_path, 'openbox-3')),
                            os.path.exists(os.path.join(full_path, 'metacity-1'))
                        ])
                        if has_wm:
                            themes['wm_themes'].append(item)
                            
                        # Check for Cinnamon Desktop specifically
                        if os.path.exists(os.path.join(full_path, 'cinnamon')):
                            themes['desktop_themes'].append(item)
            except (PermissionError, OSError):
                continue

    # 3. Final Sorting & De-duplication (The Alphabetical Fix)
    # We use key=str.lower so 'awp' and 'AWP' sit together
    themes['gtk_themes'] = sorted(list(set(all_raw_themes)), key=str.lower)
    themes['icon_themes'] = sorted(list(set(themes['icon_themes'])), key=str.lower)
    themes['cursor_themes'] = sorted(list(set(themes['cursor_themes'])), key=str.lower)
    themes['wm_themes'] = sorted(list(set(themes['wm_themes'])), key=str.lower)
    themes['desktop_themes'] = sorted(list(set(themes['desktop_themes'])), key=str.lower)

    return themes

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
