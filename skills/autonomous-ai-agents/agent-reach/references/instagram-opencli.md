# Instagram via OpenCLI — Setup & Comandos

## Setup

1. Instalar extensão OpenCLI no Chrome:
   - Baixar: https://github.com/jackwener/OpenCLI/releases/download/ext-v1.0.21/opencli-extension-v1.0.21.zip
   - Extrair para `C:\opencli-extension\`
   - Abrir `chrome://extensions/` → Modo Desenvolvedor → Carregar sem compactação
   - Selecionar `C:\opencli-extension\`

2. Verificar conexão:
   ```bash
   opencli doctor
   # Deve mostrar: Extension: connected ✅
   ```

3. Estar logado no Instagram pelo Chrome

## Comandos

## ⚠️ REGRA CRÍTICA: ECONOMIA DE RAM

**SEMPRE** usar estas flags em todo comando OpenCLI:

```bash
--window background --site-session persistent
```

- `--window background` → NÃO abre janela do Chrome visível
- `--site-session persistent` → Reaproveita a mesma sessão (não cria nova)

**Sem essas flags**, cada comando abre uma janela nova do Chrome e consome ~200-400MB de RAM.

Use os aliases (definidos em ~/.bashrc):
```bash
oi="opencli instagram --window background --site-session persistent"
ot="opencli twitter --window background --site-session persistent"
of="opencli facebook --window background --site-session persistent"
```

### Perfil
```bash
opencli instagram profile "username" -f yaml --window background --site-session persistent
# ou via alias: oi profile "username" -f yaml
```
Retorna: username, name, bio, followers, following, posts, verified, url

### Busca de usuários
```bash
opencli instagram search "query" -f yaml --window background --site-session persistent
# ou: oi search "query" -f yaml
```
Retorna: username, name, private, verified, rank, url, rank

### Posts recentes
```bash
opencli instagram user "username" -f yaml --window background --site-session persistent
# ou: oi user "username" -f yaml
```
Retorna: caption, comments, date, likes, type (photo/video/carousel), index

### Explore
```bash
opencli instagram explore -f yaml --window background --site-session persistent
# ou: oi explore -f yaml
```

### Troubleshooting

- **Extension not connected**: Reabrir Chrome, verificar extensão instalada
- **429 Too Many Requests**: Aguardar, reduzir frequência
- **Login required**: Logar no Instagram no Chrome e tentar novamente
- **Daemon not running**: `opencli daemon restart`
