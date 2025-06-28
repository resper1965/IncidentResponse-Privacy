#!/bin/bash

# Install only PyMuPDF to fix the fitz import error
echo "📦 Installing PyMuPDF to fix fitz import error..."

cd /opt/privacy

# Stop the service
systemctl stop privacy

# Activate virtual environment and install PyMuPDF
source venv/bin/activate
pip install PyMuPDF==1.23.8
deactivate

# Test the import
echo "🧪 Testing fitz import..."
sudo -u privacy /opt/privacy/venv/bin/python3 -c "
import sys
sys.path.insert(0, '/opt/privacy')
try:
    import fitz
    print('✅ fitz (PyMuPDF) imported successfully')
    print(f'PyMuPDF version: {fitz.version[0]}')
except Exception as e:
    print(f'❌ fitz import failed: {e}')
"

# Start the service
systemctl start privacy

# Wait for startup
sleep 10

# Test the connection
echo "🧪 Testing HTTPS connection..."
curl -I https://monster.e-ness.com.br

echo "✅ PyMuPDF installation completed!"