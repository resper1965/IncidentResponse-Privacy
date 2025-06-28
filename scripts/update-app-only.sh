#!/bin/bash

# Atualização rápida apenas do código da aplicação LGPD
# Para VPS que já tem sistema instalado

echo "🔄 Atualizando código da aplicação..."

cd /opt/privacy

# Fazer backup rápido
cp web_interface.py web_interface.py.backup.$(date +%s) 2>/dev/null || true

# Baixar arquivos atualizados específicos
echo "📥 Baixando web_interface.py atualizado..."
wget -O web_interface.py.new https://raw.githubusercontent.com/seu-repo/lgpd-system/main/web_interface.py

# Verificar se o download funcionou
if [ -f "web_interface.py.new" ]; then
    mv web_interface.py.new web_interface.py
    chown lgpd:lgpd web_interface.py
    echo "✅ web_interface.py atualizado"
else
    echo "❌ Erro no download"
    exit 1
fi

# Reiniciar apenas o serviço
echo "🔄 Reiniciando serviço..."
systemctl restart privacy

# Verificar se funcionou
sleep 2
if systemctl is-active --quiet privacy; then
    echo "✅ Aplicação atualizada e funcionando!"
    echo "🌐 Acesse: http://$(hostname -I | awk '{print $1}')"
else
    echo "❌ Erro no serviço. Restaurando backup..."
    mv web_interface.py.backup.* web_interface.py 2>/dev/null || true
    systemctl restart privacy
fi