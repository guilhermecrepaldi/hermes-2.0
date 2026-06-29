@echo off
chcp 65001 >nul
title HeadRoom - Ativacao Segura
echo ========================================
echo   Ativacao Segura - Headroom Proxy
echo ========================================
echo.
echo [1/6] Verificando se o proxy Headroom esta respondendo...
curl -s http://127.0.0.1:8787/health >nul 2>&1
if %errorlevel% neq 0 (
    echo.
    echo ❌ PROXY HEADROOM NAO ESTA RODANDO!
    echo    Inicie o proxy primeiro:
    echo    cd %%HERMES_HOME%%\hermes-agent
    echo    python headroom_proxy.py --port 8787 --upstream https://api.deepseek.com
    echo.
    pause
    exit /b 1
)
echo ✅ Proxy Headroom respondendo em :8787

echo.
echo [2/6] Verificando se o proxy consegue falar com DeepSeek...
curl -s -X POST http://127.0.0.1:8787/v1/chat/completions ^
  -H "Content-Type: application/json" ^
  -H "Authorization: Bearer sk-04b4b2bab5d949c3b40f679e742ccb8c" ^
  -d "{\"model\":\"deepseek-v4-flash\",\"messages\":[{\"role\":\"user\",\"content\":\"ping\"}],\"max_tokens\":5}" ^
  --max-time 15 >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Proxy nao consegue falar com DeepSeek! Abortando.
    pause
    exit /b 1
)
echo ✅ Proxy comunica com DeepSeek com sucesso

echo.
echo [3/6] Fazendo backup dos arquivos...
set HERMES_HOME=C:\Users\Home\AppData\Local\hermes
copy /Y "%HERMES_HOME%\config.yaml" "%HERMES_HOME%\config.yaml.bak.pre-headroom" >nul
copy /Y "%HERMES_HOME%\.env" "%HERMES_HOME%\.env.bak.pre-headroom" >nul
echo ✅ Backup criado: config.yaml.bak.pre-headroom / .env.bak.pre-headroom

echo.
echo [4/6] Alterando config.yaml para apontar pro Headroom...
python3 -c "
import yaml, os
path = r'C:\Users\Home\AppData\Local\hermes\config.yaml'
with open(path) as f:
    cfg = yaml.safe_load(f)
old_url = cfg['model']['base_url']
cfg['model']['base_url'] = 'http://localhost:8787/v1'
with open(path, 'w') as f:
    yaml.dump(cfg, f, default_flow_style=False, allow_unicode=True)
print(f'  model.base_url: {old_url} → http://localhost:8787/v1')
"
echo ✅ config.yaml alterado

echo.
echo [5/6] Alterando .env para apontar pro Headroom...
python3 -c "
path = r'C:\Users\Home\AppData\Local\hermes\.env'
with open(path) as f:
    lines = f.readlines()
new_lines = []
for line in lines:
    if line.startswith('DEEPSEEK_BASE_URL='):
        new_lines.append('DEEPSEEK_BASE_URL=http://localhost:8787/v1\n')
    elif line.startswith('OPENAI_BASE_URL='):
        new_lines.append('OPENAI_BASE_URL=http://localhost:8787/v1\n')
    else:
        new_lines.append(line)
with open(path, 'w') as f:
    f.writelines(new_lines)
print('  DEEPSEEK_BASE_URL: https://api.deepseek.com → http://localhost:8787/v1')
print('  OPENAI_BASE_URL:   https://api.deepseek.com → http://localhost:8787/v1')
"
echo ✅ .env alterado

echo.
echo [6/6] Testando conexao atraves do proxy...
echo.
echo Testando chamada via Headroom...
python3 -c "
import json, urllib.request
req = urllib.request.Request(
    'http://localhost:8787/v1/chat/completions',
    data=json.dumps({'model':'deepseek-v4-flash','messages':[{'role':'user','content':'Say exactly HELLO_HEADROOM'}],'max_tokens':10}).encode(),
    headers={'Content-Type':'application/json','Authorization':'Bearer sk-04b4b2bab5d949c3b40f679e742ccb8c'},
    method='POST'
)
resp = urllib.request.urlopen(req, timeout=20)
data = json.loads(resp.read())
content = data['choices'][0]['message']['content']
print(f'✅ Hermes CONECTADO via Headroom!')
print(f'   Resposta: {content[:50]}...' if len(content)>50 else f'   Resposta: {content}')
print(f'   Modelo: {data[\"model\"]}')
print(f'   Tokens: {data[\"usage\"][\"total_tokens\"]}')
" 2>&1
if %errorlevel% neq 0 (
    echo.
    echo ❌ FALHA NA CONEXAO VIA HEADROOM!
    echo    Fazendo rollback automatico...
    copy /Y "%HERMES_HOME%\config.yaml.bak.pre-headroom" "%HERMES_HOME%\config.yaml" >nul
    copy /Y "%HERMES_HOME%\.env.bak.pre-headroom" "%HERMES_HOME%\.env" >nul
    echo ✅ Rollback concluido! Configuracao restaurada.
    echo.
    echo O Hermes continua apontando direto pra DeepSeek. Nada quebrado.
    pause
    exit /b 1
)

echo.
echo ========================================
echo   ✅ HEADROOM ATIVADO COM SUCESSO!
echo ========================================
echo.
echo Hermes agora fala com DeepSeek via Headroom
echo Proxy:    http://localhost:8787/v1
echo Saude:    http://localhost:8787/health
echo.
echo ⚠ Para aplicar no Hermes Desktop:
echo    1. Feche o Hermes Desktop
echo    2. Abra novamente
echo    3. Pronto - ja esta usando Headroom
echo.
echo ⚠ Rollback rapido:
echo    - Rode: rollback_headroom.bat
echo    - Ou:  copy config.yaml.bak.pre-headroom config.yaml
echo.
pause
