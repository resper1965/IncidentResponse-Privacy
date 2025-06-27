#!/bin/bash

# =============================================================================
# Script de População do Banco de Dados - n.crisisops
# Popular padrões regex e prioridades de busca no PostgreSQL
# =============================================================================

echo "🗄️ Populando banco de dados PostgreSQL..."

# Configurações da conexão
DB_HOST="localhost"
DB_NAME="privacy"
DB_USER="privacy"
DB_PASS="ncrisisops_secure_2025"

export PGPASSWORD="$DB_PASS"

echo "📋 Inserindo prioridades de busca..."

# Inserir prioridades de busca
psql -h $DB_HOST -U $DB_USER -d $DB_NAME << 'EOF'
-- Limpar tabela existente
TRUNCATE TABLE search_priorities RESTART IDENTITY CASCADE;

-- Inserir prioridades de busca padrão
INSERT INTO search_priorities (priority, company_name, email_domain, is_active) VALUES
(1, 'BRADESCO', 'bradesco.com.br', true),
(2, 'PETROBRAS', 'petrobras.com.br', true),
(3, 'ONS', 'ons.org.br', true),
(4, 'EMBRAER', 'embraer.com.br', true),
(5, 'REDE DOR', 'rededor.com.br', true),
(6, 'ED GLOBO', 'edglobo.com.br', true),
(7, 'GLOBO', 'globo.com', true),
(8, 'ELETROBRAS', 'eletrobras.com', true),
(9, 'CREFISA', 'crefisa.com.br', true),
(10, 'EQUINIX', 'equinix.com', true),
(11, 'COHESITY', 'cohesity.com', true),
(12, 'NETAPP', 'netapp.com', true),
(13, 'HITACHI', 'hitachi.com', true),
(14, 'LENOVO', 'lenovo.com', true),
(15, 'VALE', 'vale.com', true),
(16, 'ITAU', 'itau.com.br', true),
(17, 'SANTANDER', 'santander.com.br', true),
(18, 'BTG PACTUAL', 'btgpactual.com', true),
(19, 'AMBEV', 'ambev.com.br', true),
(20, 'JBS', 'jbs.com.br', true);

SELECT 'Prioridades de busca inseridas: ' || COUNT(*) FROM search_priorities;
EOF

echo "🔍 Inserindo padrões regex..."

# Inserir padrões regex
psql -h $DB_HOST -U $DB_USER -d $DB_NAME << 'EOF'
-- Limpar tabela existente
TRUNCATE TABLE regex_patterns RESTART IDENTITY CASCADE;

-- Inserir padrões regex padrão
INSERT INTO regex_patterns (field_name, regex_pattern, explanation, is_active) VALUES
('cpf', '\b\d{3}\.?\d{3}\.?\d{3}-?\d{2}\b', 'CPF no formato XXX.XXX.XXX-XX ou apenas dígitos', true),
('rg', '\b\d{1,2}\.?\d{3}\.?\d{3}-?[0-9X]\b', 'RG no formato XX.XXX.XXX-X', true),
('cnh', '\b\d{11}\b', 'CNH com 11 dígitos', true),
('passaporte', '\b[A-Z]{2}\d{6}\b', 'Passaporte brasileiro formato AAXXXXXX', true),
('email', '\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', 'Endereço de email válido', true),
('telefone', '\b(?:\+55\s?)?(?:\(\d{2}\)\s?)?(?:9\s?)?\d{4}-?\d{4}\b', 'Telefone brasileiro com ou sem código de área', true),
('celular', '\b(?:\+55\s?)?(?:\(\d{2}\)\s?)?9\d{4}-?\d{4}\b', 'Celular brasileiro', true),
('cep', '\b\d{5}-?\d{3}\b', 'CEP no formato XXXXX-XXX', true),
('conta_bancaria', '\b\d{4,8}-?\d{1}\b', 'Conta bancária com dígito verificador', true),
('agencia', '\b\d{4}-?\d{1}\b', 'Agência bancária', true),
('cartao_credito', '\b(?:\d{4}\s?){3}\d{4}\b', 'Cartão de crédito 16 dígitos', true),
('pis_pasep', '\b\d{3}\.?\d{5}\.?\d{2}-?\d{1}\b', 'PIS/PASEP', true),
('titulo_eleitor', '\b\d{4}\s?\d{4}\s?\d{4}\b', 'Título de eleitor', true),
('cnpj', '\b\d{2}\.?\d{3}\.?\d{3}\/?\d{4}-?\d{2}\b', 'CNPJ formato XX.XXX.XXX/XXXX-XX', true),
('endereco', '\b(?:Rua|Av|Avenida|R\.|Al|Alameda|Tv|Travessa|Pç|Praça)\s+[^,\n]+,?\s*\d+', 'Endereço com logradouro e número', true);

SELECT 'Padrões regex inseridos: ' || COUNT(*) FROM regex_patterns;
EOF

echo "📊 Verificando dados inseridos..."

# Verificar inserção
psql -h $DB_HOST -U $DB_USER -d $DB_NAME << 'EOF'
-- Mostrar estatísticas
SELECT 
    'SEARCH_PRIORITIES' as tabela,
    COUNT(*) as total_registros,
    COUNT(*) FILTER (WHERE is_active = true) as ativos
FROM search_priorities
UNION ALL
SELECT 
    'REGEX_PATTERNS' as tabela,
    COUNT(*) as total_registros,
    COUNT(*) FILTER (WHERE is_active = true) as ativos
FROM regex_patterns;

-- Mostrar algumas prioridades
SELECT '--- PRIORIDADES DE BUSCA (Top 10) ---' as info;
SELECT priority, company_name, email_domain 
FROM search_priorities 
WHERE is_active = true 
ORDER BY priority 
LIMIT 10;

-- Mostrar alguns padrões
SELECT '--- PADRÕES REGEX (Alguns exemplos) ---' as info;
SELECT field_name, explanation 
FROM regex_patterns 
WHERE is_active = true 
ORDER BY field_name 
LIMIT 8;
EOF

echo ""
echo "✅ População do banco concluída!"
echo ""
echo "📋 Para verificar os dados posteriormente:"
echo "   psql -h localhost -U privacy -d privacy"
echo "   SELECT * FROM search_priorities ORDER BY priority;"
echo "   SELECT * FROM regex_patterns WHERE is_active = true;"