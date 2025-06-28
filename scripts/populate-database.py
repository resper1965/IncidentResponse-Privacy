#!/usr/bin/env python3
"""
Script para popular o banco de dados com dados iniciais
Usado durante o deploy de produção
"""

import os
import sys
import sqlite3
from pathlib import Path

def populate_database():
    """Popula o banco com dados iniciais"""
    try:
        # Usar SQLite diretamente para garantir compatibilidade
        db_path = "lgpd_data.db"
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        print('✅ Conectado ao banco SQLite')
        
        # Criar tabelas se não existirem
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS regex_patterns (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome_campo TEXT NOT NULL,
                pattern_regex TEXT NOT NULL,
                explicacao TEXT,
                ativo BOOLEAN DEFAULT 1,
                data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS prioridades_busca (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                prioridade INTEGER NOT NULL,
                nome_empresa TEXT NOT NULL,
                dominio_email TEXT NOT NULL,
                ativo BOOLEAN DEFAULT 1,
                data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        print('✅ Tabelas criadas')
        
        # Carregar padrões regex completos e avançados
        patterns = [
            # Documentos brasileiros principais
            ('cpf', r'(?:CPF[:\s]*)?(?:\d{3}\.?\d{3}\.?\d{3}[-\.]?\d{2})', 'CPF brasileiro com validação'),
            ('rg', r'(?:RG[:\s]*)?(?:\d{1,2}\.?\d{3}\.?\d{3}[-\.]?[\dX])', 'RG brasileiro'),
            ('cnpj', r'(?:CNPJ[:\s]*)?(?:\d{2}\.?\d{3}\.?\d{3}\/?\d{4}[-\.]?\d{2})', 'CNPJ empresarial'),
            
            # Documentos pessoais secundários
            ('pis', r'(?:PIS[:\s]*|PASEP[:\s]*)?(?:\d{3}\.?\d{5}\.?\d{2}[-\.]?\d{1})', 'PIS/PASEP'),
            ('titulo_eleitor', r'(?:Título[:\s]*|Eleitor[:\s]*)?(?:\d{4}[\s\.]?\d{4}[\s\.]?\d{4})', 'Título de eleitor'),
            ('ctps', r'(?:CTPS[:\s]*|Carteira[:\s]*)?(?:\d{7}[-\.]?\d{1})', 'Carteira de Trabalho'),
            ('nis', r'(?:NIS[:\s]*)?(?:\d{11})', 'Número de Identificação Social'),
            ('cnh', r'(?:CNH[:\s]*)?(?:\d{11})', 'Carteira Nacional de Habilitação'),
            
            # Dados financeiros
            ('cartao_credito', r'(?:Cartão[:\s]*)?(?:\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4})', 'Cartão de crédito'),
            ('conta_bancaria', r'(?:Conta[:\s]*|C/C[:\s]*)?(?:\d{4,6}[-\.]?\d{1,2})', 'Conta bancária'),
            ('agencia', r'(?:Agência[:\s]*|Ag[:\s]*)?(?:\d{4}[-\.]?\d{1})', 'Agência bancária'),
            ('pix', r'(?:PIX[:\s]*)?(?:\+55\d{11}|[\w\.-]+@[\w\.-]+\.\w+|\d{11,14})', 'Chave PIX'),
            
            # Dados de contato
            ('email', r'(?:E-?mail[:\s]*)?([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})', 'Email'),
            ('telefone', r'(?:Tel[:\s]*|Fone[:\s]*|Celular[:\s]*)?(?:\+?55[\s\-]?)?(?:\(?\d{2}\)?[\s\-]?)?\d{4,5}[\s\-]?\d{4}', 'Telefone brasileiro'),
            ('whatsapp', r'(?:WhatsApp[:\s]*|Zap[:\s]*)?(?:\+?55[\s\-]?)?(?:\(?\d{2}\)?[\s\-]?)?\d{5}[\s\-]?\d{4}', 'WhatsApp'),
            
            # Endereços
            ('cep', r'(?:CEP[:\s]*)?(?:\d{5}[-\.]?\d{3})', 'CEP brasileiro'),
            ('endereco', r'(?:Endereço[:\s]*|Rua[:\s]*|Av[:\s]*|Avenida[:\s]*)([\w\s,\.\-]+\d+)', 'Endereço completo'),
            
            # Dados pessoais sensíveis
            ('data_nascimento', r'(?:Nascimento[:\s]*|Data[:\s]*)?(?:\d{1,2}[\/\-\.]\d{1,2}[\/\-\.]\d{4})', 'Data de nascimento'),
            ('nome_completo', r'(?:Nome[:\s]*)?([A-ZÁÊÔÇÃ][a-záêôçã]+(?:\s+[A-ZÁÊÔÇÃ][a-záêôçã]+){1,})', 'Nome completo brasileiro'),
            ('nome_mae', r'(?:Mãe[:\s]*|Filiação[:\s]*)?([A-ZÁÊÔÇÃ][a-záêôçã]+(?:\s+[A-ZÁÊÔÇÃ][a-záêôçã]+){1,})', 'Nome da mãe'),
            ('nome_pai', r'(?:Pai[:\s]*)?([A-ZÁÊÔÇÃ][a-záêôçã]+(?:\s+[A-ZÁÊÔÇÃ][a-záêôçã]+){1,})', 'Nome do pai'),
            
            # Dados de saúde
            ('sus', r'(?:SUS[:\s]*|CNS[:\s]*)?(?:\d{15})', 'Cartão SUS'),
            ('plano_saude', r'(?:Plano[:\s]*|Convênio[:\s]*)?(?:\d{10,16})', 'Número plano de saúde'),
            
            # Dados educacionais
            ('cpf_responsavel', r'(?:Responsável[:\s]*|CPF[:\s]*Resp[:\s]*)?(?:\d{3}\.?\d{3}\.?\d{3}[-\.]?\d{2})', 'CPF do responsável'),
            ('matricula', r'(?:Matrícula[:\s]*|RA[:\s]*)?(?:\d{6,12})', 'Número de matrícula'),
            
            # Dados trabalhistas
            ('salario', r'(?:Salário[:\s]*|Renda[:\s]*)?(?:R\$[\s]?)(?:\d{1,3}(?:\.\d{3})*(?:,\d{2})?)', 'Salário'),
            ('cargo', r'(?:Cargo[:\s]*|Função[:\s]*)([\w\s]+)', 'Cargo/função'),
            
            # Dados biométricos e físicos
            ('biometria', r'(?:Digital[:\s]*|Biometria[:\s]*)', 'Dados biométricos'),
            ('foto', r'(?:Foto[:\s]*|Imagem[:\s]*)', 'Fotografia'),
            
            # Senhas e códigos de acesso
            ('senha', r'(?:Senha[:\s]*|Password[:\s]*|Pass[:\s]*)', 'Senha de acesso'),
            ('token', r'(?:Token[:\s]*|Código[:\s]*)', 'Token de acesso'),
            
            # Dados específicos LGPD
            ('ip_address', r'(?:\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})', 'Endereço IP'),
            ('cookies', r'(?:Cookie[:\s]*)', 'Dados de cookies'),
            ('localizacao', r'(?:GPS[:\s]*|Localização[:\s]*)', 'Dados de localização'),
            
            # Dados jurídicos
            ('oab', r'(?:OAB[:\s]*)?(?:\d{6})', 'Número OAB'),
            ('processo', r'(?:Processo[:\s]*)?(?:\d{7}[-\.]?\d{2}\.\d{4}\.\d{1}\.\d{2}\.\d{4})', 'Número de processo'),
            
            # Identificadores únicos
            ('protocolo', r'(?:Protocolo[:\s]*)?(?:\d{10,20})', 'Número de protocolo'),
            ('codigo_cliente', r'(?:Cliente[:\s]*|Código[:\s]*)?(?:\d{6,12})', 'Código de cliente')
        ]
        
        # Inserir padrões regex
        cursor.execute("DELETE FROM regex_patterns")  # Limpar dados antigos
        for nome, pattern, descricao in patterns:
            cursor.execute(
                "INSERT INTO regex_patterns (nome_campo, pattern_regex, explicacao) VALUES (?, ?, ?)",
                (nome, pattern, descricao)
            )
        
        # Carregar prioridades empresariais completas (setor financeiro e crítico)
        priorities = [
            # PRIORIDADE MÁXIMA (1) - Clientes críticos do sistema financeiro
            (1, 'Banco Bradesco S.A.', 'bradesco.com.br'),
            (1, 'Petróleo Brasileiro S.A. - Petrobras', 'petrobras.com.br'),
            (1, 'Operador Nacional do Sistema Elétrico - ONS', 'ons.org.br'),
            (1, 'Banco Central do Brasil', 'bcb.gov.br'),
            (1, 'Comissão de Valores Mobiliários - CVM', 'cvm.gov.br'),
            
            # PRIORIDADE ALTA (2) - Grandes bancos públicos e privados
            (2, 'Banco do Brasil S.A.', 'bb.com.br'),
            (2, 'Caixa Econômica Federal', 'caixa.gov.br'),
            (2, 'Itaú Unibanco S.A.', 'itau.com.br'),
            (2, 'Banco Santander Brasil S.A.', 'santander.com.br'),
            (2, 'Banco BTG Pactual S.A.', 'btgpactual.com'),
            
            # PRIORIDADE MÉDIA-ALTA (3) - Fintechs e bancos digitais
            (3, 'Nu Pagamentos S.A. (Nubank)', 'nubank.com.br'),
            (3, 'Banco Inter S.A.', 'bancointer.com.br'),
            (3, 'Banco Original S.A.', 'original.com.br'),
            (3, 'Banco C6 S.A.', 'c6bank.com.br'),
            (3, 'Banco Next (Bradesco)', 'next.me'),
            
            # PRIORIDADE MÉDIA (4) - Empresas de energia e telecomunicações
            (4, 'Centrais Elétricas Brasileiras S.A. - Eletrobras', 'eletrobras.com'),
            (4, 'CPFL Energia S.A.', 'cpfl.com.br'),
            (4, 'Enel Brasil S.A.', 'enel.com.br'),
            (4, 'Telefônica Brasil S.A. (Vivo)', 'telefonica.com.br'),
            (4, 'TIM S.A.', 'tim.com.br'),
            (4, 'Claro S.A.', 'claro.com.br'),
            
            # PRIORIDADE MÉDIA-BAIXA (5) - Varejo e e-commerce
            (5, 'Magazine Luiza S.A.', 'magazineluiza.com.br'),
            (5, 'B2W Digital (Americanas)', 'americanas.com.br'),
            (5, 'Via S.A. (Casas Bahia)', 'viavarejo.com.br'),
            (5, 'Mercado Livre Brasil Ltda.', 'mercadolivre.com.br'),
            (5, 'Amazon Brasil', 'amazon.com.br'),
            
            # PRIORIDADE BAIXA (6) - Seguradoras e previdência
            (6, 'Bradesco Seguros S.A.', 'bradescoseguros.com.br'),
            (6, 'SulAmérica S.A.', 'sulamerica.com.br'),
            (6, 'Porto Seguro S.A.', 'portoseguro.com.br'),
            (6, 'Itaú Seguros S.A.', 'itauseguros.com.br'),
            
            # PRIORIDADE MÍNIMA (7) - Órgãos públicos e governo
            (7, 'Ministério da Fazenda', 'fazenda.gov.br'),
            (7, 'Receita Federal do Brasil', 'receita.fazenda.gov.br'),
            (7, 'Tribunal de Contas da União', 'tcu.gov.br'),
            (7, 'Controladoria-Geral da União', 'cgu.gov.br'),
            
            # PRIORIDADE ESPECIAL (8) - Cooperativas de crédito
            (8, 'Sicredi', 'sicredi.com.br'),
            (8, 'Sicoob', 'sicoob.com.br'),
            (8, 'Unicred', 'unicred.com.br'),
            
            # PRIORIDADE GENÉRICA (9) - Outros domínios importantes
            (9, 'Empresa genérica', 'empresa.com.br'),
            (9, 'Organização padrão', 'organizacao.org.br'),
            (9, 'Instituição governamental', 'gov.br')
        ]
        
        # Inserir prioridades empresariais
        for prioridade, empresa, dominio in priorities:
            database.inserir_prioridade_busca(prioridade, empresa, dominio)
        
        print('✅ Dados iniciais carregados com sucesso')
        print(f'✅ {len(patterns)} padrões regex inseridos')
        print(f'✅ {len(priorities)} prioridades empresariais inseridas')
        return True
        
    except Exception as e:
        print(f'❌ Erro ao popular banco: {e}')
        return False

if __name__ == "__main__":
    if populate_database():
        print('✅ Database populated successfully')
        sys.exit(0)
    else:
        print('❌ Failed to populate database')
        sys.exit(1)