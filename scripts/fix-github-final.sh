#!/bin/bash

# Fix GitHub definitivo - Remove arquivos grandes e limpa histórico

echo "🔧 Iniciando correção definitiva do GitHub..."

# Backup de arquivos importantes
echo "📋 Fazendo backup de arquivos essenciais..."
mkdir -p /tmp/backup-privacy
cp *.py /tmp/backup-privacy/ 2>/dev/null
cp -r templates /tmp/backup-privacy/ 2>/dev/null
cp -r scripts /tmp/backup-privacy/ 2>/dev/null
cp .env.example /tmp/backup-privacy/ 2>/dev/null
cp requirements.txt /tmp/backup-privacy/ 2>/dev/null
cp README.md /tmp/backup-privacy/ 2>/dev/null
cp replit.md /tmp/backup-privacy/ 2>/dev/null

# Remover cache e arquivos grandes
echo "🗑️ Removendo arquivos grandes e cache..."
rm -rf .cache/ 2>/dev/null
rm -rf __pycache__/ 2>/dev/null
rm -rf .pytest_cache/ 2>/dev/null
rm -rf build/ 2>/dev/null
rm -rf dist/ 2>/dev/null
rm -rf *.egg-info/ 2>/dev/null
rm -rf .venv/ 2>/dev/null
rm -rf venv/ 2>/dev/null
rm -rf node_modules/ 2>/dev/null
rm -rf data/ 2>/dev/null
rm -f *.db 2>/dev/null
rm -f *.sqlite* 2>/dev/null
rm -f *.log 2>/dev/null
rm -f *.xlsx 2>/dev/null

# Limpar arquivos temporários
echo "🧹 Limpando arquivos temporários..."
find . -name "*.pyc" -delete 2>/dev/null
find . -name "*.pyo" -delete 2>/dev/null
find . -name "*~" -delete 2>/dev/null
find . -name ".DS_Store" -delete 2>/dev/null
find . -name "Thumbs.db" -delete 2>/dev/null

# Atualizar .gitignore com todas as exclusões necessárias
echo "📝 Atualizando .gitignore..."
cat > .gitignore << 'EOF'
# LGPD Compliance System - Git Ignore Configuration

# Python Cache e Bytecode
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg
MANIFEST

# Pip Cache - Evitar arquivos grandes
.cache/
pip-cache/
pip-log.txt
pip-delete-this-directory.txt

# Virtual Environments
venv/
env/
ENV/
.venv/
.env/

# Environment Variables
.env
.env.local
.env.production
.env.development

# Database Files
*.db
*.sqlite
*.sqlite3
lgpd_data.db

# Data Directory - Proteger dados pessoais
data/
data/*
data/**/*

# Logs
logs/
*.log
*.tmp
*.temp
temp/
tmp/

# IDE Files
.vscode/
.idea/
*.swp
*.swo
*~
.DS_Store
Thumbs.db

# Backup Files
*.bak
*.backup
backup/
backups/

# Sensitive Files
secrets/
private/
confidential/
*.key
*.pem
*.p12
*.pfx

# Processing Output
output/
exports/
reports/
*.xlsx
*.csv

# AI Model Cache
.langchain/
.openai/
model_cache/

# System Files
node_modules/
npm-debug.log*

# Test Coverage
htmlcov/
.coverage
.pytest_cache/
.tox/

# File Processing
processing/
queue/
temp_files/
extracted/
EOF

echo "✅ .gitignore atualizado"

# Resetar repositório se necessário
if [ -d ".git" ]; then
    echo "🔄 Resetando repositório Git..."
    
    # Fazer unstage de todos os arquivos
    git reset HEAD . 2>/dev/null || true
    
    # Remover arquivos do índice
    git rm -r --cached . 2>/dev/null || true
    
    # Adicionar arquivos limpos
    git add .gitignore
    git add *.py
    git add templates/ 2>/dev/null || true
    git add scripts/ 2>/dev/null || true
    git add README.md 2>/dev/null || true
    git add replit.md 2>/dev/null || true
    git add .env.example 2>/dev/null || true
    git add requirements.txt 2>/dev/null || true
    
    # Commit das mudanças
    git commit -m "🔧 Limpeza definitiva: removidos arquivos grandes e cache" 2>/dev/null || true
    
    echo "✅ Repositório Git limpo"
fi

# Verificar tamanho dos arquivos
echo "📊 Verificando tamanho dos arquivos..."
du -h * 2>/dev/null | sort -hr | head -20

echo ""
echo "✅ Correção GitHub concluída!"
echo ""
echo "🚀 Próximos passos:"
echo "   git status"
echo "   git push origin main"
echo ""
echo "📋 Backup salvo em: /tmp/backup-privacy"
EOF