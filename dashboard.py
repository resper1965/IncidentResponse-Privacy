#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Dashboard Streamlit elegante para visualização dos dados extraídos
Interface principal para análise de compliance LGPD
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

# CSS elegante e moderno
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    .main {
        font-family: 'Inter', sans-serif;
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        min-height: 100vh;
    }
    
    /* Header principal */
    .hero-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 3rem 2rem;
        border-radius: 1.5rem;
        margin-bottom: 2rem;
        color: white;
        text-align: center;
        box-shadow: 0 20px 40px rgba(102, 126, 234, 0.3);
        position: relative;
        overflow: hidden;
    }
    
    .hero-header::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><defs><pattern id="grain" width="100" height="100" patternUnits="userSpaceOnUse"><circle cx="25" cy="25" r="2" fill="white" opacity="0.1"/><circle cx="75" cy="75" r="1.5" fill="white" opacity="0.08"/><circle cx="50" cy="10" r="1" fill="white" opacity="0.06"/></pattern></defs><rect width="100" height="100" fill="url(%23grain)"/></svg>');
        pointer-events: none;
    }
    
    .hero-title {
        font-size: 3rem;
        font-weight: 700;
        margin-bottom: 1rem;
        text-shadow: 0 4px 8px rgba(0,0,0,0.3);
        position: relative;
        z-index: 1;
    }
    
    .hero-subtitle {
        font-size: 1.2rem;
        opacity: 0.95;
        font-weight: 300;
        position: relative;
        z-index: 1;
    }
    
    /* Cards de métricas modernos */
    .metrics-container {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
        gap: 1.5rem;
        margin: 2rem 0;
    }
    
    .metric-card {
        background: white;
        padding: 2rem 1.5rem;
        border-radius: 1.25rem;
        box-shadow: 0 8px 32px rgba(0,0,0,0.12);
        border: none;
        transition: all 0.3s ease;
        text-align: center;
        position: relative;
        overflow: hidden;
    }
    
    .metric-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 4px;
        background: var(--accent-color, #667eea);
        border-radius: 1.25rem 1.25rem 0 0;
    }
    
    .metric-card:hover {
        transform: translateY(-8px);
        box-shadow: 0 20px 48px rgba(0,0,0,0.2);
    }
    
    .metric-icon {
        font-size: 2.5rem;
        margin-bottom: 1rem;
        opacity: 0.8;
    }
    
    .metric-value {
        font-size: 2.8rem;
        font-weight: 700;
        color: #2c3e50;
        margin-bottom: 0.5rem;
        line-height: 1;
    }
    
    .metric-label {
        font-size: 0.95rem;
        color: #7f8c8d;
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    .metric-change {
        font-size: 0.85rem;
        margin-top: 0.5rem;
        padding: 0.25rem 0.75rem;
        border-radius: 1rem;
        font-weight: 600;
    }
    
    /* Cores específicas para métricas */
    .metric-primary { --accent-color: #3498db; }
    .metric-success { --accent-color: #2ecc71; }
    .metric-warning { --accent-color: #f39c12; }
    .metric-danger { --accent-color: #e74c3c; }
    
    /* Seções elegantes */
    .section-container {
        background: white;
        border-radius: 1.25rem;
        padding: 2rem;
        margin: 2rem 0;
        box-shadow: 0 8px 32px rgba(0,0,0,0.08);
        border: 1px solid rgba(0,0,0,0.05);
    }
    
    .section-header {
        display: flex;
        align-items: center;
        margin-bottom: 1.5rem;
        padding-bottom: 1rem;
        border-bottom: 2px solid #f8f9fa;
    }
    
    .section-title {
        font-size: 1.5rem;
        font-weight: 600;
        color: #2c3e50;
        margin: 0;
        margin-left: 0.5rem;
    }
    
    /* Sidebar elegante */
    .sidebar-section {
        background: white;
        padding: 1.5rem;
        border-radius: 1rem;
        box-shadow: 0 4px 16px rgba(0,0,0,0.08);
        margin-bottom: 1.5rem;
        border: 1px solid rgba(0,0,0,0.05);
    }
    
    .sidebar-title {
        font-size: 1.1rem;
        font-weight: 600;
        color: #2c3e50;
        margin-bottom: 1rem;
        display: flex;
        align-items: center;
    }
    
    /* Botões elegantes */
    .stButton > button {
        background: linear-gradient(135deg, #667eea, #764ba2);
        color: white;
        border: none;
        border-radius: 0.75rem;
        padding: 0.75rem 1.5rem;
        font-weight: 600;
        font-size: 0.9rem;
        transition: all 0.3s ease;
        box-shadow: 0 4px 16px rgba(102, 126, 234, 0.3);
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 24px rgba(102, 126, 234, 0.4);
        background: linear-gradient(135deg, #5a67d8, #6b46c1);
    }
    
    /* Selectbox e inputs elegantes */
    .stSelectbox > div > div {
        background: white;
        border: 2px solid #e2e8f0;
        border-radius: 0.75rem;
        transition: all 0.2s ease;
    }
    
    .stSelectbox > div > div:focus-within {
        border-color: #667eea;
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
    }
    
    .stTextInput > div > div > input {
        background: white;
        border: 2px solid #e2e8f0;
        border-radius: 0.75rem;
        padding: 0.75rem;
        transition: all 0.2s ease;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: #667eea;
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
    }
    
    /* Gráficos modernos */
    .chart-container {
        background: white;
        padding: 2rem;
        border-radius: 1.25rem;
        box-shadow: 0 8px 32px rgba(0,0,0,0.08);
        margin: 1.5rem 0;
        border: 1px solid rgba(0,0,0,0.05);
    }
    
    /* Tabelas elegantes */
    .dataframe {
        border-radius: 1rem;
        overflow: hidden;
        box-shadow: 0 8px 32px rgba(0,0,0,0.08);
        border: 1px solid rgba(0,0,0,0.05);
    }
    
    /* Tags de prioridade */
    .priority-high {
        background: linear-gradient(135deg, #ff6b6b, #ee5a52);
        color: white;
        padding: 0.4rem 1rem;
        border-radius: 2rem;
        font-size: 0.8rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        box-shadow: 0 4px 16px rgba(255, 107, 107, 0.3);
    }
    
    .priority-low {
        background: linear-gradient(135deg, #51cf66, #40c057);
        color: white;
        padding: 0.4rem 1rem;
        border-radius: 2rem;
        font-size: 0.8rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        box-shadow: 0 4px 16px rgba(81, 207, 102, 0.3);
    }
    
    /* Status indicators */
    .status-indicator {
        display: inline-flex;
        align-items: center;
        padding: 0.5rem 1rem;
        border-radius: 2rem;
        font-size: 0.85rem;
        font-weight: 600;
        margin: 0.25rem;
    }
    
    .status-active {
        background: rgba(34, 197, 94, 0.1);
        color: #15803d;
        border: 1px solid rgba(34, 197, 94, 0.2);
    }
    
    .status-inactive {
        background: rgba(239, 68, 68, 0.1);
        color: #dc2626;
        border: 1px solid rgba(239, 68, 68, 0.2);
    }
    
    /* Animações */
    @keyframes fadeInUp {
        from {
            opacity: 0;
            transform: translateY(30px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    .fade-in {
        animation: fadeInUp 0.6s ease-out;
    }
    
    /* Footer elegante */
    .footer {
        background: linear-gradient(135deg, #f8f9fa, #e9ecef);
        padding: 2rem;
        border-radius: 1.25rem;
        text-align: center;
        margin-top: 3rem;
        border-top: 4px solid #667eea;
        box-shadow: 0 -8px 32px rgba(0,0,0,0.08);
    }
    
    /* Responsivo */
    @media (max-width: 768px) {
        .hero-title { font-size: 2.5rem; }
        .metric-value { font-size: 2.2rem; }
        .metrics-container { grid-template-columns: 1fr; }
    }
</style>
""", unsafe_allow_html=True)

def executar_pipeline_personalizado(diretorio):
    """Executa o pipeline de extração em diretório específico"""
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
    
    # Header principal elegante
    st.markdown("""
    <div class="hero-header fade-in">
        <h1 class="hero-title">🔐 LGPD Compliance Dashboard</h1>
        <p class="hero-subtitle">Sistema Inteligente de Monitoramento e Análise de Dados Pessoais</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar elegante
    with st.sidebar:
        # Controles do sistema
        st.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
        st.markdown('<div class="sidebar-title">🎛️ Controles do Sistema</div>', unsafe_allow_html=True)
        
        if st.button("🔄 Atualizar Dados", use_container_width=True):
            st.rerun()
        
        st.markdown("</div>", unsafe_allow_html=True)
        
        # Configuração de diretório
        st.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
        st.markdown('<div class="sidebar-title">📁 Configuração de Documentos</div>', unsafe_allow_html=True)
        
        # Diretório atual
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
        
        # Seleção de diretório
        diretorio_selecionado = st.selectbox(
            "🗂️ Diretório Raiz:",
            diretorios_disponiveis,
            index=diretorios_disponiveis.index(diretorio_atual) if diretorio_atual in diretorios_disponiveis else 0,
            help="Selecione o diretório raiz para escaneamento"
        )
        
        if diretorio_selecionado != diretorio_atual:
            st.session_state.diretorio_raiz = diretorio_selecionado
        
        # Campo customizado
        diretorio_customizado = st.text_input(
            "📝 Caminho personalizado:",
            placeholder="/caminho/para/documentos",
            help="Digite um caminho personalizado"
        )
        
        if diretorio_customizado:
            if os.path.exists(diretorio_customizado) and os.path.isdir(diretorio_customizado):
                st.session_state.diretorio_raiz = diretorio_customizado
                st.success("Diretório válido!")
            else:
                st.error("Diretório inválido")
        
        # Status do diretório
        diretorio_final = st.session_state.get('diretorio_raiz', 'data')
        st.info(f"📂 **Ativo:** `{diretorio_final}`")
        
        # Reprocessar
        if st.button("🔄 Reprocessar Documentos", use_container_width=True):
            with st.spinner("Processando..."):
                executar_pipeline_personalizado(diretorio_final)
                st.rerun()
        
        st.markdown("</div>", unsafe_allow_html=True)
        
        # Filtros
        st.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
        st.markdown('<div class="sidebar-title">🔍 Filtros Avançados</div>', unsafe_allow_html=True)
        
        origem_opcoes = ["Todos", "regex", "ia_spacy", "nao_identificado"]
        filtro_origem = st.selectbox(
            "🎯 Origem da Identificação:",
            origem_opcoes,
            help="Filtrar por método de identificação"
        )
        
        prioridade_opcoes = ["Todas", "Alta", "Baixa"]
        filtro_prioridade = st.selectbox(
            "⚡ Nível de Prioridade:",
            prioridade_opcoes,
            help="Filtrar por classificação de risco"
        )
        
        st.markdown("</div>", unsafe_allow_html=True)
        
        # Seção de empresas prioritárias
        st.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
        st.markdown('<div class="sidebar-title">🏢 Empresas Prioritárias</div>', unsafe_allow_html=True)
        
        # Carregar empresas padrão se necessário
        if st.button("📋 Carregar Lista Padrão", use_container_width=True):
            carregar_empresas_padrao()
            st.success("Lista padrão carregada!")
            st.rerun()
        
        # Adicionar nova empresa
        with st.expander("➕ Adicionar Empresa"):
            nome_empresa = st.text_input("Nome da Empresa:", key="nova_empresa")
            email_contato = st.text_input("Email de Contato:", key="novo_email")
            observacoes = st.text_area("Observações:", key="novas_obs", height=80)
            
            if st.button("Adicionar", key="btn_adicionar"):
                if nome_empresa:
                    if inserir_empresa_prioritaria(nome_empresa, observacoes, email_contato):
                        st.success("Empresa adicionada!")
                        st.rerun()
                    else:
                        st.error("Erro ao adicionar empresa")
                else:
                    st.error("Nome da empresa é obrigatório")
        
        st.markdown("</div>", unsafe_allow_html=True)
        
        # Ferramentas administrativas
        st.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
        st.markdown('<div class="sidebar-title">🛠️ Ferramentas Admin</div>', unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("💾 Backup", use_container_width=True):
                if backup_banco():
                    st.success("Backup criado!")
                else:
                    st.error("Erro no backup")
        
        with col2:
            if st.button("🗑️ Limpar", use_container_width=True):
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
        
        # Info do sistema
        st.markdown("---")
        st.markdown("**📊 Última atualização:**")
        st.markdown(f"*{datetime.now().strftime('%d/%m/%Y às %H:%M')}*")
        
        st.markdown("</div>", unsafe_allow_html=True)
    
    # Obter dados
    stats = obter_estatisticas()
    
    if not stats or stats.get('total_dados', 0) == 0:
        st.warning("⚠️ Nenhum dado encontrado. Execute o pipeline primeiro com o botão 'Reprocessar Documentos'")
        st.info("📋 Adicione arquivos na pasta selecionada e execute o processamento.")
        return
    
    # Métricas principais
    st.markdown('<div class="metrics-container">', unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class="metric-card metric-primary fade-in">
            <div class="metric-icon">📄</div>
            <div class="metric-value">{stats.get('total_dados', 0):,}</div>
            <div class="metric-label">Total de Dados</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="metric-card metric-success fade-in">
            <div class="metric-icon">📁</div>
            <div class="metric-value">{stats.get('arquivos_processados', 0)}</div>
            <div class="metric-label">Arquivos Processados</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="metric-card metric-warning fade-in">
            <div class="metric-icon">👥</div>
            <div class="metric-value">{stats.get('titulares_identificados', 0)}</div>
            <div class="metric-label">Titulares Identificados</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div class="metric-card metric-danger fade-in">
            <div class="metric-icon">🚨</div>
            <div class="metric-value">{stats.get('dados_alta_prioridade', 0)}</div>
            <div class="metric-label">Dados Prioritários</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Gráficos de análise
    st.markdown('<div class="section-container fade-in">', unsafe_allow_html=True)
    st.markdown('<div class="section-header"><span style="font-size: 1.5rem;">📈</span><h2 class="section-title">Análise Detalhada</h2></div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        st.subheader("📊 Distribuição por Tipo")
        
        if stats.get('distribuicao_campos'):
            df_campos = pd.DataFrame(
                list(stats['distribuicao_campos'].items()),
                columns=['Tipo', 'Quantidade']
            )
            
            fig_campos = px.pie(
                df_campos,
                values='Quantidade',
                names='Tipo',
                color_discrete_sequence=px.colors.qualitative.Set3
            )
            fig_campos.update_traces(
                textposition='inside', 
                textinfo='percent+label',
                textfont_size=12
            )
            fig_campos.update_layout(
                font=dict(family="Inter, sans-serif"),
                height=400,
                margin=dict(t=50, b=50, l=50, r=50)
            )
            st.plotly_chart(fig_campos, use_container_width=True)
        else:
            st.info("Nenhum dado disponível")
        
        st.markdown("</div>", unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        st.subheader("🔍 Métodos de Identificação")
        
        if stats.get('distribuicao_origem'):
            df_origem = pd.DataFrame(
                list(stats['distribuicao_origem'].items()),
                columns=['Origem', 'Quantidade']
            )
            
            # Mapear nomes
            origem_map = {
                'regex': 'Regex (Palavras-chave)',
                'ia_spacy': 'IA (spaCy NER)',
                'nao_identificado': 'Não Identificado'
            }
            df_origem['Origem'] = df_origem['Origem'].map(origem_map)
            
            fig_origem = px.bar(
                df_origem,
                x='Origem',
                y='Quantidade',
                color='Quantidade',
                color_continuous_scale='viridis'
            )
            fig_origem.update_layout(
                font=dict(family="Inter, sans-serif"),
                height=400,
                margin=dict(t=50, b=50, l=50, r=50),
                showlegend=False
            )
            st.plotly_chart(fig_origem, use_container_width=True)
        else:
            st.info("Nenhum dado disponível")
        
        st.markdown("</div>", unsafe_allow_html=True)
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Dados prioritários
    st.markdown('<div class="section-container fade-in">', unsafe_allow_html=True)
    st.markdown('<div class="section-header"><span style="font-size: 1.5rem;">🚨</span><h2 class="section-title">Dados de Alta Prioridade</h2></div>', unsafe_allow_html=True)
    
    dados_prioritarios = obter_dados_prioritarios()
    
    if dados_prioritarios:
        df_prioritarios = pd.DataFrame(dados_prioritarios)
        
        # Limitar contexto
        df_prioritarios['contexto_resumido'] = df_prioritarios['contexto'].apply(
            lambda x: x[:100] + "..." if len(x) > 100 else x
        )
        
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
        
        # Download
        csv_prioritarios = df_prioritarios.to_csv(index=False)
        st.download_button(
            label="💾 Download Dados Prioritários",
            data=csv_prioritarios,
            file_name=f"dados_prioritarios_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv"
        )
    else:
        st.info("📋 Nenhum dado de alta prioridade encontrado.")
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Base completa
    st.markdown('<div class="section-container fade-in">', unsafe_allow_html=True)
    st.markdown('<div class="section-header"><span style="font-size: 1.5rem;">📋</span><h2 class="section-title">Base Completa de Dados</h2></div>', unsafe_allow_html=True)
    
    # Aplicar filtros
    filtro_origem_db = None if filtro_origem == "Todos" else filtro_origem
    todos_dados = obter_todos_dados(filtro_origem_db)
    
    if todos_dados:
        df_todos = pd.DataFrame(todos_dados)
        
        # Filtrar por prioridade
        if filtro_prioridade != "Todas":
            df_todos = df_todos[df_todos['prioridade'] == filtro_prioridade]
        
        st.info(f"📊 Mostrando {len(df_todos)} de {len(todos_dados)} registros")
        
        if not df_todos.empty:
            # Preparar dados
            df_exibicao = df_todos.copy()
            df_exibicao['contexto_resumido'] = df_exibicao['contexto'].apply(
                lambda x: x[:80] + "..." if len(x) > 80 else x
            )
            
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
            
            # Download completo
            csv_completo = df_todos.to_csv(index=False)
            st.download_button(
                label="💾 Download Base Completa",
                data=csv_completo,
                file_name=f"base_completa_lgpd_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )
        else:
            st.warning("⚠️ Nenhum registro encontrado com os filtros aplicados.")
    else:
        st.info("📋 Nenhum dado encontrado na base.")
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Gestão de empresas prioritárias
    st.markdown('<div class="section-container fade-in">', unsafe_allow_html=True)
    st.markdown('<div class="section-header"><span style="font-size: 1.5rem;">🏢</span><h2 class="section-title">Gestão de Empresas Prioritárias</h2></div>', unsafe_allow_html=True)
    
    # Obter empresas prioritárias
    empresas_prioritarias = obter_empresas_prioritarias()
    
    if empresas_prioritarias:
        # Criar DataFrame das empresas
        df_empresas = pd.DataFrame(empresas_prioritarias)
        
        # Mostrar tabela com opções de edição
        st.subheader("📋 Lista de Empresas Prioritárias")
        
        # Exibir dados da empresa em formato editável
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
                    if st.button("🗑️ Remover", key=f"remove_{empresa['id']}"):
                        if remover_empresa_prioritaria(empresa['id']):
                            st.success("Empresa removida!")
                            st.rerun()
                        else:
                            st.error("Erro ao remover")
        
        # Estatísticas das empresas
        st.subheader("📊 Estatísticas")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Total de Empresas", len(empresas_prioritarias))
        
        with col2:
            empresas_com_email = len([e for e in empresas_prioritarias if e['email_contato']])
            st.metric("Com Email Configurado", empresas_com_email)
        
        with col3:
            empresas_com_obs = len([e for e in empresas_prioritarias if e['observacoes']])
            st.metric("Com Observações", empresas_com_obs)
        
        # Download da lista
        csv_empresas = pd.DataFrame(empresas_prioritarias).to_csv(index=False)
        st.download_button(
            label="💾 Download Lista de Empresas",
            data=csv_empresas,
            file_name=f"empresas_prioritarias_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv"
        )
        
    else:
        st.info("📋 Nenhuma empresa prioritária cadastrada. Use o botão 'Carregar Lista Padrão' na barra lateral.")
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Footer elegante
    st.markdown("""
    <div class="footer">
        <h3 style="color: #2c3e50; margin-bottom: 1rem;">🔐 LGPD Compliance Dashboard</h3>
        <p style="color: #7f8c8d; margin: 0;">
            Sistema Inteligente de Monitoramento e Análise de Dados Pessoais<br>
            Desenvolvido com Streamlit | Para reprocessar, use o botão na barra lateral
        </p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()