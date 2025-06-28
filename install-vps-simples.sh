#!/bin/bash

# Script de instalação rápida do Sistema LGPD para VPS
# Execute como root: bash install-vps-simples.sh

set -e

echo "🚀 Instalando Sistema LGPD n.crisisops"
echo "======================================"

# Atualizar sistema
apt update -y
apt install -y python3 python3-pip python3-venv postgresql postgresql-contrib nginx git certbot python3-certbot-nginx

# Configurar PostgreSQL
systemctl start postgresql
systemctl enable postgresql
sudo -u postgres psql -c "CREATE DATABASE privacy_db;"
sudo -u postgres psql -c "CREATE USER privacy_user WITH PASSWORD 'Lgpd2025#Privacy';"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE privacy_db TO privacy_user;"

# Criar usuário e diretório
useradd -m -s /bin/bash lgpd || true
mkdir -p /opt/privacy
chown lgpd:lgpd /opt/privacy
cd /opt/privacy

# Baixar código (substitua pela URL do seu repositório)
git clone https://github.com/seu-usuario/lgpd-system.git . || echo "Configure o repositório correto"

# Configurar Python
sudo -u lgpd python3 -m venv venv
sudo -u lgpd ./venv/bin/pip install --upgrade pip

# Instalar dependências
sudo -u lgpd ./venv/bin/pip install flask==3.0.0 gunicorn==21.2.0
sudo -u lgpd ./venv/bin/pip install psycopg2-binary==2.9.9 asyncpg==0.29.0
sudo -u lgpd ./venv/bin/pip install pandas==2.1.4 openpyxl==3.1.2
sudo -u lgpd ./venv/bin/pip install pdfplumber==0.10.3 PyMuPDF==1.23.22
sudo -u lgpd ./venv/bin/pip install python-docx==1.1.0 pillow==10.1.0
sudo -u lgpd ./venv/bin/pip install langchain-core==0.2.43 langchain==0.2.17
sudo -u lgpd ./venv/bin/pip install langchain-openai==0.1.25 openai==1.45.0
sudo -u lgpd ./venv/bin/pip install spacy==3.7.2 python-dotenv==1.0.0

# Baixar modelo spaCy
sudo -u lgpd ./venv/bin/python -m spacy download pt_core_news_sm

# Configurar .env
cat > .env << EOF
DATABASE_URL=postgresql://privacy_user:Lgpd2025%23Privacy@localhost:5432/privacy_db
OPENAI_API_KEY=sua_chave_openai_aqui
FLASK_ENV=production
SECRET_KEY=$(openssl rand -hex 32)
EOF
chown lgpd:lgpd .env
chmod 600 .env

# Configurar serviço systemd
cat > /etc/systemd/system/privacy.service << 'EOF'
[Unit]
Description=LGPD Privacy System
After=network.target postgresql.service

[Service]
Type=notify
User=lgpd
Group=lgpd
WorkingDirectory=/opt/privacy
Environment=PATH=/opt/privacy/venv/bin
ExecStart=/opt/privacy/venv/bin/gunicorn --bind 127.0.0.1:5000 web_interface:app
Restart=always

[Install]
WantedBy=multi-user.target
EOF

# Configurar Nginx
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
        client_max_body_size 100M;
    }
}
EOF

ln -s /etc/nginx/sites-available/privacy /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default

# Inicializar banco
cd /opt/privacy
sudo -u lgpd ./venv/bin/python -c "
from database_postgresql import inicializar_database_postgresql
from database import carregar_empresas_padrao, carregar_prioridades_padrao
inicializar_database_postgresql()
carregar_empresas_padrao()
carregar_prioridades_padrao()
print('✅ Banco inicializado')
"

# Iniciar serviços
systemctl daemon-reload
systemctl enable privacy
systemctl start privacy
systemctl restart nginx

echo "✅ INSTALAÇÃO CONCLUÍDA!"
echo "========================"
echo "Sistema rodando em: http://$(hostname -I | awk '{print $1}')"
echo ""
echo "Próximos passos:"
echo "1. Configure sua chave OpenAI em /opt/privacy/.env"
echo "2. Configure SSL: certbot --nginx -d seudominio.com"
echo "3. Reinicie: systemctl restart privacy"