#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sistema Integrado de Processamento de Dados LGPD
- Combina extração robusta, validação e IA semântica
- Processamento em lote com relatórios detalhados
- Integração com sistema existente
"""

import os
import json
import logging
from typing import List, Dict, Optional
from datetime import datetime
from pathlib import Path

# Importar módulos do sistema
try:
    from robust_data_extractor import extrair_dados_robusto, RobustDataExtractor
    from data_validator import validar_e_corrigir_dados, DataValidator
except ImportError as e:
    logging.error(f"❌ Erro ao importar módulos: {e}")
    raise

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class IntegratedProcessor:
    """Processador integrado de dados LGPD"""
    
    def __init__(self, config_path: Optional[str] = None):
        self.extractor = RobustDataExtractor()
        self.validator = DataValidator()
        
        # Configurações
        self.config = self._load_config(config_path)
        
        # Estatísticas globais
        self.global_stats = {
            'arquivos_processados': 0,
            'total_dados_extraidos': 0,
            'dados_validados': 0,
            'clientes_prioritarios': 0,
            'erros': 0,
            'tempo_processamento': 0.0
        }
    
    def _load_config(self, config_path: Optional[str]) -> Dict:
        """Carregar configurações"""
        default_config = {
            'output_dir': 'output',
            'reports_dir': 'reports',
            'enable_semantic_ai': True,
            'priority_clients': [
                'bradesco', 'petrobras', 'ons', 'embraer', 'rede_dor',
                'globo', 'eletrobras', 'crefisa', 'equinix', 'cohesity'
            ],
            'validation_threshold': 0.7,
            'max_file_size_mb': 100
        }
        
        if config_path and os.path.exists(config_path):
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    user_config = json.load(f)
                default_config.update(user_config)
                logger.info(f"✅ Configuração carregada de: {config_path}")
            except Exception as e:
                logger.warning(f"⚠️ Erro ao carregar configuração: {e}")
        
        return default_config
    
    def process_file(self, file_path: str) -> Dict:
        """Processar um arquivo individual"""
        logger.info(f"🔍 Processando arquivo: {file_path}")
        
        start_time = datetime.now()
        
        try:
            # Verificar tamanho do arquivo
            file_size = os.path.getsize(file_path) / (1024 * 1024)  # MB
            if file_size > self.config['max_file_size_mb']:
                raise ValueError(f"Arquivo muito grande: {file_size:.2f}MB")
            
            # Ler conteúdo do arquivo
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            # 1. Extração robusta com regex
            extraction_result = self.extractor.extract_all_data(content, file_path)
            
            # 2. Validação e correção
            from robust_data_extractor import ExtractedData
            dados_extraidos = [ExtractedData(**d) for d in extraction_result.get('dados', [])]
            dados_validados = self.validator.validate_and_correct(dados_extraidos)
            
            # 3. Análise semântica para clientes prioritários
            if self.config['enable_semantic_ai']:
                dados_finais = self._apply_semantic_analysis(dados_validados, content)
            else:
                dados_finais = dados_validados
            
            # 4. Filtrar por threshold de confiança
            dados_filtrados = [
                d for d in dados_finais 
                if d.confianca >= self.config['validation_threshold']
            ]
            
            # Calcular tempo de processamento
            end_time = datetime.now()
            processing_time = (end_time - start_time).total_seconds()
            
            # Preparar resultado
            result = {
                'arquivo': file_path,
                'timestamp': datetime.now().isoformat(),
                'tempo_processamento': processing_time,
                'tamanho_arquivo_mb': file_size,
                'total_dados_extraidos': len(dados_extraidos),
                'dados_validados': len(dados_validados),
                'dados_finais': len(dados_filtrados),
                'clientes_prioritarios': len([d for d in dados_finais if d.cliente_prioritario]),
                'estatisticas_extracao': extraction_result.get('estatisticas', {}),
                'dados': [
                    {
                        'tipo': d.tipo,
                        'valor': d.valor,
                        'contexto': d.contexto,
                        'confianca': d.confianca,
                        'metodo': d.metodo,
                        'validado': d.validado,
                        'cliente_prioritario': d.cliente_prioritario,
                        'hash': d.hash_valor,
                        'validation_metadata': d.validation_metadata
                    }
                    for d in dados_filtrados
                ]
            }
            
            # Atualizar estatísticas globais
            self._update_global_stats(result)
            
            logger.info(f"✅ Arquivo processado: {len(dados_filtrados)} dados finais")
            return result
            
        except Exception as e:
            logger.error(f"❌ Erro ao processar {file_path}: {e}")
            self.global_stats['erros'] += 1
            return {
                'arquivo': file_path,
                'erro': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    def _apply_semantic_analysis(self, dados: List, content: str) -> List:
        """Aplicar análise semântica para clientes prioritários"""
        if not hasattr(self.extractor, 'semantic_ai') or not self.extractor.semantic_ai.nlp:
            return dados
        
        # Detectar cliente prioritário no conteúdo
        cliente = self.extractor.semantic_ai.detect_priority_client(content)
        
        if cliente:
            logger.info(f"🎯 Cliente prioritário detectado: {cliente}")
            
            # Refinar dados com IA semântica
            dados_refinados = self.extractor.semantic_ai.refine_extraction(dados, content)
            
            # Marcar dados de clientes prioritários
            for dado in dados_refinados:
                if dado.cliente_prioritario:
                    dado.confianca = min(1.0, dado.confianca + 0.1)
            
            return dados_refinados
        
        return dados
    
    def _update_global_stats(self, result: Dict):
        """Atualizar estatísticas globais"""
        self.global_stats['arquivos_processados'] += 1
        self.global_stats['total_dados_extraidos'] += result.get('total_dados_extraidos', 0)
        self.global_stats['dados_validados'] += result.get('dados_validados', 0)
        self.global_stats['clientes_prioritarios'] += result.get('clientes_prioritarios', 0)
        self.global_stats['tempo_processamento'] += result.get('tempo_processamento', 0)
    
    def process_directory(self, directory_path: str, file_patterns: Optional[List[str]] = None) -> Dict:
        """Processar todos os arquivos de um diretório"""
        logger.info(f"📁 Processando diretório: {directory_path}")
        
        if file_patterns is None:
            file_patterns = ['*.txt', '*.doc', '*.docx', '*.pdf', '*.eml', '*.msg']
        
        # Encontrar arquivos
        files_to_process = []
        for pattern in file_patterns:
            files_to_process.extend(Path(directory_path).glob(pattern))
        
        logger.info(f"📄 Encontrados {len(files_to_process)} arquivos para processar")
        
        # Processar arquivos
        results = []
        for file_path in files_to_process:
            result = self.process_file(str(file_path))
            results.append(result)
        
        # Gerar relatório consolidado
        consolidated_report = self._generate_consolidated_report(results)
        
        # Salvar relatórios
        self._save_reports(results, consolidated_report)
        
        return consolidated_report
    
    def _generate_consolidated_report(self, results: List[Dict]) -> Dict:
        """Gerar relatório consolidado"""
        total_files = len(results)
        successful_files = len([r for r in results if 'erro' not in r])
        failed_files = total_files - successful_files
        
        # Estatísticas por tipo de dado
        data_types = {}
        priority_clients = {}
        
        for result in results:
            if 'erro' in result:
                continue
            
            for dado in result.get('dados', []):
                tipo = dado['tipo']
                data_types[tipo] = data_types.get(tipo, 0) + 1
                
                if dado.get('cliente_prioritario'):
                    cliente = dado['cliente_prioritario']
                    priority_clients[cliente] = priority_clients.get(cliente, 0) + 1
        
        return {
            'timestamp': datetime.now().isoformat(),
            'resumo': {
                'total_arquivos': total_files,
                'arquivos_sucesso': successful_files,
                'arquivos_falha': failed_files,
                'taxa_sucesso': (successful_files / total_files * 100) if total_files > 0 else 0,
                'tempo_total_processamento': self.global_stats['tempo_processamento'],
                'dados_por_tipo': data_types,
                'clientes_prioritarios': priority_clients
            },
            'estatisticas_globais': self.global_stats,
            'resultados_detalhados': results
        }
    
    def _save_reports(self, results: List[Dict], consolidated_report: Dict):
        """Salvar relatórios em arquivos"""
        # Criar diretórios se não existirem
        output_dir = Path(self.config['output_dir'])
        reports_dir = Path(self.config['reports_dir'])
        
        output_dir.mkdir(exist_ok=True)
        reports_dir.mkdir(exist_ok=True)
        
        # Salvar relatório consolidado
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        consolidated_file = reports_dir / f"relatorio_consolidado_{timestamp}.json"
        
        with open(consolidated_file, 'w', encoding='utf-8') as f:
            json.dump(consolidated_report, f, indent=2, ensure_ascii=False)
        
        # Salvar dados extraídos
        for result in results:
            if 'erro' in result:
                continue
            
            filename = Path(result['arquivo']).stem
            output_file = output_dir / f"{filename}_dados_extraidos.json"
            
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=2, ensure_ascii=False)
        
        logger.info(f"💾 Relatórios salvos em: {reports_dir}")
        logger.info(f"📊 Dados extraídos salvos em: {output_dir}")
    
    def get_processing_stats(self) -> Dict:
        """Obter estatísticas de processamento"""
        return self.global_stats.copy()

# Função principal para uso
def processar_dados_lgpd(arquivo_ou_diretorio: str, config_path: Optional[str] = None) -> Dict:
    """Função principal para processamento de dados LGPD"""
    processor = IntegratedProcessor(config_path)
    
    if os.path.isfile(arquivo_ou_diretorio):
        # Processar arquivo único
        result = processor.process_file(arquivo_ou_diretorio)
        return {
            'tipo': 'arquivo_unico',
            'resultado': result,
            'estatisticas': processor.get_processing_stats()
        }
    elif os.path.isdir(arquivo_ou_diretorio):
        # Processar diretório
        result = processor.process_directory(arquivo_ou_diretorio)
        return {
            'tipo': 'diretorio',
            'resultado': result,
            'estatisticas': processor.get_processing_stats()
        }
    else:
        raise FileNotFoundError(f"Arquivo ou diretório não encontrado: {arquivo_ou_diretorio}")

if __name__ == "__main__":
    # Teste do processador integrado
    import sys
    
    if len(sys.argv) > 1:
        path = sys.argv[1]
        config_path = sys.argv[2] if len(sys.argv) > 2 else None
        
        try:
            resultado = processar_dados_lgpd(path, config_path)
            print(json.dumps(resultado, indent=2, ensure_ascii=False))
        except Exception as e:
            print(f"❌ Erro: {e}")
    else:
        print("Uso: python integrated_processor.py <arquivo_ou_diretorio> [config.json]") 