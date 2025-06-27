#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Módulo de leitura de arquivos com suporte a múltiplos formatos
Inclui capacidade de OCR para PDFs escaneados
"""

import os
import re
from pathlib import Path
import pandas as pd
import pdfplumber
from docx import Document
import extract_msg
import pytesseract
from PIL import Image
import io

def extrair_texto(caminho_arquivo):
    """
    Extrai texto de diferentes formatos de arquivo
    
    Args:
        caminho_arquivo (str): Caminho do arquivo a ser processado
        
    Returns:
        str: Texto extraído do arquivo
    """
    try:
        arquivo_path = Path(caminho_arquivo)
        extensao = arquivo_path.suffix.lower()
        
        print(f"  📖 Lendo arquivo: {arquivo_path.name}")
        
        if extensao == '.txt':
            return extrair_texto_txt(caminho_arquivo)
        elif extensao == '.pdf':
            return extrair_texto_pdf(caminho_arquivo)
        elif extensao == '.docx':
            return extrair_texto_docx(caminho_arquivo)
        elif extensao == '.xlsx':
            return extrair_texto_xlsx(caminho_arquivo)
        elif extensao == '.csv':
            return extrair_texto_csv(caminho_arquivo)
        elif extensao == '.msg':
            return extrair_texto_msg(caminho_arquivo)
        else:
            print(f"  ⚠️  Formato não suportado: {extensao}")
            return ""
            
    except Exception as e:
        print(f"  ❌ Erro ao extrair texto: {str(e)}")
        return ""

def extrair_texto_txt(caminho_arquivo):
    """
    Extrai texto de arquivo .txt
    """
    try:
        # Tentar diferentes encodings
        encodings = ['utf-8', 'latin-1', 'cp1252', 'iso-8859-1']
        
        for encoding in encodings:
            try:
                with open(caminho_arquivo, 'r', encoding=encoding) as arquivo:
                    return arquivo.read()
            except UnicodeDecodeError:
                continue
        
        # Se nenhum encoding funcionou, usar bytes
        with open(caminho_arquivo, 'rb') as arquivo:
            conteudo = arquivo.read()
            return conteudo.decode('utf-8', errors='ignore')
            
    except Exception as e:
        print(f"    ❌ Erro ao ler arquivo TXT: {str(e)}")
        return ""

def extrair_texto_pdf(caminho_arquivo):
    """
    Extrai texto de PDF usando pdfplumber e OCR como fallback
    """
    texto = ""
    
    try:
        # Tentar extração de texto normal primeiro
        with pdfplumber.open(caminho_arquivo) as pdf:
            for i, pagina in enumerate(pdf.pages):
                try:
                    texto_pagina = pagina.extract_text()
                    if texto_pagina:
                        texto += f"\n--- Página {i+1} ---\n"
                        texto += texto_pagina
                        texto += "\n"
                except Exception as e:
                    print(f"    ⚠️  Erro na página {i+1}: {str(e)}")
                    continue
        
        # Se não extraiu texto suficiente, tentar OCR
        if len(texto.strip()) < 50:  # Texto muito curto pode indicar PDF escaneado
            print("    🔍 Texto insuficiente, tentando OCR...")
            texto_ocr = extrair_texto_pdf_ocr(caminho_arquivo)
            if texto_ocr:
                texto = texto_ocr
                
    except Exception as e:
        print(f"    ❌ Erro ao extrair texto do PDF: {str(e)}")
        
    return texto

def extrair_texto_pdf_ocr(caminho_arquivo):
    """
    Extrai texto de PDF usando OCR (pytesseract)
    """
    try:
        import fitz  # PyMuPDF - fallback se não tiver, usar pdfplumber
        
        texto_ocr = ""
        doc = fitz.open(caminho_arquivo)
        
        for num_pagina in range(len(doc)):
            pagina = doc.load_page(num_pagina)
            pix = pagina.get_pixmap()
            img_data = pix.tobytes("png")
            
            # Converter para PIL Image
            img = Image.open(io.BytesIO(img_data))
            
            # Aplicar OCR
            texto_pagina = pytesseract.image_to_string(img, lang='por')
            
            if texto_pagina.strip():
                texto_ocr += f"\n--- Página {num_pagina+1} (OCR) ---\n"
                texto_ocr += texto_pagina
                texto_ocr += "\n"
        
        doc.close()
        return texto_ocr
        
    except ImportError:
        print("    ⚠️  PyMuPDF não disponível para OCR")
        return ""
    except Exception as e:
        print(f"    ❌ Erro no OCR: {str(e)}")
        return ""

def extrair_texto_docx(caminho_arquivo):
    """
    Extrai texto de documento Word (.docx)
    """
    try:
        doc = Document(caminho_arquivo)
        texto = ""
        
        # Extrair texto dos parágrafos
        for paragrafo in doc.paragraphs:
            if paragrafo.text.strip():
                texto += paragrafo.text + "\n"
        
        # Extrair texto das tabelas
        for tabela in doc.tables:
            for linha in tabela.rows:
                for celula in linha.cells:
                    if celula.text.strip():
                        texto += celula.text + " "
                texto += "\n"
        
        return texto
        
    except Exception as e:
        print(f"    ❌ Erro ao extrair texto do DOCX: {str(e)}")
        return ""

def extrair_texto_xlsx(caminho_arquivo):
    """
    Extrai texto de planilha Excel (.xlsx)
    """
    try:
        # Ler todas as abas da planilha
        xls = pd.ExcelFile(caminho_arquivo)
        texto = ""
        
        for nome_aba in xls.sheet_names:
            df = pd.read_excel(caminho_arquivo, sheet_name=nome_aba)
            
            texto += f"\n--- Aba: {nome_aba} ---\n"
            
            # Converter DataFrame para texto
            texto += df.to_string(index=False, na_rep='')
            texto += "\n"
        
        return texto
        
    except Exception as e:
        print(f"    ❌ Erro ao extrair texto do XLSX: {str(e)}")
        return ""

def extrair_texto_csv(caminho_arquivo):
    """
    Extrai texto de arquivo CSV
    """
    try:
        # Tentar diferentes separadores e encodings
        separadores = [',', ';', '\t']
        encodings = ['utf-8', 'latin-1', 'cp1252']
        
        for encoding in encodings:
            for sep in separadores:
                try:
                    df = pd.read_csv(caminho_arquivo, sep=sep, encoding=encoding)
                    
                    # Se conseguiu ler e tem mais de uma coluna, provavelmente acertou
                    if len(df.columns) > 1:
                        return df.to_string(index=False, na_rep='')
                        
                except Exception:
                    continue
        
        # Se nenhum separador funcionou, ler como texto simples
        return extrair_texto_txt(caminho_arquivo)
        
    except Exception as e:
        print(f"    ❌ Erro ao extrair texto do CSV: {str(e)}")
        return ""

def extrair_texto_msg(caminho_arquivo):
    """
    Extrai texto de e-mail do Outlook (.msg)
    """
    try:
        msg = extract_msg.openMsg(caminho_arquivo)
        
        texto = ""
        
        # Informações básicas do e-mail
        if msg.sender:
            texto += f"De: {msg.sender}\n"
        if msg.to:
            texto += f"Para: {msg.to}\n"
        if msg.subject:
            texto += f"Assunto: {msg.subject}\n"
        if msg.date:
            texto += f"Data: {msg.date}\n"
        
        texto += "\n--- Corpo do E-mail ---\n"
        
        # Corpo do e-mail
        if msg.body:
            texto += msg.body
        
        # Anexos (apenas nomes)
        if hasattr(msg, 'attachments') and msg.attachments:
            texto += "\n--- Anexos ---\n"
            for anexo in msg.attachments:
                if hasattr(anexo, 'longFilename') and anexo.longFilename:
                    texto += f"Anexo: {anexo.longFilename}\n"
        
        return texto
        
    except Exception as e:
        print(f"    ❌ Erro ao extrair texto do MSG: {str(e)}")
        return ""

def limpar_texto(texto):
    """
    Limpa e normaliza o texto extraído
    """
    if not texto:
        return ""
    
    # Remover caracteres de controle
    texto = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]', '', texto)
    
    # Normalizar quebras de linha
    texto = re.sub(r'\r\n', '\n', texto)
    texto = re.sub(r'\r', '\n', texto)
    
    # Remover linhas vazias excessivas
    texto = re.sub(r'\n\s*\n\s*\n', '\n\n', texto)
    
    # Normalizar espaços
    texto = re.sub(r'[ \t]+', ' ', texto)
    
    return texto.strip()

# Função de teste para o módulo
if __name__ == "__main__":
    print("=== TESTE DO LEITOR DE ARQUIVOS ===")
    
    # Testar com arquivo de exemplo se existir
    teste_arquivo = "data/exemplo_contrato.txt"
    
    if os.path.exists(teste_arquivo):
        print(f"Testando com: {teste_arquivo}")
        texto = extrair_texto(teste_arquivo)
        texto_limpo = limpar_texto(texto)
        
        print(f"Texto extraído ({len(texto_limpo)} caracteres):")
        print("=" * 50)
        print(texto_limpo[:500] + "..." if len(texto_limpo) > 500 else texto_limpo)
        print("=" * 50)
    else:
        print(f"Arquivo de teste não encontrado: {teste_arquivo}")
        print("Crie arquivos na pasta 'data' para testar a extração.")
