from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class PddArtifacts:
    pdd_root: Path
    inventory: dict[str, Any]
    source_map: dict[str, Any]
    disclosure: dict[str, Any]
    grounding: dict[str, Any]

    @property
    def source_root(self) -> Path:
        return Path(str(self.inventory.get("root", "")))

    @property
    def files(self) -> list[dict[str, Any]]:
        files = self.inventory.get("files", [])
        return files if isinstance(files, list) else []


def load_artifacts(pdd_root: str | Path) -> tuple[PddArtifacts | None, list[str]]:
    root = Path(pdd_root)
    required = {
        "inventory.json": root / "inventory.json",
        "source-map.json": root / "source-map.json",
        "disclosure.json": root / "disclosure.json",
        "review/grounding.json": root / "review" / "grounding.json",
    }
    reasons = [f"missing required artifact: {name}" for name, path in required.items() if not path.exists()]
    if reasons:
        return None, reasons

    try:
        artifacts = PddArtifacts(
            pdd_root=root,
            inventory=_read_json(required["inventory.json"]),
            source_map=_read_json(required["source-map.json"]),
            disclosure=_read_json(required["disclosure.json"]),
            grounding=_read_json(required["review/grounding.json"]),
        )
    except (OSError, json.JSONDecodeError) as exc:
        return None, [f"invalid PDD artifact JSON: {exc}"]

    if artifacts.grounding.get("status") != "pass":
        reasons.append("grounding receipt is not pass")
    if artifacts.disclosure.get("schema") != "pdd.disclosure.v1":
        reasons.append("unsupported disclosure contract")
    if artifacts.source_map.get("schema") != "pdd.source_map.v1":
        reasons.append("unsupported source map")
    return (None, reasons) if reasons else (artifacts, [])


def _read_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    return payload if isinstance(payload, dict) else {}
