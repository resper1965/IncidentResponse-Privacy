#!/bin/bash

# Deploy final completo para VPS - todos os scripts em um
echo "🚀 Deploy final completo para VPS..."

cd /opt/privacy

# 1. Criar arquivo .env correto
echo "📋 Criando arquivo .env..."
cat > .env << 'EOF'
# n.crisisops - LGPD Privacy Module - Production Environment
# Configurações de produção para VPS

# === DATABASE CONFIGURATION ===
# PostgreSQL Production Database (URL-encoded password for special characters)
DATABASE_URL=postgresql://privacy_user:Lgpd2025%23Privacy@localhost:5432/privacy_db
PGHOST=localhost
PGPORT=5432
PGDATABASE=privacy_db
PGUSER=privacy_user
PGPASSWORD=Lgpd2025#Privacy

# === APPLICATION CONFIGURATION ===
FLASK_ENV=production
FLASK_DEBUG=False
SECRET_KEY=lgpd-crisis-ops-production-2025-secure-key-monster-vps

# === AI CONFIGURATION ===
# OpenAI API Key (adicionar manualmente)
OPENAI_API_KEY=

# === SYSTEM CONFIGURATION ===
# Application settings
APP_PORT=5000
APP_HOST=0.0.0.0
WORKERS=4

# Log settings
LOG_LEVEL=INFO
LOG_FILE=/var/log/privacy/privacy.log

# === SECURITY SETTINGS ===
# Domain and SSL
DOMAIN=monster.e-ness.com.br
SSL_ENABLED=true

# File upload limits
MAX_CONTENT_LENGTH=100MB
UPLOAD_FOLDER=/opt/privacy/uploads

# === PROCESSING CONFIGURATION ===
# Document processing
MAX_PARALLEL_DOCS=10
PROCESSING_TIMEOUT=300

# AI processing limits
AI_ENABLED=true
AI_MAX_REQUESTS_PER_HOUR=1000
AI_CONFIDENCE_THRESHOLD=0.7

# === BACKUP CONFIGURATION ===
BACKUP_ENABLED=true
BACKUP_RETENTION_DAYS=30
BACKUP_PATH=/opt/privacy/backups
EOF

# 2. Instalar dependências Python necessárias
echo "📦 Instalando dependências Python..."
/opt/privacy/venv/bin/pip install asyncpg psycopg2-binary --quiet

# 3. Executar merge do banco PostgreSQL
echo "🔄 Executando merge do banco PostgreSQL..."
/opt/privacy/venv/bin/python3 -c "
import asyncio
import asyncpg
from urllib.parse import quote_plus

# URL encode the password to handle special characters
password = quote_plus('Lgpd2025#Privacy')
DATABASE_URL = f'postgresql://privacy_user:{password}@localhost:5432/privacy_db'

PRIORIDADES = [
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

async def merge_database():
    print('Iniciando merge do banco PostgreSQL...')
    
    try:
        conn = await asyncpg.connect(DATABASE_URL)
        
        # Garantir que tabela existe
        await conn.execute('''
            CREATE TABLE IF NOT EXISTS search_priorities (
                id SERIAL PRIMARY KEY,
                prioridade INTEGER NOT NULL UNIQUE,
                nome_empresa VARCHAR(255) NOT NULL,
                dominio_email VARCHAR(255) NOT NULL,
                ativo BOOLEAN DEFAULT TRUE,
                criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                atualizado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Merge das prioridades
        for prioridade, nome_empresa, dominio_email in PRIORIDADES:
            await conn.execute('''
                INSERT INTO search_priorities (prioridade, nome_empresa, dominio_email)
                VALUES (\$1, \$2, \$3)
                ON CONFLICT (prioridade) DO UPDATE SET 
                    nome_empresa = EXCLUDED.nome_empresa,
                    dominio_email = EXCLUDED.dominio_email,
                    atualizado_em = CURRENT_TIMESTAMP
            ''', prioridade, nome_empresa, dominio_email)
            print(f'Merged: {nome_empresa} (Prioridade {prioridade})')
        
        # Verificar resultado
        total = await conn.fetchval('SELECT COUNT(*) FROM search_priorities WHERE ativo = true')
        print(f'✅ Total de prioridades ativas: {total}')
        
        await conn.close()
        print('✅ Merge concluído com sucesso')
        
    except Exception as e:
        print(f'❌ Erro no merge: {e}')
        return False
    
    return True

asyncio.run(merge_database())
"

# 4. Criar estrutura de diretórios de teste
echo "📁 Criando estrutura de diretórios de teste..."
mkdir -p data/bradesco/emails
mkdir -p data/petrobras/contratos
mkdir -p data/ons/documentos
mkdir -p data/embraer/projetos
mkdir -p data/outros/diversos

# Criar arquivos de teste
echo "Este é um email de joão.silva@bradesco.com.br com CPF 123.456.789-00" > data/bradesco/emails/email_teste.txt
echo "Contrato com representante da Petrobras: maria.santos@petrobras.com.br, telefone (21) 99999-1234" > data/petrobras/contratos/contrato_exemplo.txt
echo "Documento ONS com engenheiro carlos.oliveira@ons.org.br e RG 12.345.678-9" > data/ons/documentos/documento_tecnico.txt
echo "Projeto Embraer - Coordenador: ana.costa@embraer.com.br, CPF 987.654.321-00" > data/embraer/projetos/projeto_aviacao.txt
echo "Dados diversos com email teste@exemplo.com e telefone (11) 98765-4321" > data/outros/diversos/arquivo_misto.txt

# 5. Definir permissões corretas
echo "🔒 Definindo permissões..."
chown -R privacy:privacy /opt/privacy/
chmod 600 /opt/privacy/.env
chmod +x /opt/privacy/*.sh

# 6. Reiniciar serviço
echo "🔄 Reiniciando serviço privacy..."
systemctl restart privacy

# 7. Aguardar e verificar status
sleep 5
echo "📊 Verificando status final..."
systemctl status privacy --no-pager -l

echo "✅ Deploy final concluído!"
echo "🌐 Sistema disponível em: https://monster.e-ness.com.br"
echo "⚠️  IMPORTANTE: Adicione sua chave OpenAI em /opt/privacy/.env"
echo "    Edite: OPENAI_API_KEY=sua_chave_aqui"