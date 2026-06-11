# Sistema de Backup — TOP OF THE HOUR + Hermes

## O que é incluído
```
backup_toth_YYYY-MM-DD_HHMM.zip
├── projeto/                  → D:\projetos\TOP OF THE HOUR - IA\ (HTML + catálogo + CSV + scripts)
├── hermes/
│   ├── config/
│   │   ├── config.yaml       → C:\Users\Home\AppData\Local\hermes\config.yaml
│   │   ├── .env              → variáveis de ambiente
│   │   ├── auth.json         → autenticação
│   │   ├── channel_directory.json → canais de entrega
│   │   └── hooks/            → hooks do Hermes
│   ├── skills/               → TODOS os skills (não só index-news-daily)
│   ├── cron/                 → jobs agendados
│   ├── profiles/             → perfis do Hermes
│   ├── gateway/              → gateway_state.json
│   └── memory/               → .hermes/memory (persistente entre sessões)
└── version.txt               → metadados
```

## Como usar
- **Manual:** Clique em `D:\projetos\TOP OF THE HOUR - IA\backup_toth.bat` (gera ZIP no Desktop)
- **Automático:** Cron Hermes toda madrugada às **04:00** (job_id: a6464d2bf7ea, no_agent=true, script=backup_toth.bat)
- **Git:** `D:\projetos\TOP OF THE HOUR - IA\` tem repositório git — `git log` para trackear mudanças

## Script de backup
O script `backup_toth.bat` está:
- Em `D:\projetos\TOP OF THE HOUR - IA\backup_toth.bat` (fonte)
- Em `C:\Users\Home\AppData\Local\hermes\scripts\backup_toth.bat` (para cron)
