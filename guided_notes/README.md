# Guided Notes

A printable, fill-in handout for every lesson in the book — the lesson with the prose
stripped out. Objectives, a warm-up, the key ideas as fill-in-the-blank statements, and
every example and practice problem with room to work them out. Nothing is pre-solved.

## Using them

Open a handout in a browser and **Print → Save as PDF** (Letter, default margins). The
print stylesheet drops the on-screen page shadow and the "back to the lesson" link, keeps
example boxes from splitting across a page break, and starts the Practice section on a
fresh page.

Online they live alongside the book: every lesson links to its handout just above the
warm-up, and `chapters/Supplemental/guided_notes.qmd` lists all of them.

## Layout

```
guided_notes/
  src/<lesson>.html      # what you edit — one body fragment per lesson
  assets/                # shared stylesheet + SVG figures
  Unit_<n>/              # generated handouts (committed; do not hand-edit)
```

## Editing a handout

Edit the fragment in `src/`, then rebuild:

```bash
python3 scripts/build-guided-notes.py          # all lessons
python3 scripts/build-guided-notes.py 3.4 3.5  # just these
```

The builder wraps each fragment in the shared page shell (head, masthead, name/date line)
using the metadata comment at the top of the fragment.

To change the shared figures — number lines, coordinate grids, factor trees — edit
`scripts/make-guided-notes-assets.py` and run it.

## Conventions

- **Self-contained** — no JavaScript and no CDN. Math is plain HTML/CSS, so a handout
  renders the same offline as online.
- **Figures print** — they are `<img>` elements, not CSS backgrounds, so they survive a
  browser printing with "background graphics" turned off. Nothing in the design depends
  on a printed background: structure comes from borders and weight.

### Shorthands available in a fragment

| Token | Renders |
|---|---|
| `{{nl}}` | number line labelled −10 to 10 |
| `{{nl-blank}}` | same ticks, unlabelled (student picks the scale) |
| `{{nl-11}}` | coarser blank number line, 11 ticks |
| `{{grid}}` `{{grid-sm}}` `{{grid-lg}}` | coordinate plane, −10 to 10 |
| `{{grid-blank}}` | coordinate plane with no axis numbers |
| `{{grid-q1}}` | first-quadrant grid |
| `{{f a/b}}` | stacked fraction (the parts may contain markup) |
| `{{break}}` | page break |
| `{{practice-head}}` | page break + the Practice part header with a name line |

### Building blocks

- `.keys` — key points for a section
- `.ex` with `.q` (the prompt) and `.work` (the space to work in)
- `.box.warn` — a "gotcha"; `.box.tint` — objectives, reminders, notes-to-self
- `.b` — a fill-in blank, sized with `s` / `m` / `l` / `xl`
- `table.steps` — step-and-reason scaffold; `table.fill` — small table to complete;
  `table.area` — blank area model
- `.sys` — a braced system of equations
- Work-space height on `.work` or `.tallbox`: `.h05` `.h08` `.h1` `.h13` `.h16` `.h2` `.h25`
  (inches)
