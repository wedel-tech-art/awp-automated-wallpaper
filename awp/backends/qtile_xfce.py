#!/usr/bin/env python3
"""
Qtile + XFCE Backend for AWP
For Qtile window manager with XFCE theming support.
Uses feh for wallpapers (always lean), xfsettingsd for theming.
"""

import os
import subprocess

# ANSI Color Codes
CLR_RED    = "\033[91m"
CLR_GREEN  = "\033[92m"
CLR_YELLOW = "\033[93m"
CLR_CYAN   = "\033[96m"
CLR_RESET  = "\033[0m"
CLR_BOLD   = "\033[1m"

def qtile_xfce_lean_mode():
    """
    Qtile is lean by default, but kill xfdesktop if present.
    
    This ensures no xfdesktop processes interfere with Qtile.
    Called when AWP starts with lean_mode = true.
    """
    # Kill any running xfdesktop (common if switching from XFCE)
    subprocess.run(["pkill", "-f", "xfdesktop"], 
                   stderr=subprocess.DEVNULL,
                   stdout=subprocess.DEVNULL,
                   check=False)
    
    # Prevent xfce4-session from restarting xfdesktop
    subprocess.run([
        "xfconf-query", "-c", "xfce4-session",
        "-p", "/sessions/Failsafe/Client3_Command",
        "-t", "string", "-s", "true", "--create"
    ], stderr=subprocess.DEVNULL, check=False)
    
    print(f"{CLR_CYAN}[AWP-Qtile]{CLR_RESET} {CLR_GREEN}Lean mode active{CLR_RESET}")
    print(f"{CLR_CYAN}[AWP-Qtile]{CLR_RESET} Using feh for wallpapers")

def qtile_xfce_force_single_workspace_off():
    """
    No-op for Qtile - Qtile handles workspaces differently than XFCE.
    
    Required for API compatibility but does nothing.
    """
    pass

def qtile_xfce_set_wallpaper(ws_num: int, image_path: str, scaling: str):
    """
    Set wallpaper using feh (Qtile-compatible).
    
    Args:
        ws_num (int): Workspace number (0-indexed)
        image_path (str): Full path to wallpaper image
        scaling (str): 'centered', 'scaled', or 'zoomed'
    
    Note: Qtile doesn't support per-workspace wallpapers natively,
    so this sets wallpaper globally.
    """
    scaling_map = {
        'centered': '--bg-center',
        'scaled': '--bg-scale', 
        'zoomed': '--bg-fill'
    }
    
    style_flag = scaling_map.get(scaling, '--bg-fill')
    wp_name = os.path.basename(image_path)
    
    try:
        # Set wallpaper globally
        result = subprocess.run(
            ["feh", style_flag, image_path],
            capture_output=True,
            text=True,
            check=True
        )
        
        print(f"{CLR_CYAN}[AWP-Qtile]{CLR_RESET} Workspace {ws_num + 1} → "
              f"{CLR_GREEN}{CLR_BOLD}{wp_name}{CLR_RESET}")
        
    except subprocess.CalledProcessError as e:
        print(f"{CLR_RED}[AWP-Qtile] feh failed: {e.stderr}{CLR_RESET}")
    except FileNotFoundError:
        print(f"{CLR_RED}[AWP-Qtile] feh not installed!{CLR_RESET}")
        print(f"{CLR_YELLOW}Install: sudo apt install feh{CLR_RESET}")
    except Exception as e:
        print(f"{CLR_RED}[AWP-Qtile] Error: {e}{CLR_RESET}")

def qtile_xfce_set_icon(icon_path: str):
    """
    Set panel icon - supports various panels that might be used with Qtile.
    
    Args:
        icon_path (str): Full path to icon file
    
    Tries in order:
    1. xfce4-panel (if running in hybrid setup)
    2. tint2 (common with Qtile)
    3. Qtile bar (no icon support, shows note)
    """
    icon_name = os.path.basename(icon_path)
    
    # Try xfce4-panel first (if running hybrid Qtile+XFCE panel)
    if subprocess.run(["pgrep", "xfce4-panel"], 
                     capture_output=True).returncode == 0:
        try:
            subprocess.run([
                "xfconf-query", "-c", "xfce4-panel",
                "-p", "/plugins/plugin-1/button-icon",
                "-s", icon_path, "--create", "-t", "string"
            ], check=True)
            print(f"{CLR_GREEN}✓{CLR_RESET} XFCE Panel icon: {CLR_CYAN}{icon_name}{CLR_RESET}")
            return
        except subprocess.CalledProcessError:
            pass  # Try next option
    
    # Try tint2 (popular with Qtile)
    tint2_conf = os.path.expanduser("~/.config/tint2/tint2rc")
    if os.path.exists(tint2_conf):
        try:
            # Update launcher icon in tint2 config
            subprocess.run([
                "sed", "-i",
                f"s|^launcher_item_app = .*|launcher_item_app = {icon_path}|",
                tint2_conf
            ], check=True)
            
            # Reload tint2
            subprocess.run(["pkill", "-SIGUSR1", "tint2"], 
                         stderr=subprocess.DEVNULL,
                         stdout=subprocess.DEVNULL,
                         check=False)
            
            print(f"{CLR_GREEN}✓{CLR_RESET} tint2 icon: {CLR_CYAN}{icon_name}{CLR_RESET}")
            return
        except (subprocess.CalledProcessError, FileNotFoundError):
            pass
    
    # Qtile bar doesn't support menu icons natively
    print(f"{CLR_YELLOW}[AWP-Qtile] Note: No panel found for icons{CLR_RESET}")
    print(f"{CLR_YELLOW}  Qtile bar doesn't support menu icons{CLR_RESET}")
    print(f"{CLR_YELLOW}  Consider using tint2 or xfce4-panel with Qtile{CLR_RESET}")

