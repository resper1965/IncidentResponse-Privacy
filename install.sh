#!/bin/bash

# =============================================================================
# n.crisisops - Script de Instalação de Ambiente
# Sistema de Gestão de Resposta a Incidente (Privacy Module)
# =============================================================================

set -e

echo "🚀 Iniciando instalação do n.crisisops..."
echo "📋 Sistema de Compliance LGPD com IA Avançada"
echo "============================================="

# Verificar se está sendo executado como root
if [ "$EUID" -eq 0 ]; then
  echo "❌ Não execute este script como root"
  exit 1
fi

# Detectar sistema operacional
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    OS="linux"
    DISTRO=$(lsb_release -si 2>/dev/null || echo "Unknown")
elif [[ "$OSTYPE" == "darwin"* ]]; then
    OS="macos"
elif [[ "$OSTYPE" == "msys" || "$OSTYPE" == "cygwin" ]]; then
    OS="windows"
else
    echo "❌ Sistema operacional não suportado: $OSTYPE"
    exit 1
fi

echo "🔍 Sistema detectado: $OS"

# Função para instalar dependências no Ubuntu/Debian
install_ubuntu_deps() {
    echo "📦 Instalando dependências do sistema (Ubuntu/Debian)..."
    sudo apt update
    sudo apt install -y \
        python3 \
        python3-pip \
        python3-venv \
        python3-dev \
        build-essential \
        postgresql \
        postgresql-contrib \
        libpq-dev \
        tesseract-ocr \
        tesseract-ocr-por \
        git \
        curl \
        poppler-utils \
        libreoffice \
        nodejs \
        npm
}

# Função para instalar dependências no CentOS/RHEL/Fedora
install_redhat_deps() {
    echo "📦 Instalando dependências do sistema (RedHat/CentOS/Fedora)..."
    sudo yum update -y || sudo dnf update -y
    sudo yum install -y \
        python3 \
        python3-pip \
        python3-devel \
        gcc \
        gcc-c++ \
        make \
        postgresql \
        postgresql-server \
        postgresql-devel \
        tesseract \
        git \
        curl \
        poppler-utils \
        libreoffice \
        nodejs \
        npm \
        || sudo dnf install -y \
        python3 \
        python3-pip \
        python3-devel \
        gcc \
        gcc-c++ \
        make \
        postgresql \
        postgresql-server \
        postgresql-devel \
        tesseract \
        git \
        curl \
        poppler-utils \
        libreoffice \
        nodejs \
        npm
}

# Função para instalar dependências no macOS
install_macos_deps() {
    echo "📦 Instalando dependências do sistema (macOS)..."
    
    # Verificar se Homebrew está instalado
    if ! command -v brew &> /dev/null; then
        echo "🍺 Instalando Homebrew..."
        /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
    fi
    
    brew update
    brew install \
        python3 \
        postgresql \
        tesseract \
        tesseract-lang \
        git \
        poppler \
        libreoffice \
        node
}

# Instalar dependências do sistema
echo "⚙️  Instalando dependências do sistema..."
case $OS in
    linux)
        if [[ "$DISTRO" == "Ubuntu" || "$DISTRO" == "Debian" ]]; then
            install_ubuntu_deps
        elif [[ "$DISTRO" == "CentOS" || "$DISTRO" == "RedHat" || "$DISTRO" == "Fedora" ]]; then
            install_redhat_deps
        else
            echo "⚠️  Distribuição Linux não suportada automaticamente: $DISTRO"
            echo "📝 Instale manualmente: python3, pip, postgresql, tesseract, git"
        fi
        ;;
    macos)
        install_macos_deps
        ;;
    windows)
        echo "⚠️  Para Windows, instale manualmente:"
        echo "   - Python 3.8+ (https://python.org)"
        echo "   - PostgreSQL (https://postgresql.org)"
        echo "   - Tesseract OCR (https://github.com/UB-Mannheim/tesseract/wiki)"
        echo "   - Git (https://git-scm.com)"
        ;;
esac

# Verificar Python
echo "🐍 Verificando Python..."
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 não encontrado. Instale Python 3.8 ou superior."
    exit 1
fi

PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
echo "✅ Python $PYTHON_VERSION detectado"

# Verificar pip
if ! command -v pip3 &> /dev/null; then
    echo "📦 Instalando pip..."
    curl https://bootstrap.pypa.io/get-pip.py | python3
fi

# Criar ambiente virtual
echo "🔧 Criando ambiente virtual Python..."
if [ -d "venv" ]; then
    echo "⚠️  Ambiente virtual já existe. Removendo..."
    rm -rf venv
fi

python3 -m venv venv
source venv/bin/activate

# Atualizar pip no ambiente virtual
echo "📦 Atualizando pip..."
pip install --upgrade pip setuptools wheel

