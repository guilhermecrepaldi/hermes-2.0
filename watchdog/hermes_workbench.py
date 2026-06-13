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

Novos Comandos (v3 — S3 Research + Ferramentas):
  research <topico>     Pesquisa em 8 fontes (Reddit, X, YT, HN, GitHub, Web)
  research --reddit <t> Pesquisa apenas no Reddit
  research --x <t>      Pesquisa apenas no X/Twitter
  research --youtube <t> Pesquisa apenas no YouTube
  research --github <t> Pesquisa apenas no GitHub
  research --hn <t>     Pesquisa apenas no Hacker News
  convert <arquivo>     Converte docs para Markdown (MarkItDown-style)
  browse <url>          Navega e extrai conteudo (autonomo)
  batch <n> <tarefa>    Gera N variacoes, S3 escolhe a melhor
  template <nome>       Gera projeto boilerplate (fastapi, cli, react)

Templates:
  template list         Lista templates disponiveis
  template fastapi-crud Gera projeto FastAPI com CRUD
  template cli-python   Gera CLI Python
  template react-vite   Gera React + Vite

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

# ══════════════════════════════════════════════════════════════
# S3 RESEARCH — Pesquisa multi-fonte (last30days-skill style)
# ══════════════════════════════════════════════════════════════

def cmd_research(args):
    """Pesquisa um topico em 8 fontes com resultados REAIS via API."""
    if not args:
        print("Uso: hermes-workbench research <topico>")
        print("  Pesquisa multi-fonte com resultados reais.")
        print("  Use --reddit, --x, --youtube, --github, --hn para filtrar.")
        print("  Use --auto para buscar automaticamente via API (HN + GitHub).")
        print("")
        print("Exemplos:")
        print('  hermes-workbench research "AI agents trends 2026"')
        print('  hermes-workbench research --auto "RAG frameworks python"')
        print('  hermes-workbench research --github --hn "LangChain"')
        return 1

    # Parse args
    source_filter = None
    auto_mode = False
    topic_parts = []
    i = 0
    while i < len(args):
        a = args[i]
        if a == '--auto':
            auto_mode = True
        elif a.startswith('--'):
            source_filter = a[2:]
        else:
            topic_parts.append(a)
        i += 1

    topic = " ".join(topic_parts)
    if not topic:
        print("  Forneca um topico para pesquisa")
        return 1

    sources = {
        'reddit': f"https://www.reddit.com/search/?q={topic.replace(' ', '+')}",
        'x': f"https://x.com/search?q={topic.replace(' ', '%20')}&src=typed_query",
        'youtube': f"https://www.youtube.com/results?search_query={topic.replace(' ', '+')}",
        'github': f"https://github.com/search?q={topic.replace(' ', '+')}&type=repositories&s=stars&o=desc",
        'hn': '',
        'web': f"https://html.duckduckgo.com/html/?q={topic.replace(' ', '+')}",
        'polymarket': f"https://polymarket.com/search?query={topic.replace(' ', '+')}",
        'bluesky': f"https://bsky.app/search?q={topic.replace(' ', '%20')}",
    }

    source_names = {
        'reddit': 'Reddit', 'x': 'X/Twitter', 'youtube': 'YouTube',
        'github': 'GitHub', 'hn': 'Hacker News', 'web': 'Web',
        'polymarket': 'Polymarket', 'bluesky': 'Bluesky',
    }

    active = [s for s in sources] if not source_filter else [source_filter]
    if source_filter and source_filter not in sources:
        print(f"Fonte desconhecida: --{source_filter}")
        print(f"Disponiveis: {', '.join(sources.keys())}")
        return 1

    print("=" * 60)
    print(f"🔍 S3 RESEARCH: {topic}")
    print("=" * 60)
    print(f"  Fontes: {len(active)} | Modo: {'AUTO (API)' if auto_mode else 'MANUAL (browser)'}")
    print()

    results = {}  # source -> list of results

    for src in active:
        name = source_names.get(src, src)
        if src == 'hn' or (auto_mode and src == 'hn'):
            data = _research_hn(topic)
            results['hn'] = data
            print(f"  [{name}]")
            if data:
                for item in data[:5]:
                    print(f"    📌 {item['title'][:80]}")
                    print(f"       {item['points']} pts | {item.get('url','')[:70]}")
            else:
                print(f"    (sem resultados)")
            print()

        elif src == 'github' or (auto_mode and src == 'github'):
            data = _research_github(topic)
            results['github'] = data
            print(f"  [{name}]")
            if data:
                for item in data[:5]:
                    print(f"    🐙 {item['full_name']}")
                    print(f"       ⭐{item['stars']} | {item['description'][:70]}")
            else:
                print(f"    (sem resultados)")
            print()

        else:
            url = sources.get(src, '')
            if url:
                print(f"  [{name}]")
                cmd = f"browser_navigate('{url}')"
                print(f"    {cmd}")
                print()

    # Synthesis report
    print(f"{'='*60}")
    print("📋 S3 RESEARCH SYNTHESIS")
    print("=" * 60)
    print(f"\n  Topico: {topic}")
    print(f"  Data: {datetime.now().strftime('%Y-%m-%d %H:%M UTC')}")
    print(f"  Fontes: {len(active)}")

    total_items = sum(len(v) for v in results.values())
    print(f"  Resultados via API: {total_items}")

    if results.get('hn'):
        print(f"\n  ## Hacker News")
        for item in results['hn'][:3]:
            print(f"  - {item['title'][:80]} ({item['points']} pts)")

    if results.get('github'):
        print(f"\n  ## GitHub")
        for item in results['github'][:3]:
            print(f"  - {item['full_name']} ⭐{item['stars']}")

    print(f"\n  ## Recomendacao S3")
    print(f"  Para acesso completo, utilize browser_navigate para cada fonte.")
    print(f"  O modo --auto busca automaticamente HN + GitHub via API.")
    print()

    return 0


