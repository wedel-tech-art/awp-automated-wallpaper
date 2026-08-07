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
from core.constants import (
    ICON_PRESETS,
    THEME_PRESETS,
    CURSOR_PRESETS,
    TARGET_ASSETS,
    ICON_SIZES,
    ICON_REGISTRY,
    AWP_DIR,
    SVG_TEMPLATES
)
from core.utils import (
    # HSV conversions (for SVG replacements)
    hex_to_hsv,
    hsv_to_hex,
    apply_hue_shift,
    apply_sat_val,
    calculate_family_color,
    hex_to_rgb,
    rgb_to_hex,
    
    # HLS conversions (for modulate)
    hex_to_hls,
    hls_to_hex,
    
    # Math utilities
    signed_hue_diff,
    clamp,
    
    # Config helpers
    get_source_hex_from_config
)
from core.printer import get_printer
_printer = get_printer()


def _build_gtk_replacements(config, clean_hex, new_rgb):
    """
    Build color replacement tuples for GTK theme files.

    Unified approach:
        - Hex colors: auto-generate both HEX and RGB replacements
        - RGB colors: replace only the 3 RGB values (alpha preserved automatically)
        - RGB with family_ratio: uses calculated color from family_ratios
        - Derived colors: auto-generate both HEX and RGB replacements

    Args:
        config: Theme preset configuration dictionary
        clean_hex: Target hex color without '#' (e.g., 'bebe00')
        new_rgb: Target RGB values as a string (e.g., '190, 190, 0')

    Returns:
        list: List of (old_string, new_string) replacement tuples
    """
    replacements = []
    family = {}

    # --- Calculate derived family colors ---
    if config.get('family_ratios'):
        h, _, _ = hex_to_hsv(clean_hex)
        hue_degrees = h * 360

        for name, (hue_shift_deg, sat_ratio, val_ratio) in config['family_ratios'].items():
            if name == 'source_hex':
                family[name] = clean_hex
            else:
                # GTK trap zone for XFWM buttons on purple/blue hues
                if hue_shift_deg != 0 and 220.0 <= hue_degrees <= 310.0:
                    hue_shift_deg = -hue_shift_deg * 1.4
                family[name] = calculate_family_color(
                    clean_hex, sat_ratio, val_ratio, hue_shift_deg
                )

    # --- Build replacements ---
    for old, kind in config['colors']:
        if kind == 'hex':
            # --- Replace HEX ---
            replacements.append((old, clean_hex))

            # --- Auto-generate RGB (3 values only) ---
            r_old, g_old, b_old = int(old[0:2], 16), int(old[2:4], 16), int(old[4:6], 16)
            replacements.append((f"{r_old}, {g_old}, {b_old}", new_rgb))

        elif kind == 'source_hex':
            # --- source_hex maps directly to clean_hex ---
            replacements.append((old, clean_hex))

        elif kind == 'rgb' or kind.endswith('_rgb'):
            # --- RGB with optional family_ratio ---
            base_name = kind.replace('_rgb', '') if kind.endswith('_rgb') else kind
            if base_name in family:
                # Use calculated RGB from family_ratios
                r_new, g_new, b_new = hex_to_rgb(family[base_name])
                replacements.append((old, f"{r_new}, {g_new}, {b_new}"))
            else:
                # Fallback: use main RGB
                replacements.append((old, new_rgb))

        elif kind in family:
            # --- Derived hex color ---
            replacements.append((old, family[kind]))

            # --- Auto-generate RGB for derived color ---
            r_old, g_old, b_old = int(old[0:2], 16), int(old[2:4], 16), int(old[4:6], 16)
            r_new, g_new, b_new = hex_to_rgb(family[kind])
            replacements.append((f"{r_old}, {g_old}, {b_old}", f"{r_new}, {g_new}, {b_new}"))

        else:
            _printer.warning(
                f"Color kind '{kind}' not found in family ratios.",
                backend="themes"
            )

    return replacements


