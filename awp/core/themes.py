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
from core.constants import ICON_PRESETS, THEME_PRESETS, TARGET_ASSETS
from core.printer import get_printer
_printer = get_printer()


def _build_color_replacements(config, clean_hex, new_rgb):
    """Build the color replacements list, deriving family shades if needed."""
    import colorsys
    
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


def bake_awp_theme(hex_color: str, icon: str = None, preset: str = 'colloid'):
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




def bake_awp_theme_original(hex_color: str, icon: str = None):
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


def bake_awp_icon(hex_color: str, icon: str = None, preset: str = "mint"):
    """
    OWStudios Dynamic Icon Engine - QUALITY FIRST EDITION
    - Modulates masters once in RAM (/dev/shm)
    - Preserves full 32-bit RGBA for smooth anti-aliased borders
    - Uses high-quality thumbnail filtering for scaling
    - Automatically re-brands index.theme for system recognition
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

    FOLDER_ASSETS = [
        "folder-documents.png", "folder-download.png", "folder-drag-accept.png",
        "folder-music.png", "folder-pictures.png", "folder.png", "folder-publicshare.png",
        "folder-recent.png", "folder-saved-search.png", "folder-templates.png",
        "folder-videos.png", "gtk-network.png", "network-workgroup.png",
        "user-bookmarks.png", "user-desktop.png", "user-home.png"
    ]
    TRASH_ASSETS = ["user-trash.png", "user-trash-full.png"]
    
    SYMLINK_MAP = {
        "folder.png": [
            "athena.png", "file-manager.png", "gtk-directory.png", "inode-directory.png",
            "kfm.png", "nautilus-actions-config-tool.png", "nautilus.png", "nemo.png",
            "org.xfce.filemanager.png", "org.xfce.panel.directorymenu.png", 
            "org.xfce.thunar.png", "redhat-filemanager.png", "stock_folder.png",
            "system-file-manager.png", "thunar.png", "Thunar.png", "xfce-filemanager.png"
        ],
        "user-desktop.png": ["desktop.png", "gnome-fs-desktop.png", "org.xfce.panel.showdesktop.png", "org.xfce.xfdesktop.png"],
        "user-home.png": ["folder_home.png", "gnome-fs-home.png"],
        "folder-drag-accept.png": ["folder-open.png"],
        "gtk-network.png": ["folder-remote.png", "org.xfce.gigolo.png"],
        "folder-music.png": ["library-music.png"],
        "network-workgroup.png": ["network-server.png"],
        "user-bookmarks.png": ["xapp-user-favorites.png"]
    }

    if not os.path.exists(target_path):
        try:
            _printer.info(f"Baking Icons: {theme_name}", backend="themes")
            
            # --- STEP 1: RAM-Disk Workshop & Branding ---
            shm_workspace = os.path.join("/dev/shm", f"awp_masters_{clean_hex}")
            os.makedirs(shm_workspace, exist_ok=True)
            os.makedirs(target_path, exist_ok=True)
            
            index_src = os.path.join(template_path, "index.theme")
            if os.path.exists(index_src):
                index_dest = os.path.join(target_path, "index.theme")
                shutil.copy2(index_src, index_dest)
                
                # Update the internal Name field for XFCE
                subprocess.run(["sed", "-i", f"s/^Name=.*/Name={theme_name}/g", index_dest], check=True)
                # Ensure no 'Mint-Y-Purple' inheritance conflicts
                subprocess.run(["sed", "-i", f"s/Mint-Y-Purple/{theme_name}/gI", index_dest], check=True)
            
            # --- STEP 2: Color Calculation (Fletcher-Munson) ---
            r_int, g_int, b_int = int(clean_hex[0:2], 16), int(clean_hex[2:4], 16), int(clean_hex[4:6], 16)
            hls = colorsys.rgb_to_hls(r_int/255.0, g_int/255.0, b_int/255.0)
            target_hue_deg = hls[0] * 360
            
            hue_dist = min(abs(target_hue_deg - 262), 360 - abs(target_hue_deg - 262))
            factor = min(hue_dist / 140.0, 1.0)
            brightness, saturation = round(100 - (40 * factor)), round(100 + (60 * factor))
            im_hue = round(100 + ((target_hue_deg - 262) / 1.8))

            # --- STEP 3: Modulate Masters in RAM (High Quality) ---
            for asset in FOLDER_ASSETS:
                src = os.path.join(template_path, asset)
                temp_dest = os.path.join(shm_workspace, asset)
                if os.path.exists(src):
                    subprocess.run([
                        "convert", src, "-modulate", f"{brightness},{saturation},{im_hue}", 
                        "-strip", temp_dest
                    ], check=True)

            # --- STEP 4: Tree Surgery (Precision Resizing) ---
            sizes = ["16", "16@2x", "22", "22@2x", "24", "24@2x", "32", "32@2x", 
                     "48", "48@2x", "64", "64@2x", "96", "96@2x", "128", "128@2x"]
            
            for size in sizes:
                dim = int(size.split('@')[0])
                if "@2x" in size: dim *= 2
                dest_dir = os.path.join(target_path, "places", size)
                os.makedirs(dest_dir, exist_ok=True)

                for asset in FOLDER_ASSETS:
                    src = os.path.join(shm_workspace, asset)
                    dest = os.path.join(dest_dir, asset)
                    if os.path.exists(src):
                        subprocess.run([
                            "convert", src, "-background", "none", 
                            "-thumbnail", f"{dim}x{dim}", "-strip", dest
                        ], check=True)

                for asset in TRASH_ASSETS:
                    src = os.path.join(template_path, asset)
                    dest = os.path.join(dest_dir, asset)
                    if os.path.exists(src):
                        subprocess.run([
                            "convert", src, "-background", "none", 
                            "-thumbnail", f"{dim}x{dim}", "-strip", dest
                        ], check=True)

                # Symlinks
                for target, links in SYMLINK_MAP.items():
                    for link_name in links:
                        link_path = os.path.join(dest_dir, link_name)
                        if os.path.exists(link_path): os.remove(link_path)
                        os.symlink(target, link_path)

            # --- STEP 5: Top-Level Preview ---
            if icon and os.path.exists(icon):
                preview_dest = os.path.join(target_path, "folder.png")
                subprocess.run(["convert", icon, "-strip", preview_dest], check=True)

            # --- STEP 6: Finalize ---
            shutil.rmtree(shm_workspace)
            subprocess.run(["gtk-update-icon-cache", "-t", target_path], check=False)
            _printer.success(f"Icon theme {theme_name} ready", backend="themes")
            
        except Exception as e:
            _printer.error(f"Bake failed: {e}", backend="themes")
            if os.path.exists(target_path):
                shutil.rmtree(target_path)
            return None
            
    return theme_name



def bake_awp_icon_original(hex_color: str, icon: str = None):
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
