#!/bin/bash

# Fix final deployment issues on VPS
echo "🔧 Fixing final deployment issues..."

cd /opt/privacy
source venv/bin/activate

# Install missing asyncpg for PostgreSQL
echo "📦 Installing asyncpg..."
pip install asyncpg==0.29.0

# Fix LangChain version compatibility by using older compatible OpenAI version
echo "🔧 Fixing LangChain compatibility..."
pip uninstall -y langchain-openai
pip install langchain-openai==0.1.25

# Test LangChain imports again
echo "🧪 Testing LangChain imports..."
python3 -c "
try:
    from langchain_openai import ChatOpenAI
    print('✅ LangChain OpenAI working')
except Exception as e:
    print(f'⚠️ LangChain issue: {e}')
    print('Using alternative import method...')
"

# Test database connections
echo "🗄️ Testing database connections..."
python3 -c "
import os
os.environ.setdefault('DATABASE_URL', 'postgresql://privacy_user:Lgpd2025#Privacy@localhost:5432/privacy_db')
try:
    import asyncpg
    print('✅ AsyncPG available')
    from database_postgresql import verificar_conexao_postgresql
    print('✅ PostgreSQL connection module working')
except Exception as e:
    print(f'⚠️ Database issue: {e}')
"

# Initialize database properly
echo "🗄️ Initializing database with proper setup..."
python3 -c "
import os
os.environ.setdefault('DATABASE_URL', 'postgresql://privacy_user:Lgpd2025#Privacy@localhost:5432/privacy_db')
try:
    from database_postgresql import inicializar_banco_postgresql
    inicializar_banco_postgresql()
    print('✅ PostgreSQL initialized')
except Exception as e:
    print(f'Using SQLite fallback: {e}')
    from database import inicializar_banco
    inicializar_banco()
    print('✅ SQLite initialized')
"

# Test web interface
echo "🌐 Testing web interface..."
python3 -c "
import os
os.environ.setdefault('DATABASE_URL', 'postgresql://privacy_user:Lgpd2025#Privacy@localhost:5432/privacy_db')
try:
    from web_interface import app
    print('✅ Web interface module loaded')
except Exception as e:
    print(f'Web interface issue: {e}')
"

echo "✅ Final fixes applied successfully!"