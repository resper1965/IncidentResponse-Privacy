#!/bin/bash

# Correção simples e direta para VPS
echo "🔧 Correção simples PostgreSQL e IA..."

cd /opt/privacy

# 1. Criar .env mínimo e correto
echo "📋 Criando .env simples..."
cat > .env << EOF
DATABASE_URL=postgresql://privacy_user:Lgpd2025%23Privacy@localhost:5432/privacy_db
OPENAI_API_KEY=
FLASK_ENV=production
FLASK_DEBUG=False
EOF

# 2. Instalar asyncpg no ambiente virtual
echo "📦 Instalando asyncpg..."
/opt/privacy/venv/bin/pip install asyncpg --quiet

# 3. Testar conexão PostgreSQL
echo "🧪 Testando PostgreSQL..."
/opt/privacy/venv/bin/python3 -c "
import asyncio
import asyncpg
from urllib.parse import quote_plus

async def test_postgres():
    try:
        password = quote_plus('Lgpd2025#Privacy')
        conn_string = f'postgresql://privacy_user:{password}@localhost:5432/privacy_db'
        conn = await asyncpg.connect(conn_string)
        await conn.execute('SELECT 1')
        await conn.close()
        print('✅ PostgreSQL funcionando')
        return True
    except Exception as e:
        print(f'❌ PostgreSQL erro: {e}')
        return False

result = asyncio.run(test_postgres())
"

# 4. Definir permissões
echo "🔒 Ajustando permissões..."
chown privacy:privacy /opt/privacy/.env
chmod 600 /opt/privacy/.env

# 5. Reiniciar serviço
echo "🔄 Reiniciando privacy..."
systemctl restart privacy

# 6. Verificar status
sleep 3
echo "📊 Status do serviço:"
systemctl is-active privacy && echo "✅ Serviço ativo" || echo "❌ Serviço inativo"

echo ""
echo "🌐 Acesse: https://monster.e-ness.com.br"
echo ""
echo "Para ativar IA, adicione chave OpenAI:"
echo "nano /opt/privacy/.env"
echo "Mude: OPENAI_API_KEY=sua_chave_aqui"
echo "Depois: systemctl restart privacy"