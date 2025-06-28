#!/bin/bash

# Script para diagnosticar e corrigir o serviço privacy no VPS

echo "🔍 Diagnosticando serviço privacy..."

# 1. Verificar arquivo de serviço
echo "📋 Configuração do serviço:"
if [ -f "/etc/systemd/system/privacy.service" ]; then
    cat /etc/systemd/system/privacy.service
else
    echo "❌ Arquivo de serviço não encontrado!"
fi

echo ""
echo "📂 Estrutura do diretório /opt/privacy:"
ls -la /opt/privacy/

echo ""
echo "🐍 Verificando Python e dependências:"
which python3
python3 --version

echo ""
echo "📄 Verificando web_interface.py:"
if [ -f "/opt/privacy/web_interface.py" ]; then
    echo "✅ web_interface.py existe"
    head -5 /opt/privacy/web_interface.py
else
    echo "❌ web_interface.py não encontrado!"
fi

echo ""
echo "🔧 Testando execução direta:"
cd /opt/privacy
python3 web_interface.py &
sleep 3
if pgrep -f "python3 web_interface.py"; then
    echo "✅ Python executa normalmente"
    pkill -f "python3 web_interface.py"
else
    echo "❌ Erro na execução Python"
fi

echo ""
echo "📝 Verificando logs do sistema:"
journalctl -u privacy -n 10 --no-pager