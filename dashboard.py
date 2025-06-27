#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Dashboard Streamlit para visualização dos dados extraídos
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
    backup_banco
)

# Configuração da página
st.set_page_config(
    page_title="LGPD Compliance Dashboard",
    page_icon="🔐",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS customizado para melhor aparência
st.markdown("""
<style>
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #ff6b6b;
    }
    .priority-high {
        background-color: #ffebee;
        border-left: 4px solid #f44336;
    }
    .priority-low {
        background-color: #e8f5e8;
        border-left: 4px solid #4caf50;
    }
    .stDataFrame {
        border: 1px solid #ddd;
    }
</style>
""", unsafe_allow_html=True)

def main():
    """
    Interface principal do dashboard
    """
    st.title("🔐 LGPD Compliance Dashboard")
    st.markdown("---")
    
    # Sidebar com controles
    with st.sidebar:
        st.header("🎛️ Controles")
        
        # Botão para atualizar dados
        if st.button("🔄 Atualizar Dados", type="primary"):
            st.rerun()
        
        st.markdown("---")
        
        # Filtros
        st.subheader("🔍 Filtros")
        
        # Filtro por origem de identificação
        origem_opcoes = ["Todos", "regex", "ia_spacy", "nao_identificado"]
        filtro_origem = st.selectbox(
            "Origem da Identificação:",
            origem_opcoes,
            index=0
        )
        
        # Filtro por prioridade
        prioridade_opcoes = ["Todas", "Alta", "Baixa"]
        filtro_prioridade = st.selectbox(
            "Prioridade:",
            prioridade_opcoes,
            index=0
        )
        
        st.markdown("---")
        
        # Ferramentas administrativas
        st.subheader("🛠️ Ferramentas")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("💾 Backup"):
                if backup_banco():
                    st.success("✅ Backup criado!")
                else:
                    st.error("❌ Erro no backup")
        
        with col2:
            if st.button("🗑️ Limpar", type="secondary"):
                if st.session_state.get('confirmar_limpeza', False):
                    if limpar_dados():
                        st.success("✅ Dados limpos!")
                        st.session_state.confirmar_limpeza = False
                        st.rerun()
                    else:
                        st.error("❌ Erro na limpeza")
                else:
                    st.session_state.confirmar_limpeza = True
                    st.warning("⚠️ Clique novamente para confirmar")
    
    # Obter dados para o dashboard
    stats = obter_estatisticas()
    
    if not stats or stats.get('total_dados', 0) == 0:
        st.warning("⚠️ Nenhum dado encontrado. Execute o pipeline primeiro com: `python main.py`")
        st.info("📋 Adicione arquivos na pasta 'data/' e execute o processamento.")
        return
    
    # Seção de métricas principais
    st.header("📊 Resumo Geral")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="📄 Total de Dados",
            value=f"{stats.get('total_dados', 0):,}",
            delta=None
        )
    
    with col2:
        st.metric(
            label="📁 Arquivos Processados",
            value=stats.get('arquivos_processados', 0),
            delta=None
        )
    
    with col3:
        st.metric(
            label="👥 Titulares Identificados",
            value=stats.get('titulares_identificados', 0),
            delta=None
        )
    
    with col4:
        st.metric(
            label="🚨 Dados Prioritários",
            value=stats.get('dados_alta_prioridade', 0),
            delta=None
        )
    
    st.markdown("---")
    
    # Gráficos de análise
    st.header("📈 Análise Detalhada")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Gráfico de distribuição por tipo de campo
        st.subheader("📊 Distribuição por Tipo de Dado")
        
        if stats.get('distribuicao_campos'):
            df_campos = pd.DataFrame(
                list(stats['distribuicao_campos'].items()),
                columns=['Tipo', 'Quantidade']
            )
            
            fig_campos = px.pie(
                df_campos,
                values='Quantidade',
                names='Tipo',
                title="Tipos de Dados Encontrados"
            )
            fig_campos.update_traces(textposition='inside', textinfo='percent+label')
            st.plotly_chart(fig_campos, use_container_width=True)
        else:
            st.info("Nenhum dado de distribuição disponível")
    
    with col2:
        # Gráfico de origem de identificação
        st.subheader("🔍 Origem da Identificação")
        
        if stats.get('distribuicao_origem'):
            df_origem = pd.DataFrame(
                list(stats['distribuicao_origem'].items()),
                columns=['Origem', 'Quantidade']
            )
            
            # Mapear nomes mais legíveis
            df_origem['Origem'] = df_origem['Origem'].map({
                'regex': 'Regex (Palavras-chave)',
                'ia_spacy': 'IA (spaCy NER)',
                'nao_identificado': 'Não Identificado'
            })
            
            fig_origem = px.bar(
                df_origem,
                x='Origem',
                y='Quantidade',
                title="Métodos de Identificação de Titulares",
                color='Quantidade',
                color_continuous_scale='viridis'
            )
            st.plotly_chart(fig_origem, use_container_width=True)
        else:
            st.info("Nenhum dado de origem disponível")
    
    st.markdown("---")
    
    # Seção de dados prioritários
    st.header("🚨 Dados de Alta Prioridade")
    
    dados_prioritarios = obter_dados_prioritarios()
    
    if dados_prioritarios:
        # Criar DataFrame para melhor visualização
        df_prioritarios = pd.DataFrame(dados_prioritarios)
        
        # Limitar contexto para visualização
        df_prioritarios['contexto_resumido'] = df_prioritarios['contexto'].apply(
            lambda x: x[:100] + "..." if len(x) > 100 else x
        )
        
        # Selecionar colunas para exibição
        colunas_exibicao = [
            'arquivo', 'titular', 'campo', 'valor', 
            'contexto_resumido', 'origem_identificacao'
        ]
        
        st.dataframe(
            df_prioritarios[colunas_exibicao],
            use_container_width=True,
            hide_index=True,
            column_config={
                'arquivo': 'Arquivo',
                'titular': 'Titular',
                'campo': 'Tipo',
                'valor': 'Valor',
                'contexto_resumido': 'Contexto',
                'origem_identificacao': 'Origem ID'
            }
        )
        
        # Botão para download
        csv_prioritarios = df_prioritarios.to_csv(index=False)
        st.download_button(
            label="💾 Download Dados Prioritários (CSV)",
            data=csv_prioritarios,
            file_name=f"dados_prioritarios_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv"
        )
    else:
        st.info("📋 Nenhum dado de alta prioridade encontrado.")
    
    st.markdown("---")
    
    # Seção de todos os dados com filtros
    st.header("📋 Base Completa de Dados")
    
    # Aplicar filtros
    filtro_origem_db = None if filtro_origem == "Todos" else filtro_origem
    todos_dados = obter_todos_dados(filtro_origem_db)
    
    if todos_dados:
        df_todos = pd.DataFrame(todos_dados)
        
        # Filtrar por prioridade se selecionado
        if filtro_prioridade != "Todas":
            df_todos = df_todos[df_todos['prioridade'] == filtro_prioridade]
        
        # Mostrar contador de registros filtrados
        st.info(f"📊 Mostrando {len(df_todos)} de {len(todos_dados)} registros")
        
        if not df_todos.empty:
            # Preparar dados para exibição
            df_exibicao = df_todos.copy()
            df_exibicao['contexto_resumido'] = df_exibicao['contexto'].apply(
                lambda x: x[:80] + "..." if len(x) > 80 else x
            )
            
            # Configurar cores por prioridade
            def colorir_prioridade(val):
                if val == 'Alta':
                    return 'background-color: #ffebee'
                else:
                    return 'background-color: #e8f5e8'
            
            # Selecionar colunas para exibição
            colunas_principais = [
                'arquivo', 'titular', 'campo', 'valor', 
                'prioridade', 'origem_identificacao', 'contexto_resumido'
            ]
            
            # Configurar exibição do dataframe
            st.dataframe(
                df_exibicao[colunas_principais],
                use_container_width=True,
                hide_index=True,
                column_config={
                    'arquivo': st.column_config.TextColumn('Arquivo', width='medium'),
                    'titular': st.column_config.TextColumn('Titular', width='medium'),
                    'campo': st.column_config.TextColumn('Tipo', width='small'),
                    'valor': st.column_config.TextColumn('Valor', width='medium'),
                    'prioridade': st.column_config.TextColumn('Prioridade', width='small'),
                    'origem_identificacao': st.column_config.TextColumn('Origem', width='small'),
                    'contexto_resumido': st.column_config.TextColumn('Contexto', width='large')
                }
            )
            
            # Botão para download completo
            csv_completo = df_todos.to_csv(index=False)
            st.download_button(
                label="💾 Download Base Completa (CSV)",
                data=csv_completo,
                file_name=f"base_completa_lgpd_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )
        else:
            st.warning("⚠️ Nenhum registro encontrado com os filtros aplicados.")
    else:
        st.info("📋 Nenhum dado encontrado na base.")
    
    # Footer
    st.markdown("---")
    st.markdown(
        """
        <div style='text-align: center; color: #666;'>
            🔐 LGPD Compliance Dashboard | Desenvolvido com Streamlit<br>
            Para processar novos arquivos, execute: <code>python main.py</code>
        </div>
        """,
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()
