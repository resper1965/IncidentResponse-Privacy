#!/bin/bash

# =============================================================================
# Script de Correção Rápida - Erro 502 VPS
# n.crisisops - Sistema LGPD
# =============================================================================

echo "🔧 Corrigindo erro 502 na VPS..."

# Verificar se está na VPS
if [ ! -d "/opt/privacy" ]; then
    echo "❌ Este script deve ser executado na VPS com /opt/privacy"
    exit 1
fi

# Parar serviços
echo "⏸️  Parando serviços..."
systemctl stop privacy

# Atualizar arquivo web_interface.py com health check
echo "📝 Atualizando web_interface.py..."
cat > /tmp/health_route.py << 'EOF'
@app.route('/health')
def health_check():
    """Health check endpoint para load balancer"""
    return "healthy\n", 200, {'Content-Type': 'text/plain'}
EOF

# Verificar se a rota health já existe
if ! grep -q "/health" /opt/privacy/app/web_interface.py; then
    echo "➕ Adicionando rota /health..."
    # Adicionar antes da linha "if __name__ == '__main__':"
    sed -i '/if __name__ == '\''__main__'\'':/i\
@app.route('\''/health'\'')\
def health_check():\
    """Health check endpoint para load balancer"""\
    return "healthy\\n", 200, {'\''Content-Type'\'': '\''text/plain'\''}\
' /opt/privacy/app/web_interface.py
fi

# Verificar dependências Python
echo "🐍 Verificando dependências Python..."
sudo -u privacy /opt/privacy/venv/bin/pip install --upgrade flask gunicorn

# Corrigir permissões
echo "🔐 Corrigindo permissões..."
chown -R privacy:privacy /opt/privacy
chmod +x /opt/privacy/venv/bin/python
chmod +x /opt/privacy/venv/bin/gunicorn

# Testar aplicação manualmente
echo "🧪 Testando aplicação..."
cd /opt/privacy/app
timeout 10s sudo -u privacy /opt/privacy/venv/bin/python -c "
import web_interface
print('✅ Importação Python OK')
"

if [ $? -eq 0 ]; then
    echo "✅ Aplicação Python funcionando"
else
    echo "❌ Erro na aplicação Python - verificar logs"
    echo "Executando diagnóstico..."
    sudo -u privacy /opt/privacy/venv/bin/python web_interface.py &
    PYTHON_PID=$!
    sleep 5
    kill $PYTHON_PID 2>/dev/null
fi

# Reiniciar PostgreSQL se necessário
echo "🗄️  Verificando PostgreSQL..."
if ! systemctl is-active --quiet postgresql; then
    echo "🔄 Reiniciando PostgreSQL..."
    systemctl restart postgresql
    sleep 3
fi

# Testar conexão ao banco
sudo -u privacy PGPASSWORD="ncrisisops_secure_2025" psql -h localhost -U privacy privacy -c "SELECT 1;" > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo "✅ PostgreSQL conectando"
else
    echo "⚠️  PostgreSQL com problemas - continuando..."
fi

# Iniciar serviço
echo "🚀 Iniciando serviço..."
systemctl start privacy
sleep 5

# Verificar status
echo "📊 Verificando status..."
if systemctl is-active --quiet privacy; then
    echo "✅ Serviço privacy ativo"
else
    echo "❌ Serviço privacy falhou"
    echo "📋 Logs recentes:"
    journalctl -u privacy --no-pager -n 20
fi

# Testar aplicação
echo "🌐 Testando aplicação..."
sleep 3

# Teste local
if curl -s http://localhost:5000/health > /dev/null; then
    echo "✅ Health check local OK"
else
    echo "❌ Health check local falhou"
    echo "🔍 Tentando diagnóstico..."
    
    # Verificar porta 5000
    if netstat -tlnp | grep :5000; then
        echo "✅ Porta 5000 em uso"
    else
        echo "❌ Porta 5000 não está sendo usada"
    fi
    
    # Verificar processos
    if ps aux | grep gunicorn | grep -v grep; then
        echo "✅ Processos Gunicorn encontrados"
    else
        echo "❌ Nenhum processo Gunicorn"
    fi
fi

# Verificar Nginx
echo "🌍 Verificando Nginx..."
if systemctl is-active --quiet nginx; then
    echo "✅ Nginx ativo"
    nginx -t
else
    echo "🔄 Reiniciando Nginx..."
    systemctl restart nginx
fi

# Teste final
echo "🎯 Teste final..."
sleep 2

if curl -s -I http://monster.e-ness.com.br/health | grep -q "200 OK"; then
    echo "🎉 SUCESSO! Aplicação funcionando em monster.e-ness.com.br"
elif curl -s -I http://localhost/health | grep -q "200 OK"; then
    echo "✅ Aplicação funcionando localmente - verificar DNS"
else
    echo "❌ Ainda com problemas"
    echo ""
    echo "📋 Informações para diagnóstico:"
    echo "Status dos serviços:"
    systemctl status privacy --no-pager -l
    echo ""
    echo "Últimos logs:"
    journalctl -u privacy --no-pager -n 10
fi

echo ""
echo "🔧 Script de correção concluído"
echo "📖 Para mais diagnósticos, consulte: DIAGNOSTICO_502.md"