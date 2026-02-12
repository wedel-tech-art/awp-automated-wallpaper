#!/usr/bin/env python3
"""
Runtime state handling for AWP.
Responsible for writing unified runtime state.
"""

import json
from core.constants import RUNTIME_STATE_PATH


def update_runtime_state(state_dict: dict):
    """Write unified runtime state to shared memory JSON."""
    with open(RUNTIME_STATE_PATH, "w") as f:
        json.dump(state_dict, f)