def _modulate_gtk_assets(config, target_path, clean_hex, source_hex=None):
    """
    Modulate GTK PNG assets using PIL with dynamic fuzz.
    Elegant, no halo, preserves whites and insensitive variants.
    """
    from PIL import Image

    if not config or not config.get('assets'):
        return

    if not source_hex:
        source_hex = get_source_hex_from_config(config)
        if not source_hex:
            _printer.error("No source_hex found!", backend="themes")
            return

    _printer.info(
        f"Modulating GTK assets (PIL): #{source_hex} → #{clean_hex}",
        backend="themes"
    )

    src_r, src_g, src_b = hex_to_rgb(source_hex)
    tgt_r, tgt_g, tgt_b = hex_to_rgb(clean_hex)

    diff_r = tgt_r - src_r
    diff_g = tgt_g - src_g
    diff_b = tgt_b - src_b

    # --- Dynamic Fuzz ---
    min_fuzz = 30
    max_fuzz = 300  # Elegant balance

    filename_to_paths = {}
    for root, _, files in os.walk(target_path):
        for f in files:
            if f in config['assets']:
                filename_to_paths.setdefault(f, []).append(os.path.join(root, f))

    success_count = 0
    for filename in config['assets']:
        if filename in filename_to_paths:
            for asset_file in filename_to_paths[filename]:
                try:
                    img = Image.open(asset_file).convert("RGBA")
                    pixels = img.load()
                    width, height = img.size

                    for y in range(height):
                        for x in range(width):
                            r, g, b, a = pixels[x, y]
                            if a == 0:
                                continue

                            dist = abs(r - src_r) + abs(g - src_g) + abs(b - src_b)

                            if dist <= min_fuzz:
                                new_r = r + diff_r
                                new_g = g + diff_g
                                new_b = b + diff_b

                            elif dist <= max_fuzz:
                                ratio = 1.0 - ((dist - min_fuzz) / (max_fuzz - min_fuzz))
                                ratio = max(0, min(1, ratio))

                                new_r = int(r + diff_r * ratio)
                                new_g = int(g + diff_g * ratio)
                                new_b = int(b + diff_b * ratio)

                            else:
                                continue

                            new_r = max(0, min(255, new_r))
                            new_g = max(0, min(255, new_g))
                            new_b = max(0, min(255, new_b))

                            pixels[x, y] = (new_r, new_g, new_b, a)

                    img.save(asset_file, "PNG")
                    success_count += 1

                except Exception as e:
                    _printer.warning(
                        f"Failed to modulate {os.path.basename(asset_file)}: {e}",
                        backend="themes"
                    )

    if success_count:
        _printer.info(f"Modulated {success_count} GTK assets", backend="themes")


def _modulate_icon_assets(png_manifest, template_path, shm_workspace, 
                          clean_hex, source_hex):
    """
    Icon PNG modulation using selective color replacement.
    """
    modulate_assets = []
    for folder_path, files in png_manifest["modulate"].items():
        modulate_assets.extend(files)
    
    if not modulate_assets or not source_hex:
        return

    _printer.info(
        f"Replacing color in icon assets: #{source_hex} → #{clean_hex}",
        backend="themes"
    )

    file_map = {}
    for root, _, files in os.walk(template_path):
        for f in files:
            if f in modulate_assets:
                rel_path = os.path.relpath(root, template_path)
                file_map.setdefault(f, []).append({
                    'src': os.path.join(root, f),
                    'rel_dir': rel_path
                })

    success_count = 0
    for filename in modulate_assets:
        if filename in file_map:
            for entry in file_map[filename]:
                dest_dir = os.path.join(shm_workspace, entry['rel_dir'])
                dest_file = os.path.join(dest_dir, filename)
                os.makedirs(dest_dir, exist_ok=True)
                
                try:
                    subprocess.run([
                        "convert", entry['src'],
                        "-fuzz", "19%",
                        "-fill", f"#{clean_hex}",
                        "-opaque", f"#{source_hex}",
                        "-strip", dest_file
                    ], check=True, capture_output=True)
                    success_count += 1
                except subprocess.CalledProcessError as e:
                    _printer.warning(
                        f"Failed to replace color in {filename}: {e}",
                        backend="themes"
                    )
    
    if success_count:
        _printer.info(f"Replaced color in {success_count} icon assets", backend="themes")


