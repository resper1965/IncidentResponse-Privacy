#!/bin/bash

# Script simples para corrigir problema de arquivos grandes no GitHub

echo "Removendo arquivos de cache do Git..."

# Remover do índice Git
git rm -r --cached .cache/ 2>/dev/null || true

# Remover fisicamente
rm -rf .cache/
rm -rf __pycache__/

# Adicionar e fazer commit
git add .
git commit -m "Remove large cache files"

echo "Pronto! Agora pode fazer: git push origin main"