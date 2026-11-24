#!/usr/bin/env python3
"""Validate the actual conference PDFs after compilation."""
from __future__ import annotations

from pathlib import Path
import re
import subprocess
import sys
from pypdf import PdfReader

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"
IDENTIFIED = DIST / "codit2027-ieee.pdf"
REVIEW = DIST / "codit2027-ieee-review.pdf"

errors: list[str] = []


def check(condition: bool, message: str) -> None:
    print(("PASS" if condition else "FAIL") + ": " + message)
    if not condition:
        errors.append(message)


def inspect_pdf(path: Path):
    if not path.is_file():
        check(False, f"{path.name} exists")
        return None, "", []
    reader = PdfReader(str(path), strict=True)
    full_text = "\n".join(page.extract_text() or "" for page in reader.pages)
    annotations = []
    for page in reader.pages:
        for item in page.get("/Annots", []):
            annotations.append(item.get_object())
    return reader, full_text, annotations


def validate_page_geometry(reader: PdfReader, label: str) -> None:
    ok = bool(reader.pages)
    for page in reader.pages:
        width = float(page.mediabox.width)
        height = float(page.mediabox.height)
        ok = ok and abs(width - 612.0) < 0.5 and abs(height - 792.0) < 0.5
    check(ok, f"{label} uses US Letter page geometry on every page")


def validate_fonts(path: Path, label: str) -> None:
    try:
        result = subprocess.run(
            ["pdffonts", str(path)], check=True, capture_output=True, text=True
        )
    except (OSError, subprocess.CalledProcessError) as exc:
        check(False, f"{label} font inspection completed: {exc}")
        return

    # pdffonts' Type column can be one token ("TrueType") or several
    # ("Type 1", "CID Type 0C"). Parse the fixed tail of columns instead of
    # using fixed split indexes, which incorrectly read "WinAnsi" as emb.
    parsed = []
    for line in result.stdout.splitlines()[2:]:
        parts = line.split()
        if len(parts) < 8:
            continue
        font_name = parts[0]
        font_type = " ".join(parts[1:-6])
        encoding = parts[-6]
        embedded, subset, unicode_map = parts[-5:-2]
        parsed.append({
            "name": font_name,
            "type": font_type,
            "encoding": encoding,
            "embedded": embedded.lower(),
            "subset": subset.lower(),
            "unicode": unicode_map.lower(),
        })

    check(bool(parsed), f"{label} contains inspectable PDF fonts")
    if parsed:
        inventory = "; ".join(
            f"{f['name']} ({f['type']}, embedded={f['embedded']})"
            for f in parsed
        )
        check(all(f["embedded"] == "yes" for f in parsed),
              f"{label} embeds every PDF font: {inventory}")
        check(all("type 3" not in f["type"].lower() for f in parsed),
              f"{label} contains no Type 3 bitmap fonts: {inventory}")
        check(any("NimbusRomNo9L" in f["name"] for f in parsed),
              f"{label} uses an embedded Times-compatible Roman text font")


def links(annotations):
    uris = []
    citations = []
    for annotation in annotations:
        action = annotation.get("/A")
        if action is None:
            continue
        uri = action.get("/URI")
        if uri:
            uris.append(str(uri))
        if action.get("/S") == "/GoTo":
            destination = action.get("/D")
            if isinstance(destination, str):
                citations.append(destination)
            elif destination is not None:
                citations.append(str(destination))
    return uris, citations


identified, identified_text, identified_annots = inspect_pdf(IDENTIFIED)
review, review_text, review_annots = inspect_pdf(REVIEW)

