#!/bin/bash

# =============================================================================
# Script de Correção de Dependências - n.crisisops
# =============================================================================

echo "🔧 Instalando dependências ausentes na VPS..."

# Instalar PyMuPDF (fitz) e outras dependências ausentes
sudo -u privacy /opt/privacy/venv/bin/pip install \
    pymupdf==1.23.8 \
    python-pptx==0.6.23 \
    beautifulsoup4==4.12.2 \
    lxml==4.9.3 \
    striprtf==0.0.26 \
    eml-parser==1.17.7 \
    langchain-community==0.0.6 \
    langchain-text-splitters==0.0.1

echo "✅ Dependências instaladas"

# Reiniciar serviço
echo "🔄 Reiniciando serviço..."
systemctl restart privacy

# Verificar status
sleep 5
if systemctl is-active --quiet privacy; then
    echo "✅ Serviço funcionando"
    curl -s http://localhost:5000/health && echo "✅ Health check OK"
else
    echo "❌ Serviço com problema"
    journalctl -u privacy --no-pager -n 5
fi