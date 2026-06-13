#!/usr/bin/env python3
"""
Hermes Workbench — CLI Unificada
Todas as ferramentas do Workbench Hermes em um único comando.
Uso: hermes-workbench <comando> [args]

Comandos Base:
  panorama <path>      Panorama completo de qualquer projeto (S3/S2)
  compress <texto>     Comprime tool outputs para economizar tokens
  search <path> <q>    Busca solucao em projeto local
  grep <query>         Busca codigo em 1M+ repos GitHub (grep.app)
  router <tarefa>      Classifica tarefa em S1/S2/S3
  status               Status do watchdog + shells

Novos Comandos (v2):
  explain <comando>    Explica comando shell (ExplainShell)
  devtoys <ferram>     Ferramentas de dev (hash, jwt, base64, regex, json...)
  jtree <arquivo>      Visualiza JSON/YAML como arvore interativa

DevToys Tools:
  hash <texto>          Gera MD5, SHA1, SHA256, SHA512
  jwt-decode <token>    Decodifica JWT sem validar
  base64 <str> <texto>  encode|decode base64
  uuid                  Gera UUID v4
  regex <p> <texto>     Testa regex contra texto
  json-format <arquivo> Formata JSON com indentacao
  json-validate <arquivo> Valida JSON
  lorem [n]             Gera texto Lorem Ipsum (n paragrafos)
  diff <a> <b>          Compara dois textos
  colors                Mostra paleta de cores ANSI
  ip <endereco>         Info de IP (local)
  timestamp [epoch]     Converte epoch para data/hora

Ajuda:
  help                  Mostra esta ajuda
"""
import sys
import os
import json
import hashlib
import uuid
import re
import base64 as b64
import struct
import socket
import subprocess
import random
import textwrap
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# ══════════════════════════════════════════════════════════════
# EXPLAINSHELL — Explica comandos shell
# ══════════════════════════════════════════════════════════════

