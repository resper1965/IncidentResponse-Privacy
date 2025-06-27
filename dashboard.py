#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Dashboard LGPD - Interface profissional baseada em design de analytics
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import os
from database import (
    obter_estatisticas, 
    obter_dados_prioritarios, 
    obter_todos_dados, 
    limpar_dados,
    backup_banco,
    inserir_dado, 
    verificar_prioridade,
    obter_empresas_prioritarias,
    inserir_empresa_prioritaria,
    remover_empresa_prioritaria,
    carregar_empresas_padrao
)
from file_scanner import listar_arquivos_recursivos
from file_reader import extrair_texto
from data_extractor import analisar_texto, inicializar_spacy

# Configuração da página
st.set_page_config(
    page_title="LGPD Compliance Dashboard",
    page_icon="🔐",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS profissional baseado no design de analytics
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    .main {
        font-family: 'Inter', sans-serif;
        background-color: #f8f9fa;
        padding: 0;
    }
    
    /* Header dashboard */
    .dashboard-header {
        background: white;
        padding: 1.5rem 2rem;
        border-bottom: 1px solid #e1e5e9;
        margin-bottom: 1.5rem;
    }
    
    .header-title {
        font-size: 1.375rem;
        font-weight: 600;
        color: #1a1d29;
        margin: 0;
    }
    
    .header-subtitle {
        font-size: 0.875rem;
        color: #6b7280;
        margin: 0.25rem 0 0 0;
    }
    
    /* Cards de métricas - estilo analytics */
    .metrics-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
        gap: 1.5rem;
        margin-bottom: 2rem;
    }
    
    .metric-card {
        background: white;
        padding: 1.5rem;
        border-radius: 8px;
        border: 1px solid #e1e5e9;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
        transition: all 0.2s ease;
    }
    
    .metric-card:hover {
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
        transform: translateY(-1px);
    }
    
    .metric-label {
        font-size: 0.875rem;
        color: #6b7280;
        font-weight: 500;
        margin-bottom: 0.5rem;
        text-transform: uppercase;
        letter-spacing: 0.025em;
    }
    
    .metric-value {
        font-size: 2rem;
        font-weight: 700;
        color: #1a1d29;
        line-height: 1;
        margin-bottom: 0.5rem;
    }
    
    .metric-change {
        font-size: 0.875rem;
        font-weight: 500;
        display: flex;
        align-items: center;
        gap: 0.25rem;
    }
    
    .metric-change.positive {
        color: #059669;
    }
    
    .metric-change.negative {
        color: #dc2626;
    }
    
    .metric-change.neutral {
        color: #6b7280;
    }
    
    /* Seções de conteúdo */
    .content-section {
        background: white;
        border: 1px solid #e1e5e9;
        border-radius: 8px;
        margin-bottom: 1.5rem;
        overflow: hidden;
    }
    
    .section-header {
        padding: 1.25rem 1.5rem;
        border-bottom: 1px solid #e1e5e9;
        background: #f8f9fa;
    }
    
    .section-title {
        font-size: 1.125rem;
        font-weight: 600;
        color: #1a1d29;
        margin: 0;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    
    .section-content {
        padding: 1.5rem;
    }
    
    /* Sidebar personalizada */
    .sidebar-section {
        background: white;
        border: 1px solid #e1e5e9;
        border-radius: 8px;
        margin-bottom: 1rem;
        overflow: hidden;
    }
    
    .sidebar-header {
        padding: 1rem 1.25rem;
        background: #f8f9fa;
        border-bottom: 1px solid #e1e5e9;
        font-weight: 600;
        font-size: 0.875rem;
        color: #374151;
    }
    
    .sidebar-content {
        padding: 1.25rem;
    }
    
    /* Botões estilo analytics */
    .stButton > button {
        background: #3b82f6;
        color: white;
        border: none;
        border-radius: 6px;
        padding: 0.5rem 1rem;
        font-weight: 500;
        font-size: 0.875rem;
        transition: all 0.2s ease;
        box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05);
    }
    
    .stButton > button:hover {
        background: #2563eb;
        box-shadow: 0 4px 8px rgba(59, 130, 246, 0.3);
        transform: translateY(-1px);
    }
    
    /* Selectbox e inputs */
    .stSelectbox > div > div {
        background: white;
        border: 1px solid #d1d5db;
        border-radius: 6px;
        transition: border-color 0.2s ease;
    }
    
    .stSelectbox > div > div:focus-within {
        border-color: #3b82f6;
        box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
    }
    
    .stTextInput > div > div > input {
        background: white;
        border: 1px solid #d1d5db;
        border-radius: 6px;
        padding: 0.5rem 0.75rem;
        transition: border-color 0.2s ease;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: #3b82f6;
        box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
    }
    
    /* Charts container */
    .chart-container {
        background: white;
        border: 1px solid #e1e5e9;
        border-radius: 8px;
        padding: 1.5rem;
        margin-bottom: 1.5rem;
    }
    
    .chart-title {
        font-size: 1rem;
        font-weight: 600;
        color: #1a1d29;
        margin-bottom: 1rem;
    }
    
    /* Tabelas */
    .dataframe {
        border: 1px solid #e1e5e9;
        border-radius: 8px;
        overflow: hidden;
    }
    
    /* Tags de prioridade */
    .priority-tag {
        display: inline-flex;
        align-items: center;
        padding: 0.25rem 0.75rem;
        border-radius: 9999px;
        font-size: 0.75rem;
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 0.025em;
    }
    
    .priority-high {
        background: #fef2f2;
        color: #dc2626;
        border: 1px solid #fecaca;
    }
    
    .priority-low {
        background: #f0f9ff;
        color: #0369a1;
        border: 1px solid #bae6fd;
    }
    
    /* Status indicators */
    .status-badge {
        display: inline-flex;
        align-items: center;
        padding: 0.25rem 0.5rem;
        border-radius: 4px;
        font-size: 0.75rem;
        font-weight: 500;
        gap: 0.25rem;
    }
    
    .status-active {
        background: #dcfce7;
        color: #166534;
    }
    
    .status-inactive {
        background: #fef2f2;
        color: #dc2626;
    }
    
    /* Layout responsivo */
    @media (max-width: 768px) {
        .metrics-grid {
            grid-template-columns: 1fr;
        }
        
        .metric-value {
            font-size: 1.5rem;
        }
        
        .dashboard-header {
            padding: 1rem;
        }
    }
