# n.crisisops - Guia de Deploy VPS

## Configuração Específica

- **Diretório VPS**: `/opt/privacy`
- **Domínio**: `monster.e-ness.com.br`
- **Porta da Aplicação**: `5000`
- **Usuário do Sistema**: `privacy`
- **Serviço**: `privacy`

## Pré-requisitos

1. **VPS Ubuntu/CentOS** com acesso root
2. **Domínio configurado** apontando para o IP do servidor
3. **Chave OpenAI** para funcionalidades de IA

## Instalação Rápida

### 1. Copiar arquivos para o servidor

```bash
# No seu computador local
scp -r *.py install.sh deploy.sh templates/ root@your-server-ip:/tmp/

# Conectar no servidor
ssh root@your-server-ip
```

### 2. Executar deploy automatizado

```bash
cd /tmp
chmod +x deploy.sh
./deploy.sh
```

### 3. Configurar chave OpenAI

```bash
nano /opt/privacy/app/.env
# Editar linha: OPENAI_API_KEY=sk-your-actual-key-here
```

### 4. Configurar SSL (HTTPS)

```bash
# Instalar certificado SSL
certbot --nginx -d monster.e-ness.com.br

# Renovação automática
echo "0 12 * * * /usr/bin/certbot renew --quiet" | crontab -
```

### 5. Verificar instalação

```bash
systemctl status privacy
curl -f http://monster.e-ness.com.br/health
```

## Estrutura de Arquivos VPS

```
/opt/privacy/
├── app/                    # Aplicação Python
│   ├── web_interface.py    # Servidor principal
│   ├── *.py               # Módulos do sistema
│   ├── templates/         # Templates HTML
│   └── .env              # Configurações
├── venv/                  # Ambiente virtual Python
├── data/                  # Documentos para análise
├── logs/                  # Logs do sistema
├── backups/               # Backups automáticos
├── uploads/               # Arquivos enviados
└── exports/               # Relatórios gerados
```

## Comandos de Manutenção

### Status do Sistema
```bash
systemctl status privacy nginx postgresql
```

### Logs em Tempo Real
```bash
journalctl -u privacy -f
tail -f /opt/privacy/logs/privacy.log
```

### Reiniciar Serviços
```bash
systemctl restart privacy
systemctl restart nginx
```

### Backup Manual
```bash
/usr/local/bin/privacy-backup
```

### Atualizações do Sistema
```bash
cd /opt/privacy/app
sudo -u privacy git pull  # Se usando Git
systemctl restart privacy
```

## Monitoramento

### Verificar Saúde da Aplicação
```bash
curl -f http://monster.e-ness.com.br/health
```

### Logs de Erro
```bash
tail -f /opt/privacy/logs/nginx_error.log
grep ERROR /opt/privacy/logs/privacy.log
```

### Uso de Recursos
```bash
htop
df -h
du -sh /opt/privacy/*
```

## Backup e Restauração

### Backup Automático
- Executado diariamente às 2h da manhã
- Mantém últimos 30 days
- Localização: `/opt/privacy/backups/`

### Restaurar Backup
```bash
cd /opt/privacy/backups
gunzip privacy_backup_YYYYMMDD_HHMMSS.sql.gz
sudo -u privacy psql privacy < privacy_backup_YYYYMMDD_HHMMSS.sql
```

## Firewall e Segurança

### Portas Abertas
- **80**: HTTP (redireciona para HTTPS)
- **443**: HTTPS
- **22**: SSH
- **5432**: PostgreSQL (apenas local)

### Comandos de Firewall
```bash
# Ubuntu/Debian
ufw status
ufw allow 80
ufw allow 443

# CentOS/RHEL
firewall-cmd --list-all
firewall-cmd --permanent --add-service=http
firewall-cmd --permanent --add-service=https
firewall-cmd --reload
```

## Resolução de Problemas

### Aplicação não inicia
```bash
# Verificar logs
journalctl -u privacy -n 50

# Verificar configuração
sudo -u privacy /opt/privacy/venv/bin/python /opt/privacy/app/web_interface.py

# Verificar permissões
chown -R privacy:privacy /opt/privacy
```

### Nginx não funciona
```bash
# Testar configuração
nginx -t

# Verificar logs
tail -f /var/log/nginx/error.log
```

### PostgreSQL problemas
```bash
# Verificar status
systemctl status postgresql

# Conectar manualmente
sudo -u postgres psql privacy

# Verificar conexões
ss -tuln | grep 5432
```

### Performance Issues
```bash
# Verificar uso de CPU/RAM
htop

# Verificar espaço em disco
df -h

# Limpar logs antigos
journalctl --vacuum-time=7d
```

## URLs Importantes

- **Aplicação**: https://monster.e-ness.com.br
- **Health Check**: https://monster.e-ness.com.br/health
- **Logs**: `/opt/privacy/logs/`
- **Backups**: `/opt/privacy/backups/`

## Contatos de Suporte

Para problemas técnicos:
1. Verificar logs do sistema
2. Consultar este guia
3. Executar comandos de diagnóstico
4. Contatar equipe técnica com logs relevantes