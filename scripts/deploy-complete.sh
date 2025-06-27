#!/bin/bash

# Deploy completo para VPS - copia todos os arquivos necessários

echo "🚀 Deploy completo do n.crisisops para VPS..."

# Criar diretórios necessários
mkdir -p /opt/privacy/templates
mkdir -p /opt/privacy/scripts
mkdir -p /opt/privacy/data

# Copiar arquivos Python principais
echo "📋 Copiando arquivos Python..."
cp *.py /opt/privacy/ 2>/dev/null || echo "Arquivos Python já estão no local"

# Copiar template
echo "📄 Copiando template..."
if [ -f "templates/dashboard.html" ]; then
    cp templates/dashboard.html /opt/privacy/templates/
    echo "✅ Template dashboard.html copiado"
else
    echo "❌ Template não encontrado, criando básico..."
    # Criar template básico
    cat > /opt/privacy/templates/dashboard.html << 'EOF'
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>n.crisisops - LGPD Dashboard</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
</head>
<body>
    <nav class="navbar navbar-dark bg-dark">
        <div class="container-fluid">
            <span class="navbar-brand mb-0 h1">
                <i class="fas fa-shield-alt"></i> n.crisisops - Privacy Module
            </span>
        </div>
    </nav>
    
    <div class="container-fluid mt-4">
        <div class="row">
            <div class="col-12">
                <div class="card">
                    <div class="card-header">
                        <h5 class="card-title mb-0">
                            <i class="fas fa-tachometer-alt"></i> Dashboard LGPD
                        </h5>
                    </div>
                    <div class="card-body">
                        <div class="alert alert-info">
                            <i class="fas fa-info-circle"></i>
                            Sistema LGPD funcionando. Dashboard completo será carregado após configuração.
                        </div>
                        <button class="btn btn-primary" onclick="window.location.reload()">
                            <i class="fas fa-sync-alt"></i> Atualizar
                        </button>
                    </div>
                </div>
            </div>
        </div>
    </div>
    
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
EOF
    echo "✅ Template básico criado"
fi

# Copiar scripts
echo "🔧 Copiando scripts..."
cp scripts/*.sh /opt/privacy/scripts/ 2>/dev/null
cp scripts/*.py /opt/privacy/scripts/ 2>/dev/null
chmod +x /opt/privacy/scripts/*.sh

# Copiar requirements
echo "📦 Copiando requirements..."
cp production-requirements.txt /opt/privacy/ 2>/dev/null
cp requirements.txt /opt/privacy/ 2>/dev/null

# Copiar .env de exemplo
echo "⚙️ Copiando configurações..."
cp .env.example /opt/privacy/ 2>/dev/null

# Verificar estrutura final
echo "🔍 Verificando estrutura final..."
echo "Arquivos em /opt/privacy:"
ls -la /opt/privacy/

echo "Templates:"
ls -la /opt/privacy/templates/

echo "Scripts:"
ls -la /opt/privacy/scripts/

# Ajustar permissões
echo "🔐 Ajustando permissões..."
chown -R privacy:privacy /opt/privacy/
chmod 755 /opt/privacy/
chmod 644 /opt/privacy/*.py
chmod 755 /opt/privacy/scripts/*.sh

echo ""
echo "✅ Deploy completo finalizado!"
echo ""
echo "🚀 Para iniciar o serviço:"
echo "   systemctl restart privacy"
echo "   systemctl status privacy"
echo ""
echo "🌐 Acesse: https://monster.e-ness.com.br"