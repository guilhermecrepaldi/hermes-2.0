' Hermes Shellz - Ollama Invisible Launcher
' Inicia o servidor Ollama em background sem janela
' Colocado na pasta Startup para iniciar automaticamente
Dim shell
Set shell = CreateObject("WScript.Shell")
shell.Run """C:\Users\Home\AppData\Local\Programs\Ollama\ollama.exe"" serve", 0, False
Set shell = Nothing
