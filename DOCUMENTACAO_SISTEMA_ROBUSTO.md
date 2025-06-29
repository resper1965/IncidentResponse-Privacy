# Sistema Robusto de Extração de Dados LGPD - Documentação Completa

## 📋 Visão Geral

O **Sistema Robusto de Extração de Dados LGPD** é uma solução avançada para análise e conformidade com a Lei Geral de Proteção de Dados (LGPD), desenvolvida pela n.crisisops. O sistema combina **regex garantido** com **IA semântica** para fornecer extração de dados precisa e confiável.

### 🎯 Objetivos Principais

1. **Extração Garantida**: Regex robustos para todos os tipos de dados brasileiros
2. **IA Semântica**: Refinamento automático para clientes prioritários
3. **Validação Automática**: Correção e validação de dados em tempo real
4. **Processamento Integrado**: Sistema completo de análise e relatórios

---

## 🏗️ Arquitetura do Sistema

### Componentes Principais

```
┌─────────────────────────────────────────────────────────────┐
│                    Sistema Robusto LGPD                     │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────────┐  ┌─────────────────┐  ┌──────────────┐ │
│  │ Robust Data     │  │ Data Validator  │  │ Integrated   │ │
│  │ Extractor       │  │                 │  │ Processor    │ │
│  │                 │  │                 │  │              │ │
│  │ • Regex Patterns│  │ • Validation    │  │ • Batch      │ │
│  │ • Semantic AI   │  │ • Auto-Correction│  │   Processing │ │
│  │ • Context       │  │ • Integrity     │  │ • Reports    │ │
│  │   Detection     │  │   Checks        │  │ • Statistics │ │
│  └─────────────────┘  └─────────────────┘  └──────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

### Fluxo de Processamento

1. **Entrada**: Arquivo ou diretório de documentos
2. **Extração**: Regex robustos + detecção de contexto
3. **Validação**: Verificação de integridade + correção automática
4. **IA Semântica**: Refinamento para clientes prioritários
5. **Filtragem**: Aplicação de threshold de confiança
6. **Saída**: Dados estruturados + relatórios detalhados

---

## 🔍 Sistema de Extração Robusta

### RegexPatterns Class

```python
class RegexPatterns:
    PATTERNS = {
        'cpf': {
            'pattern': r'\b\d{3}[.\s-]?\d{3}[.\s-]?\d{3}[-\s]?\d{2}\b',
            'validation': r'^\d{11}$',
            'priority': 'alta'
        },
        'email': {
            'pattern': r'\b[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}\b',
            'validation': r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$',
            'priority': 'alta'
        },
        # ... outros padrões
    }
```

### Tipos de Dados Suportados

| Tipo | Padrão | Validação | Prioridade |
|------|--------|-----------|------------|
| CPF | `123.456.789-00` | Algoritmo oficial | Alta |
| Email | `usuario@dominio.com` | RFC 5322 | Alta |
| Telefone | `(11) 99999-9999` | DDD + formato | Média |
| Data | `15/03/1985` | Múltiplos formatos | Média |
| CEP | `01234-567` | 8 dígitos | Baixa |
| RG | `12.345.678-9` | 7-9 dígitos | Média |
| Placa | `ABC-1234` | Formato brasileiro | Baixa |
| IP | `192.168.1.1` | IPv4 válido | Média |

### Validação de CPF

```python
def _validate_cpf(cpf: str) -> bool:
    # Remove caracteres não numéricos
    cpf_limpo = re.sub(r'\D', '', cpf)
    
    # Verifica comprimento
    if len(cpf_limpo) != 11:
        return False
    
    # Verifica dígitos iguais
    if cpf_limpo == cpf_limpo[0] * 11:
        return False
    
    # Calcula dígitos verificadores
    soma = sum(int(cpf_limpo[i]) * (10 - i) for i in range(9))
    resto = soma % 11
    digito1 = 0 if resto < 2 else 11 - resto
    
    soma = sum(int(cpf_limpo[i]) * (11 - i) for i in range(10))
    resto = soma % 11
    digito2 = 0 if resto < 2 else 11 - resto
    
    return cpf_limpo[-2:] == f"{digito1}{digito2}"
