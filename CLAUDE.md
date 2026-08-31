# Algebra 1 Textbook — Project Context

## Build & Deploy
- **Render:** `quarto render --to html`
- **Deploy:** `./deploy.sh` (git worktree → gh-pages branch)
- **Watch assets:** `./scripts/watch-assets.sh` (run alongside `quarto preview`)

## Structure
```
chapters/Unit_1…6/   # Lessons: #.#_Topic.qmd, index.qmd, Review.qmd
chapters/Interactive/ # Gamified/exploratory lessons
assets/Unit_1…6/     # Standalone HTML widgets (included via {{< include >}})
scripts/             # JS helpers, Lua filters, build scripts
styles/              # CSS files
_extensions/         # glossary, headings
glossary.qmd         # Source → auto-built glossary.json on render
chapters/Assessments/ # Quiz & test sources; built to assessments/ (unlisted)
_quarto.yml          # Quarto config (Flatly theme, MathJax, custom CSS/JS)
```

## Callout Types
| Class | Purpose |
|---|---|
| `.objectives` | Learning objectives (checkboxes) |
| `.vocab` | Vocabulary |
| `.remember` | Key facts (red) |
| `.real-world` | Applications (teal) |
| `.you-try` | Practice + collapsible solution (blue) |
| `.you-try-m` | Multi-part practice (no collapse) |
| `.think` | Reflective prompt + collapsible answer (purple) |
| `.gotcha` | Common mistakes (orange) |
| `.answers` / `.answer` | Answer keys (green) |
| `.note` | Info note (purple) |

Syntax: `:::{.callout-type title="Title"} … :::`

## Glossary
- Link: `{{< glink "term" >}}` or `{{< glink slug="slug" text="display" >}}`
- Add terms to `glossary.qmd`: H3 heading with `{#slug}`, first paragraph = tooltip text
- Format: Definition → optional `> **Example:** …` → optional `**See Also:** …`

## Guided Notes
- Printable fill-in handout per lesson: `guided_notes/Unit_X/#.#_Slug.html`
- **Edit** the body fragment in `guided_notes/src/#.#.html`, then rebuild:
  `python3 scripts/build-guided-notes.py [lesson...]`
- Shared styles/figures in `guided_notes/assets/`; regenerate figures with
  `python3 scripts/make-guided-notes-assets.py`
- Self-contained: no JS, no CDN, math is HTML/CSS. Figures are `<img>` so they print.
- **Teacher keys:** answers go in the same fragment wrapped in `{{a}}`…`{{/a}}`;
  builder emits `#.#_Slug_KEY.html` with the answers in red (`.ans-key`)
- Each lesson `.qmd` links to its handout via a `.guided-notes-link` div above `{{< warmup >}}`
- **Lesson and handout are one change.** Editing an example, a practice problem, or an
  answer in a lesson `.qmd` means editing `guided_notes/src/#.#.html` to match and
  rebuilding — the handout restates the same problems, so the two drift silently.
- See `guided_notes/README.md` for the shorthand tokens and building blocks

## Assessments
- Sources are the teacher's markdown in `chapters/Assessments/Unit_X/` (`.md`, some `.qmd`)
- **Build:** `python3 scripts/build-assessments.py [name...]` &rarr;
  `assessments/Unit_X/<Name>.html` and `<Name>_KEY.html`
- Answer keys are authored separately in `assessments/keys/<Name>.md` so the
  quiz sources stay exactly as written; a key file is optional
- Self-contained: no JS, no CDN. Math is MathML, converted by pandoc
- **Unlisted on purpose.** They are copied into the site by `_quarto.yml`
  `resources:` but nothing links to them and they are not in the search index.
  URLs are `/assessments/Unit_X/<Name>.html`
- `/assessments/index.html` lists everything &mdash; also unlisted, a bookmark
  for the teacher. Built by the same script; a partial build leaves it alone
- Assessments that exist only as PDF are exposed at
  `/chapters/Assessments/Unit_X/<Name>.pdf`

## Widgets
- Embed: `{{< include /assets/Unit_X/widget.html >}}`
- Math API (from `scripts/inject-custom.html`): `window.setMath(el, tex, display)`, `window.qwTypesetMath(el)`
- **Themes — 5 canonical names:** `classic` (default/flatly-style), `ocean`, `midnight`, `darcula`, `terminal`
- Theme storage key: `qw_theme_v1` in localStorage (no "theme-" prefix)
- Widgets with pickers: prime_factorization_game, slope-intercept-form-game, function_machine_guess
- Widgets without pickers (read default on init only): vertex_form-widget, slope-intercept-form-widget, correlation, slope-widget

## Math
- Inline `$…$`, display `$$…$$` (MathJax 3)
- Step macros: `\stepnote{text}`, `\snplus{3}`, `\snminus{5}`
- Macros defined in `macros.tex` and `mathjax-macros.html`

## Cost/Workflow Preferences
- **No Task/Explore subagents** — use Grep and Glob directly for code searches
- Start a **new session** when switching to a different task area
- Run `/compact` when context grows long (after completing a chunk of work)
- Use **Haiku** (`/model claude-haiku-4-5-20251001`) for simple questions; switch back to Sonnet for complex edits
