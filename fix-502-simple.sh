#!/bin/bash

# Simple 502 fix without Python package installations
echo "🔧 Fixing 502 error - configuration only..."

cd /opt/privacy

# Stop services
systemctl stop privacy
systemctl stop nginx

# Check current logs
echo "📋 Recent error logs:"
tail -10 /opt/privacy/logs/gunicorn_error.log 2>/dev/null || echo "No logs found"

# Create simplified gunicorn config
echo "⚙️ Creating simple Gunicorn config..."
cat > gunicorn_simple.conf.py << 'EOF'
bind = "127.0.0.1:5000"
workers = 1
worker_class = "sync"
timeout = 60
keepalive = 2
max_requests = 1000
errorlog = "/opt/privacy/logs/gunicorn_error.log"
accesslog = "/opt/privacy/logs/gunicorn_access.log"
loglevel = "debug"
proc_name = "privacy_gunicorn"
daemon = False
pidfile = "/opt/privacy/logs/gunicorn.pid"
user = "privacy"
group = "privacy"
preload_app = False
EOF

# Update systemd service with absolute paths
echo "⚙️ Updating systemd service..."
cat > /etc/systemd/system/privacy.service << 'EOF'
[Unit]
Description=n.crisisops Privacy LGPD System
After=network.target postgresql.service

[Service]
Type=forking
User=privacy
Group=privacy
WorkingDirectory=/opt/privacy
Environment="PATH=/opt/privacy/venv/bin:/usr/local/bin:/usr/bin:/bin"
Environment="PYTHONPATH=/opt/privacy"
Environment="VIRTUAL_ENV=/opt/privacy/venv"
ExecStart=/opt/privacy/venv/bin/gunicorn --config /opt/privacy/gunicorn_simple.conf.py --daemon web_interface:app
ExecReload=/bin/kill -s HUP $MAINPID
PIDFile=/opt/privacy/logs/gunicorn.pid
KillMode=mixed
TimeoutStopSec=10
Restart=always
RestartSec=15

[Install]
WantedBy=multi-user.target
EOF

# Ensure proper permissions
mkdir -p /opt/privacy/logs
chown -R privacy:privacy /opt/privacy/logs
chown privacy:privacy /opt/privacy/gunicorn_simple.conf.py

# Test if app can start manually first
echo "🧪 Testing manual start..."
sudo -u privacy /opt/privacy/venv/bin/python3 -c "
import sys
sys.path.insert(0, '/opt/privacy')
from web_interface import app
print('App loads successfully')
" || echo "App load failed"

# Reload systemd and start services
systemctl daemon-reload
systemctl start privacy
sleep 5
systemctl start nginx

# Wait for startup
sleep 10

# Test connections
echo "🧪 Testing connections..."
curl -I http://localhost:5000 2>/dev/null || echo "Local connection failed"
curl -I https://monster.e-ness.com.br 2>/dev/null || echo "SSL connection failed"

# Show service status
echo "📊 Service status:"
systemctl status privacy --no-pager -l

echo "✅ Simple fix completed!"
echo "Check logs with: tail -f /opt/privacy/logs/gunicorn_error.log"