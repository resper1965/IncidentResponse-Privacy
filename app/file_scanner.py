#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Módulo de varredura recursiva de arquivos
Suporta múltiplos formatos de documento
"""

import os
from pathlib import Path

# Extensões suportadas
EXTENSOES_SUPORTADAS = {
    '.txt',   # Arquivos de texto
    '.pdf',   # Documentos PDF
    '.docx',  # Documentos Word
    '.xlsx',  # Planilhas Excel
    '.csv',   # Arquivos CSV
    '.msg'    # E-mails do Outlook
}

def listar_arquivos_recursivos(diretorio_base):
    """
    Varre recursivamente um diretório em busca de arquivos suportados
    
    Args:
        diretorio_base (str): Caminho do diretório base para varredura
        
    Returns:
        list: Lista de caminhos de arquivos encontrados
    """
    arquivos_encontrados = []
    
    try:
        # Converter para Path para facilitar navegação
        caminho_base = Path(diretorio_base)
        
        if not caminho_base.exists():
            print(f"❌ Diretório não encontrado: {diretorio_base}")
            return arquivos_encontrados
        
        if not caminho_base.is_dir():
            print(f"❌ Caminho não é um diretório: {diretorio_base}")
            return arquivos_encontrados
        
        # Varredura recursiva usando glob
        for extensao in EXTENSOES_SUPORTADAS:
            # Buscar arquivos com a extensão específica recursivamente
            pattern = f"**/*{extensao}"
            arquivos_extensao = list(caminho_base.glob(pattern))
            
            for arquivo in arquivos_extensao:
                if arquivo.is_file():
                    arquivos_encontrados.append(str(arquivo))
                    print(f"📄 Arquivo encontrado: {arquivo}")
        
        # Ordenar arquivos por nome para processamento consistente
        arquivos_encontrados.sort()
        
        print(f"\n📊 Total de arquivos encontrados: {len(arquivos_encontrados)}")
        
        # Estatísticas por extensão
        estatisticas = {}
        for arquivo in arquivos_encontrados:
            ext = Path(arquivo).suffix.lower()
            estatisticas[ext] = estatisticas.get(ext, 0) + 1
        
        print("📈 Distribuição por tipo:")
        for ext, count in estatisticas.items():
            print(f"  {ext}: {count} arquivo(s)")
        
    except Exception as e:
        print(f"❌ Erro durante varredura de arquivos: {str(e)}")
    
    return arquivos_encontrados

def verificar_arquivo_suportado(caminho_arquivo):
    """
    Verifica se um arquivo específico é suportado pelo sistema
    
    Args:
        caminho_arquivo (str): Caminho do arquivo a verificar
        
    Returns:
        bool: True se o arquivo é suportado, False caso contrário
    """
    try:
        arquivo_path = Path(caminho_arquivo)
        
        if not arquivo_path.exists():
            return False
        
        if not arquivo_path.is_file():
            return False
        
        extensao = arquivo_path.suffix.lower()
        return extensao in EXTENSOES_SUPORTADAS
        
    except Exception:
        return False

def obter_informacoes_arquivo(caminho_arquivo):
    """
    Obtém informações detalhadas sobre um arquivo
    
    Args:
        caminho_arquivo (str): Caminho do arquivo
        
    Returns:
        dict: Dicionário com informações do arquivo
    """
    try:
        arquivo_path = Path(caminho_arquivo)
        
        if not arquivo_path.exists():
            return None
        
        stat = arquivo_path.stat()
        
        return {
            'nome': arquivo_path.name,
            'caminho_completo': str(arquivo_path),
            'extensao': arquivo_path.suffix.lower(),
            'tamanho_bytes': stat.st_size,
            'tamanho_mb': round(stat.st_size / (1024 * 1024), 2),
            'modificado': stat.st_mtime,
            'suportado': verificar_arquivo_suportado(caminho_arquivo)
        }
        
    except Exception as e:
        print(f"❌ Erro ao obter informações do arquivo {caminho_arquivo}: {str(e)}")
        return None

# Função de teste para o módulo
if __name__ == "__main__":
    print("=== TESTE DO SCANNER DE ARQUIVOS ===")
    
    # Criar diretório de teste se não existir
    if not os.path.exists('data'):
        os.makedirs('data')
        print("Pasta 'data' criada para testes.")
    
    # Executar varredura
    arquivos = listar_arquivos_recursivos('data')
    
    if arquivos:
        print(f"\n✅ Varredura concluída. {len(arquivos)} arquivos encontrados.")
        
        # Mostrar informações detalhadas dos primeiros 5 arquivos
        print("\n📋 Detalhes dos arquivos (máximo 5):")
        for i, arquivo in enumerate(arquivos[:5]):
            info = obter_informacoes_arquivo(arquivo)
            if info:
                print(f"  {i+1}. {info['nome']} ({info['tamanho_mb']} MB)")
    else:
        print("ℹ️  Nenhum arquivo encontrado. Adicione arquivos na pasta 'data' para teste.")
