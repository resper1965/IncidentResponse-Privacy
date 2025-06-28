#!/bin/bash

# Fix PostgreSQL and AI services on VPS
echo "🔧 Fixing PostgreSQL and AI services..."

cd /opt/privacy

# Check PostgreSQL service status
echo "📊 Checking PostgreSQL status..."
systemctl status postgresql --no-pager

# Start PostgreSQL if not running
if ! systemctl is-active --quiet postgresql; then
    echo "🔄 Starting PostgreSQL..."
    systemctl start postgresql
    systemctl enable postgresql
fi

# Test PostgreSQL connection
echo "🧪 Testing PostgreSQL connection..."
sudo -u postgres psql -c "SELECT version();" 2>/dev/null || {
    echo "❌ PostgreSQL connection failed"
    echo "🔧 Initializing PostgreSQL..."
    sudo -u postgres initdb -D /var/lib/postgresql/data 2>/dev/null || true
    systemctl restart postgresql
}

# Create database and user if not exists
echo "📋 Setting up database and user..."
sudo -u postgres psql -c "CREATE DATABASE privacy_db;" 2>/dev/null || echo "Database already exists"
sudo -u postgres psql -c "CREATE USER privacy_user WITH PASSWORD 'Lgpd2025#Privacy';" 2>/dev/null || echo "User already exists"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE privacy_db TO privacy_user;" 2>/dev/null
sudo -u postgres psql -c "ALTER USER privacy_user CREATEDB;" 2>/dev/null

# Install missing Python packages
echo "📦 Installing required packages..."
/opt/privacy/venv/bin/pip install asyncpg psycopg2-binary --quiet

# Set environment variables
export DATABASE_URL="postgresql://privacy_user:Lgpd2025#Privacy@localhost:5432/privacy_db"
export PGHOST=localhost
export PGPORT=5432
export PGDATABASE=privacy_db
export PGUSER=privacy_user
export PGPASSWORD="Lgpd2025#Privacy"

# Test database connection with Python
echo "🧪 Testing database connection with Python..."
/opt/privacy/venv/bin/python3 -c "
import asyncio
import asyncpg
import os
from urllib.parse import quote_plus

async def test_connection():
    try:
        # URL encode the password to handle special characters
        password = quote_plus('Lgpd2025#Privacy')
        conn_string = f'postgresql://privacy_user:{password}@localhost:5432/privacy_db'
        conn = await asyncpg.connect(conn_string)
        version = await conn.fetchval('SELECT version()')
        print(f'✅ PostgreSQL connected: {version[:50]}...')
        await conn.close()
        return True
    except Exception as e:
        print(f'❌ Connection failed: {e}')
        return False

result = asyncio.run(test_connection())
exit(0 if result else 1)
"

if [ $? -eq 0 ]; then
    echo "✅ PostgreSQL connection successful"
    
    # Run database merge
    echo "🔄 Running database merge..."
    /opt/privacy/venv/bin/python3 vps-database-merge.py
    
    # Restart privacy service
    echo "🔄 Restarting privacy service..."
    systemctl restart privacy
    
    echo "✅ PostgreSQL and AI services fixed"
else
    echo "❌ PostgreSQL connection still failing"
fi

# Show final status
echo "📊 Final service status:"
systemctl status postgresql --no-pager -l
systemctl status privacy --no-pager -l