# n.crisisops - Sistema de Compliance LGPD

## Visão Geral

**n.crisisops** é um sistema completo de compliance para a Lei Geral de Proteção de Dados (LGPD) que automatiza o processamento de documentos, extrai dados pessoais usando inteligência artificial e fornece dashboards em tempo real para monitoramento de conformidade.

### Características Principais

- **Processamento Automatizado**: Escaneia 18+ formatos de arquivo (PDF, DOCX, XLSX, MSG, etc.)
- **IA Avançada**: Integração com GPT-3.5-turbo-1106 para análise semântica e classificação inteligente
- **Base de Dados Empresarial**: PostgreSQL com suporte a SQLite para flexibilidade
- **Processamento Prioritário**: Sistema de classificação automática para empresas estratégicas
- **Interface Moderna**: Dashboard web responsivo com monitoramento em tempo real
- **Exportação Excel**: Relatórios filtráveis por domínio e empresa
- **OCR Integrado**: Processamento de documentos escaneados com Tesseract

## Tecnologias

### Backend
- **Python 3.12** - Linguagem principal
- **Flask** - Framework web
- **SQLAlchemy** - ORM para banco de dados
- **PostgreSQL** - Banco de dados principal
- **spaCy** - Processamento de linguagem natural
- **OpenAI GPT-3.5-turbo** - Análise semântica avançada

### Frontend
- **HTML5/CSS3** - Interface responsiva
- **JavaScript** - Interatividade
- **Plotly** - Visualizações interativas
- **Montserrat Font** - Tipografia moderna

### Infraestrutura
- **Gunicorn** - Servidor WSGI
- **Nginx** - Proxy reverso
- **systemd** - Gerenciamento de serviços
- **Ubuntu/Debian** - Sistema operacional

## Estrutura do Projeto

```
n.crisisops/
├── scripts/                 # Scripts de instalação e deploy
│   ├── install_service.sh   # Instalação completa da infraestrutura
│   ├── deploy.sh           # Deploy automatizado
│   ├── fix_502.sh          # Correção de problemas
│   ├── debug_service.sh    # Diagnóstico do sistema
│   └── test_postgresql.sh  # Teste de conectividade
├── docs/                   # Documentação
│   ├── README_DEPLOY.md    # Guia de deploy
│   ├── DIAGNOSTICO_502.md  # Troubleshooting
│   └── replit.md          # Arquitetura do projeto
├── templates/              # Templates HTML
│   └── dashboard.html     # Interface principal
├── data/                  # Diretório de dados para processamento
├── web_interface.py       # Aplicação Flask principal
├── database_postgresql.py # Camada de dados PostgreSQL
├── file_reader.py         # Leitura multi-formato
├── data_extractor.py      # Extração de dados pessoais
├── file_scanner.py        # Varredura de diretórios
├── ai_super_processor.py  # Processamento com IA
├── ai_processor_simplified.py # IA simplificada
├── main.py               # Pipeline principal
└── pyproject.toml        # Configuração do projeto
```

## Instalação Rápida

### Pré-requisitos
- Ubuntu/Debian 20.04+
- Acesso root ao servidor
- Domínio configurado (opcional)

### Deploy Automatizado

```bash
# Clonar repositório
git clone https://github.com/seu-usuario/n.crisisops.git
cd n.crisisops

# Executar deploy completo
chmod +x scripts/deploy.sh
./scripts/deploy.sh
```

### Instalação Manual

```bash
# 1. Instalar infraestrutura
chmod +x scripts/install_service.sh
sudo ./scripts/install_service.sh

# 2. Copiar arquivos da aplicação
sudo cp *.py /opt/privacy/app/
sudo cp -r templates /opt/privacy/app/

# 3. Iniciar serviço
sudo systemctl start privacy
sudo systemctl enable privacy
```

## Configuração

### Variáveis de Ambiente

Crie o arquivo `/opt/privacy/app/.env`:

```env
# PostgreSQL
DATABASE_URL=postgresql://privacy:senha@localhost:5432/privacy
PGHOST=localhost
PGPORT=5432
PGDATABASE=privacy
PGUSER=privacy
PGPASSWORD=senha

# OpenAI (opcional)
OPENAI_API_KEY=sk-...

# Aplicação
FLASK_ENV=production
SECRET_KEY=sua-chave-secreta
PORT=5000
```

### Empresas Prioritárias

Configure empresas para processamento prioritário através do dashboard ou diretamente no banco:

```sql
INSERT INTO search_priorities (priority, company_name, email_domain) VALUES
(1, 'BRADESCO', 'bradesco.com.br'),
(2, 'PETROBRAS', 'petrobras.com.br'),
(3, 'EMBRAER', 'embraer.com.br');
```

## Uso

### Interface Web

1. Acesse `http://seu-servidor:5000`
2. Selecione o diretório para processamento
3. Configure empresas prioritárias
4. Execute o processamento
5. Visualize relatórios e exporte dados

### API Endpoints

```bash
# Health check
curl http://localhost:5000/health

# Processar diretório
curl -X POST http://localhost:5000/processar \
  -H "Content-Type: application/json" \
  -d '{"caminho": "/path/to/documents"}'

# Exportar dados
curl http://localhost:5000/exportar/excel
```

### Linha de Comando

```bash
# Processamento direto
cd /opt/privacy/app
python main.py --diretorio /caminho/documentos

# Com IA avançada
python ai_super_processor.py --input /documentos --output /resultados
```

## Formatos Suportados

| Formato | Extensão | Descrição |
|---------|----------|-----------|
| PDF | `.pdf` | Documentos PDF com OCR |
| Word | `.docx` | Documentos Microsoft Word |
| Excel | `.xlsx` | Planilhas Microsoft Excel |
| CSV | `.csv` | Dados tabulares |
| Email | `.msg` | Emails do Outlook |
| Texto | `.txt` | Arquivos de texto puro |
| PowerPoint | `.pptx` | Apresentações (beta) |
| Imagens | `.jpg, .png` | OCR de imagens |

## Dados Detectados

### Informações Pessoais
- **CPF** - Cadastro de Pessoa Física
- **RG** - Registro Geral
- **CNH** - Carteira Nacional de Habilitação
- **Passaporte** - Números de passaporte
- **Email** - Endereços eletrônicos
- **Telefone** - Números de telefone
- **Endereço** - Endereços completos

### Dados Sensíveis
- **Dados bancários** - Contas e agências
- **Cartão de crédito** - Números de cartão
- **Dados médicos** - Informações de saúde
- **Dados biométricos** - Identificadores únicos

## Classificação de Criticidade

### Alta Criticidade
- CPF, RG, CNH, Passaporte
- Dados bancários e cartões
- Informações médicas

### Média Criticidade
- Email pessoal
- Telefone pessoal
- Endereço residencial

### Baixa Criticidade
- Email corporativo
- Telefone comercial
- Nomes completos

## Monitoramento

### Logs do Sistema
```bash
# Logs do serviço
sudo journalctl -u privacy -f

# Logs do Gunicorn
sudo tail -f /opt/privacy/logs/gunicorn_error.log

# Status do serviço
sudo systemctl status privacy
```

### Métricas de Performance
- Documentos processados por minuto
- Taxa de detecção de dados pessoais
- Precisão da classificação por IA
- Tempo de resposta da interface

## Troubleshooting

### Problemas Comuns

**Erro 502 Bad Gateway**
```bash
sudo /opt/privacy/scripts/fix_502.sh
```

**Banco de dados não conecta**
```bash
sudo /opt/privacy/scripts/test_postgresql.sh
```

**Diagnóstico completo**
```bash
sudo /opt/privacy/scripts/debug_service.sh
```

### Logs de Debug

```bash
# Ativar debug detalhado
sudo systemctl edit privacy
```

Adicionar:
```ini
[Service]
Environment=FLASK_DEBUG=True
Environment=LOG_LEVEL=DEBUG
```

## Segurança

### Recomendações

1. **Firewall**: Bloqueie portas desnecessárias
2. **SSL**: Configure certificados TLS/SSL
3. **Backup**: Automatize backups do banco de dados
4. **Logs**: Monitore logs de acesso e erro
5. **Atualizações**: Mantenha dependências atualizadas

### Configuração SSL

```bash
# Instalar Certbot
sudo apt install certbot python3-certbot-nginx

# Obter certificado
sudo certbot --nginx -d seu-dominio.com
```

## Contribuição

### Desenvolvimento Local

```bash
# Clonar repositório
git clone https://github.com/seu-usuario/n.crisisops.git
cd n.crisisops

# Instalar dependências
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Configurar banco local
createdb privacy_dev
export DATABASE_URL=postgresql://user:pass@localhost/privacy_dev

# Executar aplicação
python web_interface.py
```

### Testes

```bash
# Executar testes
python -m pytest tests/

# Cobertura de código
coverage run -m pytest
coverage report
```

## Licença

Este projeto está licenciado sob a MIT License - veja o arquivo [LICENSE](LICENSE) para detalhes.

## Suporte

### Documentação
- [Guia de Deploy](docs/README_DEPLOY.md)
- [Troubleshooting](docs/DIAGNOSTICO_502.md)
- [Arquitetura](docs/replit.md)

### Contato
- **Email**: suporte@n.crisisops.com
- **Issues**: [GitHub Issues](https://github.com/seu-usuario/n.crisisops/issues)
- **Documentação**: [Wiki do Projeto](https://github.com/seu-usuario/n.crisisops/wiki)

---

**n.crisisops** - Powered by ness. | Sistema de Compliance LGPD Inteligente