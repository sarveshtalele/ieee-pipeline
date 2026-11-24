#!/usr/bin/env python3
"""Static source, author-block, bibliography and blind-review checks."""
from __future__ import annotations

from collections import Counter
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
PAPER = ROOT / "paper"
TEX = PAPER / "main.tex"
REVIEW_TEX = PAPER / "review.tex"
BIB = PAPER / "references.bib"
REVIEW_BIB = PAPER / "references-review.bib"

failures: list[str] = []


def check(ok: bool, message: str) -> None:
    print(("PASS" if ok else "FAIL") + ": " + message)
    if not ok:
        failures.append(message)


def cited_keys(source: str) -> set[str]:
    found: set[str] = set()
    pattern = re.compile(r"\\cite[a-zA-Z]*\*?(?:\[[^\]]*\])*\{([^}]*)\}")
    for group in pattern.findall(source):
        found.update(key.strip() for key in group.split(",") if key.strip())
    return found


def bibliography_entries(source: str) -> list[tuple[str, str]]:
    starts = list(re.finditer(r"(?m)^@(\w+)\s*\{\s*([^,\s]+)\s*,", source))
    result = []
    for index, match in enumerate(starts):
        end = starts[index + 1].start() if index + 1 < len(starts) else len(source)
        result.append((match.group(2), source[match.start():end]))
    return result


tex = TEX.read_text(encoding="utf-8")
review = REVIEW_TEX.read_text(encoding="utf-8")
bib = BIB.read_text(encoding="utf-8")
review_bib = REVIEW_BIB.read_text(encoding="utf-8")

check(r"\documentclass[10pt,conference]{IEEEtran}" in tex,
      "explicit IEEEtran 10 pt conference format")
check(r"\bibliographystyle{IEEEtran}" in tex, "IEEEtran bibliography style")
check(r"\usepackage{cite}" in tex, "IEEE numeric citation compression")
check(r"\usepackage{hyperref}" in tex, "hyperlinks enabled")
check(r"\usepackage{orcidlink}" in tex, "ORCID symbol package")
check(r"\begin{IEEEkeywords}" in tex, "IEEE Index Terms block")
check(r"\ifanonymous" in tex and r"\ifdefined\REVIEWVERSION\anonymoustrue\fi" in tex,
      "identified and blind-review modes are explicit")
check(r"\hypersetup{pdfauthor={}}" in tex, "anonymous PDF author metadata is cleared")
check(r"\bibliography{references-review}" in tex and
      r"\bibliography{references}" in tex,
      "each build selects its own bibliography")

# Separate IEEE conference author blocks: one complete block per author.
check(r"\IEEEauthorblockN{Amey Thakur\orcidlink{0000-0001-5644-1575}}" in tex,
      "Amey has an individual author-name block")
check(r"\IEEEauthorblockN{Sarvesh Talele\orcidlink{0009-0002-0818-461X}}" in tex,
      "Sarvesh has an individual author-name block")
check(tex.count(r"\IEEEauthorblockA{Independent Researcher") == 2,
      "both authors have separate Independent Researcher affiliation blocks")
check(tex.count(r"\and") >= 1, "IEEE author blocks are separated with \\and")
for value in (
    "Toronto, Canada", "Mumbai, India",
    "ameythakur20@gmail.com", "talelesarvesh@gmail.com",
    "ORCID: 0000-0001-5644-1575", "ORCID: 0009-0002-0818-461X",
):
    check(value in tex, f"identified author metadata present: {value}")
check("Independent Researchers\\\\" not in tex,
      "no merged plural affiliation remains")

# Citation coverage and bibliography hygiene for both variants.
cites = cited_keys(tex)
main_entries = bibliography_entries(bib)
review_entries = bibliography_entries(review_bib)
main_keys = [key for key, _ in main_entries]
review_keys = [key for key, _ in review_entries]
check(bool(cites), "in-text citations detected")
check(not (cites - set(main_keys)),
      "all citations resolve in the identified bibliography: "
      + str(sorted(cites - set(main_keys))))
check(not (cites - set(review_keys)),
      "all citations resolve in the blind-review bibliography: "
      + str(sorted(cites - set(review_keys))))
