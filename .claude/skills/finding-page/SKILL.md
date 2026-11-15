---
name: finding-page
description: Make the public page of one finding on the team site (monitor.invariant.team/finding/<slug>, reached from its tile on /findings): one picture a newcomer understands in seconds, one control to play with, depth behind a click. Use for every finding worth telling, a benchmark gain or an interpretability result, once it has a committed artifact and a baseline and is posted on the board.
---

# Finding page

A finding gets one page that a person outside the team understands in 5 seconds: what the problem was, what was
found, how large it is. The look (light, depth, motion), the words and the checks are in
`.claude/skills/site-ui/SKILL.md`; read it first.

## When to make one

Samer's rule of 2026-11-15: every finding worth telling gets a page, whether it is a benchmark gain or an
interpretability result. The page has minimal text and is written for a reader who knows basic machine learning and
nothing else about our work. Before writing it, read the newest benchmark results on the board
(`uv run tools/board.py ls result --new --n 20`, `uv run tools/climb.py`), so the page states the finding against
the current best numbers.

All four hold. If one fails, the board result is enough.

1. The result answers part of `DIRECTION.md`, or contradicts a published number.
2. `python3 tools/recall.py` and an Exa search found no earlier report of it, and you can name the closest published
   result.
3. Its numbers are in a committed run folder, and you read them there (Results, rule 7).
4. It is measured against the strongest baseline, with a control (Results, rules 3 and 4).

## Make it

1. Copy `.claude/skills/finding-page/template.py` to `tools/finding_<slug>.py`. `view.py` serves it at
   `/finding/<slug>` and gives it a tile on `/findings`, with no other change. The tile is the only way to the page:
   the header has four tabs (Board, Design, Proof, Findings) and never links a single finding. One finding, one file,
   one writer.
   An experiment that tests the team's method itself (the harness, a skill, a tool) is not a finding. It gets a proof
   page, made in the same way and with the same checks: the file is `tools/proof_<slug>.py`, it is served at
   `/proof/<slug>` with a tile on `/proof`, and in its header the tab Proof is the current one
   (`tools/proof_review_cuts_waste.py` is the first).
2. Fill the six values at the top:
   - `PROBLEM`: the problem as one question, at most 12 words, no term a newcomer would not know.
   - `LINE`: the finding in one sentence with its number, at most 16 words. It is also the sentence on the tile.
   - `TITLE`: two to four words, the name on the tile.
   - `DATA`: copied from the run's `metrics.json`, with the artifact path and the commit. No number from memory.
   - `PANELS`, in this order: "What is new" (what was already known, with the closest published result, and what
     this finding adds), "Why it matters" (what it changes for the direction in `DIRECTION.md`), "How we know" (what
     was run, n, the control), "What it does not show" (the wrong conclusion a reader could draw, what is untested),
     "How to reproduce it" (commit, command, artifact). Full plain sentences, following the Words rules of `site-ui`.
   - `ICON`: the tile's icon, the page's own picture reduced to one small lit glass object. It is the source of a
     JavaScript arrow function `(kit, t, tilt) => "<svg markup>"`, drawn with the kit of `tools/findings.py`
     (projection, glass slab, lit face, line, theme tokens); that file's docstring describes the call. A module
     without `ICON` gets a plain glass slab.

## The picture

1. One picture. It shows the effect itself, and the reader changes exactly one thing and watches the number move:
   the switch between the condition without the finding and the condition with it. The page loads on the problem,
   and the reader makes the finding happen.
2. The template draws one bar against the baseline, which fits a finding that is one number. Replace `draw()` when
   the finding has another shape, and keep the switch and the side column:
   - a trend: a line, with a slider on its x axis;
   - a behaviour: two real outputs side by side from the run folder, one scored right and one scored wrong;
   - a mechanism: a diagram in the manner of `tools/architecture.py`.
3. The picture has the look of the architecture page: one lit object with depth, slow motion, real data
   (`site-ui`: The look, Depth, Motion). Give the finding a body the reader can turn or switch, drawn with the same
   light and the same projection, with no 3D library. The template's flat bar is the plain starting point; replace it
   when the finding deserves more. Depth must make the finding easier to see: a single number stays a single,
   large, readable number.

## Words

1. At most 40 words in the first view: the problem, the finding, the names in the picture, the five panel names.
2. Everything else sits behind a click in the side column: one sentence, then at most three facts. No paragraphs.
3. State what is not shown as plainly as what is.

## Before it goes public

1. The checks of `site-ui` (desktop, dark, phone, no console errors).
2. Glance test: a fresh subagent sees only a screenshot of the first view and answers three questions: what was the
   problem, what was found, how large is it. It must get all three. At most two rounds.
3. Show your person the page and its tile (`uv run tools/view.py`, then `/findings` and `/finding/<slug>`) and wait
   for their yes on the wording: the page is public and carries the team's name.
4. Then commit `tools/finding_<slug>.py` with the study's `README.md` line, deploy with `infra/monitor/deploy.sh`,
   comment the link on the board result and send it on `all`.

## Later

A corrected number changes the page in the same commit. A withdrawn finding's file is deleted, and its page and tile
disappear with it.
