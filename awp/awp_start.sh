#!/bin/bash
# ==============================================================================
# AWP_START - Automated Wallpaper Profile & Daemon Manager (With Bypass List)
# ==============================================================================

# --- 0. BYPASS CONFIGURATION ---
# Add any preset names here that should NOT start the daemon.
# Example: BYPASS_LIST=("QTILE_DEFAULT" "MUSIC_STUDIO" "MINIMAL")
BYPASS_LIST=("qtile_xfce-debian")

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

# --- 1. Pre-Flight Safety Mirror ---
if [ -d "$PRESETS_DIR" ]; then
    mkdir -p "$BACKUP_DIR"
    rsync -a --delete "$PRESETS_DIR/" "$BACKUP_DIR/"
    echo -e "${CLR_CYAN}[INFO] Preset mirror updated.${CLR_RESET}"
fi

# --- 2. Preset Identity Management ---
PRESET_NAME=$1

if [ -n "$PRESET_NAME" ]; then
    TARGET_PRESET="$PRESETS_DIR/$PRESET_NAME"
    TARGET_INI="$TARGET_PRESET/$PRESET_NAME.ini"

    if [ -d "$TARGET_PRESET" ] && [ -f "$TARGET_INI" ]; then
        echo -e "${CLR_CYAN}[ACTION] Switching identity to: $PRESET_NAME${CLR_RESET}"

        if [ "$PRESET_NAME" == "TEMPLATE" ]; then
            echo -e "${CLR_YELLOW}[ACTION] Localizing TEMPLATE paths...${CLR_RESET}"
            sed -i "s|/home/[^/]*|/home/$USER|g" "$TARGET_INI"
        fi

        ln -sfn "$TARGET_INI" "$CONFIG_FILE"

        rm -f "$LOGOS_DIR/ws"*.png
        for icon in "$TARGET_PRESET"/ws*.png; do
            [ -e "$icon" ] && ln -sfn "$icon" "$LOGOS_DIR/$(basename "$icon")"
        done
        echo -e "${CLR_GREEN}[SUCCESS] Symlinks updated.${CLR_RESET}"
    fi
fi

# --- 3. System Environment Setup ---
mkdir -p "$HOME/.icons" "$HOME/.themes"
MASTER_LIB="$AWP_BASE/awp-icon-mom/Mint-Y"
if [ -d "$MASTER_LIB" ]; then
    ln -sfn "$MASTER_LIB" "$HOME/.icons/Mint-Y"
fi

# --- 4. Logic: Bypass Check & Daemon Lifecycle ---
echo -e "${CLR_CYAN}[SYSTEM] Resetting AWP Daemon lifecycle...${CLR_RESET}"
pkill -f "$DAEMON_PATH" 2>/dev/null
sleep 1

# Check if the current preset is in the bypass list
SHOULD_BYPASS=false
for bypassed in "${BYPASS_LIST[@]}"; do
    if [ "$PRESET_NAME" == "$bypassed" ]; then
        SHOULD_BYPASS=true
        break
    fi
done

if [ "$SHOULD_BYPASS" = true ]; then
    echo -e "${CLR_YELLOW}[SKIP] Preset '$PRESET_NAME' is in Bypass List. Daemon will not start.${CLR_RESET}"
else
    if [ -f "$DAEMON_PATH" ]; then
        python3 "$DAEMON_PATH" &
        echo -e "${CLR_GREEN}[READY] AWP Daemon is live.${CLR_RESET}"
    fi
fi

# --- 5. Final Status Report ---
sleep 0.5
if [ -L "$CONFIG_FILE" ]; then
    CURRENT_PRESET=$(basename "$(dirname "$(readlink -f "$CONFIG_FILE")")")
    echo -e "${CLR_CYAN}[STATUS] Active Identity: ${CLR_GREEN}${CURRENT_PRESET}${CLR_RESET}"
fi
