#!/bin/bash

# Script para corrigir completamente o serviço privacy no VPS
# Execute como root no diretório /opt/privacy

echo "Corrigindo serviço privacy..."

# Parar serviço atual
systemctl stop privacy

# Criar configuração correta do serviço
cat > /etc/systemd/system/privacy.service << 'EOF'
[Unit]
Description=n.crisisops Privacy LGPD System
After=network.target postgresql.service
Requires=postgresql.service

[Service]
Type=simple
User=root
WorkingDirectory=/opt/privacy
Environment=PATH=/usr/local/bin:/usr/bin:/bin
Environment=PYTHONPATH=/opt/privacy
ExecStart=/usr/bin/python3 /opt/privacy/web_interface.py
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

# Recarregar systemd
systemctl daemon-reload

# Aplicar correção no arquivo Python
sed -i 's/from file_scanner import encontrar_arquivos/from file_scanner import listar_arquivos_recursivos/g' /opt/privacy/web_interface.py
sed -i 's/arquivos = encontrar_arquivos(diretorio)/arquivos = listar_arquivos_recursivos(diretorio)/g' /opt/privacy/web_interface.py

# Verificar sintaxe Python
cd /opt/privacy
if python3 -m py_compile web_interface.py; then
    echo "Sintaxe Python válida"
else
    echo "Erro de sintaxe Python"
    exit 1
fi

# Habilitar e iniciar serviço
systemctl enable privacy
systemctl start privacy

# Verificar status
sleep 5
if systemctl is-active --quiet privacy; then
    echo "Serviço funcionando corretamente"
    echo "Acesse: https://monster.e-ness.com.br"
    systemctl status privacy --no-pager
else
    echo "Erro no serviço"
    journalctl -u privacy -n 10 --no-pager
fi