def cmd_explain(args):
    """Explica um comando shell quebrando flags e argumentos."""
    if not args:
        print("Uso: hermes-workbench explain <comando>")
        print('  hermes-workbench explain "grep -rn padrão *.py"')
        print('  hermes-workbench explain "docker run -d nginx"')
        return 1

    cmd = " ".join(args)
    print("=" * 60)
    print(f"🐚 EXPLAIN: {cmd}")
    print("=" * 60)

    # Split into command + args
    parts = cmd.split()
    if not parts:
        return 1

    command = parts[0]
    cmd_args = parts[1:]

    print(f"\n📌 Comando: {command}")
    if cmd_args:
        print(f"   Args:    {' '.join(cmd_args)}")
    print(f"   Total:   {len(parts)} tokens")

    # Knowledge base de flags comuns
    FLAG_KNOWLEDGE = {
        # grep
        "grep:-r": "Busca recursiva em diretorios",
        "grep:-R": "Busca recursiva (segue links simbolicos)",
        "grep:-n": "Mostra numeros das linhas",
        "grep:-i": "Ignora maiusculas/minusculas",
        "grep:-v": "Inverte a busca (mostra linhas que NAO casam)",
        "grep:-l": "Mostra apenas nomes de arquivos com match",
        "grep:-c": "Conta matches em vez de mostrar linhas",
        "grep:-w": "Match de palavra inteira",
        "grep:-E": "Usa regex estendida (-E)",
        "grep:-H": "Sempre mostra nome do arquivo",
        "grep:--include": "Filtra arquivos por padrao (ex: --include='*.py')",
        "grep:--exclude": "Exclui arquivos por padrao",
        "grep:--exclude-dir": "Exclui diretorios (ex: --exclude-dir=.git)",
        "grep:-A": "Mostra N linhas APOS o match (ex: -A 3)",
        "grep:-B": "Mostra N linhas ANTES do match (ex: -B 3)",
        "grep:-C": "Mostra N linhas de contexto (antes e depois)",
        "grep:--color": "Colore os matches no output",
        # ls
        "ls:-l": "Formato longo (permissoes, dono, tamanho, data)",
        "ls:-a": "Mostra arquivos ocultos (iniciados com .)",
        "ls:-h": "Tamanhos legiveis (KB, MB, GB)",
        "ls:-S": "Ordena por tamanho (maior primeiro)",
        "ls:-t": "Ordena por data de modificacao",
        "ls:-r": "Ordenacao reversa",
        "ls:-R": "Lista subdiretorios recursivamente",
        "ls:-d": "Lista diretorios como arquivos (nao seu conteudo)",
        "ls:-1": "Um arquivo por linha",
        # git
        "git:clone": "Clona um repositorio remoto para o diretorio local",
        "git:commit": "Cria um commit com as mudancas staged",
        "git:push": "Envia commits locais para o repositorio remoto",
        "git:pull": "Baixa e integra mudancas do repositorio remoto",
        "git:add": "Adiciona arquivos ao stage (prepara para commit)",
        "git:status": "Mostra o estado da working tree",
        "git:log": "Mostra o historico de commits",
        "git:diff": "Mostra diferencas entre commits/branches",
        "git:branch": "Lista, cria ou deleta branches",
        "git:checkout": "Troca de branch ou restaura arquivos",
        "git:merge": "Faz merge de branches",
        "git:rebase": "Reaplica commits em cima de outra base",
        "git:remote": "Gerencia repositorios remotos",
        "git:fetch": "Baixa objetos e refs de outro repositorio",
        "git:stash": "Salva mudancas temporariamente",
        "git:tag": "Cria/lista/deleta tags",
        "git:reset": "Reseta HEAD para um estado especifico",
        "git:revert": "Reverte um commit criando novo commit",
        "git:clean": "Remove arquivos nao rastreados",
        "git:init": "Inicializa um novo repositorio git",
        "git:config": "Configura opcoes do git",
        "git:help": "Mostra ajuda do git",
        "git:-m": "Mensagem do commit (ex: git commit -m 'msg')",
        "git:--amend": "Altera o ultimo commit (ex: git commit --amend)",
        "git:-a": "Adiciona automaticamente arquivos modificados ao commit",
        "git:--all": "Aplica a todas as branches ou remotes",
        "git:--force": "Forca operacao (ex: git push --force)",
        "git:-d": "Deleta branch (ex: git branch -d nome)",
        "git:-D": "Forca delecao de branch",
        "git:--hard": "Reset hard (perde mudancas nao commitadas)",
        "git:--soft": "Reset soft (mantem mudancas no stage)",
        "git:--abort": "Cancela operacao em andamento (rebase, merge)",
        "git:--continue": "Continua operacao apos resolver conflitos",
        # docker
        "docker:run": "Roda um container a partir de uma imagem",
        "docker:ps": "Lista containers rodando",
        "docker:images": "Lista imagens locais",
        "docker:build": "Constroi imagem a partir de Dockerfile",
        "docker:pull": "Baixa imagem do registry",
        "docker:push": "Envia imagem para o registry",
        "docker:stop": "Para um container rodando",
        "docker:start": "Inicia container parado",
        "docker:restart": "Reinicia container",
        "docker:rm": "Remove container(s)",
        "docker:rmi": "Remove imagem(s)",
        "docker:exec": "Executa comando em container rodando",
        "docker:logs": "Mostra logs do container",
        "docker:compose": "Gerencia multi-containers (docker-compose)",
        "docker:network": "Gerencia redes Docker",
        "docker:volume": "Gerencia volumes Docker",
        "docker:-d": "Modo detached (roda em background)",
        "docker:-it": "Modo interativo com terminal (-i + -t)",
        "docker:-p": "Mapeia porta (ex: -p 8080:80)",
        "docker:-v": "Monta volume (ex: -v /host:/container)",
        "docker:-e": "Variavel de ambiente (ex: -e KEY=value)",
        "docker:--name": "Nome do container",
        "docker:--rm": "Remove container automaticamente ao parar",
        # find
        "find:-name": "Busca por nome de arquivo (ex: -name '*.py')",
        "find:-type": "Filtra por tipo (f=arquivo, d=diretorio)",
        "find:-size": "Filtra por tamanho (ex: -size +1M)",
        "find:-mtime": "Filtra por data de modificacao (dias)",
        "find:-exec": "Executa comando para cada resultado",
        "find:-delete": "Deleta arquivos encontrados",
        "find:-maxdepth": "Limita profundidade da busca",
        "find:-mindepth": "Ignora niveis iniciais da busca",
        # chmod
        "chmod:-R": "Recursivo (aplica a subdiretorios)",
        "chmod:--reference": "Usa permissoes de outro arquivo como referencia",
        # cp / mv / rm
        "cp:-r": "Recursivo (copia diretorios)",
        "cp:-f": "Forca copia (sobrescreve sem perguntar)",
        "cp:-v": "Modo verbose (mostra o que esta copiando)",
        "cp:-i": "Modo interativo (pergunta antes de sobrescrever)",
        "cp:-p": "Preserva atributos (permissoes, timestamps)",
        "mv:-f": "Forca mover/renomear",
        "mv:-i": "Modo interativo",
        "mv:-v": "Modo verbose",
        "rm:-f": "Forca remocao (nao pergunta)",
        "rm:-r": "Recursivo (remove diretorios)",
        "rm:-i": "Modo interativo",
        "rm:-v": "Modo verbose",
        # python
        "python:-m": "Executa modulo como script (ex: python -m pytest)",
        "python:-c": "Executa comando Python inline",
        "python:-i": "Modo interativo apos execucao",
        "python:-V": "Mostra versao do Python",
        "python:-B": "Nao escreve arquivos .pyc",
        "python:-O": "Modo otimizado (remove asserts)",
        "python:-u": "Output unbuffered (uteis para pipes/logs)",
        # pip
        "pip:install": "Instala pacotes",
        "pip:uninstall": "Remove pacotes",
        "pip:list": "Lista pacotes instalados",
        "pip:freeze": "Lista pacotes no formato requirements.txt",
        "pip:show": "Mostra detalhes de um pacote",
        "pip:search": "Busca pacotes no PyPI",
        "pip:--upgrade": "Atualiza pacote",
        "pip:--user": "Instala apenas para o usuario (sem admin)",
        "pip:-r": "Instala de um arquivo de requisitos",
        # curl
        "curl:-o": "Salva output em arquivo",
        "curl:-O": "Salva com nome do servidor",
        "curl:-L": "Segue redirecionamentos",
        "curl:-H": "Adiciona header HTTP (ex: -H 'Auth: token')",
        "curl:-d": "Envia dados no body (POST)",
        "curl:-X": "Metodo HTTP (GET, POST, PUT, DELETE)",
        "curl:-v": "Modo verbose",
        "curl:-s": "Modo silencioso (sem progresso)",
        "curl:-i": "Inclui headers HTTP na resposta",
        "curl:-k": "Ignora erros de certificado SSL",
        "curl:--data": "Envia dados POST",
        "curl:--header": "Adiciona header",
        "curl:--cookie": "Envia cookie",
        "curl:--max-time": "Timeout maximo em segundos",
        # wget
        "wget:-O": "Salva em arquivo especifico",
        "wget:-c": "Continua download interrompido",
        "wget:-q": "Modo silencioso",
        "wget:-P": "Diretorio de destino",
        "wget:--timeout": "Timeout em segundos",
        "wget:--tries": "Numero de tentativas",
        # ps / kill / top
        "ps:aux": "Lista TODOS os processos do sistema",
        "ps:-ef": "Lista processos no formato completo",
        "ps:-u": "Filtra por usuario",
        "ps:-C": "Filtra por nome de comando",
        "kill:-9": "Forca matar processo (SIGKILL)",
        "kill:-15": "Termina processo graciosamente (SIGTERM - padrao)",
        "kill:-2": "Interrompe processo (SIGINT - como Ctrl+C)",
        "kill:-1": "Reinicia/config recarregada (SIGHUP)",
        "top:-u": "Filtra por usuario",
        "top:-p": "Monitora PIDs especificos",
        # ssh / scp
        "ssh:-i": "Arquivo de chave privada (ex: -i ~/.ssh/id_rsa)",
        "ssh:-p": "Porta SSH (ex: -p 2222)",
        "ssh:-v": "Modo verbose (debug)",
        "ssh:-N": "Nao executa comando (só tunel)",
        "ssh:-L": "Port forwarding local",
        "ssh:-R": "Port forwarding remoto",
        "scp:-r": "Recursivo (copia diretorios)",
        "scp:-P": "Porta SSH",
        "scp:-i": "Arquivo de chave privada",
        # tar
        "tar:-c": "Cria arquivo (create)",
        "tar:-x": "Extrai arquivo (extract)",
        "tar:-z": "Filtro gzip (arquivos .tar.gz)",
        "tar:-j": "Filtro bzip2 (arquivos .tar.bz2)",
        "tar:-f": "Arquivo de destino/origem",
        "tar:-v": "Modo verbose",
        "tar:-t": "Lista conteudo sem extrair",
        "tar:--exclude": "Exclui padrao",
        # systemctl
        "systemctl:start": "Inicia servico",
        "systemctl:stop": "Para servico",
        "systemctl:restart": "Reinicia servico",
        "systemctl:status": "Status do servico",
        "systemctl:enable": "Habilita inicio automatico",
        "systemctl:disable": "Desabilita inicio automatico",
        "systemctl:list-units": "Lista servicos",
        "systemctl:is-active": "Verifica se servico esta ativo",
        # xargs
        "xargs:-n": "Maximo de argumentos por execucao (ex: -n 1)",
        "xargs:-I": "String de substituicao (ex: -I {} cmd {})",
        "xargs:-P": "Execucao paralela (N processos)",
        "xargs:-0": "Espera input delimitado por null",
        # watch
        "watch:-n": "Intervalo em segundos (ex: watch -n 2 cmd)",
        "watch:-d": "Destaca diferencas entre execucoes",
        # sort / uniq / wc / cut / head / tail
        "sort:-n": "Ordenacao numerica",
        "sort:-r": "Ordenacao reversa",
        "sort:-u": "Remove duplicatas (unique)",
        "sort:-t": "Separador de campos (ex: -t ',')",
        "sort:-k": "Coluna para ordenar",
        "uniq:-c": "Conta ocorrencias",
        "uniq:-i": "Ignora maiusculas/minusculas",
        "uniq:-d": "Mostra apenas duplicatas",
        "wc:-l": "Conta linhas",
        "wc:-w": "Conta palavras",
        "wc:-c": "Conta caracteres/bytes",
        "cut:-d": "Delimitador de campo (ex: -d ',')",
        "cut:-f": "Campos a extrair (ex: -f 1,3)",
        "head:-n": "Numero de linhas (ex: -n 20)",
        "head:-c": "Numero de bytes",
        "tail:-n": "Numero de linhas do final",
        "tail:-f": "Modo follow (atualiza em tempo real)",
        "tail:-F": "Follow com rotacao de arquivo",
        # tee / echo / cat / less / more
        "tee:-a": "Append em vez de sobrescrever",
        "echo:-n": "Nao adiciona newline no final",
        "echo:-e": "Interpreta escapes (\n, \t, etc.)",
        "cat:-n": "Numera linhas",
        "cat:-b": "Numera linhas nao-branco",
        "cat:-s": "Suprime linhas brancas repetidas",
        "cat:-E": "Mostra $ no final de cada linha",
        "less:-N": "Mostra numeros de linha",
        "less:-S": "Nao quebra linhas longas (scroll horizontal)",
        "less:-i": "Busca ignora maiusculas/minusculas",
        # sed / awk / tr / tee
        "sed:-i": "Edicao in-place (modifica arquivo original)",
        "sed:-n": "Suprime output padrao (so mostra com p)",
        "sed:-e": "Script de edicao",
        "sed:-r": "Regex estendida",
        "awk:-F": "Separador de campos (ex: -F ',')",
        "awk:-v": "Define variavel (ex: -v var=val)",
        "tr:-d": "Deleta caracteres encontrados",
        "tr:-s": "Squish (comprime repeticoes)",
        "tr:-c": "Complemento (inverte conjunto)",
        "tee:-a": "Append em vez de sobrescrever",
    }

    # Explain the command itself
    if command in FLAG_KNOWLEDGE:
        key = command
        print(f"\n📖 {command}: {FLAG_KNOWLEDGE[key]}")

    # Explain each arg
    if cmd_args:
        print(f"\n🔍 ARGUMENTOS:")
        i = 0
        while i < len(cmd_args):
            arg = cmd_args[i]
            key = f"{command}:{arg}"

            if key in FLAG_KNOWLEDGE:
                # Check if next arg could be a value for this flag
                if i + 1 < len(cmd_args) and not cmd_args[i + 1].startswith('-'):
                    val = cmd_args[i + 1]
                    print(f"  {arg:<20} {FLAG_KNOWLEDGE[key]:<50} → valor: {val}")
                    i += 2
                else:
                    print(f"  {arg:<20} {FLAG_KNOWLEDGE[key]}")
                    i += 1
            elif arg.startswith('-') and not arg.startswith('--') and len(arg) > 2:
                # Combined short flags like -rn = -r + -n
                flags = arg[1:]
                explained = []
                for f in flags:
                    fkey = f"{command}:-{f}"
                    if fkey in FLAG_KNOWLEDGE:
                        explained.append(f"-{f}: {FLAG_KNOWLEDGE[fkey]}")
                    else:
                        explained.append(f"-{f}: ?")
                print(f"  {arg:<20} Flags combinadas:")
                for exp in explained:
                    print(f"    {'':20}{exp}")
                i += 1
            elif arg.startswith('-'):
                # Unknown flag - try partial match
                flag_base = arg.split('=')[0] if '=' in arg else arg
                partial_matches = [k for k in FLAG_KNOWLEDGE if k.startswith(f"{command}:") and 
                                  (flag_base in k or arg in k)]
                if partial_matches:
                    best = partial_matches[0]
                    print(f"  {arg:<20} {FLAG_KNOWLEDGE[best]} (aproximado)")
                else:
                    print(f"  {arg:<20} Flag nao reconhecida na base de conhecimento")
                i += 1
            else:
                # Non-flag argument
                if i == 0:
                    print(f"  {arg:<20} Argumento principal / caminho")
                else:
                    print(f"  {arg:<20} Argumento")
                i += 1

    # Show estimated man page
    print(f"\n📘 DICA: man {command} para documentacao completa")

    return 0


