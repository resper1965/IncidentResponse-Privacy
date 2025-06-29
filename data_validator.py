#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sistema de Validação e Correção Automática de Dados
- Validação de integridade
- Correção automática de formatos
- Verificação de consistência
"""

import re
import json
import logging
from typing import List, Dict, Tuple, Optional
from datetime import datetime
from dataclasses import dataclass
from robust_data_extractor import ExtractedData

logger = logging.getLogger(__name__)

@dataclass
class ValidationResult:
    """Resultado da validação"""
    is_valid: bool
    confidence: float
    corrections: List[str]
    errors: List[str]
    warnings: List[str]

class DataValidator:
    """Validador de dados com correção automática"""
    
    def __init__(self):
        self.validation_rules = {
            'cpf': self._validate_cpf,
            'rg': self._validate_rg,
            'email': self._validate_email,
            'telefone': self._validate_telefone,
            'data_nascimento': self._validate_data,
            'cep': self._validate_cep,
            'placa_veiculo': self._validate_placa,
            'ip': self._validate_ip
        }
        
        self.correction_rules = {
            'cpf': self._correct_cpf,
            'rg': self._correct_rg,
            'email': self._correct_email,
            'telefone': self._correct_telefone,
            'data_nascimento': self._correct_data,
            'cep': self._correct_cep,
            'placa_veiculo': self._correct_placa,
            'ip': self._correct_ip
        }
    
    def validate_and_correct(self, dados: List[ExtractedData]) -> List[ExtractedData]:
        """Validar e corrigir todos os dados"""
        logger.info(f"🔍 Iniciando validação de {len(dados)} dados")
        
        dados_validados = []
        
        for dado in dados:
            try:
                # Validar dado
                validation_result = self._validate_single_data(dado)
                
                # Aplicar correções se necessário
                if not validation_result.is_valid and validation_result.corrections:
                    dado = self._apply_corrections(dado, validation_result.corrections)
                    # Re-validar após correção
                    validation_result = self._validate_single_data(dado)
                
                # Atualizar confiança baseado na validação
                dado.confianca = validation_result.confidence
                dado.validado = validation_result.is_valid
                
                # Adicionar metadados de validação
                if hasattr(dado, 'validation_metadata'):
                    dado.validation_metadata = {
                        'errors': validation_result.errors,
                        'warnings': validation_result.warnings,
                        'corrections_applied': validation_result.corrections
                    }
                
                dados_validados.append(dado)
                
                if validation_result.errors:
                    logger.warning(f"⚠️ Erros em {dado.tipo}: {validation_result.errors}")
                
            except Exception as e:
                logger.error(f"❌ Erro ao validar {dado.tipo}: {e}")
                dado.confianca = 0.0
                dado.validado = False
                dados_validados.append(dado)
        
        logger.info(f"✅ Validação concluída: {len([d for d in dados_validados if d.validado])} dados válidos")
        return dados_validados
    
    def _validate_single_data(self, dado: ExtractedData) -> ValidationResult:
        """Validar um dado específico"""
        validator_func = self.validation_rules.get(dado.tipo)
        if not validator_func:
            return ValidationResult(
                is_valid=False,
                confidence=0.0,
                corrections=[],
                errors=[f"Validador não encontrado para tipo: {dado.tipo}"],
                warnings=[]
            )
        
        return validator_func(dado.valor)
    
    def _apply_corrections(self, dado: ExtractedData, corrections: List[str]) -> ExtractedData:
        """Aplicar correções ao dado"""
        valor_corrigido = dado.valor
        
        for correction in corrections:
            if correction.startswith('format:'):
                # Correção de formato
                novo_formato = correction.split(':', 1)[1]
                valor_corrigido = self._apply_format_correction(dado.tipo, valor_corrigido, novo_formato)
            elif correction.startswith('replace:'):
                # Substituição específica
                _, old, new = correction.split(':', 2)
                valor_corrigido = valor_corrigido.replace(old, new)
        
        dado.valor = valor_corrigido
        return dado
    
    def _apply_format_correction(self, tipo: str, valor: str, formato: str) -> str:
        """Aplicar correção de formato"""
        if tipo == 'cpf':
            # Remover caracteres não numéricos e aplicar formato
            numeros = re.sub(r'\D', '', valor)
            if len(numeros) == 11:
                return f"{numeros[:3]}.{numeros[3:6]}.{numeros[6:9]}-{numeros[9:]}"
        
        elif tipo == 'telefone':
            # Formatar telefone brasileiro
            numeros = re.sub(r'\D', '', valor)
            if len(numeros) == 11:
                return f"({numeros[:2]}) {numeros[2:7]}-{numeros[7:]}"
            elif len(numeros) == 10:
                return f"({numeros[:2]}) {numeros[2:6]}-{numeros[6:]}"
        
        elif tipo == 'cep':
            # Formatar CEP
            numeros = re.sub(r'\D', '', valor)
            if len(numeros) == 8:
                return f"{numeros[:5]}-{numeros[5:]}"
        
        return valor
    
    # Validadores específicos
    def _validate_cpf(self, valor: str) -> ValidationResult:
        """Validar CPF"""
        errors = []
        warnings = []
        corrections = []
        
        # Limpar valor
        cpf_limpo = re.sub(r'\D', '', valor)
        
        # Verificar comprimento
        if len(cpf_limpo) != 11:
            errors.append("CPF deve ter 11 dígitos")
            if len(cpf_limpo) > 11:
                corrections.append(f"replace:{cpf_limpo[:11]}")
            return ValidationResult(False, 0.0, corrections, errors, warnings)
        
        # Verificar dígitos iguais
        if cpf_limpo == cpf_limpo[0] * 11:
            errors.append("CPF não pode ter todos os dígitos iguais")
            return ValidationResult(False, 0.0, corrections, errors, warnings)
        
        # Calcular dígitos verificadores
        soma = sum(int(cpf_limpo[i]) * (10 - i) for i in range(9))
        resto = soma % 11
        digito1 = 0 if resto < 2 else 11 - resto
        
        soma = sum(int(cpf_limpo[i]) * (11 - i) for i in range(10))
        resto = soma % 11
        digito2 = 0 if resto < 2 else 11 - resto
        
        # Verificar dígitos verificadores
        if cpf_limpo[-2:] != f"{digito1}{digito2}":
            errors.append("Dígitos verificadores inválidos")
            return ValidationResult(False, 0.0, corrections, errors, warnings)
        
        # Sugerir formatação se não estiver formatado
        if valor != f"{cpf_limpo[:3]}.{cpf_limpo[3:6]}.{cpf_limpo[6:9]}-{cpf_limpo[9:]}":
            corrections.append(f"format:{cpf_limpo[:3]}.{cpf_limpo[3:6]}.{cpf_limpo[6:9]}-{cpf_limpo[9:]}")
        
        return ValidationResult(True, 0.95, corrections, errors, warnings)
    
    def _validate_email(self, valor: str) -> ValidationResult:
        """Validar email"""
        errors = []
        warnings = []
        corrections = []
        
        # Padrão básico de email
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        
        if not re.match(pattern, valor):
            errors.append("Formato de email inválido")
            return ValidationResult(False, 0.0, corrections, errors, warnings)
        
        # Verificar domínio comum
        dominio = valor.split('@')[1].lower()
        dominios_comuns = ['gmail.com', 'hotmail.com', 'outlook.com', 'yahoo.com']
        if dominio not in dominios_comuns:
            warnings.append(f"Domínio não comum: {dominio}")
        
        return ValidationResult(True, 0.9, corrections, errors, warnings)
    
    def _validate_telefone(self, valor: str) -> ValidationResult:
        """Validar telefone brasileiro"""
        errors = []
        warnings = []
        corrections = []
        
        # Limpar valor
        numeros = re.sub(r'\D', '', valor)
        
        # Verificar comprimento
        if len(numeros) not in [10, 11]:
            errors.append("Telefone deve ter 10 ou 11 dígitos")
            return ValidationResult(False, 0.0, corrections, errors, warnings)
        
        # Verificar DDD válido
        ddd = numeros[:2]
        ddds_validos = [str(i).zfill(2) for i in range(11, 100)]
        if ddd not in ddds_validos:
            warnings.append(f"DDD pode ser inválido: {ddd}")
        
        # Sugerir formatação
        if len(numeros) == 11:
            formato_correto = f"({numeros[:2]}) {numeros[2:7]}-{numeros[7:]}"
        else:
            formato_correto = f"({numeros[:2]}) {numeros[2:6]}-{numeros[6:]}"
        
        if valor != formato_correto:
            corrections.append(f"format:{formato_correto}")
        
        return ValidationResult(True, 0.85, corrections, errors, warnings)
    
    def _validate_data(self, valor: str) -> ValidationResult:
        """Validar data de nascimento"""
        errors = []
        warnings = []
        corrections = []
        
        # Tentar diferentes formatos
        formatos = ['%d/%m/%Y', '%d-%m-%Y', '%d.%m.%Y', '%Y-%m-%d']
        
        for fmt in formatos:
            try:
                dt = datetime.strptime(valor, fmt)
                
                # Verificar se é uma data razoável
                ano_atual = datetime.now().year
                if dt.year < 1900 or dt.year > ano_atual:
                    warnings.append(f"Ano pode ser inválido: {dt.year}")
                
                if dt.year > ano_atual - 10:
                    warnings.append("Data pode ser muito recente para nascimento")
                
                # Sugerir formato padrão
                formato_padrao = dt.strftime('%d/%m/%Y')
                if valor != formato_padrao:
                    corrections.append(f"format:{formato_padrao}")
                
                return ValidationResult(True, 0.8, corrections, errors, warnings)
                
            except ValueError:
                continue
        
        errors.append("Formato de data inválido")
        return ValidationResult(False, 0.0, corrections, errors, warnings)
    
    def _validate_cep(self, valor: str) -> ValidationResult:
        """Validar CEP"""
        errors = []
        warnings = []
        corrections = []
        
        # Limpar valor
        numeros = re.sub(r'\D', '', valor)
        
        if len(numeros) != 8:
            errors.append("CEP deve ter 8 dígitos")
            return ValidationResult(False, 0.0, corrections, errors, warnings)
        
        # Sugerir formatação
        formato_correto = f"{numeros[:5]}-{numeros[5:]}"
        if valor != formato_correto:
            corrections.append(f"format:{formato_correto}")
        
        return ValidationResult(True, 0.9, corrections, errors, warnings)
    
    def _validate_rg(self, valor: str) -> ValidationResult:
        """Validar RG"""
        errors = []
        warnings = []
        corrections = []
        
        # Limpar valor
        numeros = re.sub(r'\D', '', valor)
        
        if len(numeros) < 7 or len(numeros) > 9:
            errors.append("RG deve ter entre 7 e 9 dígitos")
            return ValidationResult(False, 0.0, corrections, errors, warnings)
        
        return ValidationResult(True, 0.7, corrections, errors, warnings)
    
    def _validate_placa(self, valor: str) -> ValidationResult:
        """Validar placa de veículo"""
        errors = []
        warnings = []
        corrections = []
        
        # Padrão brasileiro: ABC-1234
        pattern = r'^[A-Z]{3}[-\s]?\d{4}$'
        
        if not re.match(pattern, valor.upper()):
            errors.append("Formato de placa inválido")
            return ValidationResult(False, 0.0, corrections, errors, warnings)
        
        # Sugerir formatação
        placa_limpa = re.sub(r'[-\s]', '', valor.upper())
        formato_correto = f"{placa_limpa[:3]}-{placa_limpa[3:]}"
        
        if valor.upper() != formato_correto:
            corrections.append(f"format:{formato_correto}")
        
        return ValidationResult(True, 0.9, corrections, errors, warnings)
    
    def _validate_ip(self, valor: str) -> ValidationResult:
        """Validar endereço IP"""
        errors = []
        warnings = []
        corrections = []
        
        # Padrão IPv4
        pattern = r'^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$'
        
        if not re.match(pattern, valor):
            errors.append("Formato de IP inválido")
            return ValidationResult(False, 0.0, corrections, errors, warnings)
        
        # Verificar IPs reservados
        octetos = [int(x) for x in valor.split('.')]
        if octetos[0] in [0, 127, 10, 172, 192]:
            warnings.append("IP pode ser reservado/privado")
        
        return ValidationResult(True, 0.95, corrections, errors, warnings)
    
    # Funções de correção (implementações básicas)
    def _correct_cpf(self, valor: str) -> str:
        """Corrigir CPF"""
        return self._apply_format_correction('cpf', valor, '')
    
    def _correct_rg(self, valor: str) -> str:
        """Corrigir RG"""
        return re.sub(r'\D', '', valor)
    
    def _correct_email(self, valor: str) -> str:
        """Corrigir email"""
        return valor.lower().strip()
    
    def _correct_telefone(self, valor: str) -> str:
        """Corrigir telefone"""
        return self._apply_format_correction('telefone', valor, '')
    
    def _correct_data(self, valor: str) -> str:
        """Corrigir data"""
        return self._apply_format_correction('data_nascimento', valor, '')
    
    def _correct_cep(self, valor: str) -> str:
        """Corrigir CEP"""
        return self._apply_format_correction('cep', valor, '')
    
    def _correct_placa(self, valor: str) -> str:
        """Corrigir placa"""
        return self._apply_format_correction('placa_veiculo', valor, '')
    
    def _correct_ip(self, valor: str) -> str:
        """Corrigir IP"""
        return valor.strip()

# Função principal
def validar_e_corrigir_dados(dados: List[ExtractedData]) -> List[ExtractedData]:
    """Função principal para validação e correção"""
    validator = DataValidator()
    return validator.validate_and_correct(dados)

if __name__ == "__main__":
    # Teste do validador
    from robust_data_extractor import extrair_dados_robusto
    
    texto_teste = """
    CPF: 123.456.789-00
    Email: TESTE@GMAIL.COM
    Telefone: 11999999999
    Data: 15/3/1985
    CEP: 01234567
    """
    
    # Extrair dados
    resultado = extrair_dados_robusto(texto_teste, "teste.txt")
    dados = [ExtractedData(**d) for d in resultado['dados']]
    
    # Validar e corrigir
    dados_validados = validar_e_corrigir_dados(dados)
    
    print("Dados após validação e correção:")
    for dado in dados_validados:
        print(f"{dado.tipo}: {dado.valor} (válido: {dado.validado}, confiança: {dado.confianca})") 