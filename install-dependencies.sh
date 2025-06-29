#!/bin/bash

# Script para instalar todas as dependências do sistema privacy
# Execute como root no VPS

set -e

echo "📦 Instalando dependências do sistema privacy..."

# 1. Atualizar sistema
echo "🔄 Atualizando sistema..."
apt update

# 2. Instalar dependências do sistema
echo "📦 Instalando dependências do sistema..."
apt install -y \
    python3 \
    python3-pip \
    python3-venv \
    python3-dev \
    build-essential \
    libssl-dev \
    libffi-dev \
    curl \
    wget \
    git \
    nginx \
    sqlite3 \
    postgresql \
    postgresql-contrib \
    tesseract-ocr \
    tesseract-ocr-por \
    poppler-utils \
    libmagic1 \
    libxml2-dev \
    libxslt1-dev \
    libjpeg-dev \
    libpng-dev \
    libfreetype6-dev \
    liblcms2-dev \
    libwebp-dev \
    libtiff5-dev \
    libopenjp2-7-dev \
    libharfbuzz-dev \
    libfribidi-dev \
    libxcb1-dev

# 3. Criar usuário privacy se não existir
if ! id "privacy" &>/dev/null; then
    echo "👤 Criando usuário privacy..."
    useradd -m -s /bin/bash privacy
    usermod -aG sudo privacy
fi

# 4. Criar diretório da aplicação
echo "📁 Criando diretório da aplicação..."
mkdir -p /opt/privacy
chown privacy:privacy /opt/privacy

# 5. Copiar arquivos da aplicação (se existirem)
if [ -f "web_interface.py" ]; then
    echo "📄 Copiando arquivos da aplicação..."
    cp *.py /opt/privacy/
    cp -r templates /opt/privacy/ 2>/dev/null || true
    cp pyproject.toml /opt/privacy/ 2>/dev/null || true
    chown -R privacy:privacy /opt/privacy
fi

# 6. Configurar ambiente virtual
echo "🐍 Configurando ambiente virtual..."
cd /opt/privacy

# Remover ambiente virtual existente se houver problemas
if [ -d "venv" ]; then
    echo "🗑️  Removendo ambiente virtual existente..."
    rm -rf venv
fi

# Criar novo ambiente virtual
echo "📦 Criando novo ambiente virtual..."
python3 -m venv venv
chown -R privacy:privacy venv

# 7. Instalar dependências Python
echo "📦 Instalando dependências Python..."
source venv/bin/activate

# Atualizar pip
pip install --upgrade pip setuptools wheel

# Instalar dependências básicas primeiro
pip install \
    flask \
    gunicorn \
    sqlalchemy \
    psycopg2-binary \
    asyncpg

# Instalar dependências de processamento de documentos
pip install \
    pdfplumber \
    python-docx \
    openpyxl \
    pandas \
    python-pptx \
    extract-msg \
    eml-parser \
    pytesseract \
    pillow \
    beautifulsoup4 \
    lxml \
    striprtf \
    pyyaml \
    pymupdf

# Instalar dependências de IA
pip install \
    spacy \
    langchain \
    langchain-openai \
    langchain-community \
    langchain-core \
    langchain-text-splitters \
    openai

# Instalar dependências adicionais
pip install \
    plotly \
    watchdog \
    pathlib

# 8. Baixar modelo spaCy
echo "🤖 Baixando modelo spaCy..."
python -m spacy download pt_core_news_sm

# 9. Criar arquivo de configuração do serviço
echo "⚙️  Criando arquivo de serviço systemd..."
cat > /etc/systemd/system/privacy.service << 'EOF'
[Unit]
Description=n.crisisops Privacy LGPD System
After=network.target

[Service]
Type=exec
User=privacy
Group=privacy
WorkingDirectory=/opt/privacy
Environment=PATH=/opt/privacy/venv/bin
ExecStart=/opt/privacy/venv/bin/gunicorn --bind 0.0.0.0:5000 --workers 3 --timeout 120 web_interface:app
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# 10. Configurar nginx
echo "🌐 Configurando nginx..."
cat > /etc/nginx/sites-available/privacy << 'EOF'
server {
    listen 80;
    server_name _;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
EOF

# Habilitar site
ln -sf /etc/nginx/sites-available/privacy /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default

# 11. Ajustar permissões
echo "🔐 Ajustando permissões..."
chown -R privacy:privacy /opt/privacy
chmod -R 755 /opt/privacy

# 12. Recarregar e iniciar serviços
echo "🔄 Recarregando serviços..."
systemctl daemon-reload
systemctl enable privacy
systemctl restart nginx

# 13. Iniciar serviço privacy
echo "🚀 Iniciando serviço privacy..."
systemctl start privacy

# 14. Aguardar inicialização
echo "⏳ Aguardando inicialização..."
sleep 10

# 15. Verificar status
echo "📊 Status dos serviços:"
echo "=== Privacy Service ==="
systemctl status privacy --no-pager

echo "=== Nginx ==="
systemctl status nginx --no-pager

# 16. Testar aplicação
echo "🏥 Testando aplicação..."
if curl -f http://localhost:5000/health > /dev/null 2>&1; then
    echo "✅ Aplicação funcionando corretamente!"
    echo "🌐 Acesse: http://localhost:5000"
    echo "🌐 Ou via nginx: http://$(hostname -I | awk '{print $1}')"
else
    echo "❌ Aplicação não está respondendo"
    echo "📋 Verificando logs..."
    journalctl -u privacy -n 20 --no-pager
fi

echo "✅ Instalação concluída!"
echo ""
echo "📋 Próximos passos:"
echo "1. Configure sua chave OpenAI em /opt/privacy/.env"
echo "2. Adicione documentos na pasta /opt/privacy/data"
echo "3. Execute: python3 main.py para processar documentos"
echo "4. Acesse o dashboard em: http://localhost:5000" 