def qtile_xfce_set_themes(ws_num: int, config):
    """
    Apply GTK themes via xfsettingsd (requires xfsettingsd running).
    
    Args:
        ws_num (int): Workspace number (0-indexed)
        config: ConfigParser object with theme settings
    
    Note: Qtile window decorations use its own config,
    but GTK apps will use the XFCE theme.
    """
    section = f"ws{ws_num + 1}"
    if not config.has_section(section):
        return
    
    # Extract theme settings
    gtk_theme = config.get(section, 'gtk_theme', fallback=None)
    icon_theme = config.get(section, 'icon_theme', fallback=None)
    cursor_theme = config.get(section, 'cursor_theme', fallback=None)
    
    applied = []
    errors = []
    
    # Apply via xfconf-query (requires xfsettingsd daemon)
    if gtk_theme:
        try:
            subprocess.run([
                "xfconf-query", "-c", "xsettings",
                "-p", "/Net/ThemeName",
                "-s", gtk_theme, "--create"
            ], stderr=subprocess.DEVNULL, check=True)
            applied.append(f"GTK: {gtk_theme}")
        except (subprocess.CalledProcessError, FileNotFoundError):
            errors.append(f"GTK theme failed (is xfsettingsd running?)")
    
    if icon_theme:
        try:
            subprocess.run([
                "xfconf-query", "-c", "xsettings",
                "-p", "/Net/IconThemeName",
                "-s", icon_theme, "--create"
            ], stderr=subprocess.DEVNULL, check=True)
            applied.append(f"Icons: {icon_theme}")
        except (subprocess.CalledProcessError, FileNotFoundError):
            errors.append(f"Icon theme failed")
    
    if cursor_theme:
        try:
            subprocess.run([
                "xfconf-query", "-c", "xsettings",
                "-p", "/Gtk/CursorThemeName",
                "-s", cursor_theme, "--create"
            ], stderr=subprocess.DEVNULL, check=True)
            applied.append(f"Cursor: {cursor_theme}")
        except (subprocess.CalledProcessError, FileNotFoundError):
            errors.append(f"Cursor theme failed")
    
    # Results
    if applied:
        themes_str = ", ".join(applied)
        print(f"{CLR_CYAN}[AWP-Qtile]{CLR_RESET} Themes for WS{ws_num + 1}: {themes_str}")
    
    if errors:
        print(f"{CLR_YELLOW}[AWP-Qtile] Some themes failed:{CLR_RESET}")
        for error in errors:
            print(f"  {CLR_YELLOW}• {error}{CLR_RESET}")
        print(f"{CLR_YELLOW}  Ensure xfsettingsd is running: xfsettingsd --daemon{CLR_RESET}")
    
    if not applied and not errors:
        print(f"{CLR_YELLOW}[AWP-Qtile] No themes configured for WS{ws_num + 1}{CLR_RESET}")

def qtile_xfce_wallpaper_native(ws_num: int, image_path: str, scaling: str):
    """
    Native wallpaper setting - not applicable for Qtile.
    
    Qtile doesn't have a native wallpaper setter, so this falls back to feh.
    Exists for API compatibility if AWP tries to use native methods.
    
    Args:
        ws_num (int): Workspace number
        image_path (str): Wallpaper image path
        scaling (str): Scaling mode
    """
    print(f"{CLR_YELLOW}[AWP-Qtile] Qtile has no native wallpaper method{CLR_RESET}")
    print(f"{CLR_YELLOW}  Using feh instead{CLR_RESET}")
    qtile_xfce_set_wallpaper(ws_num, image_path, scaling)
