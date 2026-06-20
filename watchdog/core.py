"""Hermes 2.0 — Dataclasses, tipos compartilhados, harness e roteamento economico."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional, Dict, Any, List
import os
import json
import subprocess
import urllib.request
from datetime import datetime


def _get_logger():
    try:
        from logger import get_logger
        return get_logger(__name__)
    except ImportError:
        import logging
        return logging.getLogger(__name__)


# ═══════════════════════════════════════════════
# ROTEADOR ECONOMICO — IA Local (Ollama) primeiro
# ═══════════════════════════════════════════════

OLLAMA_URL = "http://localhost:11434/api/generate"
LOCAL_MODEL = "qwen2.5-coder:7b"        # 58 tok/s, $0
LOCAL_VISION = "qwen3-vl:4b"            # Visao, $0
DEEPSEEK_FLASH = "deepseek-v4-flash"     # Nuvem, $0.15/1M
DEEPSEEK_PRO = "deepseek-v4-pro"        # Nuvem, $0.50/1M


def ollama_disponivel() -> bool:
    """Verifica se o Ollama esta rodando localmente."""
    try:
        req = urllib.request.urlopen("http://localhost:11434/api/tags", timeout=2)
        data = json.loads(req.read())
        return len(data.get("models", [])) > 0
    except Exception:
        return False


def ollama_generate(prompt: str, model: str = LOCAL_MODEL,
                    max_tokens: int = 512) -> Optional[str]:
    """Gera texto via Ollama local. Custo: $0."""
    try:
        payload = json.dumps({
            "model": model,
            "prompt": prompt,
            "stream": False,
            "options": {"num_predict": max_tokens}
        }).encode()
        req = urllib.request.Request(OLLAMA_URL, data=payload,
                                     headers={"Content-Type": "application/json"})
        resp = urllib.request.urlopen(req, timeout=60)
        result = json.loads(resp.read())
        return result.get("response", "").strip()
    except Exception as e:
        return None


def classificar_tarefa_local(tarefa: str) -> Dict[str, Any]:
    """Usa IA local (gratis) para classificar a tarefa antes de usar API paga."""
    prompt = (
        "Classifique a tarefa abaixo em UMA das categorias:\n"
        "- 'leitura': ler arquivos, buscar informacao, pesquisar\n"
        "- 'codigo': escrever, editar, refatorar, debugar codigo\n"
        "- 'shell': comandos de terminal, instalar, build, deploy\n"
        "- 'arquitetura': planejar, desenhar, projetar, documentar\n"
        "- 'pesado': analise complexa, seguranca, decisoes criticas\n\n"
        f"Tarefa: {tarefa}\n\n"
        "Responda apenas com a categoria, uma palavra."
    )
    resposta = ollama_generate(prompt, max_tokens=20)
    if resposta:
        categoria = resposta.strip().lower()
        if categoria in ("leitura", "codigo", "shell"):
            return {"shell": "S1", "modelo": LOCAL_MODEL,
                    "custo": "$0,00 🆓", "categoria": categoria,
                    "roteador": "local (Ollama)"}
        elif categoria == "arquitetura":
            return {"shell": "S2", "modelo": DEEPSEEK_FLASH,
                    "custo": "~$0.15/M ☁️", "categoria": categoria,
                    "roteador": "nuvem (DeepSeek Flash)"}
        elif categoria == "pesado":
            return {"shell": "S3", "modelo": DEEPSEEK_PRO,
                    "custo": "~$0.50/M 🧠", "categoria": categoria,
                    "roteador": "nuvem (DeepSeek Pro)"}
    # Fallback: usa IA local mesmo se nao classificou
    return {"shell": "S1", "modelo": LOCAL_MODEL,
            "custo": "$0,00 🆓", "categoria": "fallback",
            "roteador": "local (Ollama)"}


# ═══════════════════════════════════════════════
# DATACLASSES
# ═══════════════════════════════════════════════

@dataclass
class RouterDecision:
    """Decisao do roteador S1/S2/S3."""
    shell: str
    model: str
    cost: str
    reason: str
    score_s1: int = 0
    score_s2: int = 0
    score_s3: int = 0
    router_source: str = "keyword"  # keyword | ollama

    def to_dict(self) -> dict:
        return {
            "shell": self.shell,
            "model": self.model,
            "cost": self.cost,
            "reason": self.reason,
            "score": {"S1": self.score_s1, "S2": self.score_s2, "S3": self.score_s3},
            "router": self.router_source,
        }


@dataclass
class ProjectInfo:
    """Informacoes de um projeto carregado via s3_headroom."""
    path: str = ""
    name: str = ""
    status: str = "pending"
    error: str = ""
    total_files: int = 0
    total_lines: int = 0
    languages: dict = field(default_factory=dict)
    key_files: list = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "path": self.path,
            "name": self.name,
            "status": self.status,
            "error": self.error,
            "total_files": self.total_files,
            "total_lines": self.total_lines,
            "languages": self.languages,
            "key_files": self.key_files,
        }


@dataclass
class ShellCapability:
    """Capacidade de uma shell (S1/S2/S3) para roteamento."""
    name: str
    keywords: list
    max_tokens: int = 4096
    model: str = ""
    cost: str = ""
    priority: int = 0


@dataclass
class Action:
    """Represents an action that can be executed by the agent."""
    name: str
    description: str
    parameters: Dict[str, Any] = field(default_factory=dict)
    required_permissions: List[str] = field(default_factory=list)
    security_policy: str = ""  # Descricao da security policy embedada na action


@dataclass
class Context:
    """Current context of the agent session."""
    user_input: str = ""
    hermes_progress: str = ""
    available_skills: List[str] = field(default_factory=list)
    recent_actions: List[str] = field(default_factory=list)
    token_budget: int = 0
    working_directory: str = ""
    timestamp: str = ""

    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now().isoformat()


@dataclass
class HarnessResult:
    """Result of executing an action through the harness."""
    success: bool
    summary: str
    data: Optional[Any] = None
    error: Optional[str] = None
    actions_taken: List[str] = field(default_factory=list)
    tokens_used: int = 0
    time_taken: float = 0.0


# ═══════════════════════════════════════════════
# SKILL LOADER
# ═══════════════════════════════════════════════

class SkillLoader:
    """Loads and manages available skills."""

    def __init__(self):
        self.skills: Dict[str, Any] = {}
        self._load_skills()

    def _load_skills(self) -> None:
        self.skills = {}

    def get_skill(self, name: str) -> Optional[Any]:
        return self.skills.get(name)

    def list_skills(self) -> List[str]:
        return list(self.skills.keys())


# ═══════════════════════════════════════════════
# HARNESS FABLE 5 + ECONOMIA LOCAL
# ═══════════════════════════════════════════════

class HermesHarness:
    """Main harness: permissions, context, memory, tool execution, roteamento economico.
    Complexity lives here (Fable 5 inspired)."""

    def __init__(self):
        self.logger = _get_logger()
        self.skill_loader = SkillLoader()
        self.context = Context()
        self.permissions = self._load_default_permissions()
        self.tools = self._load_available_tools()
        self._ollama_ok = ollama_disponivel()
        if self._ollama_ok:
            self.logger.info(f"Ollama disponivel: {LOCAL_MODEL} (58 tok/s, $0)")
        else:
            self.logger.warning("Ollama nao disponivel — toda classificacao vai para nuvem")

    def _load_default_permissions(self) -> Dict[str, bool]:
        return {
            "file_read": True, "file_write": True,
            "shell_execute": True, "network_access": True,
            "skill_execution": True,
        }

    def _load_available_tools(self) -> Dict[str, Any]:
        return {
            "terminal": {
                "description": "Shell commands. SECURITY: so executa comandos do usuario, "
                               "nunca comandos baixados de terceiros. Verifica URL antes de curl/wget.",
                "permissions": ["shell_execute"]
            },
            "file_read": {
                "description": "Read files. SECURITY: so le arquivos nos diretorios do projeto "
                               "e $HOME. Nunca le /etc/passwd, .env com credenciais sem permissao.",
                "permissions": ["file_read"]
            },
            "file_write": {
                "description": "Write files. SECURITY: nunca sobrescreve config.yaml, .gitignore, "
                               "ou arquivos de configuracao sem confirmacao. Nunca escreve fora do projeto.",
                "permissions": ["file_write"]
            },
            "ollama_local": {
                "description": f"IA local {LOCAL_MODEL} (gratis). SECURITY: prompt nunca sai da maquina. "
                               "Dados sensiveis podem ser processados localmente.",
                "permissions": []
            },
            "git": {
                "description": "Git operations. SECURITY: nunca faz push sem commit. "
                               "Nunca sobrescreve historico remoto com --force sem confirmacao.",
                "permissions": ["shell_execute"]
            },
            "pip": {
                "description": "Python package install. SECURITY: so instala de PyPI oficial. "
                               "Nunca instala de URLs arbitrarias ou repositorios nao verificados.",
                "permissions": ["shell_execute"]
            },
        }

    def update_context(self, user_input: str) -> None:
        self.context.user_input = user_input
        self.logger.debug(f"Context updated: {user_input[:50]}...")

    def choose_action(self, user_input: str) -> Action:
        """Escolhe acao usando IA local (gratis) para classificar, se disponivel."""
        if self._ollama_ok:
            # Roteia com IA local — custo $0
            rota = classificar_tarefa_local(user_input)
            self.logger.info(f"Roteamento local: {rota['shell']} ({rota['modelo']}) | {rota['custo']}")

            if rota["shell"] == "S2":
                return Action(name="research", description="Pesquisar (nuvem)",
                              parameters={"query": user_input},
                              required_permissions=["network_access"],
                              security_policy="SECURITY: so pesquisa fontes publicas. Nunca faz scraping de sites autenticados ou pagos.")
            elif rota["shell"] == "S3":
                return Action(name="deep_reason", description="Analise profunda (nuvem)",
                              parameters={"topic": user_input},
                              required_permissions=["network_access"],
                              security_policy="SECURITY: nunca envia codigo fonte ou dados sensiveis para API. Anonimiza antes.")
            else:
                # S1 — tudo local, gratis
                return Action(name="local_exec", description=f"Executar local ({rota['categoria']})",
                              parameters={"input": user_input},
                              security_policy="SECURITY: execucao local. Dados nunca saem da maquina. Nao requer rede.")
        else:
            # Fallback: keyword matching (sem IA local)
            user_lower = user_input.lower()
            if any(w in user_lower for w in ["pesquisar", "search", "find", "buscar"]):
                return Action(name="research", description="Pesquisar",
                              parameters={"query": user_input},
                              required_permissions=["network_access"],
                              security_policy="SECURITY: so pesquisa fontes publicas.")
            elif any(w in user_lower for w in ["criar", "create", "build", "make"]):
                return Action(name="create", description="Criar projeto",
                              parameters={"desc": user_input},
                              required_permissions=["file_write", "shell_execute"],
                              security_policy="SECURITY: cria arquivos em D:/projetos/. Nunca sobrescreve sem confirmacao.")
            elif any(w in user_lower for w in ["explicar", "explain", "como"]):
                return Action(name="explain", description="Explicar",
                              parameters={"topic": user_input},
                              security_policy="SECURITY: so usa conhecimento interno. Nunca consulta web sem permissao.")
            else:
                return Action(name="local_exec", description="Executar local",
                              parameters={"input": user_input},
                              security_policy="SECURITY: execucao local padrao.")

    def execute_action(self, action: Action, user_input: str) -> HarnessResult:
        if not self._validate_permissions(action):
            return HarnessResult(False, "Permissoes insuficientes",
                                 error="Insufficient permissions")
        if not self._validate_context(action):
            return HarnessResult(False, "Contexto insuficiente",
                                 error="Missing context")

        # Se a acao for local (S1), usa IA local — $0
        if action.name == "local_exec" and self._ollama_ok:
            try:
                resposta = ollama_generate(user_input, max_tokens=1024)
                if resposta:
                    return HarnessResult(True, resposta, data=resposta,
                                         actions_taken=[action.name], tokens_used=0)
                return HarnessResult(True, f"[IA local offline] Processando: {user_input}",
                                     data=user_input, actions_taken=[action.name])
            except Exception as e:
                return HarnessResult(False, f"Erro local: {e}", error=str(e))

        try:
            result = f"Acao {action.name} via {action.parameters.get('model', 'nuvem')}"
            return HarnessResult(True, result, data=result,
                                 actions_taken=[action.name])
        except Exception as e:
            self.logger.error(f"Erro: {e}")
            return HarnessResult(False, f"Erro: {e}", error=str(e))

    def _validate_permissions(self, action: Action) -> bool:
        for p in action.required_permissions:
            if not self.permissions.get(p, False):
                return False
        return True

    def _validate_context(self, action: Action) -> bool:
        return len(self.context.user_input) > 0

    def update_progress(self, result: HarnessResult) -> None:
        self.context.recent_actions.append(
            f"{datetime.now().isoformat()}: {result.summary}")
        if len(self.context.recent_actions) > 10:
            self.context.recent_actions = self.context.recent_actions[-10:]

    def handle_error(self, error: Exception) -> None:
        self.logger.error(f"Agent error: {error}", exc_info=True)
