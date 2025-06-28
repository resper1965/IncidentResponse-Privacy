#!/bin/bash

# Fix 502 error on VPS by debugging and fixing all issues
echo "🔧 Investigating and fixing 502 error..."

cd /opt/privacy

# Stop services
systemctl stop privacy
systemctl stop nginx

# Check what's in the logs
echo "📋 Checking recent error logs..."
tail -20 /opt/privacy/logs/gunicorn_error.log

# Test Python imports directly
echo "🧪 Testing all critical imports..."
./venv/bin/python3 -c "
import sys
sys.path.insert(0, '/opt/privacy')
print('Testing imports...')

try:
    import fitz
    print('✅ fitz (PyMuPDF) OK')
except Exception as e:
    print(f'❌ fitz error: {e}')

try:
    from file_reader import extrair_texto
    print('✅ file_reader OK')
except Exception as e:
    print(f'❌ file_reader error: {e}')

try:
    from web_interface import app
    print('✅ web_interface OK')
except Exception as e:
    print(f'❌ web_interface error: {e}')
"

# Install any missing dependencies
echo "📦 Installing missing dependencies..."
./venv/bin/pip install PyMuPDF==1.23.8 --force-reinstall

# Test if web_interface can start
echo "🧪 Testing web interface startup..."
cd /opt/privacy
timeout 10 ./venv/bin/python3 -c "
from web_interface import app
print('Web interface can be imported')
app.run(host='127.0.0.1', port=5001, debug=False)
" &

sleep 3
kill %1 2>/dev/null

# Create a simplified Gunicorn config
echo "⚙️ Creating simplified Gunicorn config..."
cat > /opt/privacy/gunicorn_simple.conf.py << 'EOF'
import multiprocessing

# Server socket
bind = "127.0.0.1:5000"
backlog = 2048

# Worker processes
workers = 2
worker_class = "sync"
worker_connections = 1000
timeout = 30
keepalive = 2

# Restart workers after this many requests
max_requests = 1000

# Logging
errorlog = "/opt/privacy/logs/gunicorn_error.log"
accesslog = "/opt/privacy/logs/gunicorn_access.log"
loglevel = "info"

# Process naming
proc_name = "privacy_gunicorn"

# Server mechanics
daemon = False
pidfile = "/opt/privacy/logs/gunicorn.pid"
user = "privacy"
group = "privacy"

# Preload app
preload_app = True
EOF

# Update systemd service with simplified config
echo "⚙️ Updating systemd service..."
cat > /etc/systemd/system/privacy.service << 'EOF'
[Unit]
Description=n.crisisops Privacy LGPD System
After=network.target postgresql.service
Requires=postgresql.service

[Service]
Type=forking
User=privacy
Group=privacy
WorkingDirectory=/opt/privacy
Environment="PATH=/opt/privacy/venv/bin:/usr/local/bin:/usr/bin:/bin"
Environment="PYTHONPATH=/opt/privacy"
ExecStart=/opt/privacy/venv/bin/gunicorn --config gunicorn_simple.conf.py --daemon web_interface:app
ExecReload=/bin/kill -s HUP $MAINPID
PIDFile=/opt/privacy/logs/gunicorn.pid
KillMode=mixed
TimeoutStopSec=5
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Create a simple test to verify the app works
echo "🧪 Creating app test script..."
cat > /opt/privacy/test_app.py << 'EOF'
#!/usr/bin/env python3
import os
import sys
sys.path.insert(0, '/opt/privacy')

try:
    from web_interface import app
    print("✅ App imported successfully")
    
    # Test a simple route
    with app.test_client() as client:
        response = client.get('/')
        print(f"✅ Home route status: {response.status_code}")
        
except Exception as e:
    print(f"❌ App test failed: {e}")
    import traceback
    traceback.print_exc()
EOF

chmod +x /opt/privacy/test_app.py

# Run the test
echo "🧪 Testing app directly..."
chown privacy:privacy /opt/privacy/test_app.py
sudo -u privacy /opt/privacy/venv/bin/python3 /opt/privacy/test_app.py

# Deactivate virtual environment if active
deactivate 2>/dev/null || true

# Reload and start services
systemctl daemon-reload
systemctl start privacy
systemctl start nginx

# Wait and test
sleep 10

echo "🧪 Testing after restart..."
curl -I http://localhost:5000
curl -I https://monster.e-ness.com.br

echo "📋 Checking service status..."
systemctl status privacy --no-pager

echo "✅ 502 fix completed!"