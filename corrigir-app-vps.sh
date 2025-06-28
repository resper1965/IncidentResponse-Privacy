#!/bin/bash

# Script completo para corrigir aplicação no VPS
# Execute no diretório /opt/privacy como root

echo "🔧 Corrigindo aplicação LGPD no VPS..."

# 1. Limpar Git primeiro
echo "📂 Limpando Git..."
rm -rf venv/
git restore scripts/atualizar-app.sh scripts/deploy-production.sh scripts/update-app-only.sh

# 2. Parar serviço
echo "⏹️ Parando serviço..."
systemctl stop privacy

# 3. Fazer backup do arquivo atual
echo "💾 Fazendo backup..."
cp web_interface.py web_interface.py.backup

# 4. Aplicar correção crítica
echo "🔧 Aplicando correção de importação..."
sed -i 's/from file_scanner import encontrar_arquivos/from file_scanner import listar_arquivos_recursivos/g' web_interface.py
sed -i 's/arquivos = encontrar_arquivos(diretorio)/arquivos = listar_arquivos_recursivos(diretorio)/g' web_interface.py

# 5. Verificar se a correção foi aplicada
echo "✅ Verificando correção..."
if grep -q "listar_arquivos_recursivos" web_interface.py; then
    echo "✅ Correção aplicada com sucesso"
else
    echo "❌ Erro: correção não foi aplicada"
    echo "Restaurando backup..."
    mv web_interface.py.backup web_interface.py
    exit 1
fi

# 6. Testar sintaxe Python
echo "🔍 Testando sintaxe..."
if python3 -m py_compile web_interface.py; then
    echo "✅ Sintaxe válida"
else
    echo "❌ Erro de sintaxe"
    echo "Restaurando backup..."
    mv web_interface.py.backup web_interface.py
    exit 1
fi

# 7. Iniciar serviço
echo "▶️ Iniciando serviço..."
systemctl start privacy

# 8. Aguardar inicialização
echo "⏳ Aguardando inicialização..."
sleep 5

# 9. Verificar status
if systemctl is-active --quiet privacy; then
    echo "✅ Serviço iniciado com sucesso!"
    echo "🌐 Sistema disponível em: https://monster.e-ness.com.br"
    
    # Mostrar últimas linhas do log
    echo "📋 Últimas linhas do log:"
    journalctl -u privacy -n 10 --no-pager
    
    echo ""
    echo "🎉 Aplicação corrigida e funcionando!"
else
    echo "❌ Erro no serviço"
    echo "📋 Status do serviço:"
    systemctl status privacy --no-pager
    echo ""
    echo "📋 Últimas linhas do log de erro:"
    journalctl -u privacy -n 20 --no-pager
    
    # Restaurar backup
    echo "🔄 Restaurando backup..."
    mv web_interface.py.backup web_interface.py
    systemctl start privacy
fi