# =============================================================================
# BAKE FUNCTIONS
# =============================================================================

def bake_awp_theme(hex_color: str, icon: str = None, preset: str = 'breeze', preset_name: str = None):
    """Dynamic Theme Synthesis Engine (AWP-G2) - Multi-Preset Edition"""
    if not hex_color or hex_color == "":
        return None

    config = THEME_PRESETS[preset]

    clean_hex = hex_color.lstrip('#').lower()
    
    # Get source_hex from config
    source_hex = get_source_hex_from_config(config)
    
    theme_name = f"awp-gtk-{preset}-{clean_hex}"
    home = os.path.expanduser("~")
    template_path = os.path.join(home, "awp", config['path'])
    
    if preset_name:
        # Per-preset path: ~/awp/presets/{preset_name}/themes/gtk/{theme_name}
        target_path = os.path.join(AWP_DIR, 'presets', preset_name, 'themes', 'gtk', theme_name)
    else:
        # Global path: ~/.themes/{theme_name} (for Fool Bake and backward compatibility)
        target_path = os.path.join(home, ".themes", theme_name)

    if not os.path.exists(target_path):
        try:
            _printer.info(f"Baking Theme: {theme_name} -> {target_path}", backend="themes")
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
            color_replacements = _build_gtk_replacements(config, clean_hex, new_rgb)

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
            _modulate_gtk_assets(config, target_path, clean_hex, source_hex)

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

def _build_manifests(registry, preset_name=None):
    """
    Dynamically generates the PNG and SVG processing manifests along with the
    symlink map based on the active icon preset and registry rules.
    """
    png_manifest = {"modulate": {}, "original": {}}
    svg_manifest = {"svg_recolor": {}, "svg_original": {}}
    symlink_map = {}

    for name, config in registry.items():
        context = config["context"]
        
        # Default baseline rules for the system matrix
        png_action = "modulate"
        svg_action = "svg_recolor"

        # Evaluate PNG rule exceptions
        if "png_action" in config:
            if preset_name in config["png_action"].get("original", []):
                png_action = "original"

        # Evaluate SVG rule exceptions
        if "svg_action" in config:
            if preset_name in config["svg_action"].get("svg_original", []):
                svg_action = "svg_original"

        # Categorize assets into their respective destination manifests
        png_manifest[png_action].setdefault(context, []).append(f"{name}.png")
        svg_manifest[svg_action].setdefault(context, []).append(f"{name}.svg")

        # Map symlinks if present in the configuration schema
        if config.get("symlinks"):
            symlink_map[f"{name}.png"] = [f"{s}.png" for s in config["symlinks"]]
            symlink_map[f"{name}.svg"] = [f"{s}.svg" for s in config["symlinks"]]

    return png_manifest, svg_manifest, symlink_map


def _build_icon_replacements(config, clean_hex, new_rgb):
    """
    Icon themes: no trap zone, pure color math.
    Called by bake_awp_icon().
    """
    replacements = []
    family = {}
    
    if config.get('family_ratios'):
        for name, (hue_shift_deg, sat_ratio, val_ratio) in config['family_ratios'].items():
            # Icons: no trap zone, even if hue_shift != 0
            family[name] = calculate_family_color(clean_hex, sat_ratio, val_ratio, hue_shift_deg)
            r, g, b = hex_to_rgb(family[name])
            family[f"{name}_rgb"] = f"{r}, {g}, {b}"
    
    # Build replacements (same logic)
    for old, kind in config['colors']:
        if kind == 'hex':
            replacements.append((old, clean_hex))
        elif kind == 'rgb':
            replacements.append((old, new_rgb))
        elif kind in family:
            replacements.append((old, family[kind]))
        else:
            _printer.warning(f"Color kind '{kind}' not found in derived family ratios.", backend="themes")
    
    return replacements
    

