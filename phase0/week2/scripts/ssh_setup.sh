#!/bin/bash
# SSH key setup helper — run on your LOCAL machine

set -e

KEY_TYPE="ed25519"      # modern, smaller, faster than rsa
KEY_FILE="$HOME/.ssh/id_${KEY_TYPE}"
COMMENT="bulbul@devops-$(date +%Y%m%d)"

echo "=== SSH Key Setup ==="

# 1. Generate key pair if it doesn't exist
if [ -f "$KEY_FILE" ]; then
    echo "[SKIP] Key already exists: $KEY_FILE"
else
    echo "[INFO] Generating $KEY_TYPE key..."
    ssh-keygen -t "$KEY_TYPE" -C "$COMMENT" -f "$KEY_FILE" -N ""
    echo "[OK]   Key created: $KEY_FILE"
fi

# 2. Show public key (copy this to server's authorized_keys)
echo ""
echo "=== Your Public Key (copy this to the server) ==="
cat "${KEY_FILE}.pub"

# 3. Ensure correct permissions
chmod 700 "$HOME/.ssh"
chmod 600 "$KEY_FILE"
chmod 644 "${KEY_FILE}.pub"
echo ""
echo "[OK] Permissions set correctly"

# 4. Reminder — how to copy key to a server
echo ""
echo "=== Copy key to server ==="
echo "ssh-copy-id -i ${KEY_FILE}.pub user@SERVER_IP"
echo "# or manually:"
echo "cat ${KEY_FILE}.pub | ssh user@SERVER_IP 'mkdir -p ~/.ssh && cat >> ~/.ssh/authorized_keys'"
