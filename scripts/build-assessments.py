#!/usr/bin/env python3
"""Build printable HTML for the quizzes and tests in chapters/Assessments.

The sources are the teacher's own markdown; this only wraps them, so the
assessments stay editable as markdown and the HTML is a build product.

    python3 scripts/build-assessments.py              # build everything
    python3 scripts/build-assessments.py Unit1_Test_A # build just these

Output goes to assessments/Unit_<n>/<Name>.html, plus <Name>_KEY.html for any
assessment that has a key in assessments/keys/<Name>.md.  The pages are
deliberately not linked from anywhere in the book: they are reachable only if
you know the URL.

Math is converted to MathML by pandoc, so a page needs no JavaScript and no
CDN - the same rule the guided notes follow.

An index is written to assessments/index.html listing everything.  It is a
resource like the pages it lists: nothing in the book links to it and it is
not in the search index, so it is a bookmark for the teacher, not a way in for
students.
"""
import glob
import html
import os
import re
import shutil
import subprocess
import sys

ROOT = os.path.normpath(os.path.join(os.path.dirname(__file__), ".."))
SRC = os.path.join(ROOT, "chapters", "Assessments")
OUT = os.path.join(ROOT, "assessments")
KEYS = os.path.join(OUT, "keys")

SHELL = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<link rel="stylesheet" href="../assets/assessments.css">
</head>
<body>
<section class="sheet">

  <div class="masthead">
    <h1>{heading}{keytag}</h1>
    <div class="sub">DHS Algebra 1 - Unit {unit}</div>
{idline}  </div>

