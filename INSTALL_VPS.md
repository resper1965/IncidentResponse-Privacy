# Instalação Definitiva VPS - n.crisisops LGPD

## Resolução Final de Dependências LangChain

O problema de dependências foi resolvido definitivamente. Use o script de instalação que instala pacotes em ordem específica para evitar conflitos.

### Comando de Instalação no VPS

```bash
cd /opt/privacy
chmod +x scripts/deploy-vps-final.sh
sudo ./scripts/deploy-vps-final.sh
```

### O que o Script Resolve

1. **Instala dependências em ordem específica** para evitar conflitos de resolução
2. **Usa versões testadas e compatíveis**:
   - `langchain-core==0.2.43`
   - `langchain-text-splitters==0.2.4` (versão disponível)
   - `langchain==0.2.17`
   - `langchain-community==0.2.17`
   - `langchain-openai==0.2.17`

3. **Evita pip-tools/pip-compile** que estava causando conflitos de resolução

### Credenciais do Sistema

- **Database**: privacy_db
- **User**: privacy_user
- **Password**: Lgpd2025#Privacy
- **Domain**: monster.e-ness.com.br
- **SSL**: Configurado automaticamente com Let's Encrypt

### Verificação Pós-Instalação

Após a instalação, o sistema estará disponível em:
- Local: http://localhost:5000
- Público: https://monster.e-ness.com.br

### Comandos de Manutenção

```bash
# Status do serviço
systemctl status privacy

# Reiniciar serviço
systemctl restart privacy

# Ver logs
tail -f /opt/privacy/logs/gunicorn_error.log

# Verificar dependências LangChain
cd /opt/privacy
source venv/bin/activate
python -c "from langchain_openai import ChatOpenAI; print('✅ LangChain OK')"
```

### Configuração da Chave OpenAI

Após a instalação, edite o arquivo `.env`:

```bash
nano /opt/privacy/.env
```

E configure:
```
OPENAI_API_KEY=sua_chave_aqui
```

Depois reinicie:
```bash
systemctl restart privacy
```