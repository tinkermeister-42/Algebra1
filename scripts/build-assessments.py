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
    <div class="sub">DHS Algebra 1 &mdash; Unit {unit}</div>
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

    # runs of <br> - four or more means "work here", not a line break
    def brs(m):
        n = m.group(0).lower().count("<br")
        return space(n * 0.55) if n >= 3 else m.group(0)
    text = re.sub(r"(?:\s*<br\s*/?>){3,}", brs, text)

    # the sources' own page breaks
    text = text.replace('<div style="page-break-after: always;"></div>',
                        '<div class="pagebreak"></div>')
    # Quarto column layout -> a plain two-up row
    text = re.sub(r":::\{layout-ncol=2\}", '<div class="columns">', text)
    text = re.sub(r":::\{[^}]*\}", "<div>", text)
    text = re.sub(r"^:::\s*$", "</div>", text, flags=re.M)
    return text


def space(cm):
    return '\n<div class="space" style="height:%.2fcm"></div>\n' % max(cm, 0.4)


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

    tag = ""
    if key_md is not None:
        tag = ' <span class="keytag">ANSWER KEY</span>'
        body += ('\n<div class="answer-key">\n<h2>Answer Key</h2>\n'
                 + pandoc(key_md) + "</div>\n")

    name = os.path.splitext(os.path.basename(path))[0]
    out_dir = os.path.join(OUT, "Unit_%s" % unit)
    os.makedirs(out_dir, exist_ok=True)
    # the sources reach images by a relative path; keep that path working
    img_src = os.path.join(os.path.dirname(path), "images")
    if os.path.isdir(img_src):
        shutil.copytree(img_src, os.path.join(out_dir, "images"), dirs_exist_ok=True)
    out = os.path.join(out_dir, name + ("_KEY" if key_md else "") + ".html")
    open(out, "w", encoding="utf-8").write(SHELL.format(
        title=html.escape(heading + (" — Answer Key" if key_md else "")),
        heading=html.escape(heading), keytag=tag, unit=unit,
        idline="" if key_md else IDLINE, body=body))
    print("built", os.path.relpath(out, ROOT))


def main(argv):
    paths = sorted(glob.glob(os.path.join(SRC, "Unit_*", "*.md")) +
                   glob.glob(os.path.join(SRC, "Unit_*", "*.qmd")))
    if argv:
        paths = [p for p in paths if any(a in os.path.basename(p) for a in argv)]
        if not paths:
            raise SystemExit("no assessment matches %s" % " ".join(argv))
    for p in paths:
        build(p)
        k = os.path.join(KEYS, os.path.splitext(os.path.basename(p))[0] + ".md")
        if os.path.exists(k):
            build(p, open(k, encoding="utf-8").read())


if __name__ == "__main__":
    main(sys.argv[1:])
