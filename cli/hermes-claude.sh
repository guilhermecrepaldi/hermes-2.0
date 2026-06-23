#!/bin/bash
# hermes-claude — Hermes wrapper for Claude Code CLI
# Inspired by free-claude-code fcc-claude launcher

HERMES_ROOT="$(cd "$(dirname "$0")/.." && pwd)"

export HERMES_ACTIVE=1
export HERMES_ROOT="$HERMES_ROOT"

echo "  Hermes Claude — running with Hermes config"
python "$HERMES_ROOT/cli/hermes-launcher.py" claude "$@"