def bake_awp_icon(hex_color: str, icon: str = None, preset: str = "mint", preset_name: str = None):
    """
    AWP Dynamic Icon Engine
    - Generates index.theme dynamically based on ICON_REGISTRY and ICON_SIZES.
    - Supports SVG-based presets via svg_manifest.
    """
    if not hex_color or hex_color == "":
        return None

    png_manifest, svg_manifest, symlink_map = _build_manifests(ICON_REGISTRY, preset_name=preset)

    clean_hex = hex_color.lstrip('#').lower()
    
    # --- RGB values for SVG recolor ---
    r_int = int(clean_hex[0:2], 16)
    g_int = int(clean_hex[2:4], 16)
    b_int = int(clean_hex[4:6], 16)

    # --- PRESET LOGIC: supports dict (svg-capable) or plain string ---
    preset_config = ICON_PRESETS.get(preset, "template-icon-presets/mint")
    if isinstance(preset_config, dict):
        template_folder = preset_config['path']
    else:
        template_folder = preset_config

    theme_name = f"awp-icons-{preset}-{clean_hex}"
    home = os.path.expanduser("~")
    template_path = os.path.join(home, "awp", template_folder)
   
    if preset_name:
        # Per-preset path: ~/awp/presets/{preset_name}/themes/icons/{theme_name}
        target_path = os.path.join(AWP_DIR, 'presets', preset_name, 'themes', 'icons', theme_name)
    else:
        # Global path: ~/.icons/{theme_name} (for Fool Bake and backward compatibility)
        target_path = os.path.join(home, ".icons", theme_name)

    if not os.path.exists(target_path):
        try:
            _printer.info(f"Baking Icons: {theme_name} -> {target_path}", backend="themes")

            # --- STEP 1: RAM-Disk Workshop & Dynamic index.theme ---
            shm_workspace = os.path.join("/dev/shm", f"awp_masters_{clean_hex}")
            os.makedirs(shm_workspace, exist_ok=True)
            os.makedirs(target_path, exist_ok=True)

            has_svg = isinstance(preset_config, dict) and preset_config.get('colors')

            # Collect all contexts from both manifests
            all_contexts = set()
            for action in png_manifest:
                for ctx in png_manifest[action].keys():
                    all_contexts.add(ctx)
            if has_svg:
                for action in svg_manifest:
                    for ctx in svg_manifest[action].keys():
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
                "# ==============================================================================",
                "# AWP DYNAMIC ICON PARADIGM STRUCTURE",
                "# ==============================================================================",
                f"# CONFIGURATION LAYOUT: {preset.upper()} Core Registry Generation",
                "# FRAMEWORK STRUCTURE: Dual Matrix Engine (Fixed PNG Chunks x Scalable SVG Layers)",
                "# UPSTREAM HERITAGE: Linux Mint Desktop Ecosystem (Mint-Y-Purple Baseline)",
                "# TARGET COMPATIBILITY: XFCE 4.18+ / GtkIconTheme System Unification",
                "# ==============================================================================",
                "",
                "[Icon Theme]",
                f"Name={theme_name}",
                f"Comment=AWP Hybrid Engine • Dynamic Multi-Context Icon Set (Upstream Baseline: Mint-Y-Purple)",
                "Inherits=Mint-Y,Adwaita,gnome,hicolor",
                "Encoding=UTF-8",
                ""
            ]

            png_contexts = set()
            for action in png_manifest:
                for ctx in png_manifest[action].keys():
                    png_contexts.add(ctx)

            svg_contexts = set()
            if has_svg:
                for action in svg_manifest:
                    for ctx in svg_manifest[action].keys():
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

            # --- STEP 2+3: Modulate PNG assets using icon-specific function ---
            # Get source_hex from icon preset
            icon_source_hex = get_source_hex_from_config(preset_config) if isinstance(preset_config, dict) else None

            if icon_source_hex:
                _modulate_icon_assets(
                    png_manifest=png_manifest,
                    template_path=template_path,
                    shm_workspace=shm_workspace,
                    clean_hex=clean_hex,
                    source_hex=icon_source_hex
                )

            # --- STEP 3.5: SVG Recolor in RAM (svg-capable presets only) ---
            if has_svg:
                _printer.info("Applying SVG color replacements...", backend="themes")
                new_rgb = f"{r_int}, {g_int}, {b_int}"
                svg_replacements = _build_icon_replacements(preset_config, clean_hex, new_rgb)
                # Copy only svg_recolor SVGs into workspace
                for folder_path, files in svg_manifest["svg_recolor"].items():
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

                for action, paths in png_manifest.items():
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
                        for master, links in symlink_map.items():
                            master_file = os.path.join(current_dir, master)
                            if os.path.exists(master_file):
                                for link_name in links:
                                    link_path = os.path.join(current_dir, link_name)
                                    if os.path.lexists(link_path): os.remove(link_path)
                                    os.symlink(master, link_path)

            # SVG assets: copy into {ctx}/scalable folders
            if has_svg:
                for action, paths in svg_manifest.items():
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
                        for master, links in symlink_map.items():
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

