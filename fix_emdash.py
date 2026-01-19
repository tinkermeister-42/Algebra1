#!/usr/bin/env python3
import re
from pathlib import Path

ROOT = Path("chapters")

def fix_text(s: str) -> str:
    orig = s

    # 1) Horizontal rule lines like "***" should be untouched
    # (no dash there anyway, but keep structure clear)

    # 2) Definition list style bullets:
    # - $(...)$ — parentheses
    # - $[\,]$ or $\{\,\}$ — brackets
    s = re.sub(
        r'^(\s*[-*+]\s+.+?)\s+—\s+',
        r'\1: ',
        s,
        flags=re.MULTILINE
    )

    # 3) Em dash at end of line becomes colon (common "lead in" usage)
    s = re.sub(r'—\s*$', ':', s, flags=re.MULTILINE)

    # 4) Spaced em dash patterns that strongly want a specific punctuation

    # " ... — but ..." -> ", but ..."
    s = re.sub(r'\s+—\s+(but\b)', r', \1', s)

    # "Direction: ... — as ..." and similar rubric bullets
    # This handles: "Negative correlation — as temperature increases, ..."
    s = re.sub(r'\s+—\s+(as\b)', r': \1', s)

    # "Strength: ... — points are ..." style
    s = re.sub(r'\s+—\s+(points\b)', r': \1', s)

    # 5) General spaced em dash -> comma
    s = re.sub(r'\s+—\s+', r', ', s)

    # 6) No space em dash cases
    # "made of—and how" -> "made of, and how"
    s = re.sub(r'([A-Za-z0-9])—and\b', r'\1, and', s)

    # "number crunching—you’re" -> "number crunching, you’re"
    s = re.sub(r'([A-Za-z0-9])—you\b', r'\1, you', s)

    # Also catch common contractions without being too aggressive
    s = re.sub(r'([A-Za-z0-9])—you\'', r"\1, you'", s)
    s = re.sub(r'([A-Za-z0-9])—we\b', r'\1, we', s)
    s = re.sub(r'([A-Za-z0-9])—it\b', r'\1, it', s)

    return s if s != orig else orig

def main():
    if not ROOT.exists():
        raise SystemExit(f"Could not find {ROOT}. Run from the book root.")

    changed_files = 0
    total_replacements = 0

    for path in ROOT.rglob("*"):
        if not path.is_file():
            continue
        if path.suffix.lower() not in {".qmd", ".md"}:
            continue

        text = path.read_text(encoding="utf-8")
        if "—" not in text:
            continue

        new_text = fix_text(text)
        if new_text == text:
            continue

        # Count how many em dashes got removed in this file
        before = text.count("—")
        after = new_text.count("—")
        removed = before - after

        bak = path.with_suffix(path.suffix + ".bak")
        if not bak.exists():
            bak.write_text(text, encoding="utf-8")

        path.write_text(new_text, encoding="utf-8")

        changed_files += 1
        total_replacements += removed
        print(f"{path}: removed {removed} em dash characters")

    print()
    print(f"Done. Files changed: {changed_files}. Em dashes removed: {total_replacements}.")
    print("Backups written as .bak next to each edited file (only if not already present).")

if __name__ == "__main__":
    main()
