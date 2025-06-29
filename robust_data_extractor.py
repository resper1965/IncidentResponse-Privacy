#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sistema Robusto de Extração de Dados LGPD
- Regex garantido para todos os dados
- IA semântica para clientes prioritários
- Validação e correção automática
"""

import re
try:
    import spacy
    SPACY_AVAILABLE = True
except ImportError:
    spacy = None
    SPACY_AVAILABLE = False
import json
import logging
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
from datetime import datetime
import hashlib

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class ExtractedData:
    """Estrutura para dados extraídos"""
    tipo: str
    valor: str
    contexto: str
    confianca: float
    metodo: str  # 'regex', 'ia_semantica', 'hibrido'
    posicao_inicio: int
    posicao_fim: int
    hash_valor: str
    validado: bool = False
    cliente_prioritario: Optional[str] = None
    validation_metadata: Optional[Dict] = None

class RegexPatterns:
    """Padrões regex robustos para dados brasileiros"""
    
    PATTERNS = {
        'cpf': {
            'pattern': r'\b\d{3}[.\s-]?\d{3}[.\s-]?\d{3}[-\s]?\d{2}\b',
            'validation': r'^\d{11}$',
            'priority': 'alta'
        },
        'rg': {
            'pattern': r'\b\d{1,2}[.\s-]?\d{3}[.\s-]?\d{3}[-\s]?[0-9Xx]\b',
            'validation': r'^\d{7,9}$',
            'priority': 'alta'
        },
        'email': {
            'pattern': r'\b[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}\b',
            'validation': r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$',
            'priority': 'alta'
        },
        'telefone': {
            'pattern': r'\b(\(?\d{2}\)?[\s-]?)?(9?\d{4})[\s-]?\d{4}\b',
            'validation': r'^\d{10,11}$',
            'priority': 'media'
        },
        'data_nascimento': {
            'pattern': r'\b(0?[1-9]|[12][0-9]|3[01])[/\-\.](0?[1-9]|1[0-2])[/\-\.](?:19|20)?\d{2}\b',
            'validation': r'^\d{2}[/\-\.]\d{2}[/\-\.]\d{4}$',
            'priority': 'media'
        },
        'cep': {
            'pattern': r'\b\d{5}[-\s]?\d{3}\b',
            'validation': r'^\d{8}$',
            'priority': 'baixa'
        },
        'placa_veiculo': {
            'pattern': r'\b([A-Z]{3}[-\s]?\d{4})\b',
            'validation': r'^[A-Z]{3}\d{4}$',
            'priority': 'baixa'
        },
        'ip': {
            'pattern': r'\b(?:\d{1,3}\.){3}\d{1,3}\b',
            'validation': r'^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$',
            'priority': 'media'
        }
    }
    
    @classmethod
    def get_pattern(cls, tipo: str) -> Dict:
        """Obter padrão específico"""
        return cls.PATTERNS.get(tipo, {})
    
    @classmethod
    def validate_value(cls, tipo: str, valor: str) -> bool:
        """Validar valor usando regex de validação"""
        pattern_info = cls.get_pattern(tipo)
        if not pattern_info:
            return False
        
        # Limpar valor para validação
        valor_limpo = re.sub(r'[.\s-]', '', valor)
        
        # Aplicar validação específica
        if tipo == 'cpf':
            return cls._validate_cpf(valor_limpo)
        elif tipo == 'email':
            return bool(re.match(pattern_info['validation'], valor))
        elif tipo == 'telefone':
            return len(valor_limpo) in [10, 11]
        elif tipo == 'data_nascimento':
            return cls._validate_date(valor)
        else:
            return bool(re.match(pattern_info['validation'], valor_limpo))
    
    @staticmethod
    def _validate_cpf(cpf: str) -> bool:
        """Validar CPF usando algoritmo oficial"""
        if len(cpf) != 11 or cpf == cpf[0] * 11:
            return False
        
        # Calcular dígitos verificadores
        soma = sum(int(cpf[i]) * (10 - i) for i in range(9))
        resto = soma % 11
        digito1 = 0 if resto < 2 else 11 - resto
        
        soma = sum(int(cpf[i]) * (11 - i) for i in range(10))
        resto = soma % 11
        digito2 = 0 if resto < 2 else 11 - resto
        
        return cpf[-2:] == f"{digito1}{digito2}"
    
    @staticmethod
    def _validate_date(data: str) -> bool:
        """Validar data de nascimento"""
        try:
            # Tentar diferentes formatos
            for fmt in ['%d/%m/%Y', '%d-%m-%Y', '%d.%m.%Y']:
                try:
                    dt = datetime.strptime(data, fmt)
                    # Verificar se é uma data razoável
                    if 1900 <= dt.year <= datetime.now().year:
                        return True
                except ValueError:
                    continue
            return False
        except:
            return False

class SemanticAI:
    """IA Semântica para refinamento de dados"""
    
    def __init__(self):
        self.nlp = None
        self.clientes_prioritarios = {
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
    
    def initialize_spacy(self):
        """Inicializar spaCy"""
        if not SPACY_AVAILABLE:
            logger.warning("⚠️ spaCy não disponível, usando fallback")
            self.nlp = None
            return
            
        try:
            if spacy is not None:
                self.nlp = spacy.load("pt_core_news_sm")
                logger.info("✅ spaCy inicializado com sucesso")
            else:
                self.nlp = None
        except OSError:
            logger.warning("⚠️ spaCy não disponível, usando fallback")
            self.nlp = None
    
    def detect_priority_client(self, texto: str) -> Optional[str]:
        """Detectar cliente prioritário no texto"""
        texto_lower = texto.lower()
        
        for cliente, keywords in self.clientes_prioritarios.items():
            for keyword in keywords:
                if keyword in texto_lower:
                    return cliente
        
        return None
    
    def extract_semantic_context(self, texto: str, posicao_inicio: int, posicao_fim: int) -> Dict:
        """Extrair contexto semântico ao redor do dado"""
        if not self.nlp:
            return {'entidades': [], 'confianca': 0.0}
        
        # Extrair contexto
        contexto_inicio = max(0, posicao_inicio - 200)
        contexto_fim = min(len(texto), posicao_fim + 200)
        contexto = texto[contexto_inicio:contexto_fim]
        
        # Processar com spaCy
        doc = self.nlp(contexto)
        
        entidades = []
        for ent in doc.ents:
            if ent.label_ in ['PER', 'ORG', 'LOC']:
                entidades.append({
                    'texto': ent.text,
                    'tipo': ent.label_,
                    'confianca': ent.prob
                })
        
        return {
            'entidades': entidades,
            'confianca': sum(ent['confianca'] for ent in entidades) / len(entidades) if entidades else 0.0
        }
    
    def refine_extraction(self, dados_regex: List[ExtractedData], texto: str) -> List[ExtractedData]:
        """Refinar extração usando IA semântica"""
        if not self.nlp:
            return dados_regex
        
        dados_refinados = []
        
        for dado in dados_regex:
            # Detectar cliente prioritário
            cliente = self.detect_priority_client(texto)
            if cliente:
                dado.cliente_prioritario = cliente
                
                # Extrair contexto semântico
                contexto_semantico = self.extract_semantic_context(
                    texto, dado.posicao_inicio, dado.posicao_fim
                )
                
                # Ajustar confiança baseado no contexto semântico
                if contexto_semantico['entidades']:
                    dado.confianca = min(1.0, dado.confianca + 0.2)
                    dado.metodo = 'hibrido'
                
                # Validar com regras semânticas específicas
                if self._validate_semantic_rules(dado, contexto_semantico):
                    dado.validado = True
            
            dados_refinados.append(dado)
        
        return dados_refinados
    
    def _validate_semantic_rules(self, dado: ExtractedData, contexto: Dict) -> bool:
        """Validar dados usando regras semânticas"""
        if dado.tipo == 'cpf':
            # Verificar se há nome de pessoa próximo
            pessoas_proximas = [e for e in contexto['entidades'] if e['tipo'] == 'PER']
            return len(pessoas_proximas) > 0
        
        elif dado.tipo == 'email':
            # Verificar se há organização relacionada
            orgs_proximas = [e for e in contexto['entidades'] if e['tipo'] == 'ORG']
            return len(orgs_proximas) > 0
        
        elif dado.tipo == 'telefone':
            # Verificar se há contexto de contato
            return 'contato' in dado.contexto.lower() or 'telefone' in dado.contexto.lower()
        
        return True

class RobustDataExtractor:
    """Extrator robusto de dados com regex garantido e IA semântica"""
    
    def __init__(self):
        self.regex_patterns = RegexPatterns()
        self.semantic_ai = SemanticAI()
        self.semantic_ai.initialize_spacy()
        
        # Estatísticas
        self.stats = {
            'total_extraidos': 0,
            'validados_regex': 0,
            'refinados_ia': 0,
            'clientes_prioritarios': 0,
            'erros': 0
        }
    
    def extract_all_data(self, texto: str, arquivo: str) -> List[ExtractedData]:
        """Extrair todos os dados do texto"""
        logger.info(f"🔍 Iniciando extração de dados de: {arquivo}")
        
        dados_extraidos = []
        
        # 1. Extração com regex garantido
        for tipo, pattern_info in self.regex_patterns.PATTERNS.items():
            try:
                dados_tipo = self._extract_by_type(texto, tipo, pattern_info)
                dados_extraidos.extend(dados_tipo)
                self.stats['total_extraidos'] += len(dados_tipo)
                self.stats['validados_regex'] += len([d for d in dados_tipo if d.validado])
                
            except Exception as e:
                logger.error(f"❌ Erro ao extrair {tipo}: {e}")
                self.stats['erros'] += 1
        
        # 2. Refinamento com IA semântica
        if dados_extraidos:
            dados_refinados = self.semantic_ai.refine_extraction(dados_extraidos, texto)
            
            # Contar refinamentos
            self.stats['refinados_ia'] = len([d for d in dados_refinados if d.metodo == 'hibrido'])
            self.stats['clientes_prioritarios'] = len([d for d in dados_refinados if d.cliente_prioritario])
            
            dados_extraidos = dados_refinados
        
        # 3. Remover duplicatas
        dados_unicos = self._remove_duplicates(dados_extraidos)
        
        logger.info(f"✅ Extração concluída: {len(dados_unicos)} dados únicos")
        return dados_unicos
    
    def _extract_by_type(self, texto: str, tipo: str, pattern_info: Dict) -> List[ExtractedData]:
        """Extrair dados de um tipo específico"""
        dados = []
        pattern = pattern_info['pattern']
        
        for match in re.finditer(pattern, texto, re.IGNORECASE):
            valor = match.group(0)
            pos_inicio = match.start()
            pos_fim = match.end()
            
            # Extrair contexto
            contexto = self._extract_context(texto, pos_inicio, pos_fim)
            
            # Validar valor
            validado = self.regex_patterns.validate_value(tipo, valor)
            
            # Calcular hash
            hash_valor = hashlib.md5(valor.encode()).hexdigest()
            
            # Criar objeto de dados
            dado = ExtractedData(
                tipo=tipo,
                valor=valor,
                contexto=contexto,
                confianca=0.9 if validado else 0.5,
                metodo='regex',
                posicao_inicio=pos_inicio,
                posicao_fim=pos_fim,
                hash_valor=hash_valor,
                validado=validado
            )
            
            dados.append(dado)
        
        return dados
    
    def _extract_context(self, texto: str, pos_inicio: int, pos_fim: int, janela: int = 150) -> str:
        """Extrair contexto ao redor do dado"""
        inicio_contexto = max(0, pos_inicio - janela)
        fim_contexto = min(len(texto), pos_fim + janela)
        
        contexto = texto[inicio_contexto:fim_contexto]
        
        # Marcar o dado encontrado
        dado_encontrado = texto[pos_inicio:pos_fim]
        contexto_marcado = contexto.replace(
            dado_encontrado, 
            f"**{dado_encontrado}**", 
            1
        )
        
        return contexto_marcado
    
    def _remove_duplicates(self, dados: List[ExtractedData]) -> List[ExtractedData]:
        """Remover dados duplicados baseado no hash"""
        seen_hashes = set()
        dados_unicos = []
        
        for dado in dados:
            if dado.hash_valor not in seen_hashes:
                seen_hashes.add(dado.hash_valor)
                dados_unicos.append(dado)
        
        return dados_unicos
    
    def get_stats(self) -> Dict:
        """Obter estatísticas da extração"""
        return self.stats.copy()
    
    def export_results(self, dados: List[ExtractedData], arquivo: str) -> Dict:
        """Exportar resultados em formato estruturado"""
        return {
            'arquivo': arquivo,
            'timestamp': datetime.now().isoformat(),
            'total_dados': len(dados),
            'estatisticas': self.get_stats(),
            'dados': [
                {
                    'tipo': d.tipo,
                    'valor': d.valor,
                    'contexto': d.contexto,
                    'confianca': d.confianca,
                    'metodo': d.metodo,
                    'validado': d.validado,
                    'cliente_prioritario': d.cliente_prioritario,
                    'hash': d.hash_valor
                }
                for d in dados
            ]
        }

# Função principal para uso
def extrair_dados_robusto(texto: str, arquivo: str) -> Dict:
    """Função principal para extração robusta de dados"""
    extractor = RobustDataExtractor()
    dados = extractor.extract_all_data(texto, arquivo)
    return extractor.export_results(dados, arquivo)

if __name__ == "__main__":
    # Teste do sistema
    texto_teste = """
    Cliente: João Silva
    CPF: 123.456.789-00
    Email: joao.silva@bradesco.com.br
    Telefone: (11) 99999-9999
    Data de Nascimento: 15/03/1985
    
    Documento da Petrobras S.A.
    Funcionário: Maria Santos
    CPF: 987.654.321-00
    Email: maria.santos@petrobras.com.br
    """
    
    resultado = extrair_dados_robusto(texto_teste, "teste.txt")
    print(json.dumps(resultado, indent=2, ensure_ascii=False)) 