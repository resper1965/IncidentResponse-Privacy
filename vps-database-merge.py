#!/usr/bin/env python3
"""
Merge específico para banco PostgreSQL na VPS
Consolida e sincroniza dados sem afetar aplicação rodando
"""

import asyncio
import asyncpg
import os
from urllib.parse import quote_plus

# URL encode the password to handle special characters
password = quote_plus('Lgpd2025#Privacy')
DATABASE_URL = f"postgresql://privacy_user:{password}@localhost:5432/privacy_db"

PRIORIDADES = [
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

async def merge_database():
    print("Iniciando merge do banco PostgreSQL...")
    
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
        
        # Criar índices para performance
        await conn.execute('''
            CREATE INDEX IF NOT EXISTS idx_search_priorities_prioridade 
            ON search_priorities(prioridade)
        ''')
        
        await conn.execute('''
            CREATE INDEX IF NOT EXISTS idx_search_priorities_empresa 
            ON search_priorities(nome_empresa)
        ''')
        
        # Merge das prioridades
        for prioridade, nome_empresa, dominio_email in PRIORIDADES:
            await conn.execute('''
                INSERT INTO search_priorities (prioridade, nome_empresa, dominio_email)
                VALUES ($1, $2, $3)
                ON CONFLICT (prioridade) DO UPDATE SET 
                    nome_empresa = EXCLUDED.nome_empresa,
                    dominio_email = EXCLUDED.dominio_email,
                    atualizado_em = CURRENT_TIMESTAMP
            ''', prioridade, nome_empresa, dominio_email)
            print(f"Merged: {nome_empresa} (Prioridade {prioridade})")
        
        # Verificar resultado
        total = await conn.fetchval('SELECT COUNT(*) FROM search_priorities WHERE ativo = true')
        print(f"Total de prioridades ativas: {total}")
        
        # Listar prioridades
        rows = await conn.fetch('''
            SELECT prioridade, nome_empresa, dominio_email, ativo
            FROM search_priorities 
            ORDER BY prioridade
        ''')
        
        print("\nPrioridades configuradas:")
        for row in rows:
            status = "Ativo" if row['ativo'] else "Inativo"
            print(f"{row['prioridade']:2d}. {row['nome_empresa']:15s} | {row['dominio_email']:25s} | {status}")
        
        await conn.close()
        print("Merge concluído com sucesso")
        
    except Exception as e:
        print(f"Erro no merge: {e}")
        return False
    
    return True

if __name__ == "__main__":
    asyncio.run(merge_database())