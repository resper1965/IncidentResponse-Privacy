#!/bin/bash

# Deploy n.crisisops LGPD System to VPS - Final Version
# Resolves all LangChain dependency conflicts definitively

set -e

echo "🚀 Iniciando deploy definitivo do sistema LGPD n.crisisops..."

# Configurações
INSTALL_PATH="/opt/privacy"
SERVICE_USER="privacy"
DOMAIN="monster.e-ness.com.br"
DB_NAME="privacy_db"
DB_USER="privacy_user"
DB_PASS="Lgpd2025#Privacy"

# Verificar se está rodando como root
if [[ $EUID -ne 0 ]]; then
   echo "❌ Este script deve ser executado como root"
   exit 1
fi

echo "📦 Atualizando sistema..."
apt update && apt upgrade -y

echo "📦 Instalando dependências do sistema..."
apt install -y python3 python3-pip python3-venv postgresql postgresql-contrib \
               nginx certbot python3-certbot-nginx tesseract-ocr tesseract-ocr-por \
               git curl wget build-essential libpq-dev python3-dev

# Configurar PostgreSQL
echo "🗄️ Configurando PostgreSQL..."
systemctl start postgresql
systemctl enable postgresql

sudo -u postgres psql -c "CREATE USER $DB_USER WITH PASSWORD '$DB_PASS';" || echo "User already exists"
sudo -u postgres psql -c "CREATE DATABASE $DB_NAME OWNER $DB_USER;" || echo "Database already exists"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE $DB_NAME TO $DB_USER;"

# Criar usuário do sistema
echo "👤 Criando usuário do sistema..."
useradd -r -s /bin/bash -d $INSTALL_PATH $SERVICE_USER || echo "User already exists"

# Criar diretório de instalação
mkdir -p $INSTALL_PATH
chown $SERVICE_USER:$SERVICE_USER $INSTALL_PATH

# Copiar arquivos (assumindo que estão no diretório atual)
echo "📁 Copiando arquivos do sistema..."
cp -r . $INSTALL_PATH/
chown -R $SERVICE_USER:$SERVICE_USER $INSTALL_PATH

# Configurar ambiente Python
echo "🐍 Configurando ambiente Python..."
cd $INSTALL_PATH
sudo -u $SERVICE_USER python3 -m venv venv

# Ativar virtual environment e instalar dependências com versões fixas
echo "📦 Instalando dependências Python com versões compatíveis..."
sudo -u $SERVICE_USER bash -c "
source venv/bin/activate
pip install --upgrade pip

# Instalar dependências em ordem específica para evitar conflitos
pip install flask==3.0.0 flask-cors==4.0.0 gunicorn==21.2.0
pip install psycopg2-binary==2.9.9 sqlalchemy==2.0.23
pip install pandas==2.1.4 plotly==5.17.0
pip install openpyxl==3.1.2 python-docx==1.1.0 pdfplumber==0.10.3
pip install pymupdf==1.23.8 python-pptx==0.6.23 extract-msg==0.48.5
pip install pytesseract==0.3.10 pillow==10.1.0
pip install beautifulsoup4==4.12.2 lxml==4.9.3 striprtf==0.0.26 eml-parser==2.0.0
pip install spacy==3.7.2 openai==1.3.7
pip install python-dotenv==1.0.0

# Instalar LangChain com versões específicas compatíveis
pip install langchain-core==0.2.43
pip install langchain-text-splitters==0.2.4
pip install langchain-community==0.2.17
pip install langchain==0.2.17
pip install langchain-openai==0.2.17

# Instalar modelo spaCy para português
python -m spacy download pt_core_news_sm
"

# Criar arquivo de configuração de produção
echo "⚙️ Criando configuração de produção..."
sudo -u $SERVICE_USER cat > $INSTALL_PATH/.env << EOF
# Configuração de Produção - n.crisisops LGPD
DATABASE_URL=postgresql://$DB_USER:$DB_PASS@localhost:5432/$DB_NAME
PGHOST=localhost
PGPORT=5432
PGUSER=$DB_USER
PGPASSWORD=$DB_PASS
PGDATABASE=$DB_NAME
FLASK_ENV=production
FLASK_DEBUG=False
OPENAI_API_KEY=your_openai_key_here
EOF

# Inicializar banco de dados
echo "🗄️ Inicializando banco de dados..."
sudo -u $SERVICE_USER bash -c "
cd $INSTALL_PATH
source venv/bin/activate
python database_postgresql.py
python scripts/populate-database.py
"

