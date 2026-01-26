#!/usr/bin/env python3
"""
lesson_context_extractor.py

Scan Algebra book lesson .qmd files and extract compact context:
- title, unit, lesson number
- headings (## only)
- callout counts for your callout types
- you-try titles
- snippets from remember, gotcha, think blocks
- intro first sentence (light heuristic)

Outputs:
- lesson_context.tsv
- lesson_context.jsonl

Usage:
  python3 lesson_context_extractor.py chapters
  python3 lesson_context_extractor.py chapters --out-dir .
  python3 lesson_context_extractor.py chapters --out-prefix lesson_context

Notes:
- Filters out Assessments, Interactive, Supplemental, index.qmd, Review.qmd, lesson_template.qmd
- Does not modify any files
"""

from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple


CALLOUT_TYPES = [
    "answers",
    "answer",
    "objectives",
    "vocab",
    "real-world",
    "remember",
    "you-try",
    "you-try-m",
    "think",
    "gotcha",
    "note",
]

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

# Matches callout openers like:
# ::: {.remember}
# ::: {.remember collapse="true"}
# ::: remember
# ::: .remember
CALLOUT_OPEN_RE = re.compile(
    r"^\s*:::\s*(?:\{\s*\.?([A-Za-z0-9_-]+)\b[^}]*\}|\.\s*([A-Za-z0-9_-]+)\b|([A-Za-z0-9_-]+)\b)",
    re.IGNORECASE,
)

CALLOUT_CLOSE_RE = re.compile(r"^\s*:::\s*$")

TITLE_HEADING_RE = re.compile(r"^\s*#\s+(.+?)\s*$")
H2_HEADING_RE = re.compile(r"^\s*##\s+(.+?)\s*$")
ATTR_BLOCK_TRAIL_RE = re.compile(r"\s*\{[^}]*\}\s*$")

EXAMPLE_RE = re.compile(r"^\s*\*\*Example\s+\d+\s*:\*\*", re.IGNORECASE)

# Captures title="..." inside opener line
TITLE_ATTR_RE = re.compile(r'title\s*=\s*"([^"]*)"', re.IGNORECASE)

UNIT_RE = re.compile(r"/Unit_(\d+)(?:/|$)")
LESSON_RE = re.compile(r"^(\d+(?:\.\d+)?)_")

SENTENCE_SPLIT_RE = re.compile(r"([.!?])\s+")


def is_lesson_file(path: Path) -> bool:
    p = "/" + str(path).replace("\\", "/").lstrip("/")
    if not p.endswith(".qmd"):
        return False
    if any(s in p for s in IGNORE_SUBSTRINGS):
        return False
    if path.name in IGNORE_FILENAMES:
        return False
    if "/chapters/Unit_" not in p:
        return False
    return True



def strip_trailing_attr_blocks(s: str) -> str:
    return ATTR_BLOCK_TRAIL_RE.sub("", s).strip()


def parse_unit_from_path(path: Path) -> str:
    m = UNIT_RE.search(str(path).replace("\\", "/"))
    return m.group(1) if m else ""


def parse_lesson_from_filename(path: Path) -> str:
    m = LESSON_RE.match(path.name)
    return m.group(1) if m else ""


def first_sentence(text: str) -> str:
    t = " ".join(text.split())
    if not t:
        return ""
    parts = SENTENCE_SPLIT_RE.split(t, maxsplit=1)
    if len(parts) >= 2:
        return (parts[0] + parts[1]).strip()
    return t


def clean_snippet_line(line: str) -> str:
    s = line.strip()
    if not s:
        return ""
    # remove common markdown prefixes
    s = re.sub(r"^[-*]\s+", "", s)
    s = re.sub(r"^\d+\.\s+", "", s)
    s = re.sub(r"^>\s+", "", s)
    s = s.strip()
    return s


def extract_intro_first_sentence(lines: List[str]) -> str:
    # Take first paragraph before first callout or first H2.
    collected: List[str] = []
    started = False

    for line in lines:
        if CALLOUT_OPEN_RE.match(line) or H2_HEADING_RE.match(line):
            break

        # skip title heading and blank lines before content
        if TITLE_HEADING_RE.match(line):
            continue

        if line.strip() == "":
            if started:
                break
            continue

        started = True
        collected.append(line.strip())

    return first_sentence(" ".join(collected))


def scan_callouts(lines: List[str]) -> Tuple[Dict[str, int], Dict[str, List[Dict[str, object]]], List[str]]:
    counts = {t: 0 for t in CALLOUT_TYPES}
    blocks: Dict[str, List[Dict[str, object]]] = {t: [] for t in CALLOUT_TYPES}
    you_try_titles: List[str] = []

    in_type: Optional[str] = None
    buf: List[str] = []
    opener_line: str = ""

    def flush_block():
        nonlocal in_type, buf, opener_line, you_try_titles
        if in_type is None:
            return
        content = "".join(buf)
        blocks[in_type].append({"opener": opener_line, "content": content})
        in_type = None
        buf = []
        opener_line = ""

    for line in lines:
        if in_type is None:
            m = CALLOUT_OPEN_RE.match(line)
            if m:
                t = (m.group(1) or m.group(2) or m.group(3) or "").strip().lower()
                # keep original hyphenated types
                if t in counts:
                    counts[t] += 1
                    in_type = t
                    buf = []
                    opener_line = line

                    if t == "you-try":
                        tm = TITLE_ATTR_RE.search(line)
                        if tm:
                            title = tm.group(1).strip()
                            if title:
                                you_try_titles.append(title)
                    continue
            continue

        # inside callout
        if CALLOUT_CLOSE_RE.match(line):
            flush_block()
            continue
        buf.append(line)

    flush_block()
    return counts, blocks, you_try_titles


