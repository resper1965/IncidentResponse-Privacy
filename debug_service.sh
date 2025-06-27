#!/bin/bash

# =============================================================================
# Script de Debug do Serviço Privacy
# n.crisisops - Sistema LGPD
# =============================================================================

echo "🔍 Debugando serviço privacy..."

# Parar serviço atual
systemctl stop privacy

# Verificar logs detalhados
echo "📋 Logs recentes do serviço:"
journalctl -u privacy --no-pager -n 50

echo ""
echo "📋 Logs do Gunicorn:"
if [ -f "/opt/privacy/logs/gunicorn.log" ]; then
    tail -20 /opt/privacy/logs/gunicorn.log
else
    echo "Arquivo de log não existe ainda"
fi

# Verificar estrutura de arquivos
echo ""
echo "📁 Estrutura de arquivos:"
ls -la /opt/privacy/app/

# Verificar permissões
echo ""
echo "🔐 Permissões:"
ls -la /opt/privacy/venv/bin/gunicorn
ls -la /opt/privacy/app/web_interface.py

# Testar importação Python
echo ""
echo "🐍 Testando importação Python:"
cd /opt/privacy/app
sudo -u privacy /opt/privacy/venv/bin/python -c "
try:
    import web_interface
    print('✅ Importação web_interface OK')
    print('✅ Flask app disponível:', hasattr(web_interface, 'app'))
except Exception as e:
    print('❌ Erro na importação:', e)
    import traceback
    traceback.print_exc()
"

# Testar Gunicorn diretamente
echo ""
echo "🚀 Testando Gunicorn manualmente:"
cd /opt/privacy/app
timeout 10s sudo -u privacy /opt/privacy/venv/bin/gunicorn --bind 0.0.0.0:5001 web_interface:app &
GUNICORN_PID=$!
sleep 3

if ps -p $GUNICORN_PID > /dev/null; then
    echo "✅ Gunicorn iniciou manualmente"
    curl -s http://localhost:5001/health && echo "" || echo "❌ Health check falhou"
    kill $GUNICORN_PID
else
    echo "❌ Gunicorn falhou ao iniciar manualmente"
fi

# Verificar arquivo de configuração
echo ""
echo "⚙️ Configuração Gunicorn:"
cat /opt/privacy/gunicorn.conf.py

# Verificar se todas as dependências estão instaladas
echo ""
echo "📦 Verificando dependências:"
sudo -u privacy /opt/privacy/venv/bin/pip list | grep -E "(flask|gunicorn|sqlalchemy|psycopg2)"

# Verificar se PostgreSQL funciona
echo ""
echo "🗄️ Testando PostgreSQL:"
if PGPASSWORD="ncrisisops_secure_2025" psql -h localhost -U privacy -d privacy -c "SELECT 1;" > /dev/null 2>&1; then
    echo "✅ PostgreSQL OK"
else
    echo "❌ PostgreSQL com problema"
fi

echo ""
echo "🔧 Sugestões de correção:"
echo "1. Verificar importação Python acima"
echo "2. Verificar logs detalhados"
echo "3. Executar: systemctl start privacy"
echo "4. Verificar: journalctl -u privacy -f"