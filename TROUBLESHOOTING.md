# Guia de Resolução de Problemas - n.crisisops Privacy

## Problemas Comuns e Soluções

### 1. Erro: "externally-managed-environment"

**Sintoma:**
```
error: externally-managed-environment
× This environment is externally managed
```

**Causa:** Python 3.12+ bloqueia instalação global de pacotes

**Solução:**
```bash
# Sempre usar ambiente virtual
cd /opt/privacy
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Erro: "venv/bin/activate: No such file or directory"

**Sintoma:**
```
-bash: venv/bin/activate: No such file or directory
```

**Causa:** Ambiente virtual não existe ou está corrompido

**Solução:**
```bash
cd /opt/privacy
rm -rf venv
python3 -m venv venv
chown -R privacy:privacy venv
source venv/bin/activate
pip install --upgrade pip
pip install gunicorn flask
```

### 3. Erro: "status=203/EXEC" no systemd

**Sintoma:**
```
Process: 1027500 ExecStart=/opt/privacy/venv/bin/gunicorn (code=exited, status=203/EXEC)
```

**Causa:** Executável não encontrado ou sem permissão

**Solução:**
```bash
# Verificar se o arquivo existe
ls -la /opt/privacy/venv/bin/gunicorn

# Verificar permissões
chmod +x /opt/privacy/venv/bin/gunicorn

# Verificar se o arquivo web_interface.py existe
ls -la /opt/privacy/web_interface.py

# Recarregar systemd
systemctl daemon-reload
systemctl restart privacy
```

### 4. Serviço não inicia

**Diagnóstico:**
```bash
# Verificar logs detalhados
journalctl -u privacy -f

# Verificar status
systemctl status privacy

# Testar manualmente
cd /opt/privacy
source venv/bin/activate
python web_interface.py
```

**Soluções comuns:**

#### A. Problema de permissões
```bash
chown -R privacy:privacy /opt/privacy
chmod -R 755 /opt/privacy
```

#### B. Problema de dependências
```bash
cd /opt/privacy
source venv/bin/activate
pip install --upgrade pip
pip install flask gunicorn
```

#### C. Problema de arquivo não encontrado
```bash
# Verificar se todos os arquivos estão presentes
ls -la /opt/privacy/*.py
ls -la /opt/privacy/templates/
```

### 5. Erro de Importação

**Sintoma:**
```
ImportError: cannot import name 'encontrar_arquivos'
```

**Causa:** Função não existe ou módulo não encontrado

**Solução:**
```bash
# Verificar se o arquivo existe
grep -r "encontrar_arquivos" /opt/privacy/

# Corrigir importação no web_interface.py
# Substituir:
# from file_scanner import encontrar_arquivos
# Por:
# from file_scanner import listar_arquivos_recursivos
```

### 6. Problema de Banco de Dados

**Sintoma:**
```
sqlite3.OperationalError: no such table
```

**Solução:**
```bash
cd /opt/privacy
source venv/bin/activate
python3 -c "
from database import inicializar_banco
inicializar_banco()
print('Banco inicializado com sucesso')
"
```

### 7. Problema de Porta em Uso

**Sintoma:**
```
Address already in use
```

**Solução:**
```bash
# Verificar o que está usando a porta 5000
netstat -tulpn | grep :5000
lsof -i :5000

# Parar processo conflitante
kill -9 <PID>

# Ou mudar porta no gunicorn.conf.py
# bind = "0.0.0.0:5001"
```

### 8. Problema de Memória

**Sintoma:**
```
MemoryError ou processo sendo morto pelo OOM killer
```

**Solução:**
```bash
# Reduzir workers no gunicorn.conf.py
# workers = 1

# Aumentar swap
sudo fallocate -l 2G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
```

### 9. Problema de SSL/HTTPS

**Sintoma:**
```
SSL certificate error
```

**Solução:**
```bash
# Instalar certificado SSL
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d seu-dominio.com

# Configurar renovação automática
echo "0 12 * * * /usr/bin/certbot renew --quiet" | sudo crontab -
```

### 10. Problema de Performance

**Sintoma:** Sistema lento ou travando

**Soluções:**
```bash
# Verificar uso de recursos
htop
df -h
free -h

# Otimizar configuração do gunicorn
# workers = 1  # Reduzir workers
# timeout = 300  # Aumentar timeout

# Limpar logs antigos
journalctl --vacuum-time=7d
```

## Scripts de Correção Automática

### Script Rápido de Correção
```bash
#!/bin/bash
# Salvar como fix-privacy.sh e executar como root

echo "🔧 Correção automática do sistema privacy..."

# Parar serviço
systemctl stop privacy

# Corrigir ambiente virtual
cd /opt/privacy
rm -rf venv
python3 -m venv venv
chown -R privacy:privacy venv

# Instalar dependências básicas
source venv/bin/activate
pip install --upgrade pip
pip install flask gunicorn

# Corrigir permissões
chown -R privacy:privacy /opt/privacy
chmod -R 755 /opt/privacy

# Recarregar e iniciar
systemctl daemon-reload
systemctl start privacy

echo "✅ Correção concluída!"
```

### Verificação de Saúde
```bash
#!/bin/bash
# Salvar como health-check.sh

echo "🏥 Verificação de saúde do sistema..."

# Verificar serviços
echo "=== Status dos Serviços ==="
systemctl status privacy --no-pager
systemctl status nginx --no-pager

# Verificar arquivos
echo "=== Verificação de Arquivos ==="
ls -la /opt/privacy/
ls -la /opt/privacy/venv/bin/gunicorn

# Verificar conectividade
echo "=== Teste de Conectividade ==="
curl -f http://localhost:5000/health || echo "❌ Aplicação não responde"

# Verificar logs
echo "=== Últimos Logs ==="
journalctl -u privacy -n 10 --no-pager
```

## Comandos Úteis

### Logs em Tempo Real
```bash
# Logs do serviço
journalctl -u privacy -f

# Logs do nginx
tail -f /var/log/nginx/error.log

# Logs da aplicação
tail -f /opt/privacy/logs/privacy.log
```

### Reiniciar Serviços
```bash
# Reiniciar privacy
systemctl restart privacy

# Reiniciar nginx
systemctl restart nginx

# Reiniciar tudo
systemctl restart privacy nginx
```

### Backup e Restauração
```bash
# Backup do banco
sqlite3 /opt/privacy/lgpd_data.db ".backup /opt/privacy/backup_$(date +%Y%m%d_%H%M%S).db"

# Backup dos arquivos
tar -czf /opt/privacy/backup_$(date +%Y%m%d_%H%M%S).tar.gz /opt/privacy/
```

## Contato e Suporte

Se os problemas persistirem:

1. **Coletar informações:**
   ```bash
   systemctl status privacy
   journalctl -u privacy -n 50
   ls -la /opt/privacy/
   ```

2. **Verificar versões:**
   ```bash
   python3 --version
   pip --version
   gunicorn --version
   ```

3. **Documentar erro específico** com contexto completo

4. **Verificar se é problema conhecido** na documentação 