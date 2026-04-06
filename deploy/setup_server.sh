#!/bin/bash
# Run this ONCE on a fresh Ubuntu 22.04 VPS as root
# Sets up Python, Nginx, Playwright deps, and creates the app user

set -e

echo "=== Setting up server ==="

# Update system
apt-get update && apt-get upgrade -y

# Install system packages
apt-get install -y \
    python3.11 python3.11-venv python3-pip \
    nginx certbot python3-certbot-nginx \
    git curl wget \
    libnss3 libatk1.0-0 libatk-bridge2.0-0 libcups2 libdrm2 \
    libxkbcommon0 libxcomposite1 libxdamage1 libxfixes3 libxrandr2 \
    libgbm1 libasound2 libpango-1.0-0 libpangocairo-1.0-0 \
    libatspi2.0-0 fonts-liberation

# Create app user
useradd -m -s /bin/bash appuser 2>/dev/null || echo "User appuser already exists"

echo "=== Server setup complete ==="
echo "Next: run deploy.sh as appuser"
