#!/usr/bin/env python3
"""
Script de População do Banco PostgreSQL - n.crisisops
Popular padrões regex e prioridades de busca
"""

import os
import sys
import psycopg2
from psycopg2.extras import execute_values

# Configurações do banco
DATABASE_CONFIG = {
    'host': 'localhost',
    'port': 5432,
    'database': 'privacy',
    'user': 'privacy',
    'password': 'ncrisisops_secure_2025'
}

# Prioridades de busca padrão
SEARCH_PRIORITIES = [
    (1, 'BRADESCO', 'bradesco.com.br'),
    (2, 'PETROBRAS', 'petrobras.com.br'),
    (3, 'ONS', 'ons.org.br'),
    (4, 'EMBRAER', 'embraer.com.br'),
    (5, 'REDE DOR', 'rededor.com.br'),
    (6, 'ED GLOBO', 'edglobo.com.br'),
    (7, 'GLOBO', 'globo.com'),
    (8, 'ELETROBRAS', 'eletrobras.com'),
    (9, 'CREFISA', 'crefisa.com.br'),
    (10, 'EQUINIX', 'equinix.com'),
    (11, 'COHESITY', 'cohesity.com'),
    (12, 'NETAPP', 'netapp.com'),
    (13, 'HITACHI', 'hitachi.com'),
    (14, 'LENOVO', 'lenovo.com'),
    (15, 'VALE', 'vale.com'),
    (16, 'ITAU', 'itau.com.br'),
    (17, 'SANTANDER', 'santander.com.br'),
    (18, 'BTG PACTUAL', 'btgpactual.com'),
    (19, 'AMBEV', 'ambev.com.br'),
    (20, 'JBS', 'jbs.com.br'),
    (21, 'MAGAZINE LUIZA', 'magazineluiza.com.br'),
    (22, 'B3', 'b3.com.br'),
    (23, 'LOCALIZA', 'localiza.com'),
    (24, 'WEG', 'weg.net'),
    (25, 'SUZANO', 'suzano.com.br'),
]

