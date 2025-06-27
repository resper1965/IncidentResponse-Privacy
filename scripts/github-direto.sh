#!/bin/bash

echo "🔗 Configuração para envio direto ao GitHub"

# Verificar se sistema limpo existe
if [ ! -d "/tmp/sistema-lgpd-limpo" ]; then
    echo "❌ Sistema limpo não encontrado. Execute primeiro:"
    echo "   ./scripts/solucao-final-git.sh"
    exit 1
fi

echo "✅ Sistema limpo encontrado (396KB)"

# Instruções para GitHub
cat << 'EOF'

📋 INSTRUÇÕES PARA GITHUB:

1. Criar repositório no GitHub:
   - Vá em github.com
   - Clique "New repository"
   - Nome: lgpd-sistema-clean
   - Deixe público ou privado
   - NÃO marque "Initialize with README"
   - Clique "Create repository"

2. Copiar URL do repositório:
   - Exemplo: https://github.com/SEU-USER/lgpd-sistema-clean.git

3. No Replit Shell, execute:

git clone SEU-REPO-URL
cd lgpd-sistema-clean
cp -r /tmp/sistema-lgpd-limpo/* .
git add .
git commit -m "Sistema LGPD completo - 396KB limpo"
git push

4. Pronto! Repositório GitHub criado com sistema completo.

EOF

echo "🔍 Verificando conteúdo do sistema limpo:"
ls -la /tmp/sistema-lgpd-limpo/

echo ""
echo "📊 Tamanho total: $(du -sh /tmp/sistema-lgpd-limpo/ | cut -f1)"
echo ""
echo "🚀 Execute os comandos acima após criar o repositório no GitHub"