"""Hermes Auto-Compactor — Intelligent context window management.
Inspired by Claude Code's CLAUDE_CODE_AUTO_COMPACT_WINDOW=190000.
"""
from __future__ import annotations
import re
import os
from pathlib import Path
from typing import Optional, Dict, Any, List
from datetime import datetime

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
MAX_CONTEXT_TOKENS = 128000
COMPACT_THRESHOLD = 0.35  # Compact when 35% full
TARGET_RATIO = 0.15  # Compact down to 15%

_compact_count = 0
_last_compact = ""


def estimate_tokens(text: str) -> int:
    """Rough token estimation (4 chars per token)."""
    return len(text) // 4


def should_compact(text: str) -> bool:
    """Check if context should be compacted."""
    tokens = estimate_tokens(text)
    ratio = tokens / MAX_CONTEXT_TOKENS
    return ratio >= COMPACT_THRESHOLD


def compact_conversation(messages: List[Dict]) -> List[Dict]:
    """Compact conversation intelligently.
    
    1. Summarize older tool outputs
    2. Collapse repeated patterns
    3. Keep user intent and final decisions
    """
    global _compact_count, _last_compact
    
    if not messages or len(messages) < 4:
        return messages
    
    _compact_count += 1
    _last_compact = datetime.now().isoformat()
    
    compacted = []
    tool_output_accumulator = []
    assistant_count = 0
    
    for msg in messages:
        role = msg.get("role", "")
        content = msg.get("content", "")
        
        if role == "tool":
            # Accumulate tool outputs and summarize when many
            tool_output_accumulator.append(content[:200])
            if len(tool_output_accumulator) > 3:
                summary = _summarize_tool_outputs(tool_output_accumulator)
                compacted.append({
                    "role": "tool",
                    "content": f"[Compacted {len(tool_output_accumulator)} tool outputs]\n{summary}"
                })
                tool_output_accumulator = []
            continue
        
        if tool_output_accumulator:
            summary = _summarize_tool_outputs(tool_output_accumulator)
            compacted.append({
                "role": "tool",
                "content": f"[Compacted {len(tool_output_accumulator)} tool outputs]\n{summary}"
            })
            tool_output_accumulator = []
        
        if role == "assistant":
            assistant_count += 1
            # Keep first 3 assistant messages fully, compact the rest
            if assistant_count > 3:
                content = _compact_assistant_message(content)
        
        compacted.append(msg)
    
    # Clean up remaining tool outputs
    if tool_output_accumulator:
        summary = _summarize_tool_outputs(tool_output_accumulator)
        compacted.append({
            "role": "tool",
            "content": f"[Compacted {len(tool_output_accumulator)} tool outputs]\n{summary}"
        })
    
    # If still too large, more aggressive compaction
    text = " ".join(m.get("content", "") for m in compacted)
    ratio = estimate_tokens(text) / MAX_CONTEXT_TOKENS
    if ratio > TARGET_RATIO:
        compacted = _aggressive_compact(compacted)
    
    return compacted


def _summarize_tool_outputs(outputs: List[str]) -> str:
    """Summarize multiple tool outputs into one."""
    # Extract key info from outputs
    summaries = []
    for out in outputs:
        lines = out.strip().split("\n")
        # Keep first and last meaningful lines
        meaningful = [l for l in lines if l.strip() and len(l.strip()) > 20]
        if meaningful:
            first = meaningful[0][:150]
            if len(meaningful) > 2:
                last = meaningful[-1][:150]
                summaries.append(f"{first} ... {last}")
            else:
                summaries.append(first)
    
    if not summaries:
        return "[Tool outputs summarized]"
    
    return "\n".join(summaries[:5])


def _compact_assistant_message(content: str) -> str:
    """Compact an assistant message to its key points."""
    if len(content) < 500:
        return content
    return content[:300] + f"\n\n[... compacted, {len(content)} chars → 300 chars]"


def _aggressive_compact(messages: List[Dict]) -> List[Dict]:
    """More aggressive compaction when still over limit."""
    compacted = []
    keep_roles = {"user", "system"}
    
    for i, msg in enumerate(messages):
        role = msg.get("role", "")
        content = msg.get("content", "")
        
        # Always keep system and user messages
        if role in keep_roles:
            compacted.append(msg)
            continue
        
        # Keep last 3 assistant and tool messages
        remaining = len(messages) - i
        is_last = remaining <= 3
        if is_last:
            compacted.append(msg)
        elif role == "assistant":
            compacted.append({"role": "assistant", "content": content[:200]})
        elif role == "tool":
            compacted.append({"role": "tool", "content": content[:100]})
    
    return compacted


def get_compact_stats() -> dict:
    """Get compaction statistics."""
    return {
        "total_compactions": _compact_count,
        "last_compact": _last_compact,
        "threshold": COMPACT_THRESHOLD,
        "target_ratio": TARGET_RATIO,
        "max_tokens": MAX_CONTEXT_TOKENS,
    }
