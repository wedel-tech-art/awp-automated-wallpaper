#!/usr/bin/env python3
"""
Unified Printing Manager for AWP
All formatted output goes through here.

Module labels are detected automatically from the calling file — no
set_backend() calls needed, no shared mutable state.

    [AWP-themes] Baking GTK theme for ws3
    [AWP-wallpaper] Target hue computed: 334
    [AWP-daemon] Rotating ws1
    [AWP-backends] Detected: qtile_xfce

The module name is the file stem (e.g. core/themes.py → "themes").
Override per-call with backend="..." if needed.
"""

import inspect
from pathlib import Path

from core.constants import (
    CLR_RED, CLR_GREEN, CLR_YELLOW, CLR_BLUE, CLR_MAGENTA,
    CLR_CYAN, CLR_WHITE, CLR_RESET, CLR_BOLD
)


class AWPPrinter:
    """Centralized printer for all AWP output"""

    def __init__(self):
        self.verbose = True

        # Explicit colors for known modules.
        # Anything not listed here gets a deterministic color from the
        # _FALLBACK_PALETTE, so new modules get a stable color for free.
        self.module_colors = {
            # ── Core infrastructure ──
            "printer":      CLR_WHITE,
            "constants":    CLR_WHITE,
            "runtime":      CLR_BLUE,
            "config":       CLR_BLUE,
            "utils":        CLR_BLUE,
            "actions":      CLR_MAGENTA,

            # ── Rendering / theming ──
            "themes":       CLR_YELLOW,
            "wallpaper":    CLR_GREEN,

            # ── Backends ──
            "backends":     CLR_YELLOW,
            "xfce":         CLR_GREEN,
            "qtile_xfce":   CLR_GREEN,
            "qtile_gnome":  CLR_GREEN,
            "qtile_wayland": CLR_GREEN,
            "gnome":        CLR_BLUE,
            "cinnamon":     CLR_MAGENTA,
            "mate":         CLR_BLUE,
            "generic":      CLR_WHITE,
            "openbox_xfce": CLR_GREEN,

            # ── Daemons ──
            "daemon":           CLR_CYAN,
            "daemon-light":     CLR_CYAN,

            # ── User-facing tools ──
            "wini":         CLR_MAGENTA,
            "baker":        CLR_YELLOW,
            "bath":         CLR_GREEN,
            "dab":          CLR_MAGENTA,
            "nav":          CLR_BLUE,

            # ── HUDs ──
            "hud_preset":   CLR_CYAN,
            "hud_vertical": CLR_CYAN,
            "hud_bottom":   CLR_CYAN,
        }

        # Deterministic fallback palette for unlisted modules.
        # Same module name → same color, forever.
        self._fallback_palette = [
            CLR_RED, CLR_GREEN, CLR_YELLOW, CLR_BLUE,
            CLR_MAGENTA, CLR_CYAN, CLR_WHITE,
        ]

    # ===== INTERNALS =====

    def set_verbose(self, verbose):
        """Set verbose mode"""
        self.verbose = verbose

    def _caller_module(self) -> str:
        """
        Determine which .py file is calling us, skipping printer.py
        and any of its internal helpers.

        For __init__.py, returns the containing directory name so
        backends/__init__.py → "backends", core/__init__.py → "core".
        """
        for frame in inspect.stack()[2:]:
            filename = frame.filename
            if filename.endswith("printer.py"):
                continue
            path = Path(filename)
            if path.stem == "__init__":
                return path.parent.name
            return path.stem
        return "AWP"

    def _get_color(self, module: str) -> str:
        """Get color for a module. Known modules get their curated color;
        unknown modules get a deterministic color from the fallback palette."""
        if module in self.module_colors:
            return self.module_colors[module]
        idx = hash(module) % len(self._fallback_palette)
        return self._fallback_palette[idx]

    def _prefix(self, backend_override: str = None) -> str:
        """Generate prefix with color-coded module context."""
        module = backend_override or self._caller_module()
        color = self._get_color(module)
        return f"{color}[AWP-{module}]{CLR_RESET}"

    # ===== CORE PRINT METHODS =====

    def themes(self, ws_num, changes, backend=None):
        """Print theme changes message"""
        if changes:
            print(f"{self._prefix(backend)} WS{ws_num + 1} themes: "
                  f"{CLR_GREEN}{', '.join(changes)}{CLR_RESET}")

    def wallpaper(self, ws_num, image_name, backend=None):
        """Print wallpaper change message"""
        print(f"{self._prefix(backend)} Workspace {ws_num + 1} -> "
              f"{CLR_GREEN}{CLR_BOLD}{image_name}{CLR_RESET}")

    def icon(self, icon_name, backend=None):
        """Print icon change message"""
        print(f"{self._prefix(backend)} {CLR_GREEN}✓{CLR_RESET} "
              f"Icon refreshed: {CLR_CYAN}{icon_name}{CLR_RESET}")

    def lean_mode(self, status="Activated", backend=None):
        """Print lean mode message"""
        print(f"{self._prefix(backend)} {CLR_YELLOW}Lean Mode {status}{CLR_RESET}")

    def error(self, message, backend=None):
        """Print error message"""
        print(f"{CLR_RED}{self._prefix(backend)} Error: {message}{CLR_RESET}")

    def warning(self, message, backend=None):
        """Print warning message"""
        print(f"{CLR_YELLOW}{self._prefix(backend)} {message}{CLR_RESET}")

    def info(self, message, backend=None):
        """Print info message"""
        print(f"{self._prefix(backend)} {message}")

    def debug(self, message, backend=None):
        """Print debug message if verbose"""
        if self.verbose:
            print(f"{CLR_CYAN}{self._prefix(backend)} [DEBUG] {message}{CLR_RESET}")

    def success(self, message, backend=None):
        """Print success message (with checkmark)"""
        print(f"{CLR_GREEN}{self._prefix(backend)} ✓ {message}{CLR_RESET}")


# Global printer instance
_printer = AWPPrinter()


def get_printer():
    """Get the global printer instance"""
    return _printer
