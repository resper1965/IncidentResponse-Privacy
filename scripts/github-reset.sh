#!/bin/bash

echo "🔧 Resetando GitHub - remoção definitiva de arquivos grandes"

# Remove arquivos grandes específicos
rm -f lgpd_data.db
rm -f matriz_dados_*.xlsx
rm -f *.log

# Atualizar .gitignore final
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

echo "✅ GitHub limpo - arquivos grandes removidos"
echo "📋 .gitignore atualizado para evitar problemas futuros"

# Verificar tamanho final
echo "📊 Arquivos maiores restantes:"
find . -type f -size +1M -not -path "./.cache/*" 2>/dev/null | head -5

echo ""
echo "🚀 Pronto para commit:"
echo "   git add ."
echo "   git commit -m 'Limpeza final - removidos arquivos grandes'"
echo "   git push"