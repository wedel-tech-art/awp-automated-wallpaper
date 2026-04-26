#!/usr/bin/env python3
"""
AWP Backends Package
Lean Mode = use feh instead of native desktop wallpaper setter.
"""
import os
import sys
import importlib
import configparser
from pathlib import Path
from core.printer import get_printer
from core.constants import (
    QT6_ACCENT_SHM,
    QT6CT_CONF_PATH,
    QT6CT_COLORS_DIR,
    KDE_COLORS_DIR,
    KDE_ACCENT_SHM
)

# Get printer instance
_printer = get_printer()
_printer.set_backend("backends")

# ============================================================================
# SHARED BACKEND UTILITIES (Qt6/KDE theming)
# These are identical across all X11 backends
# ============================================================================

def ensure_qt6_kde_symlinks():
    """Ensure symlinks exist for Qt6 and KDE theming (shared across all backends)."""
    
    target_qt_link = os.path.join(QT6CT_COLORS_DIR, "awp.conf")
    target_kde_link = os.path.join(KDE_COLORS_DIR, "AWP_Dynamic.colors")
    
    os.makedirs(QT6CT_COLORS_DIR, exist_ok=True)
    os.makedirs(KDE_COLORS_DIR, exist_ok=True)
    
    # Qt6 symlink
    if not (os.path.islink(target_qt_link) and os.readlink(target_qt_link) == QT6_ACCENT_SHM):
        if os.path.exists(target_qt_link) or os.path.islink(target_qt_link):
            os.remove(target_qt_link)
        os.symlink(QT6_ACCENT_SHM, target_qt_link)
    
    # KDE symlink
    if not (os.path.islink(target_kde_link) and os.readlink(target_kde_link) == KDE_ACCENT_SHM):
        if os.path.exists(target_kde_link) or os.path.islink(target_kde_link):
            os.remove(target_kde_link)
        os.symlink(KDE_ACCENT_SHM, target_kde_link)
    
    # Update qt6ct.conf
    if os.path.exists(QT6CT_CONF_PATH):
        cfg = configparser.ConfigParser()
        cfg.read(QT6CT_CONF_PATH)
        if not cfg.has_section('Appearance'):
            cfg.add_section('Appearance')
        if cfg.get('Appearance', 'color_scheme_path', fallback='') != target_qt_link:
            cfg.set('Appearance', 'color_scheme_path', target_qt_link)
            with open(QT6CT_CONF_PATH, 'w') as f:
                cfg.write(f)
    
    _printer.info("Qt6 & KDE symlinks verified", backend="common")

def write_qt6_kde_accent(accent_color: str):
    """Write Qt6 and KDE accent colors to RAM (shared across all backends)."""
    ensure_qt6_kde_symlinks()
    
    accent_raw = accent_color.lstrip('#').lower()
    
    # Qt6 format
    qt_content = f'''[ColorScheme]
active_colors=#ffffff, #ff2e2e2e, #ff4e4e4e, #ff3a3a3a, #ff1a1a1a, #ff2a2a2a, #ffffffff, #ffffffff, #ffffffff, #ff242424, #ff2e2e2e, #ffffffff, #{accent_raw}, #ffffffff, #ffff6a00, #ffa70b06, #ff2e2e2e, #ffffffff, #ff3f3f36, #ffffffff, #80ffffff, #{accent_raw}
inactive_colors=#ffffffff, #ff2e2e2e, #ff4e4e4e, #ff3a3a3a, #ff1a1a1a, #ff2a2a2a, #ffffffff, #ffffffff, #ffffffff, #ff242424, #ff2e2e2e, #ffffffff, #{accent_raw}, #ffffffff, #ffff6a00, #ffa70b06, #ff2e2e2e, #ffffffff, #ff3f3f36, #ffffffff, #80ffffff, #{accent_raw}
disabled_colors=#ff808080, #ff2e2e2e, #ff4e4e4e, #ff3a3a3a, #ff1a1a1a, #ff2a2a2a, #ff808080, #ffffffff, #ff808080, #ff242424, #ff2e2e2e, #ffffffff, #{accent_raw}, #ff808080, #ffff6a00, #ffa70b06, #ff2e2e2e, #ffffffff, #ff3f3f36, #ffffffff, #80ffffff, #{accent_raw}'''
    
    with open(QT6_ACCENT_SHM, 'w') as f:
        f.write(qt_content)
    
    # KDE format
    kde_content = f"""[General]
Name=AWP_Dynamic
ReferenceColorScheme=BreezeDark

[Background:Normal]
Color=#2e2e2e
[Foreground:Normal]
Color=#cfcfc2
[Background:Selection]
Color={accent_color}
[Colors:Selection]
BackgroundNormal={accent_color}
ForegroundNormal=#ffffff
[Colors:Window]
BackgroundNormal=#2e2e2e
ForegroundNormal=#cfcfc2
[Colors:View]
BackgroundNormal=#242424
ForegroundNormal=#cfcfc2
[Colors:Button]
BackgroundNormal=#3a3a3a
ForegroundNormal=#cfcfc2
"""
    
    with open(KDE_ACCENT_SHM, 'w') as f:
        f.write(kde_content)
    
    _printer.info(f"Qt6 & KDE accents synced in RAM: {accent_color}", backend="common")


