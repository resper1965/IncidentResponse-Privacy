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
    inicializar_banco
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
        processar_arquivos()
        return jsonify({'status': 'success', 'message': 'Processamento concluído'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})

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

if __name__ == '__main__':
    # Inicializar banco de dados
    inicializar_banco()
    
    # Verificar se existe pasta templates
    if not os.path.exists('templates'):
        os.makedirs('templates')
    
    app.run(host='0.0.0.0', port=5000, debug=True)