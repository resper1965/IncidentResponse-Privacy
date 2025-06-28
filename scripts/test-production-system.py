#!/usr/bin/env python3
"""
Test completo do sistema de produção
Verifica todas as funcionalidades antes do deploy
"""

import os
import sys
import sqlite3
import asyncio
from pathlib import Path

def test_database_connection():
    """Testa conexão com banco de dados"""
    try:
        conn = sqlite3.connect("lgpd_data.db")
        cursor = conn.cursor()
        
        # Verificar tabelas principais
        cursor.execute("SELECT COUNT(*) FROM regex_patterns")
        regex_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM prioridades_busca")
        priority_count = cursor.fetchone()[0]
        
        conn.close()
        
        print(f'✅ Database: {regex_count} regex patterns, {priority_count} priorities')
        return True
    except Exception as e:
        print(f'❌ Database test failed: {e}')
        return False

def test_file_processing():
    """Testa processamento de arquivos"""
    try:
        import file_reader
        import data_extractor
        
        # Criar arquivo de teste
        test_content = """
        João Silva
        CPF: 123.456.789-00
        Email: joao@bradesco.com.br
        Telefone: (11) 99999-9999
        """
        
        with open("test_document.txt", "w", encoding="utf-8") as f:
            f.write(test_content)
        
        # Testar leitura
        texto = file_reader.ler_arquivo("test_document.txt")
        
        # Testar extração
        dados = data_extractor.analisar_texto(texto, "test_document.txt")
        
        # Limpar arquivo teste
        os.remove("test_document.txt")
        
        print(f'✅ File processing: extracted {len(dados)} data points')
        return len(dados) > 0
        
    except Exception as e:
        print(f'❌ File processing test failed: {e}')
        return False

def test_web_interface():
    """Testa interface web"""
    try:
        import web_interface
        app = web_interface.app
        
        with app.test_client() as client:
            # Testar rota principal
            response = client.get('/')
            if response.status_code != 200:
                raise Exception(f"Main route failed: {response.status_code}")
            
            # Testar API estatísticas
            response = client.get('/api/estatisticas')
            if response.status_code != 200:
                raise Exception(f"Stats API failed: {response.status_code}")
            
            print('✅ Web interface: all routes working')
            return True
            
    except Exception as e:
        print(f'❌ Web interface test failed: {e}')
        return False

def test_langchain_integration():
    """Testa integração LangChain"""
    try:
        from langchain_openai import ChatOpenAI
        from langchain_community.document_loaders import TextLoader
        from langchain.text_splitter import CharacterTextSplitter
        
        print('✅ LangChain: all imports successful')
        return True
        
    except Exception as e:
        print(f'❌ LangChain test failed: {e}')
        return False

def test_production_dependencies():
    """Testa todas as dependências de produção"""
    dependencies = [
        'flask', 'psycopg2', 'pandas', 'plotly', 'openpyxl',
        'pdfplumber', 'python-docx', 'pytesseract', 'spacy',
        'langchain', 'langchain_openai', 'extract_msg'
    ]
    
    failed = []
    for dep in dependencies:
        try:
            __import__(dep)
        except ImportError:
            failed.append(dep)
    
    if failed:
        print(f'❌ Missing dependencies: {", ".join(failed)}')
        return False
    else:
        print(f'✅ Dependencies: all {len(dependencies)} packages available')
        return True

def run_complete_test():
    """Executa teste completo do sistema"""
    print('🚀 Iniciando teste completo do sistema de produção...\n')
    
    tests = [
        ('Database Connection', test_database_connection),
        ('Production Dependencies', test_production_dependencies),
        ('LangChain Integration', test_langchain_integration),
        ('File Processing', test_file_processing),
        ('Web Interface', test_web_interface)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f'Testing {test_name}...', end=' ')
        if test_func():
            passed += 1
        print()
    
    print(f'\n📊 Test Results: {passed}/{total} tests passed')
    
    if passed == total:
        print('🎉 Sistema pronto para produção!')
        print('Execute: sudo ./scripts/deploy-production.sh')
        return True
    else:
        print('❌ Sistema não está pronto para produção')
        return False

if __name__ == "__main__":
    success = run_complete_test()
    sys.exit(0 if success else 1)