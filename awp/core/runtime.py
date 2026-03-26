#!/usr/bin/env python3
"""
Runtime state handling for AWP.
Responsible for writing unified runtime state.
"""

import os
import json
from core.constants import AWP_DIR, STATE_PATH, RUNTIME_STATE_PATH, AWP_CONFIG_RAM

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
