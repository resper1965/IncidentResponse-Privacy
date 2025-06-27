#!/bin/bash

echo "🚀 Deploy para VPS - monster.e-ness.com.br"

# Verificar se está executando como root
if [ "$EUID" -ne 0 ]; then
    echo "❌ Execute como root: sudo ./deploy-vps-real.sh"
    exit 1
fi

# Criar usuário privacy se não existir
if ! id "privacy" &>/dev/null; then
    echo "👤 Criando usuário privacy..."
    useradd -r -s /bin/bash -d /opt/privacy privacy
fi

# Criar diretórios
echo "📁 Criando estrutura de diretórios..."
mkdir -p /opt/privacy/{templates,scripts,data}

# Fazer backup se já existir
if [ -d "/opt/privacy/backup" ]; then
    rm -rf /opt/privacy/backup
fi
mkdir -p /opt/privacy/backup

# Backup de arquivos existentes
if [ -f "/opt/privacy/web_interface.py" ]; then
    echo "💾 Fazendo backup dos arquivos existentes..."
    cp /opt/privacy/*.py /opt/privacy/backup/ 2>/dev/null
fi

# Atualizar sistema e instalar dependências
echo "📦 Instalando dependências do sistema..."
apt update -qq
apt install -y python3 python3-pip python3-venv nginx postgresql postgresql-contrib

# Instalar Python dependencies
echo "🐍 Instalando dependências Python..."
cd /opt/privacy
python3 -m venv venv
source venv/bin/activate

# Instalar pacotes Python essenciais
pip install --upgrade pip
pip install flask sqlalchemy psycopg2-binary pandas openpyxl
pip install pdfplumber python-docx pytesseract pillow spacy
pip install langchain langchain-openai openai gunicorn

# Baixar modelo spaCy português
python -m spacy download pt_core_news_sm

echo "✅ Dependências instaladas"

# Criar arquivo de requirements para referência
cat > /opt/privacy/requirements.txt << 'EOF'
flask>=2.3.0
sqlalchemy>=2.0.0
psycopg2-binary>=2.9.0
pandas>=2.0.0
openpyxl>=3.1.0
pdfplumber>=0.9.0
python-docx>=0.8.11
pytesseract>=0.3.10
pillow>=10.0.0
spacy>=3.6.0
langchain>=0.1.0
langchain-openai>=0.1.0
openai>=1.0.0
gunicorn>=21.0.0
asyncpg>=0.29.0
watchdog>=3.0.0
extract-msg>=0.47.0
beautifulsoup4>=4.12.0
striprtf>=0.0.26
python-pptx>=0.6.21
pymupdf>=1.23.0
lxml>=4.9.0
eml-parser>=1.17.0
pathlib2>=2.3.7
pyyaml>=6.0.1
langchain-core>=0.1.0
langchain-community>=0.0.1
langchain-text-splitters>=0.0.1
asyncio-extras>=1.3.2
EOF

echo "📋 Requirements criado"

# Criar serviço systemd
echo "🔧 Criando serviço systemd..."
cat > /etc/systemd/system/privacy.service << 'EOF'
[Unit]
Description=n.crisisops Privacy Module
After=network.target postgresql.service

[Service]
Type=exec
User=privacy
Group=privacy
WorkingDirectory=/opt/privacy
Environment=PATH=/opt/privacy/venv/bin
ExecStart=/opt/privacy/venv/bin/gunicorn --bind 0.0.0.0:5000 --workers 4 web_interface:app
Restart=always
RestartSec=3
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

# Configurar Nginx
echo "🌐 Configurando Nginx..."
cat > /etc/nginx/sites-available/privacy << 'EOF'
server {
    listen 80;
    server_name monster.e-ness.com.br;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
EOF

# Ativar site Nginx
ln -sf /etc/nginx/sites-available/privacy /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default

# Configurar PostgreSQL
echo "🗄️ Configurando PostgreSQL..."
sudo -u postgres createdb privacy 2>/dev/null || echo "Database já existe"
sudo -u postgres psql -c "CREATE USER privacy WITH PASSWORD 'privacy123';" 2>/dev/null || echo "User já existe"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE privacy TO privacy;" 2>/dev/null

# Criar arquivo .env
echo "⚙️ Criando configuração..."
cat > /opt/privacy/.env << 'EOF'
DATABASE_URL=postgresql://privacy:privacy123@localhost/privacy
OPENAI_API_KEY=your_openai_key_here
FLASK_ENV=production
FLASK_DEBUG=False
EOF

# Ajustar permissões
echo "🔐 Ajustando permissões..."
chown -R privacy:privacy /opt/privacy
chmod 755 /opt/privacy
chmod 600 /opt/privacy/.env

echo ""
echo "✅ Configuração base concluída!"
echo ""
echo "📋 Próximos passos:"
echo "1. Copie os arquivos Python do seu projeto para /opt/privacy/"
echo "2. Configure a OPENAI_API_KEY no arquivo /opt/privacy/.env"
echo "3. Execute: systemctl daemon-reload"
echo "4. Execute: systemctl enable privacy"
echo "5. Execute: systemctl start privacy"
echo "6. Execute: systemctl reload nginx"
echo ""
echo "🌐 Acesse: http://monster.e-ness.com.br"
echo ""
echo "📊 Verificar status: systemctl status privacy"
echo "📋 Ver logs: journalctl -f -u privacy"