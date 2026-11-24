#!/usr/bin/env python3
"""Cross-check manuscript table, figure and headline numbers against the
fixed, source-controlled measurement-summary snapshot.
"""
from __future__ import annotations

import json
import math
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
SUMMARY_PATH = ROOT / "paper" / "measurement-summary.json"
TEX_PATH = ROOT / "paper" / "main.tex"
tex = TEX_PATH.read_text(encoding="utf-8")
summary = json.loads(SUMMARY_PATH.read_text(encoding="utf-8"))

errors: list[str] = []


def check(ok: bool, message: str) -> None:
    print(("PASS" if ok else "FAIL") + ": " + message)
    if not ok:
        errors.append(message)


models = [
    ("GPT-2", "gpt2"),
    ("GPT-2 medium", "gpt2-medium"),
    ("GPT-2 large", "gpt2-large"),
    ("Qwen2.5-0.5B-Instruct", "Qwen/Qwen2.5-0.5B-Instruct"),
    ("TinyLlama-1.1B-Chat", "TinyLlama/TinyLlama-1.1B-Chat-v1.0"),
    ("Qwen2.5-1.5B-Instruct", "Qwen/Qwen2.5-1.5B-Instruct"),
]

check(summary.get("n_rows") == 864, "source snapshot reports 864 forward passes")
check(len(summary.get("models", {})) == 6, "source snapshot contains six models")
check(summary.get("n_conflict_total") == 304, "source snapshot has 304 genuine conflicts")
check(summary.get("adopt_in_conflict_overall_pct") == 66.8,
      "weighted document-adoption rate is 66.8%")
check(summary.get("keep_in_conflict_overall_pct") == 27.3,
      "weighted parametric-answer retention rate is 27.3%")
check(summary.get("median_phrasing_spread") == 47.9,
      "median all-probe phrasing spread is 47.9 percentage points")
check(summary.get("max_adopt_spread") == 57.6,
      "maximum conflict-only adoption spread is 57.6 percentage points")
check(summary.get("prob_over_10pct") == 332
      and summary.get("prob_over_10pct_not_top1") == 69
      and summary.get("prob_over_10pct_not_top1_pct") == 20.8,
      "probability-versus-rank counts match 332 / 69 / 20.8%")

# Reconstruct aggregate percentages from the model-level rounded rates and
# integer conflict counts as an independent internal consistency check.
total_conflicts = 0
adopted = 0
kept = 0
for _, key in models:
    item = summary["models"][key]
    check(item.get("n") == 72, f"{key}: 72 probe-phrasing pairs per condition")
    total_conflicts += item["n_conflict"]
    adopted += round(item["n_conflict"] * item["adopt_in_conflict_pct"] / 100)
    kept += round(item["n_conflict"] * item["keep_in_conflict_pct"] / 100)
check(total_conflicts == summary["n_conflict_total"],
      "sum of per-model conflicts equals the overall conflict count")
check(round(100 * adopted / total_conflicts, 1)
      == summary["adopt_in_conflict_overall_pct"],
      "per-model adoption counts reproduce the overall adoption rate")
check(round(100 * kept / total_conflicts, 1)
      == summary["keep_in_conflict_overall_pct"],
      "per-model retention counts reproduce the overall retention rate")

# Parse the six result rows from the LaTeX table.
expected = {}
for display, key in models:
    item = summary["models"][key]
    expected[display] = [
        int(item["params_m"]),
        float(item["knows_no_doc_pct"]),
        int(item["n_conflict"]),
        float(item["adopt_in_conflict_pct"]),
        float(item["keep_in_conflict_pct"]),
        float(item["phrasing_spread"]),
    ]

found = {}
for line in tex.splitlines():
    if "&" not in line:
        continue
    parts = [part.strip() for part in line.split("&")]
    if len(parts) != 7 or parts[0] not in expected:
        continue
    parts[-1] = re.sub(r"\\\\+\s*$", "", parts[-1]).strip()
    try:
        found[parts[0]] = [
            int(parts[1]), float(parts[2]), int(parts[3]),
            float(parts[4]), float(parts[5]), float(parts[6]),
        ]
    except ValueError:
        errors.append(f"could not parse result row for {parts[0]}")

check(set(found) == set(expected),
      "LaTeX results table contains each of the six source models exactly once")
for display, values in expected.items():
    if display not in found:
        continue
    actual = found[display]
    ok = len(actual) == len(values) and all(
        abs(float(a) - float(b)) < 0.051 for a, b in zip(actual, values)
    )
    check(ok, f"table row matches measured summary: {display}")

# Verify both plotted lines against the same model-level rates. The chart uses
# a log-scaled x coordinate normalized to 0..9.25 and y=percentage/20.
chart_specs = [
    (r"\\draw\[line width=1pt,knowInk\]\s*(.+)", "knows_no_doc_pct", "knowledge"),
    (r"\\draw\[line width=1pt,adoptInk,dashed\]\s*(.+)", "adopt_in_conflict_pct", "adoption"),
]
params = [summary["models"][key]["params_m"] for _, key in models]
xmin, xmax = math.log10(min(params)), math.log10(max(params))
for pattern, field, label in chart_specs:
    match = re.search(pattern, tex)
    if not match:
        check(False, f"{label} plot line exists")
        continue
    coordinates = [(float(x), float(y)) for x, y in
                   re.findall(r"\(([\d.]+),([\d.]+)\)", match.group(1))]
    check(len(coordinates) == 6, f"{label} plot contains six data points")
    if len(coordinates) != 6:
        continue
    comparisons = []
    chart_models = sorted(models, key=lambda pair: summary["models"][pair[1]]["params_m"])
    for (display, key), (x, y) in zip(chart_models, coordinates):
        item = summary["models"][key]
        expected_x = 9.25 * (math.log10(item["params_m"]) - xmin) / (xmax - xmin)
        expected_y = float(item[field]) / 20.0
        comparisons.append(abs(x - expected_x) <= 0.002
                           and abs(y - expected_y) <= 0.006)
    check(all(comparisons), f"{label} plot coordinates match source results")

# Guard narrative values most likely to drift away from the measurements.
headline_values = [
    "864 forward passes", "304 cases", "304 genuine conflicts",
    "66.8\\%", "27.3\\%", "47.9", "57.6",
    "332", "69", "20.8\\%", "25.0\\%", "98.6\\%",
    "97.2\\%", "38.6\\%", "91.8\\%", "87.3", "0.0\\%",
    "17.4\\%", "75.0\\%",
]
for value in headline_values:
    check(value in tex, f"manuscript includes source-backed headline value {value}")

if errors:
    print(f"\n{len(errors)} result consistency check(s) failed.", file=sys.stderr)
    sys.exit(1)
print("\nAll measurement-to-manuscript checks passed.")
