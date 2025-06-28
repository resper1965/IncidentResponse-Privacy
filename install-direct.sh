#!/bin/bash

# Instalação direta das dependências sem pip-tools
# Execute este comando no VPS para resolver o conflito definitivamente

echo "🔧 Instalando dependências com versões específicas compatíveis..."

cd /opt/privacy
source venv/bin/activate

# Desinstalar versões conflitantes se existirem
pip uninstall -y langchain langchain-core langchain-community langchain-text-splitters langchain-openai

# Instalar em ordem específica para evitar conflitos
echo "📦 Instalando LangChain Core..."
pip install langchain-core==0.2.43

echo "📦 Instalando Text Splitters..."
pip install langchain-text-splitters==0.2.4

echo "📦 Instalando LangChain Community..."
pip install langchain-community==0.2.17

echo "📦 Instalando LangChain Base..."
pip install langchain==0.2.17

echo "📦 Instalando LangChain OpenAI..."
pip install langchain-openai==0.2.17

# Testar importações
echo "🧪 Testando importações..."
python3 -c "
from langchain_openai import ChatOpenAI
from langchain_community.document_loaders import TextLoader
from langchain.text_splitter import CharacterTextSplitter
from langchain_core.messages import HumanMessage
print('✅ Todas as importações LangChain funcionando')
"

if [ $? -eq 0 ]; then
    echo "🎉 Dependências LangChain instaladas com sucesso!"
    echo "📋 Sistema pronto para continuar o deploy"
else
    echo "❌ Erro nas importações LangChain"
fi

echo "🔄 Continuando com o deploy..."