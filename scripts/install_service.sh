#!/bin/bash

# =============================================================================
# Script de Instalação Completa - n.crisisops
# Sistema LGPD de Compliance e Resposta a Incidentes
# =============================================================================

set -e  # Exit on any error

echo "🚀 Instalando n.crisisops - Sistema LGPD..."

# Verificar se está rodando como root
if [[ $EUID -ne 0 ]]; then
   echo "❌ Este script deve ser executado como root"
   exit 1
fi

# Criar usuário do sistema se não existir
if ! id "privacy" &>/dev/null; then
    echo "👤 Criando usuário do sistema 'privacy'..."
    useradd --system --shell /bin/bash --home-dir /opt/privacy --create-home privacy
else
    echo "✅ Usuário 'privacy' já existe"
fi

# Criar estrutura de diretórios
echo "📁 Criando estrutura de diretórios..."
mkdir -p /opt/privacy/{app,venv,logs,data,backups}
chown -R privacy:privacy /opt/privacy

# Instalar dependências do sistema
echo "📦 Instalando dependências do sistema..."
apt update
apt install -y postgresql postgresql-contrib nginx python3 python3-venv python3-pip curl unzip git

# Configurar PostgreSQL
echo "🗄️ Configurando PostgreSQL..."
systemctl start postgresql
systemctl enable postgresql

# Criar usuário e banco PostgreSQL
echo "👤 Criando usuário PostgreSQL..."
sudo -u postgres psql -c "DROP USER IF EXISTS privacy;" 2>/dev/null || true
sudo -u postgres psql -c "CREATE USER privacy WITH PASSWORD 'ncrisisops_secure_2025';"

echo "🗄️ Criando banco de dados..."
sudo -u postgres psql -c "DROP DATABASE IF EXISTS privacy;" 2>/dev/null || true
sudo -u postgres psql -c "CREATE DATABASE privacy OWNER privacy;"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE privacy TO privacy;"

# Verificar se banco foi criado
echo "✅ Verificando banco..."
if sudo -u postgres psql -lqt | cut -d \| -f 1 | grep -qw privacy; then
    echo "✅ Banco 'privacy' criado com sucesso"
else
    echo "❌ Erro ao criar banco 'privacy'"
    exit 1
fi

# Criar arquivo .env se não existir
if [ ! -f "/opt/privacy/app/.env" ]; then
    echo "🔐 Criando arquivo .env..."
    cat > /opt/privacy/app/.env << EOF
# n.crisisops - Configuração de Produção
FLASK_ENV=production
FLASK_DEBUG=False
SECRET_KEY=$(openssl rand -hex 32)

# PostgreSQL
DATABASE_URL=postgresql://privacy:ncrisisops_secure_2025@localhost:5432/privacy
PGHOST=localhost
PGPORT=5432
PGDATABASE=privacy
PGUSER=privacy
PGPASSWORD=ncrisisops_secure_2025

# Aplicação
PORT=5000
HOST=0.0.0.0
EOF
fi

# Criar configuração Gunicorn
echo "⚙️ Criando configuração do Gunicorn..."
cat > /opt/privacy/gunicorn.conf.py << 'EOF'
# Configuração do Gunicorn para n.crisisops
bind = "0.0.0.0:5000"
workers = 2
worker_class = "sync"
timeout = 120
keepalive = 2
preload_app = False
reload = False
daemon = False
pidfile = "/opt/privacy/gunicorn.pid"
accesslog = "/opt/privacy/logs/gunicorn_access.log"
errorlog = "/opt/privacy/logs/gunicorn_error.log"
loglevel = "info"
capture_output = True
EOF

# Criar serviço systemd
echo "🚀 Criando serviço systemd..."
cat > /etc/systemd/system/privacy.service << 'EOF'
[Unit]
Description=n.crisisops LGPD Compliance System
After=network.target postgresql.service
Wants=postgresql.service

[Service]
Type=exec
User=privacy
Group=privacy
WorkingDirectory=/opt/privacy/app
Environment=PATH=/opt/privacy/venv/bin:/usr/local/bin:/usr/bin:/bin
Environment=DATABASE_URL=postgresql://privacy:ncrisisops_secure_2025@localhost:5432/privacy
Environment=FLASK_ENV=production
ExecStart=/opt/privacy/venv/bin/gunicorn --config /opt/privacy/gunicorn.conf.py web_interface:app
ExecReload=/bin/kill -s HUP $MAINPID
RestartSec=5
Restart=always
StandardOutput=journal
StandardError=journal
SyslogIdentifier=privacy

[Install]
WantedBy=multi-user.target
EOF

# Configurar Python Virtual Environment
echo "🐍 Configurando ambiente Python..."
if [ ! -d "/opt/privacy/venv" ]; then
    echo "📦 Criando ambiente virtual..."
    sudo -u privacy python3 -m venv /opt/privacy/venv
fi

# Instalar dependências Python
echo "📦 Instalando dependências Python..."
sudo -u privacy /opt/privacy/venv/bin/pip install --upgrade pip

# Lista de dependências Python para produção
sudo -u privacy /opt/privacy/venv/bin/pip install \
    flask==3.0.0 \
    flask-cors==4.0.0 \
    gunicorn==21.2.0 \
    psycopg2-binary==2.9.9 \
    sqlalchemy==2.0.23 \
    pandas==2.1.4 \
    plotly==5.17.0 \
    openpyxl==3.1.2 \
    python-docx==1.1.0 \
    pdfplumber==0.10.3 \
    extract-msg==0.48.5 \
    spacy==3.7.2 \
    pytesseract==0.3.10 \
    pillow==10.1.0 \
    python-dotenv==1.0.0 \
    openai==1.3.7 \
    langchain==0.0.348 \
    langchain-openai==0.0.2 \
    pymupdf==1.23.8 \
    python-pptx==0.6.23 \
    beautifulsoup4==4.12.2 \
    lxml==4.9.3 \
    striprtf==0.0.26 \
    eml-parser==1.17.7 \
    langchain-community==0.0.6 \
    langchain-text-splitters==0.0.1

echo "✅ Dependências Python instaladas"

# Baixar modelo spaCy português se não existir
echo "🧠 Configurando modelo spaCy..."
sudo -u privacy /opt/privacy/venv/bin/python -m spacy download pt_core_news_sm || echo "⚠️ Modelo spaCy será baixado na primeira execução"

# Ajustar permissões finais
echo "🔐 Ajustando permissões..."
chown -R privacy:privacy /opt/privacy
chmod +x /opt/privacy/venv/bin/*
chmod 644 /opt/privacy/gunicorn.conf.py
chmod 600 /opt/privacy/app/.env

# Recarregar systemd
echo "🔄 Recarregando systemd..."
systemctl daemon-reload
systemctl enable privacy

echo ""
echo "📋 PRÓXIMOS PASSOS:"
echo "1. Copie os arquivos da aplicação para /opt/privacy/app/"
echo "2. Execute: systemctl start privacy"
echo "3. Verifique: systemctl status privacy"
echo "4. Teste: curl http://localhost:5000/health"
echo ""
echo "📂 Arquivos necessários em /opt/privacy/app/:"
echo "   - web_interface.py"
echo "   - database_postgresql.py"
echo "   - file_reader.py"
echo "   - data_extractor.py"
echo "   - file_scanner.py"
echo "   - ai_super_processor.py"
echo "   - templates/ (diretório)"
echo ""
echo "✅ Instalação da infraestrutura concluída!"