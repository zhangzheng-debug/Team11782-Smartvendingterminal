#!/usr/bin/env bash
set -euo pipefail

# Run on the new Ubuntu payment node after copying the service files.
# This script does not create an AWS instance and does not touch the board.

APP_DIR="${APP_DIR:-/opt/qsm-payment}"
SERVICE_USER="${SERVICE_USER:-qsm-payment}"
PORT="${PORT:-8000}"

sudo apt-get update
sudo apt-get install -y python3 python3-venv python3-pip ufw curl

if ! id "${SERVICE_USER}" >/dev/null 2>&1; then
  sudo useradd --system --home "${APP_DIR}" --shell /usr/sbin/nologin "${SERVICE_USER}"
fi

sudo mkdir -p "${APP_DIR}"
sudo chown -R "${SERVICE_USER}:${SERVICE_USER}" "${APP_DIR}"

if [ ! -d "${APP_DIR}/.venv" ]; then
  sudo -u "${SERVICE_USER}" python3 -m venv "${APP_DIR}/.venv"
fi

if [ -f "${APP_DIR}/requirements.txt" ]; then
  sudo -u "${SERVICE_USER}" "${APP_DIR}/.venv/bin/pip" install -r "${APP_DIR}/requirements.txt"
else
  sudo -u "${SERVICE_USER}" "${APP_DIR}/.venv/bin/pip" install Flask gunicorn
fi

sudo tee /etc/systemd/system/qsm-payment.service >/dev/null <<EOF
[Unit]
Description=QSM368ZP Smart Retail Demo Payment Service
After=network-online.target
Wants=network-online.target

[Service]
User=${SERVICE_USER}
WorkingDirectory=${APP_DIR}
Environment=PORT=${PORT}
Environment=PYTHONUNBUFFERED=1
ExecStartPre=${APP_DIR}/.venv/bin/python -c "from app import init_db; init_db()"
ExecStart=${APP_DIR}/.venv/bin/gunicorn --workers 1 --threads 4 --bind 0.0.0.0:${PORT} --access-logfile - --error-logfile - app:app
Restart=on-failure
RestartSec=2
NoNewPrivileges=true
PrivateTmp=true

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl enable qsm-payment.service
sudo systemctl restart qsm-payment.service
sudo ufw allow OpenSSH
sudo ufw allow "${PORT}/tcp"
sudo ufw --force enable

curl --fail --retry 6 --retry-connrefused --retry-delay 1 --max-time 8 "http://127.0.0.1:${PORT}/health"
echo
echo "Payment service is ready on port ${PORT}."
echo "For production-like use, put HTTPS Caddy/Nginx in front before exposing payment URLs."
