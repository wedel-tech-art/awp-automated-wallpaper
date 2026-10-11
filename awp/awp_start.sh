#!/bin/bash
# ==============================================================================
# AWP_START - Automated Wallpaper Profile & Daemon Manager (With Bypass List)
# ==============================================================================

# --- 0. BYPASS CONFIGURATION ---
# Add any preset names here that should NOT start the daemon.
# Example: BYPASS_LIST=("QTILE_DEFAULT" "MUSIC_STUDIO" "MINIMAL")
BYPASS_LIST=("qtile_xfce-debian" "qtile_gnome-debian" "qtile_wayland-debian")

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
DAEMON_LIGHT_PATH="$AWP_BASE/daemon-light.py"
MODE_FILE="/dev/shm/awp_rotation_mode"

# --- 1. Pre-Flight Rotating Backup ---
BACKUP_KEEP=3

if [ -d "$PRESETS_DIR" ]; then
    mkdir -p "$BACKUP_DIR"
    STAMP=$(date +%Y-%m-%d-%H-%M-%S)

    echo -e "${CLR_CYAN}[BACKUP] Snapshot: $STAMP${CLR_RESET}"

    # cd to the parent so rsync only ever copies "presets/",
    # never anything above it (no home-within-home).
    # --exclude='themes/' drops every preset's themes dir (regenerable by baker).
    T0=$(date +%s.%N)
    ( cd "$AWP_BASE" && rsync -a --one-file-system --exclude='themes/' \
        "$(basename "$PRESETS_DIR")/" "$BACKUP_DIR/$STAMP/" )
    T1=$(date +%s.%N)

    # Keep only the newest $BACKUP_KEEP snapshots.
    BEFORE=$(ls -1d "$BACKUP_DIR"/[0-9]* 2>/dev/null | wc -l)

    # Collect what's about to be pruned, so we can name it.
    PRUNED=$(ls -1d "$BACKUP_DIR"/[0-9]* 2>/dev/null | sort | head -n -"$BACKUP_KEEP")
    if [ -n "$PRUNED" ]; then
        echo "$PRUNED" | xargs -r rm -rf
    fi

    AFTER=$(ls -1d "$BACKUP_DIR"/[0-9]* 2>/dev/null | wc -l)

    # Report rsync duration
    RSYNC_SEC=$(echo "$T1 - $T0" | bc)
    echo -e "${CLR_CYAN}[BACKUP] Copy took $(printf '%.2f' "$RSYNC_SEC")s${CLR_RESET}"

    # Report what was pruned (by name) and the ring size
    if [ "$BEFORE" -gt "$AFTER" ]; then
        while IFS= read -r d; do
            echo -e "${CLR_YELLOW}[BACKUP] Pruned: $(basename "$d")${CLR_RESET}"
        done <<< "$PRUNED"
    fi
    echo -e "${CLR_GREEN}[BACKUP] Ring: $AFTER / $BACKUP_KEEP${CLR_RESET}"
fi

# --- 2. Preset Identity Management ---
PRESET_NAME=$1

