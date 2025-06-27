#!/bin/bash

echo "🔍 Diagnóstico completo do serviço privacy"

# Copie e execute este script na VPS como root

echo "=== LOGS DO SERVIÇO ==="
journalctl -u privacy --no-pager -l -n 20

echo ""
echo "=== ESTRUTURA DE ARQUIVOS ==="
ls -la /opt/privacy/

echo ""
echo "=== TESTE DE IMPORTAÇÃO ==="
cd /opt/privacy
source venv/bin/activate 2>/dev/null || echo "Virtual env não encontrado"
python3 -c "
import sys
sys.path.insert(0, '/opt/privacy')
try:
    import web_interface
    print('✅ web_interface importado')
    app = web_interface.app
    print('✅ app Flask criado')
except ImportError as e:
    print(f'❌ Erro de importação: {e}')
except Exception as e:
    print(f'❌ Erro geral: {e}')
"

echo ""
echo "=== TESTE GUNICORN MANUAL ==="
cd /opt/privacy
source venv/bin/activate
python3 -c "
import os
os.chdir('/opt/privacy')
try:
    from gunicorn.app.wsgiapp import WSGIApplication
    print('✅ Gunicorn disponível')
except Exception as e:
    print(f'❌ Erro Gunicorn: {e}')
"

echo ""
echo "=== DEPENDÊNCIAS PYTHON ==="
source venv/bin/activate
pip list | grep -E "(flask|gunicorn|sqlalchemy)"

echo ""
echo "=== VARIÁVEIS DE AMBIENTE ==="
if [ -f "/opt/privacy/.env" ]; then
    echo "✅ .env existe"
    grep -v "OPENAI_API_KEY" /opt/privacy/.env
else
    echo "❌ .env não encontrado"
fi

echo ""
echo "=== TESTE POSTGRESQL ==="
sudo -u postgres psql -c "\l" | grep privacy || echo "❌ Database privacy não encontrada"

echo ""
echo "=== PERMISSÕES ==="
ls -la /opt/privacy/ | head -10

echo ""
echo "=== PROCESSO MANUAL ==="
echo "Testando execução manual..."
cd /opt/privacy
source venv/bin/activate
export PYTHONPATH=/opt/privacy
timeout 5 python3 web_interface.py &
sleep 2
if curl -s http://localhost:5000 >/dev/null; then
    echo "✅ Servidor responde na porta 5000"
else
    echo "❌ Servidor não responde"
fi
pkill -f web_interface.py 2>/dev/null

echo ""
echo "=== PORTA 5000 ==="
netstat -tulpn | grep :5000 || echo "Porta 5000 livre"