#!/bin/bash
# Script 1 — System Health Checker
# Checks CPU, RAM, and Disk usage with WARN/CRITICAL thresholds

CPU_WARN=70;  CPU_CRIT=90
MEM_WARN=70;  MEM_CRIT=90
DISK_WARN=80; DISK_CRIT=95

RED='\033[0;31m'; YELLOW='\033[1;33m'; GREEN='\033[0;32m'; BOLD='\033[1m'; NC='\033[0m'

print_status() {
    local val=$1 warn=$2 crit=$3 label=$4 unit=$5
    if [ "$val" -ge "$crit" ]; then
        echo -e "  ${RED}[CRITICAL]${NC} ${label}: ${val}${unit}"
    elif [ "$val" -ge "$warn" ]; then
        echo -e "  ${YELLOW}[WARN]    ${NC} ${label}: ${val}${unit}"
    else
        echo -e "  ${GREEN}[OK]      ${NC} ${label}: ${val}${unit}"
    fi
}

echo -e "${BOLD}=============================================${NC}"
echo -e "${BOLD}   System Health Check — $(date '+%Y-%m-%d %H:%M:%S')${NC}"
echo -e "${BOLD}   Host: $(hostname)${NC}"
echo -e "${BOLD}=============================================${NC}"
echo ""

# CPU usage
CPU=$(top -bn1 | grep "Cpu(s)" | awk '{print int($2)}')
print_status "$CPU" "$CPU_WARN" "$CPU_CRIT" "CPU Usage" "%"

# Memory usage
MEM=$(free | awk '/Mem:/ {printf "%d", $3/$2 * 100}')
MEM_USED=$(free -h | awk '/Mem:/ {print $3}')
MEM_TOTAL=$(free -h | awk '/Mem:/ {print $2}')
print_status "$MEM" "$MEM_WARN" "$MEM_CRIT" "RAM Usage (${MEM_USED}/${MEM_TOTAL})" "%"

echo ""
echo -e "${BOLD}  Disk Usage:${NC}"
while IFS= read -r line; do
    usage=$(echo "$line" | awk '{gsub(/%/,"",$5); print $5}')
    mount=$(echo "$line" | awk '{print $6}')
    used=$(echo "$line" | awk '{print $3}')
    total=$(echo "$line" | awk '{print $2}')
    if [ "$usage" -ge "$DISK_CRIT" ] 2>/dev/null; then
        echo -e "    ${RED}[CRITICAL]${NC} $mount — ${used}/${total} (${usage}%)"
    elif [ "$usage" -ge "$DISK_WARN" ] 2>/dev/null; then
        echo -e "    ${YELLOW}[WARN]    ${NC} $mount — ${used}/${total} (${usage}%)"
    else
        echo -e "    ${GREEN}[OK]      ${NC} $mount — ${used}/${total} (${usage}%)"
    fi
done < <(df -h | awk 'NR>1 && /^\// {print}')

echo ""
echo -e "  Uptime : $(uptime -p)"
echo -e "  Load   : $(uptime | awk -F'load average:' '{print $2}' | xargs)"
echo ""
echo -e "${BOLD}=============================================${NC}"
