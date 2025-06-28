#!/bin/bash

# Fix virtual environment path on VPS
echo "🔧 Corrigindo caminho do ambiente virtual..."

cd /opt/privacy

# Parar o serviço
systemctl stop privacy

# Verificar qual Python está sendo usado
echo "📍 Verificando ambiente atual..."
which python3
ls -la venv/bin/python3

# Reinstalar PyMuPDF no ambiente correto
echo "📦 Reinstalando PyMuPDF no ambiente correto..."
./venv/bin/pip install PyMuPDF==1.23.8

# Verificar se foi instalado corretamente
echo "🧪 Testando PyMuPDF..."
./venv/bin/python3 -c "
import sys
print(f'Python path: {sys.executable}')
try:
    import fitz
    print(f'✅ PyMuPDF version: {fitz.__version__}')
except Exception as e:
    print(f'❌ PyMuPDF error: {e}')
"

# Testar importação do file_reader
echo "🧪 Testando file_reader..."
./venv/bin/python3 -c "
try:
    from file_reader import extrair_texto
    print('✅ file_reader importado com sucesso')
except Exception as e:
    print(f'❌ file_reader error: {e}')
"

# Atualizar o arquivo de serviço com caminho correto
echo "⚙️ Atualizando configuração do serviço..."
cat > /etc/systemd/system/privacy.service << 'EOF'
[Unit]
Description=n.crisisops Privacy LGPD System
After=network.target postgresql.service
Requires=postgresql.service

[Service]
Type=notify
User=privacy
Group=privacy
WorkingDirectory=/opt/privacy
Environment="PATH=/opt/privacy/venv/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"
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

# Recarregar e reiniciar
systemctl daemon-reload
systemctl start privacy

# Aguardar um pouco
sleep 5

# Verificar status
echo "🔍 Verificando status do serviço..."
systemctl status privacy --no-pager

echo "🧪 Testando aplicação..."
curl -I http://localhost:5000

echo "✅ Correção do ambiente virtual concluída!"