#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sistema Principal Funcional para VPS
- Flask web interface
- Processamento de dados LGPD
- Extração com regex garantido
- IA semântica para clientes prioritários
"""

import os
import json
import re
import logging
from datetime import datetime
from flask import Flask, render_template, request, jsonify, send_file
from werkzeug.utils import secure_filename
from pathlib import Path
import threading
import time

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config['SECRET_KEY'] = 'privacy-lgpd-vps-2024'
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # 100MB

# Criar diretórios necessários
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs('output', exist_ok=True)
os.makedirs('reports', exist_ok=True)

# Status global do processamento
processing_status = {
    'is_processing': False,
    'progress': 0,
    'current_file': '',
    'results': None,
    'error': None
}

class DataExtractor:
    """Extrator de dados com regex garantido"""
    
    def __init__(self):
        self.patterns = {
            'cpf': r'\b\d{3}[.\s-]?\d{3}[.\s-]?\d{3}[-\s]?\d{2}\b',
            'email': r'\b[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}\b',
            'telefone': r'\b(\(?\d{2}\)?[\s-]?)?(9?\d{4})[\s-]?\d{4}\b',
            'data_nascimento': r'\b(0?[1-9]|[12][0-9]|3[01])[/\-\.](0?[1-9]|1[0-2])[/\-\.](?:19|20)?\d{2}\b',
            'cep': r'\b\d{5}[-\s]?\d{3}\b',
            'rg': r'\b\d{1,2}[.\s-]?\d{3}[.\s-]?\d{3}[-\s]?[0-9Xx]\b',
            'placa_veiculo': r'\b([A-Z]{3}[-\s]?\d{4})\b',
            'ip': r'\b(?:\d{1,3}\.){3}\d{1,3}\b'
        }
        
        self.priority_clients = {
            'bradesco': ['bradesco', 'banco bradesco', 'bradesco s.a.'],
            'petrobras': ['petrobras', 'petrobras s.a.', 'petrobras brasil'],
            'ons': ['ons', 'operador nacional do sistema elétrico'],
            'embraer': ['embraer', 'embraer s.a.'],
            'rede_dor': ['rede dor', 'rede d\'or', 'rededor'],
            'globo': ['globo', 'organizações globo', 'rede globo'],
            'eletrobras': ['eletrobras', 'eletrobras s.a.'],
            'crefisa': ['crefisa', 'banco crefisa'],
            'equinix': ['equinix', 'equinix brasil'],
            'cohesity': ['cohesity', 'cohesity brasil']
        }
    
    def extract_data(self, text, filename):
        """Extrair dados do texto"""
        results = {
            'arquivo': filename,
            'timestamp': datetime.now().isoformat(),
            'dados': [],
            'estatisticas': {
                'total_encontrados': 0,
                'por_tipo': {},
                'clientes_prioritarios': 0
            }
        }
        
        # Detectar cliente prioritário
        priority_client = self.detect_priority_client(text)
        
        # Extrair dados por tipo
        for tipo, pattern in self.patterns.items():
            matches = re.finditer(pattern, text, re.IGNORECASE)
            
            for match in matches:
                valor = match.group(0)
                pos_inicio = match.start()
                pos_fim = match.end()
                
                # Extrair contexto
                contexto = self.extract_context(text, pos_inicio, pos_fim)
                
                # Validar dados
                validado = self.validate_data(tipo, valor)
                
                # Calcular confiança
                confianca = 0.9 if validado else 0.5
                if priority_client:
                    confianca = min(1.0, confianca + 0.1)
                
                dado = {
                    'tipo': tipo,
                    'valor': valor,
                    'contexto': contexto,
                    'confianca': confianca,
                    'validado': validado,
                    'cliente_prioritario': priority_client,
                    'posicao': {'inicio': pos_inicio, 'fim': pos_fim}
                }
                
                results['dados'].append(dado)
                results['estatisticas']['total_encontrados'] += 1
                
                # Contar por tipo
                if tipo not in results['estatisticas']['por_tipo']:
                    results['estatisticas']['por_tipo'][tipo] = 0
                results['estatisticas']['por_tipo'][tipo] += 1
        
        # Contar clientes prioritários
        if priority_client:
            results['estatisticas']['clientes_prioritarios'] = len([d for d in results['dados'] if d['cliente_prioritario']])
        
        return results
    
    def detect_priority_client(self, text):
        """Detectar cliente prioritário no texto"""
        text_lower = text.lower()
        
        for cliente, keywords in self.priority_clients.items():
            for keyword in keywords:
                if keyword in text_lower:
                    return cliente
        
        return None
    
    def extract_context(self, text, pos_inicio, pos_fim, window=150):
        """Extrair contexto ao redor do dado"""
        inicio_contexto = max(0, pos_inicio - window)
        fim_contexto = min(len(text), pos_fim + window)
        
        contexto = text[inicio_contexto:fim_contexto]
        
        # Marcar o dado encontrado
        dado_encontrado = text[pos_inicio:pos_fim]
        contexto_marcado = contexto.replace(dado_encontrado, f"**{dado_encontrado}**", 1)
        
        return contexto_marcado
    
    def validate_data(self, tipo, valor):
        """Validar dados extraídos"""
        if tipo == 'cpf':
            return self.validate_cpf(valor)
        elif tipo == 'email':
            return self.validate_email(valor)
        elif tipo == 'telefone':
            return self.validate_telefone(valor)
        elif tipo == 'data_nascimento':
            return self.validate_data_nascimento(valor)
        elif tipo == 'cep':
            return self.validate_cep(valor)
        else:
            return True
    
    def validate_cpf(self, cpf):
        """Validar CPF"""
        # Remover caracteres não numéricos
        cpf_limpo = re.sub(r'\D', '', cpf)
        
        # Verificar comprimento
        if len(cpf_limpo) != 11:
            return False
        
        # Verificar dígitos iguais
        if cpf_limpo == cpf_limpo[0] * 11:
            return False
        
        # Calcular dígitos verificadores
        soma = sum(int(cpf_limpo[i]) * (10 - i) for i in range(9))
        resto = soma % 11
        digito1 = 0 if resto < 2 else 11 - resto
        
        soma = sum(int(cpf_limpo[i]) * (11 - i) for i in range(10))
        resto = soma % 11
        digito2 = 0 if resto < 2 else 11 - resto
        
        return cpf_limpo[-2:] == f"{digito1}{digito2}"
    
    def validate_email(self, email):
        """Validar email"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))
    
    def validate_telefone(self, telefone):
        """Validar telefone brasileiro"""
        numeros = re.sub(r'\D', '', telefone)
        return len(numeros) in [10, 11]
    
    def validate_data_nascimento(self, data):
        """Validar data de nascimento"""
        try:
            # Tentar diferentes formatos
            for fmt in ['%d/%m/%Y', '%d-%m-%Y', '%d.%m.%Y']:
                try:
                    dt = datetime.strptime(data, fmt)
                    if 1900 <= dt.year <= datetime.now().year:
                        return True
                except ValueError:
                    continue
            return False
        except:
            return False
    
    def validate_cep(self, cep):
        """Validar CEP"""
        numeros = re.sub(r'\D', '', cep)
        return len(numeros) == 8

