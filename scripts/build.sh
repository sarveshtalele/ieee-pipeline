#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "\${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT/paper"
mkdir -p "$ROOT/dist"

check_build_logs() {
  local job="$1"
  local log="\${job}.log"
  local blg="\${job}.blg"

  if grep -E \
    'Overfull \\[hv]box|Citation .+ undefined|Reference .+ undefined|There were undefined references|Rerun to get cross-references right|LaTeX Font Warning' \
    "$log"; then
    echo "Formatting or unresolved-reference errors detected in \${job}.log." >&2
    exit 1
  fi

  if grep -E 'Warning--|I found no \\\\citation commands|I couldn'\''t open' "$blg"; then
    echo "BibTeX reported a bibliography error in \${job}.blg." >&2
    exit 1
  fi

  local underfull
  underfull="$(grep -c 'Underfull \\\\[hv]box' "$log" || true)"
  if [[ "$underfull" -gt 0 ]]; then
    echo "NOTE: \${job} has \${underfull} underfull box warning(s); inspect the rendered PDF."
  fi
}

compile_variant() {
  local job="$1"
  local source="$2"

  rm -f "\${job}.aux" "\${job}.bbl" "\${job}.blg" "\${job}.log" \
    "\${job}.out" "\${job}.fdb_latexmk" "\${job}.fls" "\${job}.synctex.gz"

  pdflatex -file-line-error -no-shell-escape \
    -interaction=nonstopmode -halt-on-error -jobname="$job" "$source"
  bibtex "$job"
  pdflatex -file-line-error -no-shell-escape \
    -interaction=nonstopmode -halt-on-error -jobname="$job" "$source"
  pdflatex -file-line-error -no-shell-escape \
    -interaction=nonstopmode -halt-on-error -jobname="$job" "$source"

  check_build_logs "$job"

  local pdf="$ROOT/dist/\${job}.pdf"
  cp "\${job}.pdf" "$pdf"
  pdfinfo "$pdf" > "$ROOT/dist/\${job}-pdfinfo.txt"

  local pages
  pages="$(pdfinfo "$pdf" | awk '/^Pages:/ {print $2}')"
  if [[ -z "$pages" || "$pages" -gt 6 ]]; then
    echo "CoDIT regular-paper limit is 6 pages; \${job} produced \${pages:-unknown}." >&2
    exit 1
  fi

  echo "Built $pdf ($pages pages)."
}

compile_variant main main.tex
compile_variant main-review review.tex

cp "$ROOT/dist/main.pdf" "$ROOT/dist/codit2027-ieee.pdf"
cp "$ROOT/dist/main-pdfinfo.txt" "$ROOT/dist/pdfinfo.txt"
cp "$ROOT/dist/main-review.pdf" "$ROOT/dist/codit2027-ieee-review.pdf"
cp "$ROOT/dist/main-review-pdfinfo.txt" "$ROOT/dist/pdfinfo-review.txt"
