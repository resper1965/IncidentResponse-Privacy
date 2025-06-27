#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Interface web simples para visualização dos dados LGPD
Substituto do Streamlit com Flask
"""

from flask import Flask, render_template, request, jsonify, send_file
import pandas as pd
import json
from datetime import datetime
import os
from database import (
    obter_estatisticas,
    obter_resultados_por_dominio,
    obter_resultados_por_empresa,
    obter_dominios_unicos,
    obter_empresas_unicas,
    carregar_empresas_padrao,
    inicializar_banco,
    obter_prioridades_busca,
    inserir_prioridade_busca,
    remover_prioridade_busca,
    carregar_prioridades_padrao,
    obter_regex_patterns,
    inserir_regex_pattern,
    carregar_regex_padrao
)
from main import processar_arquivos

app = Flask(__name__)

@app.route('/')
def dashboard():
    """Página principal do dashboard"""
    return render_template('dashboard.html')

@app.route('/api/estatisticas')
def api_estatisticas():
    """API para obter estatísticas gerais"""
    stats = obter_estatisticas()
    return jsonify(stats)

@app.route('/api/dominios')
def api_dominios():
    """API para obter lista de domínios"""
    dominios = obter_dominios_unicos()
    return jsonify(dominios)

@app.route('/api/empresas')
def api_empresas():
    """API para obter lista de empresas"""
    empresas = obter_empresas_unicas()
    return jsonify(empresas)

@app.route('/api/resultados')
def api_resultados():
    """API para obter resultados com filtros"""
    dominio = request.args.get('dominio')
    empresa = request.args.get('empresa')
    
    if dominio and dominio != 'todos':
        resultados = obter_resultados_por_dominio(dominio)
    elif empresa and empresa != 'todos':
        resultados = obter_resultados_por_empresa(empresa)
    else:
        resultados = obter_resultados_por_dominio()
    
    return jsonify(resultados)

@app.route('/api/processar', methods=['POST'])
def api_processar():
    """API para executar processamento de arquivos"""
    try:
        data = request.get_json()
        diretorio = data.get('diretorio', 'data') if data else 'data'
        
        # Validar se o diretório existe
        if not os.path.exists(diretorio):
            return jsonify({'status': 'error', 'message': f'Diretório não encontrado: {diretorio}'})
        
        processar_arquivos(diretorio)
        return jsonify({'status': 'success', 'message': 'Processamento concluído'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})

@app.route('/api/status-processamento')
def api_status_processamento():
    """API para obter status do processamento em tempo real"""
    # Por enquanto retorna status simples, pode ser expandido com WebSockets
    return jsonify({
        'processando': False,
        'arquivo_atual': '',
        'progresso': 0,
        'total_arquivos': 0
    })

@app.route('/api/carregar-empresas', methods=['POST'])
def api_carregar_empresas():
    """API para carregar empresas padrão"""
    try:
        carregar_empresas_padrao()
        return jsonify({'status': 'success', 'message': 'Empresas carregadas'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})

@app.route('/api/export-excel')
def api_export_excel():
    """API para exportar dados em Excel"""
    try:
        dominio = request.args.get('dominio')
        empresa = request.args.get('empresa')
        
        if dominio and dominio != 'todos':
            resultados = obter_resultados_por_dominio(dominio)
        elif empresa and empresa != 'todos':
            resultados = obter_resultados_por_empresa(empresa)
        else:
            resultados = obter_resultados_por_dominio()
        
        if not resultados:
            return jsonify({'status': 'error', 'message': 'Nenhum dado para exportar'})
        
        # Criar DataFrame
        df = pd.DataFrame(resultados)
        
        # Definir colunas na ordem desejada
        colunas_ordenadas = [
            'dominio', 'empresa', 'tipo_dado', 'valor_encontrado',
            'arquivo_origem', 'titular_identificado', 'metodo_identificacao',
            'prioridade', 'contexto', 'data_analise', 'status_compliance'
        ]
        
        df = df[colunas_ordenadas]
        
        # Renomear colunas para português
        df.columns = [
            'Domínio', 'Empresa', 'Tipo de Dado', 'Valor Encontrado',
            'Arquivo de Origem', 'Titular Identificado', 'Método de Identificação',
            'Prioridade', 'Contexto', 'Data da Análise', 'Status de Compliance'
        ]
        
        # Salvar Excel
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'matriz_dados_lgpd_{timestamp}.xlsx'
        
        df.to_excel(filename, index=False, sheet_name='Dados LGPD')
        
        return send_file(filename, as_attachment=True, download_name=filename)
        
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})

# === PRIORIDADE DE BUSCA APIs ===

@app.route('/api/prioridades-busca')
def api_prioridades_busca():
    """API para obter lista de prioridades de busca"""
    prioridades = obter_prioridades_busca()
    return jsonify(prioridades)

@app.route('/api/prioridades-busca', methods=['POST'])
def api_adicionar_prioridade():
    """API para adicionar nova prioridade de busca"""
    try:
        data = request.get_json()
        prioridade = data.get('prioridade')
        nome_empresa = data.get('nome_empresa')
        dominio_email = data.get('dominio_email')
        
        if not all([prioridade, nome_empresa, dominio_email]):
            return jsonify({'status': 'error', 'message': 'Todos os campos são obrigatórios'})
        
        sucesso = inserir_prioridade_busca(prioridade, nome_empresa, dominio_email)
        
        if sucesso:
            return jsonify({'status': 'success', 'message': 'Prioridade adicionada com sucesso'})
        else:
            return jsonify({'status': 'error', 'message': 'Erro ao adicionar prioridade'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})

@app.route('/api/prioridades-busca/<int:prioridade_id>', methods=['DELETE'])
def api_remover_prioridade(prioridade_id):
    """API para remover prioridade de busca"""
    try:
        sucesso = remover_prioridade_busca(prioridade_id)
        
        if sucesso:
            return jsonify({'status': 'success', 'message': 'Prioridade removida com sucesso'})
        else:
            return jsonify({'status': 'error', 'message': 'Erro ao remover prioridade'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})

@app.route('/api/carregar-prioridades-padrao', methods=['POST'])
def api_carregar_prioridades_padrao():
    """API para carregar prioridades padrão"""
    try:
        carregar_prioridades_padrao()
        return jsonify({'status': 'success', 'message': 'Prioridades padrão carregadas'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})

# === REGEX PATTERNS APIs ===

@app.route('/api/regex-patterns')
def api_regex_patterns():
    """API para obter lista de padrões regex"""
    patterns = obter_regex_patterns()
    return jsonify(patterns)

@app.route('/api/regex-patterns', methods=['POST'])
def api_adicionar_regex():
    """API para adicionar novo padrão regex"""
    try:
        data = request.get_json()
        nome_campo = data.get('nome_campo')
        pattern_regex = data.get('pattern_regex')
        explicacao = data.get('explicacao', '')
        
        if not all([nome_campo, pattern_regex]):
            return jsonify({'status': 'error', 'message': 'Nome do campo e padrão são obrigatórios'})
        
        sucesso = inserir_regex_pattern(nome_campo, pattern_regex, explicacao)
        
        if sucesso:
            return jsonify({'status': 'success', 'message': 'Padrão regex adicionado com sucesso'})
        else:
            return jsonify({'status': 'error', 'message': 'Erro ao adicionar padrão regex'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})

@app.route('/api/carregar-regex-padrao', methods=['POST'])
def api_carregar_regex_padrao():
    """API para carregar padrões regex padrão"""
    try:
        carregar_regex_padrao()
        return jsonify({'status': 'success', 'message': 'Padrões regex padrão carregados'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})

if __name__ == '__main__':
    # Inicializar banco de dados
    inicializar_banco()
    
    # Verificar se existe pasta templates
    if not os.path.exists('templates'):
        os.makedirs('templates')
    
    app.run(host='0.0.0.0', port=5000, debug=True)