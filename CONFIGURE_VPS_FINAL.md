# Configuração Final VPS - Sistema LGPD

## 1. EXECUTAR SCRIPTS DE CORREÇÃO

Execute estes comandos na VPS (como root):

```bash
cd /opt/privacy

# 1. Corrigir PostgreSQL e IA
chmod +x fix-postgresql-vps.sh
./fix-postgresql-vps.sh

# 2. Atualizar ambiente de produção  
chmod +x update-env-vps.sh
./update-env-vps.sh

# 3. Configurar estrutura de navegação
chmod +x test-navigation-vps.sh
./test-navigation-vps.sh
```

## 2. ADICIONAR CHAVE OPENAI

```bash
nano /opt/privacy/.env
```

Localize a linha:
```
OPENAI_API_KEY=
```

Substitua por:
```
OPENAI_API_KEY=sua_chave_aqui
```

Salve com `Ctrl+X`, depois `Y`, depois `Enter`.

## 3. REINICIAR SERVIÇOS

```bash
systemctl restart privacy
systemctl status privacy
```

## 4. VERIFICAR STATUS

Acesse: https://monster.e-ness.com.br

Você deve ver:
- ✅ PostgreSQL Ativo
- ✅ IA Ativa

## 5. TESTAR NAVEGAÇÃO

1. Clique no botão "📂 Navegar"
2. Navegue pela estrutura de diretórios
3. Selecione o diretório `data`
4. Clique "🔍 Processar Toda Árvore de Arquivos"

## 6. PRIORIDADES CONFIGURADAS

O sistema já tem 10 empresas prioritárias:

1. BRADESCO (Prioridade 1)
2. PETROBRAS (Prioridade 2) 
3. ONS (Prioridade 3)
4. EMBRAER (Prioridade 4)
5. REDE DOR (Prioridade 5)
6. GLOBO (Prioridade 6)
7. ELETROBRAS (Prioridade 7)
8. CREFISA (Prioridade 8)
9. EQUINIX (Prioridade 9)
10. COHESITY (Prioridade 10)

## 7. FUNCIONALIDADES ATIVAS

Após configuração, o sistema terá:

- **Navegação de Diretórios**: Interface visual para explorar arquivos
- **Processamento LGPD**: Escaneamento automático de dados pessoais
- **Priorização Empresarial**: Processamento baseado em importância
- **IA Semântica**: Análise inteligente com OpenAI
- **Relatórios Excel**: Exportação filtrada por empresa
- **Dashboard Tempo Real**: Monitoramento de status

## 8. SOLUÇÃO DE PROBLEMAS

Se PostgreSQL continuar inativo:
```bash
systemctl restart postgresql
systemctl enable postgresql
```

Se IA continuar inativa, verifique a chave OpenAI:
```bash
grep OPENAI_API_KEY /opt/privacy/.env
```

Para logs de erro:
```bash
journalctl -u privacy -f
```

## 9. ESTRUTURA DE DADOS

Coloque seus arquivos em:
```
/opt/privacy/data/
├── bradesco/
├── petrobras/
├── ons/
├── embraer/
└── outros/
```

O sistema automaticamente priorizará documentos por empresa identificada.

## 10. ACESSO FINAL

- **URL**: https://monster.e-ness.com.br
- **Usuário**: Sistema web (sem login)
- **Database**: PostgreSQL com prioridades configuradas
- **Logs**: /var/log/privacy/privacy.log