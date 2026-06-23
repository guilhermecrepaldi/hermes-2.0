#!/bin/bash
# hermes-codex — Hermes wrapper for OpenAI Codex CLI
# Inspired by free-claude-code fcc-codex launcher

HERMES_ROOT="$(cd "$(dirname "$0")/.." && pwd)"

export HERMES_ACTIVE=1
export HERMES_ROOT="$HERMES_ROOT"

echo "  Hermes Codex — running with Hermes config"
python "$HERMES_ROOT/cli/hermes-launcher.py" codex "$@"
