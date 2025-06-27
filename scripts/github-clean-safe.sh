#!/bin/bash

# Script seguro para limpar GitHub - evita arquivos do Replit

echo "🔧 Limpeza segura do GitHub..."

# Remover apenas arquivos específicos problemáticos
echo "🗑️ Removendo arquivos grandes específicos..."

# Remover databases locais
rm -f *.db 2>/dev/null
rm -f *.sqlite* 2>/dev/null
rm -f lgpd_data.db 2>/dev/null

# Remover exports Excel grandes
rm -f *.xlsx 2>/dev/null
rm -f matriz_dados_*.xlsx 2>/dev/null

# Remover logs
rm -f *.log 2>/dev/null

# Limpar cache Python apenas
find . -name "*.pyc" -delete 2>/dev/null
find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null

# Atualizar .gitignore com exclusões específicas
echo "📝 Atualizando .gitignore para evitar problemas futuros..."
cat >> .gitignore << 'EOF'

# Evitar arquivos grandes específicos
*.db
*.sqlite*
lgpd_data.db
matriz_dados_*.xlsx
*.log

# Cache Python
__pycache__/
*.pyc
*.pyo

# Data processing
data/
exports/
reports/

# Replit específico
.replit
replit.nix
.config/
EOF

echo "✅ Limpeza segura concluída"

# Mostrar arquivos maiores para verificação
echo "📊 Arquivos maiores restantes:"
find . -type f -size +1M -not -path "./.cache/*" -not -path "./.config/*" 2>/dev/null | head -10

echo ""
echo "🚀 Agora você pode fazer:"
echo "   git add ."
echo "   git commit -m 'Limpeza de arquivos grandes'"
echo "   git push"