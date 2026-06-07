from __future__ import annotations

import re
from pathlib import Path
from typing import Iterable

from pdd_iar.models import EvidenceItem

CONTRADICTION_TERMS = {
    "contradict",
    "deprecated",
    "exception",
    "force majeure",
    "not apply",
    "removed",
    "suspend",
    "waive",
    "waiver",
}


def query_tokens(query: str) -> list[str]:
    return [token for token in re.findall(r"[a-z0-9]+", query.lower()) if len(token) > 2]


def search_docs(docs_dir: str | Path | None, query: str) -> list[EvidenceItem]:
    if not docs_dir:
        return []
    root = Path(docs_dir)
    if not root.exists():
        return []
    tokens = query_tokens(query)
    hits = []
    fallback = []
    for path in sorted(root.glob("*.md")):
        content = path.read_text(encoding="utf-8", errors="replace")
        score = _score(content, tokens)
        if score:
            hits.append(EvidenceItem("orientation", path.name, _excerpt(content, tokens), score))
        else:
            fallback.append(EvidenceItem("orientation", path.name, _excerpt(content, tokens), 0))
    if not hits:
        return fallback
    return sorted(hits, key=lambda item: item.score, reverse=True)


def search_sources(source_root: Path, files: Iterable[dict[str, object]], query: str) -> list[EvidenceItem]:
    tokens = query_tokens(query)
    hits = []
    for item in files:
        if item.get("generated") or item.get("binary_asset"):
            continue
        path = source_root / str(item.get("path", ""))
        if not path.exists() or not path.is_file():
            continue
        content = path.read_text(encoding="utf-8", errors="replace")
        score = _score(" ".join([str(item.get("title", "")), str(item.get("path", "")), content]), tokens)
        if not score:
            continue
        hits.append(
            EvidenceItem(
                kind="source",
                source_path=str(item.get("path", "")),
                excerpt=_excerpt(content, tokens),
                score=score,
                authority=str(item.get("authority", "supporting")),
                freshness=str(item.get("freshness", "current")),
                version=str(item.get("version", "")),
            )
        )
    return sorted(hits, key=lambda item: (item.score, item.authority == "primary"), reverse=True)


def find_contradictions(evidence: Iterable[EvidenceItem]) -> list[EvidenceItem]:
    contradictions = []
    for item in evidence:
        text = item.excerpt.lower()
        if any(term in text for term in CONTRADICTION_TERMS):
            contradictions.append(
                EvidenceItem(
                    kind="contradiction",
                    source_path=item.source_path,
                    excerpt=item.excerpt,
                    score=item.score,
                    authority=item.authority,
                    freshness=item.freshness,
                    version=item.version,
                )
            )
    return contradictions


def _score(content: str, tokens: list[str]) -> int:
    lowered = content.lower()
    return sum(lowered.count(token) for token in tokens)


def _excerpt(content: str, tokens: list[str]) -> str:
    lines = [line.strip() for line in content.splitlines() if line.strip()]
    for line in lines:
        lowered = line.lower()
        if any(token in lowered for token in tokens) and any(term in lowered for term in CONTRADICTION_TERMS):
            return line[:240]
    for line in lines:
        if any(token in line.lower() for token in tokens):
            return line[:240]
    return (lines[0] if lines else "")[:240]
