# Architecture

PDD-IAR has one job: investigate an existing PDD artifact set.

## Flow

```text
query
  -> load .pdd artifacts
  -> validate disclosure and grounding
  -> use generated docs as orientation
  -> search mapped original sources
  -> detect contradiction markers
  -> return answerability state
```

## Required Artifacts

- `.pdd/disclosure.json`
- `.pdd/inventory.json`
- `.pdd/source-map.json`
- `.pdd/review/grounding.json`

The first MVP requires `grounding.json` to have status `pass`.

## Non-Goals

- no repository scanning;
- no documentation generation;
- no source-map generation;
- no chatbot UI;
- no LLM dependency in the core MVP.

## Next Steps

- add pluggable retrievers;
- add stronger contradiction policies;
- add citation spans;
- add optional LLM synthesis after answerability gates pass.
