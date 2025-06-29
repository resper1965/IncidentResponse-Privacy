#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Processador Recursivo de Dados LGPD
- Navega por toda a árvore de diretórios
- Processa todos os arquivos encontrados
- Relatórios hierárquicos por diretório
- Controle de profundidade e exclusões
"""

import os
import json
import logging
from typing import List, Dict, Optional, Set
from datetime import datetime
from pathlib import Path
from collections import defaultdict
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed

# Importar módulos do sistema
try:
    from integrated_processor import IntegratedProcessor
    from robust_data_extractor import extrair_dados_robusto
except ImportError as e:
    logging.error(f"❌ Erro ao importar módulos: {e}")
    raise

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class RecursiveProcessor:
    """Processador recursivo que navega por toda a árvore de diretórios"""
    
    def __init__(self, config_path: Optional[str] = None):
        self.processor = IntegratedProcessor(config_path)
        
        # Configurações de recursão
        self.config = self._load_recursive_config(config_path)
        
        # Estatísticas globais
        self.global_stats = {
            'diretorios_processados': 0,
            'arquivos_processados': 0,
            'arquivos_ignorados': 0,
            'erros': 0,
            'total_dados_extraidos': 0,
            'clientes_prioritarios': 0,
            'tempo_total': 0.0,
            'tamanho_total_mb': 0.0
        }
        
        # Cache de arquivos já processados
        self.processed_files: Set[str] = set()
        
        # Resultados organizados por diretório
        self.results_by_directory: Dict[str, List[Dict]] = defaultdict(list)
    
    def _load_recursive_config(self, config_path: Optional[str]) -> Dict:
        """Carregar configurações específicas para processamento recursivo"""
        default_config = {
            'max_depth': -1,  # -1 = sem limite
            'file_patterns': ['*.txt', '*.doc', '*.docx', '*.pdf', '*.eml', '*.msg', '*.rtf'],
            'exclude_patterns': [
                '*.tmp', '*.bak', '*.log', '*.cache',
                'node_modules', '.git', '__pycache__', '.vscode'
            ],
            'exclude_directories': [
                'node_modules', '.git', '__pycache__', '.vscode',
                'temp', 'tmp', 'cache', 'logs', 'backup'
            ],
            'max_file_size_mb': 100,
            'parallel_processing': True,
            'max_workers': 4,
            'progress_reporting': True,
            'save_intermediate_results': True,
            'resume_from_checkpoint': True,
            'checkpoint_file': 'recursive_checkpoint.json'
        }
        
        if config_path and os.path.exists(config_path):
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    user_config = json.load(f)
                default_config.update(user_config.get('recursive', {}))
                logger.info(f"✅ Configuração recursiva carregada de: {config_path}")
            except Exception as e:
                logger.warning(f"⚠️ Erro ao carregar configuração: {e}")
        
        return default_config
    
    def process_directory_tree(self, root_path: str) -> Dict:
        """Processar toda a árvore de diretórios a partir do caminho raiz"""
        logger.info(f"🌳 Iniciando processamento recursivo de: {root_path}")
        
        start_time = datetime.now()
        
        # Verificar se o diretório existe
        if not os.path.exists(root_path):
            raise FileNotFoundError(f"Diretório não encontrado: {root_path}")
        
        # Carregar checkpoint se habilitado
        if self.config['resume_from_checkpoint']:
            self._load_checkpoint()
        
        # Encontrar todos os arquivos na árvore
        all_files = self._discover_files_recursive(root_path)
        logger.info(f"📁 Encontrados {len(all_files)} arquivos para processar")
        
        # Processar arquivos
        if self.config['parallel_processing']:
            results = self._process_files_parallel(all_files)
        else:
            results = self._process_files_sequential(all_files)
        
        # Organizar resultados por diretório
        self._organize_results_by_directory(results)
        
        # Gerar relatório consolidado
        consolidated_report = self._generate_tree_report(root_path, results, start_time)
        
        # Salvar checkpoint
        if self.config['resume_from_checkpoint']:
            self._save_checkpoint()
        
        # Salvar relatórios
        self._save_tree_reports(consolidated_report)
        
        return consolidated_report
    
    def _discover_files_recursive(self, root_path: str) -> List[str]:
        """Descobrir todos os arquivos na árvore de diretórios"""
        files_to_process = []
        root_path = Path(root_path)
        
        logger.info(f"🔍 Explorando árvore de diretórios...")
        
        for pattern in self.config['file_patterns']:
            for file_path in root_path.rglob(pattern):
                # Verificar se já foi processado
                if str(file_path) in self.processed_files:
                    continue
                
                # Verificar exclusões
                if self._should_exclude_file(file_path):
                    self.global_stats['arquivos_ignorados'] += 1
                    continue
                
                # Verificar profundidade
                if not self._check_depth_limit(file_path, root_path):
                    continue
                
                # Verificar tamanho
                if not self._check_file_size(file_path):
                    continue
                
                files_to_process.append(str(file_path))
        
        logger.info(f"✅ Descoberta concluída: {len(files_to_process)} arquivos válidos")
        return files_to_process
    
    def _should_exclude_file(self, file_path: Path) -> bool:
        """Verificar se arquivo deve ser excluído"""
        # Verificar padrões de exclusão
        for pattern in self.config['exclude_patterns']:
            if file_path.match(pattern):
                return True
        
        # Verificar se está em diretório excluído
        for part in file_path.parts:
            if part in self.config['exclude_directories']:
                return True
        
        return False
    
    def _check_depth_limit(self, file_path: Path, root_path: Path) -> bool:
        """Verificar limite de profundidade"""
        if self.config['max_depth'] == -1:
            return True
        
        relative_path = file_path.relative_to(root_path)
        depth = len(relative_path.parts) - 1  # -1 porque o arquivo conta como nível
        
        return depth <= self.config['max_depth']
    
    def _check_file_size(self, file_path: Path) -> bool:
        """Verificar tamanho do arquivo"""
        try:
            file_size_mb = file_path.stat().st_size / (1024 * 1024)
            return file_size_mb <= self.config['max_file_size_mb']
        except:
            return False
    
    def _process_files_parallel(self, files: List[str]) -> List[Dict]:
        """Processar arquivos em paralelo"""
        logger.info(f"⚡ Processando {len(files)} arquivos em paralelo...")
        
        results = []
        completed = 0
        
        with ThreadPoolExecutor(max_workers=self.config['max_workers']) as executor:
            # Submeter tarefas
            future_to_file = {
                executor.submit(self._process_single_file, file_path): file_path 
                for file_path in files
            }
            
            # Coletar resultados
            for future in as_completed(future_to_file):
                file_path = future_to_file[future]
                try:
                    result = future.result()
                    results.append(result)
                    completed += 1
                    
                    # Relatório de progresso
                    if self.config['progress_reporting'] and completed % 10 == 0:
                        progress = (completed / len(files)) * 100
                        logger.info(f"📊 Progresso: {completed}/{len(files)} ({progress:.1f}%)")
                    
                except Exception as e:
                    logger.error(f"❌ Erro ao processar {file_path}: {e}")
                    self.global_stats['erros'] += 1
                    results.append({
                        'arquivo': file_path,
                        'erro': str(e),
                        'timestamp': datetime.now().isoformat()
                    })
        
        return results
    
    def _process_files_sequential(self, files: List[str]) -> List[Dict]:
        """Processar arquivos sequencialmente"""
        logger.info(f"🔄 Processando {len(files)} arquivos sequencialmente...")
        
        results = []
        completed = 0
        
        for file_path in files:
            try:
                result = self._process_single_file(file_path)
                results.append(result)
                completed += 1
                
                # Relatório de progresso
                if self.config['progress_reporting'] and completed % 10 == 0:
                    progress = (completed / len(files)) * 100
                    logger.info(f"📊 Progresso: {completed}/{len(files)} ({progress:.1f}%)")
                
            except Exception as e:
                logger.error(f"❌ Erro ao processar {file_path}: {e}")
                self.global_stats['erros'] += 1
                results.append({
                    'arquivo': file_path,
                    'erro': str(e),
                    'timestamp': datetime.now().isoformat()
                })
        
        return results
    
    def _process_single_file(self, file_path: str) -> Dict:
        """Processar um arquivo individual"""
        try:
            # Verificar se já foi processado
            if file_path in self.processed_files:
                return {'arquivo': file_path, 'status': 'já_processado'}
            
            # Processar arquivo
            result = self.processor.process_file(file_path)
            
            # Marcar como processado
            self.processed_files.add(file_path)
            
            # Atualizar estatísticas
            self._update_global_stats(result)
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Erro ao processar {file_path}: {e}")
            raise
    
    def _update_global_stats(self, result: Dict):
        """Atualizar estatísticas globais"""
        if 'erro' in result:
            self.global_stats['erros'] += 1
            return
        
        self.global_stats['arquivos_processados'] += 1
        self.global_stats['total_dados_extraidos'] += result.get('total_dados_extraidos', 0)
        self.global_stats['clientes_prioritarios'] += result.get('clientes_prioritarios', 0)
        self.global_stats['tempo_total'] += result.get('tempo_processamento', 0)
        self.global_stats['tamanho_total_mb'] += result.get('tamanho_arquivo_mb', 0)
    
    def _organize_results_by_directory(self, results: List[Dict]):
        """Organizar resultados por diretório"""
        for result in results:
            if 'erro' in result:
                continue
            
            file_path = Path(result['arquivo'])
            directory = str(file_path.parent)
            self.results_by_directory[directory].append(result)
    
    def _generate_tree_report(self, root_path: str, results: List[Dict], start_time: datetime) -> Dict:
        """Gerar relatório da árvore de diretórios"""
        end_time = datetime.now()
        total_time = (end_time - start_time).total_seconds()
        
        # Estatísticas por diretório
        directory_stats = {}
        for directory, dir_results in self.results_by_directory.items():
            successful_files = len([r for r in dir_results if 'erro' not in r])
            total_files = len(dir_results)
            
            directory_stats[directory] = {
                'total_arquivos': total_files,
                'arquivos_sucesso': successful_files,
                'arquivos_falha': total_files - successful_files,
                'taxa_sucesso': (successful_files / total_files * 100) if total_files > 0 else 0,
                'dados_extraidos': sum(r.get('total_dados_extraidos', 0) for r in dir_results),
                'clientes_prioritarios': sum(r.get('clientes_prioritarios', 0) for r in dir_results)
            }
        
        # Estatísticas por tipo de dado
        data_types = defaultdict(int)
        priority_clients = defaultdict(int)
        
        for result in results:
            if 'erro' in result:
                continue
            
            for dado in result.get('dados', []):
                data_types[dado['tipo']] += 1
                if dado.get('cliente_prioritario'):
                    priority_clients[dado['cliente_prioritario']] += 1
        
        return {
            'timestamp': datetime.now().isoformat(),
            'diretorio_raiz': root_path,
            'tempo_processamento_total': total_time,
            'resumo_geral': {
                'diretorios_processados': len(self.results_by_directory),
                'arquivos_processados': self.global_stats['arquivos_processados'],
                'arquivos_ignorados': self.global_stats['arquivos_ignorados'],
                'arquivos_com_erro': self.global_stats['erros'],
                'taxa_sucesso_geral': (
                    self.global_stats['arquivos_processados'] / 
                    (self.global_stats['arquivos_processados'] + self.global_stats['erros']) * 100
                ) if (self.global_stats['arquivos_processados'] + self.global_stats['erros']) > 0 else 0,
                'total_dados_extraidos': self.global_stats['total_dados_extraidos'],
                'clientes_prioritarios': self.global_stats['clientes_prioritarios'],
                'tamanho_total_mb': self.global_stats['tamanho_total_mb']
            },
            'estatisticas_por_diretorio': dict(directory_stats),
            'dados_por_tipo': dict(data_types),
            'clientes_prioritarios': dict(priority_clients),
            'configuracao_usada': self.config
        }
    
    def _save_tree_reports(self, consolidated_report: Dict):
        """Salvar relatórios da árvore"""
        # Criar diretórios
        reports_dir = Path(self.processor.config['reports_dir'])
        tree_reports_dir = reports_dir / 'tree_reports'
        tree_reports_dir.mkdir(exist_ok=True)
        
        # Salvar relatório consolidado
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        root_name = Path(consolidated_report['diretorio_raiz']).name
        
        consolidated_file = tree_reports_dir / f"relatorio_arvore_{root_name}_{timestamp}.json"
        with open(consolidated_file, 'w', encoding='utf-8') as f:
            json.dump(consolidated_report, f, indent=2, ensure_ascii=False)
        
        # Salvar relatórios por diretório
        for directory, results in self.results_by_directory.items():
            dir_name = Path(directory).name
            dir_report_file = tree_reports_dir / f"relatorio_diretorio_{dir_name}_{timestamp}.json"
            
            with open(dir_report_file, 'w', encoding='utf-8') as f:
                json.dump({
                    'diretorio': directory,
                    'timestamp': datetime.now().isoformat(),
                    'resultados': results
                }, f, indent=2, ensure_ascii=False)
        
        logger.info(f"💾 Relatórios da árvore salvos em: {tree_reports_dir}")
    
    def _save_checkpoint(self):
        """Salvar checkpoint do processamento"""
        checkpoint_data = {
            'processed_files': list(self.processed_files),
            'global_stats': self.global_stats,
            'timestamp': datetime.now().isoformat()
        }
        
        checkpoint_file = self.config['checkpoint_file']
        with open(checkpoint_file, 'w', encoding='utf-8') as f:
            json.dump(checkpoint_data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"💾 Checkpoint salvo: {checkpoint_file}")
    
    def _load_checkpoint(self):
        """Carregar checkpoint do processamento"""
        checkpoint_file = self.config['checkpoint_file']
        
        if os.path.exists(checkpoint_file):
            try:
                with open(checkpoint_file, 'r', encoding='utf-8') as f:
                    checkpoint_data = json.load(f)
                
                self.processed_files = set(checkpoint_data.get('processed_files', []))
                self.global_stats.update(checkpoint_data.get('global_stats', {}))
                
                logger.info(f"✅ Checkpoint carregado: {len(self.processed_files)} arquivos já processados")
            except Exception as e:
                logger.warning(f"⚠️ Erro ao carregar checkpoint: {e}")
    
    def get_processing_stats(self) -> Dict:
        """Obter estatísticas de processamento"""
        return self.global_stats.copy()

# Função principal para uso
def processar_arvore_diretorios(diretorio_raiz: str, config_path: Optional[str] = None) -> Dict:
    """Função principal para processamento recursivo de árvore de diretórios"""
    processor = RecursiveProcessor(config_path)
    return processor.process_directory_tree(diretorio_raiz)

if __name__ == "__main__":
    # Teste do processador recursivo
    import sys
    
    if len(sys.argv) > 1:
        root_dir = sys.argv[1]
        config_path = sys.argv[2] if len(sys.argv) > 2 else None
        
        try:
            resultado = processar_arvore_diretorios(root_dir, config_path)
            print(json.dumps(resultado, indent=2, ensure_ascii=False))
        except Exception as e:
            print(f"❌ Erro: {e}")
    else:
        print("Uso: python recursive_processor.py <diretorio_raiz> [config.json]")
        print("Exemplo: python recursive_processor.py /caminho/documentos/") 