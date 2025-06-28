#!/bin/bash

# Correção específica para status da IA
echo "🤖 Corrigindo status da IA..."

cd /opt/privacy

# 1. Instalar python-dotenv se não existir
echo "📦 Instalando python-dotenv..."
/opt/privacy/venv/bin/pip install python-dotenv --quiet

# 2. Testar se as variáveis estão sendo carregadas
echo "🧪 Testando carregamento de variáveis..."
/opt/privacy/venv/bin/python3 -c "
import os
from dotenv import load_dotenv

# Carregar .env
load_dotenv('.env')

# Verificar variáveis
database_url = os.getenv('DATABASE_URL', '')
openai_key = os.getenv('OPENAI_API_KEY', '')

print(f'DATABASE_URL existe: {bool(database_url)}')
print(f'OPENAI_API_KEY existe: {bool(openai_key)}')
print(f'OPENAI_API_KEY começa com sk-: {openai_key.startswith(\"sk-\")}')
print(f'Comprimento da chave: {len(openai_key)}')
"

# 3. Verificar se gunicorn.conf.py carrega variáveis
echo "🔧 Verificando configuração Gunicorn..."
if [ -f gunicorn.conf.py ]; then
    echo "✅ gunicorn.conf.py encontrado"
    grep -q "dotenv" gunicorn.conf.py && echo "✅ dotenv configurado" || echo "⚠️ dotenv não configurado"
else
    echo "⚠️ gunicorn.conf.py não encontrado"
fi

# 4. Reiniciar serviço
echo "🔄 Reiniciando serviço..."
systemctl restart privacy

# 5. Aguardar e testar
sleep 3
echo "📡 Testando API após correção..."
curl -s "http://localhost:5000/api/system-status" | python3 -m json.tool

echo ""
echo "✅ Correção aplicada!"
echo "Se IA ainda aparece inativa, verifique os logs:"
echo "journalctl -u privacy --no-pager -f"