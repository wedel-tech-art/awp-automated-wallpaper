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
from core.constants import ICON_PRESETS, THEME_PRESETS, TARGET_ASSETS, ICON_MANIFEST, ICON_MANIFEST_SVG, SYMLINK_MAP, ICON_SIZES
from core.printer import get_printer
_printer = get_printer()


def _build_color_replacements(config, clean_hex, new_rgb):
    """
    Build the color replacements list, deriving family shades if needed.
    All dynamic hue shifts are calculated using the active Mint background hex.
    """
    replacements = []
    family = {}
    
    # Check if the preset defines a family scaling ratio matrix
    if config.get('family_ratios'):
        # Convert hex to normalized RGB values
        r, g, b = int(clean_hex[0:2], 16)/255.0, int(clean_hex[2:4], 16)/255.0, int(clean_hex[4:6], 16)/255.0
        # Convert to HSV to scale saturation and value dynamically
        h, s, v = colorsys.rgb_to_hsv(r, g, b)
        
        # Populate the derived family dictionary with custom shades
        for name, (sat_ratio, val_ratio) in config['family_ratios'].items():
            nr, ng, nb = colorsys.hsv_to_rgb(h, min(1.0, s * sat_ratio), min(1.0, v * val_ratio))
            family[name] = f"{int(nr*255):02x}{int(ng*255):02x}{int(nb*255):02x}"
            family[f"{name}_rgb"] = f"{int(nr*255)}, {int(ng*255)}, {int(nb*255)}"

    # Map preset targets to their calculated replacement values
    for old, kind in config['colors']:
        if kind == 'hex':
            replacements.append((old, clean_hex))
        elif kind == 'rgb':
            replacements.append((old, new_rgb))
        else:
            # Safe check to prevent KeyErrors if a ratio is missing
            if kind in family:
                replacements.append((old, family[kind]))
            else:
                _printer.warning(f"Color kind '{kind}' not found in derived family ratios.", backend="themes")
                
    return replacements


