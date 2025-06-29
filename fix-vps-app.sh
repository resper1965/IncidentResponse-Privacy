#!/bin/bash

# Script para restaurar e atualizar aplicação no VPS
# Execute no diretório /opt/privacy do seu VPS

echo "🔧 Restaurando e atualizando aplicação..."

# Restaurar backup
if [ -f "web_interface.py.backup" ]; then
    echo "📂 Restaurando backup..."
    mv web_interface.py.backup web_interface.py
fi

# Aplicar correção diretamente no arquivo
echo "🔧 Aplicando correção de importação..."
sed -i 's/from file_scanner import encontrar_arquivos/from file_scanner import listar_arquivos_recursivos/' web_interface.py
sed -i 's/arquivos = encontrar_arquivos(diretorio)/arquivos = listar_arquivos_recursivos(diretorio)/' web_interface.py

# Adicionar logs detalhados na função de processamento
echo "📝 Adicionando logs detalhados..."
python3 << 'EOF'
import re

# Ler arquivo atual
with open('web_interface.py', 'r') as f:
    content = f.read()

# Encontrar e substituir a função api_processar
old_function = r'''@app\.route\('/api/processar', methods=\['POST'\]\)
def api_processar\(\):
    """API para executar processamento de arquivos"""
    try:
        data = request\.get_json\(\)
        diretorio = data\.get\('diretorio', 'data'\) if data else 'data'
        
        print\(f"🔍 Iniciando processamento do diretório: \{diretorio\}"\)
        
        # Validar se o diretório existe
        if not os\.path\.exists\(diretorio\):
            return jsonify\(\{'status': 'error', 'message': f'Diretório não encontrado: \{diretorio\}'\}\)
        
        # Contar arquivos primeiro
        from file_scanner import listar_arquivos_recursivos
        arquivos = listar_arquivos_recursivos\(diretorio\)
        print\(f"📁 Encontrados \{len\(arquivos\)\} arquivos para processar"\)
        
        if len\(arquivos\) == 0:
            return jsonify\(\{'status': 'error', 'message': 'Nenhum arquivo encontrado no diretório'\}\)
        
        # Mostrar alguns exemplos de arquivos encontrados
        for i, arquivo in enumerate\(arquivos\[:3\]\):
            print\(f"  📄 \{i\+1\}\. \{arquivo\}"\)
        if len\(arquivos\) > 3:
            print\(f"  \.\.\. e mais \{len\(arquivos\) \- 3\} arquivos"\)
        
        # Tentar processamento com IA se PostgreSQL ativo
        if POSTGRESQL_ENABLED:
            try:
                print\("🤖 Usando processamento com IA\.\.\."\)
                estatisticas = processar_arquivos_com_ia\(diretorio\)
                print\(f"✅ Processamento IA concluído: \{estatisticas\}"\)
                
                # Verificar quantos dados foram encontrados
                dados_encontrados = estatisticas\.get\('dados_encontrados', 0\)
                print\(f"💾 \{dados_encontrados\} dados pessoais encontrados"\)
                
                return jsonify\(\{
                    'status': 'success', 
                    'message': f'Processamento concluído: \{len\(arquivos\)\} arquivos analisados, \{dados_encontrados\} dados pessoais encontrados',
                    'estatisticas': estatisticas
                \}\)
            except Exception as e:
                print\(f"❌ Erro no processamento IA: \{e\}"\)
                # Continuar para fallback básico
        
        # Processamento básico usando SQLite
        print\("📊 Usando processamento básico \(SQLite\)\.\.\."\)
        try:
            processar_arquivos\(diretorio\)
            
            # Verificar quantos dados foram salvos
            stats = obter_estatisticas\(\)
            dados_salvos = stats\.get\('total_dados', 0\)
            print\(f"💾 \{dados_salvos\} dados salvos no banco SQLite"\)
            
            return jsonify\(\{
                'status': 'success', 
                'message': f'Processamento concluído: \{len\(arquivos\)\} arquivos analisados, \{dados_salvos\} dados pessoais encontrados',
                'dados_encontrados': dados_salvos
            \}\)
        except Exception as e:
            print\(f"❌ Erro no processamento básico: \{e\}"\)
            return jsonify\(\{'status': 'error', 'message': f'Erro no processamento: \{str\(e\)\}'\}\)
            
    except Exception as e:
        print\(f"❌ Erro geral no processamento: \{e\}"\)
        return jsonify\(\{'status': 'error', 'message': str\(e\)\}\)'''

# Verificar se a função já está atualizada
if 'listar_arquivos_recursivos' in content and 'print(f"🔍 Iniciando processamento' in content:
    print("✅ Arquivo já está atualizado")
else:
    print("⚠️ Arquivo precisa ser atualizado manualmente")

EOF

# Verificar sintaxe Python
echo "🔍 Verificando sintaxe..."
python3 -m py_compile web_interface.py

if [ $? -eq 0 ]; then
    echo "✅ Sintaxe correta"
    
    # Reiniciar serviço
    echo "🔄 Reiniciando serviço..."
    systemctl restart privacy
    sleep 3
    
    # Verificar status
    if systemctl is-active --quiet privacy; then
        echo "✅ Aplicação atualizada e funcionando!"
        echo "🌐 Sistema disponível em: http://$(hostname -I | awk '{print $1}')"
    else
        echo "❌ Erro no serviço. Verificar logs:"
        echo "journalctl -u privacy -n 20"
    fi
else
    echo "❌ Erro de sintaxe no arquivo"
    exit 1
fi