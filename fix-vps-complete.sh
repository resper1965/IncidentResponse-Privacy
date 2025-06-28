#!/bin/bash

# Complete VPS fix with proper virtual environment management
echo "Fixing VPS deployment completely..."

cd /opt/privacy

# Stop services
systemctl stop privacy
systemctl stop nginx

# Activate virtual environment properly
source venv/bin/activate

# Install missing dependencies in correct environment
echo "Installing PyMuPDF in virtual environment..."
pip install PyMuPDF==1.23.8 --force-reinstall

# Test all imports
echo "Testing critical imports..."
python3 -c "
import sys
print(f'Python executable: {sys.executable}')
try:
    import fitz
    print('PyMuPDF: OK')
except Exception as e:
    print(f'PyMuPDF error: {e}')

try:
    from file_reader import extrair_texto
    print('file_reader: OK')
except Exception as e:
    print(f'file_reader error: {e}')

try:
    from web_interface import app
    print('web_interface: OK')
except Exception as e:
    print(f'web_interface error: {e}')
"

# Deactivate virtual environment
deactivate

# Create simplified gunicorn config
cat > gunicorn_simple.conf.py << 'EOF'
bind = "127.0.0.1:5000"
workers = 2
worker_class = "sync"
timeout = 30
keepalive = 2
max_requests = 1000
errorlog = "/opt/privacy/logs/gunicorn_error.log"
accesslog = "/opt/privacy/logs/gunicorn_access.log"
loglevel = "info"
proc_name = "privacy_gunicorn"
daemon = False
pidfile = "/opt/privacy/logs/gunicorn.pid"
user = "privacy"
group = "privacy"
preload_app = True
EOF

# Update systemd service
cat > /etc/systemd/system/privacy.service << 'EOF'
[Unit]
Description=n.crisisops Privacy LGPD System
After=network.target postgresql.service

[Service]
Type=forking
User=privacy
Group=privacy
WorkingDirectory=/opt/privacy
Environment="PATH=/opt/privacy/venv/bin"
Environment="PYTHONPATH=/opt/privacy"
ExecStart=/opt/privacy/venv/bin/gunicorn --config gunicorn_simple.conf.py --daemon web_interface:app
ExecReload=/bin/kill -s HUP $MAINPID
PIDFile=/opt/privacy/logs/gunicorn.pid
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Create logs directory and set permissions
mkdir -p logs
chown -R privacy:privacy /opt/privacy/logs
chown -R privacy:privacy /opt/privacy

# Reload and start services
systemctl daemon-reload
systemctl start privacy
systemctl start nginx

# Wait for startup
sleep 10

# Test local connection
echo "Testing local connection..."
curl -I http://localhost:5000

# Test SSL connection
echo "Testing SSL connection..."
curl -I https://monster.e-ness.com.br

# Show service status
systemctl status privacy --no-pager

echo "VPS fix completed!"