#!/bin/bash

echo "🔧 Corrigindo serviço privacy existente na VPS"

# Execute na VPS como root
echo "📋 Verificando logs específicos do erro..."
journalctl -u privacy --no-pager -l -n 10

echo ""
echo "🔍 Verificando configuração do gunicorn..."
if [ ! -f "/opt/privacy/gunicorn.conf.py" ]; then
    echo "❌ gunicorn.conf.py ausente, criando..."
    cat > /opt/privacy/gunicorn.conf.py << 'EOF'
bind = "0.0.0.0:5000"
workers = 2
worker_class = "sync"
timeout = 30
keepalive = 2
user = "privacy"
group = "privacy"
EOF
    chown privacy:privacy /opt/privacy/gunicorn.conf.py
fi

echo ""
echo "🧪 Testando importação do módulo principal..."
cd /opt/privacy
source venv/bin/activate
export PYTHONPATH=/opt/privacy
python3 -c "
try:
    import web_interface
    print('✅ web_interface importado')
except Exception as e:
    print(f'❌ Erro: {e}')
    import traceback
    traceback.print_exc()
"

echo ""
echo "🔧 Simplificando configuração do serviço..."
cat > /etc/systemd/system/privacy.service << 'EOF'
[Unit]
Description=n.crisisops LGPD Compliance System
After=network.target

[Service]
Type=exec
User=privacy
Group=privacy
WorkingDirectory=/opt/privacy
Environment=PATH=/opt/privacy/venv/bin
Environment=PYTHONPATH=/opt/privacy
ExecStart=/opt/privacy/venv/bin/python3 web_interface.py
Restart=always
RestartSec=5
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

echo ""
echo "🔄 Recarregando e testando..."
systemctl daemon-reload
systemctl start privacy

echo ""
echo "📊 Status final..."
sleep 3
systemctl status privacy --no-pager -l

echo ""
echo "🧪 Teste de conectividade..."
curl -s http://localhost:5000 >/dev/null && echo "✅ Serviço responde" || echo "❌ Serviço não responde"

echo ""
echo "📋 Se ainda falhar, execute:"
echo "journalctl -u privacy -f"