# 🚀 Guia de Deploy - n.crisisops Privacy Module

## 📋 Visão Geral

Este guia explica como fazer deploy do sistema n.crisisops Privacy Module em uma VPS Ubuntu/Debian.

## 🎯 Opções de Deploy

### 1. Deploy Completo (Primeira Instalação)
Para instalar o sistema pela primeira vez na VPS:

```bash
# Baixar o script de deploy
wget https://raw.githubusercontent.com/seu-usuario/IncidentResponse-Privacy/main/scripts/deploy-vps-atual.sh

# Dar permissão de execução
chmod +x deploy-vps-atual.sh

# Executar como root
sudo ./deploy-vps-atual.sh
```

### 2. Deploy Rápido (Atualizações)
Para atualizar o sistema existente:

```bash
# Baixar o script de deploy rápido
wget https://raw.githubusercontent.com/seu-usuario/IncidentResponse-Privacy/main/scripts/deploy-rapido.sh

# Dar permissão de execução
chmod +x deploy-rapido.sh

# Executar como root
sudo ./deploy-rapido.sh
```

## 🔧 Pré-requisitos

### Requisitos do Sistema
- Ubuntu 20.04+ ou Debian 11+
- Mínimo 2GB RAM
- Mínimo 20GB espaço em disco
- Acesso root/sudo
- Domínio configurado (ex: monster.e-ness.com.br)

