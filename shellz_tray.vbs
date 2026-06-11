' Shellz Tray Icon Launcher
' Inicia o icone de bandeja do Shellz (Pausar/Retomar Ollama)
Dim shell
Set shell = CreateObject("WScript.Shell")
shell.Run "powershell -NoProfile -ExecutionPolicy Bypass -WindowStyle Hidden -File D:\projetos\hermes-watchdog\shellz_tray.ps1", 0, False
Set shell = Nothing