```

---

## 🤖 IA Semântica para Clientes Prioritários

### Clientes Prioritários Configurados

```python
clientes_prioritarios = {
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
```

### Processo de Refinamento Semântico

1. **Detecção de Cliente**: Identifica clientes prioritários no texto
2. **Análise de Contexto**: Extrai contexto semântico ao redor dos dados
3. **Validação Semântica**: Aplica regras específicas por tipo de dado
4. **Boost de Confiança**: Aumenta confiança para dados de clientes prioritários

### Exemplo de Análise Semântica

```python
def refine_extraction(self, dados_regex, texto):
    for dado in dados_regex:
        # Detectar cliente prioritário
        cliente = self.detect_priority_client(texto)
        if cliente:
            dado.cliente_prioritario = cliente
            
            # Extrair contexto semântico
            contexto = self.extract_semantic_context(
                texto, dado.posicao_inicio, dado.posicao_fim
            )
            
            # Ajustar confiança
            if contexto['entidades']:
                dado.confianca = min(1.0, dado.confianca + 0.2)
                dado.metodo = 'hibrido'
```

---

## ✅ Sistema de Validação e Correção

### ValidationResult Structure

```python
@dataclass
class ValidationResult:
    is_valid: bool
    confidence: float
    corrections: List[str]
    errors: List[str]
    warnings: List[str]
```

### Tipos de Correção

1. **Formatação**: Aplica formatos padrão (CPF, telefone, CEP)
2. **Substituição**: Corrige caracteres incorretos
3. **Validação**: Verifica integridade dos dados
4. **Normalização**: Padroniza formatos

### Exemplo de Correção Automática

```python
def _apply_format_correction(self, tipo: str, valor: str, formato: str) -> str:
    if tipo == 'cpf':
        numeros = re.sub(r'\D', '', valor)
        if len(numeros) == 11:
            return f"{numeros[:3]}.{numeros[3:6]}.{numeros[6:9]}-{numeros[9:]}"
    
    elif tipo == 'telefone':
        numeros = re.sub(r'\D', '', valor)
        if len(numeros) == 11:
            return f"({numeros[:2]}) {numeros[2:7]}-{numeros[7:]}"
    
    return valor
```

---

## 📊 Processamento Integrado

### Configuração do Sistema

```json
{
  "output_dir": "output",
  "reports_dir": "reports",
  "enable_semantic_ai": true,
  "priority_clients": ["bradesco", "petrobras", "ons"],
  "validation_threshold": 0.7,
  "max_file_size_mb": 100,
  "semantic_ai": {
    "enable_ner": true,
    "confidence_boost_priority": 0.1
  }
}
```

### Uso do Processador

```python
# Processar arquivo único
resultado = processar_dados_lgpd('documento.txt')

# Processar diretório
resultado = processar_dados_lgpd('/caminho/diretorio')

# Com configuração personalizada
resultado = processar_dados_lgpd('arquivo.txt', 'config.json')
```

### Estrutura de Saída

```json
{
  "arquivo": "documento.txt",
  "timestamp": "2024-01-15T10:30:00",
  "total_dados_extraidos": 5,
  "dados_validados": 4,
  "dados_finais": 3,
  "clientes_prioritarios": 1,
  "dados": [
    {
      "tipo": "cpf",
      "valor": "123.456.789-00",
      "contexto": "...",
      "confianca": 0.95,
      "metodo": "hibrido",
      "validado": true,
      "cliente_prioritario": "bradesco"
    }
  ]
}
```

---

## 🚀 Instalação e Configuração

### Pré-requisitos

- Python 3.8+
- Linux/Ubuntu 20.04+
- 4GB RAM mínimo
- 10GB espaço em disco

### Instalação Automática

```bash
# Baixar script de instalação
wget https://raw.githubusercontent.com/seu-repo/install_enhanced_system.sh

# Executar instalação
chmod +x install_enhanced_system.sh
./install_enhanced_system.sh
```

### Instalação Manual

```bash
# 1. Criar ambiente virtual
python3 -m venv venv
source venv/bin/activate

# 2. Instalar dependências
pip install -r requirements_enhanced.txt

# 3. Instalar spaCy
python -m spacy download pt_core_news_sm

# 4. Configurar serviços
sudo systemctl enable privacy-enhanced
sudo systemctl start privacy-enhanced
```

---

## 📈 Monitoramento e Logs

### Logs do Sistema

```bash
# Logs do processador
tail -f logs/processor.log

# Logs do serviço
sudo journalctl -u privacy-enhanced -f

# Logs do nginx
sudo tail -f /var/log/nginx/access.log
```

### Métricas de Performance

- **Taxa de Extração**: % de dados extraídos com sucesso
- **Precisão**: % de dados validados corretamente
- **Tempo de Processamento**: Tempo médio por arquivo
- **Clientes Prioritários**: Quantidade detectada

### Alertas e Notificações

```python
# Configurar alertas para clientes prioritários
if dado.cliente_prioritario:
    send_alert(f"Cliente prioritário detectado: {dado.cliente_prioritario}")
```

---

## 🔧 Manutenção e Troubleshooting

### Comandos Úteis

```bash
# Status dos serviços
sudo systemctl status privacy-enhanced
sudo systemctl status nginx

# Reiniciar serviços
sudo systemctl restart privacy-enhanced
sudo systemctl restart nginx

# Verificar logs
sudo journalctl -u privacy-enhanced --no-pager

# Testar sistema
python test_system.py
```

### Problemas Comuns

#### 1. spaCy não disponível
```bash
# Reinstalar spaCy
pip uninstall spacy
pip install spacy
python -m spacy download pt_core_news_sm
```

#### 2. Erro de permissão
```bash
# Corrigir permissões
sudo chown -R $USER:$USER /opt/privacy-lgpd-enhanced
chmod +x *.py *.sh
```

#### 3. Serviço não inicia
```bash
# Verificar configuração
sudo systemctl daemon-reload
sudo systemctl status privacy-enhanced
```

---

## 📋 Exemplos de Uso

### Exemplo 1: Processamento de Documento

```python
from integrated_processor import processar_dados_lgpd

# Processar documento
resultado = processar_dados_lgpd('relatorio_bradesco.txt')

# Verificar dados extraídos
for dado in resultado['resultado']['dados']:
    print(f"{dado['tipo']}: {dado['valor']} (confiança: {dado['confianca']})")
```

### Exemplo 2: Processamento em Lote

```python
# Processar diretório completo
resultado = processar_dados_lgpd('/caminho/documentos/')

# Relatório consolidado
resumo = resultado['resultado']['resumo']
print(f"Arquivos processados: {resumo['total_arquivos']}")
print(f"Taxa de sucesso: {resumo['taxa_sucesso']:.1f}%")
```

### Exemplo 3: Configuração Personalizada

```json
{
  "enable_semantic_ai": true,
  "priority_clients": ["minha_empresa"],
  "validation_threshold": 0.8,
  "semantic_ai": {
    "confidence_boost_priority": 0.15
  }
}
```

---

## 🔒 Segurança e Conformidade

### Proteção de Dados

- **Criptografia**: Dados sensíveis criptografados em repouso
- **Acesso**: Controle de acesso baseado em roles
- **Auditoria**: Logs completos de todas as operações
- **Retenção**: Política de retenção de dados configurável

### Conformidade LGPD

- **Minimização**: Extrai apenas dados necessários
- **Transparência**: Relatórios detalhados de processamento
- **Responsabilização**: Rastreabilidade completa
- **Direitos**: Suporte aos direitos do titular

---

## 📞 Suporte e Contato

### Documentação Adicional

- [Guia de Configuração](config_processor.json)
- [Exemplos de Uso](examples/)
- [FAQ](docs/FAQ.md)

### Contato

- **Email**: suporte@n-crisisops.com
- **Telefone**: +55 11 99999-9999
- **Documentação**: https://docs.n-crisisops.com

### Comunidade

- **GitHub**: https://github.com/n-crisisops/privacy-lgpd
- **Issues**: https://github.com/n-crisisops/privacy-lgpd/issues
- **Discussions**: https://github.com/n-crisisops/privacy-lgpd/discussions

---

## 📄 Licença

Este software é licenciado sob a Licença MIT. Veja o arquivo [LICENSE](LICENSE) para mais detalhes.

---

*Documentação gerada em: 2024-01-15*
*Versão do sistema: 2.0.0*
*Última atualização: 2024-01-15* 