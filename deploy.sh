#!/bin/bash

# =============================================================================
# n.crisisops - Script de Deploy para Produção
# Sistema de Gestão de Resposta a Incidente (Privacy Module)
# =============================================================================

set -e

echo "🚀 Deploy n.crisisops - Sistema LGPD Enterprise"
echo "==============================================="

# Configurações padrão
APP_NAME="privacy"
APP_USER="privacy"
APP_DIR="/opt/privacy"
SERVICE_NAME="privacy"
NGINX_CONF="/etc/nginx/sites-available/privacy"
DOMAIN="monster.e-ness.com.br"
PYTHON_VERSION="3.8"
PORT="5000"

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Função para log colorido
log() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Verificar se está sendo executado como root
if [ "$EUID" -ne 0 ]; then
  error "Execute este script como root (sudo ./deploy.sh)"
  exit 1
fi

# Detectar sistema operacional
if [[ -f /etc/os-release ]]; then
    . /etc/os-release
    OS=$ID
    VERSION=$VERSION_ID
else
    error "Sistema operacional não identificado"
    exit 1
fi

log "Sistema: $OS $VERSION"

# Função para Ubuntu/Debian
deploy_ubuntu() {
    log "Configurando para Ubuntu/Debian..."
    
    # Atualizar sistema
    apt update && apt upgrade -y
    
    # Instalar dependências do sistema
    apt install -y \
        python3 \
        python3-pip \
        python3-venv \
        python3-dev \
        build-essential \
        postgresql \
        postgresql-contrib \
        libpq-dev \
        nginx \
        supervisor \
        tesseract-ocr \
        tesseract-ocr-por \
        git \
        curl \
        poppler-utils \
        libreoffice \
        ufw \
        certbot \
        python3-certbot-nginx \
        htop \
        fail2ban
}

# Função para CentOS/RHEL
deploy_centos() {
    log "Configurando para CentOS/RHEL..."
    
    # Instalar EPEL
    yum install -y epel-release
    yum update -y
    
    # Instalar dependências
    yum install -y \
        python3 \
        python3-pip \
        python3-devel \
        gcc \
        gcc-c++ \
        make \
        postgresql \
        postgresql-server \
        postgresql-devel \
        nginx \
        supervisor \
        tesseract \
        git \
        curl \
        poppler-utils \
        libreoffice \
        firewalld
}

# Instalar dependências baseado no OS
case $OS in
    ubuntu|debian)
        deploy_ubuntu
        ;;
    centos|rhel|fedora)
        deploy_centos
        ;;
    *)
        error "Sistema operacional $OS não suportado"
        exit 1
        ;;
esac

# Criar usuário do sistema
log "Criando usuário do sistema..."
if ! id "$APP_USER" &>/dev/null; then
    useradd --system --shell /bin/bash --home-dir $APP_DIR --create-home $APP_USER
    log "Usuário $APP_USER criado"
else
    log "Usuário $APP_USER já existe"
fi

# Criar estrutura de diretórios
log "Criando estrutura de diretórios..."
mkdir -p $APP_DIR/{app,data,logs,backups,uploads,exports,temp}
chown -R $APP_USER:$APP_USER $APP_DIR

# Copiar aplicação
log "Copiando arquivos da aplicação..."
if [ -d "./venv" ]; then
    warning "Removendo ambiente virtual local..."
    rm -rf ./venv
fi

# Copiar todos os arquivos Python
cp -r *.py $APP_DIR/app/
cp -r templates $APP_DIR/app/ 2>/dev/null || true
cp -r static $APP_DIR/app/ 2>/dev/null || true
cp requirements.txt $APP_DIR/app/ 2>/dev/null || true
cp .env.example $APP_DIR/app/
cp replit.md $APP_DIR/app/
cp homologacao_report.md $APP_DIR/app/

# Configurar ambiente virtual
log "Configurando ambiente virtual Python..."
sudo -u $APP_USER python3 -m venv $APP_DIR/venv
sudo -u $APP_USER $APP_DIR/venv/bin/pip install --upgrade pip

# Instalar dependências Python
log "Instalando dependências Python..."
if [ -f "$APP_DIR/app/requirements.txt" ]; then
    sudo -u $APP_USER $APP_DIR/venv/bin/pip install -r $APP_DIR/app/requirements.txt
else
    sudo -u $APP_USER $APP_DIR/venv/bin/pip install \
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
        gunicorn \
        watchdog \
        requests \
        beautifulsoup4
fi

# Baixar modelo spaCy
log "Baixando modelo spaCy português..."
sudo -u $APP_USER $APP_DIR/venv/bin/python -m spacy download pt_core_news_lg || \
sudo -u $APP_USER $APP_DIR/venv/bin/python -m spacy download pt_core_news_sm

