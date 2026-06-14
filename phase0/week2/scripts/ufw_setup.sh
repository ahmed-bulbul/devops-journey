#!/bin/bash
# UFW baseline setup for a web server (HTTP + HTTPS + SSH)
# Run as root or with sudo

set -e

echo "=== UFW Baseline Setup ==="

# 1. Set default policies BEFORE enabling
ufw default deny incoming
ufw default allow outgoing
echo "[OK] Default policies: deny incoming, allow outgoing"

# 2. Allow SSH first (CRITICAL — do this before enable or you'll lock yourself out)
ufw allow 22/tcp comment 'SSH'
echo "[OK] SSH (22/tcp) allowed"

# 3. Rate-limit SSH to block brute force (max 6 attempts/30s per IP)
ufw limit 22/tcp
echo "[OK] SSH rate-limiting enabled"

# 4. Allow web traffic
ufw allow 80/tcp comment 'HTTP'
ufw allow 443/tcp comment 'HTTPS'
echo "[OK] HTTP/HTTPS allowed"

# 5. Allow Spring Boot app port (only from localhost — nginx proxies externally)
ufw allow from 127.0.0.1 to any port 8080 comment 'Spring Boot internal'
echo "[OK] Spring Boot port 8080 allowed from localhost only"

# 6. Enable (will prompt "y/n" interactively — skip in CI with: ufw --force enable)
echo ""
echo "=== Current rules preview ==="
ufw show added

echo ""
echo "Run: sudo ufw enable"
echo "Then verify: sudo ufw status verbose"
