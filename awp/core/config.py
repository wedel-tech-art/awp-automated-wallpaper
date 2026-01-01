"""
AWP Core Configuration Manager
Centralizes all configuration logic for daemon, nav, dab, and setup modules.
Handles loading, validation, caching, and workspace-specific configuration.
"""

import configparser
import os
import logging
from pathlib import Path
from typing import Any, Dict, Optional, List, Union

# CORE IMPORTS
from core.constants import CONFIG_PATH, VALID_DES

# Initialize logger for config-related events
logger = logging.getLogger("AWP.Config")

class ConfigError(Exception):
    """Raised when configuration is invalid or missing required sections."""
    pass

class AWPConfig:
    """
    Main configuration manager for AWP.
    Provides safe access to config values with caching and validation.
    
    Attributes:
        path (Path): Path to the .ini configuration file.
        config (configparser.ConfigParser): The underlying parser instance.
    """
    
    def __init__(self, config_path: str = CONFIG_PATH):
        """Initializes the manager and loads the configuration from disk."""
        self.path: Path = Path(config_path)
        self.config: configparser.ConfigParser = configparser.ConfigParser()
        self._workspace_cache: Dict[str, Any] = {}
        self._global_cache: Dict[str, Any] = {}
        self._loaded: bool = False
        self._load()

    def _load(self) -> None:
        """Load configuration file with basic validation.
        
        Raises:
            ConfigError: If the file is missing or required sections are absent.
        """
        if not self.path.exists():
            logger.critical(f"Configuration file not found: {self.path}")
            raise ConfigError(f"Configuration file not found: {self.path}")
        
        try:
            self.config.read(self.path)
            self._validate_required_sections()
            self._loaded = True
        except Exception as e:
            logger.error(f"Failed to parse config file: {e}")
            raise ConfigError(f"Invalid .ini format: {e}")

    def _validate_required_sections(self) -> None:
        """Ensures the 'general' section and workspace sections exist."""
        if 'general' not in self.config:
            raise ConfigError("Missing required section: [general]")
            
        n_ws = self.getint('general', 'workspaces', default=4)
        for i in range(1, n_ws + 1):
            section = f'ws{i}'
            if section not in self.config:
                logger.warning(f"Configured for {n_ws} workspaces, but [{section}] is missing.")

    # === CORE ACCESSORS ===
    
    def get(self, section: str, key: str, default: Any = None) -> str:
        """Safely fetch a string value from the config."""
        try:
            return self.config.get(section, key, fallback=str(default) if default is not None else '')
        except configparser.NoSectionError:
            return str(default) if default is not None else ''

    def getint(self, section: str, key: str, default: int = 0) -> int:
        """Safely fetch an integer value."""
        try:
            return self.config.getint(section, key, fallback=default)
        except (configparser.NoSectionError, ValueError):
            return default

    def getbool(self, section: str, key: str, default: bool = False) -> bool:
        """Safely fetch a boolean value."""
        try:
            return self.config.getboolean(section, key, fallback=default)
        except (configparser.NoSectionError, ValueError):
            return default

    # === GLOBAL PROPERTIES ===
    
    @property
    def de(self) -> str:
        """Returns the detected desktop environment (cached)."""
        if 'de' not in self._global_cache:
            de = self.get('general', 'os_detected', 'unknown')
            if de not in VALID_DES:
                env_de = os.environ.get("XDG_CURRENT_DESKTOP", "").lower()
                de = next((de_type for de_type in VALID_DES if de_type in env_de), "generic")
            self._global_cache['de'] = de
        return self._global_cache['de']

    @property
    def session_type(self) -> str:
        """
        Returns the session type (x11 or wayland).
        Prioritizes the .ini file, falls back to system environment.
        """
        if 'session_type' not in self._global_cache:
            # 1. Try to get from [general] section in .ini
            sess = self.get('general', 'session_type', '').lower()
            
            # 2. If .ini is empty, detect from system (Mint XFCE is x11)
            if not sess:
                sess = os.environ.get("XDG_SESSION_TYPE", "x11").lower()
            
            self._global_cache['session_type'] = sess
            
        return self._global_cache['session_type']

    @property
    def is_x11(self) -> bool:
        """Returns True if running on X11 (standard for your Mint XFCE setup)."""
        return self.session_type == "x11"

    @property
    def workspaces_count(self) -> int:
        """Returns total number of workspaces from config."""
        if 'workspaces_count' not in self._global_cache:
            self._global_cache['workspaces_count'] = self.getint('general', 'workspaces', 4)
        return self._global_cache['workspaces_count']

    @property
    def blanking_timeout(self) -> int:
        """Returns screen blanking timeout in seconds."""
        timeout_str = self.get('general', 'blanking_timeout', '0')
        return int(timeout_str) if timeout_str.isdigit() else 0

    @property
    def blanking_pause(self) -> bool:
        """
        Returns the blanking pause state from the config.
        If True, the daemon will disable screen blanking/power management.
        """
        # Uses the getbool helper to turn 'true'/'false' strings into Python booleans
        return self.getbool('general', 'blanking_pause', default=False)

    @property
    def blanking_formatted(self) -> str:
        """Returns a human-readable string of the blanking timeout (e.g., '5m')."""
        if self.getbool('general', 'blanking_pause', False) or self.blanking_timeout == 0:
            return "off"
        
        t = self.blanking_timeout
        if t < 60: return f"{t}s"
        if t < 3600: return f"{t//60}m"
        return f"{t//3600}h{(t%3600)//60}m" if t%3600 else f"{t//3600}h"

    # === WORKSPACE LOGIC ===
    
    def get_workspace_config(self, ws_num: int):
        ws_key = f"ws{ws_num + 1}"
        return {
            'folder': self.get(ws_key, 'folder', ''),
            'icon': self.get(ws_key, 'icon', ''),
            'icon_theme': self.get(ws_key, 'icon_theme', ''),   # Added
            'cursor_theme': self.get(ws_key, 'cursor_theme', ''), # Added
            'gtk_theme': self.get(ws_key, 'gtk_theme', ''),     # Added
            'desktop_theme': self.get(ws_key, 'desktop_theme', ''), # Added
            'wm_theme': self.get(ws_key, 'wm_theme', ''),       # Added
            'timing': self.get(ws_key, 'timing', '5m'),
            'mode': self.get(ws_key, 'mode', 'random'),
            'order': self.get(ws_key, 'order', 'name_az'),
            'scaling': self.get(ws_key, 'scaling', 'scaled')
        }

    def get_conky_state(self, workspace_name: str, wallpaper_path: str) -> Dict[str, str]:
        """Generates a dictionary for the optional Conky HUD integration."""
        try:
            ws_num = int(workspace_name.replace('ws', '')) - 1
            ws_cfg = self.get_workspace_config(ws_num)
            
            return {
                'wallpaper_path': wallpaper_path,
                'workspace_name': workspace_name,
                'logo_path': ws_cfg['icon'],
                'icon_color': ws_cfg['icon_color'],
                'intv': ws_cfg['timing'],
                'flow': ws_cfg['mode'],
                'sort': ws_cfg['order'],
                'view': ws_cfg['scaling'],
                'blanking_timeout': self.blanking_formatted,
                'blanking_paused': str(self.getbool('general', 'blanking_pause')),
            }
        except Exception as e:
            logger.debug(f"Could not generate Conky state: {e}")
            return {}
            
    def set(self, section: str, key: str, value: str) -> None:
        """
        Updates a configuration value in memory and clears relevant caches.
        
        Args:
            section (str): The section (e.g., 'general' or 'ws1')
            key (str): The setting name
            value (str): The new value to store
        """
        if section not in self.config:
            self.config.add_section(section)
        
        self.config.set(section, key, str(value))
        
        # Clear caches so the new value is reflected immediately 
        # when calling properties like self.de or self.workspaces_count
        if section == 'general':
            self._global_cache.clear()
        else:
            cache_key = f"ws_{section}"
            if cache_key in self._workspace_cache:
                del self._workspace_cache[cache_key]

    # === PERSISTENCE ===

    def save(self) -> None:
        """Saves current configuration to disk with a backup for safety."""
        if not self._loaded: return
            
        backup = self.path.with_suffix('.bak')
        try:
            if self.path.exists():
                self.path.replace(backup)
            
            with open(self.path, 'w') as f:
                self.config.write(f)
            logger.info(f"Configuration saved to {self.path}")
        except Exception as e:
            if backup.exists():
                backup.replace(self.path)
            logger.error(f"Save failed. Backup restored. Error: {e}")
            raise ConfigError(f"Failed to save config: {e}")

    def reload(self) -> None:
        """Forces a fresh load from disk and clears all caches."""
        self._workspace_cache.clear()
        self._global_cache.clear()
        self._load()

    def validate(self) -> List[str]:
        """Checks for common configuration issues (like missing folders)."""
        warnings = []
        for i in range(self.workspaces_count):
            folder = self.get_workspace_config(i).get('folder', '')
            if folder and not Path(folder).exists():
                warnings.append(f"WS{i+1}: Folder does not exist -> {folder}")
        return warnings
