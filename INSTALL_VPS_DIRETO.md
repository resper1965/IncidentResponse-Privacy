# Instalação Direta no VPS - Sistema LGPD

## Método 1: Download Direto

1. **Entre no seu VPS**:
```bash
ssh root@seu-ip-vps
```

2. **Baixe os arquivos do sistema**:
```bash
cd /opt
git clone https://github.com/seu-usuario/seu-repo.git privacy
cd privacy
```

3. **Execute o script de instalação**:
```bash
chmod +x scripts/install-vps-complete.sh
./scripts/install-vps-complete.sh
```

## Método 2: Instalação Manual Passo a Passo

Se não tiver o script, copie e cole este comando no seu VPS:

```bash
# 1. Atualize o sistema
apt update && apt upgrade -y

# 2. Instale dependências básicas
apt install -y python3 python3-pip python3-venv postgresql postgresql-contrib nginx git supervisor ufw certbot python3-certbot-nginx

# 3. Configure PostgreSQL
systemctl start postgresql
systemctl enable postgresql
sudo -u postgres psql -c "CREATE DATABASE privacy_db;"
sudo -u postgres psql -c "CREATE USER privacy_user WITH PASSWORD 'Lgpd2025#Privacy';"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE privacy_db TO privacy_user;"

# 4. Crie usuário do sistema
useradd -m -s /bin/bash lgpd
mkdir -p /opt/privacy
chown lgpd:lgpd /opt/privacy

# 5. Baixe o código
cd /opt/privacy
git clone https://github.com/seu-repo/lgpd-system.git .

# 6. Configure Python
sudo -u lgpd python3 -m venv venv
sudo -u lgpd ./venv/bin/pip install --upgrade pip

# 7. Instale dependências Python
sudo -u lgpd ./venv/bin/pip install flask==3.0.0 gunicorn==21.2.0 psycopg2-binary==2.9.9
sudo -u lgpd ./venv/bin/pip install pandas openpyxl pdfplumber PyMuPDF python-docx
sudo -u lgpd ./venv/bin/pip install langchain-core==0.2.43 langchain==0.2.17 langchain-openai
sudo -u lgpd ./venv/bin/pip install spacy python-dotenv plotly
sudo -u lgpd ./venv/bin/python -m spacy download pt_core_news_sm

# 8. Configure .env
cat > .env << EOF
DATABASE_URL=postgresql://privacy_user:Lgpd2025%23Privacy@localhost:5432/privacy_db
OPENAI_API_KEY=sua_chave_openai_aqui
FLASK_ENV=production
SECRET_KEY=$(openssl rand -hex 32)
EOF
chown lgpd:lgpd .env && chmod 600 .env

# 9. Configure serviço systemd
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

# 10. Configure Nginx
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
    }
}
EOF

ln -s /etc/nginx/sites-available/privacy /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default

# 11. Inicie serviços
systemctl daemon-reload
systemctl enable privacy
systemctl start privacy
systemctl restart nginx

# 12. Configure firewall
ufw enable
ufw allow ssh
ufw allow 'Nginx Full'
```

## Método 3: Script Único (Copie e Cole)

Cole este comando completo no terminal do seu VPS:

```bash
curl -sSL https://raw.githubusercontent.com/seu-repo/privacy-system/main/scripts/install-vps-complete.sh | bash
```

## Após a Instalação

1. **Configure seu domínio**:
```bash
nano /etc/nginx/sites-available/privacy
# Substitua server_name _ por server_name seudominio.com;
systemctl reload nginx
```

2. **Configure SSL**:
```bash
certbot --nginx -d seudominio.com
```

3. **Adicione chave OpenAI**:
```bash
nano /opt/privacy/.env
# Edite: OPENAI_API_KEY=sk-sua-chave-aqui
systemctl restart privacy
```

4. **Teste o sistema**:
```bash
curl http://localhost:5000
systemctl status privacy
```

## Verificação

Acesse: `http://seu-ip-vps` ou `https://seudominio.com`

Sistema instalado com:
- PostgreSQL configurado
- 10 empresas prioritárias
- IA com OpenAI integrada
- SSL automático
- Backup e logs