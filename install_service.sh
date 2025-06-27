#!/bin/bash

# =============================================================================
# Script de Instalação/Correção do Serviço Privacy
# n.crisisops - Sistema LGPD
# =============================================================================

echo "🔧 Instalando/Corrigindo serviço privacy na VPS..."

# Verificar se está na VPS
if [ ! -d "/opt/privacy" ]; then
    echo "❌ Diretório /opt/privacy não encontrado"
    echo "💡 Execute primeiro: ./deploy.sh"
    exit 1
fi

# Verificar se é root
if [ "$EUID" -ne 0 ]; then
    echo "❌ Execute como root: sudo ./install_service.sh"
    exit 1
fi

# Criar usuário privacy se não existir
if ! id "privacy" &>/dev/null; then
    echo "👤 Criando usuário privacy..."
    useradd --system --shell /bin/bash --home-dir /opt/privacy --create-home privacy
fi

# Criar estrutura de diretórios
echo "📁 Criando estrutura de diretórios..."
mkdir -p /opt/privacy/{app,data,logs,backups,uploads,exports,temp}
chown -R privacy:privacy /opt/privacy

# Copiar arquivos atualizados se estiverem em /tmp
if [ -f "/tmp/web_interface.py" ]; then
    echo "📝 Atualizando web_interface.py..."
    cp /tmp/web_interface.py /opt/privacy/app/
    chown privacy:privacy /opt/privacy/app/web_interface.py
fi

# Criar arquivo gunicorn.conf.py
echo "⚙️ Configurando Gunicorn..."
cat > /opt/privacy/gunicorn.conf.py << EOF
# Gunicorn configuration for n.crisisops
bind = "0.0.0.0:5000"
workers = 4
worker_class = "sync"
worker_connections = 1000
max_requests = 1000
max_requests_jitter = 100
timeout = 300
keepalive = 5
user = "privacy"
group = "privacy"
tmp_upload_dir = None
logfile = "/opt/privacy/logs/gunicorn.log"
loglevel = "info"
pidfile = "/opt/privacy/gunicorn.pid"
daemon = False
EOF

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
WORKERS=4

# Arquivos
MAX_FILE_SIZE=100MB
PROCESSING_TIMEOUT=300

# Logs
LOG_LEVEL=INFO
LOG_FILE=/opt/privacy/logs/privacy.log

# OpenAI (configurar manualmente)
OPENAI_API_KEY=sk-your-openai-key-here
EOF
    chown privacy:privacy /opt/privacy/app/.env
    chmod 600 /opt/privacy/app/.env
fi

# Configurar PostgreSQL
echo "🗄️ Configurando PostgreSQL..."
systemctl start postgresql
systemctl enable postgresql

# Criar usuário e banco PostgreSQL
sudo -u postgres psql << EOF
-- Criar usuário se não existir
DO \$\$
BEGIN
    IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = 'privacy') THEN
        CREATE USER privacy WITH PASSWORD 'ncrisisops_secure_2025';
    END IF;
END
\$\$;

-- Criar banco se não existir
SELECT 'CREATE DATABASE privacy OWNER privacy'
WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'privacy');

-- Conceder privilégios
GRANT ALL PRIVILEGES ON DATABASE privacy TO privacy;
EOF

# Criar serviço systemd
echo "🚀 Criando serviço systemd..."
cat > /etc/systemd/system/privacy.service << EOF
[Unit]
Description=n.crisisops LGPD Compliance System
After=network.target postgresql.service
Requires=postgresql.service

[Service]
Type=notify
User=privacy
Group=privacy
RuntimeDirectory=privacy
WorkingDirectory=/opt/privacy/app
Environment=PATH=/opt/privacy/venv/bin
ExecStart=/opt/privacy/venv/bin/gunicorn --config /opt/privacy/gunicorn.conf.py web_interface:app
ExecReload=/bin/kill -s HUP \$MAINPID
RestartSec=1
Restart=always
StandardOutput=journal
StandardError=journal
SyslogIdentifier=privacy

[Install]
WantedBy=multi-user.target
EOF

