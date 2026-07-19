#!/bin/bash
# preset_cloner.sh - Clone current preset to ALL or SPECIFIC presets
# Usage: 
#   preset_cloner.sh              # Clone to ALL presets
#   preset_cloner.sh [target]     # Clone to specific preset only

# ============================================================
# COLORS
# ============================================================
CLR_GREEN="\033[92m"
CLR_CYAN="\033[96m"
CLR_YELLOW="\033[93m"
CLR_RED="\033[91m"
CLR_RESET="\033[0m"

# ============================================================
# CONFIG
# ============================================================
AWP_DIR="$HOME/awp"
PRESETS_DIR="$AWP_DIR/presets"
ACTIVE_PRESET=$(cat /dev/shm/awp_active_preset 2>/dev/null)

# ============================================================
# BLANKING DISABLE LIST (Wayland and others)
# ============================================================
# Add any preset patterns here that should have blanking disabled
# These can be partial matches (e.g., "wayland" matches any preset with "wayland")
BLANKING_DISABLE_PATTERNS=(
    "wayland"           # All Wayland presets
    "qtile_wayland"     # Qtile Wayland presets
    "sway"              # Sway WM
    "hyprland"          # Hyprland WM
)

# Or use exact matches for specific presets
BLANKING_DISABLE_EXACT=(
    "gnome_wayland-debian"
    "gnome_wayland-cachyos"
    "gnome_wayland-arch"
    "qtile_wayland-debian"
)

# ============================================================
# DETECT ALL PRESETS (AUTO)
# ============================================================
detect_presets() {
    local presets=()
    for dir in "$PRESETS_DIR"/*; do
        if [ -d "$dir" ]; then
            name=$(basename "$dir")
            [ "$name" == "TEMPLATE" ] && continue
            presets+=("$name")
        fi
    done
    echo "${presets[@]}"
}

# ============================================================
# CHECK IF LIGHT PRESET
# ============================================================
is_light_preset() {
    local name="$1"
    [[ "$name" == *_light-* ]] || [[ "$name" == *_light ]]
}

# ============================================================
# GET BASE PRESET NAME (remove _light)
# ============================================================
get_base_preset() {
    local name="$1"
    local base="${name/_light-/-}"
    base="${base/_light/}"
    echo "$base"
}

# ============================================================
# GET DESKTOP NAME
# ============================================================
get_desktop_name() {
    local name="$1"
    
    if is_light_preset "$name"; then
        local base=$(get_base_preset "$name")
        echo "${base%-*}"
        return
    fi
    
    if [[ "$name" == qtile_* ]]; then
        echo "${name%-*}"
        return
    fi
    
    echo "${name%-*}"
}

# ============================================================
# CHECK IF BLANKING SHOULD BE DISABLED
# ============================================================
should_disable_blanking() {
    local preset="$1"
    
    # Check exact matches first
    for exact in "${BLANKING_DISABLE_EXACT[@]}"; do
        if [ "$preset" == "$exact" ]; then
            return 0  # True - disable blanking
        fi
    done
    
    # Check patterns
    for pattern in "${BLANKING_DISABLE_PATTERNS[@]}"; do
        if [[ "$preset" == *"$pattern"* ]]; then
            return 0  # True - disable blanking
        fi
    done
    
    return 1  # False - keep blanking
}

# ============================================================
# ENFORCE ICON PATHS TO LOGOS/
# ============================================================
enforce_icon_paths() {
    local ini_file="$1"
    
    # Read number of workspaces from INI (fallback to 4)
    local num_ws=$(grep "^workspaces =" "$ini_file" | head -1 | sed 's/.*= //' | tr -d ' ' || echo "4")
    if ! [[ "$num_ws" =~ ^[0-9]+$ ]] || [ "$num_ws" -lt 1 ]; then
        num_ws=4
    fi
    
    # Force ws{N}.png paths (standard format)
    for i in $(seq 1 "$num_ws"); do
        if grep -q "^icon = .*/ws${i}\.png" "$ini_file" 2>/dev/null; then
            sed -i "s|^icon = .*/ws${i}\.png|icon = $HOME/awp/logos/ws${i}.png|" "$ini_file" 2>/dev/null
        fi
    done
}

