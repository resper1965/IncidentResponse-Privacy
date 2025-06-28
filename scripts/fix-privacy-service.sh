#!/bin/bash
# Script para corrigir problemas do serviço privacy
# Execute como root no VPS

set -e

echo "🔧 Corrigindo problemas do serviço privacy..."

# 1. Parar o serviço
systemctl stop privacy

# 2. Corrigir ambiente virtual se necessário
if [ ! -d "/opt/privacy/venv" ]; then
    echo "📦 Criando ambiente virtual..."
    cd /opt/privacy
    python3 -m venv venv
    source venv/bin/activate
    pip install --upgrade pip
    pip install flask gunicorn
fi

# 3. Corrigir permissões
chown -R privacy:privacy /opt/privacy
chmod -R 755 /opt/privacy
chmod +x /opt/privacy/venv/bin/gunicorn

# 4. Recarregar e iniciar
systemctl daemon-reload
systemctl start privacy

# 5. Verificar
sleep 5
systemctl status privacy
curl -f http://localhost:5000/health && echo "✅ Serviço funcionando!" || echo "❌ Problema persistente"

echo "✅ Correção concluída!"
