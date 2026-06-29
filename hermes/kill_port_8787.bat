@echo off
echo Killing headroom processes on port 8787...
for /f "tokens=5" %%i in ('netstat -ano ^| findstr :8787 ^| findstr LISTENING') do (
    echo Killing PID %%i
    taskkill /F /PID %%i 2>nul
)
echo Done.
