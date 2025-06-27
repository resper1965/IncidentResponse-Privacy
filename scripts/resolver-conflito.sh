#!/bin/bash

echo "Resolvendo conflito Git - removendo arquivos problemáticos"

# Comandos para executar no shell manual:
cat << 'EOF'
# 1. Remover lock se existir
rm -f .git/index.lock

# 2. Resetar o merge em conflito
git merge --abort

# 3. Remover arquivos problemáticos do tracking
git rm --cached attached_assets/*.xlsx 2>/dev/null
git rm --cached attached_assets/*.txt 2>/dev/null
git rm --cached attached_assets/*.png 2>/dev/null
git rm --cached lgpd_data.db 2>/dev/null
git rm --cached requirements_deploy.txt 2>/dev/null

# 4. Remover arquivos fisicamente (opcional)
rm -f attached_assets/*.xlsx
rm -f attached_assets/*.txt
rm -f attached_assets/*.png
rm -f lgpd_data.db
rm -f requirements_deploy.txt

# 5. Adicionar apenas arquivos essenciais
git add .gitignore
git add *.py
git add templates/
git add scripts/
git add README.md
git add replit.md

# 6. Commit limpo
git commit -m 'Limpeza: removidos arquivos grandes e conflitos'

# 7. Push
git push

EOF

echo ""
echo "Execute os comandos acima no Shell para resolver o conflito."
echo "Isso irá remover os arquivos grandes e fazer commit apenas dos essenciais."