# ══════════════════════════════════════════════════════════════
# DEVTOYS — Ferramentas de desenvolvedor
# ══════════════════════════════════════════════════════════════

def cmd_devtoys(args):
    """Ferramentas de desenvolvedor: hash, jwt, base64, regex, json, uuid, diff."""
    if not args:
        print("Uso: hermes-workbench devtoys <ferramenta> [args]")
        print("")
        print("Ferramentas disponiveis:")
        print("  hash <texto>              MD5, SHA1, SHA256, SHA512")
        print("  jwt-decode <token>        Decodifica JWT")
        print('  base64 <encode|decode> <t> Base64')
        print("  uuid                      Gera UUID v4")
        print('  regex <pattern> <texto>   Testa regex')
        print("  json-format <arquivo>     Formata JSON")
        print("  json-validate <arquivo>   Valida JSON")
        print("  lorem [n]                 Lorem Ipsum (n paragrafos)")
        print('  diff <a> <b>              Compara textos')
        print("  colors                    Paleta de cores ANSI")
        print("  timestamp [epoch]         Converte epoch para data")
        print("  ip                        Mostra IP local")
        return 1

    tool = args[0]
    tool_args = args[1:]

    tools = {
        'hash': _dev_hash,
        'jwt-decode': _dev_jwt_decode,
        'base64': _dev_base64,
        'uuid': _dev_uuid,
        'regex': _dev_regex,
        'json-format': _dev_json_format,
        'json-validate': _dev_json_validate,
        'lorem': _dev_lorem,
        'diff': _dev_diff,
        'colors': _dev_colors,
        'timestamp': _dev_timestamp,
        'ip': _dev_ip,
    }

    if tool not in tools:
        print(f"Ferramenta desconhecida: {tool}")
        print("Use 'hermes-workbench devtoys' para ver as disponiveis.")
        return 1

    return tools[tool](tool_args)


