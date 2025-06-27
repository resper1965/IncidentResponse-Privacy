#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Módulo de processamento avançado com IA para LGPD
Implementa classificação inteligente, análise contextual e priorização empresarial
"""

import re
import os
from pathlib import Path
from typing import List, Dict, Tuple, Optional
from file_reader import extrair_texto
from data_extractor import analisar_texto, extrair_contexto
from database import (
    obter_prioridades_busca,
    inserir_resultado_analise,
    extrair_dominio_de_email,
    verificar_prioridade
)

class ProcessadorAvancadoLGPD:
    """
    Processador avançado com IA para análise de documentos LGPD
    Implementa priorização empresarial e classificação inteligente
    """
    
    def __init__(self):
        self.prioridades_empresas = []
        self.estatisticas = {
            'arquivos_processados': 0,
            'dados_encontrados': 0,
            'empresas_identificadas': 0,
            'processamento_por_prioridade': {}
        }
    
    def carregar_prioridades_empresariais(self):
        """Carrega tabela de prioridades empresariais do banco"""
        print("🔄 Carregando prioridades empresariais...")
        self.prioridades_empresas = obter_prioridades_busca()
        
        if self.prioridades_empresas:
            print(f"✅ {len(self.prioridades_empresas)} empresas prioritárias carregadas")
            # Mostrar top 5 empresas
            for i, empresa in enumerate(self.prioridades_empresas[:5], 1):
                print(f"  {empresa['prioridade']}. {empresa['nome_empresa']} (@{empresa['dominio_email']})")
        else:
            print("⚠️  Nenhuma empresa prioritária configurada")
        
        return len(self.prioridades_empresas) > 0
    
    def pre_analisar_arquivo(self, caminho_arquivo: str) -> Dict:
        """
        Pré-análise rápida do arquivo para identificação de empresa
        
        Args:
            caminho_arquivo (str): Caminho do arquivo
            
        Returns:
            Dict: Informações da pré-análise
        """
        try:
            # Extrair texto do arquivo
            texto = extrair_texto(caminho_arquivo)
            if not texto:
                return {'empresa_identificada': None, 'prioridade': 999, 'confianca': 0}
            
            # Analisar por empresa prioritária
            melhor_match = None
            melhor_prioridade = 999
            melhor_confianca = 0
            
            for empresa in self.prioridades_empresas:
                nome_empresa = empresa['nome_empresa']
                dominio = empresa['dominio_email']
                prioridade = empresa['prioridade']
                
                # Critério 1: Nome da empresa no documento
                confianca_nome = self._verificar_nome_empresa(texto, nome_empresa)
                
                # Critério 2: Domínio de email no documento
                confianca_dominio = self._verificar_dominio_empresa(texto, dominio)
                
                # Calcular confiança total
                confianca_total = max(confianca_nome, confianca_dominio)
                
                # Se encontrou match e tem prioridade melhor
                if confianca_total > 0.3 and prioridade < melhor_prioridade:
                    melhor_match = empresa
                    melhor_prioridade = prioridade
                    melhor_confianca = confianca_total
            
            return {
                'empresa_identificada': melhor_match,
                'prioridade': melhor_prioridade,
                'confianca': melhor_confianca,
                'tamanho_texto': len(texto)
            }
            
        except Exception as e:
            print(f"❌ Erro na pré-análise de {caminho_arquivo}: {e}")
            return {'empresa_identificada': None, 'prioridade': 999, 'confianca': 0}
    
    def _verificar_nome_empresa(self, texto: str, nome_empresa: str) -> float:
        """Verifica presença do nome da empresa no texto"""
        texto_upper = texto.upper()
        nome_upper = nome_empresa.upper()
        
        # Busca exata
        if nome_upper in texto_upper:
            return 1.0
        
        # Busca por palavras-chave da empresa
        palavras = nome_upper.split()
        matches = sum(1 for palavra in palavras if palavra in texto_upper)
        
        if matches > 0:
            return matches / len(palavras) * 0.8
        
        return 0.0
    
    def _verificar_dominio_empresa(self, texto: str, dominio: str) -> float:
        """Verifica presença do domínio da empresa no texto"""
        # Buscar emails com o domínio
        pattern_email = rf'\b[a-zA-Z0-9._%+-]+@{re.escape(dominio)}\b'
        matches = re.findall(pattern_email, texto, re.IGNORECASE)
        
        if matches:
            return 1.0
        
        # Buscar apenas o domínio
        if dominio.lower() in texto.lower():
            return 0.6
        
        return 0.0
    
    def classificar_arquivos_por_empresa(self, lista_arquivos: List[str]) -> Dict[int, List]:
        """
        Classifica arquivos por empresa prioritária
        
        Args:
            lista_arquivos (List[str]): Lista de caminhos de arquivos
            
        Returns:
            Dict[int, List]: Arquivos agrupados por prioridade
        """
        print("🔍 Classificando arquivos por empresa prioritária...")
        
        arquivos_por_prioridade = {}
        arquivos_sem_classificacao = []
        
        for arquivo in lista_arquivos:
            print(f"  📄 Analisando: {Path(arquivo).name}")
            
            analise = self.pre_analisar_arquivo(arquivo)
            prioridade = analise['prioridade']
            empresa = analise.get('empresa_identificada')
            
            if empresa:
                print(f"    ✅ Empresa: {empresa['nome_empresa']} (Prioridade {prioridade})")
                
                if prioridade not in arquivos_por_prioridade:
                    arquivos_por_prioridade[prioridade] = []
                
                arquivos_por_prioridade[prioridade].append({
                    'arquivo': arquivo,
                    'empresa': empresa,
                    'confianca': analise['confianca']
                })
            else:
                print(f"    ⚪ Empresa não identificada")
                arquivos_sem_classificacao.append({
                    'arquivo': arquivo,
                    'empresa': None,
                    'confianca': 0
                })
        
        # Adicionar arquivos sem classificação com prioridade baixa
        if arquivos_sem_classificacao:
            arquivos_por_prioridade[999] = arquivos_sem_classificacao
        
        # Estatísticas da classificação
        print(f"\n📊 Classificação concluída:")
        for prioridade in sorted(arquivos_por_prioridade.keys()):
            count = len(arquivos_por_prioridade[prioridade])
            if prioridade == 999:
                print(f"  Não classificados: {count} arquivos")
            else:
                print(f"  Prioridade {prioridade}: {count} arquivos")
        
        return arquivos_por_prioridade
    
    def processar_por_prioridade(self, arquivos_classificados: Dict[int, List]) -> Dict:
        """
        Processa arquivos seguindo ordem de prioridade empresarial
        
        Args:
            arquivos_classificados (Dict): Arquivos agrupados por prioridade
            
        Returns:
            Dict: Estatísticas do processamento
        """
        print("\n🚀 INICIANDO PROCESSAMENTO POR PRIORIDADE")
        
        total_dados_encontrados = 0
        empresas_processadas = set()
        
        # Processar por ordem de prioridade
        for prioridade in sorted(arquivos_classificados.keys()):
            arquivos_grupo = arquivos_classificados[prioridade]
            
            if prioridade == 999:
                print(f"\n📁 Processando arquivos não classificados ({len(arquivos_grupo)} arquivos)")
                empresa_nome = "Não classificado"
            else:
                empresa_nome = arquivos_grupo[0]['empresa']['nome_empresa'] if arquivos_grupo and arquivos_grupo[0]['empresa'] else "N/A"
                print(f"\n🏢 Processando PRIORIDADE {prioridade}: {empresa_nome} ({len(arquivos_grupo)} arquivos)")
            
            dados_grupo = self._processar_grupo_arquivos(arquivos_grupo, prioridade)
            total_dados_encontrados += dados_grupo
            
            if prioridade != 999 and empresa_nome != "N/A":
                empresas_processadas.add(empresa_nome)
        
        # Atualizar estatísticas
        self.estatisticas.update({
            'dados_encontrados': total_dados_encontrados,
            'empresas_identificadas': len(empresas_processadas)
        })
        
        print(f"\n✅ PROCESSAMENTO CONCLUÍDO")
        print(f"📊 Total de dados encontrados: {total_dados_encontrados}")
        print(f"🏢 Empresas identificadas: {len(empresas_processadas)}")
        
        return self.estatisticas
    
    def _processar_grupo_arquivos(self, grupo_arquivos: List[Dict], prioridade: int) -> int:
        """Processa um grupo de arquivos da mesma prioridade"""
        dados_encontrados = 0
        
        for item in grupo_arquivos:
            arquivo = item['arquivo']
            empresa = item['empresa']
            
            try:
                print(f"  📖 Processando: {Path(arquivo).name}")
                
                # Extrair texto
                texto = extrair_texto(arquivo)
                if not texto:
                    print(f"    ❌ Falha ao extrair texto")
                    continue
                
                # Analisar dados pessoais
                resultados = analisar_texto(texto, arquivo)
                
                if resultados:
                    print(f"    ✅ {len(resultados)} dados encontrados")
                    dados_encontrados += len(resultados)
                    
                    # Salvar resultados com informações da empresa
                    self._salvar_resultados_priorizados(resultados, arquivo, empresa)
                else:
                    print(f"    ⚪ Nenhum dado pessoal encontrado")
                
            except Exception as e:
                print(f"    ❌ Erro no processamento: {e}")
                continue
        
        return dados_encontrados
    
    def _salvar_resultados_priorizados(self, resultados: List[Dict], arquivo: str, empresa: Optional[Dict]):
        """Salva resultados com informações de priorização empresarial"""
        for dado in resultados:
            # Determinar informações da empresa
            if empresa:
                nome_empresa = empresa['nome_empresa']
                dominio = empresa['dominio_email']
            else:
                nome_empresa = dado.get('titular', 'Não identificado')
                dominio = ""
                
                # Tentar extrair domínio se for email
                if dado['campo'] == 'email':
                    dominio = extrair_dominio_de_email(dado['valor'])
            
            # Verificar prioridade do dado
            prioridade_dado = verificar_prioridade(dado['campo'])
            
            # Inserir no banco com informações empresariais
            inserir_resultado_analise(
                dominio=dominio,
                empresa=nome_empresa,
                tipo_dado=dado['campo'],
                valor_encontrado=dado['valor'],
                arquivo_origem=arquivo,
                contexto=dado.get('contexto', ''),
                titular_identificado=dado.get('titular', ''),
                metodo_identificacao=dado.get('origem_identificacao', ''),
                prioridade=prioridade_dado
            )
    
    def gerar_relatorio_processamento(self) -> str:
        """Gera relatório detalhado do processamento"""
        relatorio = """
