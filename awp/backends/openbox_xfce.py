#!/usr/bin/env python3
"""
Openbox + XFCE Hybrid Backend for AWP
For Openbox window manager with XFCE theming components.
Uses feh for wallpapers, xfsettingsd for theming, Openbox for WM.
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

def openbox_xfce_lean_mode():
    """
    Kills xfdesktop and prevents XFCE from restarting it.
    Similar to xfce_lean_mode() but for Openbox environment.
    """
    try:
        # 1. Stop XFCE session manager from restarting xfdesktop
        subprocess.run([
            "xfconf-query", "-c", "xfce4-session", 
            "-p", "/sessions/Failsafe/Client3_Command", 
            "-t", "string", "-s", "true", "--create"
        ], stderr=subprocess.DEVNULL)
        
        # 2. Gracefully kill current xfdesktop
        subprocess.run(["xfdesktop", "--quit"], stderr=subprocess.DEVNULL)
        
        print(f"{CLR_CYAN}[AWP-Openbox+XFCE]{CLR_RESET} {CLR_GREEN}Lean Mode: xfdesktop terminated{CLR_RESET}")
        
    except Exception as e:
        print(f"{CLR_RED}[AWP-Openbox+XFCE] Lean Mode Error: {e}{CLR_RESET}")

def openbox_xfce_force_single_workspace_off():
    """
    Disable single workspace mode in XFCE (if xfdesktop was running).
    Similar to xfce_force_single_workspace_off().
    """
    try:
        subprocess.run([
            "xfconf-query", "-c", "xfce4-desktop",
            "-p", "/backdrop/single-workspace-mode",
            "--set", "false", "--create"
        ], stderr=subprocess.DEVNULL)
    except Exception:
        pass  # Silently fail if not using xfdesktop

def openbox_xfce_set_wallpaper(ws_num: int, image_path: str, scaling: str):
    """
    Set wallpaper using feh (Openbox compatible).
    Similar to xfce_set_wallpaper() but always uses feh.
    """
    scaling_map = {
        'centered': '--bg-center',
        'scaled': '--bg-scale', 
        'zoomed': '--bg-fill'
    }
    
    style_flag = scaling_map.get(scaling, '--bg-fill')
    wp_name = os.path.basename(image_path)
    
    try:
        subprocess.run(["feh", style_flag, image_path], check=True)
        print(f"{CLR_CYAN}[AWP]{CLR_RESET} Workspace {ws_num + 1} → "
              f"{CLR_GREEN}{CLR_BOLD}{wp_name}{CLR_RESET}")
        
    except Exception as e:
        print(f"{CLR_RED}[AWP-Openbox+XFCE] feh failed: {e}{CLR_RESET}")
        # No fallback to native since Openbox doesn't have native wallpaper

def openbox_xfce_set_icon(icon_path: str):
    """
    Smart icon switcher - supports xfce4-panel or tint2.
    Similar to xfce_set_icon() but with tint2 support.
    """
    icon_name = os.path.basename(icon_path)
    
    # Try xfce4-panel first (if running hybrid setup)
    if subprocess.run(["pgrep", "xfce4-panel"], 
                     capture_output=True).returncode == 0:
        try:
            subprocess.run([
                "xfconf-query", "-c", "xfce4-panel",
                "-p", "/plugins/plugin-1/button-icon",
                "-s", icon_path, "--create", "-t", "string"
            ], check=True)
            print(f"{CLR_GREEN}✓{CLR_RESET} XFCE Panel: {CLR_CYAN}{icon_name}{CLR_RESET}")
            return
        except subprocess.CalledProcessError as e:
            print(f"{CLR_YELLOW}[AWP-Openbox+XFCE] XFCE panel icon failed: {e}{CLR_RESET}")
    
    # Try tint2 (common with Openbox)
    tint2_conf = os.path.expanduser("~/.config/tint2/tint2rc")
    if os.path.exists(tint2_conf):
        try:
            # Update launcher icon
            subprocess.run([
                "sed", "-i",
                f"s|^launcher_item_app = .*|launcher_item_app = {icon_path}|",
                tint2_conf
            ], check=True)
            
            # Reload tint2
            subprocess.run(["pkill", "-SIGUSR1", "tint2"], 
                         stderr=subprocess.DEVNULL, check=False)
            
            print(f"{CLR_GREEN}✓{CLR_RESET} tint2: {CLR_CYAN}{icon_name}{CLR_RESET}")
            return
        except (subprocess.CalledProcessError, FileNotFoundError):
            pass
    
    print(f"{CLR_YELLOW}[AWP-Openbox+XFCE] No compatible panel found{CLR_RESET}")

def openbox_xfce_set_themes(ws_num: int, config):
    """
    Apply themes via xfsettingsd + refresh Openbox.
    Similar to xfce_set_themes() but also reloads Openbox.
    """
    section = f"ws{ws_num + 1}"
    if not config.has_section(section): 
        return
    
    gtk_theme = config.get(section, 'gtk_theme', fallback=None)
    icon_theme = config.get(section, 'icon_theme', fallback=None)
    cursor_theme = config.get(section, 'cursor_theme', fallback=None)
    wm_theme = config.get(section, 'wm_theme', fallback=None)
    
    try:
        # Apply GTK themes via xfsettingsd
        if gtk_theme:
            subprocess.run([
                "xfconf-query", "-c", "xsettings",
                "-p", "/Net/ThemeName",
                "-s", gtk_theme, "--create"
            ], stderr=subprocess.DEVNULL, check=False)
        
        if icon_theme:
            subprocess.run([
                "xfconf-query", "-c", "xsettings",
                "-p", "/Net/IconThemeName",
                "-s", icon_theme, "--create"
            ], stderr=subprocess.DEVNULL, check=False)
        
        if cursor_theme:
            subprocess.run([
                "xfconf-query", "-c", "xsettings",
                "-p", "/Gtk/CursorThemeName",
                "-s", cursor_theme, "--create"
            ], stderr=subprocess.DEVNULL, check=False)
        
        # Apply Openbox theme (WM-specific)
        if wm_theme:
            # Openbox themes are in ~/.themes or /usr/share/themes
            # You might need to implement this based on your setup
            print(f"{CLR_YELLOW}[AWP-Openbox+XFCE] WM theme '{wm_theme}' (manual setup){CLR_RESET}")
            print(f"{CLR_YELLOW}  Set in ~/.config/openbox/theme.xml{CLR_RESET}")
        
        # Reload Openbox configuration
        subprocess.run(["openbox", "--reconfigure"], stderr=subprocess.DEVNULL)
        
        print(f"{CLR_CYAN}[AWP]{CLR_RESET} Openbox+XFCE Themes for WS{ws_num + 1}")
        
    except Exception as e:
        print(f"{CLR_RED}[AWP-Openbox+XFCE] Theme error: {e}{CLR_RESET}")

def openbox_xfce_wallpaper_native(ws_num: int, image_path: str, scaling: str):
    """
    Openbox doesn't have native wallpaper - falls back to feh.
    Similar to xfce_set_wallpaper_native() but just uses feh.
    """
    print(f"{CLR_YELLOW}[AWP-Openbox+XFCE] No native wallpaper, using feh{CLR_RESET}")
    openbox_xfce_set_wallpaper(ws_num, image_path, scaling)
