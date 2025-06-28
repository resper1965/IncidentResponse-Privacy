#!/usr/bin/env python3
"""
Rotina para inserir prioridades de busca no banco PostgreSQL
Executa inserção das empresas prioritárias para o sistema LGPD
"""

import os
import sys
import asyncio
from datetime import datetime

try:
    import asyncpg
    ASYNCPG_AVAILABLE = True
except ImportError:
    ASYNCPG_AVAILABLE = False
    print("⚠️ asyncpg não disponível, usando fallback SQLite")

# Configuração do banco PostgreSQL
DATABASE_URL = os.getenv('DATABASE_URL')

# Prioridades de busca padrão
PRIORIDADES_PADRAO = [
    (1, "BRADESCO", "bradesco.com.br"),
    (2, "PETROBRAS", "petrobras.com.br"),
    (3, "ONS", "ons.org.br"),
    (4, "EMBRAER", "embraer.com.br"),
    (5, "REDE DOR", "rededorsaoluiz.com.br"),
    (6, "GLOBO", "globo.com"),
    (7, "ELETROBRAS", "eletrobras.com"),
    (8, "CREFISA", "crefisa.com.br"),
    (9, "EQUINIX", "equinix.com"),
    (10, "COHESITY", "cohesity.com")
]

async def criar_tabela_prioridades(conn):
    """Cria tabela de prioridades se não existir"""
    try:
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
        
        # Criar índices para performance
        await conn.execute('''
            CREATE INDEX IF NOT EXISTS idx_search_priorities_prioridade 
            ON search_priorities(prioridade)
        ''')
        
        await conn.execute('''
            CREATE INDEX IF NOT EXISTS idx_search_priorities_dominio 
            ON search_priorities(dominio_email)
        ''')
        
        print("✅ Tabela search_priorities criada/verificada")
        
    except Exception as e:
        print(f"❌ Erro ao criar tabela: {e}")
        raise

async def inserir_prioridade(conn, prioridade, nome_empresa, dominio_email):
    """Insere uma prioridade no banco"""
    try:
        # Verifica se já existe
        resultado = await conn.fetchrow(
            'SELECT id FROM search_priorities WHERE prioridade = $1 OR nome_empresa = $2',
            prioridade, nome_empresa
        )
        
        if resultado:
            # Atualiza se já existe
            await conn.execute('''
                UPDATE search_priorities 
                SET nome_empresa = $2, dominio_email = $3, atualizado_em = CURRENT_TIMESTAMP
                WHERE prioridade = $1
            ''', prioridade, nome_empresa, dominio_email)
            print(f"🔄 Atualizada: {nome_empresa} (Prioridade {prioridade})")
        else:
            # Insere nova prioridade
            await conn.execute('''
                INSERT INTO search_priorities (prioridade, nome_empresa, dominio_email)
                VALUES ($1, $2, $3)
            ''', prioridade, nome_empresa, dominio_email)
            print(f"✅ Inserida: {nome_empresa} (Prioridade {prioridade})")
            
    except Exception as e:
        print(f"❌ Erro ao inserir {nome_empresa}: {e}")

async def listar_prioridades(conn):
    """Lista todas as prioridades cadastradas"""
    try:
        rows = await conn.fetch('''
            SELECT prioridade, nome_empresa, dominio_email, ativo, criado_em
            FROM search_priorities
            ORDER BY prioridade ASC
        ''')
        
        print("\n📋 PRIORIDADES DE BUSCA CADASTRADAS:")
        print("=" * 60)
        
        for row in rows:
            status = "✅ Ativo" if row['ativo'] else "❌ Inativo"
            print(f"{row['prioridade']:2d}. {row['nome_empresa']:15s} | {row['dominio_email']:25s} | {status}")
        
        print(f"\nTotal: {len(rows)} prioridades cadastradas")
        
    except Exception as e:
        print(f"❌ Erro ao listar prioridades: {e}")

def inserir_sqlite():
    """Fallback para SQLite quando PostgreSQL não está disponível"""
    try:
        from database import inserir_prioridade_busca, obter_prioridades_busca
        
        print("📥 Inserindo prioridades no SQLite...")
        
        for prioridade, nome_empresa, dominio_email in PRIORIDADES_PADRAO:
            try:
                inserir_prioridade_busca(prioridade, nome_empresa, dominio_email)
                print(f"✅ Inserida: {nome_empresa} (Prioridade {prioridade})")
            except Exception as e:
                print(f"🔄 Já existe ou erro: {nome_empresa} - {e}")
        
        # Lista prioridades cadastradas
        prioridades = obter_prioridades_busca()
        print("\n📋 PRIORIDADES CADASTRADAS (SQLite):")
        print("=" * 60)
        
        for prio in prioridades:
            print(f"{prio[1]:2d}. {prio[2]:15s} | {prio[3]:25s} | {'✅ Ativo' if prio[4] else '❌ Inativo'}")
        
        print(f"\nTotal: {len(prioridades)} prioridades cadastradas")
        print("✅ Prioridades inseridas com sucesso no SQLite!")
        
    except Exception as e:
        print(f"❌ Erro SQLite: {e}")

async def main():
    """Função principal"""
    print("🚀 Iniciando inserção de prioridades de busca...")
    
    if not ASYNCPG_AVAILABLE or not DATABASE_URL:
        print("📋 Usando SQLite como fallback...")
        inserir_sqlite()
        return
    
    try:
        # Conecta ao banco PostgreSQL
        print("🔌 Conectando ao PostgreSQL...")
        conn = await asyncpg.connect(DATABASE_URL)
        
        # Cria tabela se necessário
        await criar_tabela_prioridades(conn)
        
        # Insere prioridades padrão
        print("\n📥 Inserindo prioridades padrão...")
        for prioridade, nome_empresa, dominio_email in PRIORIDADES_PADRAO:
            await inserir_prioridade(conn, prioridade, nome_empresa, dominio_email)
        
        # Lista prioridades cadastradas
        await listar_prioridades(conn)
        
        # Fecha conexão
        await conn.close()
        print("\n✅ Prioridades inseridas com sucesso no PostgreSQL!")
        
    except Exception as e:
        print(f"❌ Erro PostgreSQL: {e}")
        print("📋 Tentando fallback SQLite...")
        inserir_sqlite()

if __name__ == "__main__":
    # Executa rotina
    asyncio.run(main())