def _modulate_assets(config, target_path, clean_hex):
    """
    Studio-Mastered PNG modulation engine.
    Phase-2 Closed Loop Feedback Control Edition (Universal Sobriety).
    Bakes a 1x1 test pixel in memory to measure and counteract non-linear color drift,
    ensuring consistent, matte, and premium GTK2 widgets across all presets.
    """
    if not config.get('assets'):
        return

    # --- FASE 0: PARSE ABSOLUTE TARGET VALUES ---
    r_int, g_int, b_int = int(clean_hex[0:2], 16), int(clean_hex[2:4], 16), int(clean_hex[4:6], 16)
    target_hls = colorsys.rgb_to_hls(r_int/255.0, g_int/255.0, b_int/255.0)
    target_hue_deg = target_hls[0] * 360

    source_hue = 203  # Fixed baseline for Breeze-mapped templates

    # First-pass mathematical prediction
    hue_diff = target_hue_deg - source_hue
    if hue_diff < 0: 
        hue_diff += 360
    base_im_hue = round(100 + (hue_diff / 1.7))
    if base_im_hue > 200: 
        base_im_hue -= 200

    # Base factor calculated from distance on the color wheel
    hue_dist = min(abs(target_hue_deg - source_hue), 360 - abs(target_hue_deg - source_hue))
    factor = min(hue_dist / 140.0, 1.0)
    
    base_brightness = round(100 - (20 * factor))
    base_saturation = round(100 + (30 * factor))

    # --- FASE 1: THE FEEDBACK LOOP (Virtual Pixel Probe) ---
    probe_source_hex = "#3daee9"  # Master Breeze Blue
    probe_file = os.path.join("/dev/shm", f"awp_probe_{clean_hex}.png")
    
    try:
        # Create the test pixel in RAM
        subprocess.run(["convert", "-size", "1x1", f"xc:{probe_source_hex}", probe_file], check=True)
        # Apply the theoretical modulation to the test pixel
        subprocess.run(["mogrify", "-modulate", f"{base_brightness},{base_saturation},{base_im_hue}", probe_file], check=True)
        
        # Read back the EXACT Hex code that ImageMagick generated
        result_hex = subprocess.check_output([
            "convert", probe_file, "-format", "%[hex:p{0,0}]", "info:"
        ]).decode("utf-8").strip().lower()
        
        # Clean up the virtual pixel immediately
        if os.path.exists(probe_file): 
            os.remove(probe_file)
        
        # Convert the measured result to HLS to analyze drift
        pr, pg, pb = int(result_hex[0:2], 16)/255.0, int(result_hex[2:4], 16)/255.0, int(result_hex[4:6], 16)/255.0
        measured_hls = colorsys.rgb_to_hls(pr, pg, pb)
        measured_hue_deg = measured_hls[0] * 360

        # --- FASE 2: REALITY-BASED CALIBRATION ("Sobriedad Universal") ---
        hue_drift = target_hue_deg - measured_hue_deg
        corrected_hue_diff = hue_diff + hue_drift
        final_im_hue = round(100 + (corrected_hue_diff / 1.7))
        if final_im_hue > 200: final_im_hue -= 200
        if final_im_hue < 0: final_im_hue = 0

        # Universal Elastic Compactor
        final_brightness = base_brightness

        if 30 <= measured_hue_deg <= 165:
            # Zone Yellows / Greens
            final_brightness = min(base_brightness, 80)
            final_saturation = round(100 + (5 * factor))
        elif 300 <= measured_hue_deg <= 350:
            # Zone Fucsias / Magentas
            final_brightness = min(base_brightness, 85)
            final_saturation = round(100 + (15 * factor))
        elif measured_hue_deg < 20 or measured_hue_deg > 355:
            # --- SURGICAL RED ZONE TRIGGER ---
            # Shifting to -10 to completely kill the remaining orange bleeding 
            # specially in reds.
            final_im_hue = max(0, final_im_hue - 8)
            final_brightness = min(base_brightness, 85)
            final_saturation = min(base_saturation, 110)
        else:
            # Rest (blues, purples)
            final_saturation = round(100 + (25 * factor))

    except Exception as e:
        _printer.warning(f"Feedback probe failed ({e}). Falling back to linear equations.", backend="themes")
        final_im_hue = base_im_hue
        final_brightness = base_brightness
        final_saturation = base_saturation
        measured_hue_deg = target_hue_deg

    _printer.info(
        f"Theme Feedback Loop: Target:{target_hue_deg:.1f}° -> Measured:{measured_hue_deg:.1f}° | "
        f"Calibrated Params -> H:{final_im_hue} B:{final_brightness}% S:{final_saturation}%", 
        backend="themes"
    )

    # --- FASE 3: RECURSIVE FILE SYSTEM EXECUTION ---
    # Index the target paths dynamically using the elastic folder mapping matrix
    filename_to_paths = {}
    for root, dirs, files in os.walk(target_path):
        for f in files:
            filename_to_paths.setdefault(f, []).append(os.path.join(root, f))

    # Apply the audited, ultra-calibrated values exclusively over target targets
    for filename in config['assets']:
        if filename in filename_to_paths:
            for asset_file in filename_to_paths[filename]:
                subprocess.run([
                    "mogrify", "-modulate",
                    f"{final_brightness},{final_saturation},{final_im_hue}",
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
                                "-name", "*.css", "-o", 
                                "-name", "*.svg", "-o", 
                                "-name", "*.rc", "-o", 
                                "-name", "gtkrc", "-o",
                                "-name", "index.theme", ")",
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


def bake_awp_icon(hex_color: str, icon: str = None, preset: str = "mint"):
    """
    OWStudios Dynamic Icon Engine - MANIFEST EDITION
    - Generates index.theme dynamically based on ICON_MANIFEST and ICON_SIZES.
    - Supports SVG-based presets via ICON_MANIFEST_SVG (e.g. sweet-svg).
    """
    if not hex_color or hex_color == "":
        return None

    clean_hex = hex_color.lstrip('#').lower()

    # --- PRESET LOGIC: supports dict (svg-capable) or plain string ---
    preset_config = ICON_PRESETS.get(preset, "template-icon-presets/mint")
    if isinstance(preset_config, dict):
        template_folder = preset_config['path']
    else:
        template_folder = preset_config

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

            has_svg = isinstance(preset_config, dict) and preset_config.get('colors')

            # Collect all contexts from both manifests
            all_contexts = set()
            for action in ICON_MANIFEST:
                for ctx in ICON_MANIFEST[action].keys():
                    all_contexts.add(ctx)
            if has_svg:
                for action in ICON_MANIFEST_SVG:
                    for ctx in ICON_MANIFEST_SVG[action].keys():
                        all_contexts.add(ctx)
            sorted_contexts = sorted(list(all_contexts))

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

            png_contexts = set()
            for action in ICON_MANIFEST:
                for ctx in ICON_MANIFEST[action].keys():
                    png_contexts.add(ctx)

            svg_contexts = set()
            if has_svg:
                for action in ICON_MANIFEST_SVG:
                    for ctx in ICON_MANIFEST_SVG[action].keys():
                        svg_contexts.add(ctx)

            dir_entries = []
            # PNG sized first
            for ctx in sorted(png_contexts):
                for size in ICON_SIZES:
                    dir_entries.append(f"{ctx}/{size}")
            # SVG scalable inside context folder
            if has_svg:
                for ctx in sorted(svg_contexts):
                    dir_entries.append(f"{ctx}/scalable")

            index_lines.append(f"Directories={','.join(dir_entries)}")
            index_lines.append("")

            # PNG sections
            for ctx in sorted(png_contexts):
                ctx_display = context_map.get(ctx, ctx.capitalize())
                index_lines.append(f"# --- {ctx.upper()} FOLDER SECTION ---")
                for size_str in ICON_SIZES:
                    index_lines.append(f"[{ctx}/{size_str}]")
                    base_size = size_str.split('@')[0]
                    scale = 2 if "@2x" in size_str else 1
                    index_lines.append(f"Size={base_size}")
                    if scale > 1:
                        index_lines.append(f"Scale={scale}")
                    index_lines.append(f"Context={ctx_display}")
                    index_lines.append("Type=Fixed")
                    index_lines.append("")

            # SVG scalable sections
            if has_svg:
                for ctx in sorted(svg_contexts):
                    ctx_display = context_map.get(ctx, ctx.capitalize())
                    index_lines.append(f"# --- {ctx.upper()} SCALABLE SECTION ---")
                    index_lines.append(f"[{ctx}/scalable]")
                    index_lines.append("Size=48")
                    index_lines.append("MinSize=16")
                    index_lines.append("MaxSize=512")
                    index_lines.append(f"Context={ctx_display}")
                    index_lines.append("Type=Scalable")
                    index_lines.append("")

            with open(os.path.join(target_path, "index.theme"), "w") as f:
                f.write("\n".join(index_lines))

            # --- STEP 2: Color Calculation (PNG modulation) ---
            r_int, g_int, b_int = int(clean_hex[0:2], 16), int(clean_hex[2:4], 16), int(clean_hex[4:6], 16)
            hls = colorsys.rgb_to_hls(r_int/255.0, g_int/255.0, b_int/255.0)
            target_hue_deg = hls[0] * 360
            hue_dist = min(abs(target_hue_deg - 262), 360 - abs(target_hue_deg - 262))
            factor = min(hue_dist / 140.0, 1.0)
            brightness, saturation = round(100 - (40 * factor)), round(100 + (60 * factor))
            im_hue = round(100 + ((target_hue_deg - 262) / 1.8))

            # --- STEP 3: Modulate PNG assets in RAM ---
            for folder_path, files in ICON_MANIFEST["modulate"].items():
                for asset in files:
                    src = os.path.join(template_path, asset)
                    temp_dest = os.path.join(shm_workspace, asset)
                    if os.path.exists(src):
                        subprocess.run([
                            "convert", src, "-modulate", f"{brightness},{saturation},{im_hue}",
                            "-strip", temp_dest
                        ], check=True)

            # --- STEP 3.5: SVG Recolor in RAM (svg-capable presets only) ---
            if has_svg:
                _printer.info("Applying SVG color replacements...", backend="themes")
                new_rgb = f"{r_int}, {g_int}, {b_int}"
                svg_replacements = _build_color_replacements(preset_config, clean_hex, new_rgb)
                # Copy only svg_recolor SVGs into workspace
                for folder_path, files in ICON_MANIFEST_SVG["svg_recolor"].items():
                    for asset in files:
                        src = os.path.join(template_path, asset)
                        temp_dest = os.path.join(shm_workspace, asset)
                        if os.path.exists(src):
                            shutil.copy2(src, temp_dest)
                # Apply color replacements across all SVGs in workspace
                for old, new in svg_replacements:
                    subprocess.run([
                        "find", shm_workspace, "-type", "f", "-name", "*.svg",
                        "-exec", "sed", "-i", f"s/{old}/{new}/gI", "{}", "+"
                    ], check=True)

            # --- STEP 4: Tree Surgery ---
            # PNG assets: resize into sized context folders
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

            # SVG assets: copy into {ctx}/scalable folders
            if has_svg:
                for action, paths in ICON_MANIFEST_SVG.items():
                    for folder_path, files in paths.items():
                        dest_dir = os.path.join(target_path, folder_path, "scalable")
                        os.makedirs(dest_dir, exist_ok=True)
                        for asset in files:
                            base_path = shm_workspace if action == "svg_recolor" else template_path
                            src = os.path.join(base_path, asset)
                            dest = os.path.join(dest_dir, asset)
                            if os.path.exists(src):
                                shutil.copy2(src, dest)
                                
            # --- STEP 4.2: SVG Symlinks in scalable folders ---
            if has_svg:
                for context in sorted_contexts:
                    current_dir = os.path.join(target_path, context, "scalable")
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



def bake_awp_icon_original(hex_color: str, icon: str = None, preset: str = "mint"):
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