# ============================================================
# CLONE FUNCTION (Single target)
# ============================================================
clone_to_target() {
    local TARGET="$1"
    local SOURCE="$ACTIVE_PRESET"
    
    # Skip current
    if [ "$TARGET" == "$SOURCE" ]; then
        echo -e "${CLR_YELLOW}⏭️  Skipping $TARGET (current)${CLR_RESET}"
        return 1
    fi
    
    # Skip TEMPLATE
    if [ "$TARGET" == "TEMPLATE" ]; then
        return 1
    fi
    
    SOURCE_DIR="$PRESETS_DIR/$SOURCE"
    TARGET_DIR="$PRESETS_DIR/$TARGET"
    
    # Check if source exists
    if [ ! -d "$SOURCE_DIR" ]; then
        echo -e "${CLR_RED}❌ Source not found: $SOURCE${CLR_RESET}"
        return 1
    fi
    
    echo -e "${CLR_CYAN}📦${CLR_RESET} $SOURCE ${CLR_CYAN}→${CLR_RESET} $TARGET"
    
    # Delete target if exists (fresh clone)
    if [ -d "$TARGET_DIR" ]; then
        rm -rf "$TARGET_DIR"
    fi
    
    # Copy everything
    cp -r "$SOURCE_DIR" "$TARGET_DIR"
    
    # Rename INI
    if [ -f "$TARGET_DIR/$SOURCE.ini" ]; then
        mv "$TARGET_DIR/$SOURCE.ini" "$TARGET_DIR/$TARGET.ini"
    else
        echo -e "  ${CLR_RED}❌${CLR_RESET} Source INI not found!"
        return 1
    fi
    
    # Rename BAK if exists
    if [ -f "$TARGET_DIR/$SOURCE.bak" ]; then
        mv "$TARGET_DIR/$SOURCE.bak" "$TARGET_DIR/$TARGET.bak"
    fi
    
    # Get desktop name for target
    DESKTOP=$(get_desktop_name "$TARGET")
    
    # Update os_detected
    sed -i "s/os_detected = .*/os_detected = $DESKTOP/" "$TARGET_DIR/$TARGET.ini"
    
    if is_light_preset "$TARGET"; then
        echo -e "  ${CLR_YELLOW}☀️${CLR_RESET} Light preset - os_detected = $DESKTOP"
    else
        echo -e "  ${CLR_GREEN}✅${CLR_RESET} os_detected → $DESKTOP"
    fi
    
    # ============================================================
    # ENFORCE ICON PATHS TO LOGOS/
    # ============================================================
    enforce_icon_paths "$TARGET_DIR/$TARGET.ini"
    echo -e "  ${CLR_GREEN}✅${CLR_RESET} icon paths enforced to logos/"
    
    # ============================================================
    # BLANKING DISABLE (Wayland and others)
    # ============================================================
    if should_disable_blanking "$TARGET"; then
        sed -i 's/blanking_timeout = .*/blanking_timeout = 0/' "$TARGET_DIR/$TARGET.ini"
        sed -i 's/blanking_pause = .*/blanking_pause = true/' "$TARGET_DIR/$TARGET.ini"
        echo -e "  ${CLR_GREEN}✅${CLR_RESET} blanking disabled (Wayland/Wayland-like)"
    fi
    
    # ============================================================
    # SESSION_TYPE = wayland (for any preset that needs blanking disabled)
    # ============================================================
    if should_disable_blanking "$TARGET"; then
        sed -i 's/session_type = .*/session_type = wayland/' "$TARGET_DIR/$TARGET.ini"
        echo -e "  ${CLR_GREEN}✅${CLR_RESET} session_type = wayland"
    fi
    
    # Update paths
    sed -i "s|/$SOURCE/|/$TARGET/|g" "$TARGET_DIR/$TARGET.ini"
    
    echo -e "  ${CLR_GREEN}✅${CLR_RESET} Clone complete"
    return 0
}

# ============================================================
# MAIN
# ============================================================
echo -e "${CLR_CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${CLR_RESET}"
echo -e "${CLR_CYAN}   PRESET CLONER - Universal Preset Syncer${CLR_RESET}"
echo -e "${CLR_CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${CLR_RESET}"
echo ""

