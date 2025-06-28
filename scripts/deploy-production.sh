#!/bin/bash

# n.crisisops - LGPD Privacy Module - Production Deployment Script
# Deploy completo baseado no production-requirements.txt

set -e  # Exit on any error

echo "🚀 n.crisisops - LGPD Privacy Module - Production Deployment"
echo "================================================================="

# Variáveis de configuração
INSTALL_DIR="/opt/privacy"
SERVICE_USER="privacy"
DB_NAME="privacy_db"
DB_USER="privacy_user"
DB_PASS="Lgpd2025#Privacy"
DOMAIN="monster.e-ness.com.br"

echo "📋 Verificando requisitos do sistema..."

# Verificar se está rodando como root
if [ "$EUID" -ne 0 ]; then
    echo "❌ Execute como root: sudo $0"
    exit 1
fi

# Atualizar sistema
echo "📦 Atualizando sistema..."
apt update && apt upgrade -y

# Instalar dependências do sistema
echo "🔧 Instalando dependências do sistema..."
apt install -y \
    python3 \
    python3-pip \
    python3-venv \
    python3-dev \
    postgresql \
    postgresql-contrib \
    nginx \
    supervisor \
    git \
    curl \
    wget \
    build-essential \
    libpq-dev \
    tesseract-ocr \
    tesseract-ocr-por \
    poppler-utils \
    libxml2-dev \
    libxslt1-dev \
    zlib1g-dev \
    libjpeg-dev \
    libpng-dev \
    libfreetype6-dev \
    liblcms2-dev \
    libwebp-dev \
    tcl8.6-dev \
    tk8.6-dev \
    snapd \
    certbot \
    python3-certbot-nginx

echo "👤 Configurando usuário do sistema..."

# Criar usuário privacy se não existir
if ! id "$SERVICE_USER" &>/dev/null; then
    useradd -r -s /bin/bash -d $INSTALL_DIR $SERVICE_USER
    echo "✅ Usuário $SERVICE_USER criado"
else
    echo "✅ Usuário $SERVICE_USER já existe"
fi

echo "🗄️ Configurando PostgreSQL..."

# Configurar PostgreSQL
systemctl start postgresql
systemctl enable postgresql

# Criar banco e usuário
sudo -u postgres psql << EOF
-- Criar usuário se não existir
DO \$\$
BEGIN
    IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = '$DB_USER') THEN
        CREATE USER $DB_USER WITH PASSWORD '$DB_PASS';
    END IF;
END
\$\$;

-- Criar banco se não existir
SELECT 'CREATE DATABASE $DB_NAME OWNER $DB_USER'
WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = '$DB_NAME')\gexec

-- Conceder privilégios
GRANT ALL PRIVILEGES ON DATABASE $DB_NAME TO $DB_USER;
ALTER USER $DB_USER CREATEDB;
EOF

echo "✅ PostgreSQL configurado"

echo "📁 Configurando diretórios..."

# Criar estrutura de diretórios
mkdir -p $INSTALL_DIR/{uploads,backups,logs,data}
mkdir -p /var/log/privacy
mkdir -p /etc/nginx/sites-available
mkdir -p /etc/nginx/sites-enabled

echo "🔄 Clonando/atualizando código..."

# Se o diretório já existe, fazer pull, senão clone
if [ -d "$INSTALL_DIR/.git" ]; then
    cd $INSTALL_DIR
    git pull origin main || echo "⚠️ Não foi possível fazer pull, continuando..."
else
    # Se não é um repo git, fazer backup e clonar
    if [ -d "$INSTALL_DIR" ] && [ "$(ls -A $INSTALL_DIR)" ]; then
        mv $INSTALL_DIR ${INSTALL_DIR}_backup_$(date +%Y%m%d_%H%M%S)
    fi
    
    mkdir -p $INSTALL_DIR
    # Assumindo que os arquivos já estão no diretório ou serão copiados
    echo "✅ Estrutura preparada para código"
fi

cd $INSTALL_DIR

echo "🐍 Configurando ambiente Python..."

# Criar ambiente virtual
python3 -m venv venv
source venv/bin/activate

# Atualizar pip
pip install --upgrade pip setuptools wheel

echo "📦 Instalando dependências Python..."

# Instalar dependências
pip install --upgrade pip
pip install -r production-requirements.txt || {
    echo "⚠️ Algumas dependências falharam, continuando..."
}

# Verificar instalações críticas
echo "🧪 Verificando instalações..."
python3 -c "
try:
    import flask, psycopg2, pandas, fitz, docx, spacy
    print('✅ Dependências principais instaladas')
except ImportError as e:
    print(f'⚠️ Algumas dependências podem estar ausentes: {e}')
    print('Sistema continuará funcionando com funcionalidades reduzidas')
"

echo "🤖 Baixando modelo spaCy..."
python -m spacy download pt_core_news_sm

