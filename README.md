# CoDIT 2027 IEEE Paper Pipeline

A reproducible, CI-validated IEEE conference-paper build for **The Knowledge Lifecycle of Large Language Models** (viXra:2611.0038).

## Repository scope

- Manuscript source: `paper/main.tex`.
- Identified bibliography: `paper/references.bib`.
- Double-blind bibliography: `paper/references-review.bib`.
- Archived experiment summary: `paper/measurement-summary.json`, copied from the read-only research repository at the commit recorded in `SOURCE_PROVENANCE.md`.
- Research source: [Amey-Thakur/LLM-KNOWLEDGE-LIFECYCLE](https://github.com/Amey-Thakur/LLM-KNOWLEDGE-LIFECYCLE). It is treated as read-only; this pipeline does not push changes there.

## Conference format

The current [CoDIT 2027 Call for Papers](https://codit2027.com/index.php/call-for-papers) specifies regular papers of up to 6 pages, IEEE two-column format, 10 pt Times New Roman, and blind technical review. Short/WiP papers have a 5-page limit and an 8-reference limit. This repository targets the regular-paper track; confirm the live CFP again before submission.

## Outputs committed to GitHub

- `dist/codit2027-ieee.pdf`: identified author version, with separate author blocks, green ORCID symbols, visible ORCID IDs, and individual email links.
- `dist/codit2027-ieee-review.pdf`: review version, with no author block or PDF author metadata and a separate redacted bibliography.
- `dist/pdfinfo.txt` and `dist/pdfinfo-review.txt`: PDF build metadata.

A successful push to `main` builds, validates and publishes these files back into `dist/`. Pull requests and non-main branches run validation and expose an Actions artifact; they do not write generated files into the repository. The build job has read-only repository permissions; only the downstream publish job receives write permission.

## Local build

Install TeX Live with IEEEtran, the ORCID package, BibTeX, and Poppler utilities. Then run:

```bash
make validate
make build
make validate-pdf
```

- `make validate` checks author blocks, citation coverage, unique and cited bibliography entries, blind-review redactions, LaTeX references, and the manuscript table/chart against the archived result summary.
- `make build` compiles both PDFs and fails on overfull boxes, unresolved citations/references, BibTeX warnings, or a page count above six. Underfull boxes are reported for visual review.
- `make validate-pdf` checks page count and dimensions, font embedding, clickable ORCID/email/citation links, author metadata, and the full text and hyperlinks of the blind-review PDF.

CI dependencies are pinned in `requirements-ci.txt`. The GitHub Actions workflow pins its third-party actions to reviewed commit SHAs.

## Double-blind review caution

The review build redacts nine author-authored cited works and scans the whole generated PDF for author names, handles, ORCID identifiers, email addresses, and identity-bearing links. This removes direct self-citation leaks found during the repository audit.

**It cannot guarantee anonymity.** The same work is already publicly available as viXra:2611.0038 under its title and authors. A reviewer may identify it by searching the title or distinctive text. Check CoDIT's current prior-preprint and anonymity rules before submitting the review PDF.

## Research integrity and scope

The build validates the manuscript against a fixed aggregate summary copied from the source repository. It does not rerun the 864 research forward passes, independently reproduce the experiment, validate each scientific claim, or guarantee conference acceptance or IEEE Xplore acceptance. Any research-data change must be made in the source project by its maintainers, then deliberately imported here with an updated source commit and checksum.

## Licensing

Pipeline code and CI configuration are MIT-licensed (`LICENSE`). Paper content attribution and the source content's CC BY 4.0 licence are documented in `PAPER-LICENSE.md`. Source snapshots and conversion history are documented in `SOURCE_PROVENANCE.md` and `AUDIT.md`.
