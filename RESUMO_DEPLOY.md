# 🚀 Resumo de Deploy - n.crisisops Privacy Module

## 📋 Scripts Criados

### 1. `scripts/deploy-vps-atual.sh` - Deploy Completo
**Para primeira instalação na VPS**

```bash
# Na VPS, execute:
wget https://raw.githubusercontent.com/seu-usuario/IncidentResponse-Privacy/main/scripts/deploy-vps-atual.sh
chmod +x deploy-vps-atual.sh
sudo ./deploy-vps-atual.sh
```

**O que faz:**
- ✅ Instala todas as dependências do sistema
- ✅ Configura PostgreSQL
- ✅ Cria usuário `privacy`
- ✅ Configura ambiente Python
- ✅ Instala dependências Python
- ✅ Configura Nginx + SSL
- ✅ Configura serviço systemd
- ✅ Inicializa banco de dados
- ✅ Configura renovação automática SSL

### 2. `scripts/deploy-rapido.sh` - Deploy Rápido
**Para atualizações do sistema**

```bash
# Na VPS, execute:
wget https://raw.githubusercontent.com/seu-usuario/IncidentResponse-Privacy/main/scripts/deploy-rapido.sh
chmod +x deploy-rapido.sh
sudo ./deploy-rapido.sh
```

**O que faz:**
- ✅ Faz backup automático
- ✅ Atualiza código
- ✅ Atualiza dependências Python
- ✅ Reinicia serviços
- ✅ Testa aplicação

## 🎯 Como Fazer Deploy

### Opção 1: Deploy Manual (Recomendado)
1. **Faça upload dos arquivos para a VPS:**
   ```bash
   # Na sua máquina local
   scp -r ./* root@monster.e-ness.com.br:/tmp/privacy-update/
   ```

2. **Na VPS, execute o deploy:**
   ```bash
   # Conectar na VPS
   ssh root@monster.e-ness.com.br
   
   # Executar deploy
   cd /tmp/privacy-update
   chmod +x scripts/deploy-vps-atual.sh
   sudo ./scripts/deploy-vps-atual.sh
   ```

### Opção 2: Deploy via Git (Se configurado)
1. **Na VPS, clone o repositório:**
   ```bash
   cd /opt
   git clone https://github.com/seu-usuario/IncidentResponse-Privacy.git privacy
   cd privacy
   ```

2. **Execute o deploy:**
   ```bash
   chmod +x scripts/deploy-vps-atual.sh
   sudo ./scripts/deploy-vps-atual.sh
   ```

## 🔧 Configurações Importantes

### Variáveis de Ambiente
O script criará automaticamente o arquivo `.env` com:

```env
# Configurações do Sistema
FLASK_ENV=production
FLASK_DEBUG=False
SECRET_KEY=chave_gerada_automaticamente

# Configurações do Banco
DATABASE_URL=postgresql://privacy_user:Lgpd2025#Privacy@localhost:5432/privacy_db

# Configurações de Upload
UPLOAD_FOLDER=/opt/privacy/uploads
MAX_CONTENT_LENGTH=104857600

# Configurações de Log
LOG_LEVEL=INFO
LOG_FILE=/var/log/privacy/app.log

# Configurações de IA (configurar manualmente)
OPENAI_API_KEY=sua_chave_aqui
ANTHROPIC_API_KEY=sua_chave_aqui

# Configurações de Domínio
DOMAIN=monster.e-ness.com.br
```

### Configuração Manual de APIs
Após o deploy, configure suas chaves API:

```bash
# Editar arquivo .env
sudo nano /opt/privacy/.env

# Adicionar suas chaves
OPENAI_API_KEY=sua_chave_real_aqui
ANTHROPIC_API_KEY=sua_chave_real_aqui

# Reiniciar serviço
sudo systemctl restart privacy
```

## 📊 Verificação do Deploy

### Comandos de Verificação
```bash
# Status dos serviços
sudo systemctl status privacy nginx postgresql

# Testar aplicação
curl -f http://localhost:5000

# Verificar logs
sudo journalctl -u privacy --no-pager -l -n 10

# Verificar SSL
sudo certbot certificates
```

### URLs de Acesso
- **Local**: http://localhost:5000
- **HTTPS**: https://monster.e-ness.com.br
- **Logs**: `/var/log/privacy/`

## 🔄 Atualizações Futuras

### Para atualizações rápidas:
```bash
# Na VPS
cd /opt/privacy
sudo ./scripts/deploy-rapido.sh
```

### Para atualizações completas:
```bash
# Na VPS
cd /opt/privacy
sudo ./scripts/deploy-vps-atual.sh
```

## 🚨 Troubleshooting Rápido

### Problema: Serviço não inicia
```bash
sudo journalctl -u privacy --no-pager -l -n 20
sudo chown -R privacy:privacy /opt/privacy
sudo systemctl restart privacy
```

### Problema: Erro de dependência
```bash
cd /opt/privacy
source venv/bin/activate
pip install -r requirements.txt
sudo systemctl restart privacy
```

### Problema: SSL não funciona
```bash
sudo certbot renew --force-renewal
sudo nginx -t
sudo systemctl reload nginx
```

## 📞 Suporte

### Informações Úteis
- **Diretório**: `/opt/privacy`
- **Usuário**: `privacy`
- **Banco**: `privacy_db`
- **Porta**: 5000 (interno), 443 (externo)

### Logs Importantes
- **Aplicação**: `/var/log/privacy/error.log`
- **Nginx**: `/var/log/nginx/privacy_error.log`
- **Sistema**: `journalctl -u privacy`

---

## ✅ Checklist Final

- [ ] Scripts criados e testados
- [ ] Documentação completa
- [ ] Configurações de segurança
- [ ] Backup automático
- [ ] SSL configurado
- [ ] Monitoramento configurado
- [ ] Troubleshooting documentado

**🎉 Sistema pronto para deploy!**

Execute o script `deploy-vps-atual.sh` na sua VPS para instalar o sistema completo. 