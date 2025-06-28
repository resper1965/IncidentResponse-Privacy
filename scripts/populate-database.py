#!/usr/bin/env python3
"""
Script para popular o banco de dados com dados iniciais
Usado durante o deploy de produção
"""

import os
import sys

def populate_database():
    """Popula o banco com dados iniciais"""
    try:
        # Tentar PostgreSQL primeiro
        import database_postgresql as db_pg
        print('✅ Conectado ao PostgreSQL')
        
        # Criar tabelas
        db_pg.initialize_database()
        print('✅ Tabelas criadas')
        
        # Carregar padrões regex inteligentes
        patterns = [
            ('cpf', r'\b\d{3}\.?\d{3}\.?\d{3}-?\d{2}\b', 'CPF brasileiro'),
            ('rg', r'\b\d{1,2}\.?\d{3}\.?\d{3}-?[\dX]\b', 'RG brasileiro'),
            ('email', r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', 'Email'),
            ('telefone', r'\b(?:\+55\s?)?(?:\(\d{2}\)\s?)?\d{4,5}-?\d{4}\b', 'Telefone brasileiro'),
            ('cnpj', r'\b\d{2}\.?\d{3}\.?\d{3}\/?\d{4}-?\d{2}\b', 'CNPJ'),
            ('pis', r'\b\d{3}\.?\d{5}\.?\d{2}-?\d{1}\b', 'PIS/PASEP'),
            ('titulo_eleitor', r'\b\d{4}\s?\d{4}\s?\d{4}\b', 'Título de eleitor'),
            ('cartao_credito', r'\b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}\b', 'Cartão de crédito'),
            ('cep', r'\b\d{5}-?\d{3}\b', 'CEP brasileiro'),
            ('data_nascimento', r'\b\d{1,2}[\/\-\.]\d{1,2}[\/\-\.]\d{4}\b', 'Data de nascimento')
        ]
        
        # Inserir padrões
        for nome, pattern, descricao in patterns:
            db_pg.insert_regex_pattern(nome, pattern, descricao)
        
        # Carregar prioridades empresariais
        priorities = [
            (1, 'Banco Bradesco', 'bradesco.com.br'),
            (1, 'Petrobras', 'petrobras.com.br'),
            (1, 'ONS', 'ons.org.br'),
            (2, 'Banco do Brasil', 'bb.com.br'),
            (2, 'Caixa Econômica Federal', 'caixa.gov.br'),
            (3, 'Itaú Unibanco', 'itau.com.br'),
            (3, 'Santander', 'santander.com.br'),
            (4, 'Nubank', 'nubank.com.br'),
            (4, 'Magazine Luiza', 'magazineluiza.com.br'),
            (5, 'Outros bancos', 'outros.com.br')
        ]
        
        for prioridade, empresa, dominio in priorities:
            db_pg.insert_search_priority(prioridade, empresa, dominio)
        
        print('✅ Dados iniciais carregados no PostgreSQL')
        return True
        
    except Exception as e:
        print(f'❌ Erro PostgreSQL: {e}')
        print('🔄 Tentando SQLite...')
        
        try:
            import database
            database.inicializar_banco()
            database.carregar_regex_padrao()
            database.carregar_prioridades_padrao()
            print('✅ Fallback SQLite configurado')
            return True
        except Exception as e2:
            print(f'❌ Erro SQLite: {e2}')
            return False

if __name__ == "__main__":
    if populate_database():
        print('✅ Database populated successfully')
        sys.exit(0)
    else:
        print('❌ Failed to populate database')
        sys.exit(1)