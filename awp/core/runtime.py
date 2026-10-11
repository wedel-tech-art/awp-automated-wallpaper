#!/usr/bin/env python3
"""
Runtime state handling for AWP.
Responsible for writing unified runtime state.
"""

import os
import subprocess
import json
from core.constants import (
    AWP_DIR,
    STATE_PATH,
    RUNTIME_STATE_PATH,
    AWP_CONFIG_RAM,
    SHM_ACTIVE_PRESET,
    AWP_FALLBACK_ACCENT,
)
from core.printer import get_printer

_printer = get_printer()


def update_runtime_state(state_dict: dict):
    tmp = RUNTIME_STATE_PATH + ".tmp"
    with open(tmp, "w") as f:
        json.dump(state_dict, f)
    os.replace(tmp, RUNTIME_STATE_PATH)

def load_index_state() -> dict:
    """Load workspace state from JSON file."""
    if not os.path.isfile(STATE_PATH):
        return {}
    try:
        with open(STATE_PATH, "r") as f:
            return json.load(f)
    except Exception:
        return {}

def save_index_state(state: dict):
    """Save workspace state to JSON file."""
    tmp = STATE_PATH + ".tmp"
    with open(tmp, "w") as f:
        json.dump(state, f)
    os.replace(tmp, STATE_PATH)

def update_ram_config(full_config_dict: dict):
    """
    Exports the complete configuration dictionary to a JSON file in RAM (/dev/shm).
    Uses an atomic replace operation to ensure data integrity during concurrent reads.
    """
    tmp = AWP_CONFIG_RAM + ".tmp"
    try:
        with open(tmp, "w") as f:
            json.dump(full_config_dict, f, indent=4)
        
        # Atomic replacement to prevent partial reads by other processes
        os.replace(tmp, AWP_CONFIG_RAM)
    except Exception as e:
        _printer.error(f"Error writing RAM Config: {e}")

# =============================================================================
# SYSTEM MONITORING (moved from utils.py)
# =============================================================================

def get_ram_info():
    """
    Returns RAM information in unified format: 'used|free|totalG'
    """
    try:
        with open('/proc/meminfo', 'r') as f:
            mem = {line.split()[0].rstrip(':'): int(line.split()[1]) for line in f}
        
        total = mem['MemTotal'] / 1024 / 1024
        free = mem['MemAvailable'] / 1024 / 1024
        used = total - free
        
        return f"{used:.1f}|{free:.1f}|{total:.1f}G"
    
    except Exception:
        return "??|??|??G"

def get_swap_info():
    """
    Returns SWAP information in unified format: 'used|free|totalG'
    Returns '0.0|0.0|0.0G' if no swap is present.
    """
    try:
        with open('/proc/meminfo', 'r') as f:
            mem = {line.split()[0].rstrip(':'): int(line.split()[1]) for line in f}
        
        total = mem.get('SwapTotal', 0) / 1024 / 1024
        free = mem.get('SwapFree', 0) / 1024 / 1024
        used = total - free
        
        if total == 0:
            return "0.0|0.0|0.0G"
        
        return f"{used:.1f}|{free:.1f}|{total:.1f}G"
    
    except Exception:
        return "??|??|??G"

def get_mounts_info(paths):
    """
    Returns filesystem information for multiple paths.
    Returns dict: {path: 'used|free|totalG'}
    """
    result = {}
    for path in paths:
        try:
            st = os.statvfs(path)
            used = (st.f_blocks - st.f_bfree) * st.f_frsize / (1024**3)
            free = st.f_bavail * st.f_frsize / (1024**3)
            total = st.f_blocks * st.f_frsize / (1024**3)
            result[path] = f"{used:.1f}|{free:.1f}|{total:.1f}G"
        except Exception:
            result[path] = "N/A|N/A|N/A"
    return result