# Recarregar systemd
echo "🔄 Recarregando systemd..."
systemctl daemon-reload
systemctl enable privacy

# Verificar/Instalar dependências Python
echo "🐍 Verificando ambiente Python..."
if [ ! -d "/opt/privacy/venv" ]; then
    echo "📦 Criando ambiente virtual..."
    sudo -u privacy python3 -m venv /opt/privacy/venv
fi

# Instalar dependências básicas
echo "📚 Instalando dependências..."
sudo -u privacy /opt/privacy/venv/bin/pip install --upgrade pip
sudo -u privacy /opt/privacy/venv/bin/pip install \
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

# Baixar modelo spaCy
echo "🌐 Instalando modelo spaCy..."
sudo -u privacy /opt/privacy/venv/bin/python -m spacy download pt_core_news_sm

# Corrigir permissões finais
echo "🔐 Ajustando permissões..."
chown -R privacy:privacy /opt/privacy
chmod 755 /opt/privacy
chmod +x /opt/privacy/venv/bin/python
chmod +x /opt/privacy/venv/bin/gunicorn

# Inicializar banco de dados
echo "💾 Inicializando banco de dados..."
cd /opt/privacy/app
sudo -u privacy /opt/privacy/venv/bin/python -c "
try:
    import database_postgresql
    database_postgresql.initialize_postgresql_database()
    print('✅ Banco PostgreSQL inicializado')
except Exception as e:
    print(f'⚠️ Erro ao inicializar banco: {e}')
    print('Continuando...')
"

# Testar aplicação
echo "🧪 Testando aplicação..."
timeout 10s sudo -u privacy /opt/privacy/venv/bin/python /opt/privacy/app/web_interface.py &
TEST_PID=$!
sleep 5
kill $TEST_PID 2>/dev/null
echo "✅ Teste de importação concluído"

# Iniciar serviço
echo "🚀 Iniciando serviço privacy..."
systemctl start privacy
sleep 5

# Verificar status
echo "📊 Verificando status..."
if systemctl is-active --quiet privacy; then
    echo "✅ Serviço privacy ativo"
    
    # Testar health check
    sleep 3
    if curl -s http://localhost:5000/health > /dev/null; then
        echo "✅ Health check funcionando"
    else
        echo "⚠️ Health check ainda não responde - aguarde mais um momento"
    fi
else
    echo "❌ Serviço privacy falhou"
    echo "📋 Logs recentes:"
    journalctl -u privacy --no-pager -n 20
fi

# Configurar Nginx se não estiver configurado
if [ ! -f "/etc/nginx/sites-available/privacy" ]; then
    echo "🌍 Configurando Nginx..."
    cat > /etc/nginx/sites-available/privacy << EOF
server {
    listen 80;
    server_name monster.e-ness.com.br www.monster.e-ness.com.br;
    client_max_body_size 100M;
    
    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "strict-origin-when-cross-origin" always;
    
    # Logs
    access_log /opt/privacy/logs/nginx_access.log;
    error_log /opt/privacy/logs/nginx_error.log;
    
    # Static files
    location /static/ {
        alias /opt/privacy/app/static/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
    
    # Health check
    location /health {
        access_log off;
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
    
    # Upload size
    location /api/processar {
        client_max_body_size 100M;
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_read_timeout 300s;
        proxy_connect_timeout 75s;
    }
    
    # Main application
    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_read_timeout 60s;
        proxy_connect_timeout 60s;
    }
}
EOF

    # Ativar site
    ln -sf /etc/nginx/sites-available/privacy /etc/nginx/sites-enabled/
    rm -f /etc/nginx/sites-enabled/default
    
    # Testar e recarregar Nginx
    nginx -t && systemctl reload nginx
fi

echo ""
echo "🎉 Instalação do serviço concluída!"
echo ""
echo "📋 Status dos serviços:"
systemctl status privacy --no-pager -l
echo ""
echo "🌐 Testes finais:"
echo "• Health check: curl http://localhost:5000/health"
echo "• Aplicação: http://monster.e-ness.com.br"
echo ""
echo "📖 Para logs: journalctl -u privacy -f"