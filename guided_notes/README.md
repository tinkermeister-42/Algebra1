# Guided Notes

Print-ready, fill-in-the-blank handouts — one per lesson. Each file is the lesson
with the prose stripped out: objectives, key points as blanks, every example and
practice problem, and blank number lines / work space for students to fill in.

## Using them

Open the `.html` file in a browser and **Print → Save as PDF** (Letter, default
margins). The print stylesheet drops the on-screen page shadow, keeps example
boxes from splitting across a page break, and starts the Practice section on a
fresh page.

## Conventions

- **Self-contained** — inline CSS, inline SVG, no JavaScript, no external assets
  (the one exception is a lesson image pulled from `/images/...` when the problem
  refers to a specific figure).
- **Number lines** are `<symbol>` defs reused with `<use>`:
  - `#nl` — labelled −10 to 10
  - `#nl-blank` — same ticks, unlabelled (student chooses the scale)
- **Blanks** — `<span class="b">` with size modifiers `s` / `m` / `l` / `xl`.
- **Blocks** — `.keys` (key points), `.ex` (a problem + work space), `.box.warn`
  (a "gotcha"), `.box.tint` (objectives, notes-to-self).
- **Work space** — set with `.h08` / `.h1` / `.h13` / `.h16` / `.h2` on `.work`
  (min-height in inches). Nothing is pre-solved.

## Files

- `Unit_1/1.1_Integers_and_Number_Lines.html`
