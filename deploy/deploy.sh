#!/bin/bash
# Run this from your VPS to deploy/update the app.
# Usage: bash deploy.sh /path/to/your/project
# Or just cd into the project folder and run: bash deploy/deploy.sh

set -e

APP_DIR="${1:-$(pwd)}"
VENV_DIR="$APP_DIR/venv"
SERVICE_NAME="cold-email-automation"

echo "=== Deploying Cold Email Automation ==="
echo "App directory: $APP_DIR"

cd "$APP_DIR"

# Create or update virtual environment
if [ ! -d "$VENV_DIR" ]; then
    echo "Creating virtual environment..."
    python3.11 -m venv "$VENV_DIR"
fi

# Install dependencies
echo "Installing Python dependencies..."
"$VENV_DIR/bin/pip" install --upgrade pip -q
"$VENV_DIR/bin/pip" install -r requirements.txt -r requirements_api.txt -q

# Install Playwright Chromium
echo "Installing Playwright Chromium browser..."
"$VENV_DIR/bin/playwright" install chromium
"$VENV_DIR/bin/playwright" install-deps chromium

# Write systemd service
echo "Writing systemd service..."
sudo tee /etc/systemd/system/${SERVICE_NAME}.service > /dev/null <<EOF
[Unit]
Description=Cold Email Automation Web App
After=network.target

[Service]
Type=simple
User=$(whoami)
WorkingDirectory=$APP_DIR
ExecStart=$VENV_DIR/bin/python api.py
Restart=on-failure
RestartSec=5
EnvironmentFile=$APP_DIR/.env.production

[Install]
WantedBy=multi-user.target
EOF

# Enable and (re)start service
sudo systemctl daemon-reload
sudo systemctl enable "$SERVICE_NAME"
sudo systemctl restart "$SERVICE_NAME"

echo ""
echo "=== Deployment complete ==="
echo "Service status:"
sudo systemctl status "$SERVICE_NAME" --no-pager -l
echo ""
echo "App is running on http://localhost:8000"
echo "Check logs with: sudo journalctl -u $SERVICE_NAME -f"
