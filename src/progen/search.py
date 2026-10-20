# SPDX-License-Identifier: AGPL-3.0-or-later
"""In-memory BM25 search index over Progen units and documents.

Standard library only. Zero external dependencies.
"""

from __future__ import annotations

from dataclasses import dataclass
import math
import re
from typing import Iterable, List, Optional

from .parse import Document, Role, Unit, parse_text
from .tells import STOP

_TOKEN = re.compile(r"[a-z0-9_]+", re.IGNORECASE)


def _tokenize(text: str) -> List[str]:
    return [t.lower() for t in _TOKEN.findall(text) if t.lower() not in STOP]


@dataclass(frozen=True)
class SearchHit:
    unit: Unit
    score: float
    doc_id: Optional[str] = None


class ProgenSearchIndex:
    """Zero-dependency in-memory BM25 index over topic and comment."""

    def __init__(self, k1: float = 1.5, b: float = 0.75) -> None:
        self.k1 = k1
        self.b = b
        self._units: List[tuple[Unit, Optional[str], dict[str, int], int]] = []
        self._df: dict[str, int] = {}
        self._total_len: int = 0

    def __len__(self) -> int:
        return len(self._units)

    def add_unit(self, unit: Unit, doc_id: Optional[str] = None) -> None:
        # Count topic and comment once. The raw line repeats those words.
        # Prose, admin, and protocol keep their words on text alone.
        parts = [unit.topic or "", unit.comment or ""]
        if not any(parts):
            parts = [unit.text or ""]
        tokens = _tokenize(" ".join(parts))
        tf: dict[str, int] = {}
        for tok in tokens:
            tf[tok] = tf.get(tok, 0) + 1
        for tok in tf:
            self._df[tok] = self._df.get(tok, 0) + 1
        doc_len = max(1, len(tokens))
        self._total_len += doc_len
        self._units.append((unit, doc_id, tf, doc_len))

    def add_units(self, units: Iterable[Unit], doc_id: Optional[str] = None) -> int:
        count = 0
        for u in units:
            self.add_unit(u, doc_id=doc_id)
            count += 1
        return count

    def add_document(self, doc: Document, doc_id: Optional[str] = None) -> int:
        return self.add_units(doc.units, doc_id=doc_id)

    def index_text(
        self,
        source: str,
        role: Role | str = Role.SYNTAX,
        doc_id: Optional[str] = None,
    ) -> int:
        doc = parse_text(source, role=role)
        return self.add_document(doc, doc_id=doc_id)

    def search(
        self,
        query: str,
        limit: int = 10,
        kind: Optional[str] = None,
    ) -> List[SearchHit]:
        q_tokens = _tokenize(query)
        if not q_tokens or not self._units:
            return []

        n_docs = len(self._units)
        avgdl = self._total_len / n_docs if n_docs else 1.0
        hits: List[SearchHit] = []

        for unit, doc_id, tf, doc_len in self._units:
            if kind is not None and unit.kind != kind:
                continue
            score = 0.0
            for term in q_tokens:
                freq = tf.get(term, 0)
                if freq == 0:
                    continue
                df = self._df.get(term, 0)
                idf = math.log(1.0 + (n_docs - df + 0.5) / (df + 0.5))
                denom = freq + self.k1 * (1.0 - self.b + self.b * (doc_len / avgdl))
                score += idf * ((freq * (self.k1 + 1.0)) / denom)
            if score > 0.0:
                hits.append(SearchHit(unit=unit, score=round(score, 6), doc_id=doc_id))

        hits.sort(key=lambda h: h.score, reverse=True)
        return hits[: max(0, limit)]
