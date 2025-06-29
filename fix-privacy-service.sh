#!/bin/bash

# Script para corrigir problemas do serviço privacy
# Execute como root no VPS

set -e

echo "🔧 Corrigindo problemas do serviço privacy..."

# 1. Parar o serviço se estiver rodando
echo "⏹️  Parando serviço privacy..."
systemctl stop privacy 2>/dev/null || true

# 2. Verificar se o diretório existe
if [ ! -d "/opt/privacy" ]; then
    echo "❌ Diretório /opt/privacy não encontrado!"
    exit 1
fi

cd /opt/privacy

# 3. Verificar se o ambiente virtual existe
if [ ! -d "venv" ]; then
    echo "📦 Criando ambiente virtual..."
    python3 -m venv venv
fi

# 4. Ativar ambiente virtual e instalar dependências
echo "📦 Instalando dependências..."
source venv/bin/activate

# Atualizar pip
pip install --upgrade pip

# Instalar dependências básicas
pip install gunicorn flask

# 5. Verificar se o arquivo web_interface.py existe
if [ ! -f "web_interface.py" ]; then
    echo "❌ Arquivo web_interface.py não encontrado!"
    echo "📄 Criando arquivo web_interface.py básico..."
    
    cat > web_interface.py << 'EOF'
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Interface web para o sistema de privacidade LGPD
"""

from flask import Flask, render_template, jsonify, request
import os
import sqlite3
from datetime import datetime

app = Flask(__name__)

@app.route('/')
def dashboard():
    """Dashboard principal"""
    return render_template('dashboard.html')

@app.route('/health')
def health():
    """Endpoint de saúde da aplicação"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'version': '1.0.0'
    })

@app.route('/api/stats')
def get_stats():
    """Estatísticas básicas"""
    try:
        conn = sqlite3.connect('lgpd_data.db')
        cursor = conn.cursor()
        
        # Contar dados extraídos
        cursor.execute("SELECT COUNT(*) FROM dados_extraidos")
        total_dados = cursor.fetchone()[0]
        
        # Contar arquivos processados
        cursor.execute("SELECT COUNT(DISTINCT arquivo) FROM dados_extraidos")
        total_arquivos = cursor.fetchone()[0]
        
        conn.close()
        
        return jsonify({
            'total_dados': total_dados,
            'total_arquivos': total_arquivos,
            'status': 'success'
        })
    except Exception as e:
        return jsonify({
            'error': str(e),
            'status': 'error'
        }), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
EOF
fi

# 6. Verificar se o diretório templates existe
if [ ! -d "templates" ]; then
    echo "📁 Criando diretório templates..."
    mkdir -p templates
fi

# 7. Criar template básico se não existir
if [ ! -f "templates/dashboard.html" ]; then
    echo "📄 Criando template dashboard básico..."
    
    cat > templates/dashboard.html << 'EOF'
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>n.crisisops - Módulo de Privacidade</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; }
        .header { background: #f0f0f0; padding: 20px; border-radius: 5px; }
        .status { padding: 10px; margin: 10px 0; border-radius: 5px; }
        .success { background: #d4edda; color: #155724; }
        .error { background: #f8d7da; color: #721c24; }
    </style>
</head>
<body>
    <div class="header">
        <h1>n.crisisops - Módulo de Privacidade</h1>
        <p>Sistema de análise e conformidade LGPD</p>
    </div>
    
    <div class="status success">
        ✅ Sistema funcionando corretamente
    </div>
    
    <h2>Estatísticas</h2>
    <div id="stats">Carregando...</div>
    
    <script>
        fetch('/api/stats')
            .then(response => response.json())
            .then(data => {
                if (data.status === 'success') {
                    document.getElementById('stats').innerHTML = `
                        <p><strong>Total de dados encontrados:</strong> ${data.total_dados}</p>
                        <p><strong>Arquivos processados:</strong> ${data.total_arquivos}</p>
                    `;
                } else {
                    document.getElementById('stats').innerHTML = '<p>Erro ao carregar estatísticas</p>';
                }
            })
            .catch(error => {
                document.getElementById('stats').innerHTML = '<p>Erro de conexão</p>';
            });
    </script>
</body>
</html>
EOF
fi

# 8. Verificar permissões
echo "🔐 Ajustando permissões..."
chown -R privacy:privacy /opt/privacy
chmod -R 755 /opt/privacy

# 9. Recarregar systemd
echo "🔄 Recarregando systemd..."
systemctl daemon-reload

# 10. Iniciar serviço
echo "🚀 Iniciando serviço privacy..."
systemctl start privacy

# 11. Aguardar e verificar status
echo "⏳ Aguardando inicialização..."
sleep 5

echo "📊 Status do serviço:"
systemctl status privacy --no-pager

# 12. Testar endpoint de saúde
echo "🏥 Testando endpoint de saúde..."
if curl -f http://localhost:5000/health > /dev/null 2>&1; then
    echo "✅ Serviço funcionando corretamente!"
    echo "🌐 Acesse: http://localhost:5000"
else
    echo "❌ Serviço não está respondendo"
    echo "📋 Verificando logs..."
    journalctl -u privacy -n 20 --no-pager
fi

echo "✅ Correção concluída!" 