# Como Encontrar Version Control no Replit

## Localização do Git no Replit

### Opção 1: Painel Lateral Esquerdo
Procure por um ícone que parece:
- 🔗 Ramificação/Fork
- 📋 Lista com setas
- "Git" ou "Version Control"

### Opção 2: Menu Tools
1. Clique em "Tools" no menu superior
2. Procure por "Git" ou "Version Control"

### Opção 3: Atalho de Teclado
- Pressione `Ctrl + Shift + G` (ou `Cmd + Shift + G` no Mac)

### Opção 4: Shell (Alternativa)
Se não encontrar a interface, podemos usar comandos no Shell:

```bash
# Verificar status atual
du -sh .git/

# Ver arquivos Git
ls -la .git/objects/pack/
```

## Se Não Encontrar Git UI

### Solução Alternativa: Novo Repositório
1. Criar novo repositório no GitHub
2. No Replit, ir em "File" → "Download as ZIP"
3. Extrair ZIP e fazer upload no GitHub manualmente

### Ou Usar Shell Diretamente
```bash
# Remover histórico (se conseguir)
rm -rf .git
git init
git add .gitignore *.py templates/ scripts/ README.md replit.md .env.example
git commit -m "Sistema LGPD - repositório limpo"
```

## Importante
O problema são os 172MB no pack do Git. Precisamos resetar o histórico de alguma forma.

Qual dessas opções você consegue encontrar no seu Replit?