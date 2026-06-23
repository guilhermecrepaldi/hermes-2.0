# Hermes Update Guard — Análise Compensatória Obrigatória
# ============================================================
# REGRA: NENHUM update do Hermes Agent sem análise compensativa.
#        backup FORT KNOX ANTES de qualquer update.
# ============================================================

## Fluxo Obrigatório

```
1. DETECTOU update do Hermes Agent?
   │
   ├─ SIM:
   │    ├─ bash hermes-fort-knox.sh backup   ← OBRIGATORIO
   │    ├─ Analisar CHANGELOG do update
   │    │    ├─ O que mudou?
   │    │    ├─ O que isso quebra nas nossas implementações?
   │    │    └─ O que isso MELHORA?
   │    ├─ Decidir: compensa?
   │    │    ├─ SIM → aplicar update + reaplicar autoload
   │    │    └─ NÃO → bloquear update, manter versão atual
   │    └─ Documentar decisão em hermes-progress.md
   │
   └─ NÃO → continuar normalmente
```

## Checklist de Análise

Antes de aplicar qualquer update do Hermes Agent:

- [ ] Backup feito com `bash hermes-fort-knox.sh backup`
- [ ] Skills que criamos serão sobrescritas? (skills/ fica em disco separado)
- [ ] Config.yaml será sobrescrito? (autoload, compression)
- [ ] Modulos Python (watchdog/) serão afetados?
- [ ] Memorias semanticas serão perdidas?
- [ ] Autoload skills continua intacto?
- [ ] Testes passam com a nova versão?
- [ ] Nosso hermes_loop.py continua funcional?

## Comandos

```bash
# Backup blindado (obrigatório antes de update)
bash hermes-fort-knox.sh backup

# Listar backups
bash hermes-fort-knox.sh list

# Restaurar (se o update quebrar algo)
bash hermes-fort-knox.sh restore latest

# Reaplicar config essencial
# Copiar de: hermes-config-essentials.md
```
