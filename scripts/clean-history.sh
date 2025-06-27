#!/bin/bash

echo "Removendo histórico Git e criando repositório limpo..."

# Backup essencial
mkdir -p /tmp/lgpd-backup
cp *.py /tmp/lgpd-backup/ 2>/dev/null
cp -r templates /tmp/lgpd-backup/ 2>/dev/null  
cp -r scripts /tmp/lgpd-backup/ 2>/dev/null
cp README.md /tmp/lgpd-backup/ 2>/dev/null
cp replit.md /tmp/lgpd-backup/ 2>/dev/null
cp .env.example /tmp/lgpd-backup/ 2>/dev/null
cp .replit /tmp/lgpd-backup/ 2>/dev/null

# Remover cache e temporários
rm -f *.db *.sqlite* *.xlsx *.log 2>/dev/null

# Criar gitignore final
cat > .gitignore << 'EOF'
# Arquivos grandes e cache
.cache/
.pythonlibs/
uv.lock
*.db
*.sqlite*
*.xlsx
*.log
__pycache__/
*.pyc

# Data LGPD
data/
exports/
reports/

# Config
.env
.vscode/
.idea/
EOF

echo "Histórico limpo. Agora você deve:"
echo "1. No painel Git do Replit, fazer 'Initialize Repository'"
echo "2. Adicionar arquivos essenciais"
echo "3. Fazer primeiro commit limpo"
echo ""
echo "Backup salvo em: /tmp/lgpd-backup"