# Instalar dependências Python
echo "📚 Instalando dependências Python..."
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
else
    # Instalar dependências básicas se requirements.txt não existir
    pip install \
        flask \
        flask-cors \
        sqlalchemy \
        psycopg2-binary \
        pandas \
        plotly \
        openpyxl \
        pdfplumber \
        python-docx \
        extract-msg \
        pytesseract \
        pillow \
        spacy \
        openai \
        langchain \
        langchain-openai \
        langchain-community \
        python-dotenv \
        watchdog \
        requests \
        beautifulsoup4
fi

# Baixar modelo spaCy português
echo "🌐 Baixando modelo spaCy português..."
python -m spacy download pt_core_news_lg || python -m spacy download pt_core_news_sm

# Configurar PostgreSQL (se necessário)
echo "🗄️  Configurando PostgreSQL..."
if command -v pg_config &> /dev/null; then
    echo "✅ PostgreSQL detectado"
    
    # Verificar se o serviço está rodando
    if ! pgrep -x "postgres" > /dev/null; then
        echo "🔧 Iniciando serviço PostgreSQL..."
        case $OS in
            linux)
                sudo systemctl start postgresql
                sudo systemctl enable postgresql
                ;;
            macos)
                brew services start postgresql
                ;;
        esac
    fi
else
    echo "⚠️  PostgreSQL não detectado. Funcionalidades avançadas podem ser limitadas."
fi

# Criar arquivo .env.example se não existir
if [ ! -f ".env.example" ]; then
    echo "📝 Criando arquivo .env.example..."
    cat > .env.example << EOF
# n.crisisops - Configurações de Ambiente

# OpenAI Configuration
OPENAI_API_KEY=sk-your-openai-api-key-here

# PostgreSQL Database Configuration
DATABASE_URL=postgresql://username:password@localhost:5432/ncrisisops

# PostgreSQL Connection Details
PGHOST=localhost
PGPORT=5432
PGDATABASE=ncrisisops
PGUSER=ncrisisops_user
PGPASSWORD=secure_password_here

# Application Configuration
FLASK_ENV=production
FLASK_DEBUG=False
SECRET_KEY=your-secret-key-here

# File Processing
MAX_FILE_SIZE=100MB
PROCESSING_TIMEOUT=300

# Logging
LOG_LEVEL=INFO
LOG_FILE=logs/ncrisisops.log
EOF
fi

# Criar estrutura de diretórios
echo "📁 Criando estrutura de diretórios..."
mkdir -p data logs backups uploads exports temp

# Verificar dependências opcionais
echo "🔍 Verificando dependências opcionais..."

# Tesseract
if command -v tesseract &> /dev/null; then
    echo "✅ Tesseract OCR detectado"
    tesseract --version | head -1
else
    echo "⚠️  Tesseract OCR não detectado. OCR será limitado."
fi

# LibreOffice
if command -v libreoffice &> /dev/null; then
    echo "✅ LibreOffice detectado"
else
    echo "⚠️  LibreOffice não detectado. Conversão de documentos pode ser limitada."
fi

# Executar testes básicos
echo "🧪 Executando testes básicos..."
python3 -c "
import sys
print(f'✅ Python {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}')

try:
    import flask
    print('✅ Flask')
except ImportError:
    print('❌ Flask não instalado')

try:
    import pandas
    print('✅ Pandas')
except ImportError:
    print('❌ Pandas não instalado')

try:
    import spacy
    print('✅ spaCy')
    try:
        nlp = spacy.load('pt_core_news_lg')
        print('✅ Modelo português (grande)')
    except OSError:
        try:
            nlp = spacy.load('pt_core_news_sm')
            print('✅ Modelo português (pequeno)')
        except OSError:
            print('❌ Modelo português não encontrado')
except ImportError:
    print('❌ spaCy não instalado')

try:
    import openai
    print('✅ OpenAI')
except ImportError:
    print('❌ OpenAI não instalado')
"

echo ""
echo "🎉 INSTALAÇÃO CONCLUÍDA!"
echo "========================"
echo ""
echo "📋 Próximos passos:"
echo "1. Configure suas variáveis de ambiente:"
echo "   cp .env.example .env"
echo "   # Edite .env com suas configurações"
echo ""
echo "2. Configure o banco PostgreSQL (opcional):"
echo "   sudo -u postgres createuser ncrisisops_user"
echo "   sudo -u postgres createdb ncrisisops"
echo "   sudo -u postgres psql -c \"ALTER USER ncrisisops_user PASSWORD 'secure_password_here';\""
echo ""
echo "3. Execute o sistema:"
echo "   source venv/bin/activate"
echo "   python web_interface.py"
echo ""
echo "4. Acesse: http://localhost:5000"
echo ""
echo "📚 Documentação completa em: replit.md"
echo "🐛 Relatório de problemas: homologacao_report.md"
echo ""
echo "✨ n.crisisops pronto para uso!"