import json
import shutil
import subprocess
from pathlib import Path

from pdd_iar import investigate


def _build_real_pdd_artifacts(tmp_path: Path) -> tuple[Path, Path, Path]:
    repo = tmp_path / "source-repo"
    docs = tmp_path / "docs"
    pdd_dir = tmp_path / ".pdd"
    repo.mkdir()
    (repo / "README.md").write_text(
        "\n".join(
            [
                "# ACME Supplier Evidence",
                "",
                "The ACME contract includes a penalty for late delivery.",
                "A later commercial waiver may suspend that penalty.",
            ]
        ),
        encoding="utf-8",
    )
    (repo / "operations.md").write_text(
        "The March delivery was late and triggered review of the penalty.",
        encoding="utf-8",
    )

    subprocess.run(
        ["pdd", "inventory", "--repo", str(repo), "--out", str(tmp_path / "inventory.json")],
        check=True,
        capture_output=True,
        text=True,
    )
    subprocess.run(
        ["pdd", "generate", "--inventory", str(tmp_path / "inventory.json"), "--out", str(docs)],
        check=True,
        capture_output=True,
        text=True,
    )
    subprocess.run(
        ["pdd", "review", "--docs", str(docs), "--inventory", str(tmp_path / "inventory.json"), "--out", str(pdd_dir / "review")],
        check=True,
        capture_output=True,
        text=True,
    )
    return pdd_dir, docs, repo


def test_investigation_uses_sources_not_generated_docs(tmp_path):
    if shutil.which("pdd") is None:
        raise AssertionError("pdd CLI is required for integration tests")
    pdd_dir, docs, _repo = _build_real_pdd_artifacts(tmp_path)

    report = investigate("penalty late delivery", pdd_dir=pdd_dir, docs_dir=docs)

    assert report.answerability_state == "contradictory"
    assert report.evidence
    assert all(item.kind == "source" for item in report.evidence)
    assert any(item.source_path == "README.md" for item in report.evidence)
    assert report.contradictions
    assert report.orientation


def test_missing_disclosure_contract_blocks_answer(tmp_path):
    pdd_dir, docs, _repo = _build_real_pdd_artifacts(tmp_path)
    (pdd_dir / "disclosure.json").unlink()

    report = investigate("penalty", pdd_dir=pdd_dir, docs_dir=docs)

    assert report.answerability_state == "contract_invalid"
    assert "missing required artifact: disclosure.json" in report.reasons
    assert not report.evidence


def test_failed_grounding_blocks_answer(tmp_path):
    pdd_dir, docs, _repo = _build_real_pdd_artifacts(tmp_path)
    grounding = pdd_dir / "review" / "grounding.json"
    payload = json.loads(grounding.read_text(encoding="utf-8"))
    payload["status"] = "fail"
    grounding.write_text(json.dumps(payload), encoding="utf-8")

    report = investigate("penalty", pdd_dir=pdd_dir, docs_dir=docs)

    assert report.answerability_state == "contract_invalid"
    assert "grounding receipt is not pass" in report.reasons
