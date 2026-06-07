# PDD-IAR

Progressive Disclosure Documentation - Investigative Autoregressive Retrieval.

PDD-IAR is a consumer layer for `.pdd/` artifacts. It does not generate
documentation, scan repositories, or replace PDD. It reads PDD artifacts,
verifies the disclosure contract, searches original mapped sources, and returns
an answerability state.

## Boundary

```text
PDD     -> creates inventory, source map, disclosure contract, review receipts
PDG     -> requires guardrails around PDD consumers
PDD-IAR -> investigates PDD artifacts and original source evidence
```

Generated docs are orientation only. They are never treated as source proof.

## Install

```bash
python3.11 -m pip install "pdd @ git+https://github.com/bacoco/progressive-disclosure-documentation.git@codex/pdd-iar-artifacts"
python3.11 -m pip install -e ".[test]"
```

The integration tests require the `pdd` CLI to be installed because they build
real PDD artifacts before investigating them.

## CLI

```bash
pdd-iar investigate \
  --query "penalty late delivery" \
  --pdd-root /path/to/.pdd \
  --docs-dir /path/to/docs
```

The command prints JSON with:

- `answerability_state`
- `reasons`
- `orientation`
- `evidence`
- `contradictions`
- `audit_trace`

## Answerability States

- `answerable`: mapped source evidence supports an answer.
- `contradictory`: source evidence exists, but contradiction markers are found.
- `insufficient_evidence`: the PDD contract is valid but no mapped source matches.
- `contract_invalid`: required PDD artifacts are missing or review failed.

## Verification

```bash
python3.11 -m pytest -q
```