def snippet_from_blocks(blocks: Dict[str, List[Dict[str, object]]], callout_type: str, limit: int = 2, max_len: int = 120) -> str:
    out: List[str] = []
    for b in blocks.get(callout_type, [])[:limit]:
        content = str(b.get("content", ""))
        for raw in content.splitlines():
            s = clean_snippet_line(raw)
            if not s:
                continue
            if len(s) > max_len:
                s = s[: max_len - 1] + "…"
            out.append(s)
            break
    return " | ".join(out)


def extract_title(lines: List[str]) -> str:
    for line in lines:
        m = TITLE_HEADING_RE.match(line)
        if m:
            return strip_trailing_attr_blocks(m.group(1))
    return ""


def extract_h2_headings(lines: List[str]) -> List[str]:
    hs: List[str] = []
    for line in lines:
        m = H2_HEADING_RE.match(line)
        if m:
            hs.append(strip_trailing_attr_blocks(m.group(1)))
    return hs


def extract_example_count(lines: List[str]) -> int:
    return sum(1 for line in lines if EXAMPLE_RE.match(line))


def parse_file(path: Path) -> Dict[str, object]:
    text = path.read_text(encoding="utf-8", errors="replace")
    lines = text.splitlines(keepends=True)

    unit = parse_unit_from_path(path)
    lesson = parse_lesson_from_filename(path)
    title = extract_title(lines)
    headings = extract_h2_headings(lines)

    counts, blocks, you_try_titles = scan_callouts(lines)

    row: Dict[str, object] = {
        "file": str(path),
        "unit": unit,
        "lesson": lesson,
        "title": title,
        "headings": "|".join(headings),
        "intro_first_sentence": extract_intro_first_sentence([l.rstrip("\n") for l in lines]),
        "example_count": extract_example_count([l.rstrip("\n") for l in lines]),
        "you_try_titles": "|".join(you_try_titles[:8]),
        "callout_counts": counts,
        "remember_snippets": snippet_from_blocks(blocks, "remember"),
        "gotcha_snippets": snippet_from_blocks(blocks, "gotcha"),
        "think_snippets": snippet_from_blocks(blocks, "think"),
    }

    # convenience flat fields for TSV
    for t in CALLOUT_TYPES:
        row[f"{t}_count"] = int(counts.get(t, 0))

    return row


def list_lesson_files(roots: List[Path]) -> List[Path]:
    files: List[Path] = []
    for root in roots:
        if root.is_dir():
            for p in sorted(root.rglob("*.qmd")):
                if is_lesson_file(p):
                    files.append(p)
        elif root.is_file() and root.suffix.lower() == ".qmd":
            if is_lesson_file(root):
                files.append(root)
    return files


def write_tsv(rows: List[Dict[str, object]], out_path: Path) -> None:
    fields = [
        "file",
        "unit",
        "lesson",
        "title",
        "headings",
        "intro_first_sentence",
        "example_count",
        "you-try_count",
        "you-try-m_count",
        "think_count",
        "remember_count",
        "gotcha_count",
        "real-world_count",
        "note_count",
        "you_try_titles",
        "remember_snippets",
        "gotcha_snippets",
        "think_snippets",
    ]

    with out_path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields, delimiter="\t")
        w.writeheader()
        for r in rows:
            w.writerow({k: r.get(k, "") for k in fields})


def write_jsonl(rows: List[Dict[str, object]], out_path: Path) -> None:
    with out_path.open("w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("paths", nargs="+", help="folders or .qmd files to scan, usually chapters")
    ap.add_argument("--out-dir", default=".", help="output directory")
    ap.add_argument("--out-prefix", default="lesson_context", help="output prefix, default lesson_context")
    args = ap.parse_args()

    roots = [Path(p) for p in args.paths]
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    files = list_lesson_files(roots)
    if not files:
        print("No lesson .qmd files found with the current filters.")
        return 1

    rows = [parse_file(p) for p in files]
    # stable order: unit then lesson then file
    def sort_key(r: Dict[str, object]):
        unit = r.get("unit", "")
        lesson = r.get("lesson", "")
        return (int(unit) if str(unit).isdigit() else 999, lesson, str(r.get("file", "")))

    rows.sort(key=sort_key)

    tsv_path = out_dir / f"{args.out_prefix}.tsv"
    jsonl_path = out_dir / f"{args.out_prefix}.jsonl"

    write_tsv(rows, tsv_path)
    write_jsonl(rows, jsonl_path)

    print(f"Wrote {len(rows)} lessons")
    print(f"TSV:   {tsv_path}")
    print(f"JSONL: {jsonl_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
