#!/usr/bin/env python3

from __future__ import annotations

import csv
import sys
from pathlib import Path


IGNORE_SUBSTRINGS = (
    "/chapters/Assessments/",
    "/chapters/Interactive/",
    "/chapters/Supplemental/",
)

IGNORE_FILENAMES = {
    "index.qmd",
    "Review.qmd",
    "lesson_template.qmd",
}

MIN_TOTAL_YOUTRY = 3
MIN_REMEMBER = 1
MIN_GOTCHA = 1
MIN_THINK = 1


def is_lesson(path_str: str) -> bool:
    p = path_str.replace("\\", "/")
    if any(s in p for s in IGNORE_SUBSTRINGS):
        return False
    name = Path(p).name
    if name in IGNORE_FILENAMES:
        return False
    if not p.endswith(".qmd"):
        return False
    if "/chapters/Unit_" not in p:
        return False
    return True


def main() -> int:
    if len(sys.argv) != 2:
        print("Usage: callout_todo_from_tsv.py callout_counts.tsv")
        return 2

    tsv_path = Path(sys.argv[1])
    if not tsv_path.exists():
        print(f"File not found: {tsv_path}")
        return 1

    rows = []
    with tsv_path.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f, delimiter="\t")
        for r in reader:
            file = r.get("file", "")
            if not is_lesson(file):
                continue

            def geti(k: str) -> int:
                v = (r.get(k) or "").strip()
                return int(v) if v else 0

            y1 = geti("you-try")
            y2 = geti("you-try-m")
            missing = []

            if y1 + y2 < MIN_TOTAL_YOUTRY:
                missing.append(f"needs more you try (has {y1 + y2})")
            if geti("remember") < MIN_REMEMBER:
                missing.append("needs remember")
            if geti("gotcha") < MIN_GOTCHA:
                missing.append("needs gotcha")
            if geti("think") < MIN_THINK:
                missing.append("needs think")

            score = len(missing)
            if score > 0:
                rows.append((score, file, missing))

    rows.sort(key=lambda x: (-x[0], x[1]))

    if not rows:
        print("All lessons meet the minimum callout targets.")
        return 0

    for score, file, missing in rows:
        print(f"{file}")
        for item in missing:
            print(f"  {item}")
        print()

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
