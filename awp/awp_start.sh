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
            sed -i "s|/home/[^/]*|$HOME|g" "$TARGET_INI"
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

# --- 3.5 QT6 THEMING INFRASTRUCTURE (AWP Feature) ---
echo -e "${CLR_CYAN}[QT6] Setting up Qt6 theming infrastructure...${CLR_RESET}"

# Check if qt6ct is installed
if ! command -v qt6ct &> /dev/null; then
    echo -e "${CLR_YELLOW}[WARN] qt6ct not installed. Qt6 theming will not work.${CLR_RESET}"
    echo -e "${CLR_YELLOW}[WARN] Install with: sudo apt install qt6ct${CLR_RESET}"
else
    # Create qt6ct config directory if it doesn't exist
    QT6CT_DIR="$HOME/.config/qt6ct"
    QT6CT_COLORS="$QT6CT_DIR/colors"
    QT6CT_CONF="$QT6CT_DIR/qt6ct.conf"
    AWP_SYMLINK="$QT6CT_COLORS/awp.conf"
    SHM_FILE="/dev/shm/awp-qt-color.conf"
    
    mkdir -p "$QT6CT_COLORS"
    
    # Check if qt6ct.conf exists, if not create minimal version
    if [ ! -f "$QT6CT_CONF" ]; then
        echo -e "${CLR_CYAN}[QT6] Creating minimal qt6ct.conf...${CLR_RESET}"
        cat > "$QT6CT_CONF" << EOF
[Appearance]
color_scheme_path=$HOME/.config/qt6ct/colors/awp.conf
custom_palette=true

[Fonts]
fixed="Source Code Pro,10,-1,5,400,0,0,0,0,0,0,0,0,0,0,1"
general="Source Code Pro,10,-1,5,400,0,0,0,0,0,0,0,0,0,0,1"
EOF
        echo -e "${CLR_GREEN}[QT6] Created $QT6CT_CONF${CLR_RESET}"
    fi
    
    # Ensure the symlink exists
    if [ ! -L "$AWP_SYMLINK" ] || [ "$(readlink "$AWP_SYMLINK")" != "$SHM_FILE" ]; then
        echo -e "${CLR_CYAN}[QT6] Creating symlink: $AWP_SYMLINK -> $SHM_FILE${CLR_RESET}"
        rm -f "$AWP_SYMLINK"
        ln -sf "$SHM_FILE" "$AWP_SYMLINK"
        echo -e "${CLR_GREEN}[QT6] Symlink created.${CLR_RESET}"
    fi
    
    # Check if QT_QPA_PLATFORMTHEME is set in .profile
    if ! grep -q "QT_QPA_PLATFORMTHEME=qt6ct" "$HOME/.profile" 2>/dev/null; then
        echo -e "${CLR_YELLOW}[WARN] QT_QPA_PLATFORMTHEME not set in ~/.profile${CLR_RESET}"
        echo -e "${CLR_YELLOW}[WARN] Add this line: export QT_QPA_PLATFORMTHEME=qt6ct${CLR_RESET}"
    else
        echo -e "${CLR_GREEN}[QT6] Environment variable configured.${CLR_RESET}"
    fi
    
    # Create a default color scheme file if it doesn't exist
    if [ ! -f "$SHM_FILE" ]; then
        echo -e "${CLR_CYAN}[QT6] Creating initial color scheme in RAM...${CLR_RESET}"
        cat > "$SHM_FILE" << 'EOF'
[ColorScheme]
active_colors=#ffffff, #ff2e2e2e, #ff4e4e4e, #ff3a3a3a, #ff1a1a1a, #ff2a2a2a, #ffffffff, #ffffffff, #ffffffff, #ff242424, #ff2e2e2e, #ffffffff, #00f076, #ffffffff, #ffff6a00, #ffa70b06, #ff2e2e2e, #ffffffff, #ff3f3f36, #ffffffff, #80ffffff, #ff12608a
inactive_colors=#ffffffff, #ff2e2e2e, #ff4e4e4e, #ff3a3a3a, #ff1a1a1a, #ff2a2a2a, #ffffffff, #ffffffff, #ffffffff, #ff242424, #ff2e2e2e, #ffffffff, #00f076, #ffffffff, #ffff6a00, #ffa70b06, #ff2e2e2e, #ffffffff, #ff3f3f36, #ffffffff, #80ffffff, #ff12608a
disabled_colors=#ff808080, #ff2e2e2e, #ff4e4e4e, #ff3a3a3a, #ff1a1a1a, #ff2a2a2a, #ff808080, #ffffffff, #ff808080, #ff242424, #ff2e2e2e, #ffffffff, #00f076, #ff808080, #ffff6a00, #ffa70b06, #ff2e2e2e, #ffffffff, #ff3f3f36, #ffffffff, #80ffffff, #ff12608a
EOF
        echo -e "${CLR_GREEN}[QT6] Initial color scheme created.${CLR_RESET}"
    fi
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
