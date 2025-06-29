#!/bin/bash

# n.crisisops - LGPD Privacy Module - Fix Database Quick
# Script rápido para corrigir problemas do banco PostgreSQL

echo "🔧 n.crisisops - LGPD Privacy Module - Fix Database Quick"
echo "================================================================="

# Variáveis
INSTALL_DIR="/opt/privacy"
DB_NAME="privacy_db"
DB_USER="privacy_user"
DB_PASS="Lgpd2025#Privacy"

echo "📋 Verificando PostgreSQL..."

# Verificar se PostgreSQL está rodando
if ! systemctl is-active --quiet postgresql; then
    echo "⚠️ PostgreSQL não está rodando. Iniciando..."
    systemctl start postgresql
    systemctl enable postgresql
fi

echo "✅ PostgreSQL está rodando"

echo "🔍 Verificando banco de dados..."

# Verificar se o banco existe
if ! sudo -u postgres psql -lqt | cut -d \| -f 1 | grep -qw "$DB_NAME"; then
    echo "⚠️ Banco $DB_NAME não existe. Criando..."
    
    # Criar banco e usuário
    sudo -u postgres psql << EOF
-- Criar usuário se não existir
DO \$\$
BEGIN
    IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = '$DB_USER') THEN
        CREATE USER $DB_USER WITH PASSWORD '$DB_PASS';
    END IF;
END
\$\$;

-- Criar banco
CREATE DATABASE $DB_NAME OWNER $DB_USER;

-- Conceder privilégios
GRANT ALL PRIVILEGES ON DATABASE $DB_NAME TO $DB_USER;
ALTER USER $DB_USER CREATEDB;
EOF

    echo "✅ Banco $DB_NAME criado"
else
    echo "✅ Banco $DB_NAME já existe"
fi

echo "📦 Verificando psycopg2..."

# Verificar se psycopg2 está instalado
cd $INSTALL_DIR
source venv/bin/activate

if ! python -c "import psycopg2" 2>/dev/null; then
    echo "⚠️ psycopg2 não está instalado. Instalando..."
    pip install psycopg2-binary
    echo "✅ psycopg2 instalado"
else
    echo "✅ psycopg2 já está instalado"
fi

echo "🚀 Criando script de população..."

# Criar script de população
cat > populate-database.py << 'EOF'
#!/usr/bin/env python3
"""
Script para popular o banco de dados PostgreSQL com dados iniciais
n.crisisops - LGPD Privacy Module
"""

import os
import sys
import psycopg2
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Configurações do banco
DB_CONFIG = {
    'host': 'localhost',
    'port': 5432,
    'database': 'privacy_db',
    'user': 'privacy_user',
    'password': 'Lgpd2025#Privacy'
}

def test_connection():
    """Testa a conexão com o banco de dados"""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        conn.close()
        logger.info("✅ Conexão com PostgreSQL estabelecida")
        return True
    except Exception as e:
        logger.error(f"❌ Erro na conexão com PostgreSQL: {e}")
        return False

