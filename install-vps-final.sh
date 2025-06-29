#!/bin/bash

# n.crisisops Privacy LGPD System - Instalação para VPS
# Repositório oficial: https://github.com/resper1965/IncidentResponse-Privacy
# Sempre utilize a versão mais recente do repositório acima!

set -e

echo "🚀 Iniciando instalação do n.crisisops Privacy LGPD System..."
echo "🔗 Repositório oficial: https://github.com/resper1965/IncidentResponse-Privacy"

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Função para log
log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')] $1${NC}"
}

error() {
    echo -e "${RED}[ERRO] $1${NC}"
    exit 1
}

warning() {
    echo -e "${YELLOW}[AVISO] $1${NC}"
}

info() {
    echo -e "${BLUE}[INFO] $1${NC}"
}

# Verificar se é root
if [[ $EUID -eq 0 ]]; then
   error "Este script não deve ser executado como root"
fi

# Verificar sistema operacional
if [[ "$OSTYPE" != "linux-gnu"* ]]; then
    error "Este script é destinado apenas para sistemas Linux"
fi

# Verificar se Python 3 está instalado
if ! command -v python3 &> /dev/null; then
    error "Python 3 não está instalado. Instale Python 3.8+ primeiro."
fi

# Verificar versão do Python
PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
if [[ $(echo "$PYTHON_VERSION < 3.8" | bc -l) -eq 1 ]]; then
    error "Python 3.8+ é necessário. Versão atual: $PYTHON_VERSION"
fi

log "✅ Verificações iniciais concluídas"

# Criar diretório do projeto
PROJECT_DIR="/opt/privacy-lgpd"
log "📁 Criando diretório do projeto: $PROJECT_DIR"

sudo mkdir -p $PROJECT_DIR
sudo chown $USER:$USER $PROJECT_DIR
cd $PROJECT_DIR

# Criar estrutura de diretórios
log "📂 Criando estrutura de diretórios"
mkdir -p {uploads,output,reports,logs,templates}

# Copiar arquivos do projeto
log "📋 Copiando arquivos do projeto"

# Verificar se os arquivos estão no diretório atual
if [[ -f "main_enhanced.py" ]]; then
    cp main_enhanced.py $PROJECT_DIR/
else
    error "Arquivo main_enhanced.py não encontrado no diretório atual"
fi

if [[ -f "requirements.txt" ]]; then
    cp requirements.txt $PROJECT_DIR/
else
    error "Arquivo requirements.txt não encontrado no diretório atual"
fi

if [[ -f "gunicorn.conf.py" ]]; then
    cp gunicorn.conf.py $PROJECT_DIR/
else
    error "Arquivo gunicorn.conf.py não encontrado no diretório atual"
fi