# --- Check if active preset exists ---
if [ -z "$ACTIVE_PRESET" ]; then
    echo -e "${CLR_RED}❌ No active preset found!${CLR_RESET}"
    echo -e "${CLR_YELLOW}Run awp_start.sh first.${CLR_RESET}"
    exit 1
fi

if [ "$ACTIVE_PRESET" == "TEMPLATE" ]; then
    echo -e "${CLR_RED}❌ Cannot clone from TEMPLATE (untouchable!)${CLR_RESET}"
    exit 1
fi

SOURCE_DIR="$PRESETS_DIR/$ACTIVE_PRESET"
if [ ! -d "$SOURCE_DIR" ]; then
    echo -e "${CLR_RED}❌ Source preset not found: $ACTIVE_PRESET${CLR_RESET}"
    exit 1
fi

echo -e "${CLR_GREEN}📦 Source:${CLR_RESET} $ACTIVE_PRESET"
echo ""

# ============================================================
# Check if specific target was provided
# ============================================================
if [ -n "$1" ]; then
    TARGET="$1"
    echo -e "${CLR_CYAN}🎯 Target:${CLR_RESET} $TARGET (single)"
    echo ""
    
    # Validate target exists in presets
    if [ ! -d "$PRESETS_DIR/$TARGET" ] && [ "$TARGET" != "TEMPLATE" ]; then
        echo -e "${CLR_RED}❌ Target preset not found: $TARGET${CLR_RESET}"
        echo ""
        echo -e "${CLR_CYAN}Available presets:${CLR_RESET}"
        for p in $(detect_presets); do
            echo "  - $p"
        done
        exit 1
    fi
    
    # Clone single target
    clone_to_target "$TARGET"
    EXIT_CODE=$?
    
    echo ""
    if [ $EXIT_CODE -eq 0 ]; then
        echo -e "${CLR_GREEN}✅ Clone complete!${CLR_RESET}"
        echo -e "${CLR_CYAN}💡 To switch: awp_start.sh $TARGET${CLR_RESET}"
    else
        echo -e "${CLR_YELLOW}⚠️  Clone skipped or failed${CLR_RESET}"
    fi
    exit $EXIT_CODE
fi

# ============================================================
# No target specified → Clone to ALL presets
# ============================================================
ALL_PRESETS=($(detect_presets))
TOTAL_PRESETS=${#ALL_PRESETS[@]}

echo -e "${CLR_CYAN}📋 Found ${TOTAL_PRESETS} presets total${CLR_RESET}"
echo -e "${CLR_YELLOW}⚠️  This will OVERWRITE all presets except:${CLR_RESET}"
echo -e "   - ${CLR_GREEN}$ACTIVE_PRESET${CLR_RESET} (current)"
echo -e "   - ${CLR_GREEN}TEMPLATE${CLR_RESET} (untouchable)"
echo ""
read -p "Continue? (y/N): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo -e "${CLR_YELLOW}Cancelled.${CLR_RESET}"
    exit 0
fi
echo ""

# Clone to each preset
SUCCESS=0
FAILED=0
SKIPPED=0

for TARGET in "${ALL_PRESETS[@]}"; do
    clone_to_target "$TARGET"
    case $? in
        0) SUCCESS=$((SUCCESS + 1)) ;;
        1) SKIPPED=$((SKIPPED + 1)) ;;
        *) FAILED=$((FAILED + 1)) ;;
    esac
    echo ""
done

# ============================================================
# SUMMARY
# ============================================================
echo -e "${CLR_CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${CLR_RESET}"
echo -e "${CLR_GREEN}✅ DONE!${CLR_RESET}"
echo ""
echo -e "${CLR_CYAN}📊 Summary:${CLR_RESET}"
echo -e "  Source: ${CLR_GREEN}$ACTIVE_PRESET${CLR_RESET}"
echo -e "  Cloned successfully: ${CLR_GREEN}$SUCCESS${CLR_RESET}"
echo -e "  Skipped: ${CLR_YELLOW}$SKIPPED${CLR_RESET}"
echo -e "  Failed: ${CLR_RED}$FAILED${CLR_RESET}"
echo ""
echo -e "${CLR_CYAN}💡 All presets now have the same themes and configs!${CLR_RESET}"
echo -e "${CLR_CYAN}   Each keeps its own identity (os_detected, etc.)${CLR_RESET}"
