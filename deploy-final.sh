#!/bin/bash

# Final deployment script for n.crisisops Privacy LGPD System
echo "🚀 Deploying n.crisisops Privacy System..."

cd /opt/privacy

# Stop services
systemctl stop privacy 2>/dev/null
systemctl stop nginx 2>/dev/null
pkill -f gunicorn 2>/dev/null

# Install missing Python packages
echo "📦 Installing required packages..."
source venv/bin/activate
pip install PyMuPDF==1.23.8 --quiet
deactivate

# Clean old configurations
rm -f gunicorn*.conf.py
rm -f logs/gunicorn.pid
mkdir -p logs

# Create Gunicorn configuration
cat > gunicorn.conf.py << 'EOF'
bind = "127.0.0.1:5000"
workers = 1
worker_class = "sync"
timeout = 120
keepalive = 2
max_requests = 500
errorlog = "/opt/privacy/logs/gunicorn_error.log"
accesslog = "/opt/privacy/logs/gunicorn_access.log"
loglevel = "info"
proc_name = "privacy_gunicorn"
daemon = False
pidfile = "/opt/privacy/logs/gunicorn.pid"
user = "privacy"
group = "privacy"
preload_app = False
EOF

# Create systemd service
cat > /etc/systemd/system/privacy.service << 'EOF'
[Unit]
Description=n.crisisops Privacy LGPD System
After=network.target postgresql.service

[Service]
Type=notify
User=privacy
Group=privacy
WorkingDirectory=/opt/privacy
Environment=PATH=/opt/privacy/venv/bin
Environment=PYTHONPATH=/opt/privacy
ExecStart=/opt/privacy/venv/bin/gunicorn --config /opt/privacy/gunicorn.conf.py web_interface:app
PIDFile=/opt/privacy/logs/gunicorn.pid
Restart=on-failure
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Set permissions
chown -R privacy:privacy /opt/privacy
chmod 644 /opt/privacy/gunicorn.conf.py

# Test Python imports
echo "🧪 Testing imports..."
sudo -u privacy /opt/privacy/venv/bin/python3 -c "
import sys
sys.path.insert(0, '/opt/privacy')
import fitz
from web_interface import app
print('✅ All imports successful')
"

# Start services
systemctl daemon-reload
systemctl enable privacy
systemctl start privacy
sleep 10
systemctl start nginx

# Test deployment
echo "🧪 Testing deployment..."
curl -I http://localhost:5000
curl -I https://monster.e-ness.com.br

# Show status
systemctl status privacy --no-pager -l

echo "✅ Deployment completed!"
echo "🌐 Access: https://monster.e-ness.com.br"
echo "📋 Logs: tail -f /opt/privacy/logs/gunicorn_error.log"