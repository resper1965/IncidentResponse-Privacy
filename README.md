
## Deploy em VPS

### Status Atual
- ✅ Serviço funcionando na porta 5000
- ✅ SSL configurado para monster.e-ness.com.br
- ✅ Todas as dependências instaladas
- ✅ Sistema pronto para produção

### Comandos de Manutenção
```bash
# Verificar status
systemctl status privacy
curl http://localhost:5000/health

# Reiniciar serviço
systemctl restart privacy

# Ver logs
journalctl -u privacy -f
```

### Correção Rápida
Execute o script: `./scripts/fix-privacy-service.sh`
