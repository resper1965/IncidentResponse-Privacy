#!/bin/bash

echo "🔧 Configurando padrões regex no PostgreSQL da VPS"

# Execute na VPS como root
cd /opt/privacy

echo "📋 Conectando ao PostgreSQL e criando estrutura..."

# SQL para criar tabelas e inserir padrões regex
sudo -u postgres psql -d privacy << 'EOF'
-- Criar tabela de padrões regex se não existir
CREATE TABLE IF NOT EXISTS regex_patterns (
    id SERIAL PRIMARY KEY,
    nome_campo VARCHAR(100) NOT NULL,
    pattern_regex TEXT NOT NULL,
    explicacao TEXT,
    ativo BOOLEAN DEFAULT TRUE,
    criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Limpar padrões existentes para evitar duplicatas
DELETE FROM regex_patterns;

-- Inserir padrões regex do sistema LGPD
INSERT INTO regex_patterns (nome_campo, pattern_regex, explicacao) VALUES
('CPF', '\b\d{3}\.?\d{3}\.?\d{3}-?\d{2}\b', 'CPF com ou sem formatação'),
('RG', '\b\d{1,2}\.?\d{3}\.?\d{3}-?[0-9Xx]\b', 'RG com formatação SP'),
('RG_SIMPLES', '\b\d{5,9}-?[0-9Xx]\b', 'RG formato simples'),
('EMAIL', '\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', 'Endereço de email'),
('TELEFONE', '\(?\d{2}\)?\s?9?\d{4}-?\d{4}', 'Telefone celular e fixo'),
('CEP', '\b\d{5}-?\d{3}\b', 'CEP brasileiro'),
('DATA_NASCIMENTO', '\b\d{1,2}\/\d{1,2}\/\d{4}\b', 'Data no formato DD/MM/AAAA'),
('CARTAO_CREDITO', '\b\d{4}\s?\d{4}\s?\d{4}\s?\d{4}\b', 'Número de cartão de crédito'),
('CONTA_BANCARIA', '\b\d{4,6}-?\d{1}\b', 'Número de conta bancária'),
('AGENCIA_BANCARIA', '\b\d{4}-?\d{1}?\b', 'Número de agência bancária'),
('PIS_PASEP', '\b\d{3}\.?\d{5}\.?\d{2}-?\d{1}\b', 'PIS/PASEP'),
('TITULO_ELEITOR', '\b\d{4}\s?\d{4}\s?\d{4}\b', 'Título de eleitor'),
('CNH', '\b\d{11}\b', 'Carteira Nacional de Habilitação'),
('PASSAPORTE', '\b[A-Z]{2}\d{6}\b', 'Passaporte brasileiro'),
('NOME_COMPLETO', '\b[A-Z][a-z]+\s+[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b', 'Nome completo com iniciais maiúsculas'),
('ENDERECO', '\b(?:Rua|Av|Avenida|Travessa|Alameda)\s+[A-Za-z\s]+,?\s*\d+', 'Endereço com logradouro');

-- Criar tabela de prioridades de busca se não existir
CREATE TABLE IF NOT EXISTS prioridades_busca (
    id SERIAL PRIMARY KEY,
    prioridade INTEGER NOT NULL,
    nome_empresa VARCHAR(200) NOT NULL,
    dominio_email VARCHAR(100) NOT NULL,
    ativo BOOLEAN DEFAULT TRUE,
    criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Limpar prioridades existentes
DELETE FROM prioridades_busca;

-- Inserir prioridades de empresas
INSERT INTO prioridades_busca (prioridade, nome_empresa, dominio_email) VALUES
(1, 'Banco Bradesco', 'bradesco.com.br'),
(1, 'Petrobras', 'petrobras.com.br'),
(1, 'Operador Nacional do Sistema Elétrico', 'ons.org.br'),
(2, 'Banco do Brasil', 'bb.com.br'),
(2, 'Caixa Econômica Federal', 'caixa.gov.br'),
(2, 'Itaú Unibanco', 'itau.com.br'),
(3, 'Vale S.A.', 'vale.com'),
(3, 'JBS S.A.', 'jbs.com.br'),
(3, 'Ambev', 'ambev.com.br'),
(4, 'Magazine Luiza', 'magazineluiza.com.br'),
(4, 'Via Varejo', 'viavarejo.com.br'),
(5, 'Embraer', 'embraer.com.br');

-- Verificar dados inseridos
SELECT 'Padrões Regex:', COUNT(*) FROM regex_patterns;
SELECT 'Prioridades:', COUNT(*) FROM prioridades_busca;

EOF

echo "✅ Padrões regex e prioridades configurados no PostgreSQL"

echo "🧪 Testando conexão Python com PostgreSQL..."
source venv/bin/activate
python3 -c "
import database_postgresql as db_pg
try:
    patterns = db_pg.get_regex_patterns()
    print(f'✅ {len(patterns)} padrões regex carregados')
    priorities = db_pg.get_search_priorities()
    print(f'✅ {len(priorities)} prioridades carregadas')
except Exception as e:
    print(f'❌ Erro: {e}')
"

echo "🔄 Reiniciando serviço..."
systemctl restart privacy

echo "📊 Verificando status..."
systemctl status privacy --no-pager -l

echo ""
echo "✅ Configuração completa!"
echo "🌐 Acesse: https://monster.e-ness.com.br"
echo "📋 Os padrões regex e prioridades estão configurados no PostgreSQL"