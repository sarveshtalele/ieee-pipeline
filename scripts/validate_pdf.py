#!/usr/bin/env python3
"""Validate the compiled, deliverable PDFs—not just the LaTeX source."""
from pathlib import Path
import sys
from pypdf import PdfReader

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"
IDENTIFIED = DIST / "codit2027-ieee.pdf"
REVIEW = DIST / "codit2027-ieee-review.pdf"

errors = []
def check(condition, message):
    print(("PASS" if condition else "FAIL") + ": " + message)
    if not condition:
        errors.append(message)

def inspect_pdf(path):
    if not path.is_file():
        check(False, f"{path.name} exists")
        return None, "", []
    reader = PdfReader(str(path))
    full_text = "\n".join(page.extract_text() or "" for page in reader.pages)
    annotations = []
    for page in reader.pages:
        for item in page.get("/Annots", []):
            annotations.append(item.get_object())
    return reader, full_text, annotations

identified, identified_text, identified_annots = inspect_pdf(IDENTIFIED)
review, review_text, review_annots = inspect_pdf(REVIEW)

if identified is not None:
    check(1 <= len(identified.pages) <= 6,
          f"identified PDF page count within CoDIT regular-paper limit ({len(identified.pages)})")
    author = str(identified.metadata.get("/Author", "") or "")
    check("Amey" in author and "Sarvesh" in author,
          "identified PDF author metadata present")
    check("0000-0001-5644-1575" in identified_text,
          "Amey ORCID identifier is visible")
    check("0009-0002-0818-461X" in identified_text,
          "Sarvesh ORCID identifier is visible")

    uri_links = []
    cite_destinations = []
    for annotation in identified_annots:
        action = annotation.get("/A")
        if not action:
            continue
        if action.get("/URI"):
            uri_links.append(str(action.get("/URI")))
        if action.get("/S") == "/GoTo":
            target = str(action.get("/D", ""))
            if target.startswith("cite."):
                cite_destinations.append(target)
    for identifier in ("0000-0001-5644-1575", "0009-0002-0818-461X"):
        expected = f"https://orcid.org/{identifier}"
        check(expected in uri_links, f"clickable ORCID URL: {identifier}")
    named = identified.named_destinations
    check(bool(cite_destinations), "in-text citation links are present")
    unresolved = sorted(set(target for target in cite_destinations if target not in named))
    check(not unresolved,
          "every in-text citation link targets a bibliography destination"
          + (f"; unresolved: {unresolved}" if unresolved else ""))

if review is not None:
    check(1 <= len(review.pages) <= 6,
          f"anonymous review PDF page count within CoDIT regular-paper limit ({len(review.pages)})")
    author = str(review.metadata.get("/Author", "") or "").strip()
    check(not author, "anonymous review PDF author metadata is empty")
    first_page = review.pages[0].extract_text() or ""
    check("Anonymous Submission" in first_page,
          "anonymous title page uses anonymous author block")
    check("ameythakur20@gmail.com" not in first_page.lower()
          and "talelesarvesh@gmail.com" not in first_page.lower(),
          "author email addresses are absent from anonymous title page")
    check("0000-0001-5644-1575" not in first_page
          and "0009-0002-0818-461X" not in first_page,
          "ORCID identifiers are absent from anonymous title page")
    check(any((a.get("/A") or {}).get("/S") == "/GoTo"
              and str((a.get("/A") or {}).get("/D", "")).startswith("cite.")
              for a in review_annots),
          "anonymous PDF retains linked in-text citations")

if errors:
    print(f"\n{len(errors)} PDF validation check(s) failed.", file=sys.stderr)
    sys.exit(1)
print("\nAll compiled-PDF checks passed.")
