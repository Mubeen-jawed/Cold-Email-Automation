#!/bin/bash
# =============================================================================
#  VPS QUICKSTART — Cold Email Automation Dashboard
#  Run this script on Ubuntu 22.04 LTS as root to deploy everything.
#  Usage: curl -sL <your-script-url> | bash
#         or: bash deploy/vps_quickstart.sh
# =============================================================================

set -e
APP_DIR="/opt/cold-email-automation"
SERVICE="cold-email-automation"

# ── 1. System packages ────────────────────────────────────────────────────────
echo "[1/7] Installing system packages..."
apt-get update -qq

# Detect Ubuntu version to pick correct package names
UBUNTU_VERSION=$(lsb_release -rs 2>/dev/null || echo "22.04")
echo "    Detected Ubuntu $UBUNTU_VERSION"

if dpkg --compare-versions "$UBUNTU_VERSION" ge "24.00" 2>/dev/null || [ "$(echo "$UBUNTU_VERSION >= 24.00" | awk '{print ($1 >= $3)}')" = "1" ]; then
    # Ubuntu 24.04+: python3.12, libasound2t64
    PYTHON_PKG="python3.12 python3.12-venv"
    ALSA_PKG="libasound2t64"
else
    # Ubuntu 22.04 and earlier
    PYTHON_PKG="python3.11 python3.11-venv"
    ALSA_PKG="libasound2"
fi

apt-get install -y -qq \
    $PYTHON_PKG python3-pip \
    nginx git curl rsync \
    libnss3 libatk1.0-0 libatk-bridge2.0-0 libcups2 libdrm2 \
    libxkbcommon0 libxcomposite1 libxdamage1 libxfixes3 libxrandr2 \
    libgbm1 $ALSA_PKG libpango-1.0-0 libpangocairo-1.0-0 \
    libatspi2.0-0 fonts-liberation

# Resolve python3 binary
PYTHON_BIN=$(command -v python3.12 || command -v python3.11 || command -v python3)
echo "    Using Python: $PYTHON_BIN ($($PYTHON_BIN --version))"

# ── 2. Copy project files ─────────────────────────────────────────────────────
echo "[2/7] Copying project files to $APP_DIR..."
# If running from within the project dir:
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

mkdir -p "$APP_DIR"
rsync -a --exclude=venv --exclude=__pycache__ --exclude=.git \
    "$PROJECT_DIR/" "$APP_DIR/"

cd "$APP_DIR"

# ── 3. Python virtual environment ─────────────────────────────────────────────
echo "[3/7] Setting up Python virtual environment..."
$PYTHON_BIN -m venv venv
venv/bin/pip install --upgrade pip -q
venv/bin/pip install -r requirements.txt -r requirements_api.txt -q

# ── 4. Playwright Chromium ────────────────────────────────────────────────────
echo "[4/7] Installing Playwright Chromium (for scraping)..."
venv/bin/playwright install chromium
# install-deps uses legacy package names that don't exist on Ubuntu 24.04;
# all required system libs were already installed in step 1.
if dpkg --compare-versions "$UBUNTU_VERSION" lt "24.00" 2>/dev/null; then
    venv/bin/playwright install-deps chromium
fi

# ── 5. Environment file ───────────────────────────────────────────────────────
if [ ! -f "$APP_DIR/.env.production" ]; then
    echo "[5/7] Creating .env.production — EDIT THIS FILE before starting!"
    cp "$APP_DIR/.env.production.example" "$APP_DIR/.env.production"
    echo ""
    echo "  !! ACTION REQUIRED: Edit $APP_DIR/.env.production"
    echo "     Set OPENROUTER_API_KEY and any credential env vars."
    echo "     Then run: systemctl start $SERVICE"
    echo ""
else
    echo "[5/7] .env.production already exists, skipping."
fi

# ── 6. Systemd service ────────────────────────────────────────────────────────
echo "[6/7] Writing systemd service..."
cat > /etc/systemd/system/${SERVICE}.service <<EOF
[Unit]
Description=Cold Email Automation Web Dashboard
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=$APP_DIR
ExecStart=$APP_DIR/venv/bin/python api.py
Restart=on-failure
RestartSec=5
EnvironmentFile=$APP_DIR/.env.production

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable "$SERVICE"

# ── 7. Nginx ──────────────────────────────────────────────────────────────────
echo "[7/7] Configuring Nginx..."
cp "$APP_DIR/deploy/nginx.conf" /etc/nginx/sites-available/${SERVICE}
ln -sf /etc/nginx/sites-available/${SERVICE} /etc/nginx/sites-enabled/${SERVICE}
rm -f /etc/nginx/sites-enabled/default
nginx -t && systemctl restart nginx

echo ""
echo "====================================================================="
echo " DEPLOYMENT COMPLETE"
echo "====================================================================="
echo ""
echo " Next steps:"
echo ""
echo " 1. Upload your credential files to $APP_DIR:"
echo "      credentials.json"
echo "      gmail_credentials.json"
echo "      gmail_token.json"
echo ""
echo " 2. Edit the env file:"
echo "      nano $APP_DIR/.env.production"
echo "      (set OPENROUTER_API_KEY)"
echo ""
echo " 3. Start the service:"
echo "      systemctl start $SERVICE"
echo ""
echo " 4. (Optional) Set your domain in Nginx config:"
echo "      nano /etc/nginx/sites-available/$SERVICE"
echo "      (replace YOUR_DOMAIN_OR_IP)"
echo "      systemctl reload nginx"
echo ""
echo " 5. (Optional) Get free HTTPS with Let's Encrypt:"
echo "      certbot --nginx -d yourdomain.com"
echo ""
echo " View logs:   journalctl -u $SERVICE -f"
echo " Restart app: systemctl restart $SERVICE"
echo "====================================================================="