if [[ -d "templates" ]]; then
    cp -r templates/* $PROJECT_DIR/templates/
else
    error "Diretório templates não encontrado no diretório atual"
fi

# Criar ambiente virtual
log "🐍 Criando ambiente virtual Python"
python3 -m venv venv
source venv/bin/activate

# Atualizar pip
log "⬆️ Atualizando pip"
pip install --upgrade pip

# Instalar dependências
log "📦 Instalando dependências Python"
pip install -r requirements.txt

# Criar arquivo de configuração do sistema
log "⚙️ Criando configuração do sistema"
cat > $PROJECT_DIR/config.json << EOF
{
    "system": {
        "name": "n.crisisops Privacy LGPD",
        "version": "2.0.0",
        "port": 5000,
        "host": "0.0.0.0"
    },
    "processing": {
        "max_file_size_mb": 100,
        "supported_formats": ["txt", "doc", "docx", "pdf", "eml", "msg", "rtf"],
        "workers": 2,
        "timeout": 300
    },
    "priority_clients": {
        "bradesco": ["bradesco", "banco bradesco", "bradesco s.a."],
        "petrobras": ["petrobras", "petrobras s.a.", "petrobras brasil"],
        "ons": ["ons", "operador nacional do sistema elétrico"],
        "embraer": ["embraer", "embraer s.a."],
        "rede_dor": ["rede dor", "rede d'or", "rededor"],
        "globo": ["globo", "organizações globo", "rede globo"],
        "eletrobras": ["eletrobras", "eletrobras s.a."],
        "crefisa": ["crefisa", "banco crefisa"],
        "equinix": ["equinix", "equinix brasil"],
        "cohesity": ["cohesity", "cohesity brasil"]
    }
}
EOF

# Criar arquivo de inicialização do sistema
log "🔧 Criando arquivo de inicialização"
cat > $PROJECT_DIR/start.sh << 'EOF'
#!/bin/bash
cd /opt/privacy-lgpd
source venv/bin/activate
gunicorn -c gunicorn.conf.py main_enhanced:app
EOF

chmod +x $PROJECT_DIR/start.sh

# Criar arquivo de parada do sistema
log "🛑 Criando arquivo de parada"
cat > $PROJECT_DIR/stop.sh << 'EOF'
#!/bin/bash
pkill -f "gunicorn.*main_enhanced"
echo "Sistema parado com sucesso"
EOF

chmod +x $PROJECT_DIR/stop.sh

# Criar arquivo de status do sistema
log "📊 Criando arquivo de status"
cat > $PROJECT_DIR/status.sh << 'EOF'
#!/bin/bash
if pgrep -f "gunicorn.*main_enhanced" > /dev/null; then
    echo "✅ Sistema está rodando"
    ps aux | grep "gunicorn.*main_enhanced" | grep -v grep
else
    echo "❌ Sistema não está rodando"
fi
EOF

chmod +x $PROJECT_DIR/status.sh

# Criar arquivo de logs
log "📝 Criando arquivo de logs"
cat > $PROJECT_DIR/logs/app.log << EOF
$(date): Sistema instalado com sucesso
$(date): Diretório: $PROJECT_DIR
$(date): Usuário: $USER
$(date): Python: $(python3 --version)
EOF

# Criar arquivo de teste
log "🧪 Criando arquivo de teste"
cat > $PROJECT_DIR/test.txt << EOF
Este é um arquivo de teste para o sistema n.crisisops Privacy LGPD.

Dados de teste:
- CPF: 123.456.789-00
- Email: teste@empresa.com
- Telefone: (11) 99999-9999
- Data: 01/01/1990
- CEP: 01234-567

Cliente: Bradesco S.A.
Endereço: Av. Paulista, 1000 - São Paulo/SP
RG: 12.345.678-9
Placa: ABC-1234
IP: 192.168.1.1
EOF

# Testar o sistema
log "🧪 Testando o sistema"
cd $PROJECT_DIR
source venv/bin/activate

# Testar se o Flask pode ser importado
python3 -c "import flask; print('✅ Flask importado com sucesso')" || error "Erro ao importar Flask"

# Testar se o arquivo principal pode ser executado
python3 -c "import main_enhanced; print('✅ Arquivo principal carregado com sucesso')" || error "Erro ao carregar arquivo principal"

# Criar arquivo de documentação
log "📚 Criando documentação"
cat > $PROJECT_DIR/README.md << EOF
# n.crisisops Privacy LGPD System

## Visão Geral
Sistema de extração e análise de dados para conformidade com a LGPD.

## Instalação
O sistema foi instalado em: $PROJECT_DIR

## Comandos Úteis

### Iniciar o sistema:
\`\`\`bash
cd $PROJECT_DIR
./start.sh
\`\`\`

### Parar o sistema:
\`\`\`bash
cd $PROJECT_DIR
./stop.sh
\`\`\`

### Verificar status:
\`\`\`bash
cd $PROJECT_DIR
./status.sh
\`\`\`

### Acessar interface web:
http://localhost:5000

## Estrutura de Diretórios
- \`uploads/\`: Arquivos enviados para processamento
- \`output/\`: Resultados do processamento
- \`reports/\`: Relatórios gerados
- \`logs/\`: Logs do sistema
- \`templates/\`: Templates HTML

## Configuração
O arquivo \`config.json\` contém as configurações do sistema.

## Teste
Use o arquivo \`test.txt\` para testar o sistema.

## Logs
Os logs são salvos em \`logs/app.log\`

## Suporte
Para suporte técnico, consulte a documentação ou entre em contato com a equipe n.crisisops.
EOF

# Criar arquivo de configuração do systemd (opcional)
log "🔧 Criando configuração do systemd (opcional)"
sudo tee /etc/systemd/system/privacy-lgpd.service > /dev/null << EOF
[Unit]
Description=n.crisisops Privacy LGPD System
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=$PROJECT_DIR
Environment=PATH=$PROJECT_DIR/venv/bin
ExecStart=$PROJECT_DIR/venv/bin/gunicorn -c gunicorn.conf.py main_enhanced:app
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Habilitar e iniciar o serviço (opcional)
read -p "Deseja habilitar o serviço systemd? (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    log "🔧 Habilitando serviço systemd"
    sudo systemctl daemon-reload
    sudo systemctl enable privacy-lgpd.service
    sudo systemctl start privacy-lgpd.service
    log "✅ Serviço systemd habilitado e iniciado"
else
    warning "Serviço systemd não foi habilitado. Use ./start.sh para iniciar manualmente."
fi

# Configurar firewall (se disponível)
if command -v ufw &> /dev/null; then
    log "🔥 Configurando firewall"
    sudo ufw allow 5000/tcp
    log "✅ Porta 5000 liberada no firewall"
elif command -v firewall-cmd &> /dev/null; then
    log "🔥 Configurando firewall (firewalld)"
    sudo firewall-cmd --permanent --add-port=5000/tcp
    sudo firewall-cmd --reload
    log "✅ Porta 5000 liberada no firewall"
else
    warning "Firewall não detectado. Configure manualmente se necessário."
fi

# Teste final
log "🧪 Executando teste final"
cd $PROJECT_DIR
source venv/bin/activate

# Iniciar o sistema em background para teste
timeout 10s gunicorn -c gunicorn.conf.py main_enhanced:app &
GUNICORN_PID=$!

# Aguardar um pouco para o sistema inicializar
sleep 3

# Testar se o sistema está respondendo
if curl -s http://localhost:5000/health > /dev/null; then
    log "✅ Sistema está funcionando corretamente!"
else
    warning "⚠️ Sistema pode não estar respondendo corretamente"
fi

# Parar o processo de teste
kill $GUNICORN_PID 2>/dev/null || true

# Resumo final
log "🎉 Instalação concluída com sucesso!"
echo
echo "📋 RESUMO DA INSTALAÇÃO:"
echo "========================="
echo "📍 Diretório: $PROJECT_DIR"
echo "🐍 Python: $(python3 --version)"
echo "🌐 Porta: 5000"
echo "👤 Usuário: $USER"
echo "📁 Uploads: $PROJECT_DIR/uploads"
echo "📊 Relatórios: $PROJECT_DIR/reports"
echo "📝 Logs: $PROJECT_DIR/logs"
echo
echo "🚀 PARA INICIAR O SISTEMA:"
echo "=========================="
echo "cd $PROJECT_DIR"
echo "./start.sh"
echo
echo "🌐 ACESSAR INTERFACE:"
echo "===================="
echo "http://localhost:5000"
echo
echo "📚 DOCUMENTAÇÃO:"
echo "================"
echo "cat $PROJECT_DIR/README.md"
echo
echo "✅ Instalação finalizada com sucesso!" 