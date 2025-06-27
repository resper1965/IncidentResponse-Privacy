#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Módulo de gerenciamento do banco de dados SQLite
Implementa CRUD para dados extraídos com foco em LGPD
"""

import sqlite3
import os
from datetime import datetime
from pathlib import Path

# Nome do banco de dados
DB_NAME = "lgpd_data.db"

# Campos considerados de alta prioridade
CAMPOS_ALTA_PRIORIDADE = ['cpf', 'rg', 'email', 'telefone']

def obter_conexao():
    """
    Obtém conexão com o banco de dados SQLite
    
    Returns:
        sqlite3.Connection: Conexão com o banco
    """
    try:
        conn = sqlite3.connect(DB_NAME)
        conn.row_factory = sqlite3.Row  # Permite acesso por nome de coluna
        return conn
    except Exception as e:
        print(f"❌ Erro ao conectar com banco: {str(e)}")
        return None

def inicializar_banco():
    """
    Inicializa o banco de dados com as tabelas necessárias
    """
    try:
        conn = obter_conexao()
        if not conn:
            return False
        
        cursor = conn.cursor()
        
        # Criar tabela principal de dados extraídos
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS dados_extraidos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
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
        
        # Criar tabela de logs de processamento
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS logs_processamento (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                arquivo TEXT NOT NULL,
                status TEXT NOT NULL,
                mensagem TEXT,
                data_processamento TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Criar tabela de empresas prioritárias
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS empresas_prioritarias (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome_empresa TEXT NOT NULL UNIQUE,
                observacoes TEXT,
                email_contato TEXT,
                ativa BOOLEAN DEFAULT 1,
                data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Criar índices para melhor performance
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_arquivo 
            ON dados_extraidos(arquivo)
        ''')
        
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_campo 
            ON dados_extraidos(campo)
        ''')
        
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_prioridade 
            ON dados_extraidos(prioridade)
        ''')
        
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_titular 
            ON dados_extraidos(titular)
        ''')
        
        conn.commit()
        conn.close()
        
        print("✅ Banco de dados inicializado com sucesso")
        return True
        
    except Exception as e:
        print(f"❌ Erro ao inicializar banco: {str(e)}")
        return False

def verificar_prioridade(campo):
    """
    Verifica a prioridade de um campo de dados
    
    Args:
        campo (str): Nome do campo
        
    Returns:
        str: 'Alta' ou 'Baixa'
    """
    return 'Alta' if campo.lower() in CAMPOS_ALTA_PRIORIDADE else 'Baixa'

def inserir_dado(arquivo, titular, campo, valor, contexto, prioridade, origem_identificacao):
    """
    Insere um dado extraído no banco
    
    Args:
        arquivo (str): Caminho do arquivo de origem
        titular (str): Titular do dado
        campo (str): Tipo do campo (cpf, email, etc.)
        valor (str): Valor encontrado
        contexto (str): Contexto ao redor do dado
        prioridade (str): Prioridade do dado
        origem_identificacao (str): Como o titular foi identificado
        
    Returns:
        bool: True se inserido com sucesso
    """
    try:
        conn = obter_conexao()
        if not conn:
            return False
        
        cursor = conn.cursor()
        
        # Verificar se o dado já existe (evitar duplicatas)
        cursor.execute('''
            SELECT id FROM dados_extraidos 
            WHERE arquivo = ? AND campo = ? AND valor = ?
        ''', (arquivo, campo, valor))
        
        if cursor.fetchone():
            print(f"    ℹ️  Dado já existe no banco: {campo} = {valor}")
            conn.close()
            return True
        
        # Inserir novo dado
        cursor.execute('''
            INSERT INTO dados_extraidos 
            (arquivo, titular, campo, valor, contexto, prioridade, origem_identificacao)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (arquivo, titular, campo, valor, contexto, prioridade, origem_identificacao))
        
        conn.commit()
        conn.close()
        
        return True
        
    except Exception as e:
        print(f"❌ Erro ao inserir dado no banco: {str(e)}")
        return False

def registrar_log(arquivo, status, mensagem=""):
    """
    Registra log de processamento
    
    Args:
        arquivo (str): Arquivo processado
        status (str): Status do processamento
        mensagem (str): Mensagem adicional
    """
    try:
        conn = obter_conexao()
        if not conn:
            return
        
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO logs_processamento (arquivo, status, mensagem)
            VALUES (?, ?, ?)
        ''', (arquivo, status, mensagem))
        
        conn.commit()
        conn.close()
        
    except Exception as e:
        print(f"❌ Erro ao registrar log: {str(e)}")

def obter_estatisticas():
    """
    Obtém estatísticas gerais dos dados
    
    Returns:
        dict: Dicionário com estatísticas
    """
    try:
        conn = obter_conexao()
        if not conn:
            return {}
        
        cursor = conn.cursor()
        
        stats = {}
        
        # Total de dados encontrados
        cursor.execute("SELECT COUNT(*) FROM dados_extraidos")
        stats['total_dados'] = cursor.fetchone()[0]
        
        # Arquivos processados
        cursor.execute("SELECT COUNT(DISTINCT arquivo) FROM dados_extraidos")
        stats['arquivos_processados'] = cursor.fetchone()[0]
        
        # Titulares identificados
        cursor.execute('''
            SELECT COUNT(DISTINCT titular) FROM dados_extraidos 
            WHERE titular != 'Não identificado'
        ''')
        stats['titulares_identificados'] = cursor.fetchone()[0]
        
        # Dados de alta prioridade
        cursor.execute("SELECT COUNT(*) FROM dados_extraidos WHERE prioridade = 'Alta'")
        stats['dados_alta_prioridade'] = cursor.fetchone()[0]
        
        # Distribuição por tipo de campo
        cursor.execute('''
            SELECT campo, COUNT(*) as quantidade 
            FROM dados_extraidos 
            GROUP BY campo 
            ORDER BY quantidade DESC
        ''')
        stats['distribuicao_campos'] = dict(cursor.fetchall())
        
        # Distribuição por origem de identificação
        cursor.execute('''
            SELECT origem_identificacao, COUNT(*) as quantidade 
            FROM dados_extraidos 
            GROUP BY origem_identificacao
        ''')
        stats['distribuicao_origem'] = dict(cursor.fetchall())
        
        conn.close()
        return stats
        
    except Exception as e:
        print(f"❌ Erro ao obter estatísticas: {str(e)}")
        return {}

def obter_dados_prioritarios():
    """
    Obtém lista de dados de alta prioridade
    
    Returns:
        list: Lista de dados prioritários
    """
    try:
        conn = obter_conexao()
        if not conn:
            return []
        
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT arquivo, titular, campo, valor, contexto, origem_identificacao, data_extracao
            FROM dados_extraidos 
            WHERE prioridade = 'Alta'
            ORDER BY data_extracao DESC
        ''')
        
        dados = []
        for row in cursor.fetchall():
            dados.append({
                'arquivo': row['arquivo'],
                'titular': row['titular'],
                'campo': row['campo'],
                'valor': row['valor'],
                'contexto': row['contexto'],
                'origem_identificacao': row['origem_identificacao'],
                'data_extracao': row['data_extracao']
            })
        
        conn.close()
        return dados
        
    except Exception as e:
        print(f"❌ Erro ao obter dados prioritários: {str(e)}")
        return []

def obter_todos_dados(filtro_origem=None):
    """
    Obtém todos os dados extraídos com filtro opcional
    
    Args:
        filtro_origem (str): Filtrar por origem de identificação
        
    Returns:
        list: Lista de todos os dados
    """
    try:
        conn = obter_conexao()
        if not conn:
            return []
        
        cursor = conn.cursor()
        
        if filtro_origem:
            cursor.execute('''
                SELECT * FROM dados_extraidos 
                WHERE origem_identificacao = ?
                ORDER BY data_extracao DESC
            ''', (filtro_origem,))
        else:
            cursor.execute('''
                SELECT * FROM dados_extraidos 
                ORDER BY data_extracao DESC
            ''')
        
        dados = []
        for row in cursor.fetchall():
            dados.append(dict(row))
        
        conn.close()
        return dados
        
    except Exception as e:
        print(f"❌ Erro ao obter todos os dados: {str(e)}")
        return []

def limpar_dados():
    """
    Remove todos os dados do banco (útil para reset)
    
    Returns:
        bool: True se limpeza foi bem-sucedida
    """
    try:
        conn = obter_conexao()
        if not conn:
            return False
        
        cursor = conn.cursor()
        
        cursor.execute("DELETE FROM dados_extraidos")
        cursor.execute("DELETE FROM logs_processamento")
        
        conn.commit()
        conn.close()
        
        print("✅ Banco de dados limpo com sucesso")
        return True
        
    except Exception as e:
        print(f"❌ Erro ao limpar banco: {str(e)}")
        return False

def backup_banco(caminho_backup=None):
    """
    Cria backup do banco de dados
    
    Args:
        caminho_backup (str): Caminho para o backup
        
    Returns:
        bool: True se backup foi criado
    """
    try:
        if not caminho_backup:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            caminho_backup = f"backup_lgpd_{timestamp}.db"
        
        # Copiar arquivo do banco
        import shutil
        shutil.copy2(DB_NAME, caminho_backup)
        
        print(f"✅ Backup criado: {caminho_backup}")
        return True
        
    except Exception as e:
        print(f"❌ Erro ao criar backup: {str(e)}")
        return False

# Funções para gerenciar empresas prioritárias

def inserir_empresa_prioritaria(nome_empresa, observacoes="", email_contato=""):
    """
    Insere uma empresa prioritária no banco
    
    Args:
        nome_empresa (str): Nome da empresa
        observacoes (str): Observações sobre a empresa
        email_contato (str): Email de contato
        
    Returns:
        bool: True se inserido com sucesso
    """
    try:
        conn = obter_conexao()
        if not conn:
            return False
        
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO empresas_prioritarias 
            (nome_empresa, observacoes, email_contato)
            VALUES (?, ?, ?)
        ''', (nome_empresa.upper().strip(), observacoes.strip(), email_contato.strip()))
        
        conn.commit()
        conn.close()
        
        return True
        
    except Exception as e:
        print(f"❌ Erro ao inserir empresa prioritária: {str(e)}")
        return False

def obter_empresas_prioritarias():
    """
    Obtém lista de empresas prioritárias
    
    Returns:
        list: Lista de empresas prioritárias
    """
    try:
        conn = obter_conexao()
        if not conn:
            return []
        
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, nome_empresa, observacoes, email_contato, ativa, data_criacao
            FROM empresas_prioritarias 
            WHERE ativa = 1
            ORDER BY nome_empresa
        ''')
        
        empresas = []
        for row in cursor.fetchall():
            empresas.append({
                'id': row['id'],
                'nome_empresa': row['nome_empresa'],
                'observacoes': row['observacoes'],
                'email_contato': row['email_contato'],
                'ativa': row['ativa'],
                'data_criacao': row['data_criacao']
            })
        
        conn.close()
        return empresas
        
    except Exception as e:
        print(f"❌ Erro ao obter empresas prioritárias: {str(e)}")
        return []

def remover_empresa_prioritaria(empresa_id):
    """
    Remove uma empresa prioritária (marca como inativa)
    
    Args:
        empresa_id (int): ID da empresa
        
    Returns:
        bool: True se removida com sucesso
    """
    try:
        conn = obter_conexao()
        if not conn:
            return False
        
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE empresas_prioritarias 
            SET ativa = 0
            WHERE id = ?
        ''', (empresa_id,))
        
        conn.commit()
        conn.close()
        
        return True
        
    except Exception as e:
        print(f"❌ Erro ao remover empresa prioritária: {str(e)}")
        return False

def verificar_empresa_prioritaria(texto_titular):
    """
    Verifica se um titular corresponde a uma empresa prioritária
    
    Args:
        texto_titular (str): Texto do titular
        
    Returns:
        dict: Informações da empresa prioritária ou None
    """
    try:
        empresas = obter_empresas_prioritarias()
        texto_upper = texto_titular.upper()
        
        for empresa in empresas:
            nome_empresa = empresa['nome_empresa']
            
            # Verifica se o nome da empresa está contido no texto do titular
            if nome_empresa in texto_upper or any(palavra in texto_upper for palavra in nome_empresa.split()):
                return empresa
        
        return None
        
    except Exception as e:
        print(f"❌ Erro ao verificar empresa prioritária: {str(e)}")
        return None

def carregar_empresas_padrao():
    """
    Carrega lista padrão de empresas prioritárias
    """
    empresas_padrao = [
        {"nome": "BRADESCO", "email": "contato@bradesco.com.br", "obs": ""},
        {"nome": "PETROBRAS", "email": "contato@petrobras.com.br", "obs": "Topologia"},
        {"nome": "ONS", "email": "contato@ons.org.br", "obs": ""},
        {"nome": "EMBRAER", "email": "contato@embraer.com.br", "obs": ""},
        {"nome": "REDE DOR", "email": "contato@rededor.com.br", "obs": "Retorno até 16/06"},
        {"nome": "ED GLOBO", "email": "contato@infoglobo.com.br", "obs": ""},
        {"nome": "GLOBO", "email": "contato@g.globo", "obs": ""},
        {"nome": "ELETROBRAS", "email": "contato@eletrobras.com", "obs": "Retorno até 13/06"},
        {"nome": "CREFISA", "email": "contato@crefisa.com.br", "obs": ""},
        {"nome": "EQUINIX", "email": "contato@equinix.com", "obs": ""},
        {"nome": "COHESITY", "email": "contato@cohesity.com", "obs": ""},
        {"nome": "NETAPP", "email": "contato@netapp.com", "obs": ""},
        {"nome": "HITACHI", "email": "contato@hitachivantara.com", "obs": ""},
        {"nome": "LENOVO", "email": "contato@lenovo.com", "obs": ""},
    ]
    
    for empresa in empresas_padrao:
        inserir_empresa_prioritaria(
            nome_empresa=empresa["nome"],
            observacoes=empresa["obs"],
            email_contato=empresa["email"]
        )

# Função de teste para o módulo
if __name__ == "__main__":
    print("=== TESTE DO MÓDULO DATABASE ===")
    
    # Inicializar banco
    if inicializar_banco():
        print("✅ Banco inicializado")
        
        # Inserir dados de teste
        dados_teste = [
            {
                'arquivo': 'teste.txt',
                'titular': 'João Silva',
                'campo': 'cpf',
                'valor': '123.456.789-01',
                'contexto': 'Nome: João Silva CPF: 123.456.789-01',
                'prioridade': verificar_prioridade('cpf'),
                'origem_identificacao': 'regex'
            },
            {
                'arquivo': 'teste.txt',
                'titular': 'Maria Santos',
                'campo': 'email',
                'valor': 'maria@email.com',
                'contexto': 'Contato: Maria Santos - maria@email.com',
                'prioridade': verificar_prioridade('email'),
                'origem_identificacao': 'ia_spacy'
            }
        ]
        
        print("\nInserindo dados de teste...")
        for dado in dados_teste:
            sucesso = inserir_dado(**dado)
            if sucesso:
                print(f"  ✅ Inserido: {dado['campo']} = {dado['valor']}")
        
        # Obter estatísticas
        print("\nEstatísticas:")
        stats = obter_estatisticas()
        for chave, valor in stats.items():
            print(f"  {chave}: {valor}")
        
        # Dados prioritários
        print("\nDados prioritários:")
        prioritarios = obter_dados_prioritarios()
        for dado in prioritarios:
            print(f"  {dado['campo']}: {dado['valor']} (Titular: {dado['titular']})")
    
    else:
        print("❌ Falha ao inicializar banco")
