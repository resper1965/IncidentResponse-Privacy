#!/bin/bash

# =============================================================================
# Script de Deploy Completo - n.crisisops
# Sistema LGPD de Compliance e Resposta a Incidentes
# =============================================================================

set -e

VPS_HOST="monster.e-ness.com.br"
VPS_USER="root"
REMOTE_DIR="/opt/privacy/app"

echo "🚀 Iniciando deploy do n.crisisops..."

# Verificar se os arquivos essenciais existem
REQUIRED_FILES=(
    "web_interface.py"
    "database_postgresql.py" 
    "file_reader.py"
    "data_extractor.py"
    "file_scanner.py"
    "ai_super_processor.py"
    "ai_processor_simplified.py"
    "templates/dashboard.html"
)

echo "📋 Verificando arquivos necessários..."
for file in "${REQUIRED_FILES[@]}"; do
    if [ ! -f "$file" ] && [ ! -d "$(dirname $file)" ]; then
        echo "❌ Arquivo ausente: $file"
        exit 1
    fi
    echo "✅ $file"
done

# Criar arquivo temporário com todos os arquivos Python
echo "📦 Preparando arquivos para deploy..."

<<<<<<< HEAD
# Copiar scripts de instalação e manutenção
echo "📋 Copiando scripts de instalação..."
scp scripts/install_service.sh scripts/fix_502.sh scripts/debug_service.sh scripts/test_postgresql.sh scripts/populate-database.sh scripts/populate-database.py scripts/github-fix-simple.sh scripts/fix-dependencies.sh $VPS_USER@$VPS_HOST:/tmp/

# Executar instalação da infraestrutura na VPS
echo "🏗️ Instalando infraestrutura na VPS..."
ssh $VPS_USER@$VPS_HOST "cd /tmp && chmod +x *.sh && ./install_service.sh"
=======
# Copiar scripts de instalação
echo "📋 Copiando scripts de instalação..."
scp install_service.sh fix_502.sh debug_service.sh test_postgresql.sh $VPS_USER@$VPS_HOST:/tmp/

# Executar instalação da infraestrutura na VPS
echo "🏗️ Instalando infraestrutura na VPS..."
ssh $VPS_USER@$VPS_HOST "cd /tmp && chmod +x install_service.sh && ./install_service.sh"
>>>>>>> f36977b1e82c9e3a85f66b08b07aff8b980e5345

# Criar diretório de templates na VPS
echo "📁 Criando estrutura de diretórios..."
ssh $VPS_USER@$VPS_HOST "mkdir -p $REMOTE_DIR/templates"

# Copiar arquivos Python principais
echo "📄 Copiando arquivos da aplicação..."
scp web_interface.py $VPS_USER@$VPS_HOST:$REMOTE_DIR/
scp database_postgresql.py $VPS_USER@$VPS_HOST:$REMOTE_DIR/
scp file_reader.py $VPS_USER@$VPS_HOST:$REMOTE_DIR/
scp data_extractor.py $VPS_USER@$VPS_HOST:$REMOTE_DIR/
scp file_scanner.py $VPS_USER@$VPS_HOST:$REMOTE_DIR/
scp ai_super_processor.py $VPS_USER@$VPS_HOST:$REMOTE_DIR/
scp ai_processor_simplified.py $VPS_USER@$VPS_HOST:$REMOTE_DIR/

# Copiar arquivos opcionais se existirem
OPTIONAL_FILES=(
    "database.py"
    "main.py"
    "ai_enhanced_processor.py"
)

for file in "${OPTIONAL_FILES[@]}"; do
    if [ -f "$file" ]; then
        echo "📄 Copiando arquivo opcional: $file"
        scp $file $VPS_USER@$VPS_HOST:$REMOTE_DIR/
    fi
done

# Copiar templates
echo "🎨 Copiando templates..."
if [ -d "templates" ]; then
    scp -r templates/* $VPS_USER@$VPS_HOST:$REMOTE_DIR/templates/
else
    echo "⚠️ Diretório templates não encontrado"
fi

# Ajustar permissões na VPS
echo "🔐 Ajustando permissões..."
ssh $VPS_USER@$VPS_HOST "chown -R privacy:privacy $REMOTE_DIR"
ssh $VPS_USER@$VPS_HOST "chmod 644 $REMOTE_DIR/*.py"
ssh $VPS_USER@$VPS_HOST "chmod 644 $REMOTE_DIR/templates/*" 2>/dev/null || true

# Inicializar banco de dados
echo "💾 Inicializando banco de dados..."
ssh $VPS_USER@$VPS_HOST "cd $REMOTE_DIR && sudo -u privacy /opt/privacy/venv/bin/python -c 'import database_postgresql; database_postgresql.initialize_postgresql_database()'" || echo "⚠️ Erro na inicialização do banco - continuando..."

# Iniciar serviço
echo "🚀 Iniciando serviço privacy..."
ssh $VPS_USER@$VPS_HOST "systemctl daemon-reload"
ssh $VPS_USER@$VPS_HOST "systemctl enable privacy"
ssh $VPS_USER@$VPS_HOST "systemctl restart privacy"

# Aguardar inicialização
echo "⏳ Aguardando inicialização do serviço..."
sleep 15

# Verificar status
echo "📊 Verificando status do serviço..."
if ssh $VPS_USER@$VPS_HOST "systemctl is-active --quiet privacy"; then
    echo "✅ Serviço privacy ativo"
    
    # Testar health check
    if ssh $VPS_USER@$VPS_HOST "curl -s http://localhost:5000/health" > /dev/null 2>&1; then
        echo "✅ Health check local funcionando"
        
        # Testar acesso externo
        echo "🌍 Testando acesso externo..."
        if curl -s http://$VPS_HOST/health > /dev/null 2>&1; then
            echo "✅ Acesso externo funcionando"
            echo "🎉 Deploy concluído com sucesso!"
            echo "🌐 Sistema disponível em: http://$VPS_HOST"
        else
            echo "⚠️ Acesso externo com problema - verificar Nginx"
        fi
    else
        echo "❌ Health check local falhou"
    fi
else
    echo "❌ Serviço privacy falhou - verificando logs..."
    ssh $VPS_USER@$VPS_HOST "journalctl -u privacy --no-pager -n 10"
    
    echo ""
    echo "🔧 Executando correção automática..."
    ssh $VPS_USER@$VPS_HOST "cd /tmp && ./fix_502.sh"
fi

echo ""
echo "📋 Comandos úteis para monitoramento:"
echo "   ssh $VPS_USER@$VPS_HOST 'systemctl status privacy'"
echo "   ssh $VPS_USER@$VPS_HOST 'journalctl -u privacy -f'"
echo "   ssh $VPS_USER@$VPS_HOST 'curl http://localhost:5000/health'"

echo ""
echo "✅ Deploy finalizado!"