#!/bin/bash

# Test navigation functionality on VPS
echo "🧪 Testing navigation and directory structure on VPS..."

cd /opt/privacy

# Check if data directory exists and create sample structure
echo "📁 Setting up test directory structure..."
mkdir -p data/bradesco/emails
mkdir -p data/petrobras/contratos
mkdir -p data/ons/documentos
mkdir -p data/embraer/projetos
mkdir -p data/outros/diversos

# Create some test files to demonstrate navigation
echo "📄 Creating test files..."
echo "Este é um email de joão.silva@bradesco.com.br" > data/bradesco/emails/email_teste.txt
echo "Contrato com representante da Petrobras: maria.santos@petrobras.com.br" > data/petrobras/contratos/contrato_exemplo.txt
echo "Documento ONS com CPF 123.456.789-00" > data/ons/documentos/documento_tecnico.txt
echo "Projeto Embraer - Engenheiro: carlos.lima@embraer.com.br" > data/embraer/projetos/projeto_aviacao.txt
echo "Dados diversos com telefone (11) 98765-4321" > data/outros/diversos/arquivo_misto.txt

# Set proper ownership
chown -R privacy:privacy data/

# Test file scanner
echo "🔍 Testing file scanner..."
/opt/privacy/venv/bin/python3 -c "
import sys
sys.path.append('/opt/privacy')
from file_scanner import listar_arquivos_recursivos, obter_informacoes_arquivo

print('=== TESTE DE NAVEGAÇÃO DE ARQUIVOS ===')
arquivos = listar_arquivos_recursivos('data')
print(f'Total de arquivos encontrados: {len(arquivos)}')

for arquivo in arquivos[:10]:
    info = obter_informacoes_arquivo(arquivo)
    if info:
        print(f'  📄 {info[\"nome\"]} ({info[\"tamanho_mb\"]} MB)')
"

# Test API endpoints
echo "🌐 Testing API endpoints..."
curl -s "http://localhost:5000/api/listar-diretorios?caminho=data" | head -50

echo -e "\n📊 Testing directory validation..."
curl -s "http://localhost:5000/api/validar-diretorio?caminho=data" | head -50

# Check permissions
echo -e "\n🔒 Checking permissions..."
ls -la data/
ls -la data/bradesco/
ls -la data/petrobras/

echo -e "\n✅ Navigation test completed!"
echo "🌍 Access the system at: https://monster.e-ness.com.br"
echo "📂 Use the '📂 Navegar' button to browse the data/ directory structure"