' Shellz Tray Guardian
' Mantem o icone de bandeja do Shellz rodando 24/7
' Se travar ou fechar, reinicia automaticamente
Dim shell, retry
Set shell = CreateObject("WScript.Shell")

Do While True
    shell.Run "powershell -NoProfile -ExecutionPolicy Bypass -WindowStyle Hidden -File D:\projetos\hermes-watchdog\shellz_tray.ps1", 0, True
    ' If we get here, the PS process exited
    WScript.Sleep 3000  ' Wait 3 seconds before restarting
Loop

Set shell = Nothing
