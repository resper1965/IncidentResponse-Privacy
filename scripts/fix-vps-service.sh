#!/bin/bash

echo "🔧 Corrigindo serviço privacy na VPS"

# Verificar logs detalhados
echo "📋 Verificando logs do serviço..."
journalctl -u privacy --no-pager -l -n 50

echo ""
echo "🔍 Verificando estrutura de arquivos..."
ls -la /opt/privacy/

echo ""
echo "📦 Verificando dependências Python..."
cd /opt/privacy
if [ -f "venv/bin/activate" ]; then
    source venv/bin/activate
    echo "✅ Virtual environment ativo"
    
    # Verificar se Flask está instalado
    python -c "import flask; print(f'Flask: {flask.__version__}')" 2>/dev/null || echo "❌ Flask não encontrado"
    python -c "import gunicorn; print(f'Gunicorn: {gunicorn.__version__}')" 2>/dev/null || echo "❌ Gunicorn não encontrado"
    
    # Reinstalar dependências críticas
    echo "📦 Reinstalando dependências críticas..."
    pip install --upgrade flask gunicorn sqlalchemy psycopg2-binary
    
else
    echo "❌ Virtual environment não encontrado, criando..."
    python3 -m venv venv
    source venv/bin/activate
    pip install --upgrade pip
    pip install flask gunicorn sqlalchemy psycopg2-binary pandas openpyxl
fi

echo ""
echo "🧪 Testando importação do módulo..."
python -c "
try:
    import web_interface
    print('✅ web_interface.py importado com sucesso')
except Exception as e:
    print(f'❌ Erro ao importar web_interface: {e}')
"

echo ""
echo "📝 Verificando arquivo de configuração Gunicorn..."
if [ ! -f "/opt/privacy/gunicorn.conf.py" ]; then
    echo "❌ gunicorn.conf.py não encontrado, criando..."
    cat > /opt/privacy/gunicorn.conf.py << 'EOF'
bind = "0.0.0.0:5000"
workers = 2
worker_class = "sync"
timeout = 120
keepalive = 2
max_requests = 1000
max_requests_jitter = 100
user = "privacy"
group = "privacy"
tmp_upload_dir = None
worker_tmp_dir = "/dev/shm"
worker_connections = 1000
EOF
    echo "✅ gunicorn.conf.py criado"
fi

echo ""
echo "🔐 Verificando permissões..."
chown -R privacy:privacy /opt/privacy/
chmod 755 /opt/privacy/
chmod 644 /opt/privacy/*.py
chmod 600 /opt/privacy/.env 2>/dev/null || echo "Arquivo .env não encontrado"

echo ""
echo "⚙️ Verificando arquivo .env..."
if [ ! -f "/opt/privacy/.env" ]; then
    echo "❌ .env não encontrado, criando..."
    cat > /opt/privacy/.env << 'EOF'
DATABASE_URL=postgresql://privacy:privacy123@localhost/privacy
OPENAI_API_KEY=your_openai_key_here
FLASK_ENV=production
FLASK_DEBUG=False
PYTHONPATH=/opt/privacy
EOF
    chmod 600 /opt/privacy/.env
    chown privacy:privacy /opt/privacy/.env
    echo "✅ .env criado"
fi

echo ""
echo "🗄️ Verificando PostgreSQL..."
sudo -u postgres psql -c "\l" | grep privacy || {
    echo "❌ Database privacy não encontrada, criando..."
    sudo -u postgres createdb privacy
    sudo -u postgres psql -c "CREATE USER privacy WITH PASSWORD 'privacy123';" 2>/dev/null || echo "User já existe"
    sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE privacy TO privacy;"
    echo "✅ Database criada"
}

echo ""
echo "🔧 Atualizando serviço systemd..."
cat > /etc/systemd/system/privacy.service << 'EOF'
[Unit]
Description=n.crisisops LGPD Compliance System
After=network.target postgresql.service

[Service]
Type=exec
User=privacy
Group=privacy
WorkingDirectory=/opt/privacy
Environment=PATH=/opt/privacy/venv/bin:/usr/bin:/bin
Environment=PYTHONPATH=/opt/privacy
EnvironmentFile=/opt/privacy/.env
ExecStart=/opt/privacy/venv/bin/gunicorn --config /opt/privacy/gunicorn.conf.py web_interface:app
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal
TimeoutStartSec=60

[Install]
WantedBy=multi-user.target
EOF

echo ""
echo "🔄 Reiniciando serviço..."
systemctl daemon-reload
systemctl stop privacy 2>/dev/null
sleep 2
systemctl start privacy

echo ""
echo "📊 Status final..."
systemctl status privacy --no-pager -l

echo ""
echo "🧪 Teste manual..."
echo "Execute: curl http://localhost:5000"
echo "Logs: journalctl -f -u privacy"