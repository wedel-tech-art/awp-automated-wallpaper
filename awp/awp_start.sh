#!/bin/sh
# awp_start.sh - Startup script for AWP Daemon
# Customize this script to add your own startup commands (Conky, etc.)

# CONFIG_FILE="$HOME/awp/awp_config.ini"

# =============================================================================
# FORCE SCREEN BLANKING SETTINGS (Early Override)
# We set this here to ensure it applies immediately, preventing the default
# 10-minute timeout from taking over before the Python daemon is ready.
# 1200 seconds = 20 minutes (matches your awp_config.ini setting)
# =============================================================================
#xset s 1200
#xset +dpms
#xset dpms 1200 1200 1200
# =============================================================================


# Kill any previous instances
pkill -f "$HOME/awp/awp_daemon.py" 2>/dev/null
sleep 1

# Start the AWP daemon
python3 "$HOME/awp/awp_daemon.py" &

# =============================================================================
# CUSTOM INTEGRATIONS - UNCOMMENT AND MODIFY AS NEEDED
# =============================================================================

sleep 1
pkill -f conky
sleep 1
# Example: Start Conky with your custom configuration
conky -c "$HOME/awp/conky/conkyrc_wp_sys" &

# Example: Start Conky with AWP-specific configuration  
# conky -c "$HOME/awp/conky/my_conky_config" &

# Example: Start other desktop widgets or integrations
# your_custom_widget_command &

# =============================================================================
