#!/bin/bash

# =============================================================================
# Script de Correção Rápida - Erro 502
# n.crisisops - Sistema LGPD
# =============================================================================

echo "🔧 Corrigindo problema do serviço privacy..."

# Parar serviço atual
systemctl stop privacy

# Criar configuração Gunicorn mais simples
echo "⚙️ Corrigindo configuração Gunicorn..."
cat > /opt/privacy/gunicorn.conf.py << 'EOF'
# Configuração simplificada para n.crisisops
bind = "0.0.0.0:5000"
workers = 1
worker_class = "sync"
timeout = 120
keepalive = 2
preload_app = False
reload = False
daemon = False
pidfile = "/opt/privacy/gunicorn.pid"
accesslog = "/opt/privacy/logs/gunicorn_access.log"
errorlog = "/opt/privacy/logs/gunicorn_error.log"
loglevel = "debug"
capture_output = True
EOF

# Corrigir serviço systemd
echo "🔧 Corrigindo serviço systemd..."
cat > /etc/systemd/system/privacy.service << 'EOF'
[Unit]
Description=n.crisisops LGPD Compliance System
After=network.target postgresql.service
Wants=postgresql.service

[Service]
Type=exec
User=privacy
Group=privacy
WorkingDirectory=/opt/privacy/app
Environment=PATH=/opt/privacy/venv/bin:/usr/local/bin:/usr/bin:/bin
Environment=DATABASE_URL=postgresql://privacy:ncrisisops_secure_2025@localhost:5432/privacy
ExecStart=/opt/privacy/venv/bin/gunicorn --config /opt/privacy/gunicorn.conf.py web_interface:app
ExecReload=/bin/kill -s HUP $MAINPID
RestartSec=5
Restart=always
StandardOutput=journal
StandardError=journal
SyslogIdentifier=privacy

[Install]
WantedBy=multi-user.target
EOF

# Garantir permissões corretas
echo "🔐 Corrigindo permissões..."
chown -R privacy:privacy /opt/privacy
chmod +x /opt/privacy/venv/bin/*
chmod 644 /opt/privacy/gunicorn.conf.py

# Testar importação Python antes de iniciar
echo "🐍 Testando importação..."
cd /opt/privacy/app
sudo -u privacy /opt/privacy/venv/bin/python -c "
import sys
sys.path.insert(0, '/opt/privacy/app')
try:
    import web_interface
    print('✅ Importação web_interface OK')
    app = getattr(web_interface, 'app', None)
    if app:
        print('✅ Flask app encontrada')
    else:
        print('❌ Flask app não encontrada')
except Exception as e:
    print(f'❌ Erro na importação: {e}')
    import traceback
    traceback.print_exc()
"

# Recarregar e iniciar
echo "🔄 Recarregando systemd..."
systemctl daemon-reload
systemctl enable privacy

echo "🚀 Iniciando serviço..."
systemctl start privacy

# Aguardar e verificar
sleep 10

if systemctl is-active --quiet privacy; then
    echo "✅ Serviço ativo"
    
    # Testar health check
    if curl -s http://localhost:5000/health > /dev/null 2>&1; then
        echo "✅ Health check OK"
        echo "🌍 Testando acesso externo..."
        curl -I http://monster.e-ness.com.br/health 2>/dev/null | head -1
    else
        echo "❌ Health check falhou"
    fi
else
    echo "❌ Serviço falhou - verificando logs..."
    journalctl -u privacy --no-pager -n 10
    
    echo ""
    echo "🔍 Testando Gunicorn manualmente..."
    cd /opt/privacy/app
    timeout 15s sudo -u privacy /opt/privacy/venv/bin/gunicorn --bind 0.0.0.0:5001 web_interface:app
fi

echo ""
echo "📊 Status final:"
systemctl status privacy --no-pager -l