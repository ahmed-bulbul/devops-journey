#!/bin/bash
# Script 4 — User Creation Wizard
# Usage: sudo ./create_user.sh
# Creates a Linux user interactively with validation

RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'; BOLD='\033[1m'; NC='\033[0m'

ok()   { echo -e "  ${GREEN}[OK]${NC}   $*"; }
warn() { echo -e "  ${YELLOW}[WARN]${NC} $*"; }
err()  { echo -e "  ${RED}[ERROR]${NC} $*"; }

if [ "$EUID" -ne 0 ]; then
    err "This script must be run as root: sudo $0"
    exit 1
fi

echo -e "${BOLD}=============================================${NC}"
echo -e "${BOLD}         User Creation Wizard${NC}"
echo -e "${BOLD}=============================================${NC}"
echo ""

# ── Username ─────────────────────────────────────
while true; do
    read -rp "  Username: " USERNAME
    if [ -z "$USERNAME" ]; then
        err "Username cannot be empty."
    elif id "$USERNAME" &>/dev/null; then
        err "User '$USERNAME' already exists."
    elif [[ ! "$USERNAME" =~ ^[a-z][a-z0-9_-]{2,19}$ ]]; then
        err "Must be 3–20 chars, start with a letter, only lowercase/digits/-/_"
    else
        break
    fi
done

# ── Full name ─────────────────────────────────────
read -rp "  Full name [${USERNAME}]: " FULLNAME
FULLNAME="${FULLNAME:-$USERNAME}"

# ── Shell ─────────────────────────────────────────
echo "  Available shells:"
grep -E "^/(bin|usr/bin)/(bash|sh|zsh|fish)$" /etc/shells 2>/dev/null | sed 's/^/    /'
read -rp "  Shell [/bin/bash]: " USER_SHELL
USER_SHELL="${USER_SHELL:-/bin/bash}"
if [ ! -x "$USER_SHELL" ]; then
    warn "Shell '$USER_SHELL' not found — defaulting to /bin/bash"
    USER_SHELL="/bin/bash"
fi

# ── Additional groups ─────────────────────────────
echo "  Available groups (common): sudo, docker, www-data, adm"
read -rp "  Additional groups (comma-separated) [none]: " GROUPS_INPUT

# ── Password ──────────────────────────────────────
echo ""
while true; do
    read -rsp "  Password: " PASSWORD; echo
    if [ ${#PASSWORD} -lt 8 ]; then
        err "Password must be at least 8 characters."
        continue
    fi
    read -rsp "  Confirm password: " PASSWORD2; echo
    if [ "$PASSWORD" = "$PASSWORD2" ]; then
        break
    fi
    err "Passwords do not match. Try again."
done

# ── Confirm ───────────────────────────────────────
echo ""
echo -e "${BOLD}  Review:${NC}"
echo "    Username : $USERNAME"
echo "    Full name: $FULLNAME"
echo "    Shell    : $USER_SHELL"
echo "    Groups   : ${GROUPS_INPUT:-none}"
echo ""
read -rp "  Create this user? [y/N]: " CONFIRM
if [[ ! "$CONFIRM" =~ ^[Yy]$ ]]; then
    echo "  Aborted."
    exit 0
fi

# ── Create ────────────────────────────────────────
echo ""
useradd -m -s "$USER_SHELL" -c "$FULLNAME" "$USERNAME"
echo "$USERNAME:$PASSWORD" | chpasswd
ok "User '$USERNAME' created (home: /home/$USERNAME)"

# ── Add to groups ─────────────────────────────────
if [ -n "$GROUPS_INPUT" ]; then
    IFS=',' read -ra GROUPS_ARR <<< "$GROUPS_INPUT"
    for grp in "${GROUPS_ARR[@]}"; do
        grp=$(echo "$grp" | tr -d ' ')
        if getent group "$grp" &>/dev/null; then
            usermod -aG "$grp" "$USERNAME"
            ok "Added to group: $grp"
        else
            warn "Group '$grp' does not exist — skipped"
        fi
    done
fi

# ── Force password change on first login ──────────
chage -d 0 "$USERNAME"
ok "User must change password on first login"

echo ""
echo -e "${BOLD}=============================================${NC}"
echo -e "${BOLD}  Summary${NC}"
echo -e "${BOLD}=============================================${NC}"
id "$USERNAME"
echo "  Home   : /home/$USERNAME"
echo "  Shell  : $USER_SHELL"
echo "  Passwd : $(chage -l "$USERNAME" | grep "Last password change")"
echo -e "${BOLD}=============================================${NC}"
