#!/bin/bash

echo "🔧 Atualizando dependências na VPS"

cd /opt/privacy
source venv/bin/activate

echo "📦 Instalando/atualizando dependências específicas..."

# Atualizar pip
pip install --upgrade pip

# Instalar versões específicas
pip install eml-parser==2.0.0
pip install pymupdf==1.23.8
pip install pdfplumber==0.10.3
pip install python-docx==1.1.0
pip install openpyxl==3.1.2
pip install extract-msg==0.48.5
pip install pytesseract==0.3.10
pip install pillow==10.1.0
pip install beautifulsoup4==4.12.2
pip install lxml==4.9.3
pip install striprtf==0.0.26

# Dependências Python core
pip install flask==3.0.0
pip install gunicorn==21.2.0
pip install psycopg2-binary==2.9.9
pip install sqlalchemy==2.0.23
pip install pandas==2.1.4

# IA e NLP
pip install spacy==3.7.2
pip install openai==1.3.7
pip install langchain==0.0.348
pip install langchain-openai==0.0.2

# Outras dependências
pip install python-dotenv==1.0.0
pip install asyncpg
pip install watchdog

echo "🧪 Testando importações críticas..."
python3 -c "
import sys
modules = ['fitz', 'pdfplumber', 'docx', 'openpyxl', 'extract_msg', 'eml_parser', 'flask', 'sqlalchemy', 'pandas']
for module in modules:
    try:
        __import__(module)
        print(f'✅ {module}')
    except ImportError as e:
        print(f'❌ {module}: {e}')
"

echo "🔄 Reiniciando serviço privacy..."
systemctl stop privacy
systemctl start privacy

echo "📊 Verificando status..."
sleep 3
systemctl status privacy --no-pager -l

echo "✅ Atualização concluída"