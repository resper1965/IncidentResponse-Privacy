#!/bin/bash

# Fix PyMuPDF (fitz) module missing on VPS
echo "🔧 Fixing PyMuPDF module on VPS..."

cd /opt/privacy
source venv/bin/activate

# Install PyMuPDF with specific version that works
echo "📦 Installing PyMuPDF..."
pip install PyMuPDF==1.23.8

# Verify installation
echo "🧪 Testing PyMuPDF import..."
python3 -c "
try:
    import fitz
    print('✅ PyMuPDF (fitz) working')
    print(f'Version: {fitz.__version__}')
except Exception as e:
    print(f'❌ Error: {e}')
"

# Test file_reader module
echo "🧪 Testing file_reader module..."
python3 -c "
try:
    from file_reader import extrair_texto
    print('✅ file_reader module working')
except Exception as e:
    print(f'❌ Error: {e}')
"

# Restart the service
echo "🔄 Restarting privacy service..."
systemctl restart privacy

# Test the service
sleep 5
echo "🧪 Testing service after restart..."
curl -I http://localhost:5000

echo "✅ PyMuPDF fix completed!"