def _dev_hash(args):
    if not args:
        print("Uso: hermes-workbench devtoys hash <texto>")
        return 1
    text = " ".join(args).encode('utf-8')
    print(f"  MD5:    {hashlib.md5(text).hexdigest()}")
    print(f"  SHA1:   {hashlib.sha1(text).hexdigest()}")
    print(f"  SHA256: {hashlib.sha256(text).hexdigest()}")
    print(f"  SHA512: {hashlib.sha512(text).hexdigest()}")
    return 0


def _dev_jwt_decode(args):
    if not args:
        print("Uso: hermes-workbench devtoys jwt-decode <token>")
        return 1
    token = args[0]
    parts = token.split('.')
    if len(parts) != 3:
        print("  ❌ Token JWT invalido (deve ter 3 partes separadas por .)")
        return 1
    try:
        # Fix padding for base64 decode
        def b64_decode(data):
            data = data.replace('-', '+').replace('_', '/')
            pad = 4 - len(data) % 4
            if pad != 4:
                data += '=' * pad
            return b64.b64decode(data)
        
        header = json.loads(b64_decode(parts[0]))
        payload = json.loads(b64_decode(parts[1]))
        
        print("  📋 HEADER:")
        for k, v in header.items():
            print(f"    {k}: {v}")
        print("\n  📋 PAYLOAD:")
        for k, v in payload.items():
            if k == 'exp' or k == 'iat' or k == 'nbf':
                dt = datetime.fromtimestamp(v, tz=timezone.utc)
                print(f"    {k}: {v} ({dt.strftime('%Y-%m-%d %H:%M:%S UTC')})")
            else:
                print(f"    {k}: {v}")
        print(f"\n  🔏 Signature: {parts[2][:30]}... ({len(parts[2])} chars)")
        if 'exp' in payload:
            exp = payload['exp']
            now = datetime.now(timezone.utc).timestamp()
            remaining = exp - now
            if remaining > 0:
                print(f"  ✅ Token VALIDO (expira em {remaining/86400:.1f} dias)")
            else:
                print(f"  ❌ Token EXPIRADO ha {-remaining/86400:.1f} dias")
        return 0
    except Exception as e:
        print(f"  ❌ Erro ao decodificar: {e}")
        return 1