</style>
""", unsafe_allow_html=True)

def executar_pipeline_personalizado(diretorio):
    """Executa pipeline de extração em diretório específico"""
    try:
        inicializar_spacy()
        arquivos = listar_arquivos_recursivos(diretorio)
        
        if not arquivos:
            st.warning(f"Nenhum arquivo encontrado no diretório: {diretorio}")
            return
        
        total_dados = 0
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        for i, arquivo in enumerate(arquivos):
            try:
                status_text.text(f"Processando: {os.path.basename(arquivo)}")
                texto = extrair_texto(arquivo)
                
                if texto.strip():
                    resultados = analisar_texto(texto, arquivo)
                    
                    if resultados:
                        total_dados += len(resultados)
                        
                        for dado in resultados:
                            prioridade = verificar_prioridade(dado['campo'])
                            inserir_dado(
                                arquivo=arquivo,
                                titular=dado['titular'],
                                campo=dado['campo'],
                                valor=dado['valor'],
                                contexto=dado['contexto'],
                                prioridade=prioridade,
                                origem_identificacao=dado['origem_identificacao']
                            )
                
                progress_bar.progress((i + 1) / len(arquivos))
                
            except Exception as e:
                st.error(f"Erro ao processar {arquivo}: {str(e)}")
                continue
        
        status_text.text("Processamento concluído!")
        st.success(f"Pipeline concluído! {total_dados} dados encontrados em {len(arquivos)} arquivos.")
        
    except Exception as e:
        st.error(f"Erro no pipeline: {str(e)}")

def main():
    """Interface principal do dashboard"""
    
    # Header principal
    st.markdown("""
    <div class="dashboard-header">
        <h1 class="header-title">LGPD Compliance Dashboard</h1>
        <p class="header-subtitle">Monitoramento e análise de dados pessoais em conformidade com a LGPD</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        # Controles do sistema
        st.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
        st.markdown('<div class="sidebar-header">Controles do Sistema</div>', unsafe_allow_html=True)
        st.markdown('<div class="sidebar-content">', unsafe_allow_html=True)
        
        if st.button("Atualizar Dashboard", use_container_width=True):
            st.rerun()
        
        st.markdown("</div></div>", unsafe_allow_html=True)
        
        # Configuração de diretório
        st.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
        st.markdown('<div class="sidebar-header">Configuração de Documentos</div>', unsafe_allow_html=True)
        st.markdown('<div class="sidebar-content">', unsafe_allow_html=True)
        
        diretorio_atual = st.session_state.get('diretorio_raiz', 'data')
        
        # Lista diretórios disponíveis
        diretorios_disponiveis = ['data']
        try:
            for item in os.listdir('.'):
                if (os.path.isdir(item) and 
                    not item.startswith('.') and 
                    item not in ['__pycache__', 'node_modules'] and
                    item not in diretorios_disponiveis):
                    diretorios_disponiveis.append(item)
        except:
            pass
        
        diretorio_selecionado = st.selectbox(
            "Diretório Raiz:",
            diretorios_disponiveis,
            index=diretorios_disponiveis.index(diretorio_atual) if diretorio_atual in diretorios_disponiveis else 0
        )
        
        if diretorio_selecionado != diretorio_atual:
            st.session_state.diretorio_raiz = diretorio_selecionado
        
        diretorio_customizado = st.text_input(
            "Caminho personalizado:",
            placeholder="/caminho/para/documentos"
        )
        
        if diretorio_customizado:
            if os.path.exists(diretorio_customizado) and os.path.isdir(diretorio_customizado):
                st.session_state.diretorio_raiz = diretorio_customizado
                st.success("Diretório válido!")
            else:
                st.error("Diretório inválido")
        
        diretorio_final = st.session_state.get('diretorio_raiz', 'data')
        st.info(f"**Diretório ativo:** `{diretorio_final}`")
        
        if st.button("Reprocessar Documentos", use_container_width=True):
            with st.spinner("Processando..."):
                executar_pipeline_personalizado(diretorio_final)
                st.rerun()
        
        st.markdown("</div></div>", unsafe_allow_html=True)
        
        # Filtros
        st.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
        st.markdown('<div class="sidebar-header">Filtros</div>', unsafe_allow_html=True)
        st.markdown('<div class="sidebar-content">', unsafe_allow_html=True)
        
        origem_opcoes = ["Todos", "regex", "ia_spacy", "nao_identificado"]
        filtro_origem = st.selectbox("Origem da Identificação:", origem_opcoes)
        
        prioridade_opcoes = ["Todas", "Alta", "Baixa"]
        filtro_prioridade = st.selectbox("Nível de Prioridade:", prioridade_opcoes)
        
        st.markdown("</div></div>", unsafe_allow_html=True)
        
        # Empresas prioritárias
        st.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
        st.markdown('<div class="sidebar-header">Empresas Prioritárias</div>', unsafe_allow_html=True)
        st.markdown('<div class="sidebar-content">', unsafe_allow_html=True)
        
        if st.button("Carregar Lista Padrão", use_container_width=True):
            carregar_empresas_padrao()
            st.success("Lista carregada!")
            st.rerun()
        
        with st.expander("Adicionar Empresa"):
            nome_empresa = st.text_input("Nome da Empresa:", key="nova_empresa")
            email_contato = st.text_input("Email:", key="novo_email")
            observacoes = st.text_area("Observações:", key="novas_obs", height=100)
            
            if st.button("Adicionar", key="btn_adicionar"):
                if nome_empresa:
                    if inserir_empresa_prioritaria(nome_empresa, observacoes, email_contato):
                        st.success("Empresa adicionada!")
                        st.rerun()
                    else:
                        st.error("Erro ao adicionar")
                else:
                    st.error("Nome obrigatório")
        
        st.markdown("</div></div>", unsafe_allow_html=True)
        
        # Ferramentas administrativas
        st.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
        st.markdown('<div class="sidebar-header">Ferramentas</div>', unsafe_allow_html=True)
        st.markdown('<div class="sidebar-content">', unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("Backup", use_container_width=True):
                if backup_banco():
                    st.success("Backup criado!")
                else:
                    st.error("Erro no backup")
        
        with col2:
            if st.button("Limpar", use_container_width=True):
                if st.session_state.get('confirmar_limpeza', False):
                    if limpar_dados():
                        st.success("Dados limpos!")
                        st.session_state.confirmar_limpeza = False
                        st.rerun()
                    else:
                        st.error("Erro na limpeza")
                else:
                    st.session_state.confirmar_limpeza = True
                    st.warning("Clique novamente para confirmar")
        
        st.markdown("---")
        st.markdown(f"**Última atualização:** {datetime.now().strftime('%d/%m/%Y às %H:%M')}")
        
        st.markdown("</div></div>", unsafe_allow_html=True)
    
    # Obter dados
    stats = obter_estatisticas()
    
    if not stats or stats.get('total_dados', 0) == 0:
        st.warning("Nenhum dado encontrado. Execute o pipeline usando o botão 'Reprocessar Documentos'")
        st.info("Adicione arquivos na pasta selecionada e execute o processamento.")
        return
    
    # Métricas principais - estilo analytics
    st.markdown('<div class="metrics-grid">', unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Total de Dados</div>
            <div class="metric-value">{stats.get('total_dados', 0):,}</div>
            <div class="metric-change positive">↑ Dados encontrados</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Arquivos Processados</div>
            <div class="metric-value">{stats.get('arquivos_processados', 0)}</div>
            <div class="metric-change neutral">• Documentos analisados</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Titulares Identificados</div>
            <div class="metric-value">{stats.get('titulares_identificados', 0)}</div>
            <div class="metric-change positive">↑ Pessoas identificadas</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Dados Prioritários</div>
            <div class="metric-value">{stats.get('dados_alta_prioridade', 0)}</div>
            <div class="metric-change negative">⚠ Requer atenção</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Gráficos de análise
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        st.markdown('<div class="chart-title">Distribuição por Tipo de Dado</div>', unsafe_allow_html=True)
        
        if stats.get('distribuicao_campos'):
            df_campos = pd.DataFrame(
                list(stats['distribuicao_campos'].items()),
                columns=['Tipo', 'Quantidade']
            )
            
            fig_campos = px.pie(
                df_campos,
                values='Quantidade',
                names='Tipo',
                color_discrete_sequence=['#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#06b6d4']
            )
            fig_campos.update_traces(
                textposition='inside', 
                textinfo='percent+label',
                textfont_size=11
            )
            fig_campos.update_layout(
                font=dict(family="Inter, sans-serif", size=12),
                height=350,
                margin=dict(t=20, b=20, l=20, r=20),
                showlegend=True,
                legend=dict(orientation="v", yanchor="middle", y=0.5)
            )
            st.plotly_chart(fig_campos, use_container_width=True)
        else:
            st.info("Nenhum dado disponível")
        
        st.markdown("</div>", unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        st.markdown('<div class="chart-title">Métodos de Identificação de Titulares</div>', unsafe_allow_html=True)
        
        if stats.get('distribuicao_origem'):
            df_origem = pd.DataFrame(
                list(stats['distribuicao_origem'].items()),
                columns=['Origem', 'Quantidade']
            )
            
            # Mapear nomes mais legíveis
            origem_map = {
                'regex': 'Regex (Palavras-chave)',
                'ia_spacy': 'IA (spaCy NER)',
                'nao_identificado': 'Não Identificado'
            }
            df_origem['Origem'] = df_origem['Origem'].map(lambda x: origem_map.get(x, x))
            
            fig_origem = px.bar(
                df_origem,
                x='Origem',
                y='Quantidade',
                color='Quantidade',
                color_continuous_scale=['#dbeafe', '#3b82f6']
            )
            fig_origem.update_layout(
                font=dict(family="Inter, sans-serif", size=12),
                height=350,
                margin=dict(t=20, b=20, l=20, r=20),
                showlegend=False,
                xaxis_title="",
                yaxis_title="Quantidade"
            )
            fig_origem.update_traces(marker_line_width=0)
            st.plotly_chart(fig_origem, use_container_width=True)
        else:
            st.info("Nenhum dado disponível")
        
        st.markdown("</div>", unsafe_allow_html=True)
    
    # Dados prioritários
    st.markdown('<div class="content-section">', unsafe_allow_html=True)
    st.markdown('<div class="section-header"><h3 class="section-title">🚨 Dados de Alta Prioridade</h3></div>', unsafe_allow_html=True)
    st.markdown('<div class="section-content">', unsafe_allow_html=True)
    
    dados_prioritarios = obter_dados_prioritarios()
    
    if dados_prioritarios:
        df_prioritarios = pd.DataFrame(dados_prioritarios)
        
        # Limitar contexto para visualização
        df_prioritarios['contexto_resumido'] = df_prioritarios['contexto'].str[:100] + "..."
        
        st.dataframe(
            df_prioritarios[['arquivo', 'titular', 'campo', 'valor', 'contexto_resumido', 'origem_identificacao']],
            use_container_width=True,
            hide_index=True,
            column_config={
                'arquivo': 'Arquivo',
                'titular': 'Titular',
                'campo': 'Tipo',
                'valor': 'Valor',
                'contexto_resumido': 'Contexto',
                'origem_identificacao': 'Origem'
            }
        )
        
        csv_prioritarios = df_prioritarios.to_csv(index=False)
        st.download_button(
            label="Download Dados Prioritários",
            data=csv_prioritarios,
            file_name=f"dados_prioritarios_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv"
        )
    else:
        st.info("Nenhum dado de alta prioridade encontrado.")
    
    st.markdown("</div></div>", unsafe_allow_html=True)
    
    # Base completa de dados
    st.markdown('<div class="content-section">', unsafe_allow_html=True)
    st.markdown('<div class="section-header"><h3 class="section-title">📋 Base Completa de Dados</h3></div>', unsafe_allow_html=True)
    st.markdown('<div class="section-content">', unsafe_allow_html=True)
    
    # Aplicar filtros
    filtro_origem_db = None if filtro_origem == "Todos" else filtro_origem
    todos_dados = obter_todos_dados(filtro_origem_db)
    
    if todos_dados:
        df_todos = pd.DataFrame(todos_dados)
        
        # Filtrar por prioridade
        if filtro_prioridade != "Todas":
            df_todos = df_todos[df_todos['prioridade'] == filtro_prioridade]
        
        st.info(f"Mostrando {len(df_todos)} de {len(todos_dados)} registros")
        
        if not df_todos.empty:
            # Preparar dados para exibição
            df_exibicao = df_todos.copy()
            df_exibicao['contexto_resumido'] = df_exibicao['contexto'].str[:80] + "..."
            
            st.dataframe(
                df_exibicao[['arquivo', 'titular', 'campo', 'valor', 'prioridade', 'origem_identificacao', 'contexto_resumido']],
                use_container_width=True,
                hide_index=True,
                column_config={
                    'arquivo': 'Arquivo',
                    'titular': 'Titular',
                    'campo': 'Tipo',
                    'valor': 'Valor',
                    'prioridade': 'Prioridade',
                    'origem_identificacao': 'Origem',
                    'contexto_resumido': 'Contexto'
                }
            )
            
            csv_completo = df_todos.to_csv(index=False)
            st.download_button(
                label="Download Base Completa",
                data=csv_completo,
                file_name=f"base_completa_lgpd_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )
        else:
            st.warning("Nenhum registro encontrado com os filtros aplicados.")
    else:
        st.info("Nenhum dado encontrado na base.")
    
    st.markdown("</div></div>", unsafe_allow_html=True)
    
    # Gestão de empresas prioritárias
    st.markdown('<div class="content-section">', unsafe_allow_html=True)
    st.markdown('<div class="section-header"><h3 class="section-title">🏢 Gestão de Empresas Prioritárias</h3></div>', unsafe_allow_html=True)
    st.markdown('<div class="section-content">', unsafe_allow_html=True)
    
    empresas_prioritarias = obter_empresas_prioritarias()
    
    if empresas_prioritarias:
        st.subheader("Lista de Empresas Prioritárias")
        
        for i, empresa in enumerate(empresas_prioritarias):
            with st.expander(f"🏢 {empresa['nome_empresa']}", expanded=False):
                col1, col2, col3 = st.columns([2, 2, 1])
                
                with col1:
                    st.write(f"**Nome:** {empresa['nome_empresa']}")
                    st.write(f"**Email:** {empresa['email_contato']}")
                
                with col2:
                    st.write(f"**Observações:** {empresa['observacoes'] or 'Nenhuma'}")
                    st.write(f"**Criado em:** {empresa['data_criacao'][:10]}")
                
                with col3:
                    if st.button("Remover", key=f"remove_{empresa['id']}"):
                        if remover_empresa_prioritaria(empresa['id']):
                            st.success("Empresa removida!")
                            st.rerun()
                        else:
                            st.error("Erro ao remover")
        
        # Estatísticas das empresas
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Total de Empresas", len(empresas_prioritarias))
        
        with col2:
            empresas_com_email = len([e for e in empresas_prioritarias if e['email_contato']])
            st.metric("Com Email", empresas_com_email)
        
        with col3:
            empresas_com_obs = len([e for e in empresas_prioritarias if e['observacoes']])
            st.metric("Com Observações", empresas_com_obs)
        
        # Download
        csv_empresas = pd.DataFrame(empresas_prioritarias).to_csv(index=False)
        st.download_button(
            label="Download Lista de Empresas",
            data=csv_empresas,
            file_name=f"empresas_prioritarias_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv"
        )
        
    else:
        st.info("Nenhuma empresa prioritária cadastrada. Use o botão 'Carregar Lista Padrão' na barra lateral.")
    
    st.markdown("</div></div>", unsafe_allow_html=True)

if __name__ == "__main__":
    main()