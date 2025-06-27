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
        
        # Criar tabela de resultados por domínio/empresa
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS resultados_analise (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                dominio TEXT NOT NULL,
                empresa TEXT NOT NULL,
                tipo_dado TEXT NOT NULL,
                valor_encontrado TEXT NOT NULL,
                arquivo_origem TEXT NOT NULL,
                contexto TEXT,
                titular_identificado TEXT,
                metodo_identificacao TEXT,
                prioridade TEXT NOT NULL,
                data_analise TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                status_compliance TEXT DEFAULT 'PENDENTE'
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
        
        # Criar tabela de prioridade de busca
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS prioridade_busca (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                prioridade INTEGER NOT NULL,
                nome_empresa TEXT NOT NULL,
                dominio_email TEXT NOT NULL,
                ativa BOOLEAN DEFAULT TRUE,
                data_criacao DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Criar tabela de padrões regex
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS regex_patterns (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome_campo TEXT NOT NULL UNIQUE,
                pattern_regex TEXT NOT NULL,
                explicacao TEXT,
                ativo BOOLEAN DEFAULT TRUE,
                data_criacao DATETIME DEFAULT CURRENT_TIMESTAMP
            )
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
    Verifica a prioridade de um campo de dados baseada na criticidade LGPD
    
    Args:
        campo (str): Nome do campo
        
    Returns:
        str: 'Alta', 'Média' ou 'Baixa'
    """
    # Classificação por Criticidade conforme LGPD
    campos_alta_prioridade = ['cpf', 'rg', 'telefone', 'email', 'data_nascimento']
    campos_media_prioridade = ['cep', 'placa_veiculo', 'ip']
    campos_baixa_prioridade = ['nome_completo']
    
    campo_lower = campo.lower()
    
    if campo_lower in campos_alta_prioridade:
        return 'Alta'
    elif campo_lower in campos_media_prioridade:
        return 'Média'
    elif campo_lower in campos_baixa_prioridade:
        return 'Baixa'
    else:
        return 'Média'  # Padrão para novos campos

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

# Funções para a nova tabela de resultados por domínio/empresa

def inserir_resultado_analise(dominio, empresa, tipo_dado, valor_encontrado, arquivo_origem, 
                             contexto, titular_identificado, metodo_identificacao, prioridade):
    """
    Insere resultado de análise na tabela com filtros por domínio e empresa
    
    Args:
        dominio (str): Domínio da empresa (ex: bradesco.com.br)
        empresa (str): Nome da empresa
        tipo_dado (str): Tipo do dado (cpf, email, etc.)
        valor_encontrado (str): Valor encontrado
        arquivo_origem (str): Arquivo de origem
        contexto (str): Contexto ao redor do dado
        titular_identificado (str): Titular identificado
        metodo_identificacao (str): Método usado para identificação
        prioridade (str): Prioridade do dado
        
    Returns:
        bool: True se inserido com sucesso
    """
    try:
        conn = obter_conexao()
        if not conn:
            return False
        
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO resultados_analise 
            (dominio, empresa, tipo_dado, valor_encontrado, arquivo_origem, 
             contexto, titular_identificado, metodo_identificacao, prioridade)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (dominio, empresa, tipo_dado, valor_encontrado, arquivo_origem,
              contexto, titular_identificado, metodo_identificacao, prioridade))
        
        conn.commit()
        conn.close()
        
        return True
        
    except Exception as e:
        print(f"❌ Erro ao inserir resultado de análise: {str(e)}")
        return False

def obter_resultados_por_dominio(dominio=None):
    """
    Obtém resultados filtrados por domínio
    
    Args:
        dominio (str): Domínio para filtrar (opcional)
        
    Returns:
        list: Lista de resultados
    """
    try:
        conn = obter_conexao()
        if not conn:
            return []
        
        cursor = conn.cursor()
        
        if dominio:
            cursor.execute('''
                SELECT * FROM resultados_analise 
                WHERE dominio = ?
                ORDER BY data_analise DESC
            ''', (dominio,))
        else:
            cursor.execute('''
                SELECT * FROM resultados_analise 
                ORDER BY data_analise DESC
            ''')
        
        resultados = []
        for row in cursor.fetchall():
            resultados.append(dict(row))
        
        conn.close()
        return resultados
        
    except Exception as e:
        print(f"❌ Erro ao obter resultados por domínio: {str(e)}")
        return []

def obter_resultados_por_empresa(empresa=None):
    """
    Obtém resultados filtrados por empresa
    
    Args:
        empresa (str): Nome da empresa para filtrar (opcional)
        
    Returns:
        list: Lista de resultados
    """
    try:
        conn = obter_conexao()
        if not conn:
            return []
        
        cursor = conn.cursor()
        
        if empresa:
            cursor.execute('''
                SELECT * FROM resultados_analise 
                WHERE empresa LIKE ?
                ORDER BY data_analise DESC
            ''', (f'%{empresa}%',))
        else:
            cursor.execute('''
                SELECT * FROM resultados_analise 
                ORDER BY data_analise DESC
            ''')
        
        resultados = []
        for row in cursor.fetchall():
            resultados.append(dict(row))
        
        conn.close()
        return resultados
        
    except Exception as e:
        print(f"❌ Erro ao obter resultados por empresa: {str(e)}")
        return []

def obter_dominios_unicos():
    """
    Obtém lista de domínios únicos
    
    Returns:
        list: Lista de domínios únicos
    """
    try:
        conn = obter_conexao()
        if not conn:
            return []
        
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT DISTINCT dominio FROM resultados_analise 
            ORDER BY dominio
        ''')
        
        dominios = [row[0] for row in cursor.fetchall()]
        
        conn.close()
        return dominios
        
    except Exception as e:
        print(f"❌ Erro ao obter domínios únicos: {str(e)}")
        return []

def obter_empresas_unicas():
    """
    Obtém lista de empresas únicas
    
    Returns:
        list: Lista de empresas únicas
    """
    try:
        conn = obter_conexao()
        if not conn:
            return []
        
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT DISTINCT empresa FROM resultados_analise 
            ORDER BY empresa
        ''')
        
        empresas = [row[0] for row in cursor.fetchall()]
        
        conn.close()
        return empresas
        
    except Exception as e:
        print(f"❌ Erro ao obter empresas únicas: {str(e)}")
        return []

def extrair_dominio_de_email(email):
    """
    Extrai domínio de um email
    
    Args:
        email (str): Email para extrair domínio
        
    Returns:
        str: Domínio extraído ou string vazia
    """
    try:
        if '@' in email:
            return email.split('@')[1].lower()
        return ""
    except:
        return ""

# === FUNÇÕES DE PRIORIDADE DE BUSCA ===

def inserir_prioridade_busca(prioridade, nome_empresa, dominio_email):
    """
    Insere uma nova prioridade de busca
    
    Args:
        prioridade (int): Nível de prioridade (1 = mais alta)
        nome_empresa (str): Nome da empresa
        dominio_email (str): Domínio do email da empresa
        
    Returns:
        bool: True se inserido com sucesso
    """
    try:
        conn = obter_conexao()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO prioridade_busca (prioridade, nome_empresa, dominio_email)
            VALUES (?, ?, ?)
        ''', (prioridade, nome_empresa, dominio_email))
        
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Erro ao inserir prioridade de busca: {e}")
        return False

def obter_prioridades_busca():
    """
    Obtém lista de prioridades de busca ordenada por prioridade
    
    Returns:
        list: Lista de prioridades de busca
    """
    try:
        conn = obter_conexao()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, prioridade, nome_empresa, dominio_email, ativa, data_criacao
            FROM prioridade_busca
            WHERE ativa = TRUE
            ORDER BY prioridade ASC
        ''')
        
        prioridades = []
        for row in cursor.fetchall():
            prioridades.append({
                'id': row[0],
                'prioridade': row[1],
                'nome_empresa': row[2],
                'dominio_email': row[3],
                'ativa': row[4],
                'data_criacao': row[5]
            })
        
        conn.close()
        return prioridades
    except Exception as e:
        print(f"Erro ao obter prioridades de busca: {e}")
        return []

def remover_prioridade_busca(prioridade_id):
    """
    Remove uma prioridade de busca (marca como inativa)
    
    Args:
        prioridade_id (int): ID da prioridade
        
    Returns:
        bool: True se removida com sucesso
    """
    try:
        conn = obter_conexao()
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE prioridade_busca 
            SET ativa = FALSE 
            WHERE id = ?
        ''', (prioridade_id,))
        
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Erro ao remover prioridade de busca: {e}")
        return False

def carregar_prioridades_padrao():
    """
    Carrega prioridades de busca padrão
    """
    prioridades_padrao = [
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
    
    for prioridade, nome, dominio in prioridades_padrao:
        inserir_prioridade_busca(prioridade, nome, dominio)

# === FUNÇÕES DE PADRÕES REGEX ===

def inserir_regex_pattern(nome_campo, pattern_regex, explicacao=""):
    """
    Insere um novo padrão regex
    
    Args:
        nome_campo (str): Nome do campo
        pattern_regex (str): Padrão regex
        explicacao (str): Explicação do padrão
        
    Returns:
        bool: True se inserido com sucesso
    """
    try:
        conn = obter_conexao()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO regex_patterns (nome_campo, pattern_regex, explicacao)
            VALUES (?, ?, ?)
        ''', (nome_campo, pattern_regex, explicacao))
        
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Erro ao inserir padrão regex: {e}")
        return False

def obter_regex_patterns():
    """
    Obtém lista de padrões regex ativos
    
    Returns:
        list: Lista de padrões regex
    """
    try:
        conn = obter_conexao()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, nome_campo, pattern_regex, explicacao, ativo, data_criacao
            FROM regex_patterns
            WHERE ativo = TRUE
            ORDER BY nome_campo ASC
        ''')
        
        patterns = []
        for row in cursor.fetchall():
            patterns.append({
                'id': row[0],
                'nome_campo': row[1],
                'pattern_regex': row[2],
                'explicacao': row[3],
                'ativo': row[4],
                'data_criacao': row[5]
            })
        
        conn.close()
        return patterns
    except Exception as e:
        print(f"Erro ao obter padrões regex: {e}")
        return []

def carregar_regex_padrao():
    """
    Carrega padrões regex padrão baseados na estrutura inteligente
    """
    patterns_padrao = [
        ("nome_completo", r"\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+){1,})\b", "Nome composto, mínimo dois nomes"),
        ("cpf", r"\b\d{3}[.\s-]?\d{3}[.\s-]?\d{3}[-\s]?\d{2}\b", "Variações com e sem máscara"),
        ("rg", r"\b\d{1,2}[.\s-]?\d{3}[.\s-]?\d{3}[-\s]?[0-9Xx]\b", "Variações com e sem máscara, com dígito X"),
        ("email", r"\b[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}\b", "Formato internacional de e-mail"),
        ("telefone", r"\b(\(?\d{2}\)?[\s-]?)?(9?\d{4})[\s-]?\d{4}\b", "Formatos com ou sem DDD"),
        ("data_nascimento", r"\b(0?[1-9]|[12][0-9]|3[01])[/\-\.](0?[1-9]|1[0-2])[/\-\.](?:19|20)?\d{2}\b", "Formato brasileiro de data"),
        ("placa_veiculo", r"\b([A-Z]{3}[-\s]?\d{4})\b", "Padrão antigo de placa brasileira"),
        ("cep", r"\b\d{5}[-\s]?\d{3}\b", "Variações com e sem hífen"),
        ("ip", r"\b(?:\d{1,3}\.){3}\d{1,3}\b", "IPv4")
    ]
    
    for nome, pattern, explicacao in patterns_padrao:
        inserir_regex_pattern(nome, pattern, explicacao)

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
