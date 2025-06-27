# Scripts de Deploy - n.crisisops

Este diretório contém todos os scripts necessários para deploy e manutenção do sistema LGPD na VPS.

## Scripts Disponíveis

### 📦 Deploy e Instalação

- **`deploy.sh`** - Script principal de deploy para VPS
- **`install_service.sh`** - Instalação do serviço systemd
- **`fix-dependencies.sh`** - Correção de dependências PyMuPDF

### 🗄️ Banco de Dados

- **`populate-database.sh`** - Popular banco PostgreSQL (via psql)
- **`populate-database.py`** - Popular banco PostgreSQL (via Python)

### 🔧 Manutenção

- **`debug_service.sh`** - Debug do serviço em produção
- **`fix_502.sh`** - Correção de erros 502
- **`test_postgresql.sh`** - Teste de conectividade PostgreSQL

## Como Usar na VPS

### 1. Popular o Banco de Dados

Execute um dos comandos abaixo na VPS:

```bash
# Opção 1: Via shell script (requer psql)
cd /opt/privacy
./scripts/populate-database.sh

# Opção 2: Via Python (requer psycopg2)
cd /opt/privacy
python3 scripts/populate-database.py
```

### 2. Verificar Status do Sistema

```bash
# Verificar serviço
systemctl status privacy

# Debug completo
./scripts/debug_service.sh

# Testar PostgreSQL
./scripts/test_postgresql.sh
```

### 3. Corrigir Problemas Comuns

```bash
# Erro PyMuPDF/fitz
./scripts/fix-dependencies.sh

# Erro 502 Nginx
./scripts/fix_502.sh
```

## Dados Inseridos pelos Scripts

### Prioridades de Busca (25 empresas)
- Bradesco, Petrobras, ONS, Embraer
- Rede D'Or, Globo, Eletrobras
- Vale, Itaú, Santander, BTG Pactual
- E mais 14 empresas prioritárias

### Padrões Regex (20 tipos)
- CPF, RG, CNH, Passaporte
- Email, Telefone, Celular
- CEP, Conta Bancária, Cartão de Crédito
- PIS/PASEP, Título de Eleitor
- CNPJ, Endereço, Placa de Veículo
- E mais 5 padrões específicos

## Configurações de Produção

- **Domínio**: monster.e-ness.com.br
- **Porta**: 5000
- **Usuário**: privacy
- **Diretório**: /opt/privacy
- **Banco**: PostgreSQL (privacy/ncrisisops_secure_2025)
- **SSL**: Certbot/Let's Encrypt