# n.crisisops Privacy LGPD - Sistema Funcional para VPS

> **Repositório oficial:** [https://github.com/resper1965/IncidentResponse-Privacy](https://github.com/resper1965/IncidentResponse-Privacy)

## 🚀 Visão Geral

Sistema completo de extração e análise de dados para conformidade com a LGPD, otimizado para execução em VPS Linux.

## 📋 Características Principais

- ✅ **Extração Robusta com Regex**: Garantia de extração de dados
- ✅ **IA Semântica**: Refinamento para clientes prioritários
- ✅ **Interface Web Moderna**: Dashboard responsivo e intuitivo
- ✅ **Processamento Recursivo**: Navegação completa por diretórios
- ✅ **Validação de Dados**: CPF, email, telefone, etc.
- ✅ **Relatórios Detalhados**: Estatísticas e análises
- ✅ **Configuração via JSON**: Fácil personalização
- ✅ **Logs Completos**: Monitoramento e auditoria

## 🛠️ Instalação na VPS

### Pré-requisitos

- VPS Linux (Ubuntu 20.04+ / CentOS 8+ / Debian 11+)
- Python 3.8+
- Acesso SSH com privilégios sudo
- 2GB RAM mínimo (4GB recomendado)
- 10GB espaço em disco

### Passo a Passo

#### 1. Conectar na VPS
```bash
ssh usuario@seu-vps-ip
```

#### 2. Baixar o projeto do repositório oficial
```bash
# Criar diretório de trabalho
mkdir -p ~/privacy-lgpd
cd ~/privacy-lgpd

# Clonar o repositório oficial
git clone https://github.com/resper1965/IncidentResponse-Privacy.git
cd IncidentResponse-Privacy
```

#### 3. Executar instalação
```bash
# Dar permissão de execução
chmod +x install-vps-final.sh

# Executar instalação
./install-vps-final.sh
```

#### 4. Verificar instalação
```bash
# Verificar se o sistema foi instalado
ls -la /opt/privacy-lgpd/

# Verificar status
cd /opt/privacy-lgpd
./status.sh
```

## 🚀 Como Usar

### Iniciar o Sistema
```bash
cd /opt/privacy-lgpd
./start.sh
```

### Parar o Sistema
```bash
cd /opt/privacy-lgpd
./stop.sh
```

### Verificar Status
```bash
cd /opt/privacy-lgpd
./status.sh
```

### Acessar Interface Web
```
http://seu-vps-ip:5000
```

## 📁 Estrutura do Sistema

```
/opt/privacy-lgpd/
├── main_enhanced.py          # Sistema principal
├── requirements.txt          # Dependências Python
├── gunicorn.conf.py         # Configuração Gunicorn
├── config.json              # Configuração do sistema
├── start.sh                 # Script de inicialização
├── stop.sh                  # Script de parada
├── status.sh                # Script de status
├── venv/                    # Ambiente virtual Python
├── uploads/                 # Arquivos enviados
├── output/                  # Resultados processados
├── reports/                 # Relatórios gerados
├── logs/                    # Logs do sistema
├── templates/               # Templates HTML
└── test.txt                 # Arquivo de teste
```

## 🔧 Configuração

### Arquivo config.json
```json
{
    "system": {
        "name": "n.crisisops Privacy LGPD",
        "version": "2.0.0",
        "port": 5000,
        "host": "0.0.0.0"
    },
    "processing": {
        "max_file_size_mb": 100,
        "supported_formats": ["txt", "doc", "docx", "pdf", "eml", "msg", "rtf"],
        "workers": 2,
        "timeout": 300
    },
    "priority_clients": {
        "bradesco": ["bradesco", "banco bradesco", "bradesco s.a."],
        "petrobras": ["petrobras", "petrobras s.a.", "petrobras brasil"],
        "ons": ["ons", "operador nacional do sistema elétrico"],
        "embraer": ["embraer", "embraer s.a."],
        "rede_dor": ["rede dor", "rede d'or", "rededor"],
        "globo": ["globo", "organizações globo", "rede globo"],
        "eletrobras": ["eletrobras", "eletrobras s.a."],
        "crefisa": ["crefisa", "banco crefisa"],
        "equinix": ["equinix", "equinix brasil"],
        "cohesity": ["cohesity", "cohesity brasil"]
    }
}
```

## 🌐 Interface Web

### Funcionalidades
- **Upload de Arquivos**: Drag & drop ou seleção manual
- **Processamento de Diretórios**: Escaneamento recursivo
- **Monitoramento em Tempo Real**: Progresso e status
- **Resultados Interativos**: Tabelas e estatísticas
- **Design Responsivo**: Funciona em desktop e mobile

### Endpoints da API
- `GET /` - Interface principal
- `POST /api/process-file` - Processar arquivo único
- `POST /api/process-directory` - Processar diretório
- `GET /api/status` - Status do processamento
- `GET /api/results` - Resultados disponíveis
- `POST /api/scan-directory` - Escanear diretório
- `GET /health` - Verificação de saúde

## 🔍 Tipos de Dados Extraídos

### Regex Garantido
- **CPF**: Padrão brasileiro com validação
- **Email**: Endereços de email válidos
- **Telefone**: Números brasileiros (fixo e celular)
- **Data de Nascimento**: Formatos DD/MM/YYYY
- **CEP**: Códigos postais brasileiros
- **RG**: Documentos de identidade
- **Placa de Veículo**: Padrão Mercosul
- **IP**: Endereços IPv4

### Validação
- Verificação de dígitos verificadores (CPF)
- Validação de formato (email, telefone)
- Verificação de datas válidas
- Contexto semântico

## 🎯 Clientes Prioritários

O sistema identifica automaticamente clientes prioritários:
- Bradesco
- Petrobras
- ONS (Operador Nacional do Sistema Elétrico)
- Embraer
- Rede D'Or
- Globo
- Eletrobras
- Crefisa
- Equinix
- Cohesity

## 📊 Relatórios e Estatísticas

### Métricas Geradas
- Total de arquivos processados
- Quantidade de dados extraídos por tipo
- Clientes prioritários identificados
- Taxa de confiança da extração
- Tempo de processamento
- Estatísticas por diretório

### Formato dos Relatórios
```json
{
    "diretorio": "/caminho/processado",
    "timestamp": "2024-01-01T12:00:00",
    "arquivos_processados": 150,
    "total_dados": 1250,
    "clientes_prioritarios": 45,
    "resultados_por_arquivo": [...],
    "estatisticas_gerais": {
        "por_tipo": {
            "cpf": 300,
            "email": 250,
            "telefone": 200
        },
        "por_cliente": {
            "bradesco": 15,
            "petrobras": 8
        }
    }
}
```

## 🔒 Segurança

### Medidas Implementadas
- Validação de entrada de arquivos
- Limitação de tamanho de upload
- Sanitização de caminhos de diretório
- Logs de auditoria
- Controle de acesso por IP (configurável)

### Recomendações
- Usar HTTPS em produção
- Configurar firewall adequadamente
- Manter sistema atualizado
- Fazer backup regular dos dados
- Monitorar logs de acesso

## 🐛 Troubleshooting

### Problemas Comuns

#### Sistema não inicia
```bash
# Verificar logs
tail -f /opt/privacy-lgpd/logs/app.log

# Verificar dependências
cd /opt/privacy-lgpd
source venv/bin/activate
pip list
```

#### Erro de permissão
```bash
# Corrigir permissões
sudo chown -R $USER:$USER /opt/privacy-lgpd
chmod +x /opt/privacy-lgpd/*.sh
```

#### Porta já em uso
```bash
# Verificar processos
ps aux | grep gunicorn

# Parar processos
pkill -f gunicorn
```

#### Erro de memória
```bash
# Reduzir workers no gunicorn.conf.py
workers = 1
```

### Logs Importantes
- `/opt/privacy-lgpd/logs/app.log` - Log principal
- `/var/log/syslog` - Logs do sistema (systemd)
- `gunicorn_access.log` - Acessos HTTP
- `gunicorn_error.log` - Erros HTTP

## 📈 Monitoramento

### Métricas a Monitorar
- Uso de CPU e memória
- Tempo de resposta da API
- Taxa de erro de processamento
- Espaço em disco
- Número de arquivos processados

### Comandos Úteis
```bash
# Monitorar recursos
htop
df -h
free -h

# Monitorar logs em tempo real
tail -f /opt/privacy-lgpd/logs/app.log

# Verificar status do serviço
systemctl status privacy-lgpd
```

## 🔄 Atualizações

### Atualizar Sistema
```bash
cd /opt/privacy-lgpd
./stop.sh

# Fazer backup
cp -r . ../privacy-lgpd-backup-$(date +%Y%m%d)

# Atualizar código
git pull origin main

# Reinstalar dependências
source venv/bin/activate
pip install -r requirements.txt

# Reiniciar
./start.sh
```

## 📞 Suporte

### Informações de Contato
- **Equipe**: n.crisisops
- **Documentação**: Este arquivo
- **Logs**: `/opt/privacy-lgpd/logs/`
- **Repositório oficial**: https://github.com/resper1965/IncidentResponse-Privacy

### Informações do Sistema
```bash
# Versão
python3 -c "import main_enhanced; print('Versão:', main_enhanced.__version__)"

# Configuração
cat /opt/privacy-lgpd/config.json

# Status
cd /opt/privacy-lgpd && ./status.sh
```

## ✅ Checklist de Instalação

- [ ] Python 3.8+ instalado
- [ ] Arquivos do projeto baixados do repositório oficial
- [ ] Script de instalação executado
- [ ] Sistema iniciado com sucesso
- [ ] Interface web acessível
- [ ] Upload de arquivo funcionando
- [ ] Processamento de diretório funcionando
- [ ] Logs sendo gerados
- [ ] Firewall configurado
- [ ] Backup inicial realizado

## 🎉 Conclusão

O sistema n.crisisops Privacy LGPD está pronto para uso em produção na VPS. Todas as funcionalidades foram testadas e validadas para garantir robustez e confiabilidade.

**Status**: ✅ **FUNCIONAL E PRONTO PARA PRODUÇÃO**

> **Repositório oficial:** [https://github.com/resper1965/IncidentResponse-Privacy](https://github.com/resper1965/IncidentResponse-Privacy) 