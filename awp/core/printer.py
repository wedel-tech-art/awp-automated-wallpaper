#!/usr/bin/env python3
"""
Unified Printing Manager for AWP
All formatted output goes through here
"""

from core.constants import (
    CLR_RED, CLR_GREEN, CLR_YELLOW, CLR_BLUE, CLR_MAGENTA,
    CLR_CYAN, CLR_WHITE, CLR_RESET, CLR_BOLD
)

class AWPPrinter:
    """Centralized printer for all AWP output"""
    
    def __init__(self):
        self.backend = None
        self.verbose = True
        
        # Color mapping for different modules
        self.module_colors = {
            "backends": CLR_YELLOW,
            "daemon": CLR_CYAN,
            "xfce": CLR_GREEN,
            "qtile_xfce": CLR_GREEN,
            "gnome": CLR_BLUE,
            "cinnamon": CLR_MAGENTA,
            "mate": CLR_BLUE,
            "generic": CLR_WHITE,
            "openbox_xfce": CLR_GREEN,
            "utils": CLR_BLUE,
            "core": CLR_YELLOW,
        }
    
    def set_backend(self, backend_name):
        """Manually set current backend for context"""
        self.backend = backend_name
        return self
    
    def set_verbose(self, verbose):
        """Set verbose mode"""
        self.verbose = verbose
    
    def _get_color(self, module):
        """Get color for a module, default to cyan"""
        return self.module_colors.get(module, CLR_CYAN)
    
    def _prefix(self, backend_override=None):
        """Generate prefix with color-coded module context"""
        # Determine which module is printing
        module = backend_override or self.backend or "AWP"
        
        # Get color for this module
        color = self._get_color(module)
             
        return f"{color}[AWP-{module}]{CLR_RESET}"
    
    # ===== CORE PRINT METHODS =====
    def themes(self, ws_num, changes, backend=None):
        """Print theme changes message"""
        if changes:
            print(f"{self._prefix(backend or self.backend)} WS{ws_num + 1} themes: {CLR_GREEN}{', '.join(changes)}{CLR_RESET}")
    
    def wallpaper(self, ws_num, image_name, backend=None):
        """Print wallpaper change message"""
        print(f"{self._prefix(backend or self.backend)} Workspace {ws_num + 1} -> {CLR_GREEN}{CLR_BOLD}{image_name}{CLR_RESET}")
    
    def icon(self, icon_name, backend=None):
        """Print icon change message"""
        print(f"{self._prefix(backend or self.backend)} {CLR_GREEN}✓{CLR_RESET} Icon refreshed: {CLR_CYAN}{icon_name}{CLR_RESET}")
    
    def lean_mode(self, status="Activated", backend=None):
        """Print lean mode message"""
        print(f"{self._prefix(backend or self.backend)} {CLR_YELLOW}Lean Mode {status}{CLR_RESET}")
    
    def error(self, message, backend=None):
        """Print error message"""
        print(f"{CLR_RED}{self._prefix(backend or self.backend)} Error: {message}{CLR_RESET}")
    
    def warning(self, message, backend=None):
        """Print warning message"""
        print(f"{CLR_YELLOW}{self._prefix(backend or self.backend)} {message}{CLR_RESET}")
    
    def info(self, message, backend=None):
        """Print info message"""
        print(f"{self._prefix(backend or self.backend)} {message}")
    
    def debug(self, message, backend=None):
        """Print debug message if verbose"""
        if self.verbose:
            print(f"{CLR_CYAN}{self._prefix(backend or self.backend)} [DEBUG] {message}{CLR_RESET}")
    
    def success(self, message, backend=None):
        """Print success message (with checkmark)"""
        print(f"{CLR_GREEN}{self._prefix(backend or self.backend)} ✓ {message}{CLR_RESET}")

# Global printer instance
_printer = AWPPrinter()

def get_printer():
    """Get the global printer instance"""
    return _printer
