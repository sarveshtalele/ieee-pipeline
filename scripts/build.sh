#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT/paper"
mkdir -p "$ROOT/dist"

compile_variant() {
  local job="$1"; shift
  local source="$1"; shift
  rm -f "${job}.aux" "${job}.bbl" "${job}.blg" "${job}.log" "${job}.out" "${job}.fdb_latexmk" "${job}.fls"
  pdflatex -interaction=nonstopmode -halt-on-error -jobname="$job" "$source"
  bibtex "$job"
  pdflatex -interaction=nonstopmode -halt-on-error -jobname="$job" "$source"
  pdflatex -interaction=nonstopmode -halt-on-error -jobname="$job" "$source"
  local pdf="$ROOT/dist/${job}.pdf"
  cp "${job}.pdf" "$pdf"
  pdfinfo "$pdf" > "$ROOT/dist/${job}-pdfinfo.txt"
  local pages
  pages="$(pdfinfo "$pdf" | awk '/^Pages:/ {print $2}')"
  if [[ -z "$pages" || "$pages" -gt 6 ]]; then
    echo "CoDIT regular-paper limit is 6 pages; ${job} produced ${pages:-unknown}." >&2
    exit 1
  fi
  echo "Built ${pdf} (${pages} pages)."
}

compile_variant main main.tex
compile_variant main-review review.tex
cp "$ROOT/dist/main.pdf" "$ROOT/dist/codit2027-ieee.pdf"
cp "$ROOT/dist/main-pdfinfo.txt" "$ROOT/dist/pdfinfo.txt"
cp "$ROOT/dist/main-review.pdf" "$ROOT/dist/codit2027-ieee-review.pdf"
cp "$ROOT/dist/main-review-pdfinfo.txt" "$ROOT/dist/pdfinfo-review.txt"
