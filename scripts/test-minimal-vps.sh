#!/bin/bash

echo "🔍 Diagnóstico completo da VPS"

cd /opt/privacy
source venv/bin/activate

echo "1. Testando Python básico..."
python3 --version

echo "2. Testando cada módulo individualmente..."

echo "📦 Testando fitz (PyMuPDF)..."
python3 -c "
try:
    import fitz
    print('✅ fitz OK')
except Exception as e:
    print(f'❌ fitz: {e}')
    exit(1)
"

echo "📦 Testando file_reader..."
python3 -c "
try:
    from file_reader import extrair_texto
    print('✅ file_reader OK')
except Exception as e:
    print(f'❌ file_reader: {e}')
    exit(1)
"

echo "📦 Testando main..."
python3 -c "
try:
    from main import processar_arquivos
    print('✅ main OK')
except Exception as e:
    print(f'❌ main: {e}')
    exit(1)
"

echo "📦 Testando web_interface..."
python3 -c "
try:
    import web_interface
    print('✅ web_interface OK')
except Exception as e:
    print(f'❌ web_interface: {e}')
    exit(1)
"

echo "🔧 Se todos os testes passaram, criando serviço simplificado..."

# Criar serviço com log detalhado
cat > /etc/systemd/system/privacy-test.service << 'EOF'
[Unit]
Description=n.crisisops Privacy Test
After=network.target

[Service]
Type=simple
User=privacy
Group=privacy
WorkingDirectory=/opt/privacy
Environment=PATH=/opt/privacy/venv/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
Environment=PYTHONPATH=/opt/privacy
Environment=PYTHONUNBUFFERED=1
ExecStart=/opt/privacy/venv/bin/python3 -u web_interface.py
StandardOutput=journal
StandardError=journal
Restart=no
SyslogIdentifier=privacy-test

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl stop privacy
systemctl start privacy-test

echo "📊 Aguardando inicialização..."
sleep 5

echo "📋 Logs detalhados:"
journalctl -u privacy-test --no-pager -l -n 20

echo "📊 Status:"
systemctl status privacy-test --no-pager -l