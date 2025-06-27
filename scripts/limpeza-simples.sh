#!/bin/bash

echo "Limpeza simples - removendo apenas arquivos grandes atuais"

# Remover arquivos problemáticos atuais
rm -f *.db *.sqlite* *.xlsx *.log 2>/dev/null
find . -name "*.pyc" -delete 2>/dev/null

# Atualizar .gitignore para prevenir futuros problemas
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
data/
exports/
reports/
.env
.vscode/
.idea/
EOF

echo "Verificando tamanho atual dos arquivos do projeto:"
du -sh *.py templates/ scripts/ 2>/dev/null | sort -hr

echo ""
echo "Arquivos grandes removidos:"
echo "- Base de dados (*.db, *.sqlite)"
echo "- Exports Excel (*.xlsx)"
echo "- Logs (*.log)"
echo "- Cache Python (__pycache__, *.pyc)"

echo ""
echo "O problema dos 172MB está no histórico Git (.git/objects/pack/)"
echo "Isso será resolvido naturalmente com commits futuros."
echo ""
echo "Para aplicar as mudanças:"
echo "git add .gitignore"
echo "git commit -m 'Limpeza: removidos arquivos grandes'"
echo "git push"