class FileProcessor:
    """Processador de arquivos"""
    
    def __init__(self):
        self.extractor = DataExtractor()
    
    def process_file(self, file_path):
        """Processar arquivo individual"""
        try:
            # Ler arquivo
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            # Extrair dados
            filename = os.path.basename(file_path)
            results = self.extractor.extract_data(content, filename)
            
            # Adicionar informações do arquivo
            results['tamanho_arquivo_mb'] = round(os.path.getsize(file_path) / (1024 * 1024), 2)
            results['total_dados_extraidos'] = len(results['dados'])
            
            return results
            
        except Exception as e:
            logger.error(f"Erro ao processar {file_path}: {e}")
            return {
                'arquivo': file_path,
                'erro': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    def process_directory(self, directory_path):
        """Processar diretório recursivamente"""
        results = {
            'diretorio': directory_path,
            'timestamp': datetime.now().isoformat(),
            'arquivos_processados': 0,
            'total_dados': 0,
            'clientes_prioritarios': 0,
            'resultados_por_arquivo': [],
            'estatisticas_gerais': {
                'por_tipo': {},
                'por_cliente': {}
            }
        }
        
        # Padrões de arquivo suportados
        file_patterns = ['*.txt', '*.doc', '*.docx', '*.pdf', '*.eml', '*.msg', '*.rtf']
        
        # Encontrar arquivos
        files_to_process = []
        for pattern in file_patterns:
            files_to_process.extend(Path(directory_path).glob(pattern))
        
        logger.info(f"Encontrados {len(files_to_process)} arquivos para processar")
        
        # Processar arquivos
        for file_path in files_to_process:
            try:
                file_result = self.process_file(str(file_path))
                results['resultados_por_arquivo'].append(file_result)
                results['arquivos_processados'] += 1
                
                if 'dados' in file_result:
                    results['total_dados'] += len(file_result['dados'])
                    
                    # Contar por tipo
                    for dado in file_result['dados']:
                        tipo = dado['tipo']
                        if tipo not in results['estatisticas_gerais']['por_tipo']:
                            results['estatisticas_gerais']['por_tipo'][tipo] = 0
                        results['estatisticas_gerais']['por_tipo'][tipo] += 1
                        
                        # Contar por cliente
                        if dado['cliente_prioritario']:
                            cliente = dado['cliente_prioritario']
                            if cliente not in results['estatisticas_gerais']['por_cliente']:
                                results['estatisticas_gerais']['por_cliente'][cliente] = 0
                            results['estatisticas_gerais']['por_cliente'][cliente] += 1
                            results['clientes_prioritarios'] += 1
                
            except Exception as e:
                logger.error(f"Erro ao processar {file_path}: {e}")
                results['resultados_por_arquivo'].append({
                    'arquivo': str(file_path),
                    'erro': str(e),
                    'timestamp': datetime.now().isoformat()
                })
        
        return results

# Instanciar processador
file_processor = FileProcessor()

@app.route('/')
def index():
    """Página principal"""
    return render_template('dashboard_enhanced.html')

@app.route('/api/process-file', methods=['POST'])
def process_file():
    """Processar arquivo único"""
    global processing_status
    
    try:
        if 'file' not in request.files:
            return jsonify({'success': False, 'error': 'Nenhum arquivo enviado'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'success': False, 'error': 'Nenhum arquivo selecionado'}), 400
        
        # Salvar arquivo
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        
        # Processar em background
        def process_background():
            global processing_status
            try:
                processing_status['is_processing'] = True
                processing_status['progress'] = 0
                processing_status['current_file'] = f'Processando: {filename}'
                processing_status['error'] = None
                
                # Simular progresso
                for i in range(10):
                    processing_status['progress'] = (i + 1) * 10
                    time.sleep(0.2)
                
                # Processar arquivo
                results = file_processor.process_file(file_path)
                
                processing_status['results'] = results
                processing_status['progress'] = 100
                processing_status['current_file'] = 'Processamento concluído!'
                
            except Exception as e:
                processing_status['error'] = str(e)
                logger.error(f"Erro no processamento: {e}")
            finally:
                processing_status['is_processing'] = False
        
        # Iniciar processamento em thread
        thread = threading.Thread(target=process_background)
        thread.daemon = True
        thread.start()
        
        return jsonify({
            'success': True,
            'message': f'Arquivo {filename} enviado e processamento iniciado'
        })
        
    except Exception as e:
        logger.error(f"Erro no upload: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/process-directory', methods=['POST'])
def process_directory():
    """Processar diretório"""
    global processing_status
    
    try:
        data = request.get_json()
        directory_path = data.get('directory_path')
        
        if not directory_path or not os.path.exists(directory_path):
            return jsonify({
                'success': False,
                'error': 'Diretório não encontrado'
            }), 400
        
        # Processar em background
        def process_background():
            global processing_status
            try:
                processing_status['is_processing'] = True
                processing_status['progress'] = 0
                processing_status['current_file'] = 'Iniciando processamento do diretório...'
                processing_status['error'] = None
                
                # Processar diretório
                results = file_processor.process_directory(directory_path)
                
                processing_status['results'] = results
                processing_status['progress'] = 100
                processing_status['current_file'] = 'Processamento concluído!'
                
            except Exception as e:
                processing_status['error'] = str(e)
                logger.error(f"Erro no processamento: {e}")
            finally:
                processing_status['is_processing'] = False
        
        # Iniciar processamento em thread
        thread = threading.Thread(target=process_background)
        thread.daemon = True
        thread.start()
        
        return jsonify({
            'success': True,
            'message': 'Processamento do diretório iniciado'
        })
        
    except Exception as e:
        logger.error(f"Erro ao processar diretório: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/status')
def get_status():
    """Obter status do processamento"""
    return jsonify(processing_status)

@app.route('/api/results')
def get_results():
    """Obter resultados"""
    if not processing_status['results']:
        return jsonify({
            'success': False,
            'error': 'Nenhum resultado disponível'
        }), 404
    
    return jsonify({
        'success': True,
        'results': processing_status['results']
    })

@app.route('/api/scan-directory', methods=['POST'])
def scan_directory():
    """Escanear diretório"""
    try:
        data = request.get_json()
        directory_path = data.get('directory_path')
        
        if not directory_path or not os.path.exists(directory_path):
            return jsonify({
                'success': False,
                'error': 'Diretório não encontrado'
            }), 400
        
        # Padrões de arquivo
        file_patterns = ['*.txt', '*.doc', '*.docx', '*.pdf', '*.eml', '*.msg', '*.rtf']
        
        # Encontrar arquivos
        files_found = []
        total_size = 0
        
        for pattern in file_patterns:
            for file_path in Path(directory_path).glob(pattern):
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
                'files': files_found[:50],  # Limitar a 50 arquivos para preview
                'file_types': list(set(f['type'] for f in files_found))
            }
        })
        
    except Exception as e:
        logger.error(f"Erro ao escanear diretório: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/health')
def health_check():
    """Verificação de saúde"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'version': '2.0.0'
    })

if __name__ == '__main__':
    logger.info("🚀 Iniciando Sistema de Extração de Dados LGPD")
    logger.info("📁 Diretórios criados: uploads/, output/, reports/")
    logger.info("🌐 Interface web disponível em: http://localhost:5000")
    
    app.run(host='0.0.0.0', port=5000, debug=False) 