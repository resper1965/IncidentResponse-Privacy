#!/usr/bin/env python3
"""
Merge de dados entre SQLite e PostgreSQL
Consolida prioridades e dados no banco principal
"""

import os
import asyncio
import asyncpg
import sqlite3
from datetime import datetime

DATABASE_URL = os.getenv('DATABASE_URL')

async def merge_priorities():
    """Merge prioridades entre SQLite e PostgreSQL"""
    print("🔄 Iniciando merge de prioridades...")
    
    # Conecta ao PostgreSQL
    pg_conn = await asyncpg.connect(DATABASE_URL)
    
    # Conecta ao SQLite
    sqlite_conn = sqlite3.connect('lgpd_data.db')
    sqlite_cursor = sqlite_conn.cursor()
    
    try:
        # Busca prioridades do SQLite
        sqlite_cursor.execute('''
            SELECT prioridade, nome_empresa, dominio_email, ativa
            FROM prioridade_busca 
            WHERE ativa = 1
        ''')
        sqlite_priorities = sqlite_cursor.fetchall()
        
        print(f"📋 Encontradas {len(sqlite_priorities)} prioridades no SQLite")
        
        # Busca prioridades do PostgreSQL
        pg_priorities = await pg_conn.fetch('''
            SELECT prioridade, nome_empresa, dominio_email, ativo
            FROM search_priorities 
            WHERE ativo = true
        ''')
        
        print(f"📋 Encontradas {len(pg_priorities)} prioridades no PostgreSQL")
        
        # Merge das prioridades
        merged = {}
        
        # Adiciona prioridades do PostgreSQL (principal)
        for row in pg_priorities:
            merged[row['prioridade']] = {
                'nome_empresa': row['nome_empresa'],
                'dominio_email': row['dominio_email'],
                'source': 'PostgreSQL'
            }
        
        # Adiciona prioridades do SQLite se não existirem no PostgreSQL
        for row in sqlite_priorities:
            prioridade, nome_empresa, dominio_email, ativa = row
            if prioridade not in merged:
                merged[prioridade] = {
                    'nome_empresa': nome_empresa,
                    'dominio_email': dominio_email,
                    'source': 'SQLite'
                }
                
                # Insere no PostgreSQL
                await pg_conn.execute('''
                    INSERT INTO search_priorities (prioridade, nome_empresa, dominio_email)
                    VALUES ($1, $2, $3)
                    ON CONFLICT (prioridade) DO NOTHING
                ''', prioridade, nome_empresa, dominio_email)
                
                print(f"✅ Migrada: {nome_empresa} (Prioridade {prioridade})")
        
        # Lista resultado final
        final_priorities = await pg_conn.fetch('''
            SELECT prioridade, nome_empresa, dominio_email, ativo
            FROM search_priorities 
            ORDER BY prioridade
        ''')
        
        print(f"\n📊 RESULTADO DO MERGE:")
        print("=" * 60)
        for row in final_priorities:
            status = "✅ Ativo" if row['ativo'] else "❌ Inativo"
            print(f"{row['prioridade']:2d}. {row['nome_empresa']:15s} | {row['dominio_email']:25s} | {status}")
        
        print(f"\n✅ Merge concluído: {len(final_priorities)} prioridades consolidadas")
        
    except Exception as e:
        print(f"❌ Erro durante merge: {e}")
        raise
    finally:
        sqlite_conn.close()
        await pg_conn.close()

async def merge_extracted_data():
    """Merge dados extraídos do SQLite para PostgreSQL"""
    print("\n🔄 Iniciando merge de dados extraídos...")
    
    pg_conn = await asyncpg.connect(DATABASE_URL)
    sqlite_conn = sqlite3.connect('lgpd_data.db')
    sqlite_cursor = sqlite_conn.cursor()
    
    try:
        # Verifica se tabela existe no SQLite
        sqlite_cursor.execute('''
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='dados_extraidos'
        ''')
        
        if not sqlite_cursor.fetchone():
            print("⚠️ Tabela dados_extraidos não encontrada no SQLite")
            return
        
        # Busca dados do SQLite
        sqlite_cursor.execute('''
            SELECT arquivo, titular, campo, valor, contexto, prioridade, origem_identificacao
            FROM dados_extraidos
        ''')
        sqlite_data = sqlite_cursor.fetchall()
        
        print(f"📋 Encontrados {len(sqlite_data)} registros no SQLite")
        
        if len(sqlite_data) == 0:
            print("ℹ️ Nenhum dado para migrar")
            return
        
        # Cria tabela no PostgreSQL se não existir
        await pg_conn.execute('''
            CREATE TABLE IF NOT EXISTS extracted_data (
                id SERIAL PRIMARY KEY,
                arquivo TEXT NOT NULL,
                titular TEXT NOT NULL,
                campo TEXT NOT NULL,
                valor TEXT NOT NULL,
                contexto TEXT,
                prioridade TEXT NOT NULL,
                origem_identificacao TEXT NOT NULL,
                data_extracao TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Migra dados
        migrated = 0
        for row in sqlite_data:
            arquivo, titular, campo, valor, contexto, prioridade, origem_identificacao = row
            
            # Verifica se já existe
            exists = await pg_conn.fetchval('''
                SELECT id FROM extracted_data 
                WHERE arquivo = $1 AND titular = $2 AND campo = $3 AND valor = $4
            ''', arquivo, titular, campo, valor)
            
            if not exists:
                await pg_conn.execute('''
                    INSERT INTO extracted_data 
                    (arquivo, titular, campo, valor, contexto, prioridade, origem_identificacao)
                    VALUES ($1, $2, $3, $4, $5, $6, $7)
                ''', arquivo, titular, campo, valor, contexto, prioridade, origem_identificacao)
                migrated += 1
        
        print(f"✅ Migrados {migrated} novos registros para PostgreSQL")
        
    except Exception as e:
        print(f"❌ Erro durante merge de dados: {e}")
    finally:
        sqlite_conn.close()
        await pg_conn.close()

async def main():
    """Executa merge completo"""
    print("🚀 Iniciando merge completo do banco de dados...")
    
    try:
        await merge_priorities()
        await merge_extracted_data()
        print("\n✅ Merge completo do banco concluído com sucesso!")
        
    except Exception as e:
        print(f"❌ Erro no merge: {e}")

if __name__ == "__main__":
    asyncio.run(main())