# Repository and pipeline audit

**Audit date:** 24 November 2026  
**Repository:** `sarveshtalele/ieee-pipeline`  
**Reference research repository:** `Amey-Thakur/LLM-KNOWLEDGE-LIFECYCLE` (read-only)

## Findings fixed

| Area | Finding | Change |
|---|---|---|
| IEEE author formatting | Both authors were placed inside one shared affiliation block. | Two distinct IEEE author blocks now show each author's own Independent Researcher affiliation, location, ORCID, and email. |
| Double-blind review | The earlier review PDF removed the title-page author block but retained self-authored bibliography records and identifying repository/demo links. | A separate review bibliography redacts the nine cited self-authored records. PDF validation scans the entire rendered text and hyperlink annotations, not only the first page. |
| Bibliography quality | The converted bibliography retained uncited entries and had several metadata differences from the research source bibliography. | The identified bibliography now contains only the 33 cited records, synced from the source bibliography. Two unused records were removed. The source mapping for the GPT-2 report is recorded in provenance. |
| Metrics drift | Table/chart values were manually embedded and not checked against the research output snapshot. | An archived JSON summary is checked against all six table rows, both plotted series, and manuscript headline figures. |
| LaTeX diagnostics | The build could succeed while overfull boxes or unresolved citations/references remained in logs. | Build checks now fail on overfull boxes, undefined citations/references, rerun warnings, font warnings, and BibTeX warnings. Underfull boxes are reported for human review. |
| PDF delivery checks | The old validator checked page count and only limited anonymity metadata. | It now checks page count, US Letter dimensions, embedded non-Type3 fonts, Times-compatible Roman font, separate author blocks, clickable ORCID/email/citation links, author metadata, and review-PDF text/URI leakage. |
| Local build hygiene | No ignore rules existed for LaTeX intermediates, and the previous clean target could remove the published PDFs. | Added `.gitignore`; `make clean` now removes intermediates only and preserves committed deliverables. |
| CI permissions | The build job ran with repository write permission even though it executes build code. | CI is being split into a read-only validation/build job and a downstream publish-only job with write permission. Actions and Python PDF dependency are pinned. |
| Documentation | README described artifact-only publishing and did not describe the actual GitHub `dist/` publishing model. | README and provenance now describe repository publishing, the data snapshot, blind-review redactions, and limitations. |

## Validation coverage

The CI pipeline performs:
1. Static LaTeX, author-block, bibliography and anonymity-source checks.
2. Measurement-summary consistency checks for counts, rates, all table rows, chart coordinates and selected narrative figures.
3. Two separate LaTeX/BibTeX builds: identified and blind-review.
4. Build-log checks for layout and reference warnings, plus the six-page regular-paper limit.
5. Compiled-PDF checks for text, metadata, links, fonts, page dimensions and blind-review identity leakage.
6. Artifact upload for every successful build and publication of the PDFs into `dist/` on `main`.

## Important limits

- The source research repository is not modified by this pipeline.
- The 864 forward-pass research experiment is not rerun here. The pipeline verifies the converted paper against a fixed aggregate snapshot copied from the source repository; that is not an independent scientific replication.
- The source preprint is already publicly available under its title and authors. Removing self-citation identifiers cannot guarantee double-blind anonymity because the title or distinctive text may identify the preprint.
- The font check confirms embedded Nimbus Roman (a Times-compatible substitute), not a licensed Times New Roman font file. The CFP requests Times New Roman; the final author should confirm the conference's accepted font policy or use a permitted Times New Roman font if strictly required.
- The CFP and submission rules can change. Confirm the official CoDIT 2027 instructions before uploading.
- Passing automated checks does not establish scientific validity, originality, acceptance, or IEEE Xplore eligibility.
