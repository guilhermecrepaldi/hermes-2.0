@echo off
REM ============================================================
REM headroom.bat — Windows batch toggle for Headroom Cache Proxy
REM Uso: headroom [on|off|status|stats|clear]
REM ============================================================
setlocal enabledelayedexpansion

set "HEADROOM_DIR=C:\Users\Home\neo-hermes"
set "PROXY_SCRIPT=%HEADROOM_DIR%\headroom_cache.py"
set "PIDFILE=%TEMP%\headroom.pid"
set "PORT=8787"
set "CACHE_DIR=%USERPROFILE%\.hermes\headroom_cache"

if "%1"=="" goto :status

if /I "%1"=="on" goto :on
if /I "%1"=="off" goto :off
if /I "%1"=="status" goto :status
if /I "%1"=="stats" goto :stats
if /I "%1"=="clear" goto :clear
goto :usage

:on
echo.
echo ^>^> headroom on
echo.
python "%PROXY_SCRIPT%" --port %PORT%
goto :eof

:off
echo.
echo ^>^> headroom off
echo.
REM Find and kill python processes running headroom_cache
echo Procurando processo headroom...
for /f "tokens=2 delims=," %%a in ('wmic process where "name='python.exe'" get ProcessId,CommandLine /format:csv 2^>nul ^| findstr /i "headroom_cache"') do (
    echo Matando PID %%a...
    taskkill /F /PID %%a 2>nul
)
if exist "%PIDFILE%" (
    set /p PID=<"%PIDFILE%"
    taskkill /F /PID !PID! 2>nul
    del "%PIDFILE%" 2>nul
)
echo Headroom desligado
goto :eof

:status
echo.
echo ^>^> headroom status
echo.
python -c "
import os, sys
# Check if proxy is running
import socket
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
try:
    s.connect(('127.0.0.1', %PORT%))
    print('  ✅ Proxy respondendo em http://127.0.0.1:%PORT%/v1')
    s.close()
except:
    print('  ❌ Proxy NAO esta rodando')

# Check hermes config
import subprocess
try:
    r = subprocess.run(['hermes', 'config', 'show'], capture_output=True, text=True)
    if '127.0.0.1:%PORT%' in r.stdout:
        print('  ✅ Hermes configurado para HEADROOM')
    else:
        print('  ℹ️  Hermes configurado para API DIRETA')
except:
    pass

# Cache stats
db = r'%CACHE_DIR%\cache.db'
if os.path.exists(db):
    import sqlite3
    conn = sqlite3.connect(db)
    row = conn.execute('SELECT COUNT(*), COALESCE(SUM(hits),0), COALESCE(SUM(tokens),0) FROM cache').fetchone()
    conn.close()
    print(f'  📊 Cache: {row[0]} entradas, {row[1]} hits, ~{row[2]} tokens economizados')
"
goto :eof

:stats
echo.
echo ^>^> headroom stats
echo.
python -c "
import os, sqlite3, json, time
db = r'%CACHE_DIR%\cache.db'
if not os.path.exists(db):
    print('  📭 Cache vazio')
    sys.exit(0)
conn = sqlite3.connect(db)
conn.row_factory = sqlite3.Row
row = conn.execute('SELECT COUNT(*) as e, COALESCE(SUM(hits),0) as h, COALESCE(SUM(tokens),0) as t FROM cache').fetchone()
print(f'  📦 Entradas:    {row[\"e\"]}')
print(f'  🎯 Hits:        {row[\"h\"]}')
print(f'  💰 Tokens:      {row[\"t\"]:,}')
print(f'  💵 Economia:    ~US${row[\"t\"]/1_000_000:.4f} (régua US$1/1M)')
print(f'  💵 Economia:    ~US${row[\"t\"]/1_000_000*0.15:.4f} (DeepSeek real)')
# Top 5
top = conn.execute('SELECT key, hits, tokens FROM cache ORDER BY hits DESC LIMIT 5').fetchall()
if top:
    print()
    print('  🔥 Top 5 hits:')
    for r in top:
        key = r['key'][:16]
        print(f'     {r[\"hits\"]}x — key={key}... ({r[\"tokens\"]} tok)')
conn.close()
"
goto :eof

:clear
echo.
echo ^>^> headroom clear
echo.
if exist "%CACHE_DIR%\cache.db" (
    python -c "
import sqlite3, os
db = r'%CACHE_DIR%\cache.db'
if os.path.exists(db):
    conn = sqlite3.connect(db)
    count = conn.execute('SELECT COUNT(*) FROM cache').fetchone()[0]
    conn.execute('DELETE FROM cache')
    conn.commit()
    conn.close()
    print(f'  🗑️  {count} entradas removidas.')
"
    echo Cache limpo!
) else (
    echo Cache vazio — nada a limpar.
)
goto :eof

:usage
echo Uso: headroom [on^|off^|status^|stats^|clear]
echo.
echo   on       — Liga o proxy cache (porta %PORT%)
echo   off      — Desliga o proxy, volta API direta
echo   status   — Mostra status atual
echo   stats    — Métricas detalhadas do cache
echo   clear    — Limpa todo o cache
goto :eof
