#!/bin/bash

# Update .env.production file on VPS
echo "🔧 Updating .env.production on VPS..."

cd /opt/privacy

# Backup existing .env if it exists
if [ -f .env ]; then
    cp .env .env.backup.$(date +%Y%m%d_%H%M%S)
    echo "📋 Backed up existing .env file"
fi

# Copy .env.production to .env
cp .env.production .env

# Set proper ownership
chown privacy:privacy .env
chmod 600 .env

echo "✅ .env.production copied to .env with secure permissions"

# Check if OpenAI API key is set
if grep -q "OPENAI_API_KEY=$" .env; then
    echo "⚠️  OpenAI API key is empty in .env file"
    echo "📝 Please add your OpenAI API key to /opt/privacy/.env:"
    echo "    OPENAI_API_KEY=your_api_key_here"
else
    echo "✅ OpenAI API key appears to be configured"
fi

# Restart privacy service to load new environment
echo "🔄 Restarting privacy service..."
systemctl restart privacy

# Check service status
sleep 3
if systemctl is-active --quiet privacy; then
    echo "✅ Privacy service restarted successfully"
    echo "🌐 System available at: https://monster.e-ness.com.br"
else
    echo "❌ Privacy service failed to restart"
    echo "📊 Checking service status..."
    systemctl status privacy --no-pager -l
fi

echo "🔧 Environment update completed"