def bake_awp_cursor(hex_color: str, icon: str = None, preset: str = "oxy", preset_name: str = None):
    """
    AWP Dynamic Cursor Compiling Engine
    - Reads raw multi-frame X11 binary blobs from preset templates.
    - Matches native BGRA pixel gradients via fine-tuned hardware filters.
    - Shifts color spaces mathematically to the active workspace phase.
    - Deploys a custom cursor theme package directly into ~/.icons/
    """
    if not hex_color or hex_color == "":
        return None

    clean_hex = hex_color.lstrip('#').lower()
    theme_name = f"awp-cursor-{preset}-{clean_hex}"
    
    home = os.path.expanduser("~")
    
    # Get preset config - handle both dict and string formats
    preset_config = CURSOR_PRESETS.get(preset, CURSOR_PRESETS.get('oxy'))
    if isinstance(preset_config, dict):
        template_folder = preset_config['path']
    else:
        template_folder = preset_config
    
    template_path = os.path.join(home, "awp", template_folder)
    
    if preset_name:
        # Per-preset path: ~/awp/presets/{preset_name}/themes/cursors/{theme_name}
        target_path = os.path.join(AWP_DIR, 'presets', preset_name, 'themes', 'cursors', theme_name)
    else:
        # Global path: ~/.icons/{theme_name} (for Fool Bake and backward compatibility)
        target_path = os.path.join(home, ".icons", theme_name)

    # Skip heavy work if this color iteration has already been compiled
    if os.path.exists(target_path):
        return theme_name

    try:
        _printer.info(f"Baking Cursors: {theme_name} -> {target_path}", backend="themes")

        # Extract targeted target RGB channels out of workspace hex
        target_r = int(clean_hex[0:2], 16)
        target_g = int(clean_hex[2:4], 16)
        target_b = int(clean_hex[4:6], 16)

        # Copy over the structural template skeleton (keeping links alive)
        shutil.copytree(template_path, target_path, symlinks=True)
        cursors_dir = os.path.join(target_path, "cursors")

        # Mutate the actual state machine binaries
        for filename in os.listdir(cursors_dir):
            file_path = os.path.join(cursors_dir, filename)
            if os.path.islink(file_path):
                continue

            with open(file_path, "rb") as f:
                binary_data = bytearray(f.read())

            # Sweep pixel chunks (4 bytes each: B, G, R, A)
            for i in range(0, len(binary_data), 4):
                if i + 4 > len(binary_data):
                    break

                b = binary_data[i]
                g = binary_data[i+1]
                r = binary_data[i+2]
                # a = binary_data[i+3] (Alpha preserved for edge anti-aliasing)

                # THE PERFECT OXYGEN FILTER MATRIX:
                # Lower boundary of 60 sweeps up deep shadows along the tail base
                if r > 60 and b == g and b < 50:
                    intensity_factor = r / 147.0

                    # Apply dynamic color-scaling and clamp to hardware maximums
                    binary_data[i]   = min(int(target_b * intensity_factor), 255) # New Blue
                    binary_data[i+1] = min(int(target_g * intensity_factor), 255) # New Green
                    binary_data[i+2] = min(int(target_r * intensity_factor), 255) # New Red

            # Flush the modified matrix back to disk
            with open(file_path, "wb") as f:
                f.write(binary_data)

        # Generate custom index.theme file for instant X11 system registration
        index_path = os.path.join(target_path, "index.theme")
        index_lines = [
            "# ==============================================================================",
            "# AWP HYBRID ARCHITECTURE MANIFEST",
            "# ==============================================================================",
            f"# BASE FRAMEWORK: Oxygen Cursors ({preset.upper()} Core Mutation)",
            "# COMPLIANCE: X11 Mouse Cursor Specification Blob Matrix",
            "# UPSTREAM HERITAGE: oxy-red-argentina (Debian Package: oxygencursors)",
            "# TARGET COMPATIBILITY: X11 / XFCE 4.18+ Pointer State Machine Unification",
            "# ==============================================================================",
            "",
            "[Icon Theme]",
            f"Name={theme_name}",
            f"Comment=AWP Hybrid Engine • Dynamic BGRA Pixel Matrix (Upstream: oxy-red-argentina)",
            "Inherits=core",
            "Encoding=UTF-8"
        ]
        with open(index_path, "w") as f:
            f.write("\n".join(index_lines) + "\n")

        # --- Top-Level Preview ---
        if icon and os.path.exists(icon):
            preview_dest = os.path.join(target_path, "folder.png")
            subprocess.run(["convert", icon, "-strip", preview_dest], check=True)

        _printer.success(f"Cursor theme {theme_name} ready", backend="themes")

    except Exception as e:
        _printer.error(f"Cursor bake failed: {e}", backend="themes")
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