def _dev_base64(args):
    if len(args) < 2:
        print("Uso: hermes-workbench devtoys base64 <encode|decode> <texto>")
        return 1
    op = args[0]
    text = " ".join(args[1:])
    if op == 'encode':
        result = b64.b64encode(text.encode()).decode()
        print(result)
    elif op == 'decode':
        try:
            result = b64.b64decode(text).decode()
            print(result)
        except Exception as e:
            print(f"  ❌ Erro: {e}")
            return 1
    else:
        print(f"  ❌ Operacao invalida: {op} (use encode ou decode)")
        return 1
    return 0


def _dev_uuid(args):
    uid = uuid.uuid4()
    print(f"  UUID v4: {uid}")
    print(f"  Hex:     {uid.hex}")
    print(f"  URN:     urn:uuid:{uid}")
    return 0


def _dev_regex(args):
    if len(args) < 2:
        print("Uso: hermes-workbench devtoys regex <pattern> <texto>")
        return 1
    pattern = args[0]
    text = " ".join(args[1:])
    try:
        compiled = re.compile(pattern)
        matches = compiled.findall(text)
        print(f"  Pattern:  /{pattern}/")
        print(f"  Texto:    {text[:100]}{'...' if len(text)>100 else ''}")
        print(f"  Matches:  {len(matches)}")
        for i, m in enumerate(matches[:10]):
            print(f"    [{i+1}] {str(m)[:80]}")
        if len(matches) > 10:
            print(f"    ... +{len(matches)-10} matches")
        if not matches:
            print("  (nenhum match encontrado)")
    except re.error as e:
        print(f"  ❌ Regex invalido: {e}")
        return 1
    return 0


