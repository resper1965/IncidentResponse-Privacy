#!/bin/bash

echo "🔧 Corrigindo dependências na VPS"

cd /opt/privacy
source venv/bin/activate

echo "📦 Instalando todas as dependências..."

# Atualizar pip primeiro
pip install --upgrade pip setuptools wheel

# Instalar todas as dependências do sistema
pip install --force-reinstall pymupdf
pip install --force-reinstall pdfplumber python-docx pytesseract pillow
pip install --force-reinstall openpyxl pandas sqlalchemy psycopg2-binary
pip install --force-reinstall spacy extract-msg beautifulsoup4 striprtf
pip install --force-reinstall python-pptx lxml eml-parser pyyaml
pip install --force-reinstall flask gunicorn asyncpg watchdog

echo "🧪 Testando todas as importações críticas..."

python3 -c "
try:
    import fitz
    print('✅ PyMuPDF (fitz) OK')
except ImportError as e:
    print(f'❌ PyMuPDF: {e}')

try:
    import pdfplumber
    print('✅ pdfplumber OK')
except ImportError as e:
    print(f'❌ pdfplumber: {e}')

try:
    from docx import Document
    print('✅ python-docx OK')
except ImportError as e:
    print(f'❌ python-docx: {e}')

try:
    import web_interface
    print('✅ web_interface OK')
except ImportError as e:
    print(f'❌ web_interface: {e}')
"

echo "🔄 Parando serviço..."
systemctl stop privacy

echo "🔄 Iniciando serviço..."
systemctl start privacy

echo "📊 Status final..."
sleep 5
systemctl status privacy --no-pager -l

echo ""
echo "🌐 Testando se está rodando na porta 5000..."
curl -s -o /dev/null -w "%{http_code}" http://localhost:5000 || echo "Serviço não respondeu"

echo ""
echo "✅ Correção completa!"