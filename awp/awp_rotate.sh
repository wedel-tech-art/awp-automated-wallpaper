#!/bin/bash
# Toggle auto-rotation (ADAPTIVE to current workspace + preset-aware)
# Polls /dev/shm/awp_full_state.json every 2 seconds for workspace/interval changes

FLAG="/tmp/awp_rotate"
PID_FILE="/tmp/awp_rotate.pid"
SLEEP_PID_FILE="/tmp/awp_rotate_sleep.pid"
AWP_DIR="/home/ows/awp"
PRESET_FILE="/dev/shm/awp_active_preset"
STATE_FILE="/dev/shm/awp_full_state.json"

get_current_preset() {
    if [ -f "$PRESET_FILE" ]; then
        cat "$PRESET_FILE"
    else
        echo ""
    fi
}

is_bypass_preset() {
    local preset=$(get_current_preset)
    case "$preset" in
        qtile_xfce-debian|qtile_gnome-debian|qtile_wayland-debian)
            return 0
            ;;
        *)
            return 1
            ;;
    esac
}

is_light_preset() {
    local preset=$(get_current_preset)
    [[ "$preset" == *_light-* ]] || [[ "$preset" == *_light ]]
}

get_light_preset() {
    local preset=$(get_current_preset)
    if [[ "$preset" == *-* ]]; then
        local base="${preset%-*}"
        local distro="${preset##*-}"
        echo "${base}_light-${distro}"
    else
        echo "${preset}_light"
    fi
}

get_base_preset() {
    local preset=$(get_current_preset)
    echo "${preset/_light-/-}"
}

get_current_state() {
    if [ -f "$STATE_FILE" ]; then
        python3 -c "
import json
try:
    with open('$STATE_FILE', 'r') as f:
        state = json.load(f)
    ws = state.get('workspace_name', 'unknown')
    intv = state.get('intv', '5m')
    print(f'{ws}|{intv}')
except:
    print('unknown|5m')
"
    else
        echo "unknown|5m"
    fi
}

parse_timing() {
    local timing="$1"
    case "$timing" in
        *s) echo "${timing%s}" ;;
        *m) echo $((${timing%m} * 60)) ;;
        *h) echo $((${timing%h} * 3600)) ;;
        *) echo 300 ;;
    esac
}

send_notification() {
    local msg="$1"
    local urgency="${2:-normal}"
    if command -v notify-send &> /dev/null; then
        notify-send -u "$urgency" "AWP Rotation" "$msg" 2>/dev/null
    fi
    echo "AWP Rotation: $msg"
}

# ======================================================================
# 1. PRESET DECISION
# ======================================================================
PRESET=$(get_current_preset)

if [ -z "$PRESET" ] || [ "$PRESET" == "unknown" ]; then
    send_notification "⚠️ No AWP preset detected. Please run awp_start.sh first." "critical"
    exit 1
fi

if is_bypass_preset; then
    DAEMON_MODE="bypass"
elif is_light_preset; then
    DAEMON_MODE="light"
else
    DAEMON_MODE="full"
fi

# ======================================================================
# BYPASS MODE (Qtile) - Adaptive rotation with 2-second polling
# ======================================================================
if [ "$DAEMON_MODE" == "bypass" ]; then
    if [ -f "$PID_FILE" ] && kill -0 $(cat "$PID_FILE") 2>/dev/null; then
        # Turn OFF
        rm -f "$FLAG"
        if [ -f "$SLEEP_PID_FILE" ]; then
            kill -9 $(cat "$SLEEP_PID_FILE") 2>/dev/null
            rm "$SLEEP_PID_FILE"
        fi
        kill -9 $(cat "$PID_FILE") 2>/dev/null
        rm "$PID_FILE"
        send_notification "⏹️ Rotation OFF" "normal"
    else
        # Turn ON
        touch "$FLAG"
        CURRENT_STATE=$(get_current_state)
        CURRENT_WS=$(echo "$CURRENT_STATE" | cut -d'|' -f1)
        CURRENT_INTV=$(echo "$CURRENT_STATE" | cut -d'|' -f2)
        send_notification "▶️ Rotation ON ($CURRENT_WS, $CURRENT_INTV)" "normal"
        
        (
            while [ -f "$FLAG" ]; do
                # Get current state
                CURRENT_STATE=$(get_current_state)
                CURRENT_WS=$(echo "$CURRENT_STATE" | cut -d'|' -f1)
                CURRENT_INTV=$(echo "$CURRENT_STATE" | cut -d'|' -f2)
                TOTAL_SLEEP=$(parse_timing "$CURRENT_INTV")
                
                # Sleep in 2-second chunks to check for workspace/interval changes
                CHUNK=2
                ELAPSED=0
                STATE_CHANGED=false
                
                while [ $ELAPSED -lt $TOTAL_SLEEP ] && [ -f "$FLAG" ]; do
                    sleep $CHUNK
                    ELAPSED=$((ELAPSED + CHUNK))
                    
                    # Check if workspace or interval changed
                    NEW_STATE=$(get_current_state)
                    NEW_WS=$(echo "$NEW_STATE" | cut -d'|' -f1)
                    NEW_INTV=$(echo "$NEW_STATE" | cut -d'|' -f2)
                    
                    if [ "$NEW_WS" != "$CURRENT_WS" ] || [ "$NEW_INTV" != "$CURRENT_INTV" ]; then
                        # Something changed - notify and restart timer
                        if [ "$NEW_WS" != "$CURRENT_WS" ]; then
                            send_notification "🔄 $NEW_WS ($NEW_INTV)" "normal"
                        else
                            send_notification "⏱️ Interval changed: $CURRENT_INTV → $NEW_INTV" "normal"
                        fi
                        STATE_CHANGED=true
                        break
                    fi
                done
                
                # If state changed, restart the loop with new timer
                if [ "$STATE_CHANGED" = true ]; then
                    continue
                fi
                
                # If we completed the full sleep and flag is still active, rotate
                if [ -f "$FLAG" ] && [ $ELAPSED -ge $TOTAL_SLEEP ]; then
                    python3 /home/ows/awp/nav.py next
                fi
            done
        ) &
        echo $! > "$PID_FILE"
    fi
    exit 0
fi

# ======================================================================
# DAEMON MODES (Universal) - Switch between full and light presets
# ======================================================================

# FULL mode (daemon.py running)
if [ "$DAEMON_MODE" == "full" ]; then
    # SWITCH TO LIGHT (stop rotation)
    LIGHT_PRESET=$(get_light_preset)
    send_notification "⏹️ Rotation OFF → Switching to $LIGHT_PRESET" "normal"
    "$AWP_DIR/awp_start.sh" "$LIGHT_PRESET"
    
# LIGHT mode (daemon-light.py running)
elif [ "$DAEMON_MODE" == "light" ]; then
    # SWITCH TO FULL (start rotation)
    BASE_PRESET=$(get_base_preset)
    send_notification "🔄 Rotation ON → Switching to $BASE_PRESET" "normal"
    "$AWP_DIR/awp_start.sh" "$BASE_PRESET"
fi