def _dev_json_format(args):
    if not args:
        print("Uso: hermes-workbench devtoys json-format <arquivo>")
        return 1
    path = args[0]
    try:
        with open(path, encoding='utf-8') as f:
            data = json.load(f)
        print(json.dumps(data, indent=2, ensure_ascii=False))
    except FileNotFoundError:
        print(f"  ❌ Arquivo nao encontrado: {path}")
        return 1
    except json.JSONDecodeError as e:
        print(f"  ❌ JSON invalido: {e}")
        return 1
    return 0


def _dev_json_validate(args):
    if not args:
        print("Uso: hermes-workbench devtoys json-validate <arquivo>")
        return 1
    path = args[0]
    try:
        with open(path, encoding='utf-8') as f:
            data = json.load(f)
        print(f"  ✅ JSON VALIDO")
        if isinstance(data, dict):
            print(f"     Objeto com {len(data)} chaves")
        elif isinstance(data, list):
            print(f"     Array com {len(data)} itens")
        else:
            print(f"     Tipo: {type(data).__name__}")
    except FileNotFoundError:
        print(f"  ❌ Arquivo nao encontrado: {path}")
        return 1
    except json.JSONDecodeError as e:
        print(f"  ❌ JSON INVALIDO: {e}")
        return 1
    return 0


def _dev_lorem(args):
    n = int(args[0]) if args else 3
    ipsum = """Lorem ipsum dolor sit amet consectetur adipiscing elit sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident sunt in culpa qui officia deserunt mollit anim id est laborum."""
    words = ipsum.split()
    for p in range(n):
        random.shuffle(words)
        line = ' '.join(words[:20 + random.randint(5, 15)])
        print(f"\n{line.capitalize()}.")
    return 0


def _dev_diff(args):
    if len(args) < 2:
        print("Uso: hermes-workbench devtoys diff <texto_a> <texto_b>")
        return 1
    a_lines = args[0].split('\n')
    b_lines = args[1].split('\n')
    # Simple line diff
    import difflib
    diff = difflib.unified_diff(a_lines, b_lines, lineterm='')
    for line in diff:
        if line.startswith('+'):
            print(f"\033[32m{line}\033[0m")  # green
        elif line.startswith('-'):
            print(f"\033[31m{line}\033[0m")  # red
        elif line.startswith('@@'):
            print(f"\033[36m{line}\033[0m")  # cyan
        else:
            print(line)
    return 0


def _dev_colors(args):
    """Mostra paleta de cores ANSI."""
    print("  PALETA DE CORES ANSI:")
    print()
    for fg in range(30, 38):
        line = ""
        for bg in range(40, 48):
            line += f"\033[{fg};{bg}m {fg:2d}/{bg:2d} \033[0m"
        print(f"  {line}")
    print()
    print("  CORES BRILHANTES (negrito + cor):")
    for fg in range(90, 98):
        line = ""
        for bg in range(100, 108):
            line += f"\033[{fg};{bg}m {fg:2d}/{bg:2d} \033[0m"
        print(f"  {line}")
    print()
    print("  Formatos:")
    print("    \033[1mNegrito\033[0m    \033[3mItalico\033[0m    \033[4mSublinhado\033[0m    \033[7mInvertido\033[0m    \033[9mRiscado\033[0m")
    return 0


def _dev_timestamp(args):
    if args:
        try:
            ts = float(args[0])
            dt = datetime.fromtimestamp(ts, tz=timezone.utc)
            print(f"  Epoch:    {ts}")
            print(f"  Data UTC: {dt.strftime('%Y-%m-%d %H:%M:%S UTC')}")
            print(f"  Data:     {dt.strftime('%Y-%m-%d %H:%M:%S')} (seu fuso)")
        except ValueError:
            print(f"  ❌ Epoch invalido: {args[0]}")
            return 1
    else:
        now = datetime.now(timezone.utc)
        print(f"  Agora:         {now.strftime('%Y-%m-%d %H:%M:%S UTC')}")
        print(f"  Epoch atual:   {now.timestamp():.3f}")
        print(f"  Epoch (int):   {int(now.timestamp())}")
    return 0


def _dev_ip(args):
    try:
        hostname = socket.gethostname()
        ip = socket.gethostbyname(hostname)
        print(f"  Hostname: {hostname}")
        print(f"  IP Local: {ip}")
        # Try to get external IP
        try:
            import urllib.request
            ext_ip = urllib.request.urlopen("https://api.ipify.org", timeout=5).read().decode()
            print(f"  IP Externo: {ext_ip}")
        except:
            print(f"  IP Externo: (nao foi possivel determinar)")
    except Exception as e:
        print(f"  ❌ Erro: {e}")
    return 0


# ══════════════════════════════════════════════════════════════
# JSON TREE — Visualizacao de dados como arvore
# ══════════════════════════════════════════════════════════════

