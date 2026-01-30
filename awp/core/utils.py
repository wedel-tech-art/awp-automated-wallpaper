#!/usr/bin/env python3
"""
AWP Core Utilities
Shared helper functions used by multiple AWP modules.
"""

import os
import mimetypes
from PIL import Image

CLR_CYAN = "\033[96m"
CLR_GREEN = "\033[92m"
CLR_RED = "\033[91m"
CLR_YELLOW = "\033[93m"
CLR_RESET = "\033[0m"

def x11_blanking(timeout_seconds: int):
    """
    Universal X11 screen blanking control.
    Communicates directly with the X server via xset.
    """
    import subprocess
    try:
        if timeout_seconds == 0:
            subprocess.run(["xset", "s", "off", "-dpms"], check=False)
            print(f"{CLR_CYAN}[AWP]{CLR_RESET} Screen blanking: {CLR_RED}DISABLED{CLR_RESET}")
        else:
            # s sets the timer, +dpms enables power management
            subprocess.run(["xset", "s", str(timeout_seconds)], check=False)
            subprocess.run(["xset", "+dpms", "dpms", str(timeout_seconds), str(timeout_seconds), str(timeout_seconds)], check=False)
            print(f"{CLR_CYAN}[AWP]{CLR_RESET} Screen blanking: {CLR_GREEN}{timeout_seconds}s{CLR_RESET}")
    except Exception as e:
        print(f"{CLR_RED}[AWP-UTILS] Blanking Error: {e}{CLR_RESET}")

def get_icon_color(image_path: str) -> str:
    """
    Extract dominant color from an image file.
    
    Args:
        image_path (str): Path to the image file
        
    Returns:
        str: Hex color code of the first non-transparent pixel, 
             or empty string on error
    """
    try:
        with Image.open(image_path) as img:
            rgba = img.convert("RGBA")
            pixels = list(rgba.getdata())
            for r, g, b, a in pixels:
                if a > 0:  # First non-transparent pixel
                    return f'#{r:02x}{g:02x}{b:02x}'
            return ""
    except Exception:
        return ""

import os
import shutil
import subprocess

def bake_awp_theme(hex_color: str, icon: str = None):
    """
    Genetic Theme Engine: Creates 'awp-[hex]' and copies the 
    workspace icon as 'folder.png' for Thunar.
    """
    if not hex_color or hex_color == "":
        return None

    clean_hex = hex_color.lstrip('#').lower()
    theme_name = f"awp-{clean_hex}"
    
    home = os.path.expanduser("~")
    template_path = os.path.join(home, "awp/template")
    target_path = os.path.join(home, ".themes", theme_name)

    # Only bake if it doesn't already exist (The 'End of Story' rule)
    if not os.path.exists(target_path):
        try:
            # 1. Clone the template
            shutil.copytree(template_path, target_path)

            # 2. Thumbnail Logic: Copy icon to folder.png for Thunar
            if icon and os.path.exists(icon):
                shutil.copy2(icon, os.path.join(target_path, "folder.png"))

            # 3. DNA Swap Logic (sed)
            r = int(clean_hex[0:2], 16)
            g = int(clean_hex[2:4], 16)
            b = int(clean_hex[4:6], 16)
            faded_hex = f"{int(r*0.7):02x}{int(g*0.7):02x}{int(b*0.7):02x}"

            replacements = [
                ("70737a", clean_hex), 
                ("52545a", faded_hex),
                ("Mint-Y-Dark-Grey", theme_name)
            ]

            for old, new in replacements:
                subprocess.run([
                    "find", target_path, "-type", "f", 
                    "(", "-name", "*.css", "-o", "-name", "*.svg", "-o", "-name", "*.rc", "-o", "-name", "index.theme", ")",
                    "-exec", "sed", "-i", f"s/{old}/{new}/gI", "{}", "+"
                ], check=True)

            # 4. Cleanup
            gres = os.path.join(target_path, "gtk-3.0/gtk.gresource")
            if os.path.exists(gres):
                os.remove(gres)

        except Exception as e:
            print(f"Theme Bake Error: {e}")
            return None
    
    return theme_name

