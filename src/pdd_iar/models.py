from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass(frozen=True)
class EvidenceItem:
    kind: str
    source_path: str
    excerpt: str
    score: int
    authority: str = "supporting"
    freshness: str = "current"
    version: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class InvestigationReport:
    query: str
    answerability_state: str
    reasons: list[str] = field(default_factory=list)
    orientation: list[EvidenceItem] = field(default_factory=list)
    evidence: list[EvidenceItem] = field(default_factory=list)
    contradictions: list[EvidenceItem] = field(default_factory=list)
    audit_trace: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "query": self.query,
            "answerability_state": self.answerability_state,
            "reasons": self.reasons,
            "orientation": [item.to_dict() for item in self.orientation],
            "evidence": [item.to_dict() for item in self.evidence],
            "contradictions": [item.to_dict() for item in self.contradictions],
            "audit_trace": self.audit_trace,
        }
