#!/bin/bash
# Script 5 — Spring Boot App Manager
# Usage: ./springboot_manager.sh <app-name> {start|stop|status|restart|logs}
#
# App names map to directories under ../apps/:
#   user-service   → port 8080
#   order-service  → port 8081
#   product-service→ port 8082

APPS_DIR="$(dirname "$0")/../apps"
APPS_DIR=$(realpath "$APPS_DIR")

RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'; BOLD='\033[1m'; NC='\033[0m'

declare -A APP_PORTS=(
    ["user-service"]=8080
    ["order-service"]=8081
    ["product-service"]=8082
)

usage() {
    echo ""
    echo -e "${BOLD}Usage:${NC} $0 <app-name> {start|stop|status|restart|logs}"
    echo ""
    echo "  Apps:"
    for app in "${!APP_PORTS[@]}"; do
        echo "    $app  (port ${APP_PORTS[$app]})"
    done
    echo ""
    echo "  Examples:"
    echo "    $0 user-service start"
    echo "    $0 order-service status"
    echo "    $0 product-service logs"
    echo "    $0 all status"
    echo ""
    exit 1
}

APP_NAME="$1"
COMMAND="$2"

[ -z "$APP_NAME" ] || [ -z "$COMMAND" ] && usage

resolve_app() {
    local name="$1"
    APP_DIR="${APPS_DIR}/${name}"
    JAR_FILE="${APP_DIR}/app.jar"
    PID_FILE="${APP_DIR}/app.pid"
    LOG_FILE="${APP_DIR}/app.log"
    APP_PORT="${APP_PORTS[$name]}"
}

is_running() {
    [ -f "$PID_FILE" ] && kill -0 "$(cat "$PID_FILE")" 2>/dev/null
}

cmd_start() {
    local name="$1"
    resolve_app "$name"

    if [ -z "$APP_PORT" ]; then
        echo -e "  ${RED}[ERROR]${NC} Unknown app: $name"
        return 1
    fi

    if [ ! -f "$JAR_FILE" ]; then
        echo -e "  ${RED}[ERROR]${NC} JAR not found: $JAR_FILE"
        return 1
    fi

    if is_running; then
        echo -e "  ${YELLOW}[WARN]${NC}  $name is already running (PID $(cat "$PID_FILE"))"
        return 0
    fi

    echo -e "  ${BOLD}[START]${NC} $name on port $APP_PORT..."
    nohup java -jar "$JAR_FILE" \
        --server.port="$APP_PORT" \
        --spring.profiles.active=dev \
        > "$LOG_FILE" 2>&1 &
    echo $! > "$PID_FILE"

    # Wait up to 10s for process to stay alive
    for i in $(seq 1 5); do
        sleep 2
        if is_running; then
            echo -e "  ${GREEN}[OK]${NC}    $name started (PID $(cat "$PID_FILE"), port $APP_PORT)"
            return 0
        fi
    done

    echo -e "  ${RED}[ERROR]${NC} $name failed to start — check: $LOG_FILE"
    rm -f "$PID_FILE"
    return 1
}

cmd_stop() {
    local name="$1"
    resolve_app "$name"

    if ! is_running; then
        echo -e "  ${YELLOW}[WARN]${NC}  $name is not running"
        [ -f "$PID_FILE" ] && rm -f "$PID_FILE"
        return 0
    fi

    PID=$(cat "$PID_FILE")
    echo -e "  ${BOLD}[STOP]${NC}  $name (PID $PID)..."
    kill "$PID"

    for i in $(seq 1 5); do
        sleep 1
        if ! kill -0 "$PID" 2>/dev/null; then
            rm -f "$PID_FILE"
            echo -e "  ${GREEN}[OK]${NC}    $name stopped."
            return 0
        fi
    done

    echo -e "  ${YELLOW}[WARN]${NC}  Graceful stop timed out — force killing..."
    kill -9 "$PID" 2>/dev/null
    rm -f "$PID_FILE"
    echo -e "  ${GREEN}[OK]${NC}    $name force stopped."
}

cmd_status() {
    local name="$1"
    resolve_app "$name"

    printf "  %-18s" "$name"
    if is_running; then
        PID=$(cat "$PID_FILE")
        UPTIME=$(ps -p "$PID" -o etime= 2>/dev/null | tr -d ' ')
        MEM=$(ps -p "$PID" -o rss= 2>/dev/null | awk '{printf "%.0f MB", $1/1024}')
        PORT_OPEN=$(ss -tlnp 2>/dev/null | grep ":${APP_PORT}" | wc -l)
        PORT_STATUS="(port $APP_PORT"
        [ "$PORT_OPEN" -gt 0 ] && PORT_STATUS="${PORT_STATUS} LISTENING)" || PORT_STATUS="${PORT_STATUS} not yet open)"
        echo -e "${GREEN}RUNNING${NC}   PID=$PID  up=$UPTIME  mem=$MEM  $PORT_STATUS"
    else
        echo -e "${RED}STOPPED${NC}"
        [ -f "$PID_FILE" ] && rm -f "$PID_FILE"
    fi
}

cmd_logs() {
    local name="$1"
    resolve_app "$name"

    if [ ! -f "$LOG_FILE" ]; then
        echo -e "  ${YELLOW}[WARN]${NC} No log file found: $LOG_FILE"
        return 0
    fi

    echo -e "${BOLD}--- $name — last 50 lines ($LOG_FILE) ---${NC}"
    tail -50 "$LOG_FILE"
}

# ── Handle "all" shortcut ─────────────────────────────────────────────────────
if [ "$APP_NAME" = "all" ]; then
    echo ""
    echo -e "${BOLD}=============================================${NC}"
    echo -e "${BOLD}  Spring Boot Service Manager — ALL APPS${NC}"
    echo -e "${BOLD}=============================================${NC}"
    for app in user-service order-service product-service; do
        case "$COMMAND" in
            start)   cmd_start "$app" ;;
            stop)    cmd_stop "$app" ;;
            status)  cmd_status "$app" ;;
            restart) cmd_stop "$app"; cmd_start "$app" ;;
            *) echo "  'all' supports: start|stop|status|restart" ; exit 1 ;;
        esac
    done
    echo -e "${BOLD}=============================================${NC}"
    exit 0
fi

# ── Single app ────────────────────────────────────────────────────────────────
if [ ! -d "${APPS_DIR}/${APP_NAME}" ]; then
    echo -e "${RED}[ERROR]${NC} App not found: $APP_NAME"
    usage
fi

echo ""
echo -e "${BOLD}=============================================${NC}"
echo -e "${BOLD}  Spring Boot Manager — $APP_NAME${NC}"
echo -e "${BOLD}=============================================${NC}"

case "$COMMAND" in
    start)   cmd_start "$APP_NAME" ;;
    stop)    cmd_stop "$APP_NAME" ;;
    status)  cmd_status "$APP_NAME" ;;
    restart) cmd_stop "$APP_NAME"; sleep 1; cmd_start "$APP_NAME" ;;
    logs)    cmd_logs "$APP_NAME" ;;
    *)       usage ;;
esac

echo -e "${BOLD}=============================================${NC}"
echo ""
