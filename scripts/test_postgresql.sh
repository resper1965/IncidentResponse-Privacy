#!/bin/bash

# =============================================================================
# Script de Teste PostgreSQL
# n.crisisops - Sistema LGPD
# =============================================================================

echo "🧪 Testando PostgreSQL para n.crisisops..."

# Verificar se PostgreSQL está rodando
echo "1. Verificando serviço PostgreSQL..."
if systemctl is-active --quiet postgresql; then
    echo "✅ PostgreSQL ativo"
else
    echo "❌ PostgreSQL inativo - iniciando..."
    systemctl start postgresql
    sleep 3
fi

# Verificar se usuário privacy existe
echo "2. Verificando usuário 'privacy'..."
if sudo -u postgres psql -tAc "SELECT 1 FROM pg_roles WHERE rolname='privacy'" | grep -q 1; then
    echo "✅ Usuário 'privacy' existe"
else
    echo "❌ Criando usuário 'privacy'..."
    sudo -u postgres psql -c "CREATE USER privacy WITH PASSWORD 'ncrisisops_secure_2025';"
fi

# Verificar se banco privacy existe
echo "3. Verificando banco 'privacy'..."
if sudo -u postgres psql -lqt | cut -d \| -f 1 | grep -qw privacy; then
    echo "✅ Banco 'privacy' existe"
else
    echo "❌ Criando banco 'privacy'..."
    sudo -u postgres psql -c "CREATE DATABASE privacy OWNER privacy;"
fi

# Conceder privilégios
echo "4. Concedendo privilégios..."
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE privacy TO privacy;"

# Testar conexão
echo "5. Testando conexão..."
if PGPASSWORD="ncrisisops_secure_2025" psql -h localhost -U privacy -d privacy -c "SELECT version();" > /dev/null 2>&1; then
    echo "✅ Conexão PostgreSQL funcionando"
else
    echo "❌ Erro na conexão PostgreSQL"
    echo "Detalhes do erro:"
    PGPASSWORD="ncrisisops_secure_2025" psql -h localhost -U privacy -d privacy -c "SELECT version();"
fi

# Listar bancos disponíveis
echo "6. Bancos disponíveis:"
sudo -u postgres psql -l

# Mostrar informações de conexão
echo "7. Informações de conexão:"
echo "Host: localhost"
echo "Port: 5432"
echo "Database: privacy"
echo "Username: privacy"
echo "Password: ncrisisops_secure_2025"

echo ""
echo "🔗 String de conexão:"
echo "postgresql://privacy:ncrisisops_secure_2025@localhost:5432/privacy"

echo ""
echo "🧪 Teste concluído!"