#!/usr/bin/env python3
"""Build the printable guided-notes handouts.

Each lesson's content lives in guided_notes/src/<lesson>.html as a body
fragment with a small metadata header.  This script wraps every fragment in
the shared page shell (head, MathJax, masthead, footer) and writes the
finished handout to guided_notes/Unit_<n>/<lesson>_<Slug>.html.

Answers live in the same fragment, wrapped in {{a}}...{{/a}}.  The student
handout drops them; the teacher key renders them in red.  A key is written
only for lessons whose fragment actually contains answers.

    python3 scripts/build-guided-notes.py            # build everything
    python3 scripts/build-guided-notes.py 3.4 3.5    # build just these
    python3 scripts/build-guided-notes.py --keys-only
"""
import glob
import os
import re
import sys

ROOT = os.path.normpath(os.path.join(os.path.dirname(__file__), ".."))
SRC = os.path.join(ROOT, "guided_notes", "src")
OUT = os.path.join(ROOT, "guided_notes")

SHELL = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Guided Notes {lesson} — {title}{title_suffix}</title>
<link rel="stylesheet" href="../assets/guided-notes.css">
</head>
<body>
<section class="sheet">

  <div class="masthead">
    <a class="backlink" href="../../chapters/Unit_{unit}/{lesson}_{slug}.html">&larr; back to the lesson</a>
    <h1>{lesson} &nbsp;{title}</h1>
    <div class="sub">Guided Notes &mdash; Unit {unit}: {unit_title} &mdash; DHS Algebra 1</div>
    {idline}
  </div>

{body}
</section>
</body>
</html>
"""

# Lightweight shorthands so the fragments stay readable.  Expanded here.
SHORTHAND = {
    "{{nl}}":       '<img class="nl" src="../assets/nl.svg" alt="number line from -10 to 10">',
    "{{nl-blank}}": '<img class="nl" src="../assets/nl-blank.svg" alt="blank number line">',
    "{{nl-11}}":    '<img class="nl" src="../assets/nl-blank-11.svg" alt="blank number line">',
    "{{grid}}":     '<img class="grid" src="../assets/grid.svg" alt="coordinate grid">',
    "{{grid-sm}}":  '<img class="grid sm" src="../assets/grid.svg" alt="coordinate grid">',
    "{{grid-lg}}":  '<img class="grid lg" src="../assets/grid.svg" alt="coordinate grid">',
    "{{grid-blank}}": '<img class="grid" src="../assets/grid-blank.svg" alt="blank coordinate grid">',
    "{{grid-q1}}":  '<img class="grid" src="../assets/grid-q1.svg" alt="first quadrant grid">',
    "{{break}}":    '<div class="pagebreak"></div>',
}

HEADER_RE = re.compile(r"\A<!--(.*?)-->\s*", re.S)
# {{a}}...{{/a}} marks answer content: dropped from the student handout,
# shown in red on the teacher key.
ANS_RE = re.compile(r"\{\{a\}\}(.*?)\{\{/a\}\}", re.S)
ANS_LINE_RE = re.compile(r"^[ \t]*\{\{a\}\}.*?\{\{/a\}\}[ \t]*\n", re.S | re.M)
# an answer holding block-level markup needs a block wrapper, not a <span>
BLOCK_RE = re.compile(r"<(table|div|p|ul|ol|h[1-6])\b", re.I)

IDLINE = ('<div class="idline"><span>Name</span>'
          '<span class="small">Date</span><span class="small">Period</span></div>')
KEYLINE = '<div class="keybadge">Teacher Key &mdash; answers in red</div>'


def _drop_answers(body):
    # an answer sitting alone on its line takes the whole line with it, so the
    # student handout is byte-identical to one built from a fragment with no
    # answers in it at all
    return ANS_RE.sub("", ANS_LINE_RE.sub("", body))


def _show_answers(body):
    def repl(m):
        inner = m.group(1)
        tag = "div" if BLOCK_RE.search(inner) else "span"
        return '<%s class="ans-key">%s</%s>' % (tag, inner, tag)
    return ANS_RE.sub(repl, body)
# {{f 3/4}} -> a stacked fraction.  The parts may contain markup, so the
# dividing slash is the first one that is not part of a "</" or "/>" tag.
FRAC_RE = re.compile(r"\{\{f (.+?)\}\}", re.S)


def _fraction(match):
    body = match.group(1)
    for i, ch in enumerate(body):
        if ch != "/":
            continue
        if i > 0 and body[i - 1] == "<":       # closing tag, e.g. </var>
            continue
        if i + 1 < len(body) and body[i + 1] == ">":   # self-closing tag
            continue
        return ('<span class="f"><b>%s</b><b>%s</b></span>'
                % (body[:i].strip(), body[i + 1:].strip()))
    raise SystemExit("no dividing slash in {{f %s}}" % body)


def parse(path):
    raw = open(path).read()
    m = HEADER_RE.match(raw)
    if not m:
        raise SystemExit(f"{path}: missing metadata header comment")
    meta = {}
    for line in m.group(1).strip().splitlines():
        if ":" in line:
            k, v = line.split(":", 1)
            meta[k.strip()] = v.strip()
    for key in ("lesson", "title", "unit", "unit_title", "slug"):
        if key not in meta:
            raise SystemExit(f"{path}: metadata is missing '{key}'")
    return meta, raw[m.end():]


def build(path, key=False):
    """Render one fragment.  key=True produces the teacher answer key."""
    meta, body = parse(path)
    body = _show_answers(body) if key else _drop_answers(body)
    for token, html in SHORTHAND.items():
        body = body.replace(token, html)
    body = FRAC_RE.sub(_fraction, body)
    # a practice section always starts on a fresh page, with its own name line
    body = body.replace("{{practice-head}}",
                        '<div class="pagebreak"></div>\n'
                        '  <div class="parthead"><b>%s %s &mdash; Practice</b>%s</div>'
                        % (meta["lesson"], meta["title"],
                           "" if key else '<span class="nm">Name</span>'))
    page = SHELL.format(body=body.rstrip() + "\n",
                        title_suffix=" (Teacher Key)" if key else "",
                        idline=KEYLINE if key else IDLINE,
                        **meta)
    unit_dir = os.path.join(OUT, "Unit_%s" % meta["unit"])
    os.makedirs(unit_dir, exist_ok=True)
    dest = os.path.join(unit_dir, "%s_%s%s.html"
                        % (meta["lesson"], meta["slug"], "_KEY" if key else ""))
    with open(dest, "w") as f:
        f.write(page)
    return os.path.relpath(dest, ROOT)


def has_answers(path):
    return bool(ANS_RE.search(open(path).read()))


if __name__ == "__main__":
    args = sys.argv[1:]
    keys_only = "--keys-only" in args
    wanted = set(a for a in args if not a.startswith("--"))
    made, keys, no_key = [], [], []
    for path in sorted(glob.glob(os.path.join(SRC, "*.html"))):
        stem = os.path.splitext(os.path.basename(path))[0]
        if wanted and stem not in wanted:
            continue
        if not keys_only:
            made.append(build(path))
        if has_answers(path):
            keys.append(build(path, key=True))
        else:
            no_key.append(stem)
    for m in made + keys:
        print("built", m)
    print("%d handout(s), %d teacher key(s)" % (len(made), len(keys)))
    if no_key:
        print("no answers yet (no key written): %s" % " ".join(sorted(no_key)))
