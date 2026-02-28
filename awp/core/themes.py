#!/usr/bin/env python3
"""
AWP - Automated Wallpaper Program
Core Themes Module

All Themes related functions
"""
import os
import shutil
import subprocess
import colorsys
from core.printer import get_printer
_printer = get_printer()

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

def bake_awp_theme(hex_color: str, icon: str = None):
    """Dynamic Theme Synthesis Engine (AWP-G2) - List-Based Stable Edition"""
    if not hex_color or hex_color == "": 
        return None
        
    clean_hex = hex_color.lstrip('#').lower()
    theme_name = f"awp-{clean_hex}"
    home = os.path.expanduser("~")
    template_path = os.path.join(home, "awp/template-themes")
    target_path = os.path.join(home, ".themes", theme_name)

    if not os.path.exists(target_path):
        try:
            _printer.info(f"Baking Theme: {theme_name}", backend="themes")
            shutil.copytree(template_path, target_path)
            
            # --- 1. Icon Handling ---
            if icon and os.path.exists(icon):
                dest_icon = os.path.join(target_path, "folder.png")
                ext = os.path.splitext(icon)[1].lower()
                if ext == ".png":
                    shutil.copy2(icon, dest_icon)
                else:
                    subprocess.run(["convert", icon, dest_icon], check=True)
                _printer.info(f"Icon added to theme: {os.path.basename(icon)}", backend="themes")

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

            # --- 4. The owstudios "Studio-Mastered" Logic ---
            r_int = int(clean_hex[0:2], 16)
            g_int = int(clean_hex[2:4], 16)
            b_int = int(clean_hex[4:6], 16)
            rgb_norm = (r_int/255.0, g_int/255.0, b_int/255.0)
            
            hls = colorsys.rgb_to_hls(*rgb_norm)
            target_hue_deg = hls[0] * 360

            # 1. THE ROTATION (The 'Tuner')
            # We use 1.7 instead of 1.8 to 'stretch' the rotation. 
            # This pulls Purple further away from Blue and makes Reds 'truer'.
            hue_diff = target_hue_deg - 203
            if hue_diff < 0: hue_diff += 360 
            im_hue = round(100 + (hue_diff / 1.7)) 
            
            if im_hue > 200: im_hue -= 200

            # 2. ADAPTIVE MIXING (The 'Compressor')
            # Default settings
            brightness = 85 
            saturation = 140

            # RED/ORANGE ZONE: 'Happier' (More light, less compression)
            if target_hue_deg < 30 or target_hue_deg > 330:
                brightness = 95  # Much brighter/happier
                saturation = 160 # Richer

            # YELLOW/GOLD ZONE: 'A little darker' (Industrial Gold)
            elif 45 <= target_hue_deg <= 70:
                brightness = 75  # Weighted down
                saturation = 150 

            # PURPLE ZONE: (Fixing the Blue-lean)
            elif 240 <= target_hue_deg <= 300:
                # We push the rotation an extra nudge to clear the Blue zone
                im_hue += 5 
                brightness = 90
                saturation = 150

            # GREEN ZONE: (Leaving it 'Normal' as requested)
            elif 75 < target_hue_deg < 160:
                brightness = 65 
                saturation = 160

            _printer.info(f"Theme Processing: Hue:{target_hue_deg:.1f}° B:{brightness} S:{saturation}", backend="themes")

            # --- Surgery Execution ---
            assets_dir = os.path.join(target_path, "assets")
            for filename in TARGET_ASSETS:
                asset_file = os.path.join(assets_dir, filename)
                if os.path.exists(asset_file):
                    subprocess.run([
                        "mogrify", "-modulate", 
                        f"{brightness},{saturation},{im_hue}", 
                        asset_file
                    ], check=True)

            # --- 5. Cleanup ---
            gres = os.path.join(target_path, "gtk-3.0/gtk.gresource")
            if os.path.exists(gres): os.remove(gres)
            
            # We no longer need to rmtree(target_assets_dir) because we stopped creating it!
            
            subprocess.run(["find", target_path, "-type", "f", "(", "-name", "*.css", "-o", "-name", "*.svg", ")", "-exec", "sed", "-i", "s/##/#/g", "{}", "+"])
            
            _printer.success(f"Theme {theme_name} baked successfully!", backend="themes")
            
        except Exception as e:
            _printer.error(f"System Error (Theme): {e}", backend="themes")
            return None
            
    return theme_name

