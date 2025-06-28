#!/bin/bash

# Script para atualizar código do GitHub no VPS
# Execute no diretório /opt/privacy como root
# GitHub: https://github.com/resper1965/IncidentResponse-Privacy.git

echo "🔄 Atualizando código do GitHub..."

# 1. Limpar status do Git
echo "📂 Limpando Git..."
rm -rf venv/
git restore scripts/atualizar-app.sh scripts/deploy-production.sh scripts/update-app-only.sh 2>/dev/null || true

# 2. Parar serviço
echo "⏹️ Parando serviço..."
systemctl stop privacy

# 3. Fazer backup
echo "💾 Fazendo backup..."
cp web_interface.py web_interface.py.backup-$(date +%Y%m%d_%H%M%S)

# 4. Atualizar do GitHub
echo "📥 Baixando código atualizado..."
if wget -O web_interface.py.new https://raw.githubusercontent.com/resper1965/IncidentResponse-Privacy/main/web_interface.py; then
    echo "✅ Download do web_interface.py concluído"
    mv web_interface.py.new web_interface.py
else
    echo "❌ Erro no download, aplicando correção local..."
    # Aplicar correção local se download falhar
    sed -i 's/from file_scanner import encontrar_arquivos/from file_scanner import listar_arquivos_recursivos/g' web_interface.py
    sed -i 's/arquivos = encontrar_arquivos(diretorio)/arquivos = listar_arquivos_recursivos(diretorio)/g' web_interface.py
fi

# 5. Verificar sintaxe
echo "🔍 Verificando sintaxe..."
if python3 -m py_compile web_interface.py; then
    echo "✅ Sintaxe válida"
else
    echo "❌ Erro de sintaxe, restaurando backup..."
    mv web_interface.py.backup-$(date +%Y%m%d_%H%M%S) web_interface.py
    exit 1
fi

# 6. Iniciar serviço
echo "▶️ Iniciando serviço..."
systemctl start privacy
sleep 5

# 7. Verificar status
if systemctl is-active --quiet privacy; then
    echo "✅ Serviço funcionando!"
    echo "🌐 Acesse: https://monster.e-ness.com.br"
    echo ""
    echo "📋 Log do sistema:"
    journalctl -u privacy -n 5 --no-pager
else
    echo "❌ Erro no serviço"
    systemctl status privacy --no-pager
fi