#!/bin/bash

# Fix completo para todos os problemas VPS
echo "🔧 Correção completa do sistema VPS..."

cd /opt/privacy

# 1. Corrigir .env com configurações corretas
echo "📋 Criando .env correto..."
cat > .env << 'EOF'
DATABASE_URL=postgresql://privacy_user:Lgpd2025%23Privacy@localhost:5432/privacy_db
PGHOST=localhost
PGPORT=5432
PGDATABASE=privacy_db
PGUSER=privacy_user
PGPASSWORD=Lgpd2025#Privacy
FLASK_ENV=production
FLASK_DEBUG=False
SECRET_KEY=lgpd-crisis-ops-production-2025-secure-key-monster-vps
OPENAI_API_KEY=
APP_PORT=5000
APP_HOST=0.0.0.0
WORKERS=4
DOMAIN=monster.e-ness.com.br
SSL_ENABLED=true
AI_ENABLED=true
EOF

# 2. Instalar dependências necessárias
echo "📦 Instalando dependências..."
/opt/privacy/venv/bin/pip install asyncpg psycopg2-binary --quiet

# 3. Executar merge PostgreSQL simplificado
echo "🔄 Configurando PostgreSQL..."
/opt/privacy/venv/bin/python3 -c "
import asyncio
import asyncpg
from urllib.parse import quote_plus

async def setup_postgresql():
    try:
        password = quote_plus('Lgpd2025#Privacy')
        conn_string = f'postgresql://privacy_user:{password}@localhost:5432/privacy_db'
        conn = await asyncpg.connect(conn_string)
        
        # Criar tabelas necessárias
        await conn.execute('''
            CREATE TABLE IF NOT EXISTS search_priorities (
                id SERIAL PRIMARY KEY,
                prioridade INTEGER NOT NULL UNIQUE,
                nome_empresa VARCHAR(255) NOT NULL,
                dominio_email VARCHAR(255) NOT NULL,
                ativo BOOLEAN DEFAULT TRUE,
                criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        await conn.execute('''
            CREATE TABLE IF NOT EXISTS incidentes_lgpd (
                id SERIAL PRIMARY KEY,
                empresa VARCHAR(255) NOT NULL,
                data_incidente DATE,
                tipo_incidente VARCHAR(100) NOT NULL,
                descricao TEXT,
                status VARCHAR(50) DEFAULT 'Aberto',
                criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                atualizado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Inserir prioridades empresariais
        prioridades = [
            (1, 'BRADESCO', 'bradesco.com.br'),
            (2, 'PETROBRAS', 'petrobras.com.br'),
            (3, 'ONS', 'ons.org.br'),
            (4, 'EMBRAER', 'embraer.com.br'),
            (5, 'REDE DOR', 'rededorsaoluiz.com.br'),
            (6, 'GLOBO', 'globo.com'),
            (7, 'ELETROBRAS', 'eletrobras.com'),
            (8, 'CREFISA', 'crefisa.com.br'),
            (9, 'EQUINIX', 'equinix.com'),
            (10, 'COHESITY', 'cohesity.com')
        ]
        
        for p, n, d in prioridades:
            await conn.execute('''
                INSERT INTO search_priorities (prioridade, nome_empresa, dominio_email)
                VALUES (\$1, \$2, \$3)
                ON CONFLICT (prioridade) DO UPDATE SET 
                    nome_empresa = EXCLUDED.nome_empresa,
                    dominio_email = EXCLUDED.dominio_email
            ''', p, n, d)
        
        total = await conn.fetchval('SELECT COUNT(*) FROM search_priorities')
        print(f'✅ PostgreSQL configurado com {total} prioridades')
        
        await conn.close()
        return True
        
    except Exception as e:
        print(f'❌ Erro PostgreSQL: {e}')
        return False

result = asyncio.run(setup_postgresql())
exit(0 if result else 1)
"

# 4. Criar estrutura de dados de teste
echo "📁 Criando estrutura de dados..."
mkdir -p data/{bradesco,petrobras,ons,embraer,outros}

echo "Email: joao.silva@bradesco.com.br, CPF: 123.456.789-00" > data/bradesco/email_teste.txt
echo "Contrato Petrobras: maria.santos@petrobras.com.br, RG: 12.345.678-9" > data/petrobras/contrato.txt
echo "Documento ONS: carlos@ons.org.br, telefone: (11) 99999-1234" > data/ons/documento.txt
echo "Projeto Embraer: ana@embraer.com.br, dados pessoais diversos" > data/embraer/projeto.txt
echo "Arquivo teste com dados LGPD: email@teste.com" > data/outros/arquivo.txt

# 5. Corrigir permissões
echo "🔒 Ajustando permissões..."
chown -R privacy:privacy /opt/privacy/
chmod 600 /opt/privacy/.env

# 6. Reiniciar serviço
echo "🔄 Reiniciando serviço..."
systemctl restart privacy

# 7. Aguardar e verificar
sleep 5
echo "📊 Status final:"
systemctl status privacy --no-pager -l | head -15

echo ""
echo "✅ Correção completa finalizada!"
echo "🌐 Acesse: https://monster.e-ness.com.br"
echo ""
echo "⚠️  IMPORTANTE: Adicione sua chave OpenAI:"
echo "    nano /opt/privacy/.env"
echo "    Localize: OPENAI_API_KEY="
echo "    Substitua por: OPENAI_API_KEY=sua_chave_aqui"
echo ""
echo "Após adicionar a chave, execute:"
echo "    systemctl restart privacy"