# Configurar Gunicorn
echo "🔧 Configurando Gunicorn..."
sudo -u $SERVICE_USER cat > $INSTALL_PATH/gunicorn.conf.py << 'EOF'
import multiprocessing

# Server socket
bind = "127.0.0.1:5000"
backlog = 2048

# Worker processes
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "sync"
worker_connections = 1000
timeout = 30
keepalive = 2

# Restart workers after this many requests
max_requests = 1000
max_requests_jitter = 50

# Logging
errorlog = "/opt/privacy/logs/gunicorn_error.log"
accesslog = "/opt/privacy/logs/gunicorn_access.log"
loglevel = "info"

# Process naming
proc_name = "privacy_gunicorn"

# Server mechanics
daemon = False
pidfile = "/opt/privacy/logs/gunicorn.pid"
user = "privacy"
group = "privacy"
tmp_upload_dir = None

# SSL (if needed)
preload_app = True
EOF

# Criar diretórios de log
mkdir -p $INSTALL_PATH/logs
chown $SERVICE_USER:$SERVICE_USER $INSTALL_PATH/logs

# Configurar systemd service
echo "⚙️ Configurando serviço systemd..."
cat > /etc/systemd/system/privacy.service << EOF
[Unit]
Description=n.crisisops Privacy LGPD System
After=network.target postgresql.service
Requires=postgresql.service

[Service]
Type=notify
User=$SERVICE_USER
Group=$SERVICE_USER
WorkingDirectory=$INSTALL_PATH
Environment="PATH=$INSTALL_PATH/venv/bin"
ExecStart=$INSTALL_PATH/venv/bin/gunicorn --config gunicorn.conf.py web_interface:app
ExecReload=/bin/kill -s HUP \$MAINPID
KillMode=mixed
TimeoutStopSec=5
PrivateTmp=true
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Configurar Nginx
echo "🌐 Configurando Nginx..."
cat > /etc/nginx/sites-available/$DOMAIN << EOF
server {
    listen 80;
    server_name $DOMAIN;
    
    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header Referrer-Policy "no-referrer-when-downgrade" always;
    add_header Content-Security-Policy "default-src 'self' http: https: data: blob: 'unsafe-inline'" always;
    
    # Rate limiting
    limit_req_zone \$binary_remote_addr zone=api:10m rate=10r/s;
    
    location / {
        limit_req zone=api burst=20 nodelay;
        
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        
        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }
    
    # Static files
    location /static {
        alias $INSTALL_PATH/static;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
    
    # Health check
    location /health {
        access_log off;
        proxy_pass http://127.0.0.1:5000/health;
    }
}
EOF

# Ativar site no Nginx
ln -sf /etc/nginx/sites-available/$DOMAIN /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default

# Testar configuração do Nginx
nginx -t

# Configurar SSL com Let's Encrypt
echo "🔒 Configurando SSL..."
systemctl reload nginx
certbot --nginx -d $DOMAIN --non-interactive --agree-tos --email admin@$DOMAIN

# Configurar renovação automática SSL
echo "0 12 * * * /usr/bin/certbot renew --quiet" | crontab -

# Iniciar serviços
echo "🚀 Iniciando serviços..."
systemctl daemon-reload
systemctl enable privacy
systemctl start privacy
systemctl enable nginx
systemctl restart nginx

# Testar sistema
echo "🧪 Testando sistema..."
sleep 10

if curl -f http://localhost:5000/health >/dev/null 2>&1; then
    echo "✅ Sistema funcionando localmente"
else
    echo "⚠️ Sistema não responde localmente"
fi

if curl -f https://$DOMAIN/health >/dev/null 2>&1; then
    echo "✅ Sistema funcionando via HTTPS"
else
    echo "⚠️ Sistema não responde via HTTPS"
fi

# Status final
echo ""
echo "🎉 Deploy concluído com sucesso!"
echo ""
echo "📋 Informações do sistema:"
echo "   🌐 URL: https://$DOMAIN"
echo "   📁 Instalação: $INSTALL_PATH"
echo "   👤 Usuário: $SERVICE_USER"
echo "   🗄️ Banco: $DB_NAME"
echo ""
echo "📊 Comandos úteis:"
echo "   systemctl status privacy    # Status do serviço"
echo "   systemctl restart privacy   # Reiniciar serviço"
echo "   tail -f $INSTALL_PATH/logs/gunicorn_error.log  # Ver logs"
echo ""
echo "⚠️ Lembre-se de configurar a chave OpenAI em $INSTALL_PATH/.env"
echo ""