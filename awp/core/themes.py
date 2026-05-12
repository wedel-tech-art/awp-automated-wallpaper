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
from core.constants import ICON_PRESETS, THEME_PRESETS, TARGET_ASSETS, ICON_MANIFEST, SYMLINK_MAP, ICON_SIZES
from core.printer import get_printer
_printer = get_printer()


def _build_color_replacements(config, clean_hex, new_rgb):
    """Build the color replacements list, deriving family shades if needed."""
    
    replacements = []
    
    # Derive family shades if template needs them
    family = {}
    if config.get('family_ratios'):
        r,g,b = int(clean_hex[0:2],16)/255, int(clean_hex[2:4],16)/255, int(clean_hex[4:6],16)/255
        h, s, v = colorsys.rgb_to_hsv(r, g, b)
        
        for name, (sat_ratio, val_ratio) in config['family_ratios'].items():
            nr,ng,nb = colorsys.hsv_to_rgb(h, min(1.0, s*sat_ratio), min(1.0, v*val_ratio))
            family[name]         = f"{int(nr*255):02x}{int(ng*255):02x}{int(nb*255):02x}"
            family[f"{name}_rgb"] = f"{int(nr*255)}, {int(ng*255)}, {int(nb*255)}"

    # Build replacements list
    for old, kind in config['colors']:
        if kind == 'hex':
            replacements.append((old, clean_hex))
        elif kind == 'rgb':
            replacements.append((old, new_rgb))
        else:
            # it's a family member — 'shade', 'shade_rgb', 'lighter', 'lighter_rgb'
            replacements.append((old, family[kind]))

    return replacements


def _modulate_assets(config, target_path, clean_hex):
    """Studio-Mastered PNG modulation — only runs if preset has assets."""
    if not config['assets']:
        return

    r_int = int(clean_hex[0:2], 16)
    g_int = int(clean_hex[2:4], 16)
    b_int = int(clean_hex[4:6], 16)
    rgb_norm = (r_int/255.0, g_int/255.0, b_int/255.0)

    hls = colorsys.rgb_to_hls(*rgb_norm)
    target_hue_deg = hls[0] * 360

    # 1. THE ROTATION
    hue_diff = target_hue_deg - 203
    if hue_diff < 0: hue_diff += 360
    im_hue = round(100 + (hue_diff / 1.7))
    if im_hue > 200: im_hue -= 200

    # 2. ADAPTIVE MIXING
    brightness = 85
    saturation = 140

    if target_hue_deg < 30 or target_hue_deg > 330:
        brightness = 95
        saturation = 160
    elif 45 <= target_hue_deg <= 70:
        brightness = 75
        saturation = 150
    elif 240 <= target_hue_deg <= 300:
        im_hue += 5
        brightness = 90
        saturation = 150
    elif 75 < target_hue_deg < 160:
        brightness = 65
        saturation = 160

    _printer.info(f"Theme Processing: Hue:{target_hue_deg:.1f}° B:{brightness} S:{saturation}", backend="themes")

    assets_dir = os.path.join(target_path, "assets")
    for filename in config['assets']:
        asset_file = os.path.join(assets_dir, filename)
        if os.path.exists(asset_file):
            subprocess.run([
                "mogrify", "-modulate",
                f"{brightness},{saturation},{im_hue}",
                asset_file
            ], check=True)