# Configurar PostgreSQL
log "Configurando PostgreSQL..."
if [ "$OS" = "centos" ] || [ "$OS" = "rhel" ]; then
    postgresql-setup initdb
fi

systemctl start postgresql
systemctl enable postgresql

# Criar banco de dados
sudo -u postgres psql -c "CREATE USER $APP_USER WITH PASSWORD 'ncrisisops_secure_2025';" 2>/dev/null || true
sudo -u postgres psql -c "CREATE DATABASE $APP_NAME OWNER $APP_USER;" 2>/dev/null || true
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE $APP_NAME TO $APP_USER;"

# Configurar arquivo .env
log "Configurando variáveis de ambiente..."
cat > $APP_DIR/app/.env << EOF
# n.crisisops - Configuração de Produção
FLASK_ENV=production
FLASK_DEBUG=False
SECRET_KEY=$(openssl rand -hex 32)

# PostgreSQL
DATABASE_URL=postgresql://$APP_USER:ncrisisops_secure_2025@localhost:5432/$APP_NAME
PGHOST=localhost
PGPORT=5432
PGDATABASE=$APP_NAME
PGUSER=$APP_USER
PGPASSWORD=ncrisisops_secure_2025

# Aplicação
PORT=$PORT
HOST=0.0.0.0
WORKERS=4

# Arquivos
MAX_FILE_SIZE=100MB
PROCESSING_TIMEOUT=300

# Logs
LOG_LEVEL=INFO
LOG_FILE=$APP_DIR/logs/ncrisisops.log

# OpenAI (configurar manualmente)
OPENAI_API_KEY=sk-your-openai-key-here
EOF

chown $APP_USER:$APP_USER $APP_DIR/app/.env
chmod 600 $APP_DIR/app/.env

# Configurar Gunicorn
log "Configurando Gunicorn..."
cat > $APP_DIR/gunicorn.conf.py << EOF
# Gunicorn configuration for n.crisisops
bind = "0.0.0.0:$PORT"
workers = 4
worker_class = "sync"
worker_connections = 1000
max_requests = 1000
max_requests_jitter = 100
timeout = 300
keepalive = 5
user = "$APP_USER"
group = "$APP_USER"
tmp_upload_dir = None
logfile = "$APP_DIR/logs/gunicorn.log"
loglevel = "info"
pidfile = "$APP_DIR/gunicorn.pid"
daemon = False
EOF

# Configurar systemd service
log "Configurando serviço systemd..."
cat > /etc/systemd/system/$SERVICE_NAME.service << EOF
[Unit]
Description=n.crisisops LGPD Compliance System
After=network.target postgresql.service
Requires=postgresql.service

[Service]
Type=notify
User=$APP_USER
Group=$APP_USER
RuntimeDirectory=$SERVICE_NAME
WorkingDirectory=$APP_DIR/app
Environment=PATH=$APP_DIR/venv/bin
ExecStart=$APP_DIR/venv/bin/gunicorn --config $APP_DIR/gunicorn.conf.py web_interface:app
ExecReload=/bin/kill -s HUP \$MAINPID
RestartSec=1
Restart=always
StandardOutput=journal
StandardError=journal
SyslogIdentifier=$SERVICE_NAME

[Install]
WantedBy=multi-user.target
EOF