def bake_awp_icon(hex_color: str, icon: str = None):
    """Dynamic Icon Synthesis Engine (AWP-G2) - Optimized Execution Order"""
    
    if not hex_color or hex_color == "": 
        return None
        
    clean_hex = hex_color.lstrip('#').lower()
    theme_name = f"awp-icons-{clean_hex}"
    home = os.path.expanduser("~")
    template_path = os.path.join(home, "awp/template-icons")
    target_path = os.path.join(home, ".icons", theme_name)

    if not os.path.exists(target_path):
        try:
            _printer.info(f"Baking Icons: {theme_name}", backend="themes")
            
            # 1. Clone the template
            shutil.copytree(template_path, target_path, symlinks=True)
            
            # --- 2. The Fletcher-Munson Color Logic (Logarithmic Approach) ---
            r_int = int(clean_hex[0:2], 16)
            g_int = int(clean_hex[2:4], 16)
            b_int = int(clean_hex[4:6], 16)
            rgb_norm = (r_int/255.0, g_int/255.0, b_int/255.0)
            
            hls = colorsys.rgb_to_hls(*rgb_norm)
            target_hue_deg = hls[0] * 360
            
            # Distance from the Purple Template (262°)
            hue_dist = abs(target_hue_deg - 262)
            if hue_dist > 180: hue_dist = 360 - hue_dist

            # Normalize distance (0.0 at Purple, 1.0 at Green/Yellow)
            # Green is roughly 140° away from our Purple base
            factor = min(hue_dist / 140.0, 1.0)

            # BRIGHTNESS: Starts at 100% (Purple), drops to 60% (Green)
            # This is our 'Luminosity Padding'
            brightness = round(100 - (40 * factor))

            # SATURATION: Starts at 100% (Purple), boosts to 160% (Green)
            # This keeps the 'vibrancy' while the 'volume' is down
            saturation = round(100 + (60 * factor))

            # FINAL HUE: The standard rotation
            im_hue = round(100 + ((target_hue_deg - 262) / 1.8))

            # 3. Identity Replacement (Internal Theme Name)
            index_file = os.path.join(target_path, "index.theme")
            if os.path.exists(index_file):
                subprocess.run(["sed", "-i", f"s/^Name=.*/Name={theme_name}/g", index_file], check=True)
                subprocess.run(["sed", "-i", f"s/Mint-Y-Purple/{theme_name}/gI", index_file], check=True)
            
            # --- 4. Global Graphics Surgery ---
            _printer.info(f"Applying color adjustments: Hue:{target_hue_deg:.1f}° B:{brightness} S:{saturation}", backend="themes")
            subprocess.run([
                "find", target_path, "-type", "f", "-name", "*.png", 
                "-exec", "mogrify", "-modulate", f"{brightness},{saturation},{im_hue}", "{}", "+"
            ], check=True)

            # --- 5. Icon Handling (COPY LAST) ---
            if icon and os.path.exists(icon):
                dest_icon = os.path.join(target_path, "folder.png")
                ext = os.path.splitext(icon)[1].lower()
                if ext == ".png":
                    shutil.copy2(icon, dest_icon)
                else:
                    subprocess.run(["convert", icon, dest_icon], check=True)
                _printer.info(f"Folder icon added: {os.path.basename(icon)}", backend="themes")
            
            # 6. Final Cleanup & Cache
            result = subprocess.run(["gtk-update-icon-cache", "-t", target_path], 
                                    check=False, 
                                    capture_output=True, 
                                    text=True)

            # Print stdout as success (green)
            if result.stdout:
                for line in result.stdout.splitlines():
                    if line.strip():
                        _printer.success(line.strip(), backend="themes")
                        
            # Print stderr as info (cyan) or warning (yellow) depending on content
            if result.stderr:
                for line in result.stderr.splitlines():
                    if line.strip():
                        # Check if it's actually an error message or just info
                        if "error" in line.lower() or "failed" in line.lower():
                            _printer.error(line.strip(), backend="themes")
                        else:
                            # Treat as info message (cyan) instead of error
                            _printer.info(line.strip(), backend="themes")

            # Summary message (green)
            _printer.success(f"Icon theme {theme_name} ready", backend="themes")
            
        except Exception as e:
            _printer.error(f"System Error (Icons): {e}", backend="themes")
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