def bake_awp_theme(hex_color: str, icon: str = None, preset: str = 'breeze'):
    """Dynamic Theme Synthesis Engine (AWP-G2) - Multi-Preset Edition"""
    if not hex_color or hex_color == "":
        return None

    config = THEME_PRESETS[preset]

    clean_hex = hex_color.lstrip('#').lower()
    theme_name = f"awp-gtk-{preset}-{clean_hex}"
    home = os.path.expanduser("~")
    template_path = os.path.join(home, "awp", config['path'])
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
            color_replacements = _build_color_replacements(config, clean_hex, new_rgb)

            for old, new in color_replacements:
                subprocess.run(["find", target_path, "-type", "f", "(",
                                "-name", "*.css", "-o", "-name", "*.svg", "-o",
                                "-name", "*.rc", "-o", "-name", "index.theme", ")",
                                "-exec", "sed", "-i", f"s/{old}/{new}/gI", "{}", "+"], check=True)

            # --- 4. Rebranding ---
            index_file = os.path.join(target_path, "index.theme")
            if os.path.exists(index_file):
                for name in config['rebrand']:
                    subprocess.run(["sed", "-i", f"s/{name}/{theme_name}/gI", index_file], check=True)

            # --- 5. Studio-Mastered PNG Modulation ---
            _modulate_assets(config, target_path, clean_hex)

            # --- 6. Cleanup ---
            gres = os.path.join(target_path, "gtk-3.0/gtk.gresource")
            if os.path.exists(gres): os.remove(gres)

            subprocess.run(["find", target_path, "-type", "f", "(", "-name", "*.css", "-o", "-name", "*.svg", ")",
                            "-exec", "sed", "-i", "s/##/#/g", "{}", "+"])

            _printer.success(f"Theme {theme_name} baked successfully!", backend="themes")

        except Exception as e:
            _printer.error(f"System Error (Theme): {e}", backend="themes")
            return None

    return theme_name

import os, shutil, subprocess, colorsys