def clean_themes(theme_names: list = None):
    """
    Remove AWP themes from ~/.themes and ~/.icons.
    
    Args:
        theme_names: List of specific theme names to remove.
                     If None, removes ALL awp-* themes.
    
    Returns:
        List of removed item paths
    """
    removed = []
    
    # Helper to check if a theme should be removed
    def should_remove(name):
        if theme_names is None:
            return name.startswith('awp-')
        else:
            return name in theme_names
    
    # Clean ~/.themes
    themes_dir = os.path.expanduser("~/.themes")
    if os.path.exists(themes_dir):
        for item in os.listdir(themes_dir):
            if should_remove(item):
                item_path = os.path.join(themes_dir, item)
                if os.path.isdir(item_path):
                    try:
                        shutil.rmtree(item_path)
                        removed.append(f"~/.themes/{item}")
                    except Exception:
                        pass
    
    # Clean ~/.icons
    icons_dir = os.path.expanduser("~/.icons")
    if os.path.exists(icons_dir):
        for item in os.listdir(icons_dir):
            if should_remove(item):
                item_path = os.path.join(icons_dir, item)
                if os.path.isdir(item_path):
                    try:
                        shutil.rmtree(item_path)
                        removed.append(f"~/.icons/{item}")
                    except Exception:
                        pass
    
    return removed

# =============================================================================
# SVG ICON GENERATION & UTILITIES
# =============================================================================