def create_tables():
    """Cria as tabelas necessárias"""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        # Tabela de padrões regex
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS regex_patterns (
                id SERIAL PRIMARY KEY,
                name VARCHAR(100) UNIQUE NOT NULL,
                pattern TEXT NOT NULL,
                description TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Tabela de prioridades de busca
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS search_priorities (
                id SERIAL PRIMARY KEY,
                priority INTEGER NOT NULL,
                company_name VARCHAR(200) NOT NULL,
                domain VARCHAR(200),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Tabela de resultados de extração
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS extraction_results (
                id SERIAL PRIMARY KEY,
                file_name VARCHAR(255) NOT NULL,
                file_type VARCHAR(50),
                extraction_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                total_items INTEGER DEFAULT 0,
                cpf_count INTEGER DEFAULT 0,
                email_count INTEGER DEFAULT 0,
                phone_count INTEGER DEFAULT 0,
                rg_count INTEGER DEFAULT 0,
                cep_count INTEGER DEFAULT 0,
                name_count INTEGER DEFAULT 0,
                birth_date_count INTEGER DEFAULT 0,
                results_json TEXT,
                processing_time FLOAT,
                status VARCHAR(50) DEFAULT 'completed'
            )
        """)
        
        # Tabela de configurações do sistema
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS system_config (
                id SERIAL PRIMARY KEY,
                key VARCHAR(100) UNIQUE NOT NULL,
                value TEXT,
                description TEXT,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        conn.commit()
        cursor.close()
        conn.close()
        
        logger.info("✅ Tabelas criadas com sucesso")
        return True
        
    except Exception as e:
        logger.error(f"❌ Erro ao criar tabelas: {e}")
        return False

def insert_regex_patterns():
    """Insere padrões regex padrão"""
    patterns = [
        ('CPF', r'\b\d{3}\.?\d{3}\.?\d{3}-?\d{2}\b', 'CPF brasileiro com ou sem formatação'),
        ('RG', r'\b\d{1,2}\.?\d{3}\.?\d{3}-?[0-9Xx]\b', 'RG com formatação SP'),
        ('EMAIL', r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', 'Endereço de email válido'),
        ('TELEFONE', r'\(?\d{2}\)?\s?9?\d{4}-?\d{4}', 'Telefone celular e fixo brasileiro'),
        ('CEP', r'\b\d{5}-?\d{3}\b', 'CEP brasileiro'),
        ('DATA_NASCIMENTO', r'\b\d{1,2}\/\d{1,2}\/\d{4}\b', 'Data no formato DD/MM/AAAA'),
        ('NOME_COMPLETO', r'\b[A-Z][a-z]+\s+[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b', 'Nome completo com inicial maiúscula'),
        ('CNPJ', r'\b\d{2}\.?\d{3}\.?\d{3}\/?\d{4}-?\d{2}\b', 'CNPJ brasileiro'),
        ('PIS', r'\b\d{3}\.?\d{5}\.?\d{2}-?\d{1}\b', 'PIS/PASEP'),
        ('TITULO_ELEITOR', r'\b\d{4}\s?\d{4}\s?\d{4}\b', 'Título de eleitor')
    ]
    
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        for name, pattern, description in patterns:
            cursor.execute("""
                INSERT INTO regex_patterns (name, pattern, description)
                VALUES (%s, %s, %s)
                ON CONFLICT (name) DO UPDATE SET
                    pattern = EXCLUDED.pattern,
                    description = EXCLUDED.description
            """, (name, pattern, description))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        logger.info(f"✅ {len(patterns)} padrões regex inseridos")
        return True
        
    except Exception as e:
        logger.error(f"❌ Erro ao inserir padrões regex: {e}")
        return False

def insert_search_priorities():
    """Insere prioridades de busca empresariais"""
    priorities = [
        (1, 'Banco Bradesco', 'bradesco.com.br'),
        (1, 'Petrobras', 'petrobras.com.br'),
        (1, 'ONS', 'ons.org.br'),
        (1, 'Banco Central', 'bcb.gov.br'),
        (2, 'Banco do Brasil', 'bb.com.br'),
        (2, 'Caixa Econômica Federal', 'caixa.gov.br'),
        (2, 'Itaú Unibanco', 'itau.com.br'),
        (2, 'Santander', 'santander.com.br'),
        (3, 'Vale', 'vale.com'),
        (3, 'Ambev', 'ambev.com.br'),
        (3, 'JBS', 'jbs.com.br')
    ]
    
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        for priority, company, domain in priorities:
            cursor.execute("""
                INSERT INTO search_priorities (priority, company_name, domain)
                VALUES (%s, %s, %s)
                ON CONFLICT DO NOTHING
            """, (priority, company, domain))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        logger.info(f"✅ {len(priorities)} prioridades empresariais inseridas")
        return True
        
    except Exception as e:
        logger.error(f"❌ Erro ao inserir prioridades: {e}")
        return False

def insert_system_config():
    """Insere configurações padrão do sistema"""
    configs = [
        ('max_file_size', '104857600', 'Tamanho máximo de arquivo em bytes (100MB)'),
        ('allowed_extensions', 'pdf,doc,docx,txt,eml,msg,rtf', 'Extensões de arquivo permitidas'),
        ('processing_timeout', '300', 'Timeout de processamento em segundos'),
        ('enable_ai_processing', 'true', 'Habilitar processamento com IA'),
        ('enable_semantic_analysis', 'true', 'Habilitar análise semântica'),
        ('log_level', 'INFO', 'Nível de log do sistema'),
        ('backup_enabled', 'true', 'Habilitar backup automático'),
        ('ssl_enabled', 'true', 'Habilitar SSL/TLS')
    ]
    
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        for key, value, description in configs:
            cursor.execute("""
                INSERT INTO system_config (key, value, description)
                VALUES (%s, %s, %s)
                ON CONFLICT (key) DO UPDATE SET
                    value = EXCLUDED.value,
                    description = EXCLUDED.description,
                    updated_at = CURRENT_TIMESTAMP
            """, (key, value, description))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        logger.info(f"✅ {len(configs)} configurações do sistema inseridas")
        return True
        
    except Exception as e:
        logger.error(f"❌ Erro ao inserir configurações: {e}")
        return False

def verify_database():
    """Verifica se o banco foi populado corretamente"""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        # Verificar tabelas
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
        """)
        tables = [row[0] for row in cursor.fetchall()]
        
        # Verificar dados
        cursor.execute("SELECT COUNT(*) FROM regex_patterns")
        patterns_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM search_priorities")
        priorities_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM system_config")
        config_count = cursor.fetchone()[0]
        
        cursor.close()
        conn.close()
        
        logger.info(f"✅ Verificação concluída:")
        logger.info(f"   - Tabelas criadas: {', '.join(tables)}")
        logger.info(f"   - Padrões regex: {patterns_count}")
        logger.info(f"   - Prioridades: {priorities_count}")
        logger.info(f"   - Configurações: {config_count}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Erro na verificação: {e}")
        return False

def main():
    """Função principal"""
    logger.info("🚀 Iniciando população do banco de dados PostgreSQL")
    
    # Testar conexão
    if not test_connection():
        sys.exit(1)
    
    # Criar tabelas
    if not create_tables():
        sys.exit(1)
    
    # Inserir dados
    if not insert_regex_patterns():
        sys.exit(1)
    
    if not insert_search_priorities():
        sys.exit(1)
    
    if not insert_system_config():
        sys.exit(1)
    
    # Verificar resultado
    if not verify_database():
        sys.exit(1)
    
    logger.info("🎉 População do banco de dados concluída com sucesso!")
    return True

if __name__ == "__main__":
    main()
EOF

echo "🚀 Executando script de população..."

# Executar script de população
python3 populate-database.py

if [ $? -eq 0 ]; then
    echo "✅ Script de população executado com sucesso"
else
    echo "❌ Erro ao executar script de população"
    exit 1
fi

echo "🔐 Configurando permissões..."

# Definir permissões corretas
chown -R privacy:privacy $INSTALL_DIR
chmod +x populate-database.py

echo "🚀 Reiniciando serviço..."

# Reiniciar serviço
systemctl restart privacy

echo "⏳ Aguardando inicialização..."
sleep 10

echo "🧪 Testando aplicação..."

# Verificar se a aplicação responde
if curl -f -s http://localhost:5000 > /dev/null; then
    echo "✅ Aplicação respondendo corretamente"
else
    echo "❌ Aplicação não responde, verificando logs..."
    journalctl -u privacy --no-pager -l -n 20
fi

echo ""
echo "================================================================="
echo "✅ CORREÇÃO RÁPIDA CONCLUÍDA!"
echo "================================================================="
echo "🗄️ Banco: $DB_NAME"
echo "👤 Usuário: $DB_USER"
echo "📁 Diretório: $INSTALL_DIR"
echo ""
echo "📋 Comandos úteis:"
echo "   sudo systemctl status privacy"
echo "   sudo journalctl -u privacy -f"
echo "   sudo -u postgres psql -d $DB_NAME -c 'SELECT COUNT(*) FROM regex_patterns;'"
echo "=================================================================" 