#!/bin/bash

# n.crisisops - LGPD Privacy Module - Deploy Rápido
# Script para atualizações rápidas do sistema

set -e  # Exit on any error

echo "🚀 n.crisisops - LGPD Privacy Module - Deploy Rápido"
echo "================================================================="

# Variáveis de configuração
INSTALL_DIR="/opt/privacy"
SERVICE_USER="privacy"

echo "📋 Verificando requisitos..."

# Verificar se está rodando como root
if [ "$EUID" -ne 0 ]; then
    echo "❌ Execute como root: sudo $0"
    exit 1
fi

# Verificar se o diretório existe
if [ ! -d "$INSTALL_DIR" ]; then
    echo "❌ Diretório $INSTALL_DIR não existe. Execute o deploy completo primeiro."
    exit 1
fi

echo "📦 Fazendo backup do sistema atual..."
BACKUP_DIR="${INSTALL_DIR}_backup_$(date +%Y%m%d_%H%M%S)"
cp -r $INSTALL_DIR $BACKUP_DIR
echo "✅ Backup criado em: $BACKUP_DIR"

echo "🔄 Atualizando código..."

# Parar o serviço
systemctl stop privacy

# Fazer backup dos arquivos importantes
cp $INSTALL_DIR/.env $BACKUP_DIR/
cp $INSTALL_DIR/gunicorn.conf.py $BACKUP_DIR/

# Limpar diretório (mantendo venv e uploads)
cd $INSTALL_DIR
rm -rf *.py *.txt *.md *.json *.html *.sh templates static docs scripts
rm -rf .git .github .streamlit .cache .replit

echo "📁 Copiando novos arquivos..."

# Copiar arquivos do projeto atual
cp -r /caminho/para/seu/projeto/* $INSTALL_DIR/
cp -r /caminho/para/seu/projeto/.* $INSTALL_DIR/ 2>/dev/null || true

# Restaurar arquivos importantes
cp $BACKUP_DIR/.env $INSTALL_DIR/
cp $BACKUP_DIR/gunicorn.conf.py $INSTALL_DIR/

echo "🐍 Atualizando ambiente Python..."

# Ativar ambiente virtual
source venv/bin/activate

# Atualizar dependências
pip install --upgrade pip
pip install -r requirements.txt

echo "🤖 Verificando modelo spaCy..."
python -m spacy download pt_core_news_sm

echo "🔐 Configurando permissões..."
chown -R $SERVICE_USER:$SERVICE_USER $INSTALL_DIR
chmod +x venv/bin/*
chmod 600 .env

echo "🚀 Reiniciando serviços..."

# Recarregar systemd
systemctl daemon-reload

# Reiniciar serviço
systemctl restart privacy

echo "⏳ Aguardando inicialização..."
sleep 10

echo "🧪 Testando aplicação..."

# Verificar se a aplicação responde
if curl -f -s http://localhost:5000 > /dev/null; then
    echo "✅ Aplicação respondendo corretamente"
else
    echo "❌ Aplicação não responde, verificando logs..."
    journalctl -u privacy --no-pager -l -n 20
    echo "⚠️ Verifique os logs e reinicie manualmente se necessário"
fi

echo ""
echo "================================================================="
echo "✅ DEPLOY RÁPIDO CONCLUÍDO!"
echo "================================================================="
echo "📁 Backup: $BACKUP_DIR"
echo "📁 Diretório: $INSTALL_DIR"
echo ""
echo "📋 Comandos úteis:"
echo "   sudo systemctl status privacy"
echo "   sudo systemctl restart privacy"
echo "   sudo journalctl -u privacy -f"
echo ""
echo "🔄 Para reverter: sudo systemctl stop privacy && sudo rm -rf $INSTALL_DIR && sudo mv $BACKUP_DIR $INSTALL_DIR && sudo systemctl start privacy"
echo "=================================================================" 