if [ -n "$PRESET_NAME" ]; then
    TARGET_PRESET="$PRESETS_DIR/$PRESET_NAME"
    TARGET_INI="$TARGET_PRESET/$PRESET_NAME.ini"

    if [ -d "$TARGET_PRESET" ] && [ -f "$TARGET_INI" ]; then
        echo -e "${CLR_CYAN}[ACTION] Switching identity to: $PRESET_NAME${CLR_RESET}"
        mkdir -p "$LOGOS_DIR"
        ln -sfn "$TARGET_INI" "$CONFIG_FILE"

        # ============================================================
        # 1. ENFORCE ICON PATHS TO LOGOS
        # ============================================================
        echo -e "${CLR_CYAN}[ICON] Ensuring icon paths point to logos/...${CLR_RESET}"

        # Read number of workspaces from INI (fallback to 4)
        NUM_WS=$(grep "^workspaces =" "$TARGET_INI" | head -1 | sed 's/.*= //' | tr -d ' ' || echo "4")
        if ! [[ "$NUM_WS" =~ ^[0-9]+$ ]] || [ "$NUM_WS" -lt 1 ]; then
            NUM_WS=4
        fi

        # Only force ws{N}.png paths (standard format)
        for i in $(seq 1 "$NUM_WS"); do
            # Look for lines with ws{N}.png and replace with logos/ws{N}.png
            if grep -q "^icon = .*/ws${i}\.png" "$TARGET_INI" 2>/dev/null; then
                sed -i "s|^icon = .*/ws${i}\.png|icon = $HOME/awp/logos/ws${i}.png|" "$TARGET_INI" 2>/dev/null
                echo -e "${CLR_GREEN}[ICON] Fixed ws$i${CLR_RESET}"
            fi
        done

        echo -e "${CLR_GREEN}[ICON] Icon paths enforced to logos/ ($NUM_WS workspaces)${CLR_RESET}"
        
        # ============================================================
        # 2. CREATE ICON SYMLINKS
        # ============================================================
        echo -e "${CLR_CYAN}[SYMLINK] Creating icon symlinks in logos/...${CLR_RESET}"
        
        rm -f "$LOGOS_DIR/ws"*.png
        for icon in "$TARGET_PRESET"/ws*.png; do
            [ -e "$icon" ] && ln -sfn "$icon" "$LOGOS_DIR/$(basename "$icon")"
        done
        echo -e "${CLR_GREEN}[SUCCESS] Icon symlinks updated.${CLR_RESET}"
        
        # ======================================================================
        # 3. THEME SYMLINKING
        # ======================================================================
        echo -e "${CLR_CYAN}[THEMES] Linking themes for $PRESET_NAME...${CLR_RESET}"
        
        THEMES_DIR="$TARGET_PRESET/themes"
        
        # Clean up old theme symlinks (but keep non-awp themes!)
        echo -e "${CLR_CYAN}[THEMES] Cleaning old symlinks...${CLR_RESET}"
        find "$HOME/.themes" -maxdepth 1 -type l -name "awp-*" -exec rm -f {} \; 2>/dev/null
        find "$HOME/.icons" -maxdepth 1 -type l -name "awp-*" -exec rm -f {} \; 2>/dev/null
        
        # Link GTK themes
        if [ -d "$THEMES_DIR/gtk" ]; then
            for theme in "$THEMES_DIR/gtk"/*; do
                if [ -d "$theme" ]; then
                    name=$(basename "$theme")
                    ln -sfn "$theme" "$HOME/.themes/$name"
                    echo -e "${CLR_GREEN}[THEMES] Linked GTK: $name${CLR_RESET}"
                fi
            done
        fi
        
        # Link Icon themes
        if [ -d "$THEMES_DIR/icons" ]; then
            for theme in "$THEMES_DIR/icons"/*; do
                if [ -d "$theme" ]; then
                    name=$(basename "$theme")
                    ln -sfn "$theme" "$HOME/.icons/$name"
                    echo -e "${CLR_GREEN}[THEMES] Linked Icons: $name${CLR_RESET}"
                fi
            done
        fi
        
        # Link Cursor themes
        if [ -d "$THEMES_DIR/cursors" ]; then
            for theme in "$THEMES_DIR/cursors"/*; do
                if [ -d "$theme" ]; then
                    name=$(basename "$theme")
                    ln -sfn "$theme" "$HOME/.icons/$name"
                    echo -e "${CLR_GREEN}[THEMES] Linked Cursors: $name${CLR_RESET}"
                fi
            done
        fi
        
        # If no themes were linked, show a message
        if [ ! -d "$THEMES_DIR/gtk" ] && [ ! -d "$THEMES_DIR/icons" ] && [ ! -d "$THEMES_DIR/cursors" ]; then
            echo -e "${CLR_YELLOW}[THEMES] No themes found in preset. Themes may not be baked yet.${CLR_RESET}"
        fi
        
        echo "$PRESET_NAME" > /dev/shm/awp_active_preset
        
    else
        # ❌ Preset not found!
        echo -e "${CLR_RED}[ERROR] Preset '$PRESET_NAME' not found in $PRESETS_DIR${CLR_RESET}"
        echo -e "${CLR_RED}[ERROR] Available presets:${CLR_RESET}"
        ls -1 "$PRESETS_DIR" 2>/dev/null | grep -v "TEMPLATE" | sed 's/^/  - /'
        exit 1
    fi
else
    # No preset specified → show usage
    echo -e "${CLR_YELLOW}[USAGE] awp_start.sh [PRESET_NAME]${CLR_RESET}"
    echo -e "${CLR_YELLOW}Available presets:${CLR_RESET}"
    ls -1 "$PRESETS_DIR" 2>/dev/null | grep -v "TEMPLATE" | sed 's/^/  - /'
    exit 1
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
active_colors=#ffffff, #ff2e2e2e, #ff4e4e4e, #ff3a3a3a, #ff1a1a1a, #ff2a2a2a, #ffffffff, #ffffffff, #ffffffff, #ff242424, #ff2e2e2e, #ffffffff, #2e7faf, #ffffffff, #ffff6a00, #ffa70b06, #ff2e2e2e, #ffffffff, #ff3f3f36, #ffffffff, #80ffffff, #ff12608a
inactive_colors=#ffffffff, #ff2e2e2e, #ff4e4e4e, #ff3a3a3a, #ff1a1a1a, #ff2a2a2a, #ffffffff, #ffffffff, #ffffffff, #ff242424, #ff2e2e2e, #ffffffff, #2e7faf, #ffffffff, #ffff6a00, #ffa70b06, #ff2e2e2e, #ffffffff, #ff3f3f36, #ffffffff, #80ffffff, #ff12608a
disabled_colors=#ff808080, #ff2e2e2e, #ff4e4e4e, #ff3a3a3a, #ff1a1a1a, #ff2a2a2a, #ff808080, #ffffffff, #ff808080, #ff242424, #ff2e2e2e, #ffffffff, #2e7faf, #ff808080, #ffff6a00, #ffa70b06, #ff2e2e2e, #ffffffff, #ff3f3f36, #ffffffff, #80ffffff, #ff12608a
EOF
        echo -e "${CLR_GREEN}[QT6] Initial color scheme created.${CLR_RESET}"
    fi
fi

# --- 3.6 KDE THEMING INFRASTRUCTURE (AWP Feature) ---
echo -e "${CLR_CYAN}[KDE] Setting up KDE theming infrastructure...${CLR_RESET}"

# Create KDE color schemes directory
KDE_COLORS_DIR="$HOME/.local/share/color-schemes"
KDE_COLOR_FILE="$KDE_COLORS_DIR/AWP_Dynamic.colors"
SHM_KDE_FILE="/dev/shm/awp-kde-color.colors"

mkdir -p "$KDE_COLORS_DIR"

# Create initial KDE color scheme in RAM if it doesn't exist
if [ ! -f "$SHM_KDE_FILE" ]; then
    echo -e "${CLR_CYAN}[KDE] Creating initial color scheme in RAM...${CLR_RESET}"
    cat > "$SHM_KDE_FILE" << 'EOF'
[General]
Name=AWP_Dynamic
ReferenceColorScheme=BreezeDark

[Background:Normal]
Color=#2e2e2e
[Foreground:Normal]
Color=#cfcfc2
[Background:Selection]
Color=#2e7faf
[Colors:Selection]
BackgroundNormal=#2e7faf
ForegroundNormal=#ffffff
[Colors:Window]
BackgroundNormal=#2e2e2e
ForegroundNormal=#cfcfc2
[Colors:View]
BackgroundNormal=#242424
ForegroundNormal=#cfcfc2
[Colors:Button]
BackgroundNormal=#3a3a3a
ForegroundNormal=#cfcfc2
EOF
    echo -e "${CLR_GREEN}[KDE] Initial color scheme created.${CLR_RESET}"
fi

# Ensure the symlink exists
if [ ! -L "$KDE_COLOR_FILE" ] || [ "$(readlink "$KDE_COLOR_FILE")" != "$SHM_KDE_FILE" ]; then
    echo -e "${CLR_CYAN}[KDE] Creating symlink: $KDE_COLOR_FILE -> $SHM_KDE_FILE${CLR_RESET}"
    rm -f "$KDE_COLOR_FILE"
    ln -sf "$SHM_KDE_FILE" "$KDE_COLOR_FILE"
    echo -e "${CLR_GREEN}[KDE] Symlink created.${CLR_RESET}"
fi

# --- 4. Logic: Daemon Selection & Lifecycle ---
echo -e "${CLR_CYAN}[SYSTEM] Resetting AWP Daemon lifecycle...${CLR_RESET}"
pkill -f "$DAEMON_PATH" 2>/dev/null
pkill -f "$DAEMON_LIGHT_PATH" 2>/dev/null
sleep 1

# Check if current preset should bypass daemon completely
SHOULD_BYPASS=false
for bypassed in "${BYPASS_LIST[@]}"; do
    if [ "$PRESET_NAME" == "$bypassed" ]; then
        SHOULD_BYPASS=true
        break
    fi
done

if [ "$SHOULD_BYPASS" = true ]; then
    ROTATION_MODE="on-demand"
    echo -e "${CLR_YELLOW}[SKIP] Preset '$PRESET_NAME' is in Bypass List. Daemon will not start.${CLR_RESET}"
else
    # 🆕 Only read/write MODE_FILE for non-bypass presets (XFCE, Cinnamon, etc.)
    if [ -f "$MODE_FILE" ]; then
        ROTATION_MODE=$(cat "$MODE_FILE")
    else
        ROTATION_MODE="light"
        echo "light" > "$MODE_FILE"
    fi

    if [ "$ROTATION_MODE" = "light" ]; then
        if [ -f "$DAEMON_LIGHT_PATH" ]; then
            python3 "$DAEMON_LIGHT_PATH" &
            echo -e "${CLR_GREEN}[READY] AWP Light Daemon (no rotation) is live.${CLR_RESET}"
        else
            echo -e "${CLR_RED}[ERROR] Light daemon not found at $DAEMON_LIGHT_PATH${CLR_RESET}"
        fi
    else
        if [ -f "$DAEMON_PATH" ]; then
            python3 "$DAEMON_PATH" &
            echo -e "${CLR_GREEN}[READY] AWP Full Daemon (with rotation) is live.${CLR_RESET}"
        fi
    fi
fi

# --- 5. Final Status Report ---
sleep 0.5
if [ -L "$CONFIG_FILE" ]; then
    CURRENT_PRESET=$(basename "$(dirname "$(readlink -f "$CONFIG_FILE")")")
    echo -e "${CLR_CYAN}[STATUS] Active Identity: ${CLR_GREEN}${CURRENT_PRESET}${CLR_RESET}"
    echo -e "${CLR_CYAN}[STATUS] Rotation Mode: ${CLR_GREEN}${ROTATION_MODE}${CLR_RESET}"
fi
