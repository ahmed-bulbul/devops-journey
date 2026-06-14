#!/bin/bash
# Deploy nginx as reverse proxy for a Spring Boot app
# Run as root or with sudo

set -e

APP_PORT=8080
SITE_NAME="springboot-proxy"
SITE_CONFIG="/etc/nginx/sites-available/${SITE_NAME}"
SITE_ENABLED="/etc/nginx/sites-enabled/${SITE_NAME}"
HTML_DIR="/var/www/html"

echo "=== nginx Reverse Proxy Deploy ==="

# 1. Install nginx if not present
if ! command -v nginx &>/dev/null; then
    echo "[INFO] Installing nginx..."
    apt update -q && apt install -y nginx
    echo "[OK]   nginx installed"
else
    echo "[SKIP] nginx already installed: $(nginx -v 2>&1)"
fi

# 2. Create static site content
echo "[INFO] Deploying static index.html..."
cp "$(dirname "$0")/../nginx/html/index.html" "$HTML_DIR/index.html"
echo "[OK]   index.html deployed to $HTML_DIR"

# 3. Deploy reverse proxy config
echo "[INFO] Deploying nginx site config..."
cp "$(dirname "$0")/../nginx/sites-available/springboot-proxy" "$SITE_CONFIG"

# Enable the site
if [ ! -L "$SITE_ENABLED" ]; then
    ln -s "$SITE_CONFIG" "$SITE_ENABLED"
    echo "[OK]   Site enabled"
fi

# Disable default site to avoid conflict
if [ -L "/etc/nginx/sites-enabled/default" ]; then
    rm /etc/nginx/sites-enabled/default
    echo "[OK]   Default site disabled"
fi

# 4. Test and reload
echo "[INFO] Testing nginx config..."
nginx -t
echo "[INFO] Reloading nginx..."
systemctl reload nginx
echo "[OK]   nginx reloaded"

# 5. Status check
echo ""
echo "=== nginx Status ==="
systemctl is-active nginx && echo "nginx: RUNNING" || echo "nginx: NOT RUNNING"

echo ""
echo "=== Test endpoints ==="
echo "curl http://localhost/             # static page"
echo "curl http://localhost/nginx-health # health check"
echo "curl http://localhost/api/users    # proxied to Spring Boot :${APP_PORT}"
