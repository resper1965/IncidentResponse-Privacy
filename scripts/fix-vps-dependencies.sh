#!/bin/bash

# Fix VPS LangChain dependencies
# Execute this on the VPS to resolve the dependency conflict

echo "🔧 Fixing LangChain dependencies for VPS deployment..."

cd /opt/privacy

# Create corrected requirements.in with available versions
cat > requirements.in << 'EOF'
# n.crisisops - Sistema LGPD
# Arquivo de dependências base para produção

# Framework web
flask>=3.0.0,<4.0.0
flask-cors>=4.0.0,<5.0.0
gunicorn>=21.2.0,<22.0.0

# Banco de dados
psycopg2-binary>=2.9.9,<3.0.0
sqlalchemy>=2.0.23,<3.0.0

# Análise de dados
pandas>=2.1.4,<3.0.0
plotly>=5.17.0,<6.0.0

# Processamento de documentos
openpyxl>=3.1.2,<4.0.0
python-docx>=1.1.0,<2.0.0
pdfplumber>=0.10.3,<1.0.0
pymupdf>=1.23.8,<2.0.0
python-pptx>=0.6.23,<1.0.0
extract-msg>=0.48.5,<1.0.0

# OCR e imagens
pytesseract>=0.3.10,<1.0.0
pillow>=10.1.0,<11.0.0

# Processamento de texto
beautifulsoup4>=4.12.2,<5.0.0
lxml>=4.9.3,<5.0.0
striprtf>=0.0.26,<1.0.0
eml-parser>=2.0.0,<3.0.0

# NLP e IA - Versões corrigidas baseadas em disponibilidade
spacy>=3.7.2,<4.0.0
openai>=1.3.7,<2.0.0
langchain-core>=0.2.43
langchain>=0.2.17
langchain-community>=0.2.17
langchain-text-splitters>=0.2.4
langchain-openai>=0.2.17

# Utilitários
python-dotenv>=1.0.0,<2.0.0
EOF

echo "✅ Created corrected requirements.in"

# Generate new production-requirements.txt
echo "📦 Regenerating lockfile with corrected dependencies..."
pip-compile requirements.in --output-file production-requirements.txt --resolver=backtracking --verbose

if [ $? -eq 0 ]; then
    echo "✅ Lockfile generated successfully"
    
    echo "📦 Installing corrected dependencies..."
    pip-sync production-requirements.txt
    
    if [ $? -eq 0 ]; then
        echo "✅ Dependencies installed successfully"
        
        # Test LangChain imports
        echo "🧪 Testing LangChain compatibility..."
        python3 -c "
from langchain_openai import ChatOpenAI
from langchain_community.document_loaders import TextLoader
from langchain.text_splitter import CharacterTextSplitter
print('✅ LangChain imports successful')
"
        
        if [ $? -eq 0 ]; then
            echo "🎉 VPS dependencies fixed successfully!"
            echo "📋 You can now continue with the deployment script"
        else
            echo "⚠️ LangChain imports failed, but installation completed"
        fi
    else
        echo "❌ Dependency installation failed"
    fi
else
    echo "❌ Lockfile generation failed, trying direct installation..."
    
    # Fallback to direct pip install
    cat > production-requirements.txt << 'EOF'
# n.crisisops - Sistema LGPD - VPS Compatible
flask==3.0.0
flask-cors==4.0.0
gunicorn==21.2.0
psycopg2-binary==2.9.9
sqlalchemy==2.0.23
pandas==2.1.4
plotly==5.17.0
openpyxl==3.1.2
python-docx==1.1.0
pdfplumber==0.10.3
pymupdf==1.23.8
python-pptx==0.6.23
extract-msg==0.48.5
pytesseract==0.3.10
pillow==10.1.0
beautifulsoup4==4.12.2
lxml==4.9.3
striprtf==0.0.26
eml-parser==2.0.0
spacy==3.7.2
openai==1.3.7
langchain-core==0.2.43
langchain==0.2.17
langchain-community==0.2.17
langchain-text-splitters==0.2.4
langchain-openai==0.2.17
python-dotenv==1.0.0
EOF
    
    echo "📦 Installing with fallback requirements..."
    pip install -r production-requirements.txt
fi

echo "🔄 Deployment can now continue..."