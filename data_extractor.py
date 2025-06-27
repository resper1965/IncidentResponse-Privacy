#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Módulo de extração de dados pessoais usando regex e IA
Implementa busca contextualizada e identificação de titulares
"""

import re
import spacy
from pathlib import Path

# Modelo spaCy global
nlp = None

# Padrões regex para dados pessoais brasileiros
REGEX_PATTERNS = {
    'cpf': r'\b\d{3}\.?\d{3}\.?\d{3}-?\d{2}\b',
    'rg': r'\b\d{1,2}\.?\d{3}\.?\d{3}-?\d{1}\b|\bRG\s*:?\s*\d{7,9}\b',
    'email': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
    'telefone': r'\b(?:\+55\s?)?\(?[1-9]{2}\)?\s?9?\d{4}-?\d{4}\b',
    'placa': r'\b[A-Z]{3}-?\d{4}\b|\b[A-Z]{3}\d[A-Z]\d{2}\b',
    'cep': r'\b\d{5}-?\d{3}\b',
    'ip': r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b',
    'data_nascimento': r'\b(?:0[1-9]|[12][0-9]|3[01])[\/\-](?:0[1-9]|1[012])[\/\-](?:19|20)\d{2}\b'
}

# Palavras-chave para identificação de titulares
PALAVRAS_TITULAR = [
    'nome', 'titular', 'contratante', 'cliente', 'responsável', 
    'parte', 'empresa', 'pessoa', 'indivíduo', 'portador',
    'proprietário', 'locatário', 'inquilino', 'comprador',
    'vendedor', 'paciente', 'usuário', 'candidato'
]

def inicializar_spacy():
    """
    Inicializa o modelo spaCy para português
    """
    global nlp
    
    try:
        # Tentar carregar modelo em português
        nlp = spacy.load("pt_core_news_lg")
        print("  ✅ Modelo spaCy pt_core_news_lg carregado com sucesso")
        
    except OSError:
        try:
            # Fallback para modelo menor
            nlp = spacy.load("pt_core_news_sm")
            print("  ✅ Modelo spaCy pt_core_news_sm carregado como fallback")
            
        except OSError:
            print("  ⚠️  Nenhum modelo spaCy em português encontrado")
            print("  ℹ️  Execute: python -m spacy download pt_core_news_lg")
            nlp = None
    
    except Exception as e:
        print(f"  ❌ Erro ao carregar spaCy: {str(e)}")
        nlp = None

def extrair_contexto(texto, posicao_inicio, posicao_fim, janela=150):
    """
    Extrai contexto ao redor de um dado encontrado
    
    Args:
        texto (str): Texto completo
        posicao_inicio (int): Posição inicial do dado
        posicao_fim (int): Posição final do dado
        janela (int): Tamanho da janela de contexto em caracteres
        
    Returns:
        str: Contexto extraído
    """
    inicio_contexto = max(0, posicao_inicio - janela)
    fim_contexto = min(len(texto), posicao_fim + janela)
    
    contexto = texto[inicio_contexto:fim_contexto]
    
    # Marcar o dado encontrado no contexto
    dado_encontrado = texto[posicao_inicio:posicao_fim]
    contexto_marcado = contexto.replace(
        dado_encontrado, 
        f"**{dado_encontrado}**", 
        1
    )
    
    return contexto_marcado

def buscar_titular_regex(contexto, valor_encontrado):
    """
    Busca titular usando palavras-chave no contexto
    
    Args:
        contexto (str): Contexto ao redor do dado
        valor_encontrado (str): Valor do dado encontrado
        
    Returns:
        tuple: (titular_encontrado, origem_identificacao)
    """
    titular = "Não identificado"
    origem = "nao_identificado"
    
    try:
        # Converter para minúsculas para busca
        contexto_lower = contexto.lower()
        
        # Buscar padrões de titular próximos ao dado
        for palavra_titular in PALAVRAS_TITULAR:
            # Padrão: palavra_titular seguida de dois pontos e texto
            pattern = rf'{palavra_titular}\s*:?\s*([A-Za-zÀ-ÿ\s]+?)(?:\n|\.|\,|;|$)'
            match = re.search(pattern, contexto_lower)
            
            if match:
                titular_candidato = match.group(1).strip()
                
                # Validar se é um nome válido (não vazio, não muito curto)
                if len(titular_candidato) > 3 and not titular_candidato.isdigit():
                    titular = titular_candidato.title()
                    origem = "regex"
                    break
        
        # Se não encontrou com padrão formal, buscar nomes próximos
        if origem == "nao_identificado":
            # Buscar palavras que parecem nomes (maiúsculas)
            nomes_candidatos = re.findall(r'\b[A-Z][a-z]+\s+[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b', contexto)
            
            if nomes_candidatos:
                # Pegar o primeiro nome encontrado
                titular = nomes_candidatos[0]
                origem = "regex"
        
    except Exception as e:
        print(f"    ⚠️  Erro na busca regex de titular: {str(e)}")
    
    return titular, origem

def buscar_titular_spacy(contexto, valor_encontrado):
    """
    Busca titular usando spaCy NER
    
    Args:
        contexto (str): Contexto ao redor do dado
        valor_encontrado (str): Valor do dado encontrado
        
    Returns:
        tuple: (titular_encontrado, origem_identificacao)
    """
    if not nlp:
        return "Não identificado", "nao_identificado"
    
    try:
        # Processar contexto com spaCy
        doc = nlp(contexto)
        
        # Buscar entidades de pessoa
        pessoas_encontradas = []
        
        for ent in doc.ents:
            if ent.label_ == "PER":  # Pessoa
                nome_pessoa = ent.text.strip()
                
                # Validar se é um nome válido
                if len(nome_pessoa) > 3 and not nome_pessoa.isdigit():
                    pessoas_encontradas.append(nome_pessoa)
        
        if pessoas_encontradas:
            # Retornar a primeira pessoa encontrada
            return pessoas_encontradas[0], "ia_spacy"
        
        # Se não encontrou PER, buscar ORG (organizações) como fallback
        for ent in doc.ents:
            if ent.label_ == "ORG":  # Organização
                nome_org = ent.text.strip()
                
                if len(nome_org) > 3:
                    return nome_org, "ia_spacy"
        
    except Exception as e:
        print(f"    ⚠️  Erro na busca spaCy de titular: {str(e)}")
    
    return "Não identificado", "nao_identificado"

def identificar_titular(contexto, valor_encontrado):
    """
    Identifica titular usando abordagem híbrida (regex + IA)
    
    Args:
        contexto (str): Contexto ao redor do dado
        valor_encontrado (str): Valor do dado encontrado
        
    Returns:
        tuple: (titular_encontrado, origem_identificacao)
    """
    # Tentar regex primeiro
    titular, origem = buscar_titular_regex(contexto, valor_encontrado)
    
    # Se regex não encontrou, tentar spaCy
    if origem == "nao_identificado":
        titular, origem = buscar_titular_spacy(contexto, valor_encontrado)
    
    return titular, origem

def validar_cpf(cpf):
    """
    Valida CPF usando algoritmo oficial
    """
    try:
        # Remover formatação
        cpf = re.sub(r'[^0-9]', '', cpf)
        
        if len(cpf) != 11:
            return False
        
        # Verificar se todos os dígitos são iguais
        if cpf == cpf[0] * 11:
            return False
        
        # Calcular primeiro dígito verificador
        soma = sum(int(cpf[i]) * (10 - i) for i in range(9))
        resto = soma % 11
        digito1 = 0 if resto < 2 else 11 - resto
        
        # Calcular segundo dígito verificador
        soma = sum(int(cpf[i]) * (11 - i) for i in range(10))
        resto = soma % 11
        digito2 = 0 if resto < 2 else 11 - resto
        
        return cpf[9] == str(digito1) and cpf[10] == str(digito2)
        
    except Exception:
        return False

def analisar_texto(texto, nome_arquivo):
    """
    Analisa texto e extrai dados pessoais com contexto
    
    Args:
        texto (str): Texto a ser analisado
        nome_arquivo (str): Nome do arquivo de origem
        
    Returns:
        list: Lista de dados encontrados
    """
    resultados = []
    
    if not texto or not texto.strip():
        return resultados
    
    try:
        # Processar cada tipo de dado
        for tipo_dado, pattern in REGEX_PATTERNS.items():
            matches = re.finditer(pattern, texto, re.IGNORECASE | re.MULTILINE)
            
            for match in matches:
                valor = match.group().strip()
                
                # Validações específicas
                if tipo_dado == 'cpf' and not validar_cpf(valor):
                    continue
                
                # Extrair contexto
                contexto = extrair_contexto(
                    texto, 
                    match.start(), 
                    match.end()
                )
                
                # Identificar titular
                titular, origem_identificacao = identificar_titular(contexto, valor)
                
                # Adicionar resultado
                resultado = {
                    'arquivo': nome_arquivo,
                    'campo': tipo_dado,
                    'valor': valor,
                    'contexto': contexto,
                    'titular': titular,
                    'origem_identificacao': origem_identificacao
                }
                
                resultados.append(resultado)
                
                print(f"    📋 {tipo_dado.upper()}: {valor} (Titular: {titular})")
    
    except Exception as e:
        print(f"    ❌ Erro na análise de texto: {str(e)}")
    
    return resultados

def extrair_nomes_completos(texto):
    """
    Extrai possíveis nomes completos do texto usando padrões
    
    Args:
        texto (str): Texto a ser analisado
        
    Returns:
        list: Lista de nomes encontrados
    """
    nomes = []
    
    try:
        # Padrão para nomes completos (2 ou mais palavras capitalizadas)
        pattern = r'\b[A-ZÀ-Ÿ][a-zà-ÿ]+(?:\s+[A-ZÀ-Ÿ][a-zà-ÿ]+){1,}\b'
        matches = re.findall(pattern, texto)
        
        for nome in matches:
            # Filtrar nomes muito comuns ou genéricos
            palavras_filtro = ['De', 'Da', 'Do', 'Das', 'Dos', 'E', 'O', 'A']
            
            # Validar se é realmente um nome
            palavras = nome.split()
            if len(palavras) >= 2 and not any(palavra in palavras_filtro for palavra in palavras):
                if len(nome) > 5:  # Nome mínimo
                    nomes.append(nome)
    
    except Exception as e:
        print(f"    ⚠️  Erro na extração de nomes: {str(e)}")
    
    return list(set(nomes))  # Remover duplicatas

# Função de teste para o módulo
if __name__ == "__main__":
    print("=== TESTE DO EXTRATOR DE DADOS ===")
    
    # Inicializar spaCy
    inicializar_spacy()
    
    # Texto de teste
    texto_teste = """
    CONTRATO DE LOCAÇÃO
    
    Nome do Locador: João Silva Santos
    CPF: 123.456.789-01
    E-mail: joao.silva@email.com
    Telefone: (11) 98765-4321
    
    Locatário: Maria Oliveira Costa
    RG: 12.345.678-9
    Data de Nascimento: 15/03/1985
    
    Endereço do imóvel: Rua das Flores, 123
    CEP: 01234-567
    """
    
    print("Analisando texto de teste...")
    resultados = analisar_texto(texto_teste, "teste.txt")
    
    print(f"\n✅ Análise concluída. {len(resultados)} dados encontrados:")
    
    for i, resultado in enumerate(resultados, 1):
        print(f"\n{i}. Tipo: {resultado['campo']}")
        print(f"   Valor: {resultado['valor']}")
        print(f"   Titular: {resultado['titular']}")
        print(f"   Origem: {resultado['origem_identificacao']}")
        print(f"   Contexto: {resultado['contexto'][:100]}...")
