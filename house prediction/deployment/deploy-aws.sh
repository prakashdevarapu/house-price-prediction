#!/usr/bin/env bash
# ==============================================================================
# AWS EC2 Automated Deployment Script for House Price Prediction
# Compatible with Amazon Linux 2023 and Ubuntu 22.04 / 24.04 LTS
# ==============================================================================

set -euo pipefail

APP_NAME="house-price-prediction"
APP_DIR="/var/www/${APP_NAME}"
LOG_DIR="/var/log/${APP_NAME}"
SYSTEMD_SERVICE_FILE="/etc/systemd/system/${APP_NAME}.service"

echo "============================================================"
echo " Starting Automated Deployment: ${APP_NAME}"
echo "============================================================"

# 1. Detect Operating System and Application User
if [ -f /etc/os-release ]; then
    . /etc/os-release
    OS_ID=$ID
else
    echo "Error: Cannot identify OS distribution."
    exit 1
fi

if [ "$OS_ID" = "amzn" ]; then
    echo "[+] Detected Amazon Linux 2023"
    APP_USER="ec2-user"
    PACKAGE_MGR="dnf"
    NGINX_CONF_DEST="/etc/nginx/conf.d/${APP_NAME}.conf"
elif [ "$OS_ID" = "ubuntu" ] || [ "$OS_ID" = "debian" ]; then
    echo "[+] Detected Ubuntu/Debian"
    APP_USER="ubuntu"
    PACKAGE_MGR="apt"
    NGINX_CONF_DEST="/etc/nginx/sites-available/${APP_NAME}"
else
    echo "Warning: Unrecognized OS ($OS_ID). Defaulting to user 'ec2-user'."
    APP_USER="ec2-user"
    PACKAGE_MGR="dnf"
    NGINX_CONF_DEST="/etc/nginx/conf.d/${APP_NAME}.conf"
fi

# 2. Update System Packages and Install Dependencies
echo "[+] Updating system packages..."
if [ "$PACKAGE_MGR" = "dnf" ]; then
    sudo dnf update -y
    sudo dnf install -y python3 python3-pip git nginx
elif [ "$PACKAGE_MGR" = "apt" ]; then
    sudo apt-get update -y
    sudo apt-get install -y python3 python3-pip python3-venv git nginx
fi

# 3. Create Dedicated Application and Log Directories
echo "[+] Setting up application directories in ${APP_DIR}..."
sudo mkdir -p "${APP_DIR}"
sudo mkdir -p "${LOG_DIR}"

# If repo not yet placed in /var/www, copy current working directory files
if [ "$(pwd)" != "${APP_DIR}" ]; then
    echo "[+] Copying code repository to ${APP_DIR}..."
    sudo cp -ru ./* "${APP_DIR}/"
fi

# 4. Create and Configure Python Virtual Environment
echo "[+] Setting up dedicated Python virtual environment..."
cd "${APP_DIR}"
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi

# Activate venv and install dependencies
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# 5. Train Model & Persist Artifacts
echo "[+] Training Linear Regression model on housing dataset..."
if [ ! -f "data/housing_data.csv" ]; then
    python data/generate_dataset.py
fi
python train_model.py

# 6. Run Automated Tests
echo "[+] Running test suite..."
python -m pytest tests/

# 7. Configure Permissions
echo "[+] Setting directory ownership for user: ${APP_USER}..."
sudo chown -R "${APP_USER}:${APP_USER}" "${APP_DIR}"
sudo chown -R "${APP_USER}:${APP_USER}" "${LOG_DIR}"

# 8. Configure Systemd Service
echo "[+] Installing systemd service..."
sudo cp "${APP_DIR}/deployment/house-price-prediction.service" "${SYSTEMD_SERVICE_FILE}"

# Update service user to match OS if necessary
sudo sed -i "s/User=ec2-user/User=${APP_USER}/g" "${SYSTEMD_SERVICE_FILE}"
sudo sed -i "s/Group=ec2-user/Group=${APP_USER}/g" "${SYSTEMD_SERVICE_FILE}"

sudo systemctl daemon-reload
sudo systemctl enable "${APP_NAME}.service"
sudo systemctl restart "${APP_NAME}.service"

# 9. Configure Nginx Reverse Proxy
echo "[+] Configuring Nginx reverse proxy..."
sudo cp "${APP_DIR}/deployment/nginx.conf" "${NGINX_CONF_DEST}"

if [ "$PACKAGE_MGR" = "apt" ]; then
    sudo ln -sf "${NGINX_CONF_DEST}" "/etc/nginx/sites-enabled/${APP_NAME}"
    # Remove default site if present
    sudo rm -f /etc/nginx/sites-enabled/default
fi

echo "[+] Testing Nginx syntax..."
sudo nginx -t

echo "[+] Restarting and enabling Nginx..."
sudo systemctl restart nginx
sudo systemctl enable nginx

# 10. Health Verification
echo "[+] Verifying application health endpoint..."
sleep 2
HEALTH_CHECK=$(curl -s http://127.0.0.1/health || true)
echo "Health Response: ${HEALTH_CHECK}"

echo "============================================================"
echo " Deployment Successfully Completed!"
echo " Visit your EC2 Public IP in a browser: http://<EC2_PUBLIC_IP>"
echo " View Service Logs: sudo journalctl -u ${APP_NAME} -f"
echo " View Gunicorn Logs: cat ${LOG_DIR}/error.log"
echo "============================================================"
