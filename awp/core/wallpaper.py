#!/usr/bin/env python3
"""
AWP - Automated Wallpaper Program
Core Wallpaper Module

Wallpaper composition engine. Given a template + color, produces one
composed PNG (modulated background + optional logo overlay).

Public:
    generate_wallpaper(template_id, hex_color, output_path) -> bool
    compute_wallpaper_name(hex_color, style_id) -> str

Helpers (used internally):
    generate_background(hex_color, template_data) -> str
    shift_svg_hue(svg_content, new_accent, original_hue) -> str
    get_logo_color(hex_color, whiteness_factor) -> str
"""

import os
import re
import shutil
import subprocess
import colorsys
from pathlib import Path

from PIL import Image, ImageStat

from core.constants import (
    WALLPAPER_SVG_TEMPLATES,
    DEFAULT_WALLPAPER_TEMPLATE,
    SVG_TEMPLATES,
    AWP_DIR,
)
from core.utils import (
    hex_to_hsv,
    hsv_to_hex,
    hex_to_hls,
    hls_to_hex,
)
from core.printer import get_printer

_printer = get_printer()


# =============================================================================
# NAMING
# =============================================================================

def compute_wallpaper_name(hex_color: str, style_id: str) -> str:
    """
    Compute the wallpaper filename for a given color and wallpaper style.

    Formula:
        {filename_prefix}-{hue:03d}-{hex}.png

    This is the canonical naming function. Any tool that needs to predict
    or reconstruct a wallpaper filename should call this.
    """
    template_data = WALLPAPER_SVG_TEMPLATES.get(style_id)
    if not template_data:
        return "(unavailable)"

    filename_prefix = template_data.get("filename_prefix", "awp-center")

    clean_hex = hex_color.lstrip('#')
    try:
        r = int(clean_hex[0:2], 16)
        g = int(clean_hex[2:4], 16)
        b = int(clean_hex[4:6], 16)
    except ValueError:
        return "(bad color)"

    h, l, s = colorsys.rgb_to_hls(r / 255, g / 255, b / 255)
    target_hue_deg = int(h * 360)

    return f"{filename_prefix}-{target_hue_deg:03d}-{clean_hex}.png"


# =============================================================================
# SVG HUE SHIFTING
# =============================================================================

def shift_svg_hue(svg_content: str, new_accent: str, original_hue: float = None) -> str:
    """
    Replace hex colors in an SVG with colors that have a new hue.
    """
    NEUTRAL_COLORS = ['#000000', '#505050', '#eeeeee', '#ffffff']
    clean_new = new_accent.lstrip('#')
    new_h, new_s, new_v = hex_to_hsv(clean_new)
    new_hue = new_h

    hex_pattern = r'#[0-9a-fA-F]{6}'

    def replace_hex(match):
        hex_color = match.group(0)
        clean = hex_color.lstrip('#')

        if hex_color.lower() in [c.lower() for c in NEUTRAL_COLORS]:
            return hex_color

        h, s, v = hex_to_hsv(clean)
        h_deg = h * 360

        should_shift = False
        if original_hue is not None:
            if abs(h_deg - original_hue) < 30 or abs(h_deg - (original_hue - 360)) < 30:
                should_shift = True
        else:
            should_shift = True

        if should_shift:
            return f"#{hsv_to_hex(new_hue, s, v)}"
        else:
            return hex_color

    return re.sub(hex_pattern, replace_hex, svg_content, flags=re.IGNORECASE)


# =============================================================================
# LOGO COLOR
# =============================================================================

def get_logo_color(hex_color: str, whiteness_factor: float = 0.4) -> str:
    """
    Generate a "whiter" version of a color using HLS.
    Same hue, but higher lightness (adds white).

    Args:
        hex_color: The target hex color (e.g., '#b7004f')
        whiteness_factor: 0.0 = pure target, 1.0 = pure white

    Returns:
        str: A lighter version of the color with same hue
    """
    clean = hex_color.lstrip('#')
    h, l, s = hex_to_hls(clean)

    # Increase lightness (add white)
    new_l = l + (1.0 - l) * whiteness_factor

    # Keep saturation the same
    new_s = s

    new_hex = hls_to_hex(h, new_l, new_s)
    return f"#{new_hex}"


# =============================================================================
# BACKGROUND GENERATION
# =============================================================================