check(not (set(main_keys) - cites),
      "identified bibliography contains no uncited entries: "
      + str(sorted(set(main_keys) - cites)))
check(not (set(review_keys) - cites),
      "review bibliography contains no uncited entries: "
      + str(sorted(set(review_keys) - cites)))
check(not [k for k, n in Counter(main_keys).items() if n > 1],
      "identified bibliography keys are unique")
check(not [k for k, n in Counter(review_keys).items() if n > 1],
      "review bibliography keys are unique")
check(set(main_keys) == set(review_keys),
      "identified and blind bibliographies have identical citation-key sets")

for key, entry in main_entries:
    for field in ("author", "title", "year"):
        check(re.search(rf"(?m)^\s*{field}\s*=", entry) is not None,
              f"reference {key} has required {field} metadata")

# Check that author-identifying self-references and links cannot leak through
# the blind bibliography. The identified bibliography retains full records.
leak_patterns = (
    r"Thakur,\s*Amey", r"Talele,\s*Sarvesh", r"Amey-Thakur",
    r"ameythakur", r"sarveshtalele", r"ameythakur20", r"talelesarvesh",
)
for pattern in leak_patterns:
    check(re.search(pattern, review_bib, flags=re.IGNORECASE) is None,
          f"blind bibliography removes identity marker: {pattern}")
check("Omitted for double-blind review" in review_bib,
      "self-authored references are redacted in blind-review bibliography")

# Cross-reference integrity and balanced LaTeX structure.
labels_list = re.findall(r"\\label\{([^}]+)\}", tex)
labels = set(labels_list)
refs = set(re.findall(r"\\(?:ref|eqref)\{([^}]+)\}", tex))
check(len(labels_list) == len(labels), "LaTeX labels are unique")
check(not (refs - labels), "all figure/table/section references resolve: "
      + str(sorted(refs - labels)))

without_comments = "\n".join(re.sub(r"(?<!\\)%.*$", "", line) for line in tex.splitlines())
brace_depth = 0
bad_braces = False
escaped = False
for char in without_comments:
    if escaped:
        escaped = False
        continue
    if char == "\\":
        escaped = True
    elif char == "{":
        brace_depth += 1
    elif char == "}":
        brace_depth -= 1
        if brace_depth < 0:
            bad_braces = True
            brace_depth = 0
check(not bad_braces and brace_depth == 0, "LaTeX braces are balanced")

stack: list[str] = []
for command, env in re.findall(r"\\(begin|end)\{([^}]+)\}", without_comments):
    if command == "begin":
        stack.append(env)
    elif not stack or stack.pop() != env:
        bad_braces = True
        break
check(not bad_braces and not stack, "LaTeX environments are properly nested")

check(tex.rstrip().endswith(r"\end{document}"), "document ends with \\end{document}")
check(r"\def\REVIEWVERSION{1}" in review and r"\input{main.tex}" in review,
      "review entry point selects anonymous mode")
check(not re.search(r"\\usepackage(?:\[[^]]*\])?\{geometry\}", tex),
      "IEEEtran page geometry is not overridden")
check(not re.search(r"\\(?:setlength|addtolength)\s*\{\\(?:textwidth|columnsep|oddsidemargin|topmargin)\}", tex),
      "IEEEtran text-area dimensions are not manually overridden")
check(not re.search(r"(?m)^\s*\d+(?:\.\d+)?(?<!\\)%", tex),
      "numeric percent signs are escaped")

# Hygiene: source files are UTF-8, have final newlines and no trailing spaces.
for path in (TEX, REVIEW_TEX, BIB, REVIEW_BIB):
    raw = path.read_bytes()
    check(raw.endswith(b"\n"), f"{path.relative_to(ROOT)} ends with newline")
    check(not any(line.rstrip(b"\r\n").endswith((b" ", b"\t"))
                  for line in raw.splitlines(keepends=True)),
          f"{path.relative_to(ROOT)} has no trailing whitespace")
    check(b"\x00" not in raw, f"{path.relative_to(ROOT)} contains no NUL bytes")

if failures:
    print(f"\n{len(failures)} static validation check(s) failed.", file=sys.stderr)
    sys.exit(1)
print("\nAll static manuscript and bibliography checks passed.")
