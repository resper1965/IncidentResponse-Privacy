#!/bin/bash
set -e
echo "🔧 Corrigindo problemas do serviço privacy..."

# Parar serviço
systemctl stop privacy 2>/dev/null || true

cd /opt/privacy

# Corrigir ambiente virtual
if [ ! -d "venv" ]; then
    echo "📦 Criando ambiente virtual..."
    python3 -m venv venv
fi

# Instalar dependências
echo "📦 Instalando dependências..."
source venv/bin/activate
pip install --upgrade pip
pip install flask gunicorn

# Corrigir permissões
chown -R privacy:privacy /opt/privacy
chmod -R 755 /opt/privacy

# Recarregar e iniciar
systemctl daemon-reload
systemctl start privacy

sleep 5
systemctl status privacy --no-pager

echo "✅ Correção concluída!"
