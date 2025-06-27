#!/bin/bash

# Script para copiar templates para VPS

echo "📁 Criando diretório templates..."
mkdir -p /opt/privacy/templates

echo "📋 Copiando arquivo dashboard.html..."
cp /opt/privacy/app/templates/dashboard.html /opt/privacy/templates/ 2>/dev/null || echo "Arquivo não encontrado em app/templates/"

# Verificar se existe no diretório atual
if [ -f "./templates/dashboard.html" ]; then
    cp ./templates/dashboard.html /opt/privacy/templates/
    echo "✅ Template copiado do diretório atual"
elif [ -f "/opt/privacy/app/templates/dashboard.html" ]; then
    echo "✅ Template já existe em /opt/privacy/templates/"
else
    echo "❌ Template não encontrado. Criando estrutura básica..."
    
    # Criar estrutura básica se não existir
    cat > /opt/privacy/templates/dashboard.html << 'EOF'
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>n.crisisops - LGPD Dashboard</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        .header { background: #2c3e50; color: white; padding: 20px; margin-bottom: 20px; }
        .container { max-width: 1200px; margin: 0 auto; }
        .card { background: white; border: 1px solid #ddd; padding: 20px; margin: 10px 0; border-radius: 5px; }
        .btn { background: #3498db; color: white; padding: 10px 20px; border: none; border-radius: 3px; cursor: pointer; }
        .btn:hover { background: #2980b9; }
    </style>
</head>
<body>
    <div class="header">
        <div class="container">
            <h1>n.crisisops - Privacy Module</h1>
            <p>Sistema de Gestão de Resposta a Incidentes LGPD</p>
        </div>
    </div>
    
    <div class="container">
        <div class="card">
            <h2>Dashboard LGPD</h2>
            <p>Sistema funcionando. Para configuração completa, copie o template original.</p>
            <button class="btn" onclick="window.location.reload()">Atualizar</button>
        </div>
    </div>
</body>
</html>
EOF
    echo "✅ Template básico criado"
fi

echo "🔍 Verificando templates existentes..."
ls -la /opt/privacy/templates/

echo "✅ Configuração de templates concluída"