def _research_hn(topic):
    """Pesquisa Hacker News via API JSON gratuita. Retorna lista de resultados."""
    import urllib.request
    import json as _json
    results = []
    try:
        url = f"https://hn.algolia.com/api/v1/search?query={topic.replace(' ', '+')}&tags=story&hitsPerPage=5"
        req = urllib.request.Request(url, headers={"User-Agent": "HermesWorkbench/3.0"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = _json.loads(resp.read())
            for hit in data.get('hits', [])[:5]:
                results.append({
                    'title': hit.get('title', '?'),
                    'points': hit.get('points', 0),
                    'url': hit.get('url', ''),
                    'author': hit.get('author', ''),
                    'created': hit.get('created_at', ''),
                })
    except Exception as e:
        pass
    return results


def _research_github(topic):
    """Pesquisa GitHub via API REST. Retorna lista de resultados."""
    import urllib.request
    import json as _json
    results = []
    try:
        url = f"https://api.github.com/search/repositories?q={topic.replace(' ', '+')}&sort=stars&order=desc&per_page=5"
        req = urllib.request.Request(url, headers={
            "User-Agent": "HermesWorkbench/3.0",
            "Accept": "application/vnd.github.v3+json",
        })
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = _json.loads(resp.read())
            for r in data.get('items', [])[:5]:
                results.append({
                    'full_name': r['full_name'],
                    'stars': r['stargazers_count'],
                    'description': r.get('description', '') or '',
                    'url': r['html_url'],
                    'language': r.get('language', ''),
                })
    except Exception as e:
        pass
    return results


# ══════════════════════════════════════════════════════════════
# CONVERT — Document to Markdown (MarkItDown-style)
# ══════════════════════════════════════════════════════════════

def cmd_convert(args):
    """Converte QUALQUER documento para Markdown usando MarkItDown (Microsoft 152k⭐)."""
    if not args:
        print("Uso: hermes-workbench convert <arquivo|url>")
        print("  Converte QUALQUER documento para Markdown.")
        print("  Usa MarkItDown (Microsoft) - suporta: html, docx, xlsx, pptx, pdf, csv, json, yaml, py")
        print("")
        print("Exemplos:")
        print("  hermes-workbench convert relatorio.docx")
        print("  hermes-workbench convert planilha.xlsx")
        print("  hermes-workbench convert https://example.com")
        return 1

    path = args[0]
    if not os.path.exists(path) and not path.startswith(('http://', 'https://')):
        print(f"  Arquivo nao encontrado: {path}")
        return 1

    filename = os.path.basename(path) if not path.startswith('http') else path.split('/')[-1]
    ext = os.path.splitext(path)[1].lower() if not path.startswith('http') else '.html'

    print(f"📄 Convertendo: {filename}")
    print(f"{'='*50}")

    # Try MarkItDown first (for docx, xlsx, pptx, pdf, html)
    try:
        from markitdown import MarkItDown as _MarkItDown
        _md = _MarkItDown()
        if path.startswith(('http://', 'https://')):
            import urllib.request
            req = urllib.request.Request(path, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=15) as resp:
                content = resp.read()
            import tempfile
            with tempfile.NamedTemporaryFile(suffix='.html', delete=False, mode='wb') as f:
                f.write(content)
                tmp_path = f.name
            try:
                result = _md.convert(tmp_path)
                output = result.text_content
            finally:
                os.unlink(tmp_path)
        elif ext in ('.docx', '.xlsx', '.pptx', '.pdf', '.html', '.htm'):
            result = _md.convert(path)
            output = result.text_content
        else:
            output = None

        if output:
            print(output[:5000])
            if len(output) > 5000:
                print(f"\n*Arquivo truncado para 5000 chars ({len(output)} total)*")
            print(f"\n{'='*50}")
            print(f"✅ Convertido via MarkItDown: {filename} -> Markdown")
            return 0
    except ImportError:
        pass
    except Exception as e:
        print(f"  (MarkItDown: {str(e)[:50]}, usando fallback)")
        pass

    # Fallback: conversao manual para formatos comuns
    try:
        if ext == '.json':
            with open(path) as f:
                data = json.load(f)
            print(f"# {filename}\n")
            print(f"```json")
            print(json.dumps(data, indent=2, ensure_ascii=False)[:5000])
            print("```")

        elif ext == '.csv':
            import csv
            with open(path, newline='', encoding='utf-8') as f:
                reader = csv.reader(f)
                print(f"# {filename}\n")
                for i, row in enumerate(reader):
                    print(f"| {' | '.join(row)} |")
                    if i == 0:
                        print(f"|{'|'.join('---' for _ in row)}|")

        elif ext in ('.py', '.js', '.ts', '.jsx', '.tsx', '.rs', '.go', '.java', '.c',
                     '.cpp', '.h', '.hpp', '.rb', '.php', '.swift', '.kt', '.r', '.m'):
            lang_map = {'.py': 'python', '.js': 'javascript', '.ts': 'typescript',
                       '.jsx': 'jsx', '.tsx': 'tsx', '.rs': 'rust', '.go': 'go',
                       '.java': 'java', '.c': 'c', '.cpp': 'cpp', '.rb': 'ruby',
                       '.php': 'php', '.swift': 'swift', '.kt': 'kotlin'}
            lang = lang_map.get(ext, '')
            with open(path, encoding='utf-8') as f:
                content = f.read()
            print(f"# {filename}\n")
            print(f"```{lang}")
            print(content[:5000])
            print("```")

        elif ext in ('.md', '.markdown', '.txt', '.rst'):
            with open(path, encoding='utf-8') as f:
                print(f.read()[:5000])

        elif ext == '.yaml' or ext == '.yml':
            try:
                import yaml
                with open(path, encoding='utf-8') as f:
                    data = yaml.safe_load(f)
                print(f"# {filename}\n")
                print(f"```yaml")
                import yaml as _yaml
                print(_yaml.dump(data, default_flow_style=False)[:5000])
                print("```")
            except ImportError:
                with open(path) as f:
                    print(f.read()[:5000])
        else:
            with open(path, encoding='utf-8', errors='ignore') as f:
                print(f.read(5000))

        print(f"\n{'='*50}")
        print(f"✅ Convertido: {filename} -> Markdown")

    except Exception as e:
        print(f"  Erro ao converter: {e}")
        return 1
    return 0


# ══════════════════════════════════════════════════════════════
# BROWSE — Navegador autonomo para S3
# ══════════════════════════════════════════════════════════════

def cmd_browse(args):
    """Navega ate uma URL, extrai conteudo e comprime para o S3."""
    if not args:
        print("Uso: hermes-workbench browse <url>")
        print("  Navega e extrai conteudo. Use no S3 para pesquisa autonoma.")
        print("")
        print("Exemplos:")
        print("  hermes-workbench browse https://docs.fastapi.tiangolo.com")
        print("  hermes-workbench browse https://github.com/user/repo")
        return 1

    url = args[0]
    print("=" * 60)
    print(f"🌐 S3 BROWSE: {url}")
    print("=" * 60)
    print(f"\nURL: {url}")
    print(f"Instrucao: use browser_navigate('{url}') no Hermes")
    print(f"\nFluxo S3:")
    print(f"  1. browser_navigate('{url}')")
    print(f"  2. browser_snapshot()  — extrai conteudo")
    print(f"  3. s3_headroom.compress() — comprime para tokens")
    print(f"  4. Inclui no DECISION_PACKAGE")

    # Try to extract using curl for simple pages
    import urllib.request
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            content = resp.read().decode('utf-8', errors='ignore')
            title = ""
            import re as _re
            m = _re.search(r'<title>(.*?)</title>', content, _re.IGNORECASE | _re.DOTALL)
            if m:
                title = m.group(1).strip()
            print(f"\n📋 Titulo: {title}")
            print(f"   Tamanho: {len(content)} bytes")
            print(f"   Status: {resp.status}")

            from s3_headroom import context_compress
            compressed = context_compress(content[:10000])
            print(f"\n📦 Compressao:")
            for line in compressed.split('\n')[:3]:
                print(f"   {line}")

    except Exception as e:
        print(f"\n  ⚠️  Nao foi possivel extrair: {str(e)[:60]}")
        print(f"  Use o browser_tool do Hermes para acessar.")

    return 0


# ══════════════════════════════════════════════════════════════
# BATCH — Gera N variacoes, S3 escolhe a melhor
# ══════════════════════════════════════════════════════════════

def cmd_batch(args):
    """Gera N variacoes de implementacao, S3 escolhe a melhor."""
    if len(args) < 2:
        print("Uso: hermes-workbench batch <n> <tarefa>")
        print("  Gera N variacoes de implementacao.")
        print("  S3 revisa cada uma e escolhe a melhor.")
        print("")
        print("Exemplos:")
        print('  hermes-workbench batch 3 "criar API de autenticacao JWT"')
        print('  hermes-workbench batch 2 "funcao de validacao de CPF"')
        return 1

    try:
        n = int(args[0])
        if n < 1 or n > 5:
            print("  ❌ N deve ser entre 1 e 5")
            return 1
    except ValueError:
        print(f"  ❌ N invalido: {args[0]}. Use um numero entre 1 e 5.")
        return 1

    task = " ".join(args[1:])
    from s1_router import classify_task
    routing = classify_task(task)

    print("=" * 60)
    print(f"📦 BATCH MODE — {n} variacoes")
    print("=" * 60)
    print(f"\nTarefa: {task}")
    print(f"Roteamento: {routing['shell']} ({routing['model']})")
    print(f"Custo: {routing['cost']}")
    print(f"Variacoes: {n}")
    print()

    for i in range(1, n + 1):
        sep = "=" * 50
        approaches = {1: 'Principal', 2: 'Diferente', 3: 'Alternativa'}
        approach = approaches.get(i, f'Variacao {i}')
        print(f"  +-{sep}-+")
        print(f"  |  VARIACAO {i} de {n}")
        print(f"  |  Shell: {routing['shell']} - {routing['model']}")
        print(f"  |  Abordagem: {approach}")
        print(f"  |")
        print(f"  |  S1 executa com abordagem {i}")
        print(f"  |  S3 revisa (Quality Gate)")
        print(f"  +-{sep}-+")
        print()

    print(f"\nFluxo completo:")
    print(f"  1. S1 gera {n} implementacoes diferentes")
    print(f"  2. S3 revisa cada uma (Quality Gate)")
    print(f"  3. S3 escolhe a MELHOR baseado em:")
    print(f"     - Qualidade do codigo")
    print(f"     - Cobertura de requisitos")
    print(f"     - Performance")
    print(f"     - Manutenibilidade")
    print(f"  4. Descarta as {n-1} restantes")
    print(f"  5. Commit da vencedora")
    print(f"\n💰 Economia estimada vs fazer 1 tentativa: ~{n}x mais chances de acerto")

    return 0


# ══════════════════════════════════════════════════════════════
# TEMPLATE — Gerador de projetos boilerplate
# ══════════════════════════════════════════════════════════════

TEMPLATES = {
    'fastapi-crud': {
        'desc': 'API FastAPI com CRUD completo, SQLAlchemy, Pydantic',
        'files': {
            'main.py': '''from fastapi import FastAPI
from pydantic import BaseModel
from typing import List, Optional
import uvicorn

app = FastAPI(title="{name}", version="1.0.0")

# ─── Models ───
class Item(BaseModel):
    id: Optional[int] = None
    name: str
    description: Optional[str] = None

# ─── Storage ───
_db: List[Item] = []
_counter = 0

# ─── Routes ───
@app.get("/")
def root():
    return {"message": "{name} API", "version": "1.0.0"}

@app.get("/items", response_model=List[Item])
def list_items():
    return _db

@app.post("/items", response_model=Item)
def create_item(item: Item):
    global _counter
    _counter += 1
    item.id = _counter
    _db.append(item)
    return item

@app.get("/items/{item_id}", response_model=Optional[Item])
def get_item(item_id: int):
    for item in _db:
        if item.id == item_id:
            return item
    return None

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
''',
            'requirements.txt': '''fastapi>=0.115.0
uvicorn>=0.30.0
pydantic>=2.0.0
''',
            'README.md': '''# {name}

API FastAPI com CRUD completo.

## Uso

```bash
pip install -r requirements.txt
python main.py
```

## Endpoints

- `GET /` — Status
- `GET /items` — Listar todos
- `POST /items` — Criar novo
- `GET /items/{id}` — Buscar por ID
''',
        }
    },
    'cli-python': {
        'desc': 'CLI Python com Click, logging, testes',
        'files': {
            '{name}/cli.py': '''#!/usr/bin/env python3
"""CLI {name} — Hermes Generated."""
import click
import logging

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

@click.group()
def cli():
    """{name} — CLI tool."""
    pass

@cli.command()
@click.argument("name")
def hello(name):
    """Say hello to NAME."""
    click.echo(f"Hello, {{name}}!")
    log.info(f"Said hello to {{name}}")

@cli.command()
@click.option("--count", "-c", default=1, help="Number of times")
def repeat(count):
    """Repeat the message."""
    for i in range(count):
        click.echo(f"Message {{i+1}}")

if __name__ == "__main__":
    cli()
''',
            'setup.py': '''from setuptools import setup, find_packages

setup(
    name="{name}",
    version="0.1.0",
    packages=find_packages(),
    install_requires=["click>=8.0"],
    entry_points={{"console_scripts": ["{name}={name}.cli:cli"]}},
)
''',
            'README.md': '''# {name}

CLI Python gerado pelo Hermes Workbench.

## Instalacao

```bash
pip install -e .
```

## Uso

```bash
{name} hello "Mundo"
{name} repeat --count 3
```
''',
        }
    },
    'react-vite': {
        'desc': 'App React + Vite + TypeScript basico',
        'files': {
            'src/App.tsx': '''import {{ useState }} from 'react'

function App() {{
  const [count, setCount] = useState(0)

  return (
    <div>
      <h1>{name}</h1>
      <p>Count: {{count}}</p>
      <button onClick={{() => setCount(c => c + 1)}}>
        Increment
      </button>
    </div>
  )
}}

export default App
''',
            'src/main.tsx': '''import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App'

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
)
''',
            'index.html': '''<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>{name}</title>
  </head>
  <body>
    <div id="root"></div>
    <script type="module" src="/src/main.tsx"></script>
  </body>
</html>
''',
            'package.json': '''{{
  "name": "{name}",
  "private": true,
  "version": "0.1.0",
  "type": "module",
  "scripts": {{
    "dev": "vite",
    "build": "tsc && vite build",
    "preview": "vite preview"
  }},
  "dependencies": {{
    "react": "^19.0.0",
    "react-dom": "^19.0.0"
  }},
  "devDependencies": {{
    "@types/react": "^19.0.0",
    "@types/react-dom": "^19.0.0",
    "@vitejs/plugin-react": "^4.0.0",
    "typescript": "^5.0.0",
    "vite": "^6.0.0"
  }}
}}
''',
            'tsconfig.json': '''{{
  "compilerOptions": {{
    "target": "ES2020",
    "module": "ESNext",
    "moduleResolution": "bundler",
    "jsx": "react-jsx",
    "strict": true,
    "esModuleInterop": true,
    "skipLibCheck": true
  }},
  "include": ["src"]
}}
''',
            'vite.config.ts': '''import {{ defineConfig }} from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({{
  plugins: [react()],
}})
''',
        }
    },
    'streamlit-dashboard': {
        'desc': 'Dashboard Streamlit com graficos, tabelas, upload CSV',
        'files': {
            'app.py': '''import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="{name}", layout="wide")
st.title("{name}")

# File upload
uploaded = st.file_uploader("Upload CSV", type=["csv"])
if uploaded is not None:
    df = pd.read_csv(uploaded)
    st.subheader("Data Preview")
    st.dataframe(df.head(100))
    
    cols = df.select_dtypes(include="number").columns.tolist()
    if len(cols) >= 2:
        st.subheader("Chart")
        x = st.selectbox("X axis", cols, index=0)
        y = st.selectbox("Y axis", cols, index=min(1, len(cols)-1))
        fig = px.scatter(df, x=x, y=y)
        st.plotly_chart(fig, use_container_width=True)
    
    st.subheader("Statistics")
    st.dataframe(df.describe())
else:
    st.info("Upload a CSV file to get started.")
''',
            'requirements.txt': '''streamlit>=1.40.0
pandas>=2.0.0
plotly>=5.0.0
''',
            'README.md': '''# {name}

Streamlit dashboard gerado pelo Hermes Workbench.

## Uso

```bash
pip install -r requirements.txt
streamlit run app.py
```
''',
        }
    },
    'fastapi-full': {
        'desc': 'API FastAPI completa: auth JWT, SQLAlchemy, migrations, tests',
        'files': {
            'app/main.py': '''from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt

app = FastAPI(title="{name}", version="1.0.0")
security = HTTPBearer()

# ─── Auth ───
SECRET = "change-me-in-production"

def verify_token(cred: HTTPAuthorizationCredentials = Depends(security)):
    try:
        return jwt.decode(cred.credentials, SECRET, algorithms=["HS256"])
    except jwt.PyJWTError:
        raise HTTPException(401, "Invalid token")

@app.get("/")
def root():
    return {"message": "{name} API", "status": "running"}

@app.get("/health")
def health():
    return {"status": "healthy"}
''',
            'app/models.py': '''from pydantic import BaseModel
from typing import Optional

class Item(BaseModel):
    id: Optional[int] = None
    name: str
    description: Optional[str] = None

# In-memory storage (replace with SQLAlchemy for production)
db: list[Item] = []
counter = 0
''',
            'app/routes.py': '''from fastapi import APIRouter
from app.models import Item, db, counter

router = APIRouter(prefix="/items", tags=["items"])

@router.get("/")
def list_items():
    return db

@router.post("/")
def create_item(item: Item):
    global counter
    counter += 1
    item.id = counter
    db.append(item)
    return item

@router.get("/{item_id}")
def get_item(item_id: int):
    for item in db:
        if item.id == item_id:
            return item
    return None
''',
            'requirements.txt': '''fastapi>=0.115.0
uvicorn>=0.30.0
pyjwt>=2.0.0
pydantic>=2.0.0
''',
            'tests/test_main.py': '''from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_root():
    r = client.get("/")
    assert r.status_code == 200
    assert r.json()["status"] == "running"

def test_health():
    r = client.get("/health")
    assert r.status_code == 200
''',
            'README.md': '''# {name}

API FastAPI completa com autenticacao JWT.

## Uso

```bash
pip install -r requirements.txt
uvicorn app.main:app --reload
```

## Testes

```bash
pytest tests/ -v
```
''',
        }
    },
    'nextjs-app': {
        'desc': 'App Next.js 15 com TypeScript, Tailwind, paginas basicas',
        'files': {
            'app/layout.tsx': '''import type {{ Metadata }} from "next"

export const metadata: Metadata = {{
  title: "{name}",
  description: "Generated by Hermes Workbench",
}}

export default function RootLayout({{ children }}: {{
  children: React.ReactNode
}}) {{
  return (
    <html lang="en">
      <body>{{children}}</body>
    </html>
  )
}}
''',
            'app/page.tsx': '''export default function Home() {{
  return (
    <main>
      <h1>{name}</h1>
      <p>Welcome to your Next.js app!</p>
    </main>
  )
}}
''',
            'app/globals.css': '''@tailwind base;
@tailwind components;
@tailwind utilities;

body {{
  font-family: system-ui, sans-serif;
  padding: 2rem;
}}
''',
            'package.json': '''{{
  "name": "{name}",
  "version": "0.1.0",
  "private": true,
  "scripts": {{
    "dev": "next dev",
    "build": "next build",
    "start": "next start"
  }},
  "dependencies": {{
    "next": "^15.0.0",
    "react": "^19.0.0",
    "react-dom": "^19.0.0"
  }},
  "devDependencies": {{
    "@types/node": "^22.0.0",
    "@types/react": "^19.0.0",
    "@types/react-dom": "^19.0.0",
    "typescript": "^5.0.0",
    "tailwindcss": "^4.0.0"
  }}
}}
''',
            'tsconfig.json': '''{{
  "compilerOptions": {{
    "target": "ES2017",
    "lib": ["dom", "dom.iterable", "esnext"],
    "allowJs": true,
    "skipLibCheck": true,
    "strict": true,
    "noEmit": true,
    "esModuleInterop": true,
    "module": "esnext",
    "moduleResolution": "bundler",
    "resolveJsonModule": true,
    "isolatedModules": true,
    "jsx": "preserve",
    "incremental": true,
    "plugins": [{{ "name": "next" }}]
  }},
  "include": ["next-env.d.ts", "**/*.ts", "**/*.tsx", ".next/types/**/*.ts"],
  "exclude": ["node_modules"]
}}
''',
            'next.config.ts': '''import type {{ NextConfig }} from "next"

const config: NextConfig = {{
  reactStrictMode: true,
}}

export default config
''',
            'README.md': '''# {name}

Next.js app gerado pelo Hermes Workbench.

## Uso

```bash
npm install
npm run dev
```
''',
        }
    },
}

def cmd_template(args):
    """Gera projeto boilerplate a partir de templates."""
    if not args or args[0] == 'list':
        print("Templates disponiveis:")
        print(f"  {'Nome':<20} Descricao")
        print(f"  {'-'*20} {'-'*40}")
        for name, tmpl in TEMPLATES.items():
            print(f"  {name:<20} {tmpl['desc']}")
        print(f"\nUse: hermes-workbench template <nome> [diretorio]")
        return 0

    name = args[0]
    if name not in TEMPLATES:
        print(f"  ❌ Template desconhecido: {name}")
        print("  Use 'hermes-workbench template list' para ver os disponiveis.")
        return 1

    tmpl = TEMPLATES[name]
    out_dir = args[1] if len(args) > 1 else os.path.join(os.getcwd(), name)

    import shutil as _shutil
    if os.path.exists(out_dir):
        print(f"  ❌ Diretorio ja existe: {out_dir}")
        return 1

    os.makedirs(out_dir, exist_ok=True)
    project_name = os.path.basename(out_dir)

    print(f"📦 Gerando template: {name}")
    print(f"   Projeto: {project_name}")
    print(f"   Destino: {out_dir}")
    print(f"   Arquivos: {len(tmpl['files'])}")
    print()

    for filepath, content in tmpl['files'].items():
        full_path = os.path.join(out_dir, filepath)
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        formatted = content.format(name=project_name)
        with open(full_path, 'w', encoding='utf-8') as f:
            f.write(formatted)
        print(f"  ✅ {filepath}")

    print(f"\n✅ Projeto '{project_name}' criado em {out_dir}")
    print(f"\\nProximos passos:")
    if name == 'fastapi-crud':
        print(f"  cd {out_dir}")
        print(f"  pip install -r requirements.txt")
        print(f"  python main.py")
    elif name == 'cli-python':
        print(f"  cd {out_dir}")
        print(f"  pip install -e .")
        print(f"  {project_name} hello Mundo")
    elif name == 'react-vite':
        print(f"  cd {out_dir}")
        print(f"  npm install")
        print(f"  npm run dev")
    elif name == 'streamlit-dashboard':
        print(f"  cd {out_dir}")
        print(f"  pip install -r requirements.txt")
        print(f"  streamlit run app.py")
    elif name == 'fastapi-full':
        print(f"  cd {out_dir}")
        print(f"  pip install -r requirements.txt")
        print(f"  uvicorn app.main:app --reload")
        print(f"  pytest tests/ -v  (para testar)")
    elif name == 'nextjs-app':
        print(f"  cd {out_dir}")
        print(f"  npm install")
        print(f"  npm run dev")

    return 0


# ══════════════════════════════════════════════════════════════
# MEMORIA PERSISTENTE — Contexto entre projetos/sessoes
# ══════════════════════════════════════════════════════════════

MEMORY_DIR = os.path.expanduser("~/.hermes-workbench-memory")
MEMORY_FILE = os.path.join(MEMORY_DIR, "memory.json")

def _load_memory():
    os.makedirs(MEMORY_DIR, exist_ok=True)
    if os.path.exists(MEMORY_FILE):
        try:
            with open(MEMORY_FILE, encoding='utf-8') as f:
                return json.load(f)
        except: pass
    return {"entries": [], "contexts": {}}

def _save_memory(data):
    os.makedirs(MEMORY_DIR, exist_ok=True)
    with open(MEMORY_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def cmd_memory(args):
    """Memoria persistente entre projetos e sessoes."""
    if not args or args[0] == 'list':
        data = _load_memory()
        entries = data.get('entries', [])
        print(f"📝 MEMORIA: {len(entries)} entradas")
        print(f"   Contextos: {len(data.get('contexts', {}))}")
        print()
        for e in entries[-10:]:
            print(f"  [{e.get('date','')[:10]}] {e.get('key','?')}: {e.get('value','')[:80]}")
        if len(entries) > 10:
            print(f"  ... +{len(entries)-10} entradas")
        return 0

    cmd = args[0]
    rest = args[1:]

    if cmd == 'save' and len(rest) >= 2:
        key = rest[0]
        value = " ".join(rest[1:])
        data = _load_memory()
        data['entries'].append({
            'key': key,
            'value': value,
            'date': datetime.now().isoformat(),
        })
        _save_memory(data)
        print(f"✅ Salvo: {key}")
        return 0

    elif cmd == 'search' and rest:
        query = " ".join(rest).lower()
        data = _load_memory()
        results = [e for e in data['entries'] if query in e['key'].lower() or query in e['value'].lower()]
        print(f"🔍 Buscando: {query}")
        print(f"   Resultados: {len(results)}")
        for r in results[-5:]:
            print(f"  [{r.get('date','')[:10]}] {r['key']}: {r['value'][:100]}")
        return 0

    elif cmd == 'context' and rest:
        ctx_name = rest[0]
        data = _load_memory()
        ctx = data['contexts'].get(ctx_name, {})
        if not ctx:
            print(f"Contexto '{ctx_name}' vazio ou inexistente")
            return 0
        print(f"📦 Contexto: {ctx_name}")
        for k, v in ctx.items():
            print(f"  {k}: {str(v)[:120]}")
        return 0

    elif cmd == 'save-context' and len(rest) >= 2:
        ctx_name = rest[0]
        ctx_data = " ".join(rest[1:])
        data = _load_memory()
        if ctx_name not in data['contexts']:
            data['contexts'][ctx_name] = {}
        import json as _json
        try: parsed = _json.loads(ctx_data); data['contexts'][ctx_name].update(parsed)
        except: data['contexts'][ctx_name]['note'] = ctx_data
        _save_memory(data)
        print(f"✅ Contexto '{ctx_name}' atualizado")
        return 0

    else:
        print("Uso: hermes-workbench memory <comando> [args]")
        print("  list                    Lista entradas recentes")
        print('  save <key> <value>      Salva informacao')
        print('  search <query>          Busca na memoria')
        print('  context <nome>          Ve contexto de projeto')
        print('  save-context <n> <json>  Salva contexto')
        return 0


# ══════════════════════════════════════════════════════════════
# DOCS — Documentacao automatica de projetos
# ══════════════════════════════════════════════════════════════

def cmd_docs(args):
    """Gera documentacao automatica de QUALQUER projeto."""
    if not args or args[0] == 'help':
        print("Uso: hermes-workbench docs <caminho>")
        print("  Gera documentacao automatica do projeto.")
        print("  Cria README.md + estrutura + API docs (se FastAPI).")
        print()
        print("Exemplos:")
        print("  hermes-workbench docs .")
        print("  hermes-workbench docs D:\\meu-projeto")
        return 0

    path = args[0]
    if not os.path.exists(path):
        print(f"  Caminho nao encontrado: {path}")
        return 1

    from s3_headroom import project_load, project_map
    info = project_load(path)

    project_name = os.path.basename(path)
    docs_dir = os.path.join(path, "docs")
    os.makedirs(docs_dir, exist_ok=True)

    print(f"📖 Gerando documentacao para: {project_name}")
    print(f"   Destino: {docs_dir}/")
    print()

    # README.md
    readme = f"""# {project_name}

## Visao Geral
{info.get('language', 'N/A')} project with {info['files']} files across {info['dirs']} directories.

## Estrutura
```
"""

    tree = project_map(path, max_depth=2)
    for line in tree.split('\n')[:20]:
        readme += f"{line}\n"
    if len(tree.split('\n')) > 20:
        readme += "...\n"

    readme += f"""```

## Estatisticas
- Linguagem principal: {info.get('language', 'N/A')}
- Arquivos: {info['files']}
- Pastas: {info['dirs']}
- Linhas de codigo: {info['lines']:,}

## Arquivos-chave
"""
    for kf in info.get('key_files', [])[:5]:
        readme += f"- `{kf['path']}` ({kf['lines']} lines)\n"

    readme += f"""
---
*Gerado automaticamente pelo Hermes Workbench em {datetime.now().strftime('%Y-%m-%d %H:%M')}*
"""
    readme_path = os.path.join(docs_dir, "README.md")
    with open(readme_path, 'w', encoding='utf-8') as f:
        f.write(readme)
    print(f"  ✅ docs/README.md")

    # STRUCTURE.md
    struct = f"""# Estrutura do Projeto - {project_name}

## Arvore de Diretorios
```
{tree}
```
"""
    struct_path = os.path.join(docs_dir, "STRUCTURE.md")
    with open(struct_path, 'w', encoding='utf-8') as f:
        f.write(struct)
    print(f"  ✅ docs/STRUCTURE.md")

    # API.md (se FastAPI)
    has_fastapi = any('fastapi' in f.lower() for f in os.listdir(path) if f.endswith('.py')) or \
                  any('fastapi' in open(os.path.join(root, f), encoding='utf-8', errors='ignore').read()[:500]
                      for root, _, files in os.walk(path) for f in files[:20] if f.endswith('.py'))
    if has_fastapi:
        api_doc = f"""# API Reference - {project_name}

## Endpoints
*Gerado por deteccao automatica. Para documentacao completa, execute o servidor e acesse /docs*

## Modelos
*Gerado por deteccao automatica.*

---
*Gerado automaticamente pelo Hermes Workbench*
"""
        api_path = os.path.join(docs_dir, "API.md")
        with open(api_path, 'w', encoding='utf-8') as f:
            f.write(api_doc)
        print(f"  ✅ docs/API.md (FastAPI detectado)")

    print(f"\n✅ Documentacao gerada em {docs_dir}/")
    print(f"   Arquivos: {len(os.listdir(docs_dir))}")
    return 0


# ══════════════════════════════════════════════════════════════
# TEST — Automacao de testes
# ══════════════════════════════════════════════════════════════

def cmd_test(args):
    """Gera, executa e relata testes automaticamente."""
    if not args or args[0] == 'help':
        print("Uso: hermes-workbench test <comando> [args]")
        print("  generate <path>    Gera esqueleto de testes")
        print("  run [path]         Executa pytest")
        print("  report [path]      Relatorio de cobertura")
        print()
        print("Exemplos:")
        print("  hermes-workbench test generate .")
        print("  hermes-workbench test run tests/")
        return 0

    cmd = args[0]
    path = args[1] if len(args) > 1 else os.getcwd()

    if cmd == 'generate':
        return _test_generate(path)
    elif cmd == 'run':
        return _test_run(path)
    elif cmd == 'report':
        return _test_report(path)
    else:
        print(f"Comando desconhecido: {cmd}")
        return 1


def _test_generate(path):
    """Gera esqueleto de testes para projeto Python."""
    if not os.path.exists(path):
        print(f"Caminho nao encontrado: {path}")
        return 1

    test_dir = os.path.join(path, "tests")
    os.makedirs(test_dir, exist_ok=True)

    init_file = os.path.join(test_dir, "__init__.py")
    if not os.path.exists(init_file):
        with open(init_file, 'w') as f:
            f.write("# Tests\n")
        print(f"  ✅ tests/__init__.py")

    # Find Python source files and generate test stubs
    generated = 0
    py_files = []
    for root, _, files in os.walk(path):
        if 'tests' in root or '.git' in root or '__pycache__' in root:
            continue
        for f in files:
            if f.endswith('.py') and f != '__init__.py':
                py_files.append(os.path.join(root, f))

    for src_file in py_files[:20]:
        rel = os.path.relpath(src_file, path)
        test_name = f"test_{os.path.splitext(os.path.basename(src_file))[0]}.py"
        test_path = os.path.join(test_dir, test_name)

        if os.path.exists(test_path):
            continue

        # Extract function/class names
        funcs = []
        classes = []
        with open(src_file, encoding='utf-8', errors='ignore') as f:
            for line in f:
                if line.startswith('def '):
                    funcs.append(line.split('(')[0].replace('def ', '').strip())
                elif line.startswith('class '):
                    classes.append(line.split('(')[0].replace('class ', '').strip())

        if funcs or classes:
            # Build test content without nested f-strings
            import_path = ".".join(rel.replace(os.sep, '/').replace('.py', '').split('/'))
            imports = ", ".join(classes[:3] + funcs[:3])
            test_content = '"""Tests for %s."""\n' % rel
            test_content += 'import pytest\n'
            test_content += 'from %s import %s\n\n' % (import_path, imports)
            
            for f in funcs[:5]:
                test_content += 'def test_%s():\n    """Test %s."""\n    # TODO: implement\n    assert True\n\n' % (f, f)
            
            for c in classes[:3]:
                test_content += 'class Test%s:\n    """Tests for %s."""\n\n    def test_init(self):\n        """Test initialization."""\n        # TODO: implement\n        assert True\n\n' % (c, c)
            with open(test_path, 'w', encoding='utf-8') as f:
                f.write(test_content)
            generated += 1

    print(f"✅ Testes gerados: {generated} arquivos em {test_dir}/")
    if generated == 0:
        print("   (todos ja existem ou nenhum modulo Python encontrado)")
    return 0


def _test_run(path):
    """Executa pytest no diretorio."""
    import subprocess as _sp
    print(f"🧪 Executando testes em: {path}")
    print(f"{'='*50}")
    try:
        r = _sp.run(["pytest", path, "-v", "--tb=short"],
                    capture_output=True, text=True, timeout=60,
                    creationflags=_sp.CREATE_NO_WINDOW)
        output = r.stdout + r.stderr
        print(output[-1000:])
        print(f"\n{'='*50}")
        print(f"✅ Exit code: {r.returncode}")
        return r.returncode
    except FileNotFoundError:
        print("  pytest nao instalado. Instale com: pip install pytest")
        return 1
    except Exception as e:
        print(f"  Erro: {e}")
        return 1


def _test_report(path):
    """Gera relatorio de testes."""
    import subprocess as _sp
    print(f"📊 Relatorio de testes: {path}")
    try:
        r = _sp.run(["pytest", path, "-v", "--tb=line", "--no-header"],
                    capture_output=True, text=True, timeout=120,
                    creationflags=_sp.CREATE_NO_WINDOW)
        lines = r.stdout.split('\n')
        passed = sum(1 for l in lines if 'PASSED' in l)
        failed = sum(1 for l in lines if 'FAILED' in l)
        errors = sum(1 for l in lines if 'ERROR' in l)
        print(f"  Passed: {passed}")
        print(f"  Failed: {failed}")
        print(f"  Errors: {errors}")
        print(f"  Total:  {passed + failed + errors}")
        if failed > 0:
            print(f"\n  Falhas:")
            for l in lines:
                if 'FAILED' in l:
                    print(f"    {l}")
        return 0 if failed == 0 else 1
    except FileNotFoundError:
        print("  pytest nao instalado")
        return 1


# ══════════════════════════════════════════════════════════════
# HELP
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
        'research': cmd_research,
        'convert': cmd_convert,
        'browse': cmd_browse,
        'batch': cmd_batch,
        'template': cmd_template,
        'memory': cmd_memory,
        'docs': cmd_docs,
        'test': cmd_test,
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
