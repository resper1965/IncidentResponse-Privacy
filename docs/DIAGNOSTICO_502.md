# Diagnóstico e Solução - Erro 502 VPS

## Comandos para Executar na VPS

### 1. Verificar Status dos Serviços
```bash
# Status do serviço da aplicação
systemctl status privacy

# Status do Nginx
systemctl status nginx

# Status do PostgreSQL
systemctl status postgresql
```

### 2. Verificar Logs de Erro
```bash
# Logs da aplicação
journalctl -u privacy -f --lines=50

# Logs do Nginx
tail -f /var/log/nginx/error.log

# Logs específicos da aplicação
tail -f /opt/privacy/logs/privacy.log

# Logs do Gunicorn
tail -f /opt/privacy/logs/gunicorn.log
```

### 3. Testar Aplicação Diretamente
```bash
# Verificar se a aplicação responde na porta 5000
curl -I http://localhost:5000/

# Testar health check
curl http://localhost:5000/health

# Verificar processos rodando
ps aux | grep gunicorn
ps aux | grep python
```

### 4. Verificar Configuração do Nginx
```bash
# Testar configuração
nginx -t

# Ver configuração atual
cat /etc/nginx/sites-available/privacy

# Verificar se está linkado
ls -la /etc/nginx/sites-enabled/
```

### 5. Verificar Permissões e Arquivos
```bash
# Verificar estrutura de arquivos
ls -la /opt/privacy/

# Verificar permissões
ls -la /opt/privacy/app/

# Verificar usuário privacy
id privacy

# Verificar ambiente virtual
ls -la /opt/privacy/venv/bin/
```

## Soluções Comuns

### Se a aplicação não está rodando:
```bash
# Reiniciar serviço
systemctl restart privacy

# Se falhar, executar manualmente para ver erros
cd /opt/privacy/app
sudo -u privacy /opt/privacy/venv/bin/python web_interface.py
```

### Se problema de permissões:
```bash
# Corrigir permissões
chown -R privacy:privacy /opt/privacy
chmod +x /opt/privacy/venv/bin/python
```

### Se problema no PostgreSQL:
```bash
# Verificar conexão ao banco
sudo -u privacy psql privacy -c "SELECT version();"

# Reiniciar PostgreSQL
systemctl restart postgresql
```

### Se problema no ambiente Python:
```bash
# Reinstalar dependências
cd /opt/privacy/app
sudo -u privacy /opt/privacy/venv/bin/pip install -r requirements_deploy.txt

# Verificar módulos instalados
sudo -u privacy /opt/privacy/venv/bin/pip list
```

### Se problema no Nginx:
```bash
# Recarregar configuração
nginx -s reload

# Reiniciar Nginx
systemctl restart nginx

# Verificar conectividade
netstat -tlnp | grep :80
netstat -tlnp | grep :5000
```

## Comandos de Emergência

### Parar todos os serviços:
```bash
systemctl stop privacy nginx
```

### Reinstalar aplicação:
```bash
# Parar serviços
systemctl stop privacy

# Reinstalar código
cd /tmp
# (copiar arquivos atualizados)
cp -r *.py /opt/privacy/app/
chown -R privacy:privacy /opt/privacy

# Reiniciar
systemctl start privacy
```

### Verificar logs em tempo real:
```bash
# Terminal 1: Logs da aplicação
journalctl -u privacy -f

# Terminal 2: Logs do Nginx
tail -f /var/log/nginx/error.log

# Terminal 3: Testar requisições
watch -n 2 "curl -I http://localhost:5000/health"
```

## Configuração de Debug

### Ativar modo debug temporário:
```bash
# Editar .env
nano /opt/privacy/app/.env

# Adicionar/modificar:
FLASK_DEBUG=True
LOG_LEVEL=DEBUG

# Reiniciar
systemctl restart privacy
```

### Verificar variáveis de ambiente:
```bash
# Ver variáveis carregadas
sudo -u privacy cat /opt/privacy/app/.env

# Testar conexão PostgreSQL
sudo -u privacy PGPASSWORD="ncrisisops_secure_2025" psql -h localhost -U privacy privacy -c "SELECT 1;"
```

## Status Esperado

### Aplicação funcionando:
- `systemctl status privacy` → Active (running)
- `curl http://localhost:5000/health` → "healthy"
- `ps aux | grep gunicorn` → 4 processos worker

### Nginx funcionando:
- `systemctl status nginx` → Active (running)
- `nginx -t` → syntax is ok
- `curl -I http://monster.e-ness.com.br` → 200 OK

### PostgreSQL funcionando:
- `systemctl status postgresql` → Active (running)
- Conexão ao banco funcionando

## Contato para Suporte

Envie os seguintes logs se o problema persistir:
```bash
# Coletar informações completas
journalctl -u privacy --no-pager > privacy-logs.txt
tail -100 /var/log/nginx/error.log > nginx-logs.txt
systemctl status privacy nginx postgresql > services-status.txt
```