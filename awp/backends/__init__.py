#!/usr/bin/env python3
"""
AWP Backends Package
Lean Mode = use feh instead of native desktop wallpaper setter.
"""
import sys
import importlib
from pathlib import Path

from core.printer import get_printer

# Get printer instance
_printer = get_printer()
_printer.set_backend("backends")

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
            "workspace_off": getattr(module, f"{prefix}_force_single_workspace_off"),
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

#_printer.set_backend(None)

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
