#!/bin/bash

# Script de Instalação do Sistema Robusto de Extração de Dados LGPD
# n.crisisops Privacy LGPD - Versão Enhanced

set -e

echo "🚀 Iniciando instalação do Sistema Robusto de Extração de Dados LGPD"
echo "================================================================"

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Função para log colorido
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Verificar se está rodando como root
if [[ $EUID -eq 0 ]]; then
   log_error "Este script não deve ser executado como root"
   exit 1
fi

# Verificar sistema operacional
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    log_info "Sistema Linux detectado"
elif [[ "$OSTYPE" == "darwin"* ]]; then
    log_info "Sistema macOS detectado"
else
    log_warning "Sistema operacional não testado: $OSTYPE"
fi

# Atualizar sistema
log_info "Atualizando sistema..."
sudo apt update && sudo apt upgrade -y

# Instalar dependências do sistema
log_info "Instalando dependências do sistema..."
sudo apt install -y \
    python3 \
    python3-pip \
    python3-venv \
    python3-dev \
    build-essential \
    libssl-dev \
    libffi-dev \
    git \
    curl \
    wget \
    unzip \
    nginx \
    certbot \
    python3-certbot-nginx

# Criar diretório do projeto
PROJECT_DIR="/opt/privacy-lgpd-enhanced"
log_info "Criando diretório do projeto: $PROJECT_DIR"
sudo mkdir -p $PROJECT_DIR
sudo chown $USER:$USER $PROJECT_DIR

# Clonar ou copiar arquivos do projeto
if [ -d ".git" ]; then
    log_info "Copiando arquivos do projeto atual..."
    cp -r . $PROJECT_DIR/
else
    log_info "Baixando projeto do repositório..."
    cd $PROJECT_DIR
    git clone https://github.com/seu-usuario/IncidentResponse-Privacy.git .
fi

cd $PROJECT_DIR

# Criar ambiente virtual
log_info "Criando ambiente virtual Python..."
python3 -m venv venv
source venv/bin/activate

# Atualizar pip
log_info "Atualizando pip..."
pip install --upgrade pip

# Instalar dependências Python
log_info "Instalando dependências Python..."
pip install -r requirements_enhanced.txt

# Instalar spaCy modelo português
log_info "Instalando modelo spaCy para português..."
python -m spacy download pt_core_news_sm

# Criar diretórios necessários
log_info "Criando diretórios do sistema..."
mkdir -p output reports logs data

# Configurar permissões
log_info "Configurando permissões..."
chmod +x *.py
chmod +x *.sh

# Configurar nginx
log_info "Configurando nginx..."
sudo tee /etc/nginx/sites-available/privacy-lgpd << EOF
server {
    listen 80;
    server_name monster.e-ness.com.br;
    
    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
}
EOF

# Ativar site
sudo ln -sf /etc/nginx/sites-available/privacy-lgpd /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default

# Configurar serviço systemd
log_info "Configurando serviço systemd..."
sudo tee /etc/systemd/system/privacy-enhanced.service << EOF
[Unit]
Description=Privacy LGPD Enhanced Service
After=network.target

[Service]
Type=exec
User=$USER
Group=$USER
WorkingDirectory=$PROJECT_DIR
Environment=PATH=$PROJECT_DIR/venv/bin
ExecStart=$PROJECT_DIR/venv/bin/gunicorn --config gunicorn.conf.py main:app
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Recarregar systemd
sudo systemctl daemon-reload

# Configurar SSL com Certbot
log_info "Configurando SSL..."
sudo certbot --nginx -d monster.e-ness.com.br --non-interactive --agree-tos --email seu-email@exemplo.com

# Testar configuração do nginx
log_info "Testando configuração do nginx..."
sudo nginx -t

# Iniciar serviços
log_info "Iniciando serviços..."
sudo systemctl enable privacy-enhanced
sudo systemctl start privacy-enhanced
sudo systemctl enable nginx
sudo systemctl start nginx

# Verificar status dos serviços
log_info "Verificando status dos serviços..."
sudo systemctl status privacy-enhanced --no-pager
sudo systemctl status nginx --no-pager

# Criar script de teste
log_info "Criando script de teste..."
tee test_system.py << EOF
#!/usr/bin/env python3
import requests
import json
from integrated_processor import processar_dados_lgpd

def test_system():
    print("🧪 Testando sistema...")
    
    # Teste de extração
    texto_teste = '''
    Cliente: João Silva
    CPF: 123.456.789-00
    Email: joao.silva@bradesco.com.br
    Telefone: (11) 99999-9999
    Data de Nascimento: 15/03/1985
    '''
    
    # Salvar arquivo de teste
    with open('teste.txt', 'w', encoding='utf-8') as f:
        f.write(texto_teste)
    
    # Processar
    resultado = processar_dados_lgpd('teste.txt')
    print(json.dumps(resultado, indent=2, ensure_ascii=False))
    
    # Teste da API web
    try:
        response = requests.get('http://localhost:5000/health')
        print(f"✅ API Web: {response.status_code}")
    except:
        print("❌ API Web não respondeu")
    
    print("✅ Teste concluído!")

if __name__ == "__main__":
    test_system()
EOF

# Executar teste
log_info "Executando teste do sistema..."
python test_system.py

# Criar documentação
log_info "Criando documentação..."
tee README_ENHANCED.md << EOF
# Sistema Robusto de Extração de Dados LGPD - Enhanced

## Características

### 🔍 Extração Robusta com Regex Garantido
- Padrões regex otimizados para dados brasileiros
- Validação automática de CPF, email, telefone, etc.
- Detecção de contexto para melhor precisão

### 🤖 IA Semântica para Clientes Prioritários
- Análise semântica com spaCy
- Detecção automática de clientes prioritários
- Refinamento de dados com contexto

### ✅ Validação e Correção Automática
- Validação de integridade de dados
- Correção automática de formatos
- Relatórios detalhados de validação

### 📊 Processamento Integrado
- Processamento em lote de arquivos
- Relatórios consolidados
- Estatísticas detalhadas

## Uso

### Processar arquivo único:
\`\`\`bash
python integrated_processor.py arquivo.txt
\`\`\`

### Processar diretório:
\`\`\`bash
python integrated_processor.py /caminho/diretorio
\`\`\`

### Com configuração personalizada:
\`\`\`bash
python integrated_processor.py arquivo.txt config_processor.json
\`\`\`

## Configuração

Edite \`config_processor.json\` para personalizar:
- Clientes prioritários
- Threshold de validação
- Configurações de IA semântica
- Padrões regex

## Logs

Os logs são salvos em:
- \`logs/processor.log\` - Logs do processador
- \`reports/\` - Relatórios consolidados
- \`output/\` - Dados extraídos

## Status do Serviço

\`\`\`bash
sudo systemctl status privacy-enhanced
sudo systemctl status nginx
\`\`\`

## Reiniciar Serviços

\`\`\`bash
sudo systemctl restart privacy-enhanced
sudo systemctl restart nginx
\`\`\`
EOF

log_success "🎉 Instalação concluída com sucesso!"
log_info "📁 Diretório do projeto: $PROJECT_DIR"
log_info "🌐 Acesso web: https://monster.e-ness.com.br"
log_info "📖 Documentação: $PROJECT_DIR/README_ENHANCED.md"

echo ""
echo "Próximos passos:"
echo "1. Acesse https://monster.e-ness.com.br"
echo "2. Configure clientes prioritários em config_processor.json"
echo "3. Execute testes: python test_system.py"
echo "4. Monitore logs: tail -f logs/processor.log"
echo ""
echo "Para suporte, consulte a documentação ou entre em contato." 