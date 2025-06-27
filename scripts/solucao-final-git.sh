#!/bin/bash

echo "🔄 Solução final para GitHub - criando repositório completamente limpo"

# Criar diretório de backup
mkdir -p /tmp/sistema-lgpd-limpo

# Copiar apenas arquivos essenciais
echo "📋 Copiando arquivos essenciais..."
cp *.py /tmp/sistema-lgpd-limpo/ 2>/dev/null
cp -r templates /tmp/sistema-lgpd-limpo/ 2>/dev/null
cp -r scripts /tmp/sistema-lgpd-limpo/ 2>/dev/null
cp README.md /tmp/sistema-lgpd-limpo/ 2>/dev/null
cp replit.md /tmp/sistema-lgpd-limpo/ 2>/dev/null
cp .env.example /tmp/sistema-lgpd-limpo/ 2>/dev/null
cp .replit /tmp/sistema-lgpd-limpo/ 2>/dev/null

# Criar .gitignore otimizado
cat > /tmp/sistema-lgpd-limpo/.gitignore << 'EOF'
# Sistema LGPD - Exclusões
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

# Mostrar tamanho final
echo "📊 Tamanho do sistema limpo:"
du -sh /tmp/sistema-lgpd-limpo/

echo ""
echo "✅ Sistema LGPD limpo criado em: /tmp/sistema-lgpd-limpo"
echo ""
echo "🚀 Próximos passos:"
echo "1. Criar novo repositório no GitHub"
echo "2. Fazer download da pasta /tmp/sistema-lgpd-limpo"
echo "3. Upload no novo repositório"
echo ""
echo "📁 Arquivos incluídos:"
ls -la /tmp/sistema-lgpd-limpo/