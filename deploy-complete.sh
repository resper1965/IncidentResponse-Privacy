#!/bin/bash

# Complete deployment solution for n.crisisops Privacy System
echo "🚀 Complete deployment solution..."

cd /opt/privacy

# Stop all services
systemctl stop privacy
systemctl stop nginx
pkill -f gunicorn
pkill -f nginx

# Install missing Python packages
echo "📦 Installing missing packages..."
source venv/bin/activate
pip install PyMuPDF==1.23.8 asyncpg psycopg2-binary --quiet
deactivate

# Test all imports
echo "🧪 Testing all imports..."
sudo -u privacy /opt/privacy/venv/bin/python3 -c "
import sys
sys.path.insert(0, '/opt/privacy')
try:
    import fitz
    print('✅ PyMuPDF: OK')
except Exception as e:
    print(f'❌ PyMuPDF: {e}')

try:
    import asyncpg
    print('✅ asyncpg: OK')
except Exception as e:
    print(f'❌ asyncpg: {e}')

try:
    import psycopg2
    print('✅ psycopg2: OK')
except Exception as e:
    print(f'❌ psycopg2: {e}')

try:
    from web_interface import app
    print('✅ web_interface: OK')
except Exception as e:
    print(f'❌ web_interface: {e}')
"

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

# Fix Nginx conflicts
echo "🔧 Fixing Nginx conflicts..."
rm -f /etc/nginx/sites-enabled/*

cat > /etc/nginx/sites-available/privacy << 'EOF'
server {
    listen 80;
    server_name monster.e-ness.com.br;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name monster.e-ness.com.br;

    ssl_certificate /etc/letsencrypt/live/monster.e-ness.com.br/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/monster.e-ness.com.br/privkey.pem;

    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;

    client_max_body_size 100M;
    
    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }
}
EOF

# Enable only our site
ln -sf /etc/nginx/sites-available/privacy /etc/nginx/sites-enabled/

# Set permissions
chown -R privacy:privacy /opt/privacy
chmod 644 /opt/privacy/gunicorn.conf.py

# Test Nginx configuration
nginx -t

if [ $? -eq 0 ]; then
    echo "✅ Nginx configuration valid"
else
    echo "❌ Nginx configuration error"
    exit 1
fi

# Start services
systemctl daemon-reload
systemctl enable privacy
systemctl start privacy
sleep 15
systemctl start nginx

# Test deployment
echo "🧪 Testing complete deployment..."
curl -I http://localhost:5000
echo ""
curl -I https://monster.e-ness.com.br

# Show final status
echo "📊 Final status:"
systemctl status privacy --no-pager -l
systemctl status nginx --no-pager -l

echo "✅ Complete deployment finished!"
echo "🌐 Access: https://monster.e-ness.com.br"
echo "📋 Logs: tail -f /opt/privacy/logs/gunicorn_error.log"