def generate_icon_from_svg(hex_color, template_name='awp', size=512):
    """
    Generate a PNG icon from an SVG template using rsvg-convert.
    
    Args:
        hex_color: Hex color string (e.g., '#b3004c')
        template_name: SVG template name (default: 'awp')
        size: Output size in pixels (default: 512)
    
    Returns:
        Path to the generated PNG file, or None if failed
    """
    import tempfile
    import time
    
    if not shutil.which('rsvg-convert'):
        return None
    
    # Use /dev/shm for temp files (RAM disk) if available
    if os.path.exists('/dev/shm'):
        unique_id = f"awp_icon_{int(time.time())}_{os.getpid()}"
        temp_dir = os.path.join('/dev/shm', unique_id)
        os.makedirs(temp_dir, exist_ok=True)
    else:
        temp_dir = tempfile.mkdtemp(prefix='awp_icon_')
    
    png_path = os.path.join(temp_dir, 'folder.png')
    
    try:
        svg_template = SVG_TEMPLATES.get(template_name, SVG_TEMPLATES.get('awp'))
        svg_content = svg_template.replace('{{COLOR}}', hex_color)
        
        temp_svg = os.path.join(temp_dir, 'folder.svg')
        with open(temp_svg, 'w') as f:
            f.write(svg_content)
        
        cmd = ['rsvg-convert', '-w', str(size), '-h', str(size), '-o', png_path, temp_svg]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        
        if result.returncode != 0 or not os.path.exists(png_path):
            shutil.rmtree(temp_dir, ignore_errors=True)
            return None
        
        return png_path
        
    except Exception:
        shutil.rmtree(temp_dir, ignore_errors=True)
        return None

def cleanup_temp_icon(icon_path):
    """
    Clean up temporary icon files and directory.
    
    Args:
        icon_path: Path to the temporary icon file
    """
    if not icon_path:
        return
    
    temp_dir = os.path.dirname(icon_path)
    try:
        if os.path.exists(icon_path):
            os.remove(icon_path)
        svg_path = os.path.join(temp_dir, 'folder.svg')
        if os.path.exists(svg_path):
            os.remove(svg_path)
        if os.path.exists(temp_dir) and not os.listdir(temp_dir):
            os.rmdir(temp_dir)
    except OSError:
        pass

def extract_preset_from_theme(theme_name, prefix):
    """
    Extract the preset name from a theme string.
    
    Examples:
        "awp-gtk-breeze-ff0000" → "breeze"
        "awp-icons-mint-ff0000" → "mint"
        "awp-cursor-oxy-ff0000" → "oxy"
    
    Args:
        theme_name: The full theme name (e.g., 'awp-gtk-breeze-ff0000')
        prefix: The prefix to remove (e.g., 'awp-gtk-')
    
    Returns:
        The preset name (e.g., 'breeze'), or None if not found
    """
    if not theme_name:
        return None
    
    if theme_name.startswith(prefix):
        theme_name = theme_name.replace(prefix, '')
    
    # Remove color suffix: "breeze-ff0000" → "breeze"
    parts = theme_name.rsplit('-', 1)
    return parts[0] if parts else theme_name

def extract_color_from_theme(theme_name: str) -> str:
    """
    Extract hex color from a theme name.
    
    Examples:
        "awp-gtk-breeze-ff0000" → "#ff0000"
        "awp-icons-mint-00ff00" → "#00ff00"
        "custom-theme-123456" → "#123456"
        "Adwaita" → None
    
    Args:
        theme_name: The full theme name (e.g., 'awp-gtk-breeze-ff0000')
    
    Returns:
        The hex color with # (e.g., '#ff0000'), or None if no hex found
    """
    if not theme_name:
        return None
    
    # Theme format: *-xxxxxx (6 hex chars at the end)
    parts = theme_name.split('-')
    if len(parts) >= 1:
        possible_hex = parts[-1]
        if len(possible_hex) == 6 and all(c in '0123456789abcdefABCDEF' for c in possible_hex):
            return f"#{possible_hex}"
    
    return None
