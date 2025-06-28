#!/usr/bin/env python3
"""
Verificação final para deploy VPS
Testa compatibilidade de dependências e funcionalidades críticas
"""

import sys
import importlib
from pathlib import Path

def test_langchain_compatibility():
    """Testa compatibilidade específica das versões LangChain para VPS"""
    try:
        # Importar componentes LangChain
        from langchain_openai import ChatOpenAI
        from langchain_community.document_loaders import TextLoader
        from langchain.text_splitter import CharacterTextSplitter
        from langchain_core.messages import HumanMessage
        
        # Verificar versões
        import langchain
        import langchain_core
        import langchain_openai
        import langchain_community
        
        print('✅ LangChain compatibility verified')
        print(f'   langchain: {langchain.__version__}')
        print(f'   langchain-core: {langchain_core.__version__}')
        
        # Algumas versões podem não ter __version__ diretamente
        try:
            print(f'   langchain-openai: {langchain_openai.__version__}')
        except AttributeError:
            print('   langchain-openai: version available')
            
        try:
            print(f'   langchain-community: {langchain_community.__version__}')
        except AttributeError:
            print('   langchain-community: version available')
        
        # Teste de funcionalidade básica
        llm = ChatOpenAI(
            model='gpt-3.5-turbo-1106',
            temperature=0,
            openai_api_key='test-key-for-init'
        )
        print('✅ ChatOpenAI initialization successful')
        
        return True
        
    except Exception as e:
        print(f'❌ LangChain compatibility failed: {e}')
        return False

def test_file_processing_capabilities():
    """Testa capacidades de processamento de arquivos"""
    try:
        # Testar importações críticas para processamento
        dependencies = {
            'pdfplumber': 'PDF processing',
            'docx': 'Word document processing', 
            'openpyxl': 'Excel processing',
            'pandas': 'Data analysis',
            'pytesseract': 'OCR capabilities',
            'spacy': 'NLP processing',
            'extract_msg': 'Outlook email processing',
            'eml_parser': 'Email processing'
        }
        
        failed = []
        for dep, description in dependencies.items():
            try:
                importlib.import_module(dep)
                print(f'✅ {description}: {dep}')
            except ImportError:
                failed.append((dep, description))
                print(f'❌ {description}: {dep} missing')
        
        if failed:
            print(f'\n⚠️ Missing {len(failed)} dependencies - system will work with reduced functionality')
            return False
        else:
            print(f'\n✅ All {len(dependencies)} file processing dependencies available')
            return True
            
    except Exception as e:
        print(f'❌ File processing test failed: {e}')
        return False

def test_database_configuration():
    """Testa configuração do banco de dados"""
    try:
        import sqlite3
        import psycopg2
        
        # Testar SQLite
        conn = sqlite3.connect(':memory:')
        conn.execute('SELECT 1')
        conn.close()
        print('✅ SQLite support confirmed')
        
        # Verificar suporte PostgreSQL
        print('✅ PostgreSQL driver available')
        
        return True
        
    except Exception as e:
        print(f'❌ Database configuration failed: {e}')
        return False

def test_web_framework():
    """Testa framework web"""
    try:
        import flask
        from flask import Flask
        
        app = Flask(__name__)
        print(f'✅ Flask {flask.__version__} ready')
        
        # Testar dependências web
        import plotly
        print(f'✅ Plotly {plotly.__version__} for visualization')
        
        return True
        
    except Exception as e:
        print(f'❌ Web framework test failed: {e}')
        return False

def verify_production_files():
    """Verifica arquivos essenciais para produção"""
    required_files = [
        'production-requirements.txt',
        'requirements.in',
        'scripts/deploy-production.sh',
        'scripts/populate-database.py',
        '.env.production',
        'web_interface.py',
        'database.py',
        'file_reader.py',
        'data_extractor.py'
    ]
    
    missing = []
    for file_path in required_files:
        if not Path(file_path).exists():
            missing.append(file_path)
            print(f'❌ Missing: {file_path}')
        else:
            print(f'✅ Found: {file_path}')
    
    if missing:
        print(f'\n⚠️ {len(missing)} required files missing')
        return False
    else:
        print(f'\n✅ All {len(required_files)} production files present')
        return True

def verify_dependency_ranges():
    """Verifica ranges de dependências VPS-compatíveis"""
    try:
        with open('production-requirements.txt', 'r') as f:
            content = f.read()
        
        # Verificar versões críticas
        checks = [
            ('langchain-core>=0.2.43,<0.3.0', 'LangChain core version range'),
            ('langchain>=0.2.17,<0.3.0', 'LangChain version range'),
            ('langchain-openai>=0.2.17,<0.3.0', 'LangChain OpenAI version range'),
            ('psycopg2-binary', 'PostgreSQL driver'),
            ('flask', 'Web framework'),
            ('spacy', 'NLP framework')
        ]
        
        for check, description in checks:
            if check in content:
                print(f'✅ {description}: {check}')
            else:
                print(f'❌ {description}: missing or incorrect version')
                return False
        
        print('✅ All dependency ranges VPS-compatible')
        return True
        
    except Exception as e:
        print(f'❌ Dependency verification failed: {e}')
        return False

def run_vps_readiness_check():
    """Executa verificação completa de prontidão para VPS"""
    print('🚀 n.crisisops - Verificação de Prontidão para VPS')
    print('=' * 55)
    
    tests = [
        ('Production Files', verify_production_files),
        ('Dependency Ranges', verify_dependency_ranges),
        ('Database Configuration', test_database_configuration),
        ('Web Framework', test_web_framework),
        ('File Processing', test_file_processing_capabilities),
        ('LangChain Compatibility', test_langchain_compatibility)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f'\n🧪 Testing {test_name}...')
        if test_func():
            passed += 1
        print()
    
    print('=' * 55)
    print(f'📊 VPS Readiness: {passed}/{total} tests passed')
    
    if passed == total:
        print('🎉 Sistema pronto para deploy VPS!')
        print('\n📋 Próximos passos:')
        print('1. Transferir arquivos para VPS')
        print('2. Executar: sudo ./scripts/deploy-production.sh')
        print('3. Sistema estará disponível em: https://monster.e-ness.com.br')
        print('\n🔑 Credenciais PostgreSQL:')
        print('   Database: privacy_db')
        print('   User: privacy_user')
        print('   Password: Lgpd2025#Privacy')
        return True
    else:
        print('❌ Sistema requer correções antes do deploy VPS')
        return False

if __name__ == "__main__":
    success = run_vps_readiness_check()
    sys.exit(0 if success else 1)