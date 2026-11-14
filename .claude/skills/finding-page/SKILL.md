---
name: finding-page
description: Make the public page of one novel finding on the team site (monitor.invariant.team/finding/<slug>): one picture a newcomer understands in seconds, one control to play with, depth behind a click. Use when a result is new (absent from memory and the literature), has a committed artifact and a baseline, and after posting it on the board.
---

# Finding page

A novel finding gets one page that a person outside the team understands in 5 seconds: what the problem was, what was
found, how large it is. The looks and the checks are in `.claude/skills/site-ui/SKILL.md`; read it first.

## When to make one

All four hold. If one fails, the board result is enough.

1. The result answers part of `DIRECTION.md`, or contradicts a published number.
2. `python3 tools/recall.py` and an Exa search found no earlier report of it, and you can name the closest published
   result.
3. Its numbers are in a committed run folder, and you read them there (Results, rule 7).
4. It is measured against the strongest baseline, with a control (Results, rules 3 and 4).

## Make it

1. Copy `.claude/skills/finding-page/template.py` to `tools/finding_<slug>.py`. `view.py` serves it at
   `/finding/<slug>` and links it in the header of every page, with no other change. One finding, one file, one
   writer.
2. Fill the five values at the top:
   - `PROBLEM`: the problem as one question, at most 12 words, no term a newcomer would not know.
   - `LINE`: the finding in one sentence with its number, at most 16 words.
   - `TITLE`: two to four words, the link text.
   - `DATA`: copied from the run's `metrics.json`, with the artifact path and the commit. No number from memory.
   - `PANELS`: "How we know" (what was run, n, the control, the closest published result), "What it does not show"
     (the wrong conclusion a reader could draw, what is untested), "Run it yourself" (commit, command, artifact).

## The picture

1. One picture. It shows the effect itself, and the reader changes exactly one thing and watches the number move:
   the switch between the condition without the finding and the condition with it. The page loads on the problem,
   and the reader makes the finding happen.
2. The template draws one bar against the baseline, which fits a finding that is one number. Replace `draw()` when
   the finding has another shape, and keep the switch and the side column:
   - a trend: a line, with a slider on its x axis;
   - a behaviour: two real outputs side by side from the run folder, one scored right and one scored wrong;
   - a mechanism: a diagram in the manner of `tools/architecture.py`.
3. Three dimensions only when the thing has three (a loss surface, an embedding, a direction in weight space) and a
   flat picture would hide the point. Then: one view the reader drags, drawn on a canvas; one pinned `three.js`
   import is the only library allowed on the site; a still picture when `prefers-reduced-motion` is set. Never 3D
   for a bar or a line.

## Words

1. At most 40 words in the first view: the problem, the finding, the names in the picture, the three panel names.
2. Everything else sits behind a click in the side column: one sentence, then at most three facts. No paragraphs.
3. State what is not shown as plainly as what is.

## Before it goes public

1. The checks of `site-ui` (desktop, dark, phone, no console errors).
2. Glance test: a fresh subagent sees only a screenshot of the first view and answers three questions: what was the
   problem, what was found, how large is it. It must get all three. At most two rounds.
3. Show your person the page (`uv run tools/view.py`, then `/finding/<slug>`) and wait for their yes on the wording:
   the page is public and carries the team's name.
4. Then commit `tools/finding_<slug>.py` with the study's `README.md` line, deploy with `infra/monitor/deploy.sh`,
   comment the link on the board result and send it on `all`.

## Later

A corrected number changes the page in the same commit. A withdrawn finding's file is deleted, and its page and link
disappear with it.