# Padrões regex padrão
REGEX_PATTERNS = [
    ('cpf', r'\b\d{3}\.?\d{3}\.?\d{3}-?\d{2}\b', 'CPF no formato XXX.XXX.XXX-XX ou apenas dígitos'),
    ('rg', r'\b\d{1,2}\.?\d{3}\.?\d{3}-?[0-9X]\b', 'RG no formato XX.XXX.XXX-X'),
    ('cnh', r'\b\d{11}\b', 'CNH com 11 dígitos'),
    ('passaporte', r'\b[A-Z]{2}\d{6}\b', 'Passaporte brasileiro formato AAXXXXXX'),
    ('email', r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', 'Endereço de email válido'),
    ('telefone', r'\b(?:\+55\s?)?(?:\(\d{2}\)\s?)?(?:9\s?)?\d{4}-?\d{4}\b', 'Telefone brasileiro com ou sem código de área'),
    ('celular', r'\b(?:\+55\s?)?(?:\(\d{2}\)\s?)?9\d{4}-?\d{4}\b', 'Celular brasileiro'),
    ('cep', r'\b\d{5}-?\d{3}\b', 'CEP no formato XXXXX-XXX'),
    ('conta_bancaria', r'\b\d{4,8}-?\d{1}\b', 'Conta bancária com dígito verificador'),
    ('agencia', r'\b\d{4}-?\d{1}\b', 'Agência bancária'),
    ('cartao_credito', r'\b(?:\d{4}\s?){3}\d{4}\b', 'Cartão de crédito 16 dígitos'),
    ('pis_pasep', r'\b\d{3}\.?\d{5}\.?\d{2}-?\d{1}\b', 'PIS/PASEP'),
    ('titulo_eleitor', r'\b\d{4}\s?\d{4}\s?\d{4}\b', 'Título de eleitor'),
    ('cnpj', r'\b\d{2}\.?\d{3}\.?\d{3}\/?\d{4}-?\d{2}\b', 'CNPJ formato XX.XXX.XXX/XXXX-XX'),
    ('endereco', r'\b(?:Rua|Av|Avenida|R\.|Al|Alameda|Tv|Travessa|Pç|Praça)\s+[^,\n]+,?\s*\d+', 'Endereço com logradouro e número'),
    ('placa_veiculo', r'\b[A-Z]{3}-?\d{4}\b', 'Placa de veículo formato ABC-1234'),
    ('renavam', r'\b\d{11}\b', 'RENAVAM com 11 dígitos'),
    ('certidao_nascimento', r'\b\d{6}\s?\d{2}\s?\d{2}\s?\d{4}\s?\d{1}\s?\d{5}\s?\d{3}\s?\d{7}\s?\d{2}\b', 'Certidão de nascimento'),
    ('numero_sus', r'\b\d{15}\b', 'Número do SUS com 15 dígitos'),
    ('nis', r'\b\d{11}\b', 'NIS - Número de Identificação Social'),
]

def connect_database():
    """Conecta ao banco PostgreSQL"""
    try:
        conn = psycopg2.connect(**DATABASE_CONFIG)
        return conn
    except psycopg2.Error as e:
        print(f"Erro ao conectar ao banco: {e}")
        sys.exit(1)

def populate_search_priorities(conn):
    """Popula tabela search_priorities"""
    print("Inserindo prioridades de busca...")
    
    cursor = conn.cursor()
    
    # Limpar tabela
    cursor.execute("TRUNCATE TABLE search_priorities RESTART IDENTITY CASCADE;")
    
    # Inserir dados
    insert_query = """
        INSERT INTO search_priorities (priority, company_name, email_domain, is_active)
        VALUES %s
    """
    
    data = [(priority, company, domain, True) for priority, company, domain in SEARCH_PRIORITIES]
    
    execute_values(cursor, insert_query, data)
    
    # Verificar inserção
    cursor.execute("SELECT COUNT(*) FROM search_priorities;")
    count = cursor.fetchone()[0]
    print(f"✅ {count} prioridades de busca inseridas")
    
    cursor.close()

def populate_regex_patterns(conn):
    """Popula tabela regex_patterns"""
    print("Inserindo padrões regex...")
    
    cursor = conn.cursor()
    
    # Limpar tabela
    cursor.execute("TRUNCATE TABLE regex_patterns RESTART IDENTITY CASCADE;")
    
    # Inserir dados
    insert_query = """
        INSERT INTO regex_patterns (field_name, regex_pattern, explanation, is_active)
        VALUES %s
    """
    
    data = [(field, pattern, explanation, True) for field, pattern, explanation in REGEX_PATTERNS]
    
    execute_values(cursor, insert_query, data)
    
    # Verificar inserção
    cursor.execute("SELECT COUNT(*) FROM regex_patterns;")
    count = cursor.fetchone()[0]
    print(f"✅ {count} padrões regex inseridos")
    
    cursor.close()

def show_statistics(conn):
    """Mostra estatísticas dos dados inseridos"""
    print("\n📊 Estatísticas do banco:")
    
    cursor = conn.cursor()
    
    # Mostrar prioridades
    cursor.execute("""
        SELECT priority, company_name, email_domain 
        FROM search_priorities 
        WHERE is_active = true 
        ORDER BY priority 
        LIMIT 10;
    """)
    
    print("\n🏢 Top 10 Prioridades de Busca:")
    for row in cursor.fetchall():
        print(f"  {row[0]:2d}. {row[1]} ({row[2]})")
    
    # Mostrar padrões
    cursor.execute("""
        SELECT field_name, explanation 
        FROM regex_patterns 
        WHERE is_active = true 
        ORDER BY field_name;
    """)
    
    print("\n🔍 Padrões Regex Configurados:")
    for row in cursor.fetchall():
        print(f"  • {row[0]}: {row[1]}")
    
    cursor.close()

def main():
    """Função principal"""
    print("🗄️ Populando banco de dados PostgreSQL - n.crisisops")
    print("=" * 60)
    
    # Conectar ao banco
    conn = connect_database()
    
    try:
        # Popular tabelas
        populate_search_priorities(conn)
        populate_regex_patterns(conn)
        
        # Commit das transações
        conn.commit()
        
        # Mostrar estatísticas
        show_statistics(conn)
        
        print("\n✅ População do banco concluída com sucesso!")
        
    except Exception as e:
        print(f"❌ Erro durante a população: {e}")
        conn.rollback()
        sys.exit(1)
        
    finally:
        conn.close()

if __name__ == "__main__":
    main()