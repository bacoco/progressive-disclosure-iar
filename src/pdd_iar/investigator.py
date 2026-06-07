from __future__ import annotations

from pathlib import Path

from pdd_iar.artifacts import PddArtifacts, load_artifacts
from pdd_iar.models import InvestigationReport
from pdd_iar.search import find_contradictions, search_docs, search_sources


def investigate(
    query: str,
    *,
    pdd_dir: str | Path | None = None,
    pdd_root: str | Path | None = None,
    docs_dir: str | Path | None = None,
) -> InvestigationReport:
    root = pdd_root if pdd_root is not None else pdd_dir
    if root is None:
        return _blocked(query, ["pdd_root is required"])

    artifacts, reasons = load_artifacts(root)
    if reasons or artifacts is None:
        return _blocked(query, reasons)

    audit = [
        "loaded PDD disclosure contract",
        "verified grounding receipt status",
        "treated generated docs as orientation",
        "searched original mapped sources for evidence",
    ]
    orientation = search_docs(docs_dir, query)
    mapped_files = _mapped_inventory_files(artifacts)
    evidence = search_sources(artifacts.source_root, mapped_files, query)
    contradictions = find_contradictions(evidence)

    if not evidence:
        state = "insufficient_evidence"
        reasons = ["no mapped source evidence matched the query"]
    elif contradictions:
        state = "contradictory"
        reasons = ["source evidence matched, but contradiction markers were found"]
    else:
        state = "answerable"
        reasons = ["mapped source evidence supports an answer"]

    return InvestigationReport(
        query=query,
        answerability_state=state,
        reasons=reasons,
        orientation=orientation,
        evidence=evidence,
        contradictions=contradictions,
        audit_trace=audit,
    )


def _blocked(query: str, reasons: list[str]) -> InvestigationReport:
    return InvestigationReport(
        query=query,
        answerability_state="contract_invalid",
        reasons=reasons,
        audit_trace=["blocked before retrieval because the PDD contract is invalid"],
    )


def _mapped_inventory_files(artifacts: PddArtifacts) -> list[dict[str, object]]:
    mapped = set()
    documents = artifacts.source_map.get("documents", {})
    if isinstance(documents, dict):
        for sources in documents.values():
            if isinstance(sources, list):
                mapped.update(str(source) for source in sources)
    return [item for item in artifacts.files if str(item.get("path", "")) in mapped]
