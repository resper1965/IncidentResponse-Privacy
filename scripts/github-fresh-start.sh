#!/bin/bash

echo "🔄 Criando repositório GitHub limpo..."

# Backup de arquivos essenciais
mkdir -p /tmp/backup-clean
cp *.py /tmp/backup-clean/ 2>/dev/null
cp -r templates /tmp/backup-clean/ 2>/dev/null
cp -r scripts /tmp/backup-clean/ 2>/dev/null
cp README.md /tmp/backup-clean/ 2>/dev/null
cp replit.md /tmp/backup-clean/ 2>/dev/null
cp .env.example /tmp/backup-clean/ 2>/dev/null

# Remover histórico Git atual
rm -rf .git

# Criar .gitignore definitivo
cat > .gitignore << 'EOF'
# Cache e arquivos grandes
.cache/
uv.lock
*.db
*.sqlite*
*.xlsx
*.log
__pycache__/
*.pyc
.pythonlibs/

# Data e outputs
data/
exports/
reports/

# Environment
.env

# IDE
.vscode/
.idea/
EOF

# Inicializar novo repositório
git init
git add .gitignore
git add *.py
git add templates/ 2>/dev/null || true
git add scripts/ 2>/dev/null || true
git add README.md 2>/dev/null || true
git add replit.md 2>/dev/null || true
git add .env.example 2>/dev/null || true

# Commit inicial limpo
git commit -m "🚀 Repositório limpo - sistema LGPD completo"

echo "✅ Repositório GitHub completamente limpo"
echo "📦 Tamanho atual:"
du -sh .git/

echo ""
echo "🚀 Para conectar ao GitHub:"
echo "   git remote add origin https://github.com/SEU-USER/SEU-REPO.git"
echo "   git push -u origin main"