def get_available_themes() -> dict:
    """
    Discover available themes on the system and return categorized lists.
    
    Returns:
        dict: Categorized theme lists including:
            - icon_themes: Available icon themes
            - gtk_themes: Available GTK themes
            - cursor_themes: Available cursor themes  
            - desktop_themes: Themes with Cinnamon desktop support
            - wm_themes: Themes with window manager components
    """
    themes = {
        'icon_themes': [],
        'gtk_themes': [], 
        'cursor_themes': [],
        'desktop_themes': [],  # For Cinnamon desktop/panels
        'wm_themes': []        # For window borders specifically
    }
    
    # Discover icon themes
    icon_paths = [
        '/usr/share/icons', 
        os.path.expanduser('/usr/local/share/icons'),
        os.path.expanduser('~/.icons'),
        os.path.expanduser('~/.local/share/icons')
    ]
    
    for path in icon_paths:
        if os.path.exists(path):
            try:
                items = [d for d in os.listdir(path) 
                        if os.path.isdir(os.path.join(path, d))]
                themes['icon_themes'].extend(items)
            except (PermissionError, OSError):
                pass  # Skip directories we can't read
    
    # Discover ALL themes
    theme_paths = [
        '/usr/share/themes',
        '/usr/local/share/themes', 
        os.path.expanduser('~/.themes'),
        os.path.expanduser('~/.local/share/themes')
    ]
    
    all_themes = []
    for path in theme_paths:
        if os.path.exists(path):
            try:
                items = [d for d in os.listdir(path) 
                        if os.path.isdir(os.path.join(path, d))]
                all_themes.extend(items)
            except (PermissionError, OSError):
                pass  # Skip directories we can't read
    
    # Filter for themes that have Cinnamon support (desktop themes)
    desktop_themes = []
    wm_themes = []
    
    for theme in all_themes:
        # Check all possible theme paths
        theme_paths_to_check = []
        for base_path in theme_paths:
            if os.path.exists(base_path):
                # Check for various window manager/desktop components
                possible_paths = [
                    os.path.join(base_path, theme, 'cinnamon'),
                    os.path.join(base_path, theme, 'metacity-1'), 
                    os.path.join(base_path, theme, 'xfwm4'),
                    os.path.join(base_path, theme, 'gnome-shell'),
                    os.path.join(base_path, theme, 'openbox-3')
                ]
                theme_paths_to_check.extend(possible_paths)
        
        # Check if this theme has window manager components
        has_wm = any(os.path.exists(path) for path in theme_paths_to_check)
        
        if has_wm:
            wm_themes.append(theme)
            # Themes with Cinnamon specific support are desktop themes
            if any('cinnamon' in path for path in theme_paths_to_check if os.path.exists(path)):
                desktop_themes.append(theme)
    
    # Sort all lists alphabetically
    themes['gtk_themes'] = sorted(list(set(all_themes)))
    themes['desktop_themes'] = sorted(list(set(desktop_themes)))
    themes['wm_themes'] = sorted(list(set(wm_themes)))
    themes['icon_themes'] = sorted(list(set(themes['icon_themes'])))
    
    # Discover cursor themes
    cursor_themes = []
    for path in icon_paths:
        if os.path.exists(path):
            try:
                for theme in os.listdir(path):
                    cursor_path = os.path.join(path, theme, 'cursors')
                    if os.path.exists(cursor_path):
                        cursor_themes.append(theme)
            except (PermissionError, OSError):
                pass
    
    themes['cursor_themes'] = sorted(list(set(cursor_themes)))
    
    return themes


# Optional: Add other shared utilities here if needed
# def some_other_shared_function():
#     pass