def cmd_jtree(args):
    """Visualiza JSON/YAML como arvore interativa no terminal."""
    if not args:
        print("Uso: hermes-workbench jtree <arquivo.json>")
        print("  Visualiza JSON como arvore com cores e colapso.")
        return 1

    path = args[0]
    if not os.path.exists(path):
        print(f"  ❌ Arquivo nao encontrado: {path}")
        return 1

    try:
        with open(path, encoding='utf-8') as f:
            data = json.load(f)
    except json.JSONDecodeError:
        # Try YAML
        try:
            import yaml
            with open(path, encoding='utf-8') as f:
                data = yaml.safe_load(f)
        except ImportError:
            print("  ❌ Para YAML, instale: pip install pyyaml")
            return 1
        except Exception as e:
            print(f"  ❌ Erro ao ler arquivo: {e}")
            return 1

    print(f"📂 {os.path.basename(path)}")
    print(f"{'='*50}")
    _print_tree(data)
    return 0


def _print_tree(data, indent=0, prefix="", is_last=True, max_depth=6):
    """Print data as a tree with colors."""
    if indent > max_depth:
        print(f"{'  ' * indent}  \033[90m... (profundidade maxima)\033[0m")
        return

    connector = "└── " if is_last else "├── "
    extender = "    " if is_last else "│   "

    if isinstance(data, dict):
        items = list(data.items())
        if indent == 0:
            print(f"  \033[93mObject\033[0m ({len(items)} keys)")
        for i, (key, val) in enumerate(items):
            last = i == len(items) - 1
            conn = "└── " if last else "├── "
            ext = "    " if last else "│   "

            if isinstance(val, dict):
                print(f"{'  ' * (indent + 1)}{conn}\033[36m{key}\033[0m: \033[93m{{...}}\033[0m ({len(val)} keys)")
                _print_tree(val, indent + 2, ext, True, max_depth)
            elif isinstance(val, list):
                print(f"{'  ' * (indent + 1)}{conn}\033[36m{key}\033[0m: \033[94m[{len(val)}]\033[0m")
                if len(val) > 0 and indent + 1 < max_depth:
                    for j, item in enumerate(val[:5]):
                        last_item = j == len(val) - 1 or j == 4
                        _print_tree(item, indent + 2, ext, last_item, max_depth)
                    if len(val) > 5:
                        print(f"{'  ' * (indent + 2)}{ext}  \033[90m... (+{len(val)-5} items)\033[0m")
            elif isinstance(val, str):
                v = val[:80].replace('\n', '\\n')
                suffix = "..." if len(val) > 80 else ""
                print(f"{'  ' * (indent + 1)}{conn}\033[36m{key}\033[0m: \033[32m\"{v}{suffix}\"\033[0m")
            elif isinstance(val, bool):
                print(f"{'  ' * (indent + 1)}{conn}\033[36m{key}\033[0m: \033[33m{str(val)}\033[0m")
            elif isinstance(val, (int, float)):
                print(f"{'  ' * (indent + 1)}{conn}\033[36m{key}\033[0m: \033[35m{val}\033[0m")
            elif val is None:
                print(f"{'  ' * (indent + 1)}{conn}\033[36m{key}\033[0m: \033[90mnull\033[0m")
            else:
                print(f"{'  ' * (indent + 1)}{conn}\033[36m{key}\033[0m: {val}")

    elif isinstance(data, list):
        if indent == 0:
            print(f"  \033[94mArray\033[0m ({len(data)} items)")
        for i, item in enumerate(data[:10]):
            last = i == len(data) - 1 or i == 9
            conn = "└── " if last else "├── "
            _print_tree(item, indent + 1, "", last, max_depth)
        if len(data) > 10:
            print(f"{'  ' * (indent + 1)}  \033[90m... (+{len(data)-10} items)\033[0m")
    else:
        if isinstance(data, str):
            v = data[:80].replace('\n', '\\n')
            print(f"{'  ' * indent}  \033[32m\"{v}\"\033[0m")
        elif isinstance(data, bool):
            print(f"{'  ' * indent}  \033[33m{str(data)}\033[0m")
        elif isinstance(data, (int, float)):
            print(f"{'  ' * indent}  \033[35m{data}\033[0m")
        elif data is None:
            print(f"{'  ' * indent}  \033[90mnull\033[0m")
        else:
            print(f"{'  ' * indent}  {data}")


# ══════════════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════════════

def cmd_help(args):
    print(__doc__)
    print("\nExemplos:")
    print('  hermes-workbench panorama D:\\meu-projeto')
    print('  hermes-workbench compress "texto longo..."')
    print('  hermes-workbench explain "grep -rn padrao *.py"')
    print('  hermes-workbench devtoys hash "minha senha"')
    print('  hermes-workbench devtoys jwt-decode eyJ...')
    print('  hermes-workbench devtoys uuid')
    print('  hermes-workbench devtoys lorem 5')
    print('  hermes-workbench devtoys colors')
    print('  hermes-workbench jtree dados.json')
    print('  hermes-workbench router "Criar funcao"')
    return 0


