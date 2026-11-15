---
name: site-ui
description: Guidelines for any page or change on the team site (monitor.invariant.team, served by tools/view.py), so every page looks like the same site and stays simple. Use before adding a page, a chart, a panel or any visible element to tools/view.py, tools/architecture.py or a new page module.
---

# Site UI

The site has the board (`tools/view.py`, `/`), the architecture picture (`tools/architecture.py`, `/architecture`)
and one page per finding (`tools/finding_<slug>.py`, `/finding/<slug>`; `.claude/skills/finding-page/SKILL.md`).
Copy from them. A reader should get the point of a page in 5 seconds and find depth by clicking.

## One rule above the others

The more a page shows, the less it is read. Before adding an element or a word, name what the reader can no longer
do without it. If you cannot, leave it out.

## How a page is built

1. One Python module per page, holding `PAGE = r"""..."""`: plain HTML, CSS and JavaScript, inline SVG. No framework,
   no build step, no image files, no library (the one exception is in the finding-page skill). A finding page needs
   no route; any other new page gets one route line in `view.py`. `infra/monitor/deploy.sh` ships every
   `tools/*.py`, so a new module needs no deploy change.
2. Data comes from `/data` (and `/data/<item id>`), read every 10 s, updated in place. A page never writes.
3. A failed read keeps the last data on screen and says so in the status at the top right ("Offline, last read 14:02").
   Before the first read the page shows its empty frame, never a spinner.

## Looks

1. Copy the `:root` block of `architecture.py`: `--paper`, `--sheet`, `--ink`, `--mute`, `--faint`, `--rule`,
   `--blue`, `--red`, with its dark values. Add no other color.
2. Blue means live, fresh or selected. Red means a problem (stale work, a failed read). Neither is decoration.
3. A person's color is `oklch(var(--pl) var(--pc) <hue>)`, the hue from `HUES` by the person's place in the sorted
   list of names. The same person has the same color on every page.
4. One typeface, Archivo, through its weight and width axes. Body 15 px. Names and labels in sentence case. No
   capitals-only labels, no monospace, no second typeface.
5. Text areas are flat: hairlines (`1px solid var(--rule)`), `--ink` for the one line that carries a heading, no
   cards. A picture may have light and depth, as the architecture page does: one light direction and one shadow
   recipe for the whole picture.
6. Numbers use `tabular-nums` and are set heavier than the words around them.

## Words

1. As few as possible. A label is one or two words. A sentence states one fact.
2. Plain technical English, the field's own terms, no metaphors. Write for someone who was not in the room.
   Where `README.md` or `DIRECTION.md` already says it, use those words.
3. No slogans. Samer rejected the first headline of the architecture page ("3 people. 19 agents. One question. No
   boss.") as machine-sounding (2026-11-14). So: no clipped fragments in a row, no punchline sentences ("Quote or
   nothing."), no bold lead-in at the start of each list line, no row names that sell ("Two checks agents cannot
   skip"). Write the full plain sentence, and name a part with the shortest concrete word ("Chat", "Retro").
4. Name a part by what it is. Memory is the shared database, so its picture is a database and its label says so.
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
3. Detail opens beside the picture, in a fixed column. The picture does not move or reflow.
4. A picture may move all the time when the motion is slow, follows the drawn lines and shows how the thing works.
   What travels should be real data, replayed (the architecture page replays the last messages and posts). An event
   happening now must look different from the replay (a larger dot with a halo). One drawn entrance on load. Honor
   `prefers-reduced-motion`.

## Before you say it is done

1. Open it in a browser at 1440 x 860, in dark mode, and at phone width (375). No console errors, nothing clipped,
   no horizontal scroll.
2. Glance test: give a screenshot of the first view to a fresh subagent that knows nothing about the page, and ask
   what the page says after 5 seconds and what it could not work out. Fix what it misread. At most two rounds.
3. Read every sentence against the code or the artifact it describes.
4. Describe the page in `README.md` in the same commit.