def bake_awp_icon(hex_color: str, icon: str = None, preset: str = "mint"):
    """
    OWStudios Dynamic Icon Engine - MANIFEST EDITION
    - Generates index.theme dynamically based on ICON_MANIFEST and ICON_SIZES.
    """
    if not hex_color or hex_color == "": 
        return None
        
    clean_hex = hex_color.lstrip('#').lower()

    # --- PRESET LOGIC ---
    template_folder = ICON_PRESETS.get(preset, "template-icon-presets/mint")
    theme_name = f"awp-icons-{preset}-{clean_hex}"
    home = os.path.expanduser("~")
    template_path = os.path.join(home, "awp", template_folder)
    target_path = os.path.join(home, ".icons", theme_name)

    if not os.path.exists(target_path):
        try:
            _printer.info(f"Baking Icons: {theme_name}", backend="themes")
            
            # --- STEP 1: RAM-Disk Workshop & Dynamic index.theme ---
            shm_workspace = os.path.join("/dev/shm", f"awp_masters_{clean_hex}")
            os.makedirs(shm_workspace, exist_ok=True)
            os.makedirs(target_path, exist_ok=True)
            
            # Generate index.theme content dynamically
            # Extract all contexts present in the manifest
            all_contexts = set()
            for action in ICON_MANIFEST:
                for ctx in ICON_MANIFEST[action].keys():
                    all_contexts.add(ctx)
            sorted_contexts = sorted(list(all_contexts))

            # Map folder names to XDG standard context names
            context_map = {
                "places": "Places",
                "mimetypes": "MimeTypes",
                "devices": "Devices",
                "apps": "Applications",
                "legacy": "Actions",
                "actions": "Actions"
            }

            index_lines = [
                "[Icon Theme]",
                f"Name={theme_name}",
                "Inherits=Mint-Y,Adwaita,gnome,hicolor",
                f"Comment=AWP Icon Theme uses {preset} preset and is based on Mint-Y-Purple",
                ""
            ]

            # Build the Directories list: context/size,context/size...
            dir_entries = []
            for ctx in sorted_contexts:
                for size in ICON_SIZES:
                    dir_entries.append(f"{ctx}/{size}")
            
            index_lines.append(f"Directories={','.join(dir_entries)}")
            index_lines.append("")

            # Build each directory section
            for ctx in sorted_contexts:
                ctx_display = context_map.get(ctx, ctx.capitalize())
                index_lines.append(f"# --- {ctx.upper()} FOLDER SECTION ---")
                for size_str in ICON_SIZES:
                    index_lines.append(f"[{ctx}/{size_str}]")
                    
                    # Handle @2x scale
                    base_size = size_str.split('@')[0]
                    scale = 2 if "@2x" in size_str else 1
                    
                    index_lines.append(f"Size={base_size}")
                    if scale > 1:
                        index_lines.append(f"Scale={scale}")
                    index_lines.append(f"Context={ctx_display}")
                    index_lines.append("Type=Fixed")
                    index_lines.append("")

            # Write the generated index.theme
            with open(os.path.join(target_path, "index.theme"), "w") as f:
                f.write("\n".join(index_lines))

            # --- STEP 2: Color Calculation ---
            r_int, g_int, b_int = int(clean_hex[0:2], 16), int(clean_hex[2:4], 16), int(clean_hex[4:6], 16)
            hls = colorsys.rgb_to_hls(r_int/255.0, g_int/255.0, b_int/255.0)
            target_hue_deg = hls[0] * 360
            hue_dist = min(abs(target_hue_deg - 262), 360 - abs(target_hue_deg - 262))
            factor = min(hue_dist / 140.0, 1.0)
            brightness, saturation = round(100 - (40 * factor)), round(100 + (60 * factor))
            im_hue = round(100 + ((target_hue_deg - 262) / 1.8))

            # --- STEP 3: Modulate assets in RAM ---
            for folder_path, files in ICON_MANIFEST["modulate"].items():
                for asset in files:
                    src = os.path.join(template_path, asset)
                    temp_dest = os.path.join(shm_workspace, asset)
                    if os.path.exists(src):
                        subprocess.run([
                            "convert", src, "-modulate", f"{brightness},{saturation},{im_hue}", 
                            "-strip", temp_dest
                        ], check=True)

            # --- STEP 4: Tree Surgery (Resizing into correct contexts) ---
            for size in ICON_SIZES:
                dim = int(size.split('@')[0])
                if "@2x" in size: dim *= 2
                
                for action, paths in ICON_MANIFEST.items():
                    is_modulating = (action == "modulate")
                    for folder_path, files in paths.items():
                        dest_dir = os.path.join(target_path, folder_path, size)
                        os.makedirs(dest_dir, exist_ok=True)
                        for asset in files:
                            base_path = shm_workspace if is_modulating else template_path
                            src = os.path.join(base_path, asset)
                            dest = os.path.join(dest_dir, asset)
                            if os.path.exists(src):
                                subprocess.run([
                                    "convert", src, "-background", "none", 
                                    "-thumbnail", f"{dim}x{dim}", "-strip", dest
                                ], check=True)

                # --- STEP 4.1: Universal Symlinks ---
                for context in sorted_contexts:
                    current_dir = os.path.join(target_path, context, size)
                    if os.path.exists(current_dir):
                        for master, links in SYMLINK_MAP.items():
                            master_file = os.path.join(current_dir, master)
                            if os.path.exists(master_file):
                                for link_name in links:
                                    link_path = os.path.join(current_dir, link_name)
                                    if os.path.lexists(link_path): os.remove(link_path)
                                    os.symlink(master, link_path)

            # --- STEP 5: Top-Level Preview ---
            if icon and os.path.exists(icon):
                preview_dest = os.path.join(target_path, "folder.png")
                subprocess.run(["convert", icon, "-strip", preview_dest], check=True)

            # --- STEP 6: Finalize ---
            shutil.rmtree(shm_workspace)
            subprocess.run(["gtk-update-icon-cache", "-f", "-t", target_path], check=False)
            _printer.success(f"Icon theme {theme_name} ready", backend="themes")
            
        except Exception as e:
            _printer.error(f"Bake failed: {e}", backend="themes")
            if os.path.exists(target_path):
                shutil.rmtree(target_path)
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
