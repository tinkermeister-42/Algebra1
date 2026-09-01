#!/usr/bin/env python3
"""Fail if a page in _book points at a file _book does not carry.

The handouts and the assessments are static resources, so Quarto never looks
inside them: a figure referenced only from one of those pages is not copied
unless _quarto.yml names it, and the page ships with a broken image and no
warning anywhere.  This is the warning.

    python3 scripts/check-site-assets.py
"""
import glob
import os
import re
import sys

ROOT = os.path.normpath(os.path.join(os.path.dirname(__file__), ".."))
BOOK = os.path.join(ROOT, "_book")
SRC_RE = re.compile(r'(?:src|href)="([^"#?:]+\.(?:png|jpe?g|svg|gif|pdf|css|js))"')


def main():
    pages = (glob.glob(os.path.join(BOOK, "guided_notes", "Unit_*", "*.html")) +
             glob.glob(os.path.join(BOOK, "assessments", "**", "*.html"), recursive=True))
    if not pages:
        sys.exit("no built pages found - run `quarto render` first")

    missing = []
    for page in pages:
        here = os.path.dirname(page)
        for ref in SRC_RE.findall(open(page, encoding="utf-8").read()):
            if ref.startswith(("http", "//", "data:")):
                continue
            target = os.path.normpath(os.path.join(here, ref))
            if not os.path.exists(target):
                missing.append((os.path.relpath(page, BOOK), ref))

    if missing:
        print("Missing from _book:", file=sys.stderr)
        for page, ref in sorted(set(missing)):
            print("  %-58s -> %s" % (page, ref), file=sys.stderr)
        sys.exit("%d broken reference(s); add them to _quarto.yml resources"
                 % len(set(missing)))
    print("site assets OK - %d pages, every reference resolves" % len(pages))


if __name__ == "__main__":
    main()
