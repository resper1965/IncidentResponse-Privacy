#!/bin/bash

# Recreate Gunicorn configuration from scratch
echo "🔧 Recriando configuração do Gunicorn..."

cd /opt/privacy

# Stop all services
systemctl stop privacy 2>/dev/null
systemctl stop nginx 2>/dev/null
pkill -f gunicorn 2>/dev/null

# Remove old configs and PIDs
rm -f gunicorn*.conf.py
rm -f logs/gunicorn.pid
rm -f /tmp/gunicorn.pid

# Create fresh logs directory
mkdir -p logs
chown -R privacy:privacy logs

# Create clean Gunicorn configuration
cat > gunicorn.conf.py << 'EOF'
# Gunicorn configuration for n.crisisops Privacy System
import multiprocessing

# Server socket
bind = "127.0.0.1:5000"
backlog = 2048

# Worker processes
workers = 1
worker_class = "sync"
worker_connections = 1000
timeout = 120
keepalive = 2

# Restart workers
max_requests = 500
max_requests_jitter = 50

# Logging
errorlog = "/opt/privacy/logs/gunicorn_error.log"
accesslog = "/opt/privacy/logs/gunicorn_access.log"
loglevel = "info"
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s"'

# Process naming
proc_name = "privacy_gunicorn"

# Server mechanics
daemon = False
pidfile = "/opt/privacy/logs/gunicorn.pid"
user = "privacy"
group = "privacy"
tmp_upload_dir = None

# Application
preload_app = False
reload = False
EOF

# Create clean systemd service
cat > /etc/systemd/system/privacy.service << 'EOF'
[Unit]
Description=n.crisisops Privacy LGPD System
Documentation=https://docs.gunicorn.org/
After=network.target postgresql.service
Wants=postgresql.service

[Service]
Type=notify
User=privacy
Group=privacy
RuntimeDirectory=privacy
WorkingDirectory=/opt/privacy
Environment=PATH=/opt/privacy/venv/bin
Environment=PYTHONPATH=/opt/privacy
ExecStart=/opt/privacy/venv/bin/gunicorn --config /opt/privacy/gunicorn.conf.py web_interface:app
ExecReload=/bin/kill -s HUP $MAINPID
PIDFile=/opt/privacy/logs/gunicorn.pid
KillMode=mixed
TimeoutStopSec=10
PrivateTmp=true
Restart=on-failure
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Set correct permissions
chown privacy:privacy /opt/privacy/gunicorn.conf.py
chown -R privacy:privacy /opt/privacy/logs
chmod 755 /opt/privacy
chmod 644 /opt/privacy/gunicorn.conf.py

# Test configuration syntax
echo "🧪 Testando configuração do Gunicorn..."
sudo -u privacy /opt/privacy/venv/bin/gunicorn --check-config --config /opt/privacy/gunicorn.conf.py web_interface:app

# Reload systemd
systemctl daemon-reload

# Start services
echo "🚀 Iniciando serviços..."
systemctl start privacy
sleep 10
systemctl start nginx

# Check status
echo "📊 Status dos serviços:"
systemctl status privacy --no-pager -l

# Test connections
echo "🧪 Testando conexões..."
curl -I http://localhost:5000
curl -I https://monster.e-ness.com.br

echo "✅ Configuração do Gunicorn recriada!"
echo "📋 Logs: tail -f /opt/privacy/logs/gunicorn_error.log"