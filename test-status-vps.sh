#!/bin/bash

# Teste completo de status do sistema VPS
echo "🔍 Verificando status do sistema LGPD..."

cd /opt/privacy

# 1. Verificar se o .env existe e tem as configurações corretas
echo "📋 Verificando .env..."
if [ -f .env ]; then
    echo "✅ Arquivo .env encontrado"
    if grep -q "DATABASE_URL.*postgresql" .env; then
        echo "✅ URL PostgreSQL configurada"
    else
        echo "❌ URL PostgreSQL não encontrada"
    fi
    
    if grep -q "OPENAI_API_KEY=" .env; then
        if grep -q "OPENAI_API_KEY=$" .env || grep -q "OPENAI_API_KEY=\"\"" .env; then
            echo "⚠️  Chave OpenAI não configurada"
        else
            echo "✅ Chave OpenAI configurada"
        fi
    else
        echo "❌ OPENAI_API_KEY não encontrada"
    fi
else
    echo "❌ Arquivo .env não encontrado"
fi

# 2. Testar conexão PostgreSQL diretamente
echo ""
echo "🗄️  Testando PostgreSQL..."
/opt/privacy/venv/bin/python3 -c "
import asyncio
import asyncpg
from urllib.parse import quote_plus

async def test_postgres():
    try:
        password = quote_plus('Lgpd2025#Privacy')
        conn_string = f'postgresql://privacy_user:{password}@localhost:5432/privacy_db'
        conn = await asyncpg.connect(conn_string)
        result = await conn.fetchval('SELECT COUNT(*) FROM search_priorities')
        await conn.close()
        print(f'✅ PostgreSQL: {result} prioridades carregadas')
        return True
    except Exception as e:
        print(f'❌ PostgreSQL erro: {e}')
        return False

asyncio.run(test_postgres())
"

# 3. Verificar se asyncpg está instalado
echo ""
echo "📦 Verificando dependências..."
/opt/privacy/venv/bin/python3 -c "
try:
    import asyncpg
    print('✅ asyncpg instalado')
except ImportError:
    print('❌ asyncpg não instalado')

try:
    import openai
    print('✅ openai instalado')
except ImportError:
    print('❌ openai não instalado')
"

# 4. Testar API de status diretamente
echo ""
echo "🌐 Testando API de status..."
curl -s "http://localhost:5000/api/system-status" | python3 -m json.tool

# 5. Verificar logs do serviço
echo ""
echo "📊 Últimos logs do serviço:"
journalctl -u privacy --no-pager -l -n 10

# 6. Status do serviço
echo ""
echo "🔧 Status do serviço privacy:"
systemctl is-active privacy && echo "✅ Serviço ativo" || echo "❌ Serviço inativo"
systemctl is-enabled privacy && echo "✅ Serviço habilitado" || echo "❌ Serviço desabilitado"

echo ""
echo "🌐 Acesse o dashboard: https://monster.e-ness.com.br"
echo ""
echo "Se PostgreSQL ou IA estão inativos:"
echo "1. Execute: ./fix-simple-vps.sh"  
echo "2. Adicione chave OpenAI ao .env"
echo "3. Reinicie: systemctl restart privacy"