def get_dynamic_mount_labels(target_mounts=None):
    """
    Dynamically map mount paths to device labels.
    
    Args:
        target_mounts: List of mount paths to map (e.g., ["/", "/mnt/internal1500"])
                      If None, returns all mounts.
    
    Returns:
        Dictionary: {mount_path: device_label} (e.g., {"/": "SDA2", "/mnt/internal1500": "SDB1"})
    """
    mount_labels = {}
    
    try:
        # Use -l flag for list format (no tree characters like ├─ └─)
        # Use -o for specific columns: NAME (device name) and MOUNTPOINT
        lsblk_output = subprocess.check_output(
            ["lsblk", "-l", "-o", "NAME,MOUNTPOINT"], 
            encoding='utf-8'
        )
        
        mount_to_dev = {}
        for line in lsblk_output.splitlines():
            # Skip the header line
            if line.startswith('NAME'):
                continue
                
            parts = line.split(maxsplit=1)
            if len(parts) == 2:
                dev_name, mountpoint = parts
                if mountpoint and mountpoint.strip():
                    # Clean the device name (remove any remaining special chars just in case)
                    dev_name = dev_name.strip()
                    mountpoint = mountpoint.strip()
                    mount_to_dev[mountpoint] = dev_name
        
        # If no specific targets requested, return all mounts
        if target_mounts is None:
            target_mounts = list(mount_to_dev.keys())
        
        # Build labels for requested mount points
        for mount in target_mounts:
            if mount in mount_to_dev:
                dev = mount_to_dev[mount]
                # Create label like "SDA2" (strip any numbers to keep just base name if preferred)
                # Remove partition numbers if you want just sda/sdb/sdc:
                # import re
                # dev = re.sub(r'\d+$', '', dev)
                label = dev.upper()
                mount_labels[mount] = label
            else:
                # Provide fallback label if mount point not found
                mount_labels[mount] = "???"
                
    except Exception as e:
        # Fallback to generic labels if detection fails
        _printer.warning(f"Could not detect mount labels dynamically: {e}")
        if target_mounts:
            for mount in target_mounts:
                if mount == "/":
                    mount_labels[mount] = "ROOT"
                else:
                    mount_labels[mount] = os.path.basename(mount).upper()[:8]
    
    return mount_labels
    
def get_preset_from_shm():
    """Read the current preset name from RAM-based session state."""
    shm_path = SHM_ACTIVE_PRESET
    if os.path.exists(shm_path):
        try:
            with open(shm_path, 'r') as f:
                return f.read().strip()
        except Exception:
            pass
    return None

