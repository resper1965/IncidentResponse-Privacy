#!/bin/bash

# Script para limpar Git e aplicar correções no VPS
# Execute no diretório /opt/privacy

echo "🧹 Limpando status do Git..."

# Remover arquivos não rastreados (venv/)
echo "📂 Removendo pasta venv/"
rm -rf venv/

# Descartar mudanças nos scripts modificados
echo "↩️ Descartando mudanças nos scripts..."
git restore scripts/atualizar-app.sh
git restore scripts/deploy-production.sh
git restore scripts/update-app-only.sh

# Verificar status após limpeza
echo "📋 Status após limpeza:"
git status

echo "✅ Git limpo e pronto!"