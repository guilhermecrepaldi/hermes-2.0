' Hermes 2.0 - Watchdog Invisible Launcher
' Executa o watchdog_hermes.bat SEM abrir janela cmd
' Usado pelo guardian e pelo atalho de startup
Dim shell
Set shell = CreateObject("WScript.Shell")
shell.Run "D:\projetos\hermes-watchdog\watchdog_hermes.bat", 0, False
Set shell = Nothing
