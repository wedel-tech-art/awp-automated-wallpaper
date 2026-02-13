#!/bin/sh
# awp_start.sh - Startup script for AWP Daemon
# Customize this script to add your own startup commands (Conky, etc.)

# Kill any previous instances
pkill -f "$HOME/awp/daemon.py" 2>/dev/null
sleep 1

# Start the AWP daemon
python3 "$HOME/awp/daemon.py" &
