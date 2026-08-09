#!/usr/bin/env python3
"""
Runtime state handling for AWP.
Responsible for writing unified runtime state.
"""

import os
import json
from core.constants import AWP_DIR, STATE_PATH, RUNTIME_STATE_PATH, AWP_CONFIG_RAM, SHM_ACTIVE_PRESET

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
        print(f"Error writing RAM Config: {e}")

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
    import subprocess
    
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
        print(f"Warning: Could not detect mount labels dynamically: {e}")
        if target_mounts:
            for mount in target_mounts:
                if mount == "/":
                    mount_labels[mount] = "ROOT"
                else:
                    import os
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

