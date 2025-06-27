#!/bin/bash

echo "🔄 Sincronizando arquivos para VPS monster.e-ness.com.br"

# Configurações da VPS
VPS_HOST="monster.e-ness.com.br"
VPS_USER="root"
VPS_PATH="/opt/privacy"

# Verificar se SSH funciona
echo "🔍 Testando conexão SSH..."
if ! ssh -o ConnectTimeout=10 $VPS_USER@$VPS_HOST "echo 'SSH OK'"; then
    echo "❌ Falha na conexão SSH. Verifique:"
    echo "  - Chave SSH configurada"
    echo "  - Servidor acessível"
    echo "  - Usuário $VPS_USER tem acesso"
    exit 1
fi

echo "✅ Conexão SSH estabelecida"

# Criar estrutura de diretórios na VPS
echo "📁 Criando estrutura na VPS..."
ssh $VPS_USER@$VPS_HOST "
    mkdir -p $VPS_PATH/{templates,scripts,data}
    mkdir -p $VPS_PATH/backup
"

# Fazer backup dos arquivos existentes
echo "💾 Fazendo backup dos arquivos existentes..."
ssh $VPS_USER@$VPS_HOST "
    if [ -f '$VPS_PATH/web_interface.py' ]; then
        cp $VPS_PATH/*.py $VPS_PATH/backup/ 2>/dev/null || true
        echo 'Backup realizado'
    fi
"

# Copiar arquivos Python principais
echo "📋 Copiando arquivos Python..."
scp *.py $VPS_USER@$VPS_HOST:$VPS_PATH/

# Copiar templates
echo "📄 Copiando templates..."
if [ -d "templates" ]; then
    scp -r templates/* $VPS_USER@$VPS_HOST:$VPS_PATH/templates/
fi

# Copiar scripts
echo "🔧 Copiando scripts..."
if [ -d "scripts" ]; then
    scp -r scripts/* $VPS_USER@$VPS_HOST:$VPS_PATH/scripts/
fi

# Copiar configurações
echo "⚙️ Copiando configurações..."
scp .env.example $VPS_USER@$VPS_HOST:$VPS_PATH/ 2>/dev/null || true
scp README.md $VPS_USER@$VPS_HOST:$VPS_PATH/ 2>/dev/null || true
scp replit.md $VPS_USER@$VPS_HOST:$VPS_PATH/ 2>/dev/null || true

# Ajustar permissões na VPS
echo "🔐 Ajustando permissões na VPS..."
ssh $VPS_USER@$VPS_HOST "
    chown -R privacy:privacy $VPS_PATH 2>/dev/null || true
    chmod 755 $VPS_PATH
    chmod 644 $VPS_PATH/*.py
    chmod +x $VPS_PATH/scripts/*.sh 2>/dev/null || true
    chmod 600 $VPS_PATH/.env 2>/dev/null || true
"

# Verificar estrutura final
echo "🔍 Verificando arquivos na VPS..."
ssh $VPS_USER@$VPS_HOST "
    echo 'Arquivos Python:'
    ls -la $VPS_PATH/*.py | head -5
    echo ''
    echo 'Templates:'
    ls -la $VPS_PATH/templates/ 2>/dev/null || echo 'Pasta templates vazia'
    echo ''
    echo 'Scripts:'
    ls -la $VPS_PATH/scripts/ | head -5
"

# Instalar/atualizar dependências na VPS
echo "📦 Instalando dependências na VPS..."
ssh $VPS_USER@$VPS_HOST "
    cd $VPS_PATH
    if [ ! -d 'venv' ]; then
        python3 -m venv venv
    fi
    source venv/bin/activate
    pip install --upgrade pip
    pip install flask sqlalchemy psycopg2-binary pandas openpyxl
    pip install pdfplumber python-docx pytesseract pillow spacy
    pip install langchain langchain-openai openai gunicorn
    python -m spacy download pt_core_news_sm 2>/dev/null || echo 'Modelo spaCy já instalado'
"

# Reiniciar serviço na VPS
echo "🚀 Reiniciando serviço na VPS..."
ssh $VPS_USER@$VPS_HOST "
    systemctl daemon-reload
    systemctl restart privacy 2>/dev/null || echo 'Serviço será configurado manualmente'
    systemctl status privacy --no-pager -l || echo 'Status do serviço será verificado'
"

echo ""
echo "✅ Sincronização completa!"
echo ""
echo "🌐 Acesse: https://monster.e-ness.com.br"
echo "📊 Status: ssh $VPS_USER@$VPS_HOST 'systemctl status privacy'"
echo "📋 Logs: ssh $VPS_USER@$VPS_HOST 'journalctl -f -u privacy'"
echo ""
echo "🔧 Próximos passos na VPS:"
echo "1. Configurar OPENAI_API_KEY em /opt/privacy/.env"
echo "2. Verificar DATABASE_URL no .env"
echo "3. Reiniciar: systemctl restart privacy"