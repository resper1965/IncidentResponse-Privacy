#!/usr/bin/env python3
"""
Setup de prioridades de busca para PostgreSQL
Sistema LGPD n.crisisops
"""

import os
import asyncio
import asyncpg

DATABASE_URL = os.getenv('DATABASE_URL')

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

async def setup():
    print("Configurando prioridades de busca no PostgreSQL...")
    
    conn = await asyncpg.connect(DATABASE_URL)
    
    # Cria tabela se necessário
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
    
    # Insere/atualiza prioridades
    for prioridade, nome_empresa, dominio_email in PRIORIDADES:
        await conn.execute('''
            INSERT INTO search_priorities (prioridade, nome_empresa, dominio_email)
            VALUES ($1, $2, $3)
            ON CONFLICT (prioridade) 
            DO UPDATE SET nome_empresa = $2, dominio_email = $3
        ''', prioridade, nome_empresa, dominio_email)
        print(f"Configurado: {nome_empresa} (Prioridade {prioridade})")
    
    # Lista resultado
    rows = await conn.fetch('SELECT * FROM search_priorities ORDER BY prioridade')
    print(f"\nTotal configurado: {len(rows)} prioridades")
    
    await conn.close()
    print("Configuração concluída")

if __name__ == "__main__":
    asyncio.run(setup())