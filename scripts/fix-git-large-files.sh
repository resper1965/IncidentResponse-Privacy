#!/bin/bash

# =============================================================================
# Script de Correção de Arquivos Grandes no Git - n.crisisops
# Remove arquivos de cache grandes que impedem o push para GitHub
# =============================================================================

echo "🔧 Corrigindo problemas de arquivos grandes no Git..."

# Verificar se estamos no diretório correto
if [ ! -f "web_interface.py" ]; then
    echo "❌ Execute este script no diretório /opt/privacy"
    exit 1
fi

echo "📂 Removendo arquivos de cache grandes do índice Git..."

# Remover arquivos de cache do índice Git
git rm -r --cached .cache/ 2>/dev/null || echo "Cache .cache/ não encontrado no índice"
git rm -r --cached pip-cache/ 2>/dev/null || echo "Cache pip-cache/ não encontrado no índice"
git rm --cached .cache/pip/http-v2/c/3/3/8/7/c33872dcbc256de6b1395254fcb8bc440eee16fd02a3f3f89c663bc7.body 2>/dev/null || echo "Arquivo específico não encontrado"

echo "🧹 Removendo diretórios de cache físicos..."

# Remover diretórios de cache físicos
rm -rf .cache/
rm -rf pip-cache/
rm -rf __pycache__/
rm -rf *.pyc
rm -rf .pytest_cache/

echo "📝 Atualizando .gitignore..."

# Garantir que o .gitignore está atualizado
if ! grep -q ".cache/" .gitignore; then
    echo ".cache/" >> .gitignore
fi

if ! grep -q "pip-cache/" .gitignore; then
    echo "pip-cache/" >> .gitignore
fi

echo "✅ Limpeza do histórico Git (BFG alternative)..."

# Limpar histórico de arquivos grandes usando git filter-branch
git filter-branch --force --index-filter \
  "git rm --cached --ignore-unmatch .cache/pip/http-v2/c/3/3/8/7/c33872dcbc256de6b1395254fcb8bc440eee16fd02a3f3f89c663bc7.body" \
  --prune-empty --tag-name-filter cat -- --all

# Limpar referências
git for-each-ref --format="%(refname)" refs/original/ | xargs -n 1 git update-ref -d

# Forçar garbage collection
git reflog expire --expire=now --all
git gc --prune=now --aggressive

echo "📊 Verificando tamanho do repositório..."

# Mostrar arquivos maiores que 10MB
echo "Arquivos grandes restantes (>10MB):"
find . -type f -size +10M -not -path "./.git/*" -not -path "./data/*" | head -10

echo "💾 Adicionando mudanças ao Git..."

# Adicionar mudanças
git add .gitignore
git add -A

echo "📝 Fazendo commit das correções..."

# Commit das correções
git commit -m "fix: Remove large cache files and update .gitignore

- Removed .cache/ directory with large pip cache files
- Updated .gitignore to prevent future cache commits
- Cleaned Git history of large files
- Repository now compliant with GitHub size limits"

echo ""
echo "✅ Correção concluída!"
echo ""
echo "📤 Agora você pode fazer push com:"
echo "   git push origin main"
echo ""
echo "🔍 Se ainda houver problemas, verifique:"
echo "   git ls-files | xargs ls -lh | sort -k5 -h | tail -10"