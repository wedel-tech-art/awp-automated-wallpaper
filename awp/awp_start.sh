#!/bin/bash
# ==============================================================================
# AWP_START - Automated Wallpaper Profile & Daemon Manager
# Author: wedel-tech-art
# Repository: awp-automated-wallpaper
# Description: Manages preset identities, workspace icons, and daemon lifecycle.
# Features: SED-based path localization for TEMPLATE identity.
# ==============================================================================

# --- ANSI Colors for Bash ---
CLR_GREEN="\033[92m"
CLR_CYAN="\033[96m"
CLR_YELLOW="\033[93m"
CLR_RED="\033[91m"
CLR_RESET="\033[0m"

# --- Configuration & Paths ---
AWP_BASE="$HOME/awp"
PRESETS_DIR="$AWP_BASE/presets"
BACKUP_DIR="$AWP_BASE/presets-backup"
LOGOS_DIR="$AWP_BASE/logos"
CONFIG_FILE="$AWP_BASE/awp_config.ini"
DAEMON_PATH="$AWP_BASE/daemon.py"
STATE_FILE="/dev/shm/awp_full_state.json"
INDEX_FILE="$AWP_BASE/indexes.json"

# --- 1. Pre-Flight Safety Mirror ---
# Create a physical backup of all presets before performing symlink operations.
if [ -d "$PRESETS_DIR" ]; then
    mkdir -p "$BACKUP_DIR"
    # Using rsync to ensure an exact mirror without duplicating data unnecessarily
    rsync -a --delete "$PRESETS_DIR/" "$BACKUP_DIR/"
    echo -e "${CLR_CYAN}[INFO] Preset mirror updated at: $BACKUP_DIR${CLR_RESET}"
else
    echo -e "${CLR_YELLOW}[WARN] No presets folder found at $PRESETS_DIR. Skipping mirror.${CLR_RESET}"
fi

# --- 2. Preset Identity Management (The Identity Robbery) ---
# Check if a preset name was passed as the first argument.
PRESET_NAME=$1

if [ -n "$PRESET_NAME" ]; then
    TARGET_PRESET="$PRESETS_DIR/$PRESET_NAME"
    TARGET_INI="$TARGET_PRESET/$PRESET_NAME.ini"

    if [ -d "$TARGET_PRESET" ] && [ -f "$TARGET_INI" ]; then
        echo -e "${CLR_CYAN}[ACTION] Switching identity to: $PRESET_NAME${CLR_RESET}"

        # --- SELF-HEALING HOME PATH FOR TEMPLATE ---
        if [ "$PRESET_NAME" == "TEMPLATE" ]; then
            echo -e "${CLR_YELLOW}[ACTION] Localizing TEMPLATE paths for $USER...${CLR_RESET}"
            # Replaces /home/[any_user] with /home/$USER globally in the .ini
            sed -i "s|/home/[^/]*|/home/$USER|g" "$TARGET_INI"
        fi

        # Point the main config symlink to the chosen preset's .ini
        ln -sfn "$TARGET_INI" "$CONFIG_FILE"

        # Clean workspace icon symlinks first to ensure a clean mapping for variable WS counts
        rm -f "$LOGOS_DIR/ws"*.png
        for icon in "$TARGET_PRESET"/ws*.png; do
            [ -e "$icon" ] || continue
            ln -sfn "$icon" "$LOGOS_DIR/$(basename "$icon")"
        done
        echo -e "${CLR_GREEN}[SUCCESS] Symlinks updated for $PRESET_NAME assets.${CLR_RESET}"
    else
        echo -e "${CLR_RED}[ERROR] Preset '$PRESET_NAME' not found or missing .ini file!${CLR_RESET}"
        echo "[ABORT] Restarting daemon with current configuration."
    fi
fi

# --- 3. System Environment Setup ---
# Ensure local icon and theme directories exist for the XFCE/Qtile environment.
mkdir -p "$HOME/.icons"
mkdir -p "$HOME/.themes"

# Link the Master Icon Library (Mint-Y focus)
MASTER_LIB="$AWP_BASE/awp-icon-mom/Mint-Y"
SYSTEM_TARGET="$HOME/.icons/Mint-Y"

if [ -d "$MASTER_LIB" ]; then
    ln -sfn "$MASTER_LIB" "$SYSTEM_TARGET"
fi

# --- 4. Process & State Cleanup ---
# Terminate existing daemon instances and clear ephemeral memory for a fresh start.
echo -e "${CLR_CYAN}[SYSTEM] Resetting AWP Daemon lifecycle...${CLR_RESET}"
pkill -f "$DAEMON_PATH" 2>/dev/null
sleep 1

# Clear JSON state and persistent index to prevent workspace/wallpaper mismatches.
rm -f "$STATE_FILE" 2>/dev/null
rm -f "$INDEX_FILE" 2>/dev/null
sleep 1

# --- 5. Execution ---
# Start the daemon in the background if the file exists.
if [ -f "$DAEMON_PATH" ]; then
    python3 "$DAEMON_PATH" &
    echo -e "${CLR_GREEN}[READY] AWP Daemon is live.${CLR_RESET}"
else
    echo -e "${CLR_RED}[FATAL] daemon.py not found at $DAEMON_PATH${CLR_RESET}"
fi

# --- 6. Final Status Report ---
# Confirms the currently active preset by reading the symlink.
sleep 0.5
if [ -L "$CONFIG_FILE" ]; then
    CURRENT_INI=$(readlink -f "$CONFIG_FILE")
    CURRENT_PRESET=$(basename "$(dirname "$CURRENT_INI")")
    echo -e "${CLR_CYAN}[STATUS] Active Identity: ${CLR_GREEN}${CURRENT_PRESET}${CLR_RESET}"
else
    echo -e "${CLR_YELLOW}[STATUS] No active preset linked.${CLR_RESET}"
fi
