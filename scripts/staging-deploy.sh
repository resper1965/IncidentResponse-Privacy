#!/bin/bash

# n.crisisops - LGPD Privacy Module - Staging Deployment
# Testa o deploy completo antes da produção

set -e

echo "🧪 n.crisisops - LGPD Privacy Module - Staging Deployment"
echo "=========================================================="

# Verificar se está rodando como root
if [ "$EUID" -ne 0 ]; then
    echo "❌ Execute como root: sudo $0"
    exit 1
fi

# Variáveis de staging
STAGING_DIR="/opt/privacy-staging"
STAGING_USER="privacy-staging"
STAGING_DB="privacy_staging"
STAGING_DB_USER="privacy_staging_user"
STAGING_DB_PASS="Staging2025#Test"
STAGING_PORT="5001"

echo "📋 Preparando ambiente de staging..."

# Criar usuário staging
if ! id "$STAGING_USER" &>/dev/null; then
    useradd -r -s /bin/bash -d $STAGING_DIR $STAGING_USER
    echo "✅ Usuário $STAGING_USER criado"
fi

# Criar diretórios
mkdir -p $STAGING_DIR/{uploads,backups,logs,data}
mkdir -p /var/log/privacy-staging

echo "🗄️ Configurando banco staging..."

# Configurar banco staging
sudo -u postgres psql << EOF
DO \$\$
BEGIN
    IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = '$STAGING_DB_USER') THEN
        CREATE USER $STAGING_DB_USER WITH PASSWORD '$STAGING_DB_PASS';
    END IF;
END
\$\$;

SELECT 'CREATE DATABASE $STAGING_DB OWNER $STAGING_DB_USER'
WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = '$STAGING_DB')\gexec

GRANT ALL PRIVILEGES ON DATABASE $STAGING_DB TO $STAGING_DB_USER;
EOF

echo "📁 Copiando código para staging..."

# Copiar código atual
cp -r /opt/privacy/* $STAGING_DIR/ || {
    echo "⚠️ Diretório de produção não encontrado, usando código atual"
    cp -r ./* $STAGING_DIR/
}

cd $STAGING_DIR

echo "🐍 Configurando ambiente Python staging..."

# Remover venv existente se houver
rm -rf venv

# Criar novo ambiente virtual
python3 -m venv venv
source venv/bin/activate

# Instalar dependências
pip install --upgrade pip
pip install -r production-requirements.txt

echo "🧪 Testando importações..."

# Testar importações críticas
python3 -c "
modules = ['flask', 'fitz', 'pdfplumber', 'docx', 'psycopg2']
for module in modules:
    try:
        __import__(module)
        print(f'✅ {module}')
    except ImportError as e:
        print(f'❌ {module}: {e}')
        exit(1)
"

echo "⚙️ Configurando ambiente staging..."

# Criar arquivo .env para staging
cat > .env << EOF
DATABASE_URL=postgresql://$STAGING_DB_USER:$STAGING_DB_PASS@localhost:5432/$STAGING_DB
FLASK_ENV=development
FLASK_DEBUG=True
SECRET_KEY=staging-secret-key
APP_PORT=$STAGING_PORT
APP_HOST=0.0.0.0
EOF

echo "🗄️ Inicializando banco staging..."

# Inicializar banco
python3 -c "
import os
os.environ['DATABASE_URL'] = 'postgresql://$STAGING_DB_USER:$STAGING_DB_PASS@localhost:5432/$STAGING_DB'

try:
    import database_postgresql as db_pg
    db_pg.initialize_database()
    print('✅ Banco PostgreSQL inicializado')
except Exception as e:
    print(f'⚠️ PostgreSQL falhou: {e}')
    import database
    database.inicializar_banco()
    print('✅ Fallback SQLite configurado')
"

echo "🚀 Configurando serviço staging..."

# Criar serviço staging
cat > /etc/systemd/system/privacy-staging.service << EOF
[Unit]
Description=n.crisisops LGPD Privacy Module - Staging
After=network.target

[Service]
Type=exec
User=$STAGING_USER
Group=$STAGING_USER
WorkingDirectory=$STAGING_DIR
Environment=PATH=$STAGING_DIR/venv/bin
Environment=PYTHONPATH=$STAGING_DIR
Environment=FLASK_ENV=development
EnvironmentFile=$STAGING_DIR/.env
ExecStart=$STAGING_DIR/venv/bin/python3 web_interface.py
Restart=always
RestartSec=5
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

echo "🔐 Configurando permissões..."

# Definir permissões
chown -R $STAGING_USER:$STAGING_USER $STAGING_DIR
chown -R $STAGING_USER:$STAGING_USER /var/log/privacy-staging
chmod 600 $STAGING_DIR/.env

echo "▶️ Iniciando serviço staging..."

# Iniciar serviço
systemctl daemon-reload
systemctl enable privacy-staging
systemctl restart privacy-staging

echo "⏳ Aguardando inicialização..."
sleep 10

echo "🧪 Testando staging..."

# Testar se responde
if curl -f -s http://localhost:$STAGING_PORT > /dev/null; then
    echo "✅ Staging respondendo na porta $STAGING_PORT"
    
    # Testar endpoint básico
    if curl -s http://localhost:$STAGING_PORT/api/system-status | grep -q "status"; then
        echo "✅ API respondendo corretamente"
    else
        echo "⚠️ API pode estar com problemas"
    fi
    
else
    echo "❌ Staging não responde"
    echo "📋 Logs do serviço:"
    journalctl -u privacy-staging --no-pager -l -n 10
    exit 1
fi

echo "📊 Status dos serviços:"
systemctl status privacy-staging --no-pager -l

echo ""
echo "=========================================================="
echo "✅ STAGING DEPLOYMENT CONCLUÍDO!"
echo "=========================================================="
echo "🌐 URL Staging: http://localhost:$STAGING_PORT"
echo "📁 Diretório: $STAGING_DIR"
echo "👤 Usuário: $STAGING_USER"
echo "🗄️ Banco: postgresql://$STAGING_DB_USER@localhost:5432/$STAGING_DB"
echo ""
echo "📋 Comandos staging:"
echo "   sudo systemctl status privacy-staging"
echo "   sudo systemctl restart privacy-staging"
echo "   sudo journalctl -u privacy-staging -f"
echo ""
echo "🚀 Execute o deploy de produção:"
echo "   sudo ./scripts/deploy-production.sh"
echo "=========================================================="