"""
AWP Core Configuration Manager
Centralizes all configuration logic for daemon, nav, dab, and setup modules.
Handles loading, validation, caching, and workspace-specific configuration.
"""
import configparser
import os
from pathlib import Path
from typing import Any, Dict, Optional, Tuple
from core.constants import CONFIG_PATH, AWP_DIR

class ConfigError(Exception):
    """Raised when configuration is invalid or missing required sections."""
    pass

class AWPConfig:
    """
    Main configuration manager for AWP.
    Provides safe access to config values with caching and validation.
    """
    
    def __init__(self, config_path: str = CONFIG_PATH):
        self.path = Path(config_path)
        self.config = configparser.ConfigParser()
        self._workspace_cache = {}
        self._global_cache = {}
        self._loaded = False
        self._load()

    def _load(self):
        """Load configuration file with basic validation."""
        if not self.path.exists():
            raise ConfigError(f"Configuration file not found: {self.path}")
        
        self.config.read(self.path)
        self._validate_required_sections()
        self._loaded = True

    def _validate_required_sections(self):
        """Validate required sections exist based on workspaces count."""
        required = ['general']
        try:
            n_ws = self.getint('general', 'workspaces', fallback=4)
            for i in range(1, n_ws + 1):
                required.append(f'ws{i}')
        except:
            pass  # Will be caught by getint validation
        
        missing = [sec for sec in required if sec not in self.config]
        if missing:
            raise ConfigError(f"Missing required sections: {missing}")

    # === CORE ACCESSORS (Thread-safe with caching) ===
    
    def get(self, section: str, key: str, default: Any = None) -> str:
        """Get string value with fallback."""
        try:
            return self.config.get(section, key, fallback=str(default) if default is not None else '')
        except configparser.NoSectionError:
            return str(default) if default is not None else ''

    def getint(self, section: str, key: str, default: int = 0) -> int:
        """Get integer value with fallback."""
        try:
            return self.config.getint(section, key, fallback=default)
        except (configparser.NoSectionError, ValueError):
            return default

    def getbool(self, section: str, key: str, default: bool = False) -> bool:
        """Get boolean value with fallback."""
        try:
            return self.config.getboolean(section, key, fallback=default)
        except (configparser.NoSectionError, ValueError):
            return default

    def getlist(self, section: str, key: str, sep: str = ',', default: list = None) -> list:
        """Get list value split by separator."""
        if default is None:
            default = []
        val = self.get(section, key, "")
        return [x.strip() for x in val.split(sep) if x.strip()] or default

    # === GLOBAL SETTINGS (Replace daemon globals) ===
    
    @property
    def de(self) -> str:
        """The .ini is the master. Validation is done by checking the filesystem."""
        de = self._global_cache.get('de')
        if de is None:
            # 1. Trust the .ini file first
            de = self.get('general', 'os_detected', 'unknown').lower()
            
            # 2. Check the filesystem: Does backends/{de}.py exist?
            # We use AWP_DIR from constants to build the path
            backend_file = Path(AWP_DIR) / "backends" / f"{de}.py"
            
            if not backend_file.exists():
                # 3. If .ini is wrong/unknown, fallback to env detection
                env_de = os.environ.get("XDG_CURRENT_DESKTOP", "").lower()
                
                # Dynamic check: Does any .py file in backends/ match our environment?
                # We'll default to generic if we can't find a file match
                de = "generic" 
                for backend_file in (Path(AWP_DIR) / "backends").glob("*.py"):
                    name = backend_file.stem
                    if name != "__init__" and name in env_de:
                        de = name
                        break
                        
            self._global_cache['de'] = de
        return de

    @property
    def session_type(self) -> str:
        """X11 or Wayland session type."""
        if 'session_type' not in self._global_cache:
            self._global_cache['session_type'] = self.get('general', 'session_type', 'x11')
        return self._global_cache['session_type']

    @property
    def workspaces_count(self) -> int:
        """Number of configured workspaces."""
        if 'workspaces_count' not in self._global_cache:
            self._global_cache['workspaces_count'] = self.getint('general', 'workspaces', 4)
        return self._global_cache['workspaces_count']

    @property
    def blanking_pause(self) -> bool:
        """Screen blanking paused."""
        return self.getbool('general', 'blanking_pause', False)

    @property
    def blanking_timeout(self) -> int:
        """Screen blanking timeout in seconds."""
        timeout_str = self.get('general', 'blanking_timeout', '0')
        return int(timeout_str) if timeout_str.isdigit() else 0

    @property
    def blanking_formatted(self) -> str:
        """Formatted blanking timeout for display."""
        if self.blanking_pause or self.blanking_timeout == 0:
            return "off"
        
        timeout_sec = self.blanking_timeout
        if timeout_sec < 60:
            return f"{timeout_sec}s"
        elif timeout_sec < 3600:
            return f"{timeout_sec//60}m"
        else:
            hours = timeout_sec // 3600
            minutes = (timeout_sec % 3600) // 60
            return f"{hours}h{minutes}m" if minutes > 0 else f"{hours}h"

    # === WORKSPACE HELPERS (Replaces Workspace config reloading) ===
    
    def get_workspace_config(self, ws_num: int) -> Dict[str, Any]:
        """Get complete configuration for a workspace."""
        ws_key = f"ws{ws_num + 1}"
        cache_key = f"ws_{ws_key}"
        
        if cache_key not in self._workspace_cache:
            self._workspace_cache[cache_key] = {
                'folder': self.get(ws_key, 'folder', ''),
                'timing': self.get(ws_key, 'timing', '1m'),
                'mode': self.get(ws_key, 'mode', 'random'),
                'order': self.get(ws_key, 'order', 'name_az'),
                'scaling': self.get(ws_key, 'scaling', 'scaled'),
                'icon': self.get(ws_key, 'icon', ''),
                'icon_color': self.get(ws_key, 'icon_color', '#109daf'),
                'icon_theme': self.get(ws_key, 'icon_theme', ''),
                'gtk_theme': self.get(ws_key, 'gtk_theme', ''),
                'cursor_theme': self.get(ws_key, 'cursor_theme', ''),
                'desktop_theme': self.get(ws_key, 'desktop_theme', ''),
                'wm_theme': self.get(ws_key, 'wm_theme', ''),
            }
        return self._workspace_cache[cache_key]

    def invalidate_workspace_cache(self, ws_num: int = None):
        """Clear workspace cache (call after config changes)."""
        if ws_num is not None:
            cache_key = f"ws_ws{ws_num + 1}"
            self._workspace_cache.pop(cache_key, None)
        else:
            self._workspace_cache.clear()

    # === RUN TIME GENERATOR ===
    
    def generate_runtime_state(self, workspace_name: str, wallpaper_path: str) -> Dict[str, str]:
        """Generate runtime state dictionary for current state."""
        ws_num = int(workspace_name.replace('ws', '')) - 1
        ws_config = self.get_workspace_config(ws_num)
        
        return {
            'wallpaper_path': wallpaper_path,
            'workspace_name': workspace_name,
            'logo_path': ws_config['icon'],
            'icon_color': ws_config['icon_color'],
            'intv': ws_config['timing'],
            'flow': ws_config['mode'],
            'sort': ws_config['order'],
            'view': ws_config['scaling'],
            'blanking_timeout': self.blanking_formatted,
            'blanking_paused': str(self.blanking_pause),
        }

    # === MUTATORS (For dashboards and runtime updates) ===
    
    def set(self, section: str, key: str, value: Any):
        """Set configuration value and save."""
        self.config.set(section, key, str(value))
        self._invalidate_caches()
        self.save()

    def save(self):
        """Save configuration with atomic backup."""
        if not self._loaded:
            return
            
        backup_path = self.path.with_suffix('.bak')
        if self.path.exists():
            self.path.rename(backup_path)
        
        try:
            with open(self.path, 'w') as f:
                self.config.write(f)
        except Exception as e:
            # Restore backup on failure
            if backup_path.exists():
                backup_path.rename(self.path)
            raise ConfigError(f"Failed to save config: {e}")

    def reload(self):
        """Reload configuration from disk and clear caches."""
        self._loaded = False
        self._global_cache.clear()
        self._workspace_cache.clear()
        self._load()

    def _invalidate_caches(self):
        """Clear all caches after mutation."""
        self._global_cache.clear()
        self._workspace_cache.clear()

    # === UTILITY ===
    
    def as_dict(self) -> Dict[str, Dict[str, str]]:
        """Return full configuration as dictionary (for dashboards)."""
        result = {}
        for section in self.config.sections():
            result[section] = dict(self.config[section])
        return result

    def validate(self) -> list:
        """Validate configuration and return warnings."""
        warnings = []
        
        # Check workspace folders exist
        n_ws = self.workspaces_count
        for i in range(n_ws):
            ws_config = self.get_workspace_config(i)
            if not Path(ws_config['folder']).exists():
                warnings.append(f"Workspace ws{i+1}: folder not found - {ws_config['folder']}")
        
        return warnings

    @classmethod
    def create_default(cls, config_path: str) -> 'AWPConfig':
        """Create default configuration file (for awp_setup.py)."""
        config = cls(config_path)  # Will fail if exists
        # Implementation for setup would go here
        raise NotImplementedError("Use awp_setup.py for initial config creation")
