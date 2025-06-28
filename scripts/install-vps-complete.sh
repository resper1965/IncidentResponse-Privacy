#!/bin/bash

# Script de instalação completa para VPS - Sistema LGPD n.crisisops
# Testado em Ubuntu 20.04/22.04 e CentOS 7/8

set -e

echo "🚀 Instalando Sistema LGPD n.crisisops no VPS"
echo "=============================================="

# Verificar se é root ou sudo
if [[ $EUID -ne 0 ]]; then
   echo "❌ Este script precisa ser executado como root ou com sudo"
   exit 1
fi

# Detectar sistema operacional
if [ -f /etc/os-release ]; then
    . /etc/os-release
    OS=$NAME
    VER=$VERSION_ID
else
    echo "❌ Não foi possível detectar o sistema operacional"
    exit 1
fi

echo "📋 Sistema detectado: $OS $VER"

# Atualizar sistema
echo "🔄 Atualizando sistema..."
if [[ "$OS" == *"Ubuntu"* ]] || [[ "$OS" == *"Debian"* ]]; then
    apt update -y
    apt upgrade -y
    apt install -y curl wget git nginx python3 python3-pip python3-venv postgresql postgresql-contrib supervisor ufw certbot python3-certbot-nginx
elif [[ "$OS" == *"CentOS"* ]] || [[ "$OS" == *"Red Hat"* ]] || [[ "$OS" == *"Rocky"* ]]; then
    yum update -y
    yum install -y curl wget git nginx python3 python3-pip postgresql postgresql-server postgresql-contrib supervisor firewalld certbot python3-certbot-nginx
    postgresql-setup initdb
    systemctl enable postgresql
    systemctl start postgresql
fi

# Criar usuário do sistema
echo "👤 Criando usuário do sistema..."
useradd -m -s /bin/bash lgpd || true
usermod -aG sudo lgpd || true

# Criar diretório da aplicação
echo "📁 Criando estrutura de diretórios..."
mkdir -p /opt/privacy
chown lgpd:lgpd /opt/privacy
cd /opt/privacy

# Baixar código do repositório
echo "📥 Baixando código do sistema..."
if [ -d ".git" ]; then
    echo "⚠️  Repositório já existe, atualizando..."
    sudo -u lgpd git pull
else
    sudo -u lgpd git clone https://github.com/your-repo/lgpd-system.git .
fi

# Instalar dependências Python
echo "🐍 Instalando Python e dependências..."
sudo -u lgpd python3 -m venv venv
sudo -u lgpd ./venv/bin/pip install --upgrade pip

# Instalar dependências em ordem específica para evitar conflitos
echo "📦 Instalando dependências específicas..."
sudo -u lgpd ./venv/bin/pip install wheel setuptools

# Dependências core
sudo -u lgpd ./venv/bin/pip install \
    flask==3.0.0 \
    gunicorn==21.2.0 \
    psycopg2-binary==2.9.9 \
    asyncpg==0.29.0 \
    pandas==2.1.4 \
    openpyxl==3.1.2

# Dependências de processamento de arquivos
sudo -u lgpd ./venv/bin/pip install \
    pdfplumber==0.10.3 \
    PyMuPDF==1.23.22 \
    python-docx==1.1.0 \
    pillow==10.1.0 \
    pytesseract==0.3.10 \
    extract-msg==0.41.1 \
    python-pptx==0.6.23 \
    beautifulsoup4==4.12.2 \
    striprtf==0.0.26

# Dependências de IA (ordem específica)
sudo -u lgpd ./venv/bin/pip install \
    langchain-core==0.2.43 \
    langchain-text-splitters==0.2.4 \
    langchain==0.2.17 \
    langchain-openai==0.1.25 \
    langchain-community==0.2.17 \
    openai==1.45.0

# Dependências adicionais
sudo -u lgpd ./venv/bin/pip install \
    spacy==3.7.2 \
    python-dotenv==1.0.0 \
    plotly==5.17.0 \
    watchdog==3.0.0

# Instalar modelo spaCy para português
echo "🧠 Instalando modelo de linguagem..."
sudo -u lgpd ./venv/bin/python -m spacy download pt_core_news_sm

# Configurar PostgreSQL
echo "🗄️ Configurando PostgreSQL..."
systemctl start postgresql
systemctl enable postgresql

# Criar banco e usuário
sudo -u postgres psql << EOF
CREATE DATABASE privacy_db;
CREATE USER privacy_user WITH PASSWORD 'Lgpd2025#Privacy';
GRANT ALL PRIVILEGES ON DATABASE privacy_db TO privacy_user;
ALTER USER privacy_user CREATEDB;
\q
EOF

# Configurar arquivo .env
echo "⚙️ Configurando variáveis de ambiente..."
cat > /opt/privacy/.env << EOF
DATABASE_URL=postgresql://privacy_user:Lgpd2025%23Privacy@localhost:5432/privacy_db
OPENAI_API_KEY=sua_chave_openai_aqui
FLASK_ENV=production
FLASK_DEBUG=False
SECRET_KEY=$(openssl rand -hex 32)
EOF

chown lgpd:lgpd /opt/privacy/.env
chmod 600 /opt/privacy/.env

# Configurar Gunicorn
echo "🔧 Configurando Gunicorn..."
cat > /opt/privacy/gunicorn.conf.py << 'EOF'
import multiprocessing

