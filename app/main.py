#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Pipeline principal para processamento de documentos LGPD
Coordena a varredura, extração e armazenamento de dados pessoais
"""

import os
import sys
from file_scanner import listar_arquivos_recursivos
from file_reader import extrair_texto
from data_extractor import analisar_texto, inicializar_spacy
from database import (
    inicializar_banco, 
    inserir_dado, 
    verificar_prioridade,
    inserir_resultado_analise,
    extrair_dominio_de_email,
    verificar_empresa_prioritaria,
    obter_prioridades_busca
)

def processar_arquivos(diretorio_base="data"):
    """
    Pipeline principal que coordena todo o processo de extração
    
    Args:
        diretorio_base (str): Diretório base para varredura de arquivos
    """
    print("=== INICIANDO PIPELINE LGPD ===")
    
    # Inicializar componentes
    print("Inicializando banco de dados...")
    inicializar_banco()
    
    print("Carregando modelo spaCy...")
    inicializar_spacy()
    
    # Verificar se o diretório existe
    if not os.path.exists(diretorio_base):
        print(f"Diretório '{diretorio_base}' não encontrado.")
        return
    
    # Listar arquivos recursivamente
    print(f"Escaneando arquivos em '{diretorio_base}'...")
    arquivos = listar_arquivos_recursivos(diretorio_base)
    
    if not arquivos:
        print(f"Nenhum arquivo encontrado no diretório '{diretorio_base}'.")
        return
    
    print(f"Encontrados {len(arquivos)} arquivos para processamento.")
    
    # Processar cada arquivo
    arquivos_processados = 0
    arquivos_com_erro = 0
    total_dados_encontrados = 0
    
    for arquivo in arquivos:
        try:
            print(f"\nProcessando: {arquivo}")
            
            # Extrair texto do arquivo
            texto = extrair_texto(arquivo)
            
            if not texto.strip():
                print(f"  ⚠️  Arquivo vazio ou sem texto extraível: {arquivo}")
                continue
            
            # Analisar texto e extrair dados pessoais
            resultados = analisar_texto(texto, arquivo)
            
            if resultados:
                print(f"  ✅ Encontrados {len(resultados)} dados pessoais")
                total_dados_encontrados += len(resultados)
                
                # Inserir dados no banco
                for dado in resultados:
                    prioridade = verificar_prioridade(dado['campo'])
                    
                    # Inserir no banco original
                    inserir_dado(
                        arquivo=arquivo,
                        titular=dado['titular'],
                        campo=dado['campo'],
                        valor=dado['valor'],
                        contexto=dado['contexto'],
                        prioridade=prioridade,
                        origem_identificacao=dado['origem_identificacao']
                    )
                    
                    # Determinar domínio e empresa para nova tabela
                    dominio = ""
                    empresa = ""
                    
                    # Se o dado é um email, extrair domínio
                    if dado['campo'] == 'email':
                        dominio = extrair_dominio_de_email(dado['valor'])
                    
                    # Verificar se titular corresponde a empresa prioritária
                    empresa_info = verificar_empresa_prioritaria(dado['titular'])
                    if empresa_info:
                        empresa = empresa_info['nome_empresa']
                        if not dominio and empresa_info['email_contato']:
                            dominio = extrair_dominio_de_email(empresa_info['email_contato'])
                    else:
                        empresa = dado['titular']
                    
                    # Inserir na nova tabela de resultados
                    inserir_resultado_analise(
                        dominio=dominio,
                        empresa=empresa,
                        tipo_dado=dado['campo'],
                        valor_encontrado=dado['valor'],
                        arquivo_origem=arquivo,
                        contexto=dado['contexto'],
                        titular_identificado=dado['titular'],
                        metodo_identificacao=dado['origem_identificacao'],
                        prioridade=prioridade
                    )
            else:
                print(f"  ℹ️  Nenhum dado pessoal encontrado")
            
            arquivos_processados += 1
            
        except Exception as e:
            print(f"  ❌ Erro no arquivo {arquivo}: {str(e)}")
            arquivos_com_erro += 1
            continue
    
    # Relatório final
    print("\n=== RELATÓRIO FINAL ===")
    print(f"Arquivos processados com sucesso: {arquivos_processados}")
    print(f"Arquivos com erro: {arquivos_com_erro}")
    print(f"Total de dados pessoais encontrados: {total_dados_encontrados}")
    print("\nPara visualizar os resultados, execute:")
    print("streamlit run dashboard.py")

if __name__ == "__main__":
    try:
        processar_arquivos()
    except KeyboardInterrupt:
        print("\n\n⏹️  Processamento interrompido pelo usuário.")
    except Exception as e:
        print(f"\n❌ Erro crítico no pipeline: {str(e)}")
        sys.exit(1)
