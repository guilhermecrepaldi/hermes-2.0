#!/usr/bin/env python3
"""Notify hook — notificação pós-tarefa (placeholder)."""
import sys, json, os
sys.path.insert(0, os.path.dirname(__file__))
from validate import run_hook
run_hook("notify")
