#!/bin/sh
# awp_start.sh - Startup script for AWP Daemon
# Ensure target directories exist
mkdir -p "$HOME/.icons"
mkdir -p "$HOME/.themes"

# --- System Environment Setup ---
# Verify and link the Master Icon Library to the user environment
MASTER_LIB="$HOME/awp/awp-icon-mom/Mint-Y"
SYSTEM_TARGET="$HOME/.icons/Mint-Y"

if [ -d "$MASTER_LIB" ]; then
    # -sfn ensures the link is created or updated without recursion errors
    ln -sfn "$MASTER_LIB" "$SYSTEM_TARGET"
fi

# --- Process Management ---
pkill -f "$HOME/awp/daemon.py" 2>/dev/null
sleep 1

# Clear the previous state to ensure a fresh "Truth"
rm -f /dev/shm/awp_full_state.json 2>/dev/null
sleep 1

# Start the AWP daemon
python3 "$HOME/awp/daemon.py" &
