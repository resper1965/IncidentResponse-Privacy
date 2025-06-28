#!/bin/bash

# Script de atualização do aplicativo LGPD - apenas código
# Para usar em VPS que já tem o sistema instalado

set -e

echo "🔄 Atualizando Sistema LGPD n.crisisops"
echo "======================================="

# Verificar se está no diretório correto
if [ ! -f "web_interface.py" ]; then
    echo "❌ Execute este script no diretório da aplicação (/opt/privacy)"
    exit 1
fi

# Parar o serviço
echo "⏹️ Parando serviço..."
systemctl stop privacy || true

# Fazer backup dos arquivos principais
echo "💾 Criando backup..."
mkdir -p backups/$(date +%Y%m%d_%H%M%S)
cp web_interface.py backups/$(date +%Y%m%d_%H%M%S)/ || true
cp database.py backups/$(date +%Y%m%d_%H%M%S)/ || true
cp .env backups/$(date +%Y%m%d_%H%M%S)/ || true

# Atualizar código do Git
echo "📥 Baixando atualizações..."
git pull origin main || echo "⚠️ Erro no git pull, continuando..."

# Atualizar dependências se necessário
echo "📦 Verificando dependências..."
./venv/bin/pip install --upgrade flask gunicorn psycopg2-binary

# Recarregar configurações
echo "⚙️ Recarregando configurações..."
systemctl daemon-reload

# Iniciar serviço
echo "🚀 Iniciando serviço..."
systemctl start privacy

# Verificar status
echo "🔍 Verificando status..."
sleep 3
systemctl status privacy --no-pager -l

# Testar se está funcionando
echo "🧪 Testando aplicação..."
if curl -f http://localhost:5000 > /dev/null 2>&1; then
    echo "✅ Aplicação funcionando corretamente!"
else
    echo "❌ Erro na aplicação. Verificar logs:"
    echo "   journalctl -u privacy -f"
fi

echo ""
echo "✅ ATUALIZAÇÃO CONCLUÍDA!"
echo "========================"
echo ""
echo "📋 Comandos úteis:"
echo "   Ver logs: journalctl -u privacy -f"
echo "   Reiniciar: systemctl restart privacy"
echo "   Status: systemctl status privacy"