bind = "127.0.0.1:5000"
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "sync"
worker_connections = 1000
max_requests = 1000
max_requests_jitter = 100
timeout = 300
keepalive = 5
preload_app = True
user = "lgpd"
group = "lgpd"
tmp_upload_dir = None
secure_scheme_headers = {
    'X-FORWARDED-PROTOCOL': 'ssl',
    'X-FORWARDED-PROTO': 'https',
    'X-FORWARDED-SSL': 'on'
}
EOF

# Configurar serviço systemd
echo "⚡ Configurando serviço systemd..."
cat > /etc/systemd/system/privacy.service << 'EOF'
[Unit]
Description=n.crisisops Privacy LGPD System
After=network.target postgresql.service
Requires=postgresql.service

[Service]
Type=notify
User=lgpd
Group=lgpd
WorkingDirectory=/opt/privacy
Environment=PATH=/opt/privacy/venv/bin
ExecStart=/opt/privacy/venv/bin/gunicorn --config gunicorn.conf.py web_interface:app
ExecReload=/bin/kill -s HUP $MAINPID
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
cat > /etc/nginx/sites-available/privacy << 'EOF'
server {
    listen 80;
    server_name _;
    
    # Redirecionar HTTP para HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name _;
    
    # Certificados SSL (serão configurados pelo Certbot)
    ssl_certificate /etc/letsencrypt/live/SEU_DOMINIO/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/SEU_DOMINIO/privkey.pem;
    
    # Configurações SSL modernas
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512:ECDHE-RSA-AES256-GCM-SHA384:DHE-RSA-AES256-GCM-SHA384;
    ssl_prefer_server_ciphers off;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;
    
    # Headers de segurança
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Content-Type-Options nosniff always;
    add_header X-Frame-Options DENY always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "strict-origin-when-cross-origin" always;
    
    # Configurações de upload
    client_max_body_size 100M;
    
    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header X-Forwarded-Host $host;
        proxy_set_header X-Forwarded-Port $server_port;
        
        # Timeouts
        proxy_connect_timeout 300s;
        proxy_send_timeout 300s;
        proxy_read_timeout 300s;
    }
    
    # Servir arquivos estáticos
    location /static {
        alias /opt/privacy/static;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
EOF

# Habilitar site
ln -sf /etc/nginx/sites-available/privacy /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default

# Configurar firewall
echo "🔥 Configurando firewall..."
if [[ "$OS" == *"Ubuntu"* ]] || [[ "$OS" == *"Debian"* ]]; then
    ufw --force enable
    ufw allow ssh
    ufw allow 'Nginx Full'
    ufw allow 5432
elif [[ "$OS" == *"CentOS"* ]] || [[ "$OS" == *"Red Hat"* ]] || [[ "$OS" == *"Rocky"* ]]; then
    systemctl start firewalld
    systemctl enable firewalld
    firewall-cmd --permanent --add-service=ssh
    firewall-cmd --permanent --add-service=http
    firewall-cmd --permanent --add-service=https
    firewall-cmd --permanent --add-port=5432/tcp
    firewall-cmd --reload
fi

# Inicializar banco de dados
echo "🗄️ Inicializando banco de dados..."
cd /opt/privacy
sudo -u lgpd ./venv/bin/python << 'EOF'
from database_postgresql import inicializar_database_postgresql
from database import carregar_empresas_padrao, carregar_prioridades_padrao, carregar_regex_padrao

print("Inicializando PostgreSQL...")
inicializar_database_postgresql()

print("Carregando dados padrão...")
carregar_empresas_padrao()
carregar_prioridades_padrao()
carregar_regex_padrao()

print("✅ Banco de dados inicializado com sucesso!")
EOF

# Habilitar e iniciar serviços
echo "🚀 Iniciando serviços..."
systemctl daemon-reload
systemctl enable privacy
systemctl start privacy
systemctl enable nginx
systemctl restart nginx

# Verificar status
echo "🔍 Verificando status dos serviços..."
systemctl status postgresql --no-pager -l
systemctl status privacy --no-pager -l
systemctl status nginx --no-pager -l

echo ""
echo "✅ INSTALAÇÃO CONCLUÍDA!"
echo "========================="
echo ""
echo "📋 Próximos passos:"
echo ""
echo "1. Configurar seu domínio:"
echo "   - Edite /etc/nginx/sites-available/privacy"
echo "   - Substitua 'SEU_DOMINIO' pelo seu domínio real"
echo ""
echo "2. Configurar SSL com Let's Encrypt:"
echo "   sudo certbot --nginx -d seudominio.com"
echo ""
echo "3. Adicionar sua chave OpenAI:"
echo "   sudo nano /opt/privacy/.env"
echo "   # Edite OPENAI_API_KEY=sua_chave_aqui"
echo ""
echo "4. Reiniciar serviço:"
echo "   sudo systemctl restart privacy"
echo ""
echo "5. Testar acesso:"
echo "   http://seu-ip-ou-dominio"
echo ""
echo "📂 Diretórios importantes:"
echo "   - Aplicação: /opt/privacy"
echo "   - Logs: sudo journalctl -u privacy -f"
echo "   - Nginx: /var/log/nginx/"
echo ""
echo "🔐 Credenciais PostgreSQL:"
echo "   - Banco: privacy_db"
echo "   - Usuário: privacy_user"
echo "   - Senha: Lgpd2025#Privacy"
echo ""
echo "🎉 Sistema LGPD instalado e funcionando!"