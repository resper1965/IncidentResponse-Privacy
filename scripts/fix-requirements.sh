#!/bin/bash

# n.crisisops - LGPD Privacy Module - Fix Requirements
# Script para corrigir problema do requirements.txt na VPS

echo "🔧 n.crisisops - LGPD Privacy Module - Fix Requirements"
echo "================================================================="

# Variáveis
INSTALL_DIR="/opt/privacy"

echo "📋 Verificando requisitos..."

# Verificar se está rodando como root
if [ "$EUID" -ne 0 ]; then
    echo "❌ Execute como root: sudo $0"
    exit 1
fi

# Verificar se o diretório existe
if [ ! -d "$INSTALL_DIR" ]; then
    echo "❌ Diretório $INSTALL_DIR não existe. Execute o deploy completo primeiro."
    exit 1
fi

echo "📁 Verificando arquivos no diretório..."

cd $INSTALL_DIR
ls -la *.txt *.py 2>/dev/null || echo "⚠️ Poucos arquivos encontrados"

echo "📦 Baixando requirements.txt do GitHub..."

# Baixar requirements.txt do GitHub
wget -O requirements.txt https://raw.githubusercontent.com/resper1965/IncidentResponse-Privacy/main/requirements.txt

if [ $? -eq 0 ]; then
    echo "✅ requirements.txt baixado com sucesso"
else
    echo "❌ Erro ao baixar requirements.txt"
    echo "📝 Criando requirements.txt básico..."
    
    # Criar requirements.txt básico
    cat > requirements.txt << 'EOF'
Flask==2.3.3
Werkzeug==2.3.7
gunicorn==21.2.0
psycopg2-binary==2.9.7
pandas==2.0.3
numpy==1.24.3
PyMuPDF==1.23.8
python-docx==0.8.11
extract-msg==0.41.0
eml-parser==1.18.0
striprtf==0.0.26
spacy==3.6.1
langchain==0.0.267
openai==0.28.1
anthropic==0.7.7
python-dotenv==1.0.0
requests==2.31.0
beautifulsoup4==4.12.2
lxml==4.9.3
Pillow==10.0.1
tesseract-ocr==0.0.1
python-magic==0.4.27
chardet==5.2.0
cryptography==41.0.4
bcrypt==4.0.1
passlib==1.7.4
SQLAlchemy==2.0.21
alembic==1.12.0
redis==5.0.1
celery==5.3.4
flower==2.0.1
prometheus-client==0.17.1
structlog==23.1.0
sentry-sdk==1.32.0
EOF
    
    echo "✅ requirements.txt básico criado"
fi

echo "🐍 Verificando ambiente Python..."

# Verificar se o ambiente virtual existe
if [ ! -d "$INSTALL_DIR/venv" ]; then
    echo "❌ Ambiente virtual não existe. Criando..."
    cd $INSTALL_DIR
    python3 -m venv venv
    echo "✅ Ambiente virtual criado"
else
    echo "✅ Ambiente virtual existe"
fi

echo "📦 Ativando ambiente virtual..."

# Ativar ambiente virtual
cd $INSTALL_DIR
source venv/bin/activate

echo "📦 Atualizando pip..."

# Atualizar pip
pip install --upgrade pip setuptools wheel

echo "📦 Instalando dependências Python..."

# Instalar dependências
pip install -r requirements.txt

if [ $? -eq 0 ]; then
    echo "✅ Dependências Python instaladas com sucesso"
else
    echo "⚠️ Algumas dependências podem ter falhado, tentando instalação individual..."
    
    # Instalar dependências críticas individualmente
    pip install Flask==2.3.3
    pip install gunicorn==21.2.0
    pip install psycopg2-binary==2.9.7
    pip install pandas==2.0.3
    pip install PyMuPDF==1.23.8
    pip install python-docx==0.8.11
    pip install spacy==3.6.1
    pip install python-dotenv==1.0.0
    
    echo "✅ Dependências críticas instaladas"
fi

echo "🤖 Baixando modelo spaCy..."

# Baixar modelo spaCy
python -m spacy download pt_core_news_sm

echo "🔐 Configurando permissões..."

# Definir permissões corretas
chown -R privacy:privacy $INSTALL_DIR
chmod +x venv/bin/*

echo "🚀 Reiniciando serviço..."

# Reiniciar serviço
systemctl restart privacy

echo "⏳ Aguardando inicialização..."
sleep 10

echo "🧪 Testando aplicação..."

# Verificar se a aplicação responde
if curl -f -s http://localhost:5000 > /dev/null; then
    echo "✅ Aplicação respondendo corretamente"
else
    echo "❌ Aplicação não responde, verificando logs..."
    journalctl -u privacy --no-pager -l -n 20
fi

echo ""
echo "================================================================="
echo "✅ CORREÇÃO DE REQUIREMENTS CONCLUÍDA!"
echo "================================================================="
echo "📁 Diretório: $INSTALL_DIR"
echo "📦 Requirements: requirements.txt"
echo "🐍 Ambiente: venv/"
echo ""
echo "📋 Comandos úteis:"
echo "   sudo systemctl status privacy"
echo "   sudo journalctl -u privacy -f"
echo "   cd $INSTALL_DIR && source venv/bin/activate && pip list"
echo ""
echo "🔍 Para verificar dependências:"
echo "   cd $INSTALL_DIR"
echo "   source venv/bin/activate"
echo "   pip list | grep -E '(Flask|psycopg2|spacy)'"
echo "=================================================================" 