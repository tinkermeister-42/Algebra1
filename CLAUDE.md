# Algebra 1 Textbook: Project Context

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
  rebuilding. The handout restates the same problems, so the two drift silently.
- See `guided_notes/README.md` for the shorthand tokens and building blocks

## Assessments
- Sources are the teacher's markdown in `chapters/Assessments/Unit_X/` (`.md`, some `.qmd`)
- **Build:** `python3 scripts/build-assessments.py [name...]` &rarr;
  `assessments/Unit_X/<Name>.html` and `<Name>_KEY.html`
- Answer keys are authored separately in `assessments/keys/<Name>.md` so the
  quiz sources stay exactly as written; a key file is optional
- Self-contained: no JS, no CDN. Math is MathML, converted by pandoc
- **Work space is measured, not trusted.** Sources mark out room three ways
  (`<br>` runs, `\vspace`, raw `{=latex}`) and some not at all, so the builder
  tops every question up: 3cm to work in, 0.8cm if it is answered on a rule in
  its own text, none for a figure or a question stem introducing its parts
- **Unlisted on purpose.** They are copied into the site by `_quarto.yml`
  `resources:` but nothing links to them and they are not in the search index.
  URLs are `/assessments/Unit_X/<Name>.html`
- `/assessments/index.html` lists everything. It is also unlisted, a bookmark
  for the teacher. Built by the same script; a partial build leaves it alone
- **Assessment rhythm:** one quiz about 3-4 lessons into a unit, then a test
  over the whole unit. A second quiz would sit back to back with the test, so
  don't add one (Unit 1 is the exception: eight lessons, two quizzes)
- Every quiz has a matching `*_Quiz_*_Review` at 2-3x the problems
- Assessments that exist **only** as PDF are copied to
  `/assessments/Unit_X/<Name>.pdf`. The teacher's older PDF exports of the
  rest are not served: the HTML prints, and those exports are stale

## Widgets
- Embed: `{{< include /assets/Unit_X/widget.html >}}`
- Math API (from `scripts/inject-custom.html`): `window.setMath(el, tex, display)`, `window.qwTypesetMath(el)`
- **Themes - 5 canonical names:** `classic` (default/flatly-style), `ocean`, `midnight`, `darcula`, `terminal`
- Theme storage key: `qw_theme_v1` in localStorage (no "theme-" prefix)
- Widgets with pickers: prime_factorization_game, slope-intercept-form-game, function_machine_guess
- Widgets without pickers (read default on init only): vertex_form-widget, slope-intercept-form-widget, correlation, slope-widget

## Math
- Inline `$…$`, display `$$…$$` (MathJax 3)
- Step macros: `\stepnote{text}`, `\snplus{3}`, `\snminus{5}`
- Macros defined in `macros.tex` and `mathjax-macros.html`

## Writing Style

**Who is reading this.** About 80% of the students are not native English
speakers. Many read well below grade level, and some have never been to school
before and are placed in Algebra 1 because of their age. Reading is the barrier,
not the mathematics. Every sentence a student has to decode twice is a sentence
that costs them the math.

Write for that reader:

- **Short sentences.** One idea each. Split a sentence before adding a clause
- **Common words.** Prefer "use" to "utilize", "shows" to "demonstrates",
  "same" to "equivalent" outside the glossary term itself
- **No colloquialisms or figurative idioms**, where the literal words do not
  give the meaning: "earns its keep", "comes in handy", "takes forever",
  "falls apart", "gets in the way", "what your gut tells you". Plain phrasal
  verbs ("show up", "figure out") are fine
- **No dash asides.** AI writes "the total goes up - removing a fee is like
  being handed the money" constantly; this teacher almost never does. The fix is
  not a different dash character, it is a different sentence. Split it in two,
  use a comma, or put a short aside in parentheses. Labels in a list take a
  colon ("**Substitution**: replace one variable"). Section headings keep the
  spaced hyphen they already use
- **Lead with the concrete.** A number, a picture, or a story first; the general
  rule after. The money model in 1.1.5 is the pattern to copy
- **Do not let prose carry the math.** If a step matters, it belongs in a
  worked example, a labelled figure, or a fill-in blank, not buried in a
  paragraph

**The mathematics does not get easier.** These students still sit the EOC, and
it is written at full difficulty in dense language. Simplify the sentence, never
the problem: keep the multi-step work, the negatives, the word problems, the
rigour. The goal is that reading stops hiding what a student actually knows.

Because EOC items are wordy, the book should also build that reading up rather
than avoid it: introduce a type of problem in plain language first, then show
the same problem worded the way the test words it.

## Cost/Workflow Preferences
- **No Task/Explore subagents**: use Grep and Glob directly for code searches
- Start a **new session** when switching to a different task area
- Run `/compact` when context grows long (after completing a chunk of work)
- Use **Haiku** (`/model claude-haiku-4-5-20251001`) for simple questions; switch back to Sonnet for complex edits