# Configurar Nginx
log "Configurando Nginx..."
cat > $NGINX_CONF << EOF
server {
    listen 80;
    server_name $DOMAIN www.$DOMAIN;
    client_max_body_size 100M;
    
    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "strict-origin-when-cross-origin" always;
    
    # Logs
    access_log $APP_DIR/logs/nginx_access.log;
    error_log $APP_DIR/logs/nginx_error.log;
    
    # Static files
    location /static/ {
        alias $APP_DIR/app/static/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
    
    # Upload size
    location /api/processar {
        client_max_body_size 100M;
        proxy_pass http://127.0.0.1:$PORT;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_read_timeout 300s;
        proxy_connect_timeout 75s;
    }
    
    # Main application
    location / {
        proxy_pass http://127.0.0.1:$PORT;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_read_timeout 60s;
        proxy_connect_timeout 60s;
    }
    
    # Health check
    location /health {
        access_log off;
        return 200 "healthy\n";
        add_header Content-Type text/plain;
    }
}
EOF

# Ativar site no Nginx
ln -sf $NGINX_CONF /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default

# Configurar firewall
log "Configurando firewall..."
if command -v ufw &> /dev/null; then
    ufw --force enable
    ufw allow ssh
    ufw allow 'Nginx Full'
    ufw allow 5432 # PostgreSQL (apenas para admin)
elif command -v firewall-cmd &> /dev/null; then
    systemctl start firewalld
    systemctl enable firewalld
    firewall-cmd --permanent --add-service=ssh
    firewall-cmd --permanent --add-service=http
    firewall-cmd --permanent --add-service=https
    firewall-cmd --reload
fi

# Configurar logrotate
log "Configurando rotação de logs..."
cat > /etc/logrotate.d/ncrisisops << EOF
$APP_DIR/logs/*.log {
    daily
    missingok
    rotate 30
    compress
    delaycompress
    notifempty
    create 644 $APP_USER $APP_USER
    postrotate
        systemctl reload $SERVICE_NAME
    endscript
}
EOF

# Configurar backup automatico
log "Configurando backup automático..."
cat > /usr/local/bin/privacy-backup << EOF
#!/bin/bash
BACKUP_DIR="$APP_DIR/backups"
DATE=\$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="\$BACKUP_DIR/ncrisisops_backup_\$DATE.sql"

mkdir -p \$BACKUP_DIR
sudo -u $APP_USER pg_dump $APP_NAME > \$BACKUP_FILE
gzip \$BACKUP_FILE

# Manter apenas últimos 30 dias
find \$BACKUP_DIR -name "*.gz" -mtime +30 -delete

echo "Backup criado: \$BACKUP_FILE.gz"
EOF

chmod +x /usr/local/bin/privacy-backup

# Configurar cron para backup
(crontab -l 2>/dev/null; echo "0 2 * * * /usr/local/bin/privacy-backup") | crontab -

# Testar configuração do Nginx
nginx -t
if [ $? -ne 0 ]; then
    error "Erro na configuração do Nginx"
    exit 1
fi

# Ajustar permissões finais
chown -R $APP_USER:$APP_USER $APP_DIR
chmod -R 755 $APP_DIR
chmod 600 $APP_DIR/app/.env

# Inicializar banco de dados
log "Inicializando banco de dados..."
cd $APP_DIR/app
sudo -u $APP_USER $APP_DIR/venv/bin/python -c "
import database_postgresql
database_postgresql.initialize_postgresql_database()
print('✅ Banco PostgreSQL inicializado')
"

# Recarregar e iniciar serviços
log "Iniciando serviços..."
systemctl daemon-reload
systemctl enable $SERVICE_NAME
systemctl start $SERVICE_NAME
systemctl reload nginx

# Verificar status dos serviços
sleep 5

if systemctl is-active --quiet $SERVICE_NAME; then
    log "✅ Serviço $SERVICE_NAME ativo"
else
    error "❌ Falha ao iniciar $SERVICE_NAME"
    systemctl status $SERVICE_NAME
    exit 1
fi

if systemctl is-active --quiet nginx; then
    log "✅ Nginx ativo"
else
    error "❌ Falha no Nginx"
    systemctl status nginx
    exit 1
fi

# Teste de conectividade
log "Testando conectividade..."
sleep 2
if curl -f http://localhost/health &>/dev/null; then
    log "✅ Aplicação respondendo"
else
    warning "❌ Aplicação não está respondendo"
fi

# Instruções finais
echo ""
echo "🎉 DEPLOY CONCLUÍDO COM SUCESSO!"
echo "================================"
echo ""
echo "📋 Informações do Deploy:"
echo "• Aplicação: $APP_DIR/app"
echo "• Usuário: $APP_USER"
echo "• Porta: $PORT"
echo "• Logs: $APP_DIR/logs/"
echo "• Backups: $APP_DIR/backups/"
echo ""
echo "🔧 Comandos úteis:"
echo "• Status: systemctl status $SERVICE_NAME"
echo "• Logs: journalctl -u $SERVICE_NAME -f"
echo "• Restart: systemctl restart $SERVICE_NAME"
echo "• Backup: /usr/local/bin/ncrisisops-backup"
echo ""
echo "⚙️  Configurações necessárias:"
echo "1. Configure a chave OpenAI:"
echo "   sudo nano $APP_DIR/app/.env"
echo "   # Edite OPENAI_API_KEY=sk-your-key-here"
echo ""
echo "2. Para HTTPS com SSL:"
echo "   certbot --nginx -d your-domain.com"
echo ""
echo "3. Monitoramento:"
echo "   tail -f $APP_DIR/logs/ncrisisops.log"
echo ""
echo "🌐 Acesso:"
echo "• HTTP: http://$DOMAIN/"
echo "• Logs: $APP_DIR/logs/"
echo ""
echo "2. Para HTTPS com SSL:"
echo "   certbot --nginx -d $DOMAIN"
echo ""
echo "✨ n.crisisops rodando em produção!"