def main():
    if len(sys.argv) < 2 or sys.argv[1] in ('-h', '--help', 'help'):
        return cmd_help(sys.argv[2:])

    cmd = sys.argv[1]
    args = sys.argv[2:]

    commands = {
        'panorama': lambda a: _import_and_run('s3_headroom', 'cmd_panorama_wrapper', a),
        'compress': lambda a: _import_and_run('s3_headroom', 'cmd_compress_wrapper', a),
        'search': lambda a: _import_and_run('s3_headroom', 'cmd_search_wrapper', a),
        'grep': cmd_grep,
        'router': lambda a: _import_and_run('s1_router', 'cmd_router_wrapper', a),
        'status': cmd_status,
        'explain': cmd_explain,
        'devtoys': cmd_devtoys,
        'jtree': cmd_jtree,
        'help': cmd_help,
    }

    if cmd not in commands:
        print(f"Comando desconhecido: {cmd}")
        print("Use 'hermes-workbench help' para ver os comandos disponiveis.")
        return 1

    return commands[cmd](args)


def _import_and_run(module_name, wrapper_name, args):
    """Importa modulo e executa funcao wrapper."""
    import importlib
    try:
        mod = importlib.import_module(module_name)
        fn = getattr(mod, wrapper_name, None)
        if fn:
            return fn(args)
        # Fallback to original commands
        return _fallback_command(module_name, args)
    except Exception as e:
        print(f"  ❌ Erro ao carregar {module_name}: {e}")
        return 1


def _fallback_command(module_name, args):
    """Fallback para comandos originais quando wrapper nao existe."""
    if module_name == 's3_headroom':
        if len(sys.argv) > 2:
            return _orig_wrapper(args)
    return 1


def _orig_wrapper(args):
    """Wrapper para comandos originais usando __name__."""
    if not args:
        return 1
    cmd = args[0]
    rest = args[1:]
    
    if cmd == 'panorama':
        from s3_headroom import project_load, project_map
        if not rest:
            print("Uso: panorama <path>")
            return 1
        path = rest[0]
        info = project_load(path)
        print(json.dumps({k: v for k, v in info.items() if k != 'key_files'}, indent=2))
        return 0
    elif cmd == 'compress':
        from s3_headroom import context_compress
        print(context_compress(" ".join(rest)))
        return 0
    elif cmd == 'search':
        from s3_headroom import solution_search
        if len(rest) < 2:
            print("Uso: search <path> <query>")
            return 1
        results = solution_search(rest[0], " ".join(rest[1:]))
        print(json.dumps(results, indent=2))
        return 0
    return 1


# Comandos que ficam inline (nao precisam de import)
def cmd_grep(args):
    if not args:
        print("Uso: hermes-workbench grep <query> [--lang L] [--max N]")
        return 1
    query = args[0]
    print(f"🔍 Buscando '{query}' em 1M+ repos GitHub...")
    print(f"   Use browser_navigate('https://grep.app/search?q={query.replace(' ', '+')}')")
    return 0


def cmd_router(args):
    if not args:
        print("Uso: hermes-workbench router <tarefa>")
        return 1
    from s1_router import classify_task
    result = classify_task(" ".join(args))
    print(f"  Shell:    {result['shell']} ({result['model']})")
    print(f"  Custo:    {result['cost']}")
    print(f"  Motivo:   {result['reason']}")
    print(f"  Scores:   S1={result['score']['S1']}  S2={result['score']['S2']}  S3={result['score']['S3']}")
    return 0


def cmd_status(args):
    import subprocess as sp
    def tl(name):
        r = sp.run(["tasklist", "/FI", f"IMAGENAME eq {name}", "/NH"],
                   capture_output=True, text=True, timeout=10,
                   creationflags=sp.CREATE_NO_WINDOW)
        return name in r.stdout.lower()
    
    print("=" * 40)
    print("📊 WORKBENCH STATUS")
    print("=" * 40)
    print(f"  {'🟢' if tl('ollama.exe') else '🔴'} S1 (Ollama)          $0,00 🆓")
    print(f"  🟢 S2 (DeepSeek)        ~$0.15/M ☁️ (via API)")
    print(f"  🟢 S3 (deepseek-pro)    ~$0.50/M 🧠 (via API)")
    print(f"  {'🟢' if tl('wscript.exe') else '🔴'} Watchdog Guardian     wscript.exe")
    print(f"  {'🟢' if tl('pythonw.exe') else '🔴'} Watchdog (pythonw)    pythonw.exe")
    
    wd = os.path.dirname(os.path.abspath(__file__))
    tools = [("s3_headroom.py","🧠 S3 Headroom"),("s3_grep.py","🔍 S3 Grep"),
             ("s1_router.py","🧭 S1 Router"),("watchdog_hermes.py","⚙️ Watchdog"),
             ("shellz_menu.bat","🖥️ Shellz Menu")]
    print(f"\n  FERRAMENTAS INSTALADAS:")
    for f, n in tools:
        print(f"  {'✅' if os.path.exists(os.path.join(wd,f)) else '❌'} {n:<20} {f}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