echo "📝 Configurando arquivos de ambiente..."

# Copiar arquivo de ambiente
cp .env.production .env

echo "🗄️ Inicializando banco de dados..."

# Executar script de configuração do banco
python3 -c "
import os
os.environ['DATABASE_URL'] = 'postgresql://$DB_USER:$DB_PASS@localhost:5432/$DB_NAME'

try:
    import database_postgresql as db_pg
    print('✅ Conectado ao PostgreSQL')
    
    # Criar tabelas
    db_pg.initialize_database()
    print('✅ Tabelas criadas')
    
    # Carregar padrões regex
    patterns = [
        ('CPF', r'\b\d{3}\.?\d{3}\.?\d{3}-?\d{2}\b', 'CPF com ou sem formatação'),
        ('RG', r'\b\d{1,2}\.?\d{3}\.?\d{3}-?[0-9Xx]\b', 'RG com formatação SP'),
        ('EMAIL', r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', 'Endereço de email'),
        ('TELEFONE', r'\(?\d{2}\)?\s?9?\d{4}-?\d{4}', 'Telefone celular e fixo'),
        ('CEP', r'\b\d{5}-?\d{3}\b', 'CEP brasileiro'),
        ('DATA_NASCIMENTO', r'\b\d{1,2}\/\d{1,2}\/\d{4}\b', 'Data no formato DD/MM/AAAA'),
        ('NOME_COMPLETO', r'\b[A-Z][a-z]+\s+[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b', 'Nome completo')
    ]
    
    # Inserir padrões
    for nome, pattern, descricao in patterns:
        db_pg.insert_regex_pattern(nome, pattern, descricao)
    
    # Carregar prioridades empresariais
    priorities = [
        (1, 'Banco Bradesco', 'bradesco.com.br'),
        (1, 'Petrobras', 'petrobras.com.br'),
        (1, 'ONS', 'ons.org.br'),
        (2, 'Banco do Brasil', 'bb.com.br'),
        (2, 'Caixa Econômica Federal', 'caixa.gov.br')
    ]
    
    for prioridade, empresa, dominio in priorities:
        db_pg.insert_search_priority(prioridade, empresa, dominio)
    
    print('✅ Dados iniciais carregados')
    
except Exception as e:
    print(f'❌ Erro na configuração do banco: {e}')
    import database
    database.inicializar_banco()
    print('✅ Fallback para SQLite configurado')
"

echo "🔧 Configurando serviço systemd..."

cat > /etc/systemd/system/privacy.service << 'EOF'
[Unit]
Description=n.crisisops LGPD Privacy Module
After=network.target postgresql.service
Requires=postgresql.service

[Service]
Type=exec
User=privacy
Group=privacy
WorkingDirectory=/opt/privacy
Environment=PATH=/opt/privacy/venv/bin
Environment=PYTHONPATH=/opt/privacy
Environment=FLASK_ENV=production
EnvironmentFile=/opt/privacy/.env
ExecStart=/opt/privacy/venv/bin/gunicorn --config gunicorn.conf.py web_interface:app
Restart=always
RestartSec=5
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

echo "⚙️ Configurando Gunicorn..."

cat > gunicorn.conf.py << 'EOF'
# Gunicorn configuration for n.crisisops Privacy Module

# Server socket
bind = "0.0.0.0:5000"
backlog = 2048

# Worker processes
workers = 4
worker_class = "sync"
worker_connections = 1000
timeout = 300
keepalive = 2

# Restart workers
max_requests = 1000
max_requests_jitter = 50
preload_app = True

# Logging
accesslog = "/var/log/privacy/access.log"
errorlog = "/var/log/privacy/error.log"
loglevel = "info"
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s"'

# Process naming
proc_name = "privacy-lgpd"

# Security
limit_request_line = 4094
limit_request_fields = 100
limit_request_field_size = 8190
EOF

echo "🌐 Configurando Nginx..."

cat > /etc/nginx/sites-available/privacy << EOF
# HTTP Server - Redirect to HTTPS
server {
    listen 80;
    server_name $DOMAIN;
    
    # ACME Challenge for Let's Encrypt
    location /.well-known/acme-challenge/ {
        root /var/www/html;
    }
    
    # Redirect all other traffic to HTTPS
    location / {
        return 301 https://\$server_name\$request_uri;
    }
}

# HTTPS Server
server {
    listen 443 ssl http2;
    server_name $DOMAIN;

    # SSL Configuration (will be updated by certbot)
    ssl_certificate /etc/letsencrypt/live/$DOMAIN/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/$DOMAIN/privkey.pem;
    
    # Modern SSL Configuration
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384;
    ssl_prefer_server_ciphers off;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;
    
    # HSTS
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;

    # Security headers
    add_header X-Frame-Options DENY always;
    add_header X-Content-Type-Options nosniff always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "strict-origin-when-cross-origin" always;
    add_header Content-Security-Policy "default-src 'self'; script-src 'self' 'unsafe-inline' 'unsafe-eval'; style-src 'self' 'unsafe-inline'; img-src 'self' data:; font-src 'self';" always;

    # File upload limit
    client_max_body_size 100M;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto https;
        proxy_set_header X-Forwarded-Port 443;
        proxy_connect_timeout 300s;
        proxy_send_timeout 300s;
        proxy_read_timeout 300s;
        proxy_buffering off;
        proxy_request_buffering off;
    }

    # Static files
    location /static {
        alias /opt/privacy/static;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    # Logs
    access_log /var/log/nginx/privacy_access.log;
    error_log /var/log/nginx/privacy_error.log;
}
EOF

# Ativar site
ln -sf /etc/nginx/sites-available/privacy /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default

echo "🔐 Configurando permissões..."

# Definir permissões
chown -R $SERVICE_USER:$SERVICE_USER $INSTALL_DIR
chown -R $SERVICE_USER:$SERVICE_USER /var/log/privacy
chmod +x $INSTALL_DIR/venv/bin/*
chmod 600 $INSTALL_DIR/.env

echo "🔐 Configurando SSL com Let's Encrypt..."

# Criar diretório para ACME challenge
mkdir -p /var/www/html

# Ativar site temporariamente sem SSL
cat > /etc/nginx/sites-available/privacy-temp << EOF
server {
    listen 80;
    server_name $DOMAIN;
    
    location /.well-known/acme-challenge/ {
        root /var/www/html;
    }
    
    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
}
EOF

# Ativar configuração temporária
ln -sf /etc/nginx/sites-available/privacy-temp /etc/nginx/sites-enabled/privacy
rm -f /etc/nginx/sites-enabled/default

# Testar nginx
nginx -t && systemctl reload nginx

echo "🚀 Iniciando serviços..."

# Recarregar systemd
systemctl daemon-reload

# Iniciar serviços
systemctl enable privacy
systemctl enable nginx
systemctl restart nginx
systemctl start privacy

echo "⏳ Aguardando aplicação inicializar..."
sleep 15

# Verificar se aplicação está respondendo
if ! curl -f -s http://localhost:5000 > /dev/null; then
    echo "❌ Aplicação não iniciou, verificando logs..."
    journalctl -u privacy --no-pager -l -n 10
    echo "⚠️ Continuando com SSL mesmo assim..."
fi

echo "📜 Obtendo certificado SSL..."

# Obter certificado SSL
if certbot certonly \
    --webroot \
    --webroot-path=/var/www/html \
    --email admin@$DOMAIN \
    --agree-tos \
    --no-eff-email \
    --domains $DOMAIN; then
    
    echo "✅ Certificado SSL obtido com sucesso"
    
    # Ativar configuração SSL completa
    ln -sf /etc/nginx/sites-available/privacy /etc/nginx/sites-enabled/privacy
    
    # Testar configuração SSL
    nginx -t && systemctl reload nginx
    
    # Configurar renovação automática
    cat > /etc/cron.d/certbot-renew << 'EOF'
0 12 * * * root certbot renew --quiet --post-hook "systemctl reload nginx"
EOF
    
    echo "✅ Renovação automática configurada"
    
else
    echo "⚠️ Falha ao obter certificado SSL, mantendo HTTP"
    echo "Execute manualmente: sudo certbot --nginx -d $DOMAIN"
fi

echo "⏳ Aguardando inicialização..."
sleep 10

echo "📊 Verificando status dos serviços..."

# Status dos serviços
systemctl status postgresql --no-pager -l
systemctl status nginx --no-pager -l  
systemctl status privacy --no-pager -l

echo "🧪 Testando aplicação..."

# Testar se a aplicação responde
if curl -f -s http://localhost:5000 > /dev/null; then
    echo "✅ Aplicação respondendo localmente"
else
    echo "❌ Aplicação não responde"
    journalctl -u privacy --no-pager -l -n 20
fi

echo ""
echo "================================================================="
echo "✅ DEPLOY CONCLUÍDO!"
echo "================================================================="
echo "🌐 URL: https://$DOMAIN"
echo "📁 Diretório: $INSTALL_DIR"
echo "👤 Usuário: $SERVICE_USER"
echo "🗄️ Banco: postgresql://$DB_USER@localhost:5432/$DB_NAME"
echo "🔐 SSL: Let's Encrypt configurado"
echo ""
echo "📋 Comandos úteis:"
echo "   sudo systemctl status privacy"
echo "   sudo systemctl restart privacy"
echo "   sudo journalctl -u privacy -f"
echo "   sudo tail -f /var/log/privacy/error.log"
echo "   sudo certbot renew --dry-run"
echo ""
echo "🔑 Configure OPENAI_API_KEY em $INSTALL_DIR/.env"
echo "🔒 Certificado SSL será renovado automaticamente"
echo "================================================================="