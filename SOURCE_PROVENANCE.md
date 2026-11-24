# Source provenance

## Source manuscript and experiment snapshot

- Research source: [Amey-Thakur/LLM-KNOWLEDGE-LIFECYCLE](https://github.com/Amey-Thakur/LLM-KNOWLEDGE-LIFECYCLE).
- Source manuscript: `preprint/main.tex`, empirical preprint record viXra:2611.0038.
- Source repository HEAD inspected on 24 November 2026: `ada159df52a62fcd8312cda32669e527322ada9a`.
- Canonical source bibliography: `preprint/references.bib`, Git blob `cdd354a6110e18589781e0ea5643bf1caa072ea0`.
- Aggregate experiment results: `experiments/counterfactual_summary.json`, Git blob `e876fd7d76f228690859344911ca3aa7b4ba7d96`.
- The research repository was inspected read-only. No files, branches, issues, or workflows in it were modified.

## Conversion and bibliography handling

- Conference manuscript: `paper/main.tex`, IEEEtran 10 pt conference format, two-column output, IEEEtran bibliography style, linked numeric citations.
- The identified bibliography `paper/references.bib` contains the 33 entries cited by the conference manuscript, sourced from the canonical preprint bibliography. Citation keys are now aligned with the canonical source keys.
- Two unused source bibliography records were excluded rather than carried into the conference paper.
- `paper/references-review.bib` preserves the same citation keys while replacing nine author-identifying self-reference entries with anonymous placeholders. It is selected only for the review build.
- Bibliographic records are copied from the source bibliography. This pipeline checks required fields, cite-key coverage, duplicates and uncited records, but does not independently re-verify every publisher/DOI record.

## Data and PDF validation

- `paper/measurement-summary.json` is a snapshot of the source aggregate `counterfactual_summary.json`. Its upstream commit and Git blob SHA are recorded in `paper/measurement-summary.provenance.json`.
- The validation script cross-checks the reported counts and percentages, all six table rows, and the two plotted series against that snapshot.
- The original experiments are not rerun by this conversion pipeline. Numeric agreement with the snapshot is not an independent replication of the experiment.
- The identified PDF includes the two separate author blocks, individual locations, emails and ORCID links.
- The review PDF removes author metadata and its title-page author block, substitutes self-reference entries, and is scanned for author identity text and identity-bearing hyperlinks. This cannot guarantee anonymity because the viXra preprint is already public and searchable by title.

## Conference instructions

The official CoDIT 2027 Call for Papers was checked on 24 November 2026: regular-paper limit up to six pages, IEEE double-column format, 10 pt Times New Roman, and blind technical review. Re-check the current conference page before submission because requirements can change:
https://codit2027.com/index.php/call-for-papers
