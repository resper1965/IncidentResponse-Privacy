#!/bin/bash

# Teste da API de status com logs detalhados
echo "🧪 Testando API de status com logs..."

cd /opt/privacy

# 1. Testar API e mostrar resposta
echo "📡 Chamando API de status..."
curl -s "http://localhost:5000/api/system-status" | python3 -m json.tool

echo ""
echo "🔍 Verificando logs do Gunicorn..."

# 2. Verificar se o Gunicorn está rodando
ps aux | grep gunicorn | grep -v grep

echo ""
echo "📊 Logs do systemd (últimas 20 linhas)..."
journalctl -u privacy --no-pager -l -n 20

echo ""
echo "🌐 Testando conexão direta no processo..."
/opt/privacy/venv/bin/python3 -c "
import os
import sys
sys.path.append('/opt/privacy')

# Carregar variáveis de ambiente
from dotenv import load_dotenv
load_dotenv('/opt/privacy/.env')

# Testar validação OpenAI
openai_key = os.getenv('OPENAI_API_KEY', '').strip()
print(f'📋 Chave OpenAI: {openai_key[:10]}...{openai_key[-10:] if len(openai_key) > 20 else openai_key}')
print(f'📏 Comprimento: {len(openai_key)}')
print(f'🔑 Começa com sk-: {openai_key.startswith(\"sk-\")}')

ai_status = bool(openai_key and openai_key != '' and openai_key.startswith('sk-'))
print(f'✅ Status IA: {ai_status}')

# Testar PostgreSQL
try:
    import psycopg2
    from urllib.parse import unquote_plus
    
    database_url = os.getenv('DATABASE_URL', '')
    print(f'🗄️  Database URL: {database_url[:30]}...{database_url[-20:]}')
    
    if 'postgresql://' in database_url:
        conn_parts = database_url.replace('postgresql://', '').split('@')
        if len(conn_parts) == 2:
            user_pass = conn_parts[0].split(':')
            host_db = conn_parts[1].split('/')
            if len(user_pass) == 2 and len(host_db) == 2:
                user = user_pass[0]
                password = unquote_plus(user_pass[1])
                host_port = host_db[0].split(':')
                host = host_port[0]
                port = host_port[1] if len(host_port) > 1 else '5432'
                database = host_db[1]
                
                print(f'🔗 Conectando: {user}@{host}:{port}/{database}')
                
                conn = psycopg2.connect(
                    host=host,
                    port=port,
                    database=database,
                    user=user,
                    password=password
                )
                cursor = conn.cursor()
                cursor.execute('SELECT COUNT(*) FROM search_priorities')
                count = cursor.fetchone()[0]
                cursor.close()
                conn.close()
                print(f'✅ PostgreSQL: {count} prioridades encontradas')
            else:
                print('❌ Erro: formato da URL inválido')
        else:
            print('❌ Erro: URL mal formada')
    else:
        print('❌ Erro: não é URL PostgreSQL')
        
except Exception as e:
    print(f'❌ Erro PostgreSQL: {e}')
"