=== RELATÓRIO DE PROCESSAMENTO AVANÇADO LGPD ===

📊 ESTATÍSTICAS GERAIS:
  • Arquivos processados: {arquivos_processados}
  • Dados pessoais encontrados: {dados_encontrados}
  • Empresas identificadas: {empresas_identificadas}
  • Empresas prioritárias configuradas: {total_empresas}

🏢 PROCESSAMENTO POR PRIORIDADE:
""".format(
            arquivos_processados=self.estatisticas['arquivos_processados'],
            dados_encontrados=self.estatisticas['dados_encontrados'],
            empresas_identificadas=self.estatisticas['empresas_identificadas'],
            total_empresas=len(self.prioridades_empresas)
        )
        
        for prioridade, dados in self.estatisticas.get('processamento_por_prioridade', {}).items():
            if prioridade == 999:
                relatorio += f"  • Não classificados: {dados['arquivos']} arquivos, {dados['dados']} dados\n"
            else:
                relatorio += f"  • Prioridade {prioridade}: {dados['arquivos']} arquivos, {dados['dados']} dados\n"
        
        relatorio += "\n✅ Processamento concluído com priorização empresarial aplicada."
        
        return relatorio


# Função principal de processamento avançado
def processar_arquivos_com_ia(diretorio_base: str = "data") -> Dict:
    """
    Processamento avançado de arquivos com IA e priorização empresarial
    
    Args:
        diretorio_base (str): Diretório base para varredura
        
    Returns:
        Dict: Estatísticas do processamento
    """
    processador = ProcessadorAvancadoLGPD()
    
    # Carregar prioridades empresariais
    if not processador.carregar_prioridades_empresariais():
        print("⚠️  Continuando sem priorização empresarial")
    
    # Verificar diretório
    if not os.path.exists(diretorio_base):
        print(f"❌ Diretório '{diretorio_base}' não encontrado")
        return {}
    
    # Listar arquivos
    from file_scanner import listar_arquivos_recursivos
    arquivos = listar_arquivos_recursivos(diretorio_base)
    
    if not arquivos:
        print(f"❌ Nenhum arquivo encontrado em '{diretorio_base}'")
        return {}
    
    print(f"📁 Encontrados {len(arquivos)} arquivos para processamento")
    
    # Classificar por empresa
    arquivos_classificados = processador.classificar_arquivos_por_empresa(arquivos)
    
    # Processar por prioridade
    estatisticas = processador.processar_por_prioridade(arquivos_classificados)
    
    # Gerar relatório
    relatorio = processador.gerar_relatorio_processamento()
    print(relatorio)
    
    return estatisticas


if __name__ == "__main__":
    # Teste do processador avançado
    from database import inicializar_banco
    from data_extractor import inicializar_spacy
    
    print("=== TESTE DO PROCESSADOR AVANÇADO LGPD ===")
    
    # Inicializar dependências
    inicializar_banco()
    inicializar_spacy()
    
    # Executar processamento
    resultado = processar_arquivos_com_ia("data")
    
    print(f"\n🎯 Processamento concluído: {resultado}")