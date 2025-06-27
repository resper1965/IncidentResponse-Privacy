# Deploy para VPS - monster.e-ness.com.br

## Scripts Disponíveis

### 1. Setup Inicial da VPS
```bash
# Na VPS, execute como root:
./scripts/deploy-vps-real.sh
```
Este script:
- Cria usuário `privacy`
- Instala Python, PostgreSQL, Nginx
- Configura serviço systemd
- Instala dependências Python
- Configura banco PostgreSQL

### 2. Sincronização de Arquivos
```bash
# No Replit, execute:
chmod +x scripts/sync-to-vps.sh
./scripts/sync-to-vps.sh
```
Este script:
- Copia todos os arquivos Python para VPS
- Sincroniza templates e scripts
- Atualiza dependências
- Reinicia serviço

### 3. Verificação e Debug
```bash
# Na VPS:
systemctl status privacy
journalctl -f -u privacy
```

## Processo Completo de Deploy

### Passo 1: Preparar VPS
Execute na VPS como root:
```bash
# Fazer download do script
wget https://raw.githubusercontent.com/seu-repo/scripts/deploy-vps-real.sh
chmod +x deploy-vps-real.sh
sudo ./deploy-vps-real.sh
```

### Passo 2: Configurar Variáveis
Edite o arquivo `.env` na VPS:
```bash
nano /opt/privacy/.env
```
Configure:
```
DATABASE_URL=postgresql://privacy:privacy123@localhost/privacy
OPENAI_API_KEY=sk-sua-chave-aqui
FLASK_ENV=production
FLASK_DEBUG=False
```

### Passo 3: Sincronizar Código
No Replit:
```bash
./scripts/sync-to-vps.sh
```

### Passo 4: Iniciar Sistema
Na VPS:
```bash
systemctl daemon-reload
systemctl enable privacy
systemctl start privacy
systemctl reload nginx
```

### Passo 5: Verificar
```bash
systemctl status privacy
curl http://localhost:5000
```

## Acesso Final
- URL: https://monster.e-ness.com.br
- Logs: `journalctl -f -u privacy`
- Config: `/opt/privacy/.env`
- Reiniciar: `systemctl restart privacy`

## Arquivos Principais na VPS
```
/opt/privacy/
├── web_interface.py       # Aplicação Flask principal
├── database_postgresql.py # Banco PostgreSQL  
├── ai_super_processor.py  # IA avançada
├── file_reader.py         # Leitor de arquivos
├── templates/             # Templates HTML
├── scripts/               # Scripts auxiliares
└── .env                   # Configurações
```

## Troubleshooting

### Problema: Serviço não inicia
```bash
journalctl -u privacy --no-pager -l
```

### Problema: Dependências
```bash
cd /opt/privacy
source venv/bin/activate
pip install --force-reinstall -r requirements.txt
```

### Problema: PostgreSQL
```bash
sudo -u postgres psql
\l  # listar databases
\q  # sair
```

### Problema: Nginx
```bash
nginx -t  # testar configuração
systemctl reload nginx
```