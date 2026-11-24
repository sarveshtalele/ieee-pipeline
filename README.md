# CoDIT 2027 IEEE Paper Pipeline

A reproducible GitHub Actions pipeline for the empirical preprint **The Knowledge Lifecycle of Large Language Models** (viXra:2611.0038).

## Scope
- Converted manuscript: `paper/main.tex`; bibliography: `paper/references.bib`.
- Source repository `Amey-Thakur/LLM-KNOWLEDGE-LIFECYCLE` is a read-only reference. This pipeline does not write to it.
- Official CoDIT 2027 instructions: https://codit2027.com/index.php/call-for-papers
- Official limits: regular paper up to 6 pages; short/WiP up to 5 pages and no more than 8 references. IEEE two-column, 10 pt, Times New Roman. Regular papers undergo blind technical review.

## Outputs
- `dist/codit2027-ieee.pdf`: identified author preview with green ORCID symbols and visible clickable ORCID IDs.
- `dist/codit2027-ieee-review.pdf`: anonymous review version, with blank PDF author metadata.
- Build checks validate citation keys, ORCID identifiers, IEEEtran class/style and the six-page cap.

## Build locally
Install TeX Live including `IEEEtran`, `orcidlink`, BibTeX and Poppler utilities, then:

```bash
make validate
make build
```

GitHub Actions runs on pushes, pull requests and manual dispatch, then publishes both PDFs and `pdfinfo` metadata as a build artifact.

## Submission caution
Use the anonymous PDF for blind review, but inspect all self-citations, repository links and acknowledgements for deanonymization before uploading to PaperCept. The identified PDF is an author preview, not the blind-review copy. This pipeline does not submit a paper or guarantee conference acceptance or IEEE Xplore acceptance.

## Licensing
Pipeline code and CI configuration are MIT-licensed (`LICENSE`). Manuscript attribution and source-content licence are documented in `PAPER-LICENSE.md`.
