#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Interface Web Melhorada para Sistema Robusto de Extração de Dados LGPD
- Seleção de diretório para processamento recursivo
- Upload de arquivos individuais
- Monitoramento em tempo real
- Relatórios interativos
"""

import os
import json
import logging
from flask import Flask, render_template, request, jsonify, send_file, redirect, url_for
from werkzeug.utils import secure_filename
from pathlib import Path
import threading
import time
from datetime import datetime

# Importar módulos do sistema
try:
    from recursive_processor import RecursiveProcessor, processar_arvore_diretorios
    from integrated_processor import IntegratedProcessor, processar_dados_lgpd
except ImportError as e:
    logging.error(f"❌ Erro ao importar módulos: {e}")
    raise

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config['SECRET_KEY'] = 'privacy-lgpd-enhanced-2024'
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # 100MB

# Criar diretórios necessários
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs('output', exist_ok=True)
os.makedirs('reports', exist_ok=True)

# Variáveis globais para controle de processamento
processing_status = {
    'is_processing': False,
    'current_task': None,
    'progress': 0,
    'total_files': 0,
    'processed_files': 0,
    'current_file': '',
    'start_time': None,
    'estimated_time': None,
    'results': None
}

class ProcessingManager:
    """Gerenciador de processamento em background"""
    
    def __init__(self):
        self.recursive_processor = None
        self.integrated_processor = None
    
    def start_recursive_processing(self, directory_path: str, config_path: str = None):
        """Iniciar processamento recursivo"""
        global processing_status
        
        try:
            processing_status.update({
                'is_processing': True,
                'current_task': 'recursive',
                'progress': 0,
                'total_files': 0,
                'processed_files': 0,
                'current_file': 'Iniciando descoberta de arquivos...',
                'start_time': datetime.now(),
                'estimated_time': None,
                'results': None
            })
            
            # Criar processador
            self.recursive_processor = RecursiveProcessor(config_path)
            
            # Processar em thread separada
            thread = threading.Thread(
                target=self._process_recursive_background,
                args=(directory_path, config_path)
            )
            thread.daemon = True
            thread.start()
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Erro ao iniciar processamento recursivo: {e}")
            processing_status['is_processing'] = False
            return False
    
    def _process_recursive_background(self, directory_path: str, config_path: str = None):
        """Processar recursivamente em background"""
        global processing_status
        
        try:
            # Processar árvore de diretórios
            result = self.recursive_processor.process_directory_tree(directory_path)
            
            # Atualizar status final
            processing_status.update({
                'is_processing': False,
                'progress': 100,
                'results': result,
                'current_file': 'Processamento concluído!'
            })
            
            logger.info("✅ Processamento recursivo concluído com sucesso")
            
        except Exception as e:
            logger.error(f"❌ Erro no processamento recursivo: {e}")
            processing_status.update({
                'is_processing': False,
                'current_file': f'Erro: {str(e)}'
            })
    
    def start_file_processing(self, file_path: str, config_path: str = None):
        """Iniciar processamento de arquivo único"""
        global processing_status
        
        try:
            processing_status.update({
                'is_processing': True,
                'current_task': 'single_file',
                'progress': 0,
                'total_files': 1,
                'processed_files': 0,
                'current_file': f'Processando: {os.path.basename(file_path)}',
                'start_time': datetime.now(),
                'estimated_time': None,
                'results': None
            })
            
            # Criar processador
            self.integrated_processor = IntegratedProcessor(config_path)
            
            # Processar em thread separada
            thread = threading.Thread(
                target=self._process_file_background,
                args=(file_path, config_path)
            )
            thread.daemon = True
            thread.start()
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Erro ao iniciar processamento de arquivo: {e}")
            processing_status['is_processing'] = False
            return False
    
    def _process_file_background(self, file_path: str, config_path: str = None):
        """Processar arquivo em background"""
        global processing_status
        
        try:
            # Processar arquivo
            result = self.integrated_processor.process_file(file_path)
            
            # Atualizar status final
            processing_status.update({
                'is_processing': False,
                'progress': 100,
                'results': result,
                'current_file': 'Processamento concluído!'
            })
            
            logger.info("✅ Processamento de arquivo concluído com sucesso")
            
        except Exception as e:
            logger.error(f"❌ Erro no processamento de arquivo: {e}")
            processing_status.update({
                'is_processing': False,
                'current_file': f'Erro: {str(e)}'
            })

# Instanciar gerenciador
processing_manager = ProcessingManager()

@app.route('/')
def index():
    """Página principal"""
    return render_template('dashboard_enhanced.html')

@app.route('/api/start-recursive', methods=['POST'])
def start_recursive_processing():
    """Iniciar processamento recursivo"""
    try:
        data = request.get_json()
        directory_path = data.get('directory_path')
        config_path = data.get('config_path')
        
        if not directory_path or not os.path.exists(directory_path):
            return jsonify({
                'success': False,
                'error': 'Diretório não encontrado ou inválido'
            }), 400
        
        if processing_status['is_processing']:
            return jsonify({
                'success': False,
                'error': 'Já existe um processamento em andamento'
            }), 400
        
        # Iniciar processamento
        success = processing_manager.start_recursive_processing(directory_path, config_path)
        
        if success:
            return jsonify({
                'success': True,
                'message': 'Processamento recursivo iniciado com sucesso'
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Erro ao iniciar processamento'
            }), 500
            
    except Exception as e:
        logger.error(f"❌ Erro ao iniciar processamento recursivo: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/upload-file', methods=['POST'])
def upload_file():
    """Upload e processamento de arquivo único"""
    try:
        if 'file' not in request.files:
            return jsonify({
                'success': False,
                'error': 'Nenhum arquivo enviado'
            }), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({
                'success': False,
                'error': 'Nenhum arquivo selecionado'
            }), 400
        
        # Salvar arquivo
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        
        # Iniciar processamento
        success = processing_manager.start_file_processing(file_path)
        
        if success:
            return jsonify({
                'success': True,
                'message': f'Arquivo {filename} enviado e processamento iniciado'
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Erro ao iniciar processamento'
            }), 500
            
    except Exception as e:
        logger.error(f"❌ Erro no upload de arquivo: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/status')
def get_status():
    """Obter status do processamento"""
    global processing_status
    
    # Calcular tempo estimado se disponível
    if processing_status['start_time'] and processing_status['progress'] > 0:
        elapsed = (datetime.now() - processing_status['start_time']).total_seconds()
        if processing_status['progress'] > 0:
            estimated_total = elapsed / (processing_status['progress'] / 100)
            remaining = estimated_total - elapsed
            processing_status['estimated_time'] = max(0, remaining)
    
    return jsonify(processing_status)

@app.route('/api/results')
def get_results():
    """Obter resultados do processamento"""
    global processing_status
    
    if not processing_status['results']:
        return jsonify({
            'success': False,
            'error': 'Nenhum resultado disponível'
        }), 404
    
    return jsonify({
        'success': True,
        'results': processing_status['results']
    })

@app.route('/api/stop-processing', methods=['POST'])
def stop_processing():
    """Parar processamento em andamento"""
    global processing_status
    
    if processing_status['is_processing']:
        processing_status.update({
            'is_processing': False,
            'current_file': 'Processamento interrompido pelo usuário'
        })
        
        return jsonify({
            'success': True,
            'message': 'Processamento interrompido'
        })
    else:
        return jsonify({
            'success': False,
            'error': 'Nenhum processamento em andamento'
        }), 400

@app.route('/api/scan-directory', methods=['POST'])
def scan_directory():
    """Escanear diretório para mostrar arquivos que serão processados"""
    try:
        data = request.get_json()
        directory_path = data.get('directory_path')
        
        if not directory_path or not os.path.exists(directory_path):
            return jsonify({
                'success': False,
                'error': 'Diretório não encontrado'
            }), 400
        
        # Configurações de escaneamento
        file_patterns = ['*.txt', '*.doc', '*.docx', '*.pdf', '*.eml', '*.msg', '*.rtf']
        exclude_dirs = ['node_modules', '.git', '__pycache__', '.vscode', 'temp', 'tmp']
        
        # Encontrar arquivos
        files_found = []
        total_size = 0
        
        for pattern in file_patterns:
            for file_path in Path(directory_path).rglob(pattern):
                # Verificar exclusões
                should_exclude = False
                for part in file_path.parts:
                    if part in exclude_dirs:
                        should_exclude = True
                        break
                
                if not should_exclude:
                    try:
                        file_size = file_path.stat().st_size
                        total_size += file_size
                        files_found.append({
                            'path': str(file_path),
                            'name': file_path.name,
                            'size_mb': round(file_size / (1024 * 1024), 2),
                            'type': file_path.suffix.lower()
                        })
                    except:
                        continue
        
        return jsonify({
            'success': True,
            'scan_results': {
                'directory': directory_path,
                'total_files': len(files_found),
                'total_size_mb': round(total_size / (1024 * 1024), 2),
                'files': files_found[:100],  # Limitar a 100 arquivos para preview
                'file_types': list(set(f['type'] for f in files_found))
            }
        })
        
    except Exception as e:
        logger.error(f"❌ Erro ao escanear diretório: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/download-report/<report_type>')
def download_report(report_type):
    """Download de relatórios"""
    try:
        if report_type == 'latest':
            # Encontrar relatório mais recente
            reports_dir = Path('reports')
            if not reports_dir.exists():
                return jsonify({
                    'success': False,
                    'error': 'Nenhum relatório encontrado'
                }), 404
            
            json_files = list(reports_dir.glob('*.json'))
            if not json_files:
                return jsonify({
                    'success': False,
                    'error': 'Nenhum relatório encontrado'
                }), 404
            
            latest_file = max(json_files, key=lambda x: x.stat().st_mtime)
            return send_file(latest_file, as_attachment=True)
        
        else:
            return jsonify({
                'success': False,
                'error': 'Tipo de relatório não suportado'
            }), 400
            
    except Exception as e:
        logger.error(f"❌ Erro ao baixar relatório: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/health')
def health_check():
    """Verificação de saúde da aplicação"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'version': '2.0.0'
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True) 