---
name: site-ui
description: Guidelines for any page or change on the team site (monitor.invariant.team, served by tools/view.py), covering the look (one lit object with depth, slow motion that replays real data), the words, the behaviour and the checks. Use before adding a page, a picture, a chart, a panel or any visible element to tools/view.py, tools/architecture.py, tools/findings.py or a new page module.
---

# Site UI

The home page is https://invariant.team (`tools/home.py`, also `/home` here): a dial that leads to every page of this
site, monitor.invariant.team. A page that is not a header tab is reached from there, so add a new page to `PAGES` in `home.py`.
The header of every page has four tabs: Board (`/`, `tools/view.py`), Design (`/architecture`,
`tools/architecture.py`), Proof (`/proof`) and Findings (`/findings`, `tools/findings.py`). Design is the reference for how the site
should look and move. Open it in a browser before you design anything, and copy its tokens, its light, its depth and
its motion. Board is a page of lists and one chart: it uses the same tokens and type, has no lit object, and its
chart is its one picture. Findings is a grid of tiles, one per finding, and each tile opens the page of that finding
(`tools/finding_<slug>.py`, `/finding/<slug>`; `.claude/skills/finding-page/SKILL.md`). On a finding's page the tab
Findings is the current one. Proof is the same
grid for the experiments that test the team's method itself (the harness, a skill, a tool) and not the research
question: one tile per experiment, each opening `tools/proof_<slug>.py` at `/proof/<slug>`, where the tab Proof is the
current one (Samer, 2026-11-15: a test of the method is proof of the method and is not a finding).

A reader should get the point of a page in 5 seconds and find depth by clicking.

## One rule above the others

The more a page shows, the less it is read. Before adding an element or a word, name what the reader can no longer
do without it. If you cannot, leave it out. A page looks expensive because of what was left out and how exactly
the rest is made.

## The look

1. One object. A page has one picture, and the picture is one lit object in a quiet room: a body in the centre and
   fine lines around it. Everything else on the page is type and space.
2. One light, from the upper left, in both themes. Dark is the hero: a lit glass body in a dark room, with a soft
   glow. Light is the same object as white porcelain on a cool grey table, with a cast shadow in place of the glow.
   Use the tokens of `architecture.py` for this (`--glass-hi`, `--glass`, `--glass-lo`, `--rim-a`, `--rim-b`,
   `--rim-c`, `--glow`, `--shadow`, `--spec`, `--bloom`). Add no second light and no second shadow recipe.
3. Color comes from the `:root` block of `architecture.py`, with its dark values. `--blue` is the one accent and
   means live, fresh or selected. `--red` means a problem. A person's color is `oklch(var(--pl) var(--pc) <hue>)`,
   the hue from `HUES` by the person's place in the sorted list of names, the same on every page. Add no other color.
4. Lines are fine, and they change with depth: thin and faint at the back, heavier in front. A gradient is light on
   the object or on the one button, never decoration. No cards, no boxes around things, no shadows under text.
5. One typeface, Archivo, through its weight and width axes. The one sentence of a page is large and light (weight
   300). Labels are small and heavier. Sentence case, tabular numbers, no capitals-only labels, no monospace.
6. The words sit in a flat column beside the picture: the sentence, hairlines (`1px solid var(--rule)`), one button.
7. Something that acts is drawn as a mark, and data is drawn as a dot. An agent is the mark of the product it runs
   on (the Claude mark for Claude Code, the OpenAI mark for Codex; outlines in `architecture.py`), flat, in its
   person's color. A board item is a dot: hollow for open work, solid for a result, small for an idea or a note.
   A key at the bottom names each glyph in one or two words.

## Depth

1. The picture is a small three-dimensional scene seen from slightly above, drawn in SVG with our own projection
   (`world` and `proj` in `architecture.py`). No 3D library.
2. What is near is larger and brighter. What is far is smaller and fainter. What passes behind the body is hidden.
3. Depth never costs legibility. The body faces the viewer so its content stays readable, and nothing crosses it.
   Names stay upright and still: they never tilt, mirror or drift, and a ring is open under its own name.
4. Every part that can be clicked has a generous invisible hit area, so depth does not make clicking harder.

## Motion

1. The picture always moves, slowly. The whole view sways by a few degrees, leans a few degrees toward the mouse and
   settles back, and each part turns at its own slow rate.
2. What travels is real data, replayed: about every 2.5 s one real event from the newest 40, looped. On the
   architecture page a message is a pulse in its sender's color that runs to every other person's agents, and a
   post is a pulse that runs to the board, after which a ripple returns to every agent. Never invent an event.
3. An event that is happening now looks different from the replay and plays next: a larger dot with a halo.
4. A pulse is a small lit head with a tapered tail and a soft light around it, in the color of whoever caused it.
5. One drawn entrance on load. A selection dims everything else. A walk-through stops the replay.
6. With `prefers-reduced-motion` the page shows one still, well-composed frame and nothing replays.
7. Keep each frame cheap: a few dozen attributes set per frame, and no filter recomputed every frame.

## Words

1. As few as possible. A label is one or two words. A sentence states one fact.
2. Plain technical English, the field's own terms. Write for someone who was not in the room. Where `README.md` or
   `DIRECTION.md` already says it, use those words.
3. No slogans. Samer rejected the first headline of the architecture page ("3 people. 19 agents. One question. No
   boss.") as machine-sounding (2026-11-14). So: no clipped fragments in a row, no punchline sentences ("Quote or
   nothing."), no bold lead-in at the start of each list line, no row names that sell ("Two checks agents cannot
   skip"). Write the full plain sentence, and name a part with the shortest concrete word ("Chat", "Retro").
4. Draw and name a part by what it is. An agent is a session of Claude Code or Codex, so it is drawn as that mark.
5. Every number on a page is live or names where it was measured. No number typed from memory.
6. Claim only what the code enforces or a file records. If something is not measured yet, say so on the page.
7. Explain a rule by what happens and why ("If the code has unpushed changes, the tool stops with an error. This way
   the exact code behind every result can be found later."), never by a compressed claim ("every number traces to
   code").

## Behaviour

1. Nothing essential on hover: the page is shown on a projector and on phones. Everything works by click and by
   keyboard, with a visible focus ring.
2. A selection is one value mirrored in the address (`/#result-8b1c48`, `/architecture#board`), so every state has
   a link, Back works and Esc closes.
3. Detail opens beside the picture, in the fixed column. The picture does not reflow.

## How a page is built

1. One Python module per page, holding `PAGE = r"""..."""`: plain HTML, CSS and JavaScript, inline SVG. No framework,
   no build step, no image files, no library. A finding page needs no route; any other new page gets one route line
   in `view.py`. `infra/monitor/deploy.sh` ships every `tools/*.py`, so a new module needs no deploy change.
2. Data comes from `/data` (and `/data/<item id>`), read every 10 s, updated in place. A page never writes.
3. A failed read keeps the last data on screen and says so in the status at the top right ("Offline, last read 14:02").
   Before the first read the page shows its empty frame, never a spinner.

## Before you say it is done

1. Open it in a browser at 1440 x 860 in dark and in light, and at phone width (375). No console errors, nothing
   clipped, no horizontal scroll, marks still readable on the phone.
2. Watch it move for 30 seconds in a visible tab. A hidden or background tab slows animation, so a screenshot from
   one proves nothing about the motion.
3. Glance test: give a screenshot of the first view to a fresh subagent that knows nothing about the page, and ask
   what the page says after 5 seconds and what it could not work out. Fix what it misread. At most two rounds.
4. Read every sentence against the code or the artifact it describes.
5. Describe the page in `README.md` in the same commit.
