#!/bin/bash

echo "📦 Instalando dependências faltantes na VPS"

# Execute na VPS como root
cd /opt/privacy
source venv/bin/activate

echo "📋 Instalando dependências Python ausentes..."

# Instalar todas as dependências necessárias
pip install --upgrade pip
pip install pymupdf  # Para fitz
pip install pdfplumber python-docx pytesseract pillow
pip install openpyxl pandas sqlalchemy psycopg2-binary
pip install spacy extract-msg beautifulsoup4 striprtf
pip install python-pptx lxml eml-parser pyyaml
pip install langchain langchain-openai openai
pip install asyncpg watchdog pathlib2

# Instalar modelo spaCy português
python -m spacy download pt_core_news_sm

echo "✅ Dependências instaladas"

echo "🧪 Testando importações..."
python3 -c "
import fitz; print('✅ PyMuPDF (fitz)')
import web_interface; print('✅ web_interface')
"

echo "🔄 Reiniciando serviço..."
systemctl restart privacy

echo "📊 Status final..."
sleep 3
systemctl status privacy --no-pager -l