def generate_background(hex_color: str, template_data: dict) -> str:
    """
    Generate the background for a template.
    Supports both 'image_bg' (PNG/JPG/etc) and 'svg_bg' (rendered SVG).
    Returns the path to the temporary background PNG.
    """
    WALLPAPER_DIR = AWP_DIR / "wallpapers"
    template_type = template_data.get("type", "image_bg")

    # ─── IMAGE Background ───
    if template_type == "image_bg":
        bg_filename = template_data.get("background")

        if not bg_filename:
            _printer.error(f"No background filename specified in template_data")
            return None

        bg_path = WALLPAPER_DIR / "image" / bg_filename

        if not bg_path.exists():
            _printer.error(f"Background file missing: {bg_path}")
            return None

        # ─── Get modulation settings (with defaults) ───
        mod = template_data.get("modulation", {})
        vivid = mod.get("vivid", True)
        strength = mod.get("strength", 1.0)
        bright_min = mod.get("brightness_min", 100)
        bright_factor = mod.get("brightness_factor", 80/255)
        sat_min = mod.get("saturation_min", 100)
        sat_factor = mod.get("saturation_factor", 200/255)
        sig_contrast = mod.get("sigmoidal_contrast", "3,50%")

        # ─── Analyze image for brightness/saturation ───
        with Image.open(bg_path).convert("HSV") as img:
            stat = ImageStat.Stat(img)
            s_mean, v_mean = stat.mean[1], stat.mean[2]

            base_val = 150 - (v_mean * bright_factor * 255 / 150)
            base_sat = 300 - (s_mean * sat_factor * 255 / 150)

            val_b = int(max(bright_min, bright_min + (base_val - bright_min) * strength))
            sat_b = int(max(sat_min, sat_min + (base_sat - sat_min) * strength))

        # ─── Get original background hue ───
        with Image.open(bg_path).convert("RGB") as img:
            img.thumbnail((50, 50))
            pixels = list(img.getdata())
            avg_r = sum(p[0] for p in pixels) // len(pixels)
            avg_g = sum(p[1] for p in pixels) // len(pixels)
            avg_b = sum(p[2] for p in pixels) // len(pixels)
            h_avg, l_avg, s_avg = colorsys.rgb_to_hls(avg_r/255, avg_g/255, avg_b/255)
            original_bg_hue = int(h_avg * 360)

        _printer.debug(f"Background: {bg_filename} | Original hue: {original_bg_hue}° | Strength: {strength} | Sample: {len(pixels)} pixels")

        # ─── Calculate target hue ───
        clean = hex_color.lstrip('#')
        r, g, b = int(clean[0:2], 16), int(clean[2:4], 16), int(clean[4:6], 16)
        h, l, s = colorsys.rgb_to_hls(r/255, g/255, b/255)
        target_hue_deg = int(h * 360)

        # ─── Modulate the image ───
        hue_delta = (target_hue_deg - original_bg_hue) % 360
        im_hue = 100 + (hue_delta * 100 / 180)

        temp_bg = "/dev/shm/image_bg.png"

        convert_cmd = [
            "convert", str(bg_path),
            "-modulate", f"{val_b},{sat_b},{im_hue:.2f}"
        ]

        if vivid and strength > 0:
            convert_cmd.extend(["-sigmoidal-contrast", sig_contrast])
            _printer.debug(f"Vivid: ON (strength: {strength}, contrast: {sig_contrast})")
        else:
            if strength == 0:
                _printer.debug(f"Vivid: OFF (strength is 0, pure hue mode)")
            else:
                _printer.debug(f"Vivid: OFF")

        convert_cmd.append(temp_bg)

        subprocess.run(convert_cmd, check=True)

        return temp_bg

    # ─── SVG BACKGROUND ───
    elif template_type == "svg_bg":
        svg_content = template_data["svg"]
        original_hue = template_data.get("original_hue", 334)
        svg_content = shift_svg_hue(svg_content, hex_color, original_hue)

        temp_svg_path = "/dev/shm/temp_svg_bg.svg"
        temp_bg = "/dev/shm/svg_bg.png"

        with open(temp_svg_path, 'w') as f:
            f.write(svg_content)

        subprocess.run([
            "rsvg-convert",
            "-w", "1920",
            "-h", "1080",
            temp_svg_path,
            "-o", temp_bg
        ], check=True)

        os.remove(temp_svg_path)
        return temp_bg

    else:
        _printer.error(f"Unknown template type: {template_type}")
        return None


# =============================================================================
# WALLPAPER GENERATION
# =============================================================================

def generate_wallpaper(template_id: str, hex_color: str, output_path: Path) -> bool:
    """
    Generate one wallpaper PNG.

    Pure function — no Qt, no thread, no GUI. Callable from:
      - Wini's GUI worker (PresetCreatorWorker)
      - Wini's CLI mode (run_cli)
      - Any other tool that needs a composed wallpaper

    Args:
        template_id: key in WALLPAPER_SVG_TEMPLATES (e.g. "awp-center",
                     "awp-firma-cave")
        hex_color:   the wallpaper's target color (e.g. "#b7004f")
        output_path: where to write the PNG (Path or str)

    Returns:
        True on success, False on failure.
    """
    try:
        template_data = WALLPAPER_SVG_TEMPLATES.get(template_id)
        if not template_data:
            template_data = WALLPAPER_SVG_TEMPLATES[DEFAULT_WALLPAPER_TEMPLATE]

        # Get target info
        clean_hex = hex_color.lstrip('#')
        r, g, b = int(clean_hex[0:2], 16), int(clean_hex[2:4], 16), int(clean_hex[4:6], 16)
        h, l, s = colorsys.rgb_to_hls(r/255, g/255, b/255)
        target_hue_deg = int(h * 360)

        template_type = template_data.get("type", "image_bg")

        # ============================================================
        # NO-LOGO BACKGROUND (already fully composed, no overlay)
        # ============================================================
        if template_data.get("no_logo"):

            if template_type == "image_bg":
                temp_bg = generate_background(hex_color, template_data)
                if not temp_bg or not os.path.exists(temp_bg):
                    _printer.error("Failed to generate background for no_logo image_bg")
                    return False

                output_path.parent.mkdir(parents=True, exist_ok=True)

                filename_prefix = template_data.get("filename_prefix", "awp-center")
                filename = f"{filename_prefix}-{target_hue_deg:03d}-{clean_hex}.png"
                output_png = output_path.parent / filename

                shutil.copy2(temp_bg, output_png)
                os.remove(temp_bg)

                return output_png.exists()

            # No-logo SVG: hue-shift and rasterize directly.
            svg_content = shift_svg_hue(template_data["svg"], hex_color, template_data.get("original_hue"))

            temp_dir = Path("/dev/shm") / f"awp_wallpaper_{os.getpid()}"
            temp_dir.mkdir(parents=True, exist_ok=True)

            temp_svg = temp_dir / "temp_wallpaper.svg"
            with open(temp_svg, 'w') as f:
                f.write(svg_content)

            output_path.parent.mkdir(parents=True, exist_ok=True)

            if shutil.which("rsvg-convert"):
                temp_png = temp_dir / "temp_wallpaper.png"
                subprocess.run([
                    "rsvg-convert",
                    "-w", "1920",
                    "-h", "1080",
                    "-o", str(temp_png),
                    str(temp_svg)
                ], check=True, capture_output=True)

                filename_prefix = template_data.get("filename_prefix", "awp-center")
                filename = f"{filename_prefix}-{target_hue_deg:03d}-{clean_hex}.png"
                output_png = output_path.parent / filename

                shutil.copy2(temp_png, output_png)

                temp_svg.unlink(missing_ok=True)
                temp_png.unlink(missing_ok=True)
                temp_dir.rmdir()

                return output_png.exists()
            else:
                _printer.warning("rsvg-convert not found - cannot render no-logo SVG")
                return False

        # ============================================================
        # BACKGROUND + LOGO OVERLAY (image_bg or svg_bg)
        # ============================================================
        elif template_type in ["image_bg", "svg_bg"]:

            temp_bg = generate_background(hex_color, template_data)
            if not temp_bg or not os.path.exists(temp_bg):
                _printer.error(f"Failed to generate background for {template_type}")
                return False

            logo_template_name = template_data.get("logo_template", "awp-firma")
            logo_svg = SVG_TEMPLATES.get(logo_template_name)

            if not logo_svg:
                _printer.error(f"Logo template not found: {logo_template_name}")
                return False

            whiteness_factor = template_data.get("whiteness_factor", 0.0)

            if whiteness_factor > 0:
                logo_hex = get_logo_color(hex_color, whiteness_factor)
                _printer.debug(f"Target: {hex_color} → Logo: {logo_hex} (whiteness: {whiteness_factor})")
            else:
                logo_hex = hex_color
                _printer.debug(f"Target: {hex_color} → Logo: {logo_hex} (no whiteness)")

            logo_svg_content = logo_svg.replace('{{COLOR}}', logo_hex)

            temp_logo_svg = "/dev/shm/temp_logo.svg"
            with open(temp_logo_svg, 'w') as f:
                f.write(logo_svg_content)

            logo_size = template_data.get("logo_size", 90)
            temp_logo = "/dev/shm/temp_logo.png"

            subprocess.run([
                "rsvg-convert",
                "-w", str(logo_size),
                "-h", str(logo_size),
                temp_logo_svg,
                "-o", temp_logo
            ], check=True)

            os.remove(temp_logo_svg)

            logo_x = template_data.get("logo_x", 15)
            logo_y = template_data.get("logo_y", 5)
            filename_prefix = template_data.get("filename_prefix", "awp-firma")

            output_png = output_path.parent / f"{filename_prefix}-{target_hue_deg:03d}-{clean_hex}.png"

            subprocess.run([
                "composite",
                "-gravity", "SouthWest",
                "-geometry", f"+{logo_x}+{logo_y}",
                temp_logo,
                temp_bg,
                str(output_png)
            ], check=True)

            os.remove(temp_bg)
            os.remove(temp_logo)

            return output_png.exists()

        else:
            _printer.error(f"Unknown template type: {template_type}")
            return False

    except Exception as e:
        _printer.error(f"generate_wallpaper failed: {e}")
        return False