# =============================================================================
# ACCENT READING — SHARED UTILITY
# =============================================================================
#
# read_raw_accent() is the canonical reader for the workspace accent color
# stored in RUNTIME_STATE_PATH (/dev/shm/awp_full_state.json, key "icon_color").
#
# -----------------------------------------------------------------------------
# CURRENT STATE (as of this writing)
# -----------------------------------------------------------------------------
# Several tools still have their own local accent readers instead of using
# this function. They are functionally similar but diverge in two ways:
#
#   1. FALLBACK COLOR
#      - wini, dab, hud_preset  → AWP_FALLBACK_ACCENT (#3daee9)   [correct]
#      - hud_wp, hud_vertical, hud_bottom → "#ffffff"             [bug]
#      - bath                   → tiered: raw → qt → AWP_FALLBACK_ACCENT
#
#      The "#ffffff" fallback in the three HUDs is a bug. On a fresh install
#      with no /dev/shm state, those HUDs render white text on a dark panel,
#      which looks broken. They should use AWP_FALLBACK_ACCENT.
#
#   2. ALPHA CHANNEL HANDLING
#      - bath, read_raw_accent  → strips 8-digit alpha (e.g. #ff00bebe → #00bebe)
#      - wini, dab, hud_preset  → only accepts 6-digit hex
#      - hud_wp, hud_vertical, hud_bottom → no validation at all
#
#      AWP currently writes 6-digit hexes, so this hasn't caused visible bugs.
#      If AWP ever writes 8-digit hexes (e.g. from an alpha-aware color picker),
#      the HUDs would pass invalid colors to Qt and render nothing.
#
# -----------------------------------------------------------------------------
# KNOWN DUPLICATE READERS (Group A — raw accent from awp_full_state.json)
# -----------------------------------------------------------------------------
#   File                  Function / location          Fallback
#   ---------------------------------------------------------------------------
#   core/runtime.py       read_raw_accent()              AWP_FALLBACK_ACCENT
#   dab                   update_info_colors() (inline)  AWP_FALLBACK_ACCENT
#   bath                  get_awp_real_accent()          tiered → qt accent
#   hud_wp.py             update_ui() (inline)           "#ffffff"
#   hud_vertical.py       update_ui() (inline)           "#ffffff"
#   hud_bottom.py         update_ui() (inline)           "#ffffff"
#
# MIGRATED (no longer duplicate):
#   wini                  ✅ imports read_raw_accent
#   hud_preset.py         ✅ imports read_raw_accent
#
# -----------------------------------------------------------------------------
# KNOWN DUPLICATE READERS (Group B — Qt accent from awp-qt-color.conf)
# -----------------------------------------------------------------------------
#   File                  Function / location          Extraction
#   ---------------------------------------------------------------------------
#   wini                  _get_accent_color()            last field in active_colors
#   dab                   get_awp_derived_accent()       last field in active_colors
#   bath                  get_awp_accent()               fields[12] (fixed index)
#
# NOTE: wini and dab use "last field"; bath uses fields[12]. These are not
# currently equivalent unless active_colors always has exactly 13 fields.
# Before unifying Group B, resolve which index is correct — inspect an actual
# /dev/shm/awp-qt-color.conf and count the fields.
#
# A future read_qt_accent() in this file should be the canonical reader for
# Group B, once the extraction logic is settled.
#
# -----------------------------------------------------------------------------
# FUTURE MIGRATION — WHEN AND WHY
# -----------------------------------------------------------------------------
# Migrating consumers to read_raw_accent() is a cleanup, not a bug fix.
# The tools all work today. Unification buys:
#
#   - Consistency: all tools render the same fallback color in the zero-state
#   - Maintainability: one place to fix if the /dev/shm format changes
#   - Correctness: alpha-channel handling is centralized
#
# Migrate opportunistically: when you touch a consumer file for another reason
# (adding a feature, fixing a bug), replace its local reader with a call to
# this function. Each migration is a ~3-line change per file:
#
#   Before:
#       color = data.get('icon_color', '#ffffff')
#
#   After:
#       from core.runtime import read_raw_accent
#       color = read_raw_accent()
#
# Do NOT do a big-bang refactor across all 8 consumers at once. The duplication
# is not causing problems, and a mass edit risks introducing subtle bugs in
# tools you aren't currently testing.
#
# -----------------------------------------------------------------------------
# WHEN UNIFICATION BECOMES MANDATORY
# -----------------------------------------------------------------------------
# Stop treating this as optional when any of the following happens:
#
#   1. A 9th consumer of the raw accent appears.
#   2. The /dev/shm/awp_full_state.json schema changes (renamed key,
#      changed format, additional fields).
#   3. AWP starts writing 8-digit hex colors to icon_color.
#   4. A user reports the white-vs-blue fallback inconsistency.
#
# Any of those turns the duplication from aesthetic debt into an active
# maintenance hazard.
#
# -----------------------------------------------------------------------------
# DESIGN NOTES
# -----------------------------------------------------------------------------
# - Returns lowercase hex ("#00bebe", not "#00BEBE"). AWP stores lowercase,
#   and Qt is case-insensitive for CSS colors, so this is a no-op for
#   well-formed inputs. If a consumer ever compares against an uppercase
#   literal, that comparison will need to be updated.
#
# - The `fallback` parameter allows callers to declare their own zero-state
#   policy. Example, preserving bath's tiered behavior:
#
#       accent = read_raw_accent(fallback=read_qt_accent())
#
#   Most consumers should pass nothing and accept AWP_FALLBACK_ACCENT.
#
# - Does not raise. Returns the fallback on any error: missing file,
#   malformed JSON, missing icon_color, invalid hex length, non-string value.
#
# =============================================================================

def read_raw_accent(fallback=None):
    """
    Read the raw workspace accent from RUNTIME_STATE_PATH.

    Handles:
      - Missing file
      - Malformed JSON
      - Missing or invalid icon_color field
      - 8-digit hex (strips alpha channel)
      - 6-digit hex (returns as-is)

    Falls back to `fallback` (default: AWP_FALLBACK_ACCENT) on any error.
    """
    if fallback is None:
        fallback = AWP_FALLBACK_ACCENT

    try:
        with open(RUNTIME_STATE_PATH, "r") as f:
            data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError, OSError):
        return fallback

    color = data.get("icon_color")
    if not isinstance(color, str) or not color.startswith("#"):
        return fallback

    raw = color.lstrip("#")
    if len(raw) == 8:
        raw = raw[2:]      # strip alpha
    if len(raw) == 6:
        return f"#{raw.lower()}"

    return fallback