{body}
</section>
</body>
</html>
"""

IDLINE = """    <div class="idline"><span>Name</span><span class="small">Date</span>\
<span class="small">Period</span></div>
"""


def pandoc(text):
    p = subprocess.run(["pandoc", "-f", "markdown+raw_html", "-t", "html",
                        "--mathml", "--wrap=none"],
                       input=text, capture_output=True, text=True)
    if p.returncode:
        raise SystemExit("pandoc failed:\n" + p.stderr)
    return p.stdout


def prepare(text):
    """Turn the three different ways the sources ask for work space into one.

    They use runs of <br>, LaTeX \\vspace, and raw ```{=latex} blocks; the
    first survives conversion, the other two would either print literally or
    vanish.  All three become a .space div of a measured height."""
    # ```{=latex} ... ``` blocks: keep the \vspace inside, drop the rest
    def latex_block(m):
        cm = sum(float(v) for v in re.findall(r"\\vspace\{([\d.]+)cm\}", m.group(1)))
        brk = "\\newpage" in m.group(1)
        out = ('\n<div class="pagebreak"></div>\n' if brk else "")
        return out + (space(cm) if cm else "")

    text = re.sub(r"```\{=latex\}(.*?)```", latex_block, text, flags=re.S)
    text = re.sub(r"\\vspace\{([\d.]+)cm\}", lambda m: space(float(m.group(1))), text)

    # runs of <br> - in these sources even a doubled break after a question
    # means "room to work", not a line break
    def brs(m):
        return space(m.group(0).lower().count("<br") * 0.6)
    text = re.sub(r"(?:\s*<br\s*/?>){2,}", brs, text)

    # the sources' own page breaks
    text = text.replace('<div style="page-break-after: always;"></div>',
                        '<div class="pagebreak"></div>')
    # Quarto column layout -> a plain two-up row
    text = re.sub(r":::\{layout-ncol=2\}", '<div class="columns">', text)
    text = re.sub(r":::\{[^}]*\}", "<div>", text)
    text = re.sub(r"^:::\s*$", "</div>", text, flags=re.M)
    return text


def space(cm):
    # min-height, not height: on a key the answer is written into this block,
    # and a long one must push the page down rather than run over what follows
    return '\n<div class="space" style="min-height:%.2fcm"></div>\n' % max(cm, 0.4)


# What a question needs underneath it if the source did not say.  Some sources
# mark out room and some leave it entirely to the page, so the room is measured
# after conversion and topped up rather than trusted.
WORK_CM = 3.0        # anything you have to work out
BLANK_CM = 0.8       # a question answered on a rule in its own text
SPACE_RE = re.compile(r'(?:min-)?height:([\d.]+)cm')
# a question starts at a list item or at a bold "12." at the head of a paragraph
QUESTION_RE = re.compile(r'<li>|<p><strong>\d+\.')


def ensure_room(body):
    """Top every question up to a workable amount of space.

    A question that is answered on a rule inside its own text needs very
    little; one that says solve, simplify or explain needs room to show the
    work; one that already carries a figure needs none."""
    marks = [m.start() for m in QUESTION_RE.finditer(body)]
    if not marks:
        return body
    depth = list_depth(body)
    out = [body[:marks[0]]]
    for i, start in enumerate(marks):
        end = marks[i + 1] if i + 1 < len(marks) else len(body)
        chunk = body[start:end]
        # A sub-part is measured on its own content only.  Room that sits
        # after the part belongs to the question as a whole, and counting it
        # would leave the last part with no room at all.  A top-level question
        # keeps the old reading: room after its </li> is still its own.
        j = own_li_end(chunk) if chunk.startswith("<li>") and depth[start] > 1 else -1
        mine = chunk[:j] if j != -1 else chunk
        have = sum(float(v) for v in SPACE_RE.findall(mine))
        # a stem that only introduces its own a/b/c parts gets nothing: the
        # room belongs under the parts, not between them and the question
        opens = len(re.findall(r"<[ou]l[ >]", mine)) - len(re.findall(r"</[ou]l>", mine))
        if opens > 0 or "<img" in mine or "<table" in mine:
            want = 0.0
        elif re.search(r"_{3,}", mine):
            want = BLANK_CM
        else:
            want = WORK_CM
        if have < want:
            pad = space(want - have)
            k = j if j != -1 else chunk.rfind("</li>")
            chunk = chunk[:k] + pad + chunk[k:] if k != -1 else chunk + pad
        out.append(chunk)
    return "".join(out)


def list_depth(body):
    """How deep in <ol>/<ul> every offset of the body is."""
    out, depth, at = {}, 0, 0
    events = []
    for m in re.finditer(r"<(?:ol|ul)\b[^>]*>|</(?:ol|ul)>", body):
        events.append((m.start(), m.end(), m.group(0).startswith("</")))
    class D(dict):
        def __missing__(self, pos):
            d = 0
            for s, e, closing in events:
                if s >= pos:
                    break
                d += -1 if closing else 1
            return d
    return D()


def own_li_end(chunk):
    """Where the list item this chunk opens with closes, skipping nested ones."""
    depth = 0
    for m in re.finditer(r"<li>|</li>", chunk):
        if m.group(0) == "<li>":
            depth += 1
        else:
            depth -= 1
            if depth == 0:
                return m.start()
    return -1


ANS_SPLIT = "<!--ANSSPLIT-->"


def split_key(key_md):
    """The key markdown as {question number: markdown for that answer}.

    A key is a numbered list, one entry per question, so an entry runs from
    its own "12." to the next one at the start of a line."""
    starts = [(m.start(), int(m.group(1)))
              for m in re.finditer(r"^(\d+)\.[ \t]", key_md, re.M)]
    if not starts:
        return {}, key_md
    out, before = {}, key_md[:starts[0][0]].strip()
    for i, (pos, n) in enumerate(starts):
        end = starts[i + 1][0] if i + 1 < len(starts) else len(key_md)
        out[n] = re.sub(r"^\d+\.[ \t]+", "", key_md[pos:end].strip())
    return out, before


def render_answers(answers):
    """One pandoc run for the lot, split back apart on a marker."""
    if not answers:
        return {}
    nums = sorted(answers)
    joined = ("\n\n" + ANS_SPLIT + "\n\n").join(answers[n] for n in nums)
    parts = pandoc(joined).split(ANS_SPLIT)
    if len(parts) != len(nums):       # a stray marker collision; give up cleanly
        return {}
    return {n: parts[i].strip() for i, n in enumerate(nums)}


def split_parts(md):
    """An answer written "a. ... b. ... c. ..." split into its parts.

    Returns None unless the letters run a, b, c... in order, which keeps an
    "e.g." or a stray initial from being mistaken for a part label."""
    marks = [(m.start(), m.end(), m.group(1))
             for m in re.finditer(r"(?<![A-Za-z0-9])([a-h])\.[ \t]", md)]
    if len(marks) < 2:
        return None
    for k, (_, _, letter) in enumerate(marks):
        if letter != chr(ord("a") + k):
            return None
    out = []
    for k, (_, end, _) in enumerate(marks):
        stop = marks[k + 1][0] if k + 1 < len(marks) else len(md)
        out.append(md[end:stop].strip().rstrip("&nbsp;").strip())
    return out


def part_blanks(body, start, end):
    """The blank belonging to each lettered part of one question.

    Only a blank inside a part's own list item counts.  A question often also
    has room after its parts, and pairing an answer with that would push every
    part's answer one place along."""
    out, depth, here = [], 0, None
    tag = re.compile(r'<(?:ol|ul)\b[^>]*>|</(?:ol|ul)>|<li>|</li>'
                     r'|<div class="space"[^>]*>\s*</div>')
    for m in tag.finditer(body, start, end):
        s = m.group(0)
        if s.startswith("<ol") or s.startswith("<ul"):
            depth += 1
        elif s in ("</ol>", "</ul>"):
            depth -= 1
        elif s == "<li>":
            if depth == 1:
                here = None
                out.append(None)
        elif s == "</li>":
            pass
        elif depth == 1 and out and out[-1] is None:
            out[-1] = (m.start(), m.end(),
                       re.match(r'<div class="space"[^>]*>', s).group(0))
    return out if out and all(b is not None for b in out) else []


def questions(body):
    """The span of each numbered question, so its answer can go inside it.

    Three shapes come out of pandoc: a bold "12." heading the question, a real
    ordered list, which pandoc restarts with start="12" whenever the source
    breaks the numbering, and, on a paper whose sections are the questions, an
    "## 12." heading.  Sub-parts are an <ol type="a"> inside one of those, and
    never a question of their own."""
    spans = {}
    tag = re.compile(r'<(ol|ul)\b[^>]*>|</(ol|ul)>|<li>|</li>'
                     r'|(?:<p>)?<strong>(\d+)\.(?!\d)')
    stack, pending = [], []
    for m in tag.finditer(body):
        s = m.group(0)
        if m.group(3):                            # a bold "12." question
            if not stack:
                spans[int(m.group(3))] = [m.start(), None]
            continue
        if s.startswith("<ol") or s.startswith("<ul"):
            start = re.search(r'start="(\d+)"', s)
            typ = re.search(r'type="([^"]+)"', s)
            numbered = s.startswith("<ol") and (not typ or typ.group(1) == "1")
            stack.append([numbered, int(start.group(1)) if start else 1])
            continue
        if s in ("</ol>", "</ul>"):
            if stack:
                stack.pop()
            continue
        if s == "<li>":
            if len(stack) == 1 and stack[0][0]:
                pending.append((stack[0][1], m.end()))
                stack[0][1] += 1
            continue
        if s == "</li>":
            if len(stack) == 1 and pending:
                n, at = pending.pop()
                spans[n] = [at, m.start()]

    heads = r'(?:<p>)?<strong>\d+\.(?!\d)|<h2\b'
    if not spans:
        # a paper whose sections are its questions: "## 3. Fractions"
        for m in re.finditer(r'<h2\b[^>]*>(\d+)\.(?!\d)', body):
            spans[int(m.group(1))] = [m.start(), None]
        heads = r'<h2\b'

    # a question with no list to close runs until the next one starts
    marks = [m.start() for m in re.finditer(heads, body)] + [len(body)]
    for n, span in list(spans.items()):
        if span[1] is None:
            span[1] = next(x for x in marks if x > span[0])
    return spans


def inline_key(body, key_md):
    """Answer the paper in the space provided.

    The key keeps the quiz's own work space and the answer is written into it,
    so a key sits page for page beside a student's copy.  Where a question has
    lettered parts and each part has its own blank, each part is answered in
    its own blank."""
    answers, preamble = split_key(key_md)
    spans = questions(body)

    # one pandoc run for everything: whole answers, and the parts of any
    # answer whose letters line up with that question's blanks
    space_re = re.compile(r'(<div class="space"[^>]*>)\s*</div>')
    jobs, plan = [], []
    for n in sorted(answers):
        if n not in spans:
            continue
        start, end = spans[n]
        blanks = [(m.start(), m.end(), m.group(1))
                  for m in space_re.finditer(body, start, end)]
        lettered = part_blanks(body, start, end)
        parts = split_parts(answers[n]) if lettered else None
        if parts and len(parts) == len(lettered):
            for blank, md in zip(lettered, parts):
                plan.append((blank, len(jobs)))
                jobs.append(md)
        else:
            plan.append((blanks[0] if blanks else (end, end, None), len(jobs)))
            jobs.append(answers[n])

    rendered = render_answers(dict(enumerate(jobs)))
    if not rendered and jobs:                     # marker collision; fall back
        plan = []

    edits = []
    for (a, b, open_tag), k in plan:
        ans = '<div class="ans">%s</div>' % rendered[k]
        # written inside the blank, so the key keeps the quiz's own layout
        edits.append((a, b, open_tag + ans + "</div>" if open_tag
                      else "\n" + ans + "\n"))
    for a, b, chunk in sorted(edits, reverse=True):
        body = body[:a] + chunk + body[b:]

    placed = {n for n in answers if n in spans}
    left = [n for n in sorted(answers) if n not in placed]
    if preamble or left:
        rest = render_answers({n: answers[n] for n in left})
        body += ('\n<div class="answer-key">\n<h2>Answer Key</h2>\n'
                 + (pandoc(preamble) if preamble else "")
                 + "\n".join('<div class="ans"><b>%d.</b> %s</div>' % (n, rest[n])
                              for n in sorted(rest)) + "</div>\n")
    return body


def meta(path, text):
    """Title from the file's own H1, unit from the folder."""
    m = re.search(r"^#\s+(.+?)\s*$", text, re.M)
    head = m.group(1) if m else os.path.basename(path)
    head = re.sub(r"\\([_&])", r"\1", head).replace("**", "")
    unit = re.search(r"Unit_(\d)", path)
    return head, (unit.group(1) if unit else "?")


def strip_name_line(text):
    """The masthead carries the name/date rule, so drop the source's own."""
    return re.sub(r"^\*\*Name:?\*?\*?[^\n]*$", "", text, flags=re.M)


def build(path, key_md=None):
    text = open(path, encoding="utf-8").read()
    heading, unit = meta(path, text)
    body = text.split("\n", 1)[1] if text.startswith("#") else text
    body = pandoc(prepare(strip_name_line(body)))
    body = re.sub(r"^\s*<hr\s*/?>\s*", "", body)   # the masthead already rules off

    body = ensure_room(body)

    tag = ""
    if key_md is not None:
        tag = ' <span class="keytag">ANSWER KEY</span>'
        body = inline_key(body, key_md)

    name = os.path.splitext(os.path.basename(path))[0]
    out_dir = os.path.join(OUT, "Unit_%s" % unit)
    os.makedirs(out_dir, exist_ok=True)
    # the sources reach images by a relative path; keep that path working
    img_src = os.path.join(os.path.dirname(path), "images")
    if os.path.isdir(img_src):
        shutil.copytree(img_src, os.path.join(out_dir, "images"), dirs_exist_ok=True)
    out = os.path.join(out_dir, name + ("_KEY" if key_md else "") + ".html")
    open(out, "w", encoding="utf-8").write(SHELL.format(
        title=html.escape(heading + (" - Answer Key" if key_md else "")),
        heading=html.escape(heading), keytag=tag, unit=unit,
        idline="" if key_md else IDLINE, body=body))
    print("built", os.path.relpath(out, ROOT))



INDEX_SHELL = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Assessments - DHS Algebra 1</title>
<link rel="stylesheet" href="assets/assessments.css">
<style>
  .sheet {{ width: 8in; }}
  .idx {{ width: 100%; border-collapse: collapse; margin: 4px 0 18px; }}
  .idx th, .idx td {{ border: 0; border-bottom: 1px solid var(--faint);
                      padding: 5px 8px; text-align: left; }}
  .idx th {{ background: none; font-size: 9.5pt; letter-spacing: .04em;
             text-transform: uppercase; color: #555; border-bottom: 1.5px solid var(--ink); }}
  .idx td.k {{ text-align: right; white-space: nowrap; }}
  .idx a {{ color: var(--accent); text-decoration: none; }}
  .idx a:hover {{ text-decoration: underline; }}
  .idx a.key {{ color: var(--key); }}
  .note {{ font-size: 10pt; color: #555; margin: 0 0 14px; }}
  @media print {{ .sheet {{ width: auto; }} }}
</style>
</head>
<body>
<section class="sheet">
  <div class="masthead">
    <h1>Assessments</h1>
    <div class="sub">DHS Algebra 1 - quizzes, tests and answer keys</div>
  </div>
  <p class="note">Nothing in the book links here. Bookmark this page.
  Every sheet is laid out for letter paper - use your browser's
  <b>Print</b> command, and choose <i>Save as PDF</i> for a digital copy.</p>
{body}
</section>
</body>
</html>
"""


def write_index(built):
    """One page listing every assessment, for the teacher to bookmark."""
    rows = {}
    for unit, name, has_key in built:
        rows.setdefault(unit, []).append((name, has_key))

    body = []
    for unit in sorted(rows):
        body.append("  <h2>Unit %s</h2>\n  <table class=\"idx\">" % unit)
        body.append("    <tr><th>Assessment</th><th>Answer key</th></tr>")
        for name, has_key in sorted(rows[unit]):
            key = ('<a class="key" href="Unit_%s/%s_KEY.html">key</a>' % (unit, name)
                   if has_key else " - ")
            body.append('    <tr><td><a href="Unit_%s/%s.html">%s</a></td>'
                        '<td class="k">%s</td></tr>' % (unit, name, name, key))
        body.append("  </table>")

    # Only the ones with no markdown source.  The rest are the teacher's own
    # older exports of assessments that now build to HTML, and they predate
    # every correction made since - listing them would hand out stale papers.
    have = {n.lower() for _, n, _ in built}
    pdfs = []
    for f in sorted(glob.glob(os.path.join(SRC, "Unit_*", "*.pdf"))):
        if os.path.splitext(os.path.basename(f))[0].lower() in have:
            continue
        unit = re.search(r"Unit_(\d)", f).group(1)
        dest = os.path.join(OUT, "Unit_%s" % unit, os.path.basename(f))
        os.makedirs(os.path.dirname(dest), exist_ok=True)
        shutil.copyfile(f, dest)
        pdfs.append((unit, os.path.basename(f)))
    if pdfs:
        body.append("  <h2>PDF only</h2>")
        body.append("  <p class=\"note\">These exist only as PDF, so there is no "
                    "HTML version and no key.</p>")
        body.append("  <table class=\"idx\">")
        for unit, base in pdfs:
            body.append('    <tr><td><a href="Unit_%s/%s">%s</a></td>'
                        '<td class="k"> - </td></tr>' % (unit, base, base))
        body.append("  </table>")

    out = os.path.join(OUT, "index.html")
    open(out, "w", encoding="utf-8").write(INDEX_SHELL.format(body="\n".join(body)))
    print("built", os.path.relpath(out, ROOT))


def main(argv):
    paths = sorted(glob.glob(os.path.join(SRC, "Unit_*", "*.md")) +
                   glob.glob(os.path.join(SRC, "Unit_*", "*.qmd")))
    if argv:
        paths = [p for p in paths if any(a in os.path.basename(p) for a in argv)]
        if not paths:
            raise SystemExit("no assessment matches %s" % " ".join(argv))
    built = []
    for p in paths:
        build(p)
        name = os.path.splitext(os.path.basename(p))[0]
        k = os.path.join(KEYS, name + ".md")
        has_key = os.path.exists(k)
        if has_key:
            build(p, open(k, encoding="utf-8").read())
        built.append((re.search(r"Unit_(\d)", p).group(1), name, has_key))
    if not argv:                      # a partial build must not shrink the index
        write_index(built)


if __name__ == "__main__":
    main(sys.argv[1:])
