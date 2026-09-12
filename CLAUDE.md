# Algebra 1 Textbook: Project Context

## Build & Deploy
- **Render:** `quarto render --to html`
- **Deploy:** `./deploy.sh` (git worktree → gh-pages branch)
- **Watch assets:** `./scripts/watch-assets.sh` (run alongside `quarto preview`)

**Every change gets deployed, so a container has to be able to run `./deploy.sh`.**
A fresh Claude Code container has none of the four things it needs. Set them
up before saying a change is done:

| Need | Why | Get it |
|---|---|---|
| **quarto &ge; 1.7.0** | the Glossary extension refuses anything older, and the render dies before writing a file | tarball from `github.com/quarto-dev/quarto-cli/releases/download/v<V>/quarto-<V>-linux-amd64.tar.gz` into `/opt/quarto`, symlink `bin/quarto` onto the path |
| **Chromium** | a Unit 1 lesson has a diagram quarto renders through Chrome; without it the render stops at file 5 with "Chrome not found" | already at `/opt/pw-browsers/chromium-1194/chrome-linux/chrome`; export `QUARTO_CHROMIUM` to point at it. Do **not** run `quarto install chromium` |
| **pandoc** | `scripts/build-assessments.py` shells out to it | `apt-get install -y pandoc` |
| **a clean tree** | `deploy.sh` refuses to run with uncommitted or staged changes | commit first |

- **Downloads:** the sandbox proxy only serves GitHub for repos in this
  session's scope. `add_repo` for `quarto-dev/quarto-cli` (read) opens the
  release download. PyPI and npm are already allowed, `pip install quarto-cli`
  is not (the classifier blocks it)
- `deploy.sh` renders, runs `scripts/check-site-assets.py`, then force-pushes
  the built `_book` to `gh-pages`. It takes a few minutes, so start it in the
  background and wait on the log rather than a tool timeout
- The push reports **"Bypassed rule violations ... Commits must have verified
  signatures"**. That is the branch rule being waived, not a failure. Set
  `SIGN_COMMITS=true` to sign the deploy commit instead
- `main` and `gh-pages` are separate. Pushing to `main` publishes nothing;
  only `./deploy.sh` moves the site

## Branches

Keep the repository clean. Dead branches are clutter.

- Work happens on a feature branch. Granular commits there are fine and
  wanted while the feature is still being worked on, which is exactly when
  the branch still exists
- When a feature is finished it goes to `main` as **one squashed commit**
  naming the feature. `main` keeps a history of what was added, not of every
  step it took to get there
- The branch is deleted once it is merged
- **Nothing is merged or deleted without the teacher signing off on it.**
  Propose it, show what would land, and wait

Two things that bite:

- **Deploying is not merging.** `deploy.sh` force-pushes the built `_book` to
  `gh-pages` and touches nothing else, so a change can be live on the site
  while its source exists only on a feature branch. Check
  `git rev-list --count origin/main..HEAD` before assuming work is safe
- **This session's credentials cannot delete branches.** `git push origin
  --delete` returns HTTP 403. That is a permission limit, not a safety
  refusal, so branch removal is the teacher's to do

Before calling a branch safe to delete, use
`git merge-base --is-ancestor origin/<branch> origin/main`. A commit count of
zero from `git rev-list origin/main..origin/<branch>` says the same thing, but
`git diff --name-only main branch` does **not**: it reports differences in
both directions, so a fully merged branch can look like it carries hundreds of
unmerged files when those files are `main`'s own later work.

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
- **A key answers the paper in the space provided.** It keeps the quiz's own
  work space and writes the answer into it in red, so a key sits page for page
  beside a student's copy. The builder matches the key's `12.` to question 12
  (a bold `**12.**`, an `<ol>` item, or an `## 12.` section); where an answer
  reads `a. ... b. ...` and each part has its own blank, each part is answered
  in its own blank. A question with a figure and no blank gets its answer
  underneath. Anything it cannot match at all falls back to a block at the end,
  so a key that grows a trailing "Answer Key" heading means the numbering
  stopped lining up
- **Page for page holds by page, not by page count.** Key page N carries the
  same questions as sheet page N. A key still runs a page longer where the
  answers it adds outweigh the name line it drops, and that is fine; buying
  the count back would mean taking room away from the student
- Self-contained: no JS, no CDN. Math is MathML, converted by pandoc
- **Work space is measured, not trusted.** Sources mark out room three ways
  (`<br>` runs, `\vspace`, raw `{=latex}`) and some not at all, so the builder
  tops every question up: 3cm to work in, 0.8cm if it is answered on a rule in
  its own text, 0.4cm if it is answered by circling a choice already printed,
  none for a figure or a question stem introducing its parts
- **A long `<br>` run counts for less.** The run lengths cluster on 5, 6, 8 and
  10 (254 runs) against 9 at four and 6 at nine, and the same ten lines sit
  under "give the domain" and under "solve with the quadratic formula". Round
  numbers mean somebody filling out a page, not measuring a question, so a run
  earns 0.6cm a line for five lines and 0.3cm a line after that. `\vspace`,
  which is written in cm and so is deliberate, is taken as it stands
- **Page breaks are measured too, and the sources' own are dropped.** They were
  placed against the teacher's older PDF export, where a page held different
  amounts. Kept, they fired after the content had already run onto the next
  page and left it nearly blank. Write `<div class="pagebreak"></div>` if a
  sheet ever has to start a part on a fresh page on purpose
- **A question and the room to answer it stay on one page.** A page ending
  between them hands the student a stem with nowhere to work. So the builder
  wraps a loose `**4.**` question and everything under it in one `.q` block,
  pulls a figure that fell out of its list item back inside, and tags a bold
  line that only introduces the questions below it `.lead`; the stylesheet
  keeps each whole. A question split into `a, b, c` is the exception: it may
  break between parts, since each part is its own item with its own room, and
  only the stem and the first part have to stay together
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

## Curriculum Judgment

**Do not propose cutting a lesson.** The teacher has taught geometry, statistics,
Algebra 2 and Algebra 1, and did mathematics professionally for twenty years
before that. Scope decisions are his.

Analysis that ranked lessons by EOC standards coverage got three cuts wrong in
a row, because what a lesson is for is not visible in its text:

- **1.6 and 1.7 (percents)** looked unused: zero downstream references, no
  standard names it. They are the most transferable content in the book, and
  percent is what `A1.DS.A.4` calls relative frequency
- **1.2 (prime factorization)** looked unused because Units 5 and 6 call the
  same skill "factoring". Its numeric rehearsal is a prerequisite for nine of
  the twenty-six lessons that follow. It is also how multiplication facts get
  retaught to students who never learned them, in a form a fifteen-year-old
  will accept

A grep measures vocabulary, not dependency, and never measures purpose. A
lesson may exist for fluency, for confidence, or for a student who leaves
school this year. Report what the measurements say and let him decide.

## Cost/Workflow Preferences
- **No Task/Explore subagents**: use Grep and Glob directly for code searches
- Start a **new session** when switching to a different task area
- Run `/compact` when context grows long (after completing a chunk of work)
- Use **Haiku** (`/model claude-haiku-4-5-20251001`) for simple questions; switch back to Sonnet for complex edits
