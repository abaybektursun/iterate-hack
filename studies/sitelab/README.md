# sitelab: interactive 3D pictures of the team's work

Question: which pictures of the agents and the work, built only from real data, are worth a place on the team site?
Twenty-one prototypes, one idea each. Live at https://monitor.invariant.team/lab/ under the page name "AI Psychosis maxxing" (`tools/view.py` serves this folder at
`/lab/`; `infra/monitor/deploy.sh` puts `index.html` and each prototype's `index.html` and `data.json` into the zip).

The Lab page itself (`index.html`) is written by `python3 studies/sitelab/build_index.py`: the site's header, type and
tokens, one row per picture and one preview plate. Each picture's still, `prototypes/<slug>/shot.webp` (a headless
screenshot of its opening view), is written into the page as a data URI, so the page is one request.

Local: `python3 studies/sitelab/serve.py` then http://127.0.0.1:8777/ (passes `/data` through to the site).

| Prototype (`prototypes/<slug>/`) | Picture | Data |
|---|---|---|
| score-terrain | posted scores as a plaster relief, one benchmark at a time | live `/data` scores |
| problem-field | one bead per problem, moving between right and wrong under two configurations | per-problem rows (`build.py`) |
| trace-ribbons | each agent transcript as a wire, tool calls as beads | one laptop's Claude Code transcripts, labels redacted (`build.py`) |
| physics-board | the board as rigid bodies in a tray | live `/data` |
| weight-space | every model made by weight arithmetic, with a dial over the edit size | rlneurons readouts (`build.py`) |
| lineage | which item cites which, regrown over time | board table, finding pages, theory rounds (`build.py`) |
| token-flow | answers as grain streams that finish or hit the token cap | rows of hard328 at cap 16,384 and 32,768 (`build.py`) |
| forecast-range | theories' forecasts against the measured numbers, round by round | studies/theory rounds and forecast runs (`build.py`) |
| time-helix | items, messages, commits, GPU jobs and scores on one helix, one turn per hour | board, events, git log, job records (`build.py`) |
| crystal | one crystal per result, grown by a stated rule | live `/data`, finding pages (`build.py`) |
| repo-city | the repository's history as a model city | `git log --numstat` (`build.py`) |
| model-interior | the 32 layers with the RL weight change, its top directions and the loop neurons | rlneurons and cleanneurons readouts (`build.py`) |
| one-take | a 90-second single shot through plain base, cue, vote, weight edit and RL on one register of 500 pins each | per-problem rows (`build.py`) |
| orrery | a brass orrery: one arm per study at the distance its best base score is short of RL's one-sample 463, one bead per result | board snapshot, `studies/` folders (`build.py`) |
| vote-machine | four samples per problem drop as balls into a ballot cabinet; the tallest stack is the vote | per-sample rows of hard328 (`build.py`) |
| tide | 500 stone columns, easiest to hardest, flooded to the level each configuration solves | per-problem rows (`build.py`) |
| call-it | a forecasting game on a slide rule, scored by the rule of `studies/theory/lib/round.py` | theory rounds (`build.py`) |
| music-box | commits, board items, messages and scores as pins on a cylinder that plucks a comb (Web Audio) | board, events, git log (`build.py`) |
| mobile | a hanging mobile with one leaf per open work item, balanced by a physics engine | live `/data` |
| ledger | a balance weighing each method's tokens per problem against the accuracy it bought | posted scores (`build.py`), live `/data` |
| library | one book per paper the agents read, opening on its recorded findings | `papers/` records (`build.py`) |

Each `data.json` is rebuilt with `uv run studies/sitelab/prototypes/<slug>/build.py`. `shoot.py` watches a page in
headless Chrome with hardware WebGL in real time (frames at real intervals, pointer steps, console errors); its printed
frame rate counts animation callbacks, not drawn frames. Every page was checked with it for errors and an opening frame.
Not checked: sound (music-box, vote-machine, ledger, one-take), and motion and drag by a person in a visible browser.
The pages use a serif face and a brass accent, which differs from the site's rules in `.claude/skills/site-ui/SKILL.md`.