# ============================================================================
# BACKEND CONFIGURATION
# ============================================================================
# Get the directory where this __init__.py sits
_backend_dir = Path(__file__).parent

# Automatically find all .py files except __init__.py
BACKEND_NAMES = [f.stem for f in _backend_dir.glob("*.py") if f.stem != "__init__"]

BACKENDS = {}

_printer.info("Loading backends...")

for name in BACKEND_NAMES:
    try:
        module = importlib.import_module(f".{name}", "backends")
        prefix = name
        
        # REQUIRED: wallpaper (could be feh or native depending on backend)
        funcs = {
            "wallpaper": getattr(module, f"{prefix}_set_wallpaper"),
            "icon": getattr(module, f"{prefix}_set_icon"),
            "themes": getattr(module, f"{prefix}_set_themes"),
            "lean_mode": getattr(module, f"{prefix}_lean_mode"),
            "current_ws": getattr(module, f"{prefix}_current_ws"),
        }
        
        # OPTIONAL: native wallpaper method (some backends have both)
        native_func = getattr(module, f"{prefix}_set_wallpaper_native", None)
        if native_func:
            funcs["wallpaper_native"] = native_func
            native_status = " (+native)"
        else:
            native_status = " (feh-only)"
        
        # Store backend
        BACKENDS[name] = funcs
        
        # Status message with more detail using printer
        if name == "xfce":
            _printer.success(f"{name}{native_status} - xfdesktop or feh (dual-mode)")
        elif name in ["generic", "openbox_xfce", "qtile_xfce"]:
            _printer.success(f"{name}{native_status} - feh only")
        elif name in ["cinnamon", "gnome", "mate"]:
            _printer.success(f"{name}{native_status} - native only")
        else:
            _printer.success(f"{name}{native_status}")
        
    except AttributeError as e:
        _printer.error(f"{name} (missing function: {e})")
        BACKENDS[name] = None
    except ModuleNotFoundError:
        _printer.error(f"{name} (file not found)")
        BACKENDS[name] = None
    except Exception as e:
        _printer.error(f"{name} (error: {e})")
        BACKENDS[name] = None

# Remove failed backends
BACKENDS = {k: v for k, v in BACKENDS.items() if v is not None}

# ============================================================================
# STATUS & API
# ============================================================================
available = list(BACKENDS.keys())
if not available:
    _printer.error("No backends loaded!")
    sys.exit(1)

# Categorize backends
native_backends = [name for name, funcs in BACKENDS.items() 
                   if "wallpaper_native" in funcs]
feh_only_backends = [name for name in available 
                     if name not in native_backends]

_printer.info(f"Available: {', '.join(available)}")
if native_backends:
    _printer.info(f"Native wallpaper support: {', '.join(native_backends)}")
if feh_only_backends:
    _printer.info(f"Feh-only (always lean): {', '.join(feh_only_backends)}")

# Export
backend_funcs = BACKENDS
def get_backend(name): return BACKENDS.get(name)
def list_backends(): return list(BACKENDS.keys())