if identified is not None:
    check(1 <= len(identified.pages) <= 6,
          f"identified PDF page count within CoDIT regular-paper limit ({len(identified.pages)})")
    validate_page_geometry(identified, "identified PDF")
    validate_fonts(IDENTIFIED, "identified PDF")

    metadata = identified.metadata or {}
    author = str(metadata.get("/Author", "") or "")
    check("Amey" in author and "Sarvesh" in author,
          "identified PDF author metadata present")
    first_page = identified.pages[0].extract_text() or ""
    check("Amey Thakur" in first_page and "Sarvesh Talele" in first_page,
          "both author names are visible on the first page")
    check(first_page.count("Independent Researcher") == 2,
          "first page shows two separate Independent Researcher affiliations")
    check("Toronto, Canada" in first_page and "Mumbai, India" in first_page,
          "each author has the correct separate location")
    check("ameythakur20@gmail.com" in first_page
          and "talelesarvesh@gmail.com" in first_page,
          "each author has an individual email address")
    check("0000-0001-5644-1575" in first_page
          and "0009-0002-0818-461X" in first_page,
          "both ORCID identifiers are visible on the first page")

    uri_links, cite_destinations = links(identified_annots)
    for identifier in ("0000-0001-5644-1575", "0009-0002-0818-461X"):
        expected = f"https://orcid.org/{identifier}"
        check(expected in uri_links, f"clickable ORCID URL: {identifier}")
    for email in ("ameythakur20@gmail.com", "talelesarvesh@gmail.com"):
        check(f"mailto:{email}" in uri_links, f"clickable author email: {email}")
    named = identified.named_destinations
    check(bool(cite_destinations), "identified in-text citation links are present")
    unresolved = sorted(set(target for target in cite_destinations
                            if target.startswith("cite.") and target not in named))
    check(not unresolved,
          "identified citation links resolve to bibliography destinations"
          + (f"; unresolved: {unresolved}" if unresolved else ""))

if review is not None:
    check(1 <= len(review.pages) <= 6,
          f"anonymous review PDF page count within CoDIT regular-paper limit ({len(review.pages)})")
    validate_page_geometry(review, "blind-review PDF")
    validate_fonts(REVIEW, "blind-review PDF")

    metadata = review.metadata or {}
    author = str(metadata.get("/Author", "") or "").strip()
    check(not author, "blind-review PDF author metadata is empty")
    first_page = review.pages[0].extract_text() or ""
    check("Anonymous Submission" in first_page,
          "blind-review title page uses anonymous author block")
    check("Independent Researcher" not in first_page
          and "Toronto, Canada" not in first_page
          and "Mumbai, India" not in first_page,
          "blind-review title page contains no author affiliations or locations")

    # Scan the entire document, not just the title page. Self-citations in the
    # previous build exposed both authors and the code repository in the refs.
    identity_markers = (
        "amey", "sarvesh", "thakur", "talele", "ameythakur",
        "sarveshtalele", "ameythakur20", "talelesarvesh",
        "0000-0001-5644-1575", "0009-0002-0818-461X",
    )
    lower_text = review_text.lower()
    for marker in identity_markers:
        check(marker not in lower_text,
              f"blind-review PDF contains no author identity marker: {marker}")
    check(review_text.count("Omitted for double-blind review") >= 9,
          "all author-identifying self-reference entries are redacted")
    review_uris, review_citations = links(review_annots)
    identity_url_markers = (
        "Amey-Thakur", "ameythakur", "sarveshtalele", "talelesarvesh",
        "0000-0001-5644-1575", "0009-0002-0818-461X",
    )
    for marker in identity_url_markers:
        check(not any(marker.lower() in uri.lower() for uri in review_uris),
              f"blind-review PDF has no identity-bearing hyperlink: {marker}")
    check(bool(review_citations),
          "blind-review PDF retains linked in-text citations")
    named = review.named_destinations
    unresolved = sorted(set(target for target in review_citations
                            if target.startswith("cite.") and target not in named))
    check(not unresolved,
          "blind-review citation links resolve to bibliography destinations"
          + (f"; unresolved: {unresolved}" if unresolved else ""))

if errors:
    print(f"\n{len(errors)} compiled-PDF validation check(s) failed.", file=sys.stderr)
    sys.exit(1)
print("\nAll compiled-PDF checks passed.")
