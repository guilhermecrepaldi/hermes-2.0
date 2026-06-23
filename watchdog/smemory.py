"""Hermes Semantic Memory — Cross-session persistent memory.
Remembers decisions, patterns, and outcomes across sessions.
Gets smarter over time.
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Optional

try:
    from logger import get_logger
    logger = get_logger(__name__)
except ImportError:
    import logging
    logger = logging.getLogger(__name__)


MEMORY_DIR = Path.home() / ".hermes" / "semantic_memory"
MAX_MEMORIES = 100
MAX_AGE_DAYS = 30


@dataclass
class MemoryEntry:
    """A single memory entry."""
    id: str
    content: str
    category: str  # decision | pattern | error | success | preference
    tags: List[str] = field(default_factory=list)
    confidence: float = 0.5
    created_at: str = ""
    last_accessed: str = ""
    access_count: int = 0
    related_ids: List[str] = field(default_factory=list)

    def __post_init__(self):
        if not self.created_at:
            self.created_at = datetime.now().isoformat()
        if not self.last_accessed:
            self.last_accessed = self.created_at


class SemanticMemory:
    """Persistent memory that spans sessions and gets smarter over time.

    Stores:
    - Decisions made and their outcomes
    - Error patterns and solutions
    - User preferences and corrections
    - Successful strategies
    """

    def __init__(self):
        MEMORY_DIR.mkdir(parents=True, exist_ok=True)
        self.memories: List[MemoryEntry] = []
        self._load()

    def _load(self):
        """Load memories from disk."""
        path = MEMORY_DIR / "memories.json"
        if path.exists():
            try:
                data = json.loads(path.read_text(encoding="utf-8"))
                for item in data:
                    self.memories.append(MemoryEntry(**item))
                logger.info(f"Loaded {len(self.memories)} semantic memories")
            except Exception as e:
                logger.warning(f"Failed to load memories: {e}")

    def _save(self):
        """Save memories to disk."""
        path = MEMORY_DIR / "memories.json"
        try:
            data = [{
                "id": m.id,
                "content": m.content,
                "category": m.category,
                "tags": m.tags,
                "confidence": m.confidence,
                "created_at": m.created_at,
                "last_accessed": m.last_accessed,
                "access_count": m.access_count,
                "related_ids": m.related_ids,
            } for m in self.memories]
            path.write_text(json.dumps(data, indent=2), encoding="utf-8")
        except Exception as e:
            logger.warning(f"Failed to save memories: {e}")

    def remember(self, content: str, category: str = "decision",
                 tags: Optional[List[str]] = None,
                 confidence: float = 0.5,
                 related_ids: Optional[List[str]] = None) -> MemoryEntry:
        """Store a new memory."""
        entry = MemoryEntry(
            id=f"mem_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{len(self.memories)}",
            content=content,
            category=category,
            tags=tags or [],
            confidence=confidence,
            related_ids=related_ids or [],
        )
        self.memories.append(entry)

        # Auto-compact if over limit
        if len(self.memories) > MAX_MEMORIES:
            self._compact()

        self._save()
        logger.debug(f"Remembered: {content[:60]}...")
        return entry

    def recall(self, query: str, max_results: int = 5,
               min_confidence: float = 0.0) -> List[MemoryEntry]:
        """Search memories by keyword matching."""
        query_lower = query.lower()
        query_words = set(query_lower.split())

        scored = []
        for mem in self.memories:
            if mem.confidence < min_confidence:
                continue

            content_lower = mem.content.lower()
            tag_lower = " ".join(mem.tags).lower()
            searchable = content_lower + " " + tag_lower

            # Score by word overlap
            score = sum(1 for w in query_words if w in searchable)

            if score > 0:
                scored.append((score, mem))

        # Sort by score, then by access count, then by confidence
        scored.sort(key=lambda x: (-x[0], -x[1].access_count, -x[1].confidence))

        results = [mem for _, mem in scored[:max_results]]

        # Update access stats
        for mem in results:
            mem.access_count += 1
            mem.last_accessed = datetime.now().isoformat()
        self._save()

        return results

    def recall_by_category(self, category: str) -> List[MemoryEntry]:
        """Recall all memories of a category."""
        return [m for m in self.memories if m.category == category]

    def remember_error(self, error: str, solution: str) -> MemoryEntry:
        """Remember an error and how it was solved."""
        return self.remember(
            content=f"Error: {error} -> Solution: {solution}",
            category="error",
            tags=["error", "solution"],
            confidence=0.7,
        )

    def remember_success(self, strategy: str, result: str) -> MemoryEntry:
        """Remember a successful strategy."""
        return self.remember(
            content=f"Strategy: {strategy} -> Result: {result}",
            category="success",
            tags=["success", "strategy"],
            confidence=0.8,
        )

    def remember_preference(self, preference: str) -> MemoryEntry:
        """Remember a user preference."""
        return self.remember(
            content=preference,
            category="preference",
            tags=["preference", "user"],
            confidence=1.0,
        )

    def _compact(self):
        """Remove oldest/lowest-value memories."""
        # Remove expired memories
        cutoff = datetime.now() - timedelta(days=MAX_AGE_DAYS)
        self.memories = [
            m for m in self.memories
            if datetime.fromisoformat(m.created_at) > cutoff
            or m.confidence > 0.8  # Keep high confidence memories
        ]

        # If still over limit, remove lowest confidence
        if len(self.memories) > MAX_MEMORIES:
            self.memories.sort(key=lambda m: (m.confidence, m.access_count))
            self.memories = self.memories[-MAX_MEMORIES:]

    def get_stats(self) -> dict:
        """Get memory statistics."""
        categories = {}
        for m in self.memories:
            categories[m.category] = categories.get(m.category, 0) + 1

        return {
            "total": len(self.memories),
            "categories": categories,
            "total_accesses": sum(m.access_count for m in self.memories),
            "oldest": min(m.created_at for m in self.memories) if self.memories else "",
            "newest": max(m.created_at for m in self.memories) if self.memories else "",
        }

    def forget_old(self, max_age_days: int = MAX_AGE_DAYS):
        """Forget memories older than max_age_days."""
        cutoff = datetime.now() - timedelta(days=max_age_days)
        before = len(self.memories)
        self.memories = [
            m for m in self.memories
            if datetime.fromisoformat(m.created_at) > cutoff
        ]
        self._save()
        logger.info(f"Forgot {before - len(self.memories)} old memories")
