#!/bin/bash

# Script para executar staging completo na VPS
echo "🧪 Executando staging deployment na VPS"

# Navegar para diretório do projeto
cd /opt/privacy

# Executar staging
sudo ./scripts/staging-deploy.sh

echo "✅ Staging concluído!"