### Portas Necessárias
- **80** (HTTP - para Let's Encrypt)
- **443** (HTTPS - aplicação principal)
- **22** (SSH - acesso remoto)

## 📦 Estrutura de Instalação

```
/opt/privacy/
├── venv/                    # Ambiente virtual Python
├── uploads/                 # Arquivos enviados
├── backups/                 # Backups automáticos
├── logs/                    # Logs da aplicação
├── data/                    # Dados processados
├── static/                  # Arquivos estáticos
├── templates/               # Templates HTML
├── .env                     # Variáveis de ambiente
├── gunicorn.conf.py         # Configuração Gunicorn
├── requirements.txt         # Dependências Python
└── *.py                     # Código da aplicação
```

## 🔐 Configuração de Segurança

### Usuário do Sistema
- **Usuário**: `privacy`
- **Diretório**: `/opt/privacy`
- **Permissões**: Apenas para o serviço

### Banco de Dados
- **Sistema**: PostgreSQL
- **Banco**: `privacy_db`
- **Usuário**: `privacy_user`
- **Senha**: `Lgpd2025#Privacy`

### SSL/TLS
- **Provedor**: Let's Encrypt
- **Renovação**: Automática (cron)
- **Protocolos**: TLS 1.2 e 1.3

## 🌐 Configuração de Rede

### Nginx
- **Proxy reverso**: Porta 5000 → 80/443
- **Upload máximo**: 100MB
- **Headers de segurança**: HSTS, CSP, etc.

### Firewall (UFW)
```bash
# Configurar firewall
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable
```

## 📊 Monitoramento

### Logs do Sistema
```bash
# Logs da aplicação
sudo journalctl -u privacy -f

# Logs do Nginx
sudo tail -f /var/log/nginx/privacy_access.log
sudo tail -f /var/log/nginx/privacy_error.log

# Logs da aplicação
sudo tail -f /var/log/privacy/error.log
```

### Status dos Serviços
```bash
# Verificar status
sudo systemctl status privacy
sudo systemctl status nginx
sudo systemctl status postgresql

# Reiniciar serviços
sudo systemctl restart privacy
sudo systemctl restart nginx
```

## 🔑 Configuração de Chaves API

### OpenAI
```bash
# Editar arquivo .env
sudo nano /opt/privacy/.env

# Adicionar sua chave
OPENAI_API_KEY=sua_chave_aqui
```

### Outras APIs
```bash
# Anthropic (opcional)
ANTHROPIC_API_KEY=sua_chave_aqui

# Outras APIs conforme necessário
```

## 🚀 Comandos Úteis

### Gerenciamento de Serviços
```bash
# Iniciar serviço
sudo systemctl start privacy

# Parar serviço
sudo systemctl stop privacy

# Reiniciar serviço
sudo systemctl restart privacy

# Verificar status
sudo systemctl status privacy

# Habilitar auto-inicialização
sudo systemctl enable privacy
```

### Backup e Restore
```bash
# Backup manual
sudo cp -r /opt/privacy /opt/privacy_backup_$(date +%Y%m%d_%H%M%S)

# Restore manual
sudo systemctl stop privacy
sudo rm -rf /opt/privacy
sudo mv /opt/privacy_backup_YYYYMMDD_HHMMSS /opt/privacy
sudo systemctl start privacy
```

### Atualização de Dependências
```bash
# Ativar ambiente virtual
sudo -u privacy /opt/privacy/venv/bin/activate

# Atualizar pip
sudo -u privacy /opt/privacy/venv/bin/pip install --upgrade pip

# Instalar novas dependências
sudo -u privacy /opt/privacy/venv/bin/pip install -r /opt/privacy/requirements.txt
```

## 🔍 Troubleshooting

### Problemas Comuns

#### 1. Serviço não inicia
```bash
# Verificar logs
sudo journalctl -u privacy --no-pager -l -n 50

# Verificar permissões
sudo chown -R privacy:privacy /opt/privacy
sudo chmod +x /opt/privacy/venv/bin/*
```

#### 2. Erro de dependência Python
```bash
# Reinstalar ambiente virtual
sudo -u privacy python3 -m venv /opt/privacy/venv_new
sudo -u privacy /opt/privacy/venv_new/bin/pip install -r /opt/privacy/requirements.txt
sudo mv /opt/privacy/venv /opt/privacy/venv_old
sudo mv /opt/privacy/venv_new /opt/privacy/venv
```

#### 3. Problemas de SSL
```bash
# Renovar certificado manualmente
sudo certbot renew --force-renewal

# Verificar configuração Nginx
sudo nginx -t
sudo systemctl reload nginx
```

#### 4. Problemas de Banco de Dados
```bash
# Verificar conexão PostgreSQL
sudo -u postgres psql -d privacy_db -c "SELECT version();"

# Recriar banco se necessário
sudo -u postgres dropdb privacy_db
sudo -u postgres createdb privacy_db -O privacy_user
```

### Logs de Debug
```bash
# Logs detalhados da aplicação
sudo tail -f /var/log/privacy/error.log

# Logs do Gunicorn
sudo tail -f /var/log/privacy/access.log

# Logs do sistema
sudo journalctl -u privacy -f --no-pager
```

## 📈 Monitoramento de Performance

### Métricas Importantes
- **CPU**: Uso por worker
- **RAM**: Uso da aplicação
- **Disco**: Espaço em uploads/
- **Rede**: Requisições por minuto

### Comandos de Monitoramento
```bash
# Uso de recursos
htop
df -h
free -h

# Processos Python
ps aux | grep python

# Conexões de rede
netstat -tlnp | grep :5000
```

## 🔄 Atualizações Automáticas

### Script de Atualização Automática
```bash
#!/bin/bash
# /opt/privacy/scripts/auto-update.sh

cd /opt/privacy
git pull origin main
source venv/bin/activate
pip install -r requirements.txt
sudo systemctl restart privacy
```

### Cron Job (Opcional)
```bash
# Adicionar ao crontab
0 2 * * 0 /opt/privacy/scripts/auto-update.sh >> /var/log/privacy/update.log 2>&1
```

## 📞 Suporte

### Informações de Contato
- **Email**: suporte@n.crisisops.com
- **Documentação**: https://docs.n.crisisops.com
- **Issues**: https://github.com/seu-usuario/IncidentResponse-Privacy/issues

### Informações do Sistema
```bash
# Versão do sistema
cat /opt/privacy/VERSION

# Configuração atual
sudo cat /opt/privacy/.env

# Status completo
sudo systemctl status privacy nginx postgresql
```

---

## ✅ Checklist de Deploy

- [ ] Sistema operacional atualizado
- [ ] Dependências do sistema instaladas
- [ ] Usuário `privacy` criado
- [ ] PostgreSQL configurado
- [ ] Ambiente Python configurado
- [ ] Código da aplicação copiado
- [ ] Dependências Python instaladas
- [ ] Arquivo `.env` configurado
- [ ] Banco de dados inicializado
- [ ] Serviço systemd configurado
- [ ] Gunicorn configurado
- [ ] Nginx configurado
- [ ] SSL configurado
- [ ] Permissões ajustadas
- [ ] Serviços iniciados
- [ ] Aplicação respondendo
- [ ] Firewall configurado
- [ ] Backup inicial criado

---

**🎉 Deploy concluído com sucesso!**

O sistema estará disponível em: `https://monster.e-ness.com.br` 