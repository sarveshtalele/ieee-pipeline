#!/usr/bin/env python3
from pathlib import Path
import re
import sys
from collections import Counter

ROOT = Path(__file__).resolve().parents[1]
TEX = ROOT / "paper" / "main.tex"
REVIEW = ROOT / "paper" / "review.tex"
BIB = ROOT / "paper" / "references.bib"
text = TEX.read_text(encoding="utf-8")
review = REVIEW.read_text(encoding="utf-8")
bib = BIB.read_text(encoding="utf-8")

failures = []
def check(ok, message):
    print(("PASS" if ok else "FAIL") + ": " + message)
    if not ok:
        failures.append(message)

check(r"\documentclass[conference]{IEEEtran}" in text, "IEEEtran conference class")
check(r"\bibliographystyle{IEEEtran}" in text, "IEEEtran numeric bibliography style")
check(r"\orcidlink{0000-0001-5644-1575}" in text, "Amey green ORCID symbol")
check(r"\orcidlink{0009-0002-0818-461X}" in text, "Sarvesh green ORCID symbol")
check("ORCID: 0000-0001-5644-1575" in text, "Amey ORCID ID is visibly printed")
check("ORCID: 0009-0002-0818-461X" in text, "Sarvesh ORCID ID is visibly printed")
check(r"\usepackage{cite}" in text, "IEEE numeric citation package")
check(r"\usepackage{hyperref}" in text, "PDF hyperlinks enabled")
check(r"\hypersetup" in text and "citecolor=" in text, "PDF citation links styled")
check(r"\begin{IEEEkeywords}" in text, "IEEE keywords block")
check(r"\bibliography{references}" in text, "bibliography included")

citation_groups = re.findall(r"\\cite(?:\[[^\]]*\])?\{([^}]*)\}", text)
cites = {key.strip() for group in citation_groups for key in group.split(",") if key.strip()}
keys_list = re.findall(r"@\w+\s*\{\s*([^,\s]+)", bib)
keys = set(keys_list)
missing = sorted(cites - keys)
duplicates = sorted(k for k, count in Counter(keys_list).items() if count > 1)
check(bool(cites), "in-text citations were detected")
check(not missing, "all citation keys resolve" + (f"; missing {missing}" if missing else ""))
check(not duplicates, "BibTeX keys are unique" + (f"; duplicates {duplicates}" if duplicates else ""))

labels = set(re.findall(r"\\label\{([^}]+)\}", text))
references = set(re.findall(r"\\(?:ref|eqref)\{([^}]+)\}", text))
unresolved_refs = sorted(references - labels)
check(not unresolved_refs, "all cross-references resolve"
      + (f"; missing labels {unresolved_refs}" if unresolved_refs else ""))
check(text.rstrip().endswith(r"\end{document}"), "document ends cleanly")
check(r"\def\REVIEWVERSION{1}" in review and r"\input{main.tex}" in review,
      "blind-review build entry point")
check(r"\ifanonymous" in text and r"\hypersetup{pdfauthor={}}" in text,
      "anonymous build clears author metadata")

for value in ["864 forward passes", "304 cases", "66.8\\%", "27.3\\%",
              "47.9", "57.6", "20.8\\%"]:
    check(value in text, f"preserved result: {value}")

if failures:
    sys.exit(1)
print("\nAll LaTeX source checks passed.")
