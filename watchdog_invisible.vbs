' Hermes 2.0 - Watchdog Invisible Guardian (pythonw = zero janelas)
' Loop infinito: mantem o watchdog_hermes.py rodando 24/7
' Se o watchdog cair (exit), reinicia automaticamente
' pythonw.exe NUNCA abre console - 100% invisivel
Dim shell, retryCount, pythonwPath, scriptPath
Set shell = CreateObject("WScript.Shell")

' Caminho ABSOLUTO do pythonw.exe (evita problemas de PATH)
pythonwPath = "C:\Users\Home\AppData\Local\hermes\hermes-agent\venv\Scripts\pythonw.exe"
scriptPath = "D:\projetos\hermes-watchdog\watchdog_hermes.py"

' Tenta reiniciar watchdog ate 5 vezes se falhar rapidamente
retryCount = 0

Do While True
    ' Run watchdog via pythonw.exe (hidden=0), wait=True
    On Error Resume Next
    shell.Run pythonwPath & " " & scriptPath, 0, True
    On Error Goto 0
    
    ' If we get here, watchdog EXITED (crashed or was killed)
    retryCount = retryCount + 1
    
    ' Se falhou 5x seguidas muito rapido, espera 30s antes de tentar de novo
    If retryCount >= 5 Then
        WScript.Sleep 30000
        retryCount = 0
    Else
        WScript.Sleep 3000
    End If
Loop

Set shell = Nothing
