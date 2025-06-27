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
from database import inicializar_banco, inserir_dado, verificar_prioridade

def processar_arquivos():
    """
    Pipeline principal que coordena todo o processo de extração
    """
    print("=== INICIANDO PIPELINE LGPD ===")
    
    # Inicializar componentes
    print("Inicializando banco de dados...")
    inicializar_banco()
    
    print("Carregando modelo spaCy...")
    inicializar_spacy()
    
    # Verificar se a pasta data existe
    if not os.path.exists('data'):
        os.makedirs('data')
        print("Pasta 'data' criada. Adicione arquivos para processamento.")
        return
    
    # Listar arquivos recursivamente
    print("Escaneando arquivos...")
    arquivos = listar_arquivos_recursivos('data')
    
    if not arquivos:
        print("Nenhum arquivo encontrado na pasta 'data'.")
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
                    inserir_dado(
                        arquivo=arquivo,
                        titular=dado['titular'],
                        campo=dado['campo'],
                        valor=dado['valor'],
                        contexto=dado['contexto'],
                        prioridade=prioridade,
                        origem